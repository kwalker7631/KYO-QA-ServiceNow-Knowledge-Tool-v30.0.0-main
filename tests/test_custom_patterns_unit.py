import unittest
import re
import custom_patterns


class TestCustomPatterns(unittest.TestCase):
    def test_first_pattern_simplified(self):
        self.assertEqual(custom_patterns.MODEL_PATTERNS[0], r"\bFS-\d+[A-Z]*\b")

    def test_patterns_compile(self):
        """Ensure both model and QA patterns compile."""
        for pat in custom_patterns.MODEL_PATTERNS + custom_patterns.QA_NUMBER_PATTERNS:
            try:
                re.compile(pat)
            except re.error as exc:
                self.fail(f"Pattern {pat} failed to compile: {exc}")

    def test_qa_patterns_present(self):
        """Check that QA patterns list is not empty."""
        self.assertGreater(len(custom_patterns.QA_NUMBER_PATTERNS), 0)


if __name__ == "__main__":
    unittest.main()
