import unittest
from pathlib import Path
import importlib

class TestConfig(unittest.TestCase):
    def test_status_column_name_and_newline(self):
        # Reload the module to ensure we read the latest file
        if 'config' in importlib.sys.modules:
            importlib.reload(importlib.import_module('config'))
        else:
            importlib.import_module('config')
        import config
        self.assertEqual(config.STATUS_COLUMN_NAME, "Processing Status")

        # Verify the file ends with a newline
        path = Path('config.py')
        text = path.read_bytes()
        self.assertTrue(text.endswith(b"\n"), "config.py should end with a newline")

if __name__ == '__main__':
    unittest.main()
