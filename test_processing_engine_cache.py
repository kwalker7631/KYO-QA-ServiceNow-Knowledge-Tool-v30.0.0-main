import json
import sys
from types import ModuleType
from queue import SimpleQueue
from pathlib import Path

# Stub heavy dependencies before importing processing_engine
sys.modules.setdefault("openpyxl", ModuleType("openpyxl"))
styles_mod = sys.modules.setdefault("openpyxl.styles", ModuleType("openpyxl.styles"))
utils_mod = sys.modules.setdefault("openpyxl.utils", ModuleType("openpyxl.utils"))
class DummyPatternFill:
    def __init__(self, *a, **k):
        pass

class DummyAlignment:
    def __init__(self, *a, **k):
        pass

setattr(styles_mod, "PatternFill", DummyPatternFill)
setattr(styles_mod, "Alignment", DummyAlignment)
class DummyFont:
    def __init__(self, *a, **k):
        pass

setattr(styles_mod, "Font", DummyFont)
setattr(utils_mod, "get_column_letter", lambda x: "A")
sys.modules.setdefault("pandas", ModuleType("pandas"))
sys.modules.setdefault("fitz", ModuleType("fitz"))
sys.modules.setdefault("pytesseract", ModuleType("pytesseract"))
pil_mod = sys.modules.setdefault("PIL", ModuleType("PIL"))
setattr(pil_mod, "Image", object)
sys.modules.setdefault("cv2", ModuleType("cv2"))
sys.modules.setdefault("numpy", ModuleType("numpy"))
sys.modules.setdefault("pikepdf", ModuleType("pikepdf"))

import processing_engine


def test_qa_numbers_cached(tmp_path, monkeypatch):
    # direct cache and txt output to temp directory
    monkeypatch.setattr(processing_engine, "CACHE_DIR", tmp_path)
    txt_dir = tmp_path / "txt"
    monkeypatch.setattr(processing_engine, "PDF_TXT_DIR", txt_dir)
    txt_dir.mkdir()

    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_text("dummy", encoding="utf-8")

    monkeypatch.setattr(processing_engine, "_is_ocr_needed", lambda x: False)
    monkeypatch.setattr(processing_engine, "process_single_document", lambda p: ("success", "", "text"))

    def dummy_harvest(text, name):
        return {"models": "ModelA", "author": "AuthorA", "qa_numbers": "QA-123"}

    monkeypatch.setattr(processing_engine, "harvest_all_data", dummy_harvest)
    q = SimpleQueue()

    result = processing_engine.process_single_pdf(pdf_file, q)
    assert result["qa_numbers"] == "QA-123"

    cache_file = processing_engine.get_cache_path(pdf_file)
    data = json.loads(cache_file.read_text())
    assert data["qa_numbers"] == "QA-123"

    monkeypatch.setattr(processing_engine, "harvest_all_data", lambda *a, **k: {"models": "", "author": "", "qa_numbers": "WRONG"})
    cached_result = processing_engine.process_single_pdf(pdf_file, q)
    assert cached_result["qa_numbers"] == "QA-123"

