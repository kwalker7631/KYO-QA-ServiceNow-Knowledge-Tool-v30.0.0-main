import queue
from types import MethodType, ModuleType
import tkinter as tk
import sys

# Provide dummy openpyxl modules so kyo_qa_tool_app imports without dependencies
sys.modules.setdefault("openpyxl", ModuleType("openpyxl"))
styles_mod = sys.modules.setdefault("openpyxl.styles", ModuleType("openpyxl.styles"))
utils_mod = sys.modules.setdefault("openpyxl.utils", ModuleType("openpyxl.utils"))
setattr(styles_mod, "PatternFill", object)
setattr(styles_mod, "Alignment", object)
setattr(utils_mod, "get_column_letter", lambda x: "A")
sys.modules.setdefault("fitz", ModuleType("fitz"))
sys.modules.setdefault("pytesseract", ModuleType("pytesseract"))
pil_mod = sys.modules.setdefault("PIL", ModuleType("PIL"))
setattr(pil_mod, "Image", object)
sys.modules.setdefault("cv2", ModuleType("cv2"))
sys.modules.setdefault("numpy", ModuleType("numpy"))
sys.modules.setdefault("pikepdf", ModuleType("pikepdf"))

from kyo_qa_tool_app import KyoQAToolApp

class DummyBtn:
    def __init__(self):
        self.state = tk.DISABLED
    def config(self, state=None):
        self.state = state

class DummyVar:
    def set(self, value):
        self.value = value
    def get(self):
        return getattr(self, 'value', 0)

    def get(self):
        return getattr(self, "value", 0)

class DummyTree:
    def insert(self, *a, **k):
        pass
    def delete(self, *a, **k):
        pass

class DummyApp:
    def __init__(self):
        self.response_queue = queue.Queue()
        self.open_result_btn = DummyBtn()
        self.status_current_file = DummyVar()
        self.progress_value = DummyVar()
        self.reviewable_files = []
        self.review_tree = DummyTree()
        self.result_file_path = None
        self.progress_value = DummyVar()
    def log_message(self, msg):
        pass
    def update_ui_for_finish(self, status):
        pass
    def after(self, delay, callback):
        pass
    def _update_time_remaining(self):
        pass

def test_enable_open_result_message():
    app = DummyApp()
    # Bind the processing method from the real class
    app.process_response_queue = MethodType(KyoQAToolApp.process_response_queue, app)
    # Put the enable message in the queue
    app.response_queue.put({"type": "enable_open_result"})
    app.process_response_queue()
    assert app.open_result_btn.state == tk.NORMAL

def test_progress_message_updates_value():
    app = DummyApp()
    app.process_response_queue = MethodType(KyoQAToolApp.process_response_queue, app)
    app.response_queue.put({"type": "progress", "current": 2, "total": 4})
    app.process_response_queue()
    assert app.progress_value.get() == 50.0
