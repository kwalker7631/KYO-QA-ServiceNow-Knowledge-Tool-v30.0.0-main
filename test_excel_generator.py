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


def test_generate_excel_with_qa_numbers(tmp_path):
    sample_df = pd.DataFrame([
        {
            "file_name": "qa_test.pdf",
            "Short description": "QA",
            "processing_status": "Success",
            "QA Numbers": "QA-123",
        }
    ])

    # create a minimal template workbook that includes a QA Numbers column
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.append([
        "Short description",
        "Meta",
        "Author",
        "QA Numbers",
        "Processing Status",
    ])
    ws.append(["", "", "", "", ""])  # placeholder row for merging
    template_path = tmp_path / "tmpl.xlsx"
    wb.save(template_path)

    output_file = tmp_path / "out_qan.xlsx"
    generate_excel(sample_df.to_dict("records"), output_file, template_path)

    wb2 = load_workbook(output_file)
    ws2 = wb2.active
    headers = [c.value for c in ws2[1]]
    qa_idx = headers.index("QA Numbers") + 1
    assert ws2.cell(row=2, column=qa_idx).value == "QA-123"
