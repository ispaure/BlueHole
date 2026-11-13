"""Read-only capture and comparison of Blender keymap candidates.

Snapshots are private. The user role contains candidate bindings, including inactive
rows. Blender's context, tool handlers, operator poll and event dispatch determine
precedence. The comparison does not test those conditions.
"""

import argparse
from collections import Counter, defaultdict
from collections.abc import Mapping
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import re
import sys
from tempfile import NamedTemporaryFile


SCHEMA_VERSION = 1
ROLES = ("default", "active", "addon", "user")
MODIFIERS = ("shift", "ctrl", "alt", "oskey", "hyper")
RNA_MATH_ARRAYS = frozenset({"Color", "Euler", "Matrix", "Quaternion", "Vector"})
EVENT_FIELDS = ("type", "value", "any", *MODIFIERS, "key_modifier", "direction", "repeat", "map_type")
SCOPE_FIELDS = ("name", "space_type", "region_type", "is_modal", "is_tool")
INPUT_FIELDS = (
    "use_emulate_numpad", "use_mouse_emulate_3_button", "mouse_emulate_3_button_modifier",
    "use_multitouch_gestures", "mouse_double_click_time", "drag_threshold", "drag_threshold_mouse",
    "drag_threshold_tablet", "move_threshold", "view_zoom_method", "view_zoom_axis",
    "view_rotate_method", "invert_mouse_zoom", "invert_zoom_wheel", "touchpad_scroll_direction",
    "use_mouse_depth_navigate", "use_zoom_to_mouse", "use_rotate_around_active",
    "view_rotate_sensitivity_turntable", "view_rotate_sensitivity_trackball", "ndof_sensitivity",
)
SEMANTIC_FIELDS = ("scope", "target", "event", "properties", "active", "read_issues")
ROW_EVIDENCE = "candidate-effective keyconfig"
PATH_PATTERN = re.compile(r"(?<![\w./\\])(?:[A-Za-z]:[/\\]|[/\\]{2}|~/|file:/|/[^/\s])", re.IGNORECASE)


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(",", ":"))


