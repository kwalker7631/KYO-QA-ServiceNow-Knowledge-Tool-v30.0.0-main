import py_compile
from pathlib import Path

def test_compile_ocr_utils():
    try:
        py_compile.compile(str(Path(__file__).resolve().parents[1] / 'ocr_utils.py'), doraise=True)
    except py_compile.PyCompileError as e:
        assert False, f"Compilation failed: {e}"
