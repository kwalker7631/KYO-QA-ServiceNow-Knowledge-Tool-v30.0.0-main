import unittest
import re
import custom_patterns


class TestCustomPatterns(unittest.TestCase):
    def test_first_pattern_simplified(self):
        self.assertEqual(custom_patterns.MODEL_PATTERNS[0], r"\bFS-\d+[A-Z]*\b")

    def test_patterns_compile(self):
        for pat in custom_patterns.MODEL_PATTERNS:
            try:
                re.compile(pat)
            except re.error as exc:
                self.fail(f"Pattern {pat} failed to compile: {exc}")

    def test_no_double_escaping(self):
        """Ensure patterns do not contain double backslashes."""
        for pat in custom_patterns.MODEL_PATTERNS:
            self.assertNotIn("\\\\b", pat)

if __name__ == "__main__":
    unittest.main()
