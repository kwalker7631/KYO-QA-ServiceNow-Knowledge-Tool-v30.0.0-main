import importlib
import sys
import types
from pathlib import Path

import pandas as pd


def test_generate_excel_with_template(tmp_path, monkeypatch):
    """Ensure data is written when using an Excel template."""
    # Build fake openpyxl module
    fake_openpyxl = types.ModuleType("openpyxl")

    class FakeCell:
        def __init__(self):
            self.value = None

    class FakeWorksheet:
        def __init__(self, title="Sheet1"):
            self.title = title
            self.cells = {}

        def cell(self, row, column, value=None):
            key = (row, column)
            cell = self.cells.setdefault(key, FakeCell())
            if value is not None:
                cell.value = value
            return cell

    class FakeWorkbook:
        def __init__(self):
            self.worksheets = [FakeWorksheet("Template")]  # template sheet

        @property
        def sheetnames(self):
            return [ws.title for ws in self.worksheets]

        def remove(self, ws):
            self.worksheets.remove(ws)

        def create_sheet(self, title):
            ws = FakeWorksheet(title)
            self.worksheets.append(ws)
            return ws

        def save(self, path):
            Path(path).write_text("saved")
            self.saved_path = path

    created = []

    def fake_workbook_factory():
        wb = FakeWorkbook()
        created.append(wb)
        return wb

    def fake_load_workbook(path):
        return FakeWorkbook()

    class FakeWorksheetCopy:
        def __init__(self, src, tgt):
            pass

        def copy_worksheet(self):
            pass

    def fake_dataframe_to_rows(df, index=False, header=True):
        rows = []
        if header:
            rows.append(list(df.columns))
        for row in df.itertuples(index=index):
            values = list(row)[1:] if index else list(row)
            rows.append(values)
        return rows

    fake_openpyxl.load_workbook = fake_load_workbook
    fake_openpyxl.Workbook = fake_workbook_factory
    fake_openpyxl.worksheet = types.SimpleNamespace(
        copier=types.SimpleNamespace(WorksheetCopy=FakeWorksheetCopy)
    )
    fake_openpyxl.utils = types.SimpleNamespace(
        dataframe=types.SimpleNamespace(dataframe_to_rows=fake_dataframe_to_rows)
    )

    monkeypatch.setitem(sys.modules, "openpyxl", fake_openpyxl)

    import excel_generator

    importlib.reload(excel_generator)

    data = [
        {"Short description": "foo"},
        {"Short description": "bar"},
    ]
    output_file = tmp_path / "out.xlsx"
    excel_generator.generate_excel(data, output_file, "template.xlsx")

    wb = created[0]
    ws = wb.worksheets[-1]
    assert ws.cell(2, 1).value == "foo"
    assert ws.cell(3, 1).value == "bar"
    assert output_file.exists()