def _digest(value):
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _json_value(value):
    """Convert safe scalars and collections without using object repr."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Non-finite number")
        return 0.0 if value == 0 else value
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    if isinstance(value, Mapping) and all(isinstance(key, str) for key in value):
        return {key: _json_value(entry) for key, entry in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(entry) for entry in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_json_value(entry) for entry in value), key=_canonical)
    raise TypeError("Unsupported value type")


def _rna_array(value, math_array_types):
    """Preserve numeric array dimensions, including mathutils matrix rows."""
    value_type = type(value)
    if value_type in (bool, int, float):
        return _json_value(value)
    if value_type in (list, tuple, *math_array_types) or value_type.__name__ == "bpy_prop_array":
        return [_rna_array(entry, math_array_types) for entry in value]
    raise TypeError("Unsupported RNA array value type")


def _redact_strings(value, redact):
    if isinstance(value, str):
        result = redact(value)
        if not isinstance(result, str):
            raise TypeError("Redaction callback must return a string")
        return result
    if isinstance(value, list):
        return [_redact_strings(entry, redact) for entry in value]
    if isinstance(value, dict):
        return {_redact_strings(key, redact): _redact_strings(entry, redact) for key, entry in value.items()}
    return value


def _read_properties(properties, *, operator_properties=()):
    """Read RNA getters, including defaults and known-safe macro property groups."""
    issues = {}
    mathutils = sys.modules.get("mathutils")
    math_array_types = tuple(getattr(mathutils, name) for name in RNA_MATH_ARRAYS if hasattr(mathutils, name))

    def read_group(group, prefix=""):
        values = {}
        for prop in group.bl_rna.properties:
            name = prop.identifier
            if name == "rna_type":
                continue
            path = prefix + name
            try:
                if prop.type == "POINTER":
                    fixed_type = getattr(prop, "fixed_type", None) if operator_properties else None
                    while fixed_type is not None and fixed_type.identifier != "OperatorProperties":
                        fixed_type = fixed_type.base
                    if not operator_properties or fixed_type is None:
                        issues[path] = "pointer_skipped"
                        continue
                    value = getattr(group, name)
                    if isinstance(value, operator_properties):
                        values[name] = read_group(value, path + ".")
                    else:
                        issues[path] = "pointer_skipped"
                elif prop.type == "COLLECTION":
                    issues[path] = "collection_skipped"
                else:
                    value = getattr(group, name)
                    if prop.type == "ENUM" and value == "":
                        issues[path] = "RNA_enum_unresolved"
                    if getattr(prop, "is_array", False):
                        values[name] = _rna_array(value, math_array_types)
                    else:
                        values[name] = _json_value(value)
            except (AttributeError, KeyError, ReferenceError, RuntimeError, TypeError, ValueError) as error:
                issues[path] = type(error).__name__
        return values

    if properties is None:
        return {}, {"properties": "RNA_unavailable"}
    if getattr(properties, "bl_rna", None) is None:
        return {}, {"properties": "RNA_schema_unavailable"}
    return read_group(properties), issues


def _capture_map(keymap, operator_properties):
    scope = {field: getattr(keymap, field, None) for field in SCOPE_FIELDS}
    items = []
    for item in keymap.keymap_items:
        issues = {}
        event = {}
        for field in EVENT_FIELDS:
            try:
                event[field] = getattr(item, field)
                if event[field] == "":
                    issues[f"event.{field}"] = "RNA_enum_unresolved"
            except AttributeError:
                if field in {"type", "value"}:
                    event[field] = ""
                    issues[f"event.{field}"] = "RNA_event_unavailable"
            except (ReferenceError, RuntimeError, ValueError) as error:
                if field in {"type", "value"}:
                    event[field] = ""
                issues[f"event.{field}"] = type(error).__name__
        target_field = "propvalue" if scope["is_modal"] else "idname"
        try:
            target = getattr(item, target_field)
            if not target or (scope["is_modal"] and target == "NONE"):
                issues["target"] = "RNA_target_unresolved"
        except (AttributeError, ReferenceError, RuntimeError, ValueError) as error:
            target = None
            issues["target"] = type(error).__name__
        properties = {}
        if not scope["is_modal"]:
            try:
                properties, property_issues = _read_properties(
                    item.properties, operator_properties=operator_properties,
                )
                issues.update(property_issues)
            except (AttributeError, ReferenceError, RuntimeError, ValueError) as error:
                issues["properties"] = type(error).__name__
        items.append({
            "target": target,
            "event": event,
            "active": item.active,
            "properties": properties,
            "read_issues": issues,
            "is_user_defined": item.is_user_defined,
            "is_user_modified": item.is_user_modified,
            "blender_id": item.id,
        })
    return {
        "scope": scope,
        "is_user_modified": keymap.is_user_modified,
        "is_tool_source": "RNA" if scope["is_tool"] is not None else "unavailable",
        "tool_name_hint": " Tool: " in scope["name"],
        "items": items,
    }


def _capture_addons(preferences):
    configured = {addon.module for addon in preferences.addons}
    loaded = {name for name, module in tuple(sys.modules.items())
              if module is not None and getattr(module, "__addon_enabled__", False) is True}
    addon_utils = sys.modules.get("addon_utils")
    cached = getattr(addon_utils, "addons_fake_modules", {})
    inventory = []
    for name in sorted(configured | loaded | set(cached)):
        module = sys.modules.get(name)
        info = getattr(module, "bl_info", {}) or getattr(cached.get(name), "bl_info", {})
        inventory.append({
            "module": name,
            "version": info.get("version") if isinstance(info, dict) else None,
            "configured": name in configured,
            "loaded": name in loaded,
        })
    return inventory


def capture_snapshot(metadata=None, *, redact=None):
    """Capture keyconfigs as currently exposed by Blender and return a private snapshot.

    Call after startup in the context being measured. Caller metadata can record
    startup timing, readiness observations and controlled launch settings.
    """
    try:
        import bpy
    except ImportError:
        raise RuntimeError("Capture must run in Blender after the keyconfig initializes") from None

    wm = bpy.context.window_manager
    if wm is None:
        raise RuntimeError("No Blender window manager is available for keymap capture")
    configs = wm.keyconfigs
    roles = {}
    seen = {}
    for role in ROLES:
        config = getattr(configs, role)
        if config is None:
            roles[role] = {"available": False, "name": None, "alias_of": None, "maps": []}
            continue
        pointer = config.as_pointer()
        alias = seen.get(pointer)
        seen.setdefault(pointer, role)
        roles[role] = {
            "available": True, "name": config.name, "alias_of": alias,
            "maps": [] if alias else [
                _capture_map(keymap, bpy.types.OperatorProperties) for keymap in config.keymaps
            ],
        }

    preferences = bpy.context.preferences
    options, option_issues = _read_properties(configs.active.preferences) if configs.active else ({}, {})
    app_fields = ("version", "version_string", "version_cycle", "build_hash", "build_branch",
                  "build_commit_date", "build_commit_time", "build_platform", "background")
    details = {
        "blender": {field: getattr(bpy.app, field) for field in app_fields if hasattr(bpy.app, field)},
        "python": sys.version_info[:3],
        "gui": not bpy.app.background,
        "window_count": len(wm.windows),
        "active_config": roles["active"]["name"],
        "active_options": options,
        "active_option_read_issues": option_issues,
        "inputs": {field: getattr(preferences.inputs, field) for field in INPUT_FIELDS
                   if hasattr(preferences.inputs, field)},
        "addons": _capture_addons(preferences),
        "addon_inventory_scope": "Configured, loaded, and already cached add-on metadata",
        "caller": metadata if metadata is not None else {},
    }
    details = _json_value(details)
    if redact is not None:
        details = _redact_strings(details, redact)
    return normalize_snapshot({"schema_version": SCHEMA_VERSION, "metadata": details, "roles": roles})


def _semantic_row(row):
    return {field: row[field] for field in SEMANTIC_FIELDS}


def _validate_shape(snapshot):
    if (not isinstance(snapshot, dict) or type(snapshot.get("schema_version")) is not int
            or snapshot["schema_version"] != SCHEMA_VERSION):
        raise ValueError("Expected a keymap snapshot with schema_version 1")
    if not isinstance(snapshot.get("metadata", {}), dict):
        raise ValueError("Snapshot metadata must be an object")
    roles = snapshot.get("roles")
    if not isinstance(roles, dict) or set(roles) != set(ROLES):
        raise ValueError("Snapshot must contain default, active, addon and user roles")
    for role in ROLES:
        config = roles[role]
        if not isinstance(config, dict) or not isinstance(config.get("maps"), list):
            raise ValueError(f"Expected a map list for the {role} role")
        if type(config.get("available", True)) is not bool:
            raise ValueError(f"Invalid availability for the {role} role")
        alias = config.get("alias_of")
        if alias is not None:
            if alias not in ROLES[:ROLES.index(role)] or config["maps"]:
                raise ValueError(f"Invalid alias for the {role} role")
            if not config.get("available", True) or not roles[alias].get("available", True):
                raise ValueError(f"Unavailable configuration alias for the {role} role")
        if not config.get("available", True) and config["maps"]:
            raise ValueError(f"Unavailable configuration has maps for the {role} role")
        for keymap in config["maps"]:
            if not isinstance(keymap, dict) or not isinstance(keymap.get("items"), list):
                raise ValueError(f"Expected an item list for a map in the {role} role")
            scope = keymap.get("scope")
            if not isinstance(scope, dict) or any(
                not isinstance(scope.get(field), str) for field in SCOPE_FIELDS[:3]
            ) or type(scope.get("is_modal")) is not bool or type(scope.get("is_tool")) not in (type(None), bool):
                raise ValueError(f"Invalid map scope in the {role} role")
            for item in keymap["items"]:
                event = item.get("event") if isinstance(item, dict) else None
                if not isinstance(event, dict) or not all(isinstance(event.get(field), str)
                                                          for field in ("type", "value")):
                    raise ValueError(f"Invalid keymap event in the {role} role")
                if (item.get("target") is not None and not isinstance(item["target"], str)
                        or type(item.get("active")) is not bool
                        or not isinstance(item.get("properties", {}), dict)
                        or not isinstance(item.get("read_issues", {}), dict)):
                    raise ValueError(f"Invalid keymap item in the {role} role")
                if any(field in event and (
                    type(event[field]) not in (bool, int) or event[field] not in (-1, 0, 1)
                ) for field in MODIFIERS):
                    raise ValueError(f"Invalid keymap modifier in the {role} role")


def normalize_snapshot(snapshot):
    """Return a normalized copy. List positions are the source of captured order."""
    _validate_shape(snapshot)
    normalized = _json_value(snapshot)
    normalized["visibility"] = "private"
    normalized.setdefault("metadata", {})
    for role in ROLES:
        counts = Counter()
        config = normalized["roles"][role]
        config.setdefault("available", True)
        config.setdefault("alias_of", None)
        for map_order, keymap in enumerate(config["maps"]):
            scope = {field: keymap["scope"].get(field) for field in SCOPE_FIELDS}
            keymap["scope"] = scope
            keymap["order"] = map_order
            for order, item in enumerate(keymap["items"]):
                item.setdefault("target", None)
                item.setdefault("properties", {})
                item.setdefault("read_issues", {})
                item["order"] = order
                row_id = _digest(_semantic_row({**item, "scope": scope}))
                item["row_id"] = row_id
                item["occurrence_id"] = _digest([row_id, counts[row_id]])
                counts[row_id] += 1
    return normalized


def validate_snapshot(snapshot):
    """Raise ValueError for an invalid snapshot or inconsistent supplied IDs/order."""
    _validated_snapshot(snapshot)


def _validated_snapshot(snapshot):
    try:
        normalized = normalize_snapshot(snapshot)
    except TypeError as error:
        raise ValueError("Snapshot contains an unsupported value") from error
    def inconsistent(actual, expected):
        return type(actual) is not type(expected) or actual != expected

    for role in ROLES:
        for keymap, expected in zip(snapshot["roles"][role]["maps"], normalized["roles"][role]["maps"]):
            if inconsistent(keymap.get("order", expected["order"]), expected["order"]):
                raise ValueError(f"Inconsistent map order in the {role} role")
            for item, normalized_item in zip(keymap["items"], expected["items"]):
                for field in ("row_id", "occurrence_id", "order"):
                    if inconsistent(item.get(field, normalized_item[field]), normalized_item[field]):
                        raise ValueError(f"Inconsistent {field} in the {role} role")
    return normalized


def _write_json(path, payload):
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def write_snapshot(path, snapshot):
    """Atomically write a normalized private snapshot with owner-only permissions."""
    path = Path(path)
    temporary = None
    try:
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(normalize_snapshot(snapshot), handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _maps(snapshot, role):
    config = snapshot["roles"][role]
    if not config["available"]:
        raise ValueError(f"The {role} keyconfig role is unavailable")
    while config["alias_of"] is not None:
        config = snapshot["roles"][config["alias_of"]]
    return config["maps"]


def _rows(maps):
    return [
        {**item, "scope": keymap["scope"], "map_order": keymap["order"]}
        for keymap in maps for item in keymap["items"]
    ]


def _public_row(row):
    fields = (*SEMANTIC_FIELDS, "row_id", "occurrence_id", "map_order", "order",
              "is_user_defined", "is_user_modified")
    return {field: row[field] for field in fields if field in row}


def _publish(value, redact):
    def safe_string(value):
        value = redact(value) if redact is not None else value
        if not isinstance(value, str):
            raise TypeError("Redaction callback must return a string")
        return "<redacted-path>" if PATH_PATTERN.search(value) else value

    return _redact_strings(value, safe_string)


def events_overlap(left, right):
    """Test literal event overlap, independent of Blender's runtime event remapping."""
    def compatible(field, wildcard):
        a, b = left.get(field), right.get(field)
        return a == b or a in wildcard or b in wildcard

    if not left.get("type") or not right.get("type") or not left.get("value") or not right.get("value"):
        return False
    if not compatible("type", (None, "ANY")) or not compatible("value", (None, "ANY")):
        return False
    if left.get("value") == right.get("value") == "CLICK_DRAG":
        if not compatible("direction", (None, "ANY")):
            return False
    if not compatible("key_modifier", (None, "NONE")):
        return False
    if left.get("any") or right.get("any"):
        return True
    return all(compatible(field, (None, -1)) for field in MODIFIERS)


