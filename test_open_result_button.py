import types
import sys
import queue
import tkinter as tk
from pathlib import Path

# Stub out heavy dependencies so the module imports without them
sys.modules.setdefault('config', types.SimpleNamespace(BRAND_COLORS={}, ASSETS_DIR=Path('.')))
sys.modules.setdefault('processing_engine', types.SimpleNamespace(run_processing_job=lambda *a, **k: None))
sys.modules.setdefault('file_utils', types.SimpleNamespace(open_file=lambda path: None, ensure_folders=lambda: None, cleanup_temp_files=lambda: None))
sys.modules.setdefault('kyo_review_tool', types.SimpleNamespace(ReviewWindow=object))
sys.modules.setdefault('version', types.SimpleNamespace(VERSION='1.0'))
sys.modules.setdefault('logging_utils', types.SimpleNamespace(setup_logger=lambda name: None))
sys.modules.setdefault('gui_components', types.SimpleNamespace(create_main_header=lambda *a, **k: None, create_io_section=lambda *a, **k: None, create_process_controls=lambda *a, **k: None))

from kyo_qa_tool_app import KyoQAToolApp

class DummyVar:
    def __init__(self):
        self._v = None
    def set(self, v):
        self._v = v
    def get(self):
        return self._v

class DummyBtn:
    def __init__(self):
        self.state = None
    def config(self, **kw):
        self.state = kw.get('state')

class DummyTree:
    def insert(self, *a, **kw):
        pass

def test_open_result_button_enabled_after_result_path():
    app = types.SimpleNamespace(
        response_queue=queue.Queue(),
        log_message=lambda *a, **k: None,
        status_current_file=DummyVar(),
        reviewable_files=[],
        review_tree=DummyTree(),
        update_ui_for_finish=lambda status: None,
        result_file_path=None,
        count_pass=DummyVar(), count_fail=DummyVar(), count_review=DummyVar(), count_ocr=DummyVar(),
        count_protected=DummyVar(), count_corrupted=DummyVar(), count_ocr_failed=DummyVar(), count_no_text=DummyVar(),
        open_result_btn=DummyBtn(),
    )
    app.after = lambda *a, **k: None
    app.process_response_queue = lambda: None  # avoid recursive scheduling

    app.response_queue.put({'type': 'result_path', 'path': 'res.xlsx'})
    KyoQAToolApp.process_response_queue(app)

    assert app.result_file_path == 'res.xlsx'
    assert app.open_result_btn.state == tk.NORMAL
