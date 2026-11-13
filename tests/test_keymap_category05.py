"""Bulk structural comparison of the remaining Deluxe keymaps."""

from collections import Counter, defaultdict
from dataclasses import asdict
import importlib
import json
import sys
import types
import unittest
from unittest.mock import Mock, patch

from runtime_keymap_fakes import FakeItems, FakeProperties, FakeRuntime, row
from test_keymap_category04 import BASELINE, FIXTURES, ROOT, preset_properties, read_jsonl


class Category05CatalogTest(unittest.TestCase):

    def test_catalog_fields_order_toggles_and_coverage(self):
        receipt = json.loads((FIXTURES / 'deluxe_keymaps_category05/bulk-catalog.json').read_text())
        ledger = {r['row_id']: r for r in read_jsonl(BASELINE / 'reconciliation-ledger.jsonl')
                  if r['owner'] == '05'}
        self.assertEqual(len(ledger), 3175)

        def count(id_, capture):
            return ledger[id_]['presence'].get(capture, {}).get('user', 0)

        candidates = {id_ for id_ in ledger
                      if count(id_, 'full') > max(count(id_, 'stock'), count(id_, 'neither'))}
        catalog = receipt['catalog']
        exceptions = receipt['exceptions']
        existing = {id_ for id_, entry in catalog.items() if entry[-1] in ('existing', 'defaults')}
        self.assertEqual(existing, {id_ for id_, r in ledger.items()
                                   if count(id_, 'full')
                                   and r['runtime_coverage']['reference_bluehole_owned']})
        self.assertEqual(candidates, (catalog.keys() - existing) | exceptions.keys())
        self.assertFalse(catalog.keys() & exceptions.keys())
        self.assertEqual(receipt['stock_reductions'], {
            id_: count(id_, 'stock') - count(id_, 'full') for id_ in ledger
            if count(id_, 'stock') > count(id_, 'full')
        })
        self.assertEqual(set(receipt['absent_in_full_and_stock']), {
            id_ for id_ in ledger if not count(id_, 'full') and not count(id_, 'stock')
        })
        self.assertEqual(set(receipt['blue_hole_pies_absent_in_full']), {
            id_ for id_ in receipt['absent_in_full_and_stock']
            if ledger[id_]['runtime_coverage']['reference_bluehole_owned']
        })
        positions = defaultdict(set)
        for delta in read_jsonl(BASELINE / 'comparison-deltas.jsonl'):
            after = delta['after']
            if delta['comparison'] == 'stock-to-full' and after:
                positions[after['row_id']].add((after['map_order'], after['order']))

        runtime = FakeRuntime()
        runtime.bpy.types = types.SimpleNamespace(PropertyGroup=type('PropertyGroup', (), {}))
        prefs = types.SimpleNamespace(keymap=types.SimpleNamespace(enable_keymaps=True))
        bpy_props = types.ModuleType('bpy.props')
        bpy_props.BoolProperty = lambda **definition: definition
        prefix = '_bluehole_category05'
        with patch.dict(sys.modules, {'bpy': runtime.bpy, 'bpy.props': bpy_props,
                                      'rna_keymap_ui': types.SimpleNamespace(draw_kmi=Mock())}):
            def stub(suffix, path=None, **attrs):
                name = prefix + suffix
                module = types.ModuleType(name)
                if path is not None:
                    module.__path__ = [str(ROOT / path)]
                vars(module).update(attrs)
                sys.modules[name] = module

            def load(suffix):
                return importlib.import_module(prefix + '.' + suffix)

            stub('', '.')
            stub('.preferences', 'preferences')
            stub('.preferences.addon', 'preferences/addon')
            stub('.preferences.prefs', prefs=lambda: prefs)
            stub('.Lib.commonUtils.runtime.diagnostics')
            stub('.debug.debug_flags')
            stub('.operators.ui_ops', WM_OT_BH_ToggleUISection=types.SimpleNamespace(
                bl_idname='test.toggle'), draw_action_feature_keymaps_dropdown_state={})
            self.check_registration(runtime, prefs, load, ledger, catalog, positions)

    def check_registration(self, runtime, prefs, load, ledger, catalog, positions):
        adapter = load('keymaps.keymap_action_utils')
        utils = load('keymaps.keymap_utils')
        registers = {}
        for category in ('pipeline', 'sculpt', 'other', 'pie'):
            if category == 'pie':
                props = load('preferences.addon.pie_props').PiePG
                registers[category] = load('keymaps.pie.pie_keymaps_register')
            else:
                module = load(f'preferences.addon.keymaps.keymap_props_{category}')
                props = getattr(module, f'{category.title()}KeymapPG')
                registers[category] = load(f'keymaps.{category}_keymaps_register')
            settings = types.SimpleNamespace(**{
                key: definition['default'] for key, definition in props.__annotations__.items()
            })
            setattr(prefs if category == 'pie' else prefs.keymap, category, settings)
        # Deluxe uses the existing Pie switch alongside the main Keymaps switch.
        prefs.pie.enable_pie_menus = True
        actions = {
            'pipeline': registers['pipeline'].get_enabled_pipeline_actions(),
            'sculpt': registers['sculpt'].get_enabled_sculpt_actions(),
            'other': load('actions.actions.keymaps.other_actions').OTHER_ACTIONS,
            'pie': registers['pie'].get_enabled_pie_actions(),
        }
        preset = preset_properties()
        keys_by_category = defaultdict(list)
        emitted = {}
        expected = defaultdict(list)
        map_roles = {}
        for id_, (category, group, map_order, order, source) in catalog.items():
            ref = ledger[id_]['binding']
            scope = utils.KeymapScope(**ref['scope'])
            event = utils.KeymapEvent(**ref['event'])
            key = (scope, event, ref['target'])
            self.assertNotIn(key, emitted, id_)
            emitted[key] = (id_, ref)
            keys_by_category[category].append(key)
            if source in ('preset', 'ledger'):
                self.assertIn((map_order, order), positions[id_], id_)
            expected[scope, category].append((order, key, ref['active']))

            if scope not in map_roles:
                stock = runtime.map('default', scope.name, space=scope.space_type)
                provider = runtime.map('addon', scope.name, space=scope.space_type)
                map_roles[scope] = stock, provider
                stock.keymap_items.append_fixture(row('wm.inherited_stock', key='F23'))
                provider.keymap_items.append_fixture(row('wm.inherited_provider', key='F24'))

        def canonical(value):
            if isinstance(value, (tuple, list)):
                return tuple(canonical(part) for part in value)
            return value

        for category, category_actions in actions.items():
            observed = []
            for action in category_actions:
                for binding in action.keymap_bindings:
                    scope = adapter._binding_scope(binding, None)
                    event = adapter._event(binding)
                    key = (scope, event, action.get_idname())
                    id_, ref = emitted[key]
                    self.assertEqual(asdict(scope), ref['scope'], id_)
                    self.assertEqual(asdict(event), ref['event'], id_)
                    self.assertEqual(binding.active, ref['active'], id_)
                    _, group, _, _, source = catalog[id_]
                    properties = action.get_props()
                    effective = {k: canonical(v) for k, v in ref['properties'].items()}
                    if source == 'preset':
                        preset_key = (scope.name, scope.space_type, scope.region_type,
                                      ref['target'], event.type, event.value)
                        self.assertTrue(any(
                            properties.keys() == candidate.keys()
                            and all(preset_event.get(field, default) == getattr(event, field)
                                    for field, default in (
                                        ('any', False), ('shift', False), ('ctrl', False),
                                        ('alt', False), ('oskey', False), ('repeat', False),
                                        ('direction', 'ANY'), ('key_modifier', 'NONE')))
                            for preset_event, candidate in preset[preset_key]
                        ), id_)
                        self.assertLessEqual(properties.items(), effective.items(), id_)
                    elif source == 'defaults':
                        self.assertFalse(properties, id_)
                    else:
                        self.assertEqual(properties, effective, id_)
                    if category in ('sculpt', 'pipeline') and group != 'save-as':
                        module = load(f'actions.actions.keymaps.{category}')
                        get_group = getattr(module, f'get_{category}_group_actions')
                        self.assertIn(action, get_group(group), id_)
                    observed.append(key)
            self.assertCountEqual(observed, keys_by_category[category])

        create = FakeItems.new

        def with_schema(items, idname, *args, **kwargs):
            fields = {k: v for k, v in kwargs.items() if k != 'head'}
            native_type = 'MOUSE' if any(word in kwargs['type'] for word in ('MOUSE', 'TRACKPAD')) else 'KEYBOARD'
            event = utils.KeymapEvent(**fields, map_type=native_type)
            key = (utils.capture_scope(items.map), event, idname)
            _, ref = emitted[key]
            schema = {k: canonical(v) for k, v in ref['properties'].items()}
            with patch.object(items, 'new_prop_schema', schema):
                return create(items, idname, *args, **kwargs)

        def fake_property(properties, name):
            # Native RNA's Save As copy field shadows the dict method in the fake.
            if name == 'copy' and name in properties:
                return properties[name]
            return object.__getattribute__(properties, name)

        with patch.object(FakeItems, 'new', with_schema), patch.object(
                FakeProperties, '__getattribute__', fake_property):
            for category, register in registers.items():
                utils.bind_category_pairs(register.KEYMAP_CATEGORY,
                                          getattr(register, f'registered_{category}_keymaps'))
                actual_count = register.register()
                self.assertEqual(actual_count, len(keys_by_category[category]),
                                 (category, [d for d in utils.runtime_diagnostics() if d.status != 'applied']))
            self.assertFalse([d for d in utils.runtime_diagnostics() if d.status != 'applied'])
            for keymap in runtime.configs.user.keymaps:
                scope = utils.capture_scope(keymap)
                owned = [item for item in keymap.keymap_items if not item.idname.startswith('wm.inherited_')]
                actual = defaultdict(list)
                for item in owned:
                    key = (scope, utils.capture_event(item), item.idname)
                    id_, ref = emitted[key]
                    self.assertEqual(dict(utils.capture_target(item).properties),
                                     {k: canonical(v) for k, v in ref['properties'].items()}, id_)
                    category = catalog[id_][0]
                    actual[category].append((key, item.active))
                for category in registers:
                    self.assertEqual(actual[category], [
                        (key, active) for _, key, active in sorted(expected[scope, category])
                    ], (scope, category))

            counts = Counter((category, group) for category, group, *_ in catalog.values())
            for category in ('pipeline', 'sculpt'):
                module = load(f'actions.actions.keymaps.{category}')
                settings = getattr(prefs.keymap, category)
                total = len(keys_by_category[category])
                for group, toggle in getattr(module, f'{category.upper()}_KEYMAP_GROUPS').items():
                    setattr(settings, toggle, False)
                    self.assertEqual(registers[category].register(), total - counts[category, group])
                    setattr(settings, toggle, True)
                setattr(settings, f'enable_{category}_keymaps', False)
                self.assertEqual(registers[category].register(), counts[category, 'save-as'])
            prefs.keymap.other.enable_other_keymaps = False
            self.assertEqual(registers['other'].register(), 0)
            prefs.pie.enable_editor_pie_shortcuts = False
            self.assertEqual(registers['pie'].register(), counts['pie', 'blue-hole'])
            prefs.pie.enable_pie_menus = False
            self.assertEqual(registers['pie'].register(), 0)
            registers['pipeline'].unregister()

        self.assertEqual(utils.runtime_stats()['features'], 0)
        self.assertEqual(utils.runtime_stats()['owned'], 0)
        for keymap in runtime.configs.user.keymaps:
            self.assertEqual([item.idname for item in keymap.keymap_items],
                             ['wm.inherited_provider', 'wm.inherited_stock'])