def _collisions(rows):
    groups = defaultdict(list)
    for row in rows:
        if row["active"]:
            groups[_canonical(row["scope"])].append(row)
    for group in groups.values():
        for first, second in combinations(group, 2):
            if events_overlap(first["event"], second["event"]):
                yield {
                    "scope": first["scope"],
                    "bindings": [
                        {field: row[field] for field in ("occurrence_id", "target", "event", "map_order", "order")}
                        for row in (first, second)
                    ],
                }


def _delta(kind, before=None, after=None):
    return {
        "id": _digest([kind, before and before["occurrence_id"], after and after["occurrence_id"]]),
        "kind": kind,
        "before": _public_row(before) if before is not None else None,
        "after": _public_row(after) if after is not None else None,
        "provenance": "unverified",
    }


def _group_rows(rows, fields):
    groups = defaultdict(list)
    for row in rows:
        groups[_canonical([row[field] for field in fields])].append(row)
    return groups


def _row_deltas(before, after):
    base = {row["occurrence_id"]: row for row in before}
    reference = {row["occurrence_id"]: row for row in after}
    shared = base.keys() & reference.keys()

    # Measure relative order among retained occurrences. An insertion shifts absolute
    # indices, but it does not move the retained rows relative to one another.
    old_groups = _group_rows((row for row in before if row["occurrence_id"] in shared), ("scope",))
    new_groups = _group_rows((row for row in after if row["occurrence_id"] in shared), ("scope",))
    for scope, old_group in old_groups.items():
        for old, new in zip(old_group, new_groups[scope]):
            if old["occurrence_id"] != new["occurrence_id"]:
                yield _delta("reordered", old, reference[old["occurrence_id"]])

    base = {key: row for key, row in base.items() if key not in shared}
    reference = {key: row for key, row in reference.items() if key not in shared}
    # Pair only unambiguous observed transitions within a scope. Pairing describes
    # the difference between snapshots and does not establish edit history.
    rules = (
        (("target", "event", "properties", "read_issues"), "activation"),
        (("target", "event"), "changed"),
        (("target", "properties", "read_issues"), "rebound"),
        (("event",), "replacement_candidate"),
    )
    for fields, kind in rules:
        old_groups = _group_rows(base.values(), ("scope", *fields))
        new_groups = _group_rows(reference.values(), ("scope", *fields))
        for key, old_group in old_groups.items():
            new_group = new_groups.get(key, ())
            if len(old_group) != 1 or len(new_group) != 1:
                continue
            old, new = old_group[0], new_group[0]
            if kind == "activation":
                yield _delta("enabled" if new["active"] else "disabled", old, new)
            else:
                yield _delta(kind, old, new)
            del base[old["occurrence_id"]]
            del reference[new["occurrence_id"]]
    yield from (_delta("removed", before=row) for row in base.values())
    yield from (_delta("added", after=row) for row in reference.values())


