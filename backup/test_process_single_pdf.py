import sys, types, unittest
from pathlib import Path

for m in ["fitz", "pytesseract", "cv2", "numpy", "pikepdf"]:
    sys.modules.setdefault(m, types.ModuleType(m))
# minimal PIL.Image stub
pil_mod = types.ModuleType("PIL")
pil_mod.Image = object
sys.modules.setdefault("PIL", pil_mod)

# simple openpyxl stub so excel_generator imports without the real package
openpyxl_mod = types.ModuleType("openpyxl")
styles_mod = types.ModuleType("styles")
class _Dummy:
    def __init__(self, *a, **k):
        pass
styles_mod.Font = styles_mod.PatternFill = styles_mod.Alignment = _Dummy
utils_mod = types.ModuleType("utils")
utils_mod.get_column_letter = lambda x: "A"
openpyxl_mod.styles = styles_mod
openpyxl_mod.utils = utils_mod
sys.modules.setdefault("openpyxl", openpyxl_mod)
sys.modules.setdefault("openpyxl.styles", styles_mod)
sys.modules.setdefault("openpyxl.utils", utils_mod)

import processing_engine

class DummyQueue:
    def __init__(self):
        self.items = []
    def put(self, item):
        self.items.append(item)

class TestProcessSinglePDF(unittest.TestCase):
    def test_qa_numbers_added(self):
        tmp_dir = Path('temp_test_dir')
        tmp_dir.mkdir(exist_ok=True)
        pdf_path = tmp_dir / 'sample.pdf'
        pdf_path.write_text('dummy')

        processing_engine.process_single_document = lambda p: ("success", "", "QA-111\nAuthor: Bob")
        processing_engine._is_ocr_needed = lambda p: False
        processing_engine.harvest_all_data = lambda text, fn: {"models": "M1", "author": "Bob", "qa_numbers": "QA-111"}
        processing_engine.CACHE_DIR = tmp_dir

        q = DummyQueue()
        result = processing_engine.process_single_pdf(pdf_path, q, ignore_cache=True)
        self.assertEqual(result["qa_numbers"], "QA-111")

        for f in tmp_dir.iterdir():
            f.unlink()
        tmp_dir.rmdir()

if __name__ == '__main__':
    unittest.main()
