import os, sys
import ast
import inspect
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Provide dummy version module to satisfy start_tool import
dummy_version = types.ModuleType('version')
dummy_version.get_version = lambda: '0.0.0'
sys.modules['version'] = dummy_version

import start_tool


def test_initialize_colors_global_usage():
    source = inspect.getsource(start_tool.initialize_colors)
    tree = ast.parse(source)
    global_stmt = next((n for n in ast.walk(tree) if isinstance(n, ast.Global)), None)
    assert global_stmt is not None, "No global statement found"
    expected = {
        'COLOR_INFO',
        'COLOR_SUCCESS',
        'COLOR_WARNING',
        'COLOR_ERROR',
        'COLOR_RESET',
    }
    assert set(global_stmt.names) == expected
