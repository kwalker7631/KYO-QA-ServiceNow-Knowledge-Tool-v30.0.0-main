import time
import queue
import sys
import types

openpyxl_stub = types.ModuleType("openpyxl")
openpyxl_stub.styles = types.ModuleType("openpyxl.styles")
openpyxl_stub.styles.PatternFill = object
openpyxl_stub.styles.Alignment = object
openpyxl_stub.utils = types.ModuleType("openpyxl.utils")
openpyxl_stub.utils.get_column_letter = lambda *a, **k: "A"
sys.modules.setdefault("openpyxl", openpyxl_stub)
sys.modules.setdefault("openpyxl.styles", openpyxl_stub.styles)
sys.modules.setdefault("openpyxl.utils", openpyxl_stub.utils)

for mod in ["fitz", "cv2", "numpy", "pytesseract", "pikepdf"]:
    sys.modules.setdefault(mod, types.ModuleType(mod))

pil = types.ModuleType("PIL")
pil.Image = object
sys.modules.setdefault("PIL", pil)
sys.modules.setdefault("PIL.Image", pil)
from kyo_qa_tool_app import KyoQAToolApp, BRAND_COLORS  # noqa: E402

class DummyLabel:
    def __init__(self):
        self.foreground = None
    def config(self, **kwargs):
        self.foreground = kwargs.get('foreground')

class DummyVar:
    def __init__(self):
        self.value = None
    def set(self, val):
        self.value = val

class DummyApp:
    def __init__(self):
        self.led_label = DummyLabel()
        self.led_status_var = DummyVar()
        self.progress_value = DummyVar()
        self.time_remaining_var = DummyVar()
        self.response_queue = queue.Queue()
        self.start_time = time.time()
        self.process_response_queue = lambda: None
    def after(self, *args, **kwargs):
        pass
    def log_message(self, *args, **kwargs):
        pass
    def update_ui_for_finish(self, *args, **kwargs):
        pass


def test_set_led_sets_color():
    app = DummyApp()
    KyoQAToolApp.set_led(app, "Processing")
    assert app.led_label.foreground == BRAND_COLORS["accent_blue"]


def test_process_queue_progress():
    app = DummyApp()
    app.response_queue.put({"type": "progress", "current": 1, "total": 4})
    KyoQAToolApp.process_response_queue(app)
    assert app.progress_value.value == 25.0
