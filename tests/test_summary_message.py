import unittest
from summary_utils import build_summary_message

class TestSummaryMessage(unittest.TestCase):
    def test_summary_format(self):
        msg = build_summary_message(2, 1, 3)
        self.assertEqual(msg, "Pass: 2\nFail: 1\nReview: 3")

if __name__ == '__main__':
    unittest.main()