def _map_changes(base_maps, reference_maps):
    old_groups = _group_rows(base_maps, ("scope",))
    new_groups = _group_rows(reference_maps, ("scope",))
    for scope in sorted(old_groups.keys() | new_groups.keys()):
        old = [keymap["order"] for keymap in old_groups.get(scope, ())]
        new = [keymap["order"] for keymap in new_groups.get(scope, ())]
        if old != new:
            yield {"scope": json.loads(scope)[0], "before_order": old, "after_order": new}


def compare_snapshots(base, reference, *, role="user", redact=None):
    """Report multiset differences and same-scope overlaps without selecting winners.

    IDs hash private semantic values so exact matches survive display redaction.
    The report excludes raw capture metadata and config names. Supply a redactor
    for private names or identifiers beyond machine paths.
    """
    if role not in ROLES:
        raise ValueError("Unknown keyconfig role")
    base_maps = _maps(_validated_snapshot(base), role)
    reference_maps = _maps(_validated_snapshot(reference), role)
    before, after = _rows(base_maps), _rows(reference_maps)
    deltas = list(_row_deltas(before, after))
    collisions = {"base": list(_collisions(before)), "reference": list(_collisions(after))}
    report = {
        "schema_version": SCHEMA_VERSION,
        "role": role,
        "evidence": ROW_EVIDENCE if role == "user" else f"{role} keyconfig rows",
        "precedence": "unverified",
        "collision_scope": "Active bindings with overlapping literal event fields in the same recorded map scope",
        "deltas": deltas,
        "collisions": collisions,
        "map_changes": list(_map_changes(base_maps, reference_maps)),
        "summary": {
            "base_rows": len(before),
            "reference_rows": len(after),
            "deltas": dict(sorted(Counter(delta["kind"] for delta in deltas).items())),
            "base_collision_pairs": len(collisions["base"]),
            "reference_collision_pairs": len(collisions["reference"]),
        },
    }
    return _publish(report, redact)


