import importlib
from pathlib import Path
import custom_patterns
from data_harvesters import ensure_custom_patterns_file


def test_invalid_patterns_skipped():
    cp_path = Path('custom_patterns.py')
    original = cp_path.read_text()
    try:
        cp_path.write_text("""# custom_patterns.py
MODEL_PATTERNS = [r'valid', r'[invalid']
QA_NUMBER_PATTERNS = []
""")
        importlib.reload(custom_patterns)
        ensure_custom_patterns_file()
        assert "[invalid" not in custom_patterns.MODEL_PATTERNS
        assert "valid" in custom_patterns.MODEL_PATTERNS
    finally:
        cp_path.write_text(original)
        importlib.reload(custom_patterns)

