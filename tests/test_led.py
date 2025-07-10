import types
import sys

# Stub heavy dependencies before importing the app module
sys.modules['processing_engine'] = types.ModuleType('processing_engine')
sys.modules['processing_engine'].run_processing_job = lambda *a, **kw: None

from kyo_qa_tool_app import KyoQAToolApp
from config import BRAND_COLORS

class DummyVar:
    def __init__(self):
        self.value = None
    def set(self, v):
        self.value = v
    def get(self):
        return self.value

class DummyWidget:
    def __init__(self):
        self.config_called = {}
    def configure(self, **kwargs):
        self.config_called.update(kwargs)
    def winfo_children(self):
        return []

def test_set_led_processing():
    app = types.SimpleNamespace()
    app.led_status_var = DummyVar()
    app.led_label = DummyWidget()
    app.status_frame = DummyWidget()
    KyoQAToolApp.set_led(app, "Processing")
    assert app.led_status_var.get() == "●"
    assert app.led_label.config_called["foreground"] == BRAND_COLORS["success_green"]
    assert app.status_frame.config_called["background"] == BRAND_COLORS["status_processing_bg"]


def test_set_led_ready_and_error():
    app = types.SimpleNamespace()
    app.led_status_var = DummyVar()
    app.led_label = DummyWidget()
    app.status_frame = DummyWidget()

    KyoQAToolApp.set_led(app, "Ready")
    assert app.led_label.config_called["foreground"] == BRAND_COLORS["success_green"]

    KyoQAToolApp.set_led(app, "Error")
    assert app.led_label.config_called["foreground"] == BRAND_COLORS["fail_red"]
