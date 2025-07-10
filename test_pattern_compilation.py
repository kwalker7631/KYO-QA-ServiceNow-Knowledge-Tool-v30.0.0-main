import unittest
import re
import importlib

import custom_patterns

class TestPatternCompilation(unittest.TestCase):
    def test_patterns_compile(self):
        """Ensure all regex patterns compile successfully."""
        importlib.reload(custom_patterns)
        for pattern in custom_patterns.MODEL_PATTERNS + custom_patterns.QA_NUMBER_PATTERNS:
            try:
                re.compile(pattern)
            except re.error as e:
                self.fail(f"Pattern {pattern!r} failed to compile: {e}")

if __name__ == "__main__":
    unittest.main()
