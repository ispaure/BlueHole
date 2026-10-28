"""Explicit candidate-source injection for tests, preserving the add-on namespace.

Production imports and the recorded subtree revision are never changed here.
"""
import importlib
import importlib.util
import os
from pathlib import Path
import sys


def install_candidate(namespace):
    selected = os.environ.get('BLUEHOLE_SHARED_TEST_SOURCE')
    if not selected:
        return
    source = Path(selected).resolve()
    if not (source / '__init__.py').is_file():
        raise ValueError('BLUEHOLE_SHARED_TEST_SOURCE must name an explicit shared package.')
    importlib.import_module(namespace + '.Lib')
    name = namespace + '.Lib.commonUtils'
    spec = importlib.util.spec_from_file_location(name, source / '__init__.py',
                                                submodule_search_locations=[str(source)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
