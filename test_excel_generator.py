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
from config import META_COLUMN_NAME, AUTHOR_COLUMN_NAME


def test_generate_excel_headers(tmp_path):
    sample_df = pd.DataFrame([{"Short description": "Test", "Article body": "body"}])
    output_file = tmp_path / "out.xlsx"
    generate_excel(sample_df.to_dict("records"), output_file)
    assert output_file.exists()

    wb = load_workbook(output_file)
    ws = wb.active
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    assert headers == DEFAULT_TEMPLATE_HEADERS


def test_generate_excel_with_template(tmp_path):
    sample_df = pd.DataFrame([{"Short description": "Test", "Article body": "body"}])
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


def test_merge_short_desc_with_prefix(tmp_path):
    if pd is None or load_workbook is None:
        pytest.skip("Required libraries not installed", allow_module_level=True)

    template = Path("Sample_Set/kb_knowledge_Template.xlsx")
    output_file = tmp_path / "merge_prefix.xlsx"

    sample_results = [
        {
            "file_name": "prefix_test.pdf",
            META_COLUMN_NAME: "meta",
            AUTHOR_COLUMN_NAME: "author",
            "processing_status": "Success",
        }
    ]

    # Create a copy of the template and embed the prefixed short description
    wb = load_workbook(template)
    ws = wb.active
    sd_idx = DEFAULT_TEMPLATE_HEADERS.index("Short description") + 1
    ws.cell(row=2, column=sd_idx).value = "Processed: prefix_test.pdf"
    temp_template = tmp_path / "temp_template.xlsx"
    wb.save(temp_template)

    generate_excel(sample_results, output_file, temp_template)

    wb = load_workbook(output_file)
    ws = wb.active
    meta_idx = DEFAULT_TEMPLATE_HEADERS.index(META_COLUMN_NAME) + 1
    author_idx = DEFAULT_TEMPLATE_HEADERS.index(AUTHOR_COLUMN_NAME) + 1
    assert ws.cell(row=2, column=meta_idx).value == "meta"
    assert ws.cell(row=2, column=author_idx).value == "author"
