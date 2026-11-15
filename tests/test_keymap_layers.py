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

    def test_ui_and_profile_do_not_reach_into_native_ownership(self):
        for path in [ROOT / 'keymaps/deluxe_profiles.py', * (ROOT / 'preferences/addon/keymaps').glob('*.py')]:
            text = path.read_text()
            self.assertNotIn('runtime._', text, str(path))
            self.assertNotIn('runtime._FEATURES', text, str(path))


if __name__ == '__main__':
    unittest.main()
