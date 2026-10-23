"""Pie action declarations stay independent of the menus which draw them."""
import ast
import importlib
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


class PieActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.namespace = '_bluehole_pie_contract_tests'
        package = types.ModuleType(cls.namespace)
        package.__path__ = [str(cls.root)]
        sys.modules[cls.namespace] = package
        cls.addClassCleanup(lambda: [sys.modules.pop(name, None) for name in tuple(sys.modules)
            if name == cls.namespace or name.startswith(cls.namespace + '.')])
        class RejectPresentation:
            def find_spec(self, fullname, path=None, target=None):
                if fullname == 'bpy' or fullname.startswith(cls.namespace + '.ui'):
                    raise AssertionError('Action declaration imported presentation: ' + fullname)
        with patch.object(sys, 'meta_path', [RejectPresentation(), *sys.meta_path]):
            cls.catalog = importlib.import_module(cls.namespace + '.actions.actions.pie_actions')

    def test_catalog_import_does_not_load_presentation(self):
        self.assertTrue(self.catalog.PIE_ACTIONS)
        self.assertIs(self.catalog.get_all_pie_actions(), self.catalog.PIE_ACTIONS)
        self.assertFalse(any(name.startswith(self.namespace + '.ui') for name in sys.modules))

    def test_action_targets_match_literal_menu_declarations(self):
        identifiers = set()
        for path in (self.root / 'ui/menus/pie').glob('*_pies.py'):
            for node in ast.parse(path.read_text()).body:
                if isinstance(node, ast.ClassDef):
                    for statement in node.body:
                        if isinstance(statement, ast.Assign) and any(
                                isinstance(target, ast.Name) and target.id == 'bl_idname'
                                for target in statement.targets):
                            identifiers.add(ast.literal_eval(statement.value))
        for action in self.catalog.PIE_ACTIONS:
            with self.subTest(menu=action.get_props(None)['name']):
                self.assertEqual(action.get_idname(), 'wm.call_menu_pie')
                self.assertIn(action.get_props(None)['name'], identifiers)
