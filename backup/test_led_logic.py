import unittest
import types
import sys

processing_engine_stub = types.ModuleType('processing_engine')
processing_engine_stub.run_processing_job = lambda *a, **k: None
sys.modules['processing_engine'] = processing_engine_stub


class TestLEDColors(unittest.TestCase):
    def test_processing_color(self):
        fg, bg = get_led_colors("Processing")
        self.assertEqual(fg, BRAND_COLORS["accent_blue"])
        self.assertEqual(bg, BRAND_COLORS["status_processing_bg"])

    def test_default(self):
        fg, bg = get_led_colors("unknown")
        self.assertEqual(fg, BRAND_COLORS["kyocera_black"])
        self.assertEqual(bg, BRAND_COLORS["status_default_bg"])

    def test_ready_and_error(self):
        fg_ready, _ = get_led_colors("Ready")
        self.assertEqual(fg_ready, BRAND_COLORS["success_green"])

        fg_error, _ = get_led_colors("Error")
        self.assertEqual(fg_error, BRAND_COLORS["fail_red"])

if __name__ == "__main__":
    unittest.main()

