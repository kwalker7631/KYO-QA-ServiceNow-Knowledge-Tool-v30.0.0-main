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

from excel_generator import generate_excel
from config import META_COLUMN_NAME, QA_NUMBERS_COLUMN_NAME

DEFAULT_TEMPLATE_HEADERS = [
    "Active",
    "Article type",
    "Author",
    "Category(category)",
    "Configuration item",
    "Confidence",
    "Description",
    "Attachment link",
    "Disable commenting",
    "Disable suggesting",
    "Display attachments",
    "Flagged",
    "Governance",
    "Category(kb_category)",
    "Knowledge Base",
    "Meta",
    "Meta Description",
    "Ownership Group",
    "Published",
    "Scheduled publish date",
    "Short description",
    "Article body",
    "Topic",
    "Problem Code",
    "Product Description",
    "Ticket#",
    "Valid to",
    "View as allowed",
    "Wiki",
    "Sys ID",
    "Process Status",
    "Needs Review",
]


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


def test_generate_excel_includes_qa_numbers(tmp_path):
    sample_df = pd.DataFrame([
        {
            "file_name": "doc1.pdf",
            "Short description": "doc1",
            META_COLUMN_NAME: "Model1",
            "qa_numbers": "QA1234",
        }
    ])
    output_file = tmp_path / "qa.xlsx"
    template = Path("Sample_Set/kb_knowledge_Template.xlsx")
    generate_excel(sample_df.to_dict("records"), output_file, template)
    wb = load_workbook(output_file)
    ws = wb.active
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    if QA_NUMBERS_COLUMN_NAME in headers:
        qa_idx = headers.index(QA_NUMBERS_COLUMN_NAME) + 1
        assert ws.cell(row=2, column=qa_idx).value == "QA1234"
    else:
        meta_idx = headers.index(META_COLUMN_NAME) + 1
        assert "QA1234" in (ws.cell(row=2, column=meta_idx).value or "")
