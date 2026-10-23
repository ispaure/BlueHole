"""Audit shared call contracts and global bindings without executing Blender code."""
import ast
import builtins
import dis
import importlib
import inspect
from pathlib import Path
import symtable
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = '_bluehole_shared_contracts'
BLENDER_PROPERTIES = {'BoolProperty', 'BoolVectorProperty', 'CollectionProperty',
                      'EnumProperty', 'FloatProperty', 'FloatVectorProperty',
                      'IntProperty', 'IntVectorProperty', 'PointerProperty',
                      'StringProperty', 'RemoveProperty'}


def consumer_sources():
    return sorted(path for path in ROOT.rglob('*.py')
                  if not set(path.relative_to(ROOT).parts) & {'Lib', 'tests', '.git', '.github', 'test-results'})


def module_name(path):
    parts = path.relative_to(ROOT).with_suffix('').parts
    if path.name == '__init__.py':
        parts = parts[:-1]
    return '.'.join((NAMESPACE, *parts))


def imported_module(node, path):
    name = node.module or ''
    if not node.level:
        return name
    module = module_name(path)
    package = module if path.name == '__init__.py' else module.rpartition('.')[0]
    return importlib.util.resolve_name('.' * node.level + name, package)


def shared_value(owner, name):
    try:
        return getattr(owner, name)
    except AttributeError:
        return importlib.import_module(owner.__name__ + '.' + name)


class SharedContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        package = types.ModuleType(NAMESPACE)
        package.__path__ = [str(ROOT)]
        cls.modules = set(sys.modules)
        sys.modules[NAMESPACE] = package

    @classmethod
    def tearDownClass(cls):
        for name in tuple(sys.modules):
            if name not in cls.modules and (name == NAMESPACE or name.startswith(NAMESPACE + '.')):
                sys.modules.pop(name, None)

    def test_shared_imports_attributes_and_call_signatures(self):
        for path in consumer_sources():
            tree = ast.parse(path.read_bytes())
            aliases = {}
            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom):
                    continue
                name = imported_module(node, path)
                if not name.startswith(NAMESPACE + '.Lib.commonUtils'):
                    continue
                with self.subTest(source=str(path.relative_to(ROOT)), line=node.lineno):
                    owner = importlib.import_module(name)
                    for item in node.names:
                        if item.name != '*':
                            aliases[item.asname or item.name] = shared_value(owner, item.name)
            for node in ast.walk(tree):
                if (not isinstance(node, ast.Attribute) or not isinstance(node.value, ast.Name)
                        or node.value.id not in aliases):
                    continue
                with self.subTest(source=str(path.relative_to(ROOT)), line=node.lineno):
                    self.assertTrue(hasattr(aliases[node.value.id], node.attr), node.attr)
            for node in ast.walk(tree):
                if (not isinstance(node, ast.Call)
                        or any(isinstance(arg, ast.Starred) for arg in node.args)
                        or any(keyword.arg is None for keyword in node.keywords)):
                    continue
                if isinstance(node.func, ast.Name) and node.func.id in aliases:
                    value = aliases[node.func.id]
                elif (isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
                      and node.func.value.id in aliases):
                    value = getattr(aliases[node.func.value.id], node.func.attr)
                else:
                    continue
                with self.subTest(source=str(path.relative_to(ROOT)), line=node.lineno):
                    try:
                        signature = inspect.signature(value)
                    except (ValueError, TypeError):
                        continue
                    signature.bind(*[object() for arg in node.args],
                                   **{keyword.arg: object() for keyword in node.keywords})

    def test_functions_have_explicit_or_exported_global_bindings(self):
        files = {module_name(path): path for path in consumer_sources()}
        cache = {}

        def bindings(name):
            if name in cache:
                return cache[name]
            if name.startswith(NAMESPACE + '.Lib.commonUtils'):
                owner = importlib.import_module(name)
                return set(getattr(owner, '__all__', (key for key in vars(owner) if not key.startswith('_'))))
            if name == 'bpy.props':
                return BLENDER_PROPERTIES
            if name in files:
                path = files[name]
                source = path.read_text()
                symbols = symtable.symtable(source, str(path), 'exec').get_symbols()
                names = {symbol.get_name() for symbol in symbols if symbol.is_assigned() or symbol.is_imported()}
                cache[name] = names
                tree = ast.parse(source)
                # Imports inside functions/classes have local scopes, so only
                # collect wildcard imports from module-level control flow.
                def imports(nodes):
                    for node in nodes:
                        if isinstance(node, ast.ImportFrom) and any(item.name == '*' for item in node.names):
                            yield node
                        elif not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                            for field in ('body', 'orelse', 'finalbody'):
                                yield from imports(getattr(node, field, ()))
                            for handler in getattr(node, 'handlers', ()):
                                yield from imports(handler.body)
                for node in imports(tree.body):
                    names.update(key for key in bindings(imported_module(node, path)) if not key.startswith('_'))
                return names
            # Other wildcard dependencies are standard-library modules; unknown
            # Blender modules are kept explicit rather than given invented APIs.
            owner = importlib.import_module(name)
            return set(getattr(owner, '__all__', (key for key in vars(owner) if not key.startswith('_'))))

        def check_code(code, names, path):
            for operation in dis.get_instructions(code):
                if operation.opname == 'LOAD_GLOBAL':
                    with self.subTest(source=str(path.relative_to(ROOT)), function=code.co_name, name=operation.argval):
                        self.assertTrue(operation.argval in names or hasattr(builtins, operation.argval),
                                        'Missing global ' + operation.argval)
            for constant in code.co_consts:
                if isinstance(constant, types.CodeType):
                    check_code(constant, names, path)

        implicit = {'__name__', '__file__', '__package__', '__path__', '__spec__', '__builtins__', '__annotations__'}
        for name, path in files.items():
            check_code(compile(path.read_bytes(), str(path), 'exec'), bindings(name) | implicit, path)


if __name__ == '__main__':
    unittest.main()