NAVIGATION_OPERATORS = frozenset({
    "view3d.dolly", "view3d.localview", "view3d.move", "view3d.rotate", "view3d.smoothview",
    "view3d.view_all", "view3d.view_axis", "view3d.view_camera", "view3d.view_center_cursor",
    "view3d.view_center_lock", "view3d.view_center_pick", "view3d.view_lock_clear",
    "view3d.view_lock_to_active", "view3d.view_orbit", "view3d.view_pan", "view3d.view_roll",
    "view3d.view_selected", "view3d.walk", "view3d.fly", "view3d.zoom", "view3d.zoom_border",
    "image.view_all", "image.view_pan", "image.view_selected", "image.view_zoom",
})
SELECTION_FAMILIES = frozenset({"view3d", "object", "mesh", "uv"})
MODELLING_FAMILIES = frozenset({"object", "mesh", "uv"})
MODELLING_MODAL_MAPS = frozenset({"Bevel Modal Map", "Custom Normals Modal Map", "Knife Tool Modal Map"})
EDITORS_03 = frozenset({"EMPTY", "VIEW_3D", "IMAGE_EDITOR"})


def classify_delta(delta):
    """Assign one brief through explicit, reviewable rules."""
    before, after = delta["before"], delta["after"]
    row = after if after is not None else before
    if any(entry is not None and not entry["active"] for entry in (before, after)):
        return "05", "Inactive binding or activation transition"

    scope = row["scope"]
    name = scope["name"]
    target = row["target"] or ""
    family, _, action = target.partition(".")
    properties = row["properties"]
    tool = properties.get("name") if target == "wm.tool_set_by_id" else None
    if (target == "wm.call_menu_pie" or family in {"paint", "sculpt", "brush", "export_scene", "import_scene"}
            or name == "Sculpt" or " Tool: Sculpt" in name or name.startswith("Sculpt ")):
        return "05", "Pie, sculpt, paint or pipeline operator family"
    if scope["space_type"] in EDITORS_03:
        if target in NAVIGATION_OPERATORS or target.startswith("view3d.ndof_"):
            return "03", "Navigation operator family"
        if scope["is_modal"] and name.startswith("View3D ") and any(
            name == f"View3D {navigation} Modal" for navigation in ("Dolly", "Fly", "Move", "Rotate", "Walk", "Zoom")
        ):
            return "03", "Viewport navigation modal map"
        if family in SELECTION_FAMILIES and (action == "select" or action.startswith("select_")):
            return "03", "Selection operator family"
        if family == "transform" or name == "Transform Modal Map" or tool in (
            "builtin.move", "builtin.rotate", "builtin.scale", "builtin.transform",
        ):
            return "03", "Transform operator, tool or modal map"
        if isinstance(tool, str) and tool.startswith("builtin.select"):
            return "03", "Selection tool"
    if scope["space_type"] in EDITORS_03 and (family in MODELLING_FAMILIES or name in MODELLING_MODAL_MAPS):
        return "04", "Object, Mesh or UV operator family or modelling modal map"
    return "05", "Sculpt, pipeline, pies, other editors, global or unresolved ownership"


