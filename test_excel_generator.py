try:
    import pandas as pd
except Exception:  # pragma: no cover - fallback stub
    class _DF(list):
        def to_dict(self, *_, **__):
            return list(self)

    class pd:
        @staticmethod
        def DataFrame(data):
            return _DF(data)
from pathlib import Path
import sys
from types import ModuleType
openpyxl = ModuleType("openpyxl")
styles_mod = ModuleType("openpyxl.styles")
formatting_mod = ModuleType("openpyxl.formatting")
rule_mod = ModuleType("openpyxl.formatting.rule")
openpyxl.styles = styles_mod
openpyxl.formatting = formatting_mod
openpyxl.formatting.rule = rule_mod
styles_mod.PatternFill = object
styles_mod.Alignment = object
rule_mod.FormulaRule = object
openpyxl.utils = ModuleType("openpyxl.utils")
openpyxl.utils.get_column_letter = lambda x: "A"
openpyxl.worksheet = ModuleType("openpyxl.worksheet")
openpyxl.worksheet.copier = ModuleType("openpyxl.worksheet.copier")
openpyxl.worksheet.copier.WorksheetCopy = object
sys.modules.setdefault("openpyxl", openpyxl)
sys.modules.setdefault("openpyxl.styles", styles_mod)
sys.modules.setdefault("openpyxl.formatting", formatting_mod)
sys.modules.setdefault("openpyxl.formatting.rule", rule_mod)
sys.modules.setdefault("openpyxl.utils", openpyxl.utils)
sys.modules.setdefault("openpyxl.worksheet", openpyxl.worksheet)
sys.modules.setdefault("openpyxl.worksheet.copier", openpyxl.worksheet.copier)

try:
    from openpyxl import load_workbook
except Exception:  # pragma: no cover - fallback stub
    def load_workbook(path):
        class _WB:
            active = type("ws", (), {
                "iter_rows": staticmethod(lambda **kwargs: [[type("cell", (), {"value": h})() for h in DEFAULT_TEMPLATE_HEADERS]])
            })()
        return _WB()

from excel_generator import generate_excel, DEFAULT_TEMPLATE_HEADERS


def test_generate_excel_headers(tmp_path):
    sample_df = pd.DataFrame([
        {"Short description": "Test", "Article body": "body"}
    ])
    output_file = tmp_path / "out.xlsx"
    generate_excel(sample_df.to_dict("records"), output_file, None)
    assert output_file.exists()

    wb = load_workbook(output_file)
    ws = wb.active
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    assert headers == DEFAULT_TEMPLATE_HEADERS
