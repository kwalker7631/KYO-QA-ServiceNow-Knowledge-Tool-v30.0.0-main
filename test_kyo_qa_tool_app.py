import types
import sys
import tkinter as tk

openpyxl_stub = types.ModuleType("openpyxl")
styles = types.ModuleType("styles")
styles.PatternFill = object
styles.Alignment = object
openpyxl_stub.styles = styles
sys.modules["openpyxl.styles"] = styles
openpyxl_stub.utils = types.ModuleType("utils")
openpyxl_stub.utils.get_column_letter = lambda x: x
sys.modules["openpyxl.utils"] = openpyxl_stub.utils
sys.modules.setdefault("openpyxl", openpyxl_stub)

processing_engine_stub = types.ModuleType("processing_engine")
def run_processing_job(job, queue, cancel_event, pause_event):
    pass
processing_engine_stub.run_processing_job = run_processing_job
sys.modules.setdefault("processing_engine", processing_engine_stub)

from kyo_qa_tool_app import KyoQAToolApp

class DummyVar:
    def __init__(self, value=0):
        self._value = value
    def set(self, value):
        self._value = value
    def get(self):
        return self._value

class DummyButton:
    def __init__(self):
        self.kwargs = {}
    def config(self, **kwargs):
        self.kwargs.update(kwargs)
    def configure(self, **kwargs):
        self.kwargs.update(kwargs)
    def winfo_children(self):
        return []

class DummyReviewTree:
    def __init__(self):
        self.children = [1]
    def delete(self, *args):
        self.children = []
    def get_children(self):
        return self.children

def make_dummy_app():
    dummy = types.SimpleNamespace()
    for name in [
        "count_pass",
        "count_fail",
        "count_review",
        "count_ocr",
        "count_protected",
        "count_corrupted",
        "count_ocr_failed",
        "count_no_text",
    ]:
        setattr(dummy, name, DummyVar(1))
    dummy.progress_value = DummyVar(50)
    dummy.reviewable_files = [1]
    dummy.review_tree = DummyReviewTree()
    dummy.process_btn = DummyButton()
    dummy.rerun_btn = DummyButton()
    dummy.open_result_btn = DummyButton()
    dummy.pause_btn = DummyButton()
    dummy.stop_btn = DummyButton()
    dummy.status_frame = DummyButton()
    dummy.led_label = DummyButton()
    dummy.led_status_var = DummyVar()
    dummy.cancel_event = types.SimpleNamespace(clear=lambda: None)
    dummy.pause_event = types.SimpleNamespace(clear=lambda: None)
    dummy.is_processing = False
    dummy.is_paused = True
    dummy.set_led = KyoQAToolApp.set_led.__get__(dummy)
    return dummy

def test_update_ui_for_start_resets_state():
    app = make_dummy_app()
    KyoQAToolApp.update_ui_for_start(app)
    assert app.is_processing is True
    assert app.is_paused is False
    assert app.process_btn.kwargs["state"] == tk.DISABLED
    assert app.pause_btn.kwargs["state"] == tk.NORMAL
    assert app.count_pass.get() == 0
    assert app.review_tree.get_children() == []

def test_update_ui_for_start_resets_progress():
    app = make_dummy_app()
    KyoQAToolApp.update_ui_for_start(app)
    assert app.progress_value.get() == 0
