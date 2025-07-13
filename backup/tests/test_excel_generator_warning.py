import importlib
import sys
import types
import logging

from config import META_COLUMN_NAME, AUTHOR_COLUMN_NAME, DESCRIPTION_COLUMN_NAME


def test_warning_logged_for_missing_row(tmp_path, monkeypatch, caplog):
    class Column(list):
        def apply(self, func):
            return [func(x) for x in self]

    class DataFrame:
        def __init__(self, records):
            self.records = [dict(r) for r in records]
            self.index = []

        def applymap(self, func):
            for r in self.records:
                for k, v in r.items():
                    r[k] = func(v)
            return self

        def __getitem__(self, key):
            return Column([r[key] for r in self.records])

        def __setitem__(self, key, values):
            for r, v in zip(self.records, values):
                r[key] = v

        def set_index(self, col, inplace=False):
            self.index = [r[col] for r in self.records]

        @property
        def loc(self):
            df = self

            class Loc:
                def __getitem__(self, key):
                    idx = df.index.index(key)
                    return df.records[idx]

            return Loc()

    pandas_stub = types.ModuleType("pandas")
    pandas_stub.DataFrame = DataFrame
    monkeypatch.setitem(sys.modules, "pandas", pandas_stub)

    class Cell:
        def __init__(self, value=None):
            self.value = value
            self.fill = None

    class Worksheet:
        def __init__(self):
            self.rows = [
                [
                    Cell(DESCRIPTION_COLUMN_NAME),
                    Cell(META_COLUMN_NAME),
                    Cell(AUTHOR_COLUMN_NAME),
                    Cell("Processing Status"),
                ],
                [Cell("missing.xlsx"), Cell(), Cell(), Cell()],
            ]

        def __getitem__(self, idx):
            return self.rows[idx - 1]

        def iter_rows(self, min_row=1):
            return iter(self.rows[min_row - 1 :])

        def cell(self, row, column):
            return self.rows[row - 1][column - 1]

    class Workbook:
        def __init__(self):
            self.active = Worksheet()

        def save(self, path):
            pass

    openpyxl_stub = types.ModuleType("openpyxl")
    openpyxl_stub.load_workbook = lambda path: Workbook()
    styles_mod = types.ModuleType("openpyxl.styles")
    class Dummy:
        def __init__(self, *a, **k):
            pass

    styles_mod.Font = Dummy
    styles_mod.PatternFill = Dummy
    styles_mod.Alignment = Dummy
    utils_mod = types.ModuleType("openpyxl.utils")
    utils_mod.get_column_letter = lambda i: "A"
    openpyxl_stub.styles = styles_mod
    openpyxl_stub.utils = utils_mod
    monkeypatch.setitem(sys.modules, "openpyxl", openpyxl_stub)
    monkeypatch.setitem(sys.modules, "openpyxl.styles", styles_mod)
    monkeypatch.setitem(sys.modules, "openpyxl.utils", utils_mod)

    exg = importlib.reload(importlib.import_module("excel_generator"))
    monkeypatch.setattr(exg, "apply_styles", lambda ws: None)
    monkeypatch.setattr(exg.shutil, "copy", lambda src, dst: None)

    template = tmp_path / "template.xlsx"
    template.touch()
    output = tmp_path / "out.xlsx"

    all_results = [
        {
            "file_name": "other.xlsx",
            "processing_status": "Success",
            META_COLUMN_NAME: "meta",
            AUTHOR_COLUMN_NAME: "author",
        }
    ]

    with caplog.at_level(logging.WARNING):
        exg.generate_excel(all_results, output, template)

    assert any("missing.xlsx" in rec.message and "2" in rec.message for rec in caplog.records)
