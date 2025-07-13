import pytest

try:
    from openpyxl import Workbook  # noqa: F401
except Exception:
    Workbook = None

if Workbook is None:
    pytest.skip("Required libraries not installed", allow_module_level=True)

from excel_generator import ExcelWriter


def test_excel_writer_save(tmp_path):
    file_path = tmp_path / "writer_test.xlsx"
    writer = ExcelWriter(str(file_path), headers=["A", "B"])
    writer.add_row({"A": 1, "B": 2})
    writer.save()
    assert file_path.exists()
