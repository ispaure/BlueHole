"""Test candidate baseline tooling without launching Blender."""

from copy import deepcopy
import json
from pathlib import Path
import os
import stat
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import blender_keymap_baseline as baseline


def binding(target, event_type="A", *, active=True, properties=None, blender_id=1, **event):
    return {
        "target": target,
        "event": {
            "type": event_type, "value": "PRESS", "any": False,
            "shift": 0, "ctrl": 0, "alt": 0, "oskey": 0,
            "key_modifier": "NONE", "direction": "ANY", "repeat": False, "map_type": "KEYBOARD",
            **event,
        },
        "active": active,
        "properties": properties or {},
        "blender_id": blender_id,
        "is_user_defined": False,
        "is_user_modified": False,
    }


def keymap(name, *items, modal=False, space="EMPTY", tool=None):
    return {
        "scope": {"name": name, "space_type": space, "region_type": "WINDOW",
                  "is_modal": modal, "is_tool": tool},
        "items": list(items),
    }


def snapshot(*maps):
    roles = {role: {"name": role, "maps": []} for role in baseline.ROLES}
    roles["user"]["maps"] = list(maps)
    return {"schema_version": 1, "roles": roles}


class KeymapSnapshotTests(unittest.TestCase):
    def test_deterministic_ids_preserve_duplicates_and_exclude_volatile_fields(self):
        item = binding("mesh.example", properties={"array": [1, 2], "flag": True})
        duplicate = binding("mesh.example", properties={"flag": True, "array": [1, 2]}, blender_id=-100)
        first = baseline.normalize_snapshot(snapshot(keymap("Mesh", item, duplicate)))
        other = snapshot(keymap("Empty"), keymap("Mesh", binding("mesh.other", "B"), duplicate))
        other["roles"]["default"]["maps"] = [keymap("Mesh", duplicate)]
        other = baseline.normalize_snapshot(other)
        rows = first["roles"]["user"]["maps"][0]["items"]
        separate = other["roles"]["user"]["maps"][1]["items"][1]
        self.assertEqual(rows[0]["row_id"], rows[1]["row_id"])
        self.assertEqual(rows[0]["row_id"], separate["row_id"])
        self.assertEqual(rows[0]["occurrence_id"], separate["occurrence_id"])
        self.assertEqual(rows[0]["row_id"], other["roles"]["default"]["maps"][0]["items"][0]["row_id"])
        self.assertNotEqual(rows[0]["occurrence_id"], rows[1]["occurrence_id"])
        self.assertEqual(rows[1]["blender_id"], -100)
        self.assertNotIn("row_id", item)
        self.assertEqual(first, baseline.normalize_snapshot(first))
        baseline.validate_snapshot(first)
        first["roles"]["user"]["maps"][0]["items"][1]["row_id"] = "invalid"
        with self.assertRaisesRegex(ValueError, "Inconsistent row_id"):
            baseline.validate_snapshot(first)
        with self.assertRaisesRegex(ValueError, "Inconsistent row_id"):
            baseline.compare_snapshots(first, first)

    def test_validation_checks_input_types_and_resolves_aliases_in_role_order(self):
        capture = snapshot()
        capture["roles"] = dict(reversed(tuple(capture["roles"].items())))
        capture["roles"]["active"]["alias_of"] = "default"
        baseline.validate_snapshot(capture)
        capture["roles"]["default"] = []
        with self.assertRaisesRegex(ValueError, "map list for the default role"):
            baseline.validate_snapshot(capture)
        with self.assertRaisesRegex(ValueError, "schema_version 1"):
            baseline.validate_snapshot({**snapshot(), "schema_version": True})
        with self.assertRaisesRegex(ValueError, "Invalid keymap modifier"):
            baseline.validate_snapshot(snapshot(keymap("Mesh", binding("mesh.example", shift=2))))

    def test_binding_scope_target_event_properties_and_activation_change_semantic_id(self):
        normal = binding("mesh.example", properties={"flag": True})
        rows = [
            keymap("Mesh", normal,
                   binding("mesh.example", properties={"flag": False}),
                   binding("mesh.example", properties={"flag": True}, active=False),
                   binding("mesh.example", properties={"flag": True}, hyper=1),
                   binding("mesh.other", properties={"flag": True})),
            keymap("Other", normal),
            keymap("Mesh", normal, space="VIEW_3D"),
            keymap("Mesh", normal, modal=True),
            keymap("Mesh", normal, tool=True),
        ]
        result = baseline.normalize_snapshot(snapshot(*rows))
        identifiers = [row["row_id"] for keymap_ in result["roles"]["user"]["maps"]
                       for row in keymap_["items"]]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_aliased_role_matches_concrete_role(self):
        base, ref = snapshot(), snapshot()
        for capture in (base, ref):
            capture["roles"]["default"]["maps"] = [keymap("Mesh", binding("mesh.example"))]
        base["roles"]["active"]["alias_of"] = "default"
        ref["roles"]["active"]["maps"] = ref["roles"]["default"]["maps"]
        report = baseline.compare_snapshots(base, ref, role="active")
        self.assertEqual(report["summary"]["base_rows"], 1)
        self.assertEqual(report["deltas"], [])
        ref["roles"]["active"]["available"] = False
        with self.assertRaisesRegex(ValueError, "Unavailable configuration"):
            baseline.compare_snapshots(base, ref, role="active")

    def test_effective_rna_getters_include_defaults_and_report_omissions(self):
        class RNAProps:
            def is_property_set(self, name):
                return False

            @property
            def inaccessible(self):
                raise RuntimeError("private path")

            @property
            def pointer(self):
                raise AssertionError("unsafe getter must not be evaluated")

        props = RNAProps()
        props.boolean = False
        props.options = {"TWO", "ONE"}
        props.vector = (1.0, -0.0, 3.0)
        props.settings = {"nested": ["value"]}
        props.dynamic = ""
        props.text = ""
        props.bl_rna = SimpleNamespace(properties=[
            SimpleNamespace(identifier=name, type=kind)
            for name, kind in (
                ("rna_type", "POINTER"), ("boolean", "BOOLEAN"), ("options", "ENUM"),
                ("vector", "FLOAT"), ("settings", "STRING"),
                ("pointer", "POINTER"), ("inaccessible", "ENUM"),
                ("dynamic", "ENUM"), ("text", "STRING"),
            )
        ])
        values, issues = baseline._read_properties(props)
        self.assertEqual(values, {"boolean": False, "options": ["ONE", "TWO"],
                                  "vector": [1.0, 0.0, 3.0], "settings": {"nested": ["value"]},
                                  "dynamic": "", "text": ""})
        self.assertEqual(issues, {"pointer": "pointer_skipped", "inaccessible": "RuntimeError",
                                  "dynamic": "RNA_enum_unresolved"})

    def test_rna_array_defaults_preserve_matrix_rows_and_reject_unexpected_iterables(self):
        class Array:
            def __init__(self, values):
                self.values = values

            def __getitem__(self, index):
                return self.values[index]

        class UnexpectedArray:
            def __iter__(self):
                raise AssertionError("arbitrary iterable must not be traversed")

        vector_type = type("Vector", (Array,), {"__module__": "builtins"})
        matrix_type = type("Matrix", (Array,), {"__module__": "builtins"})
        impostor_type = type("Vector", (UnexpectedArray,), {"__module__": "mathutils"})
        rna_array_type = type("bpy_prop_array", (Array,), {})
        vector = vector_type((1.0, -0.0, 3.0))
        props = SimpleNamespace(
            vector=vector,
            matrix=matrix_type((vector, vector_type((4.0, 5.0, 6.0)))),
            flags=rna_array_type((True, False)),
            unexpected=UnexpectedArray(),
            impostor=impostor_type(),
            invalid_number=vector_type((float("nan"),)),
            invalid_leaf=vector_type((object(),)),
            non_array=vector,
        )
        props.bl_rna = SimpleNamespace(properties=[
            SimpleNamespace(identifier=name, type=kind, is_array=name != "non_array")
            for name, kind in (
                ("vector", "FLOAT"), ("matrix", "FLOAT"), ("flags", "BOOLEAN"),
                ("unexpected", "FLOAT"), ("impostor", "FLOAT"), ("invalid_number", "FLOAT"),
                ("invalid_leaf", "FLOAT"), ("non_array", "FLOAT"),
            )
        ])
        mathutils = SimpleNamespace(Vector=vector_type, Matrix=matrix_type)
        with patch.dict(sys.modules, {"mathutils": mathutils}):
            values, issues = baseline._read_properties(props)
        self.assertEqual(values, {
            "vector": [1.0, 0.0, 3.0],
            "matrix": [[1.0, 0.0, 3.0], [4.0, 5.0, 6.0]],
            "flags": [True, False],
        })
        self.assertEqual(issues, {
            "unexpected": "TypeError", "impostor": "TypeError", "invalid_number": "ValueError",
            "invalid_leaf": "TypeError", "non_array": "TypeError",
        })

    def test_capture_distinguishes_unknown_modal_and_unavailable_properties(self):
        event = binding("mesh.example")["event"]
        modal = SimpleNamespace(propvalue="NONE", active=True, is_user_defined=False,
                                is_user_modified=False, id=1, **event)
        regular = SimpleNamespace(idname="mesh.example", properties=None, active=False,
                                  is_user_defined=True, is_user_modified=True, id=-2, **event)
        scope = {"name": "Example", "space_type": "EMPTY", "region_type": "WINDOW",
                 "is_user_modified": True}
        modal_row = baseline._capture_map(
            SimpleNamespace(**scope, is_modal=True, keymap_items=[modal]), (),
        )["items"][0]
        regular_map = baseline._capture_map(
            SimpleNamespace(**scope, is_modal=False, keymap_items=[regular]), (),
        )
        self.assertEqual(modal_row["target"], "NONE")
        self.assertEqual(modal_row["read_issues"], {"target": "RNA_target_unresolved"})
        self.assertEqual(regular_map["items"][0]["read_issues"], {"properties": "RNA_unavailable"})
        self.assertIsNone(regular_map["scope"]["is_tool"])
        self.assertEqual(regular_map["is_tool_source"], "unavailable")

    def test_write_round_trip_and_cli_compare(self):
        capture = snapshot(keymap("Mesh", binding("mesh.example")))
        with TemporaryDirectory() as folder:
            private_path = Path(folder) / "capture.json"
            comparison_path = Path(folder) / "comparison.json"
            baseline.write_snapshot(private_path, capture)
            loaded = json.loads(private_path.read_text(encoding="utf-8"))
            self.assertEqual(loaded, baseline.normalize_snapshot(capture))
            self.assertEqual(loaded["visibility"], "private")
            if os.name == "posix":
                self.assertEqual(stat.S_IMODE(private_path.stat().st_mode), 0o600)
            self.assertEqual(baseline.main(["--compare", str(private_path), str(private_path),
                                            "--output", str(comparison_path)]), 0)
            result = json.loads(comparison_path.read_text(encoding="utf-8"))
            self.assertEqual(result["ledger"]["entries"], [])
            self.assertEqual(result["summary"]["reference_rows"], 1)

    def test_cli_capture_reports_its_runtime_requirement(self):
        result = subprocess.run(
            [sys.executable, "-S", baseline.__file__, "--capture", "unused"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Capture must run in Blender", result.stderr)


class KeymapComparisonTests(unittest.TestCase):
    def test_multiset_add_remove_replacement_and_modal_inactivation(self):
        base = snapshot(
            keymap("Mesh", binding("mesh.old"), binding("mesh.repeat", "D"), binding("mesh.repeat", "D")),
            keymap("Transform Modal Map", binding("CONFIRM", "RET"), modal=True),
        )
        ref = snapshot(
            keymap("Mesh", binding("mesh.new"), binding("mesh.repeat", "D"), binding("mesh.added", "B")),
            keymap("Transform Modal Map", binding("CONFIRM", "RET", active=False), modal=True),
        )
        report = baseline.compare_snapshots(base, ref)
        self.assertEqual(report["summary"]["deltas"], {
            "added": 1, "disabled": 1, "removed": 1, "replacement_candidate": 1,
        })
        changes = {delta["kind"]: delta for delta in report["deltas"]}
        self.assertEqual(changes["removed"]["before"]["target"], "mesh.repeat")
        self.assertEqual(changes["replacement_candidate"]["after"]["target"], "mesh.new")
        self.assertEqual(changes["replacement_candidate"]["provenance"], "unverified")
        self.assertTrue(changes["disabled"]["before"]["scope"]["is_modal"])
        self.assertFalse(changes["disabled"]["after"]["active"])
        self.assertEqual(len(report["collisions"]["base"]), 1)
        self.assertEqual(report["collisions"]["reference"], [])
        self.assertEqual(report["precedence"], "unverified")
        self.assertEqual(report, baseline.compare_snapshots(deepcopy(base), deepcopy(ref)))

    def test_relative_order_identifies_swaps_without_insertion_noise(self):
        a, b, c = (binding(f"mesh.{key.lower()}", key) for key in ("A", "B", "C"))
        base = snapshot(keymap("Mesh", a, b))
        ref = snapshot(keymap("Mesh", c, a, b))
        self.assertEqual(baseline.compare_snapshots(base, ref)["summary"]["deltas"], {"added": 1})
        swapped = snapshot(keymap("Other"), keymap("Mesh", b, a))
        report = baseline.compare_snapshots(base, swapped)
        self.assertEqual(report["summary"]["deltas"], {"reordered": 2})
        self.assertEqual({row["scope"]["name"] for row in report["map_changes"]}, {"Mesh", "Other"})

    def test_ambiguous_replacements_remain_separate(self):
        base = snapshot(keymap("Mesh", binding("mesh.a"), binding("mesh.b")))
        ref = snapshot(keymap("Mesh", binding("mesh.c"), binding("mesh.d")))
        report = baseline.compare_snapshots(base, ref)
        self.assertEqual(report["summary"]["deltas"], {"added": 2, "removed": 2})
        self.assertTrue(all(delta["provenance"] == "unverified" for delta in report["deltas"]))

    def test_event_overlap_accounts_for_wildcards_modifiers_direction_and_repeat(self):
        event = binding("mesh.example", shift=1)["event"]
        self.assertTrue(baseline.events_overlap(event, {**event, "any": True, "shift": 0}))
        self.assertTrue(baseline.events_overlap(event, {**event, "shift": -1}))
        self.assertFalse(baseline.events_overlap(event, {**event, "shift": 0}))
        self.assertTrue(baseline.events_overlap(event, {**event, "value": "ANY", "repeat": True}))
        self.assertTrue(baseline.events_overlap(event, {**event, "key_modifier": "B"}))
        self.assertFalse(baseline.events_overlap({**event, "key_modifier": "C"}, {**event, "key_modifier": "B"}))
        self.assertFalse(baseline.events_overlap(event, {**event, "type": "B"}))
        drag = {**event, "value": "CLICK_DRAG", "direction": "NORTH"}
        self.assertTrue(baseline.events_overlap(drag, {**drag, "direction": "ANY"}))
        self.assertFalse(baseline.events_overlap(drag, {**drag, "direction": "SOUTH"}))
        self.assertFalse(baseline.events_overlap(event, {**event, "type": ""}))

    def test_collisions_are_scoped_and_exclude_inactive_bindings(self):
        left = keymap("Example", binding("mesh.a"), binding("mesh.b", active=False))
        right = keymap("Example", binding("mesh.c"), space="VIEW_3D")
        third = keymap("Another", binding("mesh.d"))
        report = baseline.compare_snapshots(snapshot(left, right, third), snapshot(left, right, third))
        self.assertEqual(report["collisions"], {"base": [], "reference": []})

    def test_publication_redacts_paths_and_metadata_without_collapsing_ids(self):
        base = snapshot()
        base["metadata"] = {"caller": {"launcher": "/Users/example/private-launcher"}}
        ref = snapshot(keymap("Test", binding("wm.example", properties={
            "first": "Run /Users/example/a directory/private",
            "second": r"C:\Users\example\private",
            "third": "file:///Volumes/example/private",
            "fourth": "private-label",
        }), binding("wm.example", properties={"first": "/Users/example/another"})))
        redact = lambda text: text.replace("private-label", "neutral-label")
        report = baseline.compare_snapshots(base, ref, redact=redact)
        serialized = json.dumps(report)
        self.assertNotIn("example/private", serialized)
        self.assertNotIn("Users", serialized)
        self.assertNotIn("a directory", serialized)
        self.assertNotIn("private-label", serialized)
        self.assertNotIn("blender_id", serialized)
        self.assertIn("neutral-label", serialized)
        rows = [delta["after"] for delta in report["deltas"]]
        self.assertEqual(len({row["row_id"] for row in rows}), 2)
        self.assertTrue(all(row["properties"]["first"] == "<redacted-path>" for row in rows))
        ledger = baseline.build_ledger(report, development=ref)
        self.assertEqual([entry["development_after"]["exact_row_count"] for entry in ledger["entries"]], [1, 1])

    def test_ledger_assigns_each_delta_with_explicit_pending_verification(self):
        ref = snapshot(
            keymap("Mesh", binding("mesh.select_all"), binding("transform.translate", "B"),
                   binding("mesh.bevel", "C"), binding("object.convert", "D"),
                   binding("third_party.tool", "E"), binding("mesh.delete", "F", active=False)),
            keymap("Sculpt", binding("sculpt.brush_stroke")),
            keymap("3D View", binding("view3d.move")),
            keymap("3D View Tool: Move", binding("wm.tool_set_by_id", properties={"name": "builtin.move"})),
            keymap("UV Editor", binding("uv.unwrap")),
            keymap("Image Editor", binding("wm.call_menu_pie")),
            keymap("Window", binding("export_scene.gltf")),
        )
        report = baseline.compare_snapshots(snapshot(), ref)
        development = snapshot(keymap("Mesh", binding("mesh.select_all"), binding("mesh.select_all")))
        ledger = baseline.build_ledger(report, development=development)
        self.assertEqual(len(ledger["entries"]), len(report["deltas"]))
        self.assertEqual(len({entry["delta_id"] for entry in ledger["entries"]}), len(report["deltas"]))
        owners = {delta["after"]["target"]: entry["owner"]
                  for delta, entry in zip(report["deltas"], ledger["entries"])}
        self.assertEqual(owners, {
            "mesh.select_all": "03", "transform.translate": "03", "mesh.bevel": "04",
            "object.convert": "04", "third_party.tool": "05", "mesh.delete": "05",
            "sculpt.brush_stroke": "05", "view3d.move": "03", "wm.tool_set_by_id": "03",
            "uv.unwrap": "04", "wm.call_menu_pie": "05", "export_scene.gltf": "05",
        })
        for delta, entry in zip(report["deltas"], ledger["entries"]):
            self.assertEqual(entry["verification"], "pending")
            self.assertEqual(entry["provenance"], "unverified")
            self.assertTrue(entry["classification_reason"])
            count = 2 if delta["after"]["target"] == "mesh.select_all" else 0
            self.assertEqual(entry["development_after"]["exact_row_count"], count)
        with self.assertRaisesRegex(ValueError, "Classifier must assign one brief"):
            baseline.build_ledger(report, classifier=lambda delta: ("", "Unassigned"))
        with patch.object(baseline, "classify_delta", wraps=baseline.classify_delta) as classifier:
            baseline.build_ledger(report, classifier=classifier)
            self.assertEqual(classifier.call_count, len(report["deltas"]))


class NativeBaselineFixtureTests(unittest.TestCase):
    fixtures = Path(__file__).parent / "fixtures" / "deluxe_keymaps"

    @classmethod
    def setUpClass(cls):
        cls.header = json.loads((cls.fixtures / "reconciliation-ledger.json").read_text())
        cls.rows = [json.loads(line) for line in
                    (cls.fixtures / cls.header["entries_file"]).read_text().splitlines()]

    def test_native_ledger_owns_every_relevant_delta_row_once(self):
        by_id = {row["row_id"]: row for row in self.rows}
        self.assertEqual(len(by_id), len(self.rows))
        self.assertEqual(len(self.rows), self.header["row_count"])
        self.assertEqual(sum(self.header["owners"].values()), len(self.rows))
        links = set()
        for line in (self.fixtures / "comparison-deltas.jsonl").read_text().splitlines():
            delta = json.loads(line)
            links.add((delta["comparison"], delta["id"]))
            if delta["comparison"] != "industry-to-full":
                for side in ("before", "after"):
                    if delta[side] is not None:
                        self.assertIn(delta[side]["row_id"], by_id)
        for row in self.rows:
            self.assertIn(row["owner"], {"03", "04", "05"})
            self.assertTrue(row["classification_reason"])
            self.assertTrue(row["evidence"])
            self.assertTrue(all((item["comparison"], item["delta_id"]) in links
                                for item in row["evidence"]))
            self.assertNotIn("TypeError", row["binding"]["read_issues"].values())

    def test_sanitized_samples_round_trip_and_retain_modal_scope(self):
        samples = [json.loads((self.fixtures / name).read_text())
                   for name in ("sample-stock.json", "sample-full.json")]
        for sample in samples:
            baseline.validate_snapshot(sample)
            self.assertEqual(sample["visibility"], "sanitized-sample")
            serialized = json.dumps(sample)
            self.assertNotIn("/Users/", serialized)
            self.assertNotIn("userpref.blend", serialized)
            maps = baseline._maps(sample, "user")
            self.assertTrue(any(keymap["scope"]["is_modal"] for keymap in maps))
            self.assertTrue(all("native_order" in item for keymap in maps
                                for item in keymap["items"]))
        comparison = baseline.compare_snapshots(*samples)
        self.assertTrue(comparison["deltas"])
        self.assertEqual(comparison["precedence"], "unverified")

    def test_native_capture_controls_and_input_effect_receipt(self):
        manifest = json.loads((self.fixtures / "capture-manifest.json").read_text())
        controls = ("full", "no-preset", "no-overrides", "neither")
        self.assertTrue(all(manifest["controlled_checks"].values()))
        full = manifest["captures"]["full"]
        for name in controls:
            capture = manifest["captures"][name]
            self.assertTrue(capture["gui"])
            self.assertTrue(capture["source_preserved"])
            self.assertEqual(capture["loaded_addons"], full["loaded_addons"])
            self.assertEqual(capture["bluehole_owned_rows"], full["bluehole_owned_rows"])
            self.assertEqual(capture["input_outcomes"]["keyboard_dispatch_control"], 1)
        self.assertEqual(manifest["captures"]["no-preset"]["active_keyconfig"], "Blender")
        effect = json.loads((self.fixtures / "input-preference-effect.json").read_text())
        self.assertTrue(effect["sources_preserved"])
        self.assertEqual(effect["keyboard_dispatch_control"], 1)
        cases = {row["invert_mouse_zoom"]: row for row in effect["cases"]}
        distances = [cases[value]["after_distance"] - cases[value]["before_distance"]
                     for value in (False, True)]
        self.assertLess(distances[0] * distances[1], 0)


if __name__ == "__main__":
    unittest.main()
