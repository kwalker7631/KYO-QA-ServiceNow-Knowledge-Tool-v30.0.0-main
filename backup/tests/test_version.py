import importlib

import version


def test_get_version():
    assert version.get_version() == version.VERSION


def test_import_start_tool():
    mod = importlib.import_module("start_tool")
    assert hasattr(mod, "get_venv_python_path")


def test_import_packaging_script():
    mod = importlib.import_module("packaging_script")
    assert mod.current_version == version.VERSION


def test_print_header_uses_get_version(capsys):
    start_mod = importlib.import_module("start_tool")
    start_mod.print_header()
    captured = capsys.readouterr().out
    assert version.VERSION in captured