def build_ledger(comparison, development=None, *, classifier=classify_delta):
    """Assign each delta to a brief and optionally count exact observed development rows."""
    role = comparison["role"]
    development_rows = None
    if development is not None:
        development_rows = _rows(_maps(_validated_snapshot(development), role))
    matches = Counter(row["row_id"] for row in development_rows or ())
    exact_occurrences = {row["occurrence_id"] for row in development_rows or ()}
    ledger = []
    seen = set()
    for delta in comparison["deltas"]:
        if delta["id"] in seen:
            raise ValueError("Comparison contains duplicate delta IDs")
        seen.add(delta["id"])
        owner, reason = classifier(delta)
        if owner not in {"03", "04", "05"} or not reason:
            raise ValueError("Classifier must assign one brief and supply a reason")
        entry = {
            "delta_id": delta["id"],
            "owner": owner,
            "classification_reason": reason,
            "verification": "pending",
            "provenance": "unverified",
        }
        if development_rows is not None:
            for side in ("before", "after"):
                row = delta[side]
                if row is not None:
                    entry[f"development_{side}"] = {
                        "exact_row_count": matches[row["row_id"]],
                        "exact_occurrence_present": row["occurrence_id"] in exact_occurrences,
                        "read_issues_present": bool(row["read_issues"]),
                    }
        ledger.append(entry)
    return {
        "schema_version": SCHEMA_VERSION,
        "role": role,
        "coverage": "Exact captured row matches only. Dispatch and origin remain unverified.",
        "entries": ledger,
    }


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
        if "--" in argv:
            argv = argv[argv.index("--") + 1:]
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--capture", type=Path, metavar="PRIVATE_OUTPUT")
    mode.add_argument("--compare", type=Path, nargs=2, metavar=("BASE", "REFERENCE"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.compare and args.output is None:
        parser.error("--compare requires --output")
    if args.capture and args.output is not None:
        parser.error("--capture takes its output path directly")
    try:
        if args.capture:
            write_snapshot(args.capture, capture_snapshot())
        else:
            snapshots = [json.loads(path.read_text(encoding="utf-8")) for path in args.compare]
            comparison = compare_snapshots(*snapshots)
            _write_json(args.output, {**comparison, "ledger": build_ledger(comparison)})
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        parser.exit(1, f"{parser.prog}: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
