import pandas as pd
from openpyxl import load_workbook, Workbook

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


def test_generate_excel_with_template(tmp_path):
    data = [{"Short description": "Test", "Article body": "body"}]

    template = tmp_path / "template.xlsx"
    wb = Workbook()
    wb.active.title = "Existing"
    wb.save(template)

    output_file = tmp_path / "out_template.xlsx"
    generate_excel(data, output_file, template)

    assert output_file.exists()
    out_wb = load_workbook(output_file)
    assert "Existing" in out_wb.sheetnames
    assert "ServiceNow Import" in out_wb.sheetnames
