import pytest
from pathlib import Path

try:
    import pandas as pd
except Exception:
    pd = None

try:
    from openpyxl import load_workbook
except Exception:
    load_workbook = None

if pd is None or load_workbook is None:
    pytest.skip("Required libraries not installed", allow_module_level=True)

from excel_generator import generate_excel, DEFAULT_TEMPLATE_HEADERS


def test_generate_excel_headers(tmp_path):
    sample_df = pd.DataFrame([
        {"Short description": "Test", "Article body": "body"}
    ])
    output_file = tmp_path / "out.xlsx"
    generate_excel(sample_df.to_dict("records"), output_file)
    assert output_file.exists()

    wb = load_workbook(output_file)
    ws = wb.active
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    assert headers == DEFAULT_TEMPLATE_HEADERS

def test_generate_excel_with_template(tmp_path):
    sample_df = pd.DataFrame([
        {"Short description": "Test", "Article body": "body"}
    ])
    output_file = tmp_path / "out_template.xlsx"
    template = Path("Sample_Set/kb_knowledge_Template.xlsx")
    generate_excel(sample_df.to_dict("records"), output_file, template)
    assert output_file.exists()

    wb = load_workbook(output_file)
    ws = wb.active
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    assert headers == DEFAULT_TEMPLATE_HEADERS
    assert ws.max_row == 2
    sd_index = DEFAULT_TEMPLATE_HEADERS.index("Short description") + 1
    assert ws.cell(row=2, column=sd_index).value == "Test"


def test_generate_excel_appends_missing_rows(tmp_path):
    sample_df = pd.DataFrame([
        {"file_name": "existing.pdf", "Short description": "Existing", "processing_status": "Success"},
        {"file_name": "new.pdf", "Short description": "New Entry", "processing_status": "Success"},
    ])

    # Create a simple template with one existing row
    template_path = tmp_path / "template.xlsx"
    wb = load_workbook(Path("Sample_Set/kb_knowledge_Template.xlsx"))
    ws = wb.active
    ws.delete_rows(2, ws.max_row - 1)
    ws.cell(row=2, column=DEFAULT_TEMPLATE_HEADERS.index("Short description") + 1).value = "existing"
    wb.save(template_path)

    output_file = tmp_path / "out_append.xlsx"
    generate_excel(sample_df.to_dict("records"), output_file, template_path)

    wb = load_workbook(output_file)
    ws = wb.active
    assert ws.max_row == 3
