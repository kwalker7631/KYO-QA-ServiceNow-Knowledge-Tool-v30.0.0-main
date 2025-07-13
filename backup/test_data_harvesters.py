import unittest

from data_harvesters import get_combined_patterns, harvest_models
from config import MODEL_PATTERNS as DEFAULT_MODEL_PATTERNS
from custom_patterns import MODEL_PATTERNS as CUSTOM_MODEL_PATTERNS


class TestDataHarvesters(unittest.TestCase):
    def test_combined_patterns_include_custom_and_default(self):
        combined = get_combined_patterns("MODEL_PATTERNS", DEFAULT_MODEL_PATTERNS)
        for pattern in CUSTOM_MODEL_PATTERNS:
            self.assertIn(pattern, combined)
        for pattern in DEFAULT_MODEL_PATTERNS:
            self.assertIn(pattern, combined)

    def test_harvest_models_with_custom_pattern(self):
        text = "Example FS-1234MFP document"
        found = harvest_models(text, "sample.pdf")
        self.assertIn("FS-1234MFP", found)


if __name__ == "__main__":
    unittest.main()
