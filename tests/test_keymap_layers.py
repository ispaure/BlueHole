"""The catalog compiler and schema must be usable without Blender."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LayerTests(unittest.TestCase):
    def test_compile_without_importing_blender_and_keep_all_declared_requests(self):
        subprocess.run([sys.executable, '-c', '''
import sys
from types import SimpleNamespace
from keymaps.catalog_inventory import read_catalog
from keymaps.catalog_plan import CatalogPlanner, profile_assignment_id
from keymaps.deluxe_schema import validate_catalog
catalog, _ = read_catalog('keymaps/deluxe-defaults.json')
validate_catalog(catalog)
state, groups = CatalogPlanner(catalog).plan(catalog, SimpleNamespace(keymap=SimpleNamespace(enable_keymaps=True)))
ids = {profile_assignment_id(request.request_id) for requests in groups.values() for request in requests}
expected = {id_ for id_, row in catalog['assignments'].items()
            if row.get('enabled', True) and state[row['section']]}
assert ids == expected, (len(ids), len(expected))
assert 'bpy' not in sys.modules
'''], cwd=ROOT, check=True)

    def test_dopesheet_frame_jump_companions_follow_the_editable_routes(self):
        from types import SimpleNamespace
        from keymaps.catalog_inventory import read_catalog
        from keymaps.catalog_plan import CatalogPlanner, profile_assignment_id
        from keymaps.descriptors import KeymapScope

        catalog, _ = read_catalog(ROOT / 'keymaps/deluxe-defaults.json')
        planner = CatalogPlanner(catalog)
        settings = SimpleNamespace(keymap=SimpleNamespace(enable_keymaps=True))

        def companions():
            _, groups = planner.plan(catalog, settings)
            return [request for requests in groups.values() for request in requests
                    if request.target.idname == 'wm.bh_dopesheet_frame_jump']

        routes = companions()
        self.assertEqual(len(routes), 4)
        self.assertEqual({(r.event.type, r.event.ctrl, r.event.oskey) for r in routes},
                         {(key, ctrl, oskey) for key in ('LEFT_ARROW', 'RIGHT_ARROW')
                          for ctrl, oskey in ((True, False), (False, True))})
        for route in routes:
            self.assertEqual(route.scope, KeymapScope('Frames'))
            self.assertEqual(dict(route.target.properties), {'end': route.event.type == 'RIGHT_ARROW'})
        assignment = catalog['assignments'][profile_assignment_id(routes[0].request_id)]
        catalog['events'][assignment['event']] = {'type': 'F18'}
        self.assertEqual(len(companions()), 3)
        settings.keymap.enable_keymaps = False
        self.assertEqual(companions(), [])

    def test_node_socket_companion_follows_the_reviewed_drag_chain(self):
        from types import SimpleNamespace
        from keymaps.catalog_inventory import read_catalog
        from keymaps.catalog_plan import CatalogPlanner, NODE_DRAG_CHAIN

        catalog, _ = read_catalog(ROOT / 'keymaps/deluxe-defaults.json')
        planner = CatalogPlanner(catalog)
        settings = SimpleNamespace(keymap=SimpleNamespace(enable_keymaps=True))

        def chain():
            _, groups = planner.plan(catalog, settings)
            return [request for requests in groups.values() for request in requests
                    if request.dispatch_group == NODE_DRAG_CHAIN
                    or request.target.idname == 'node.bh_link_socket']

        routes = chain()
        self.assertEqual([request.target.idname for request in routes],
                         ['node.translate_attach', 'transform.translate', 'node.bh_link_socket'])
        self.assertEqual(routes[-1].event, routes[0].event)
        self.assertEqual(routes[-1].scope, routes[0].scope)
        catalog['sections']['other.parity-node-editor']['enabled'] = False
        self.assertEqual(chain(), [])
        catalog['sections']['other.parity-node-editor']['enabled'] = True
        catalog['assignments'][routes[0].request_id]['event'] = 'g-press-4f6a072800f4'
        self.assertEqual(chain(), [])

    def test_ui_and_profile_do_not_reach_into_native_ownership(self):
        for path in [ROOT / 'keymaps/deluxe_profiles.py', * (ROOT / 'preferences/addon/keymaps').glob('*.py')]:
            text = path.read_text()
            self.assertNotIn('runtime._', text, str(path))
            self.assertNotIn('runtime._FEATURES', text, str(path))


if __name__ == '__main__':
    unittest.main()
