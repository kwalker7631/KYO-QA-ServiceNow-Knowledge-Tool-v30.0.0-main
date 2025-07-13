# excel_generator.py - Definitive version with true cloning, styling, and robust data handling.
# This version correctly preserves all data from the original template.

import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import re
from pathlib import Path
import shutil

from logging_utils import setup_logger, log_info, log_warning, log_error
from custom_exceptions import ExcelGenerationError
from config import META_COLUMN_NAME, AUTHOR_COLUMN_NAME, DESCRIPTION_COLUMN_NAME

logger = setup_logger("excel_generator")

ILLEGAL_CHARACTERS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

# --- Style Definitions - Restored to match original flair ---
HEADER_FONT = Font(bold=True, color="FFFFFF", name="Calibri", size=11)
HEADER_FILL = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
CELL_FONT = Font(name="Calibri", size=11)
STATUS_FILLS = {
    "Success": PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"),
    "Needs Review": PatternFill(
        start_color="FFEB9C", end_color="FFEB9C", fill_type="solid"
    ),
    "Failed": PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"),
    "Protected": PatternFill(
        start_color="D9D9D9", end_color="D9D9D9", fill_type="solid"
    ),
    "Corrupted": PatternFill(
        start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"
    ),
    "OCR Failed": PatternFill(
        start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"
    ),
    "No Text Found": PatternFill(
        start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"
    ),
}

# Default header order as found in the sample template
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


class ExcelWriter:
    """Minimal Excel writer used in tests."""

    def __init__(self, file_path, headers=None):
        self.file_path = Path(file_path)
        self.headers = headers or []
        self.rows = []

    def add_row(self, row_dict):
        self.rows.append(row_dict)

    def save(self):
        try:
            import openpyxl

            wb = openpyxl.Workbook()
            ws = wb.active
            if self.headers:
                ws.append(self.headers)
            for row in self.rows:
                ws.append([row.get(h) for h in self.headers])
            wb.save(self.file_path)
        except Exception:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write("")


def sanitize_for_excel(value):
    """Sanitizes a value to be safely written to an Excel cell."""
    if isinstance(value, str):
        return ILLEGAL_CHARACTERS_RE.sub("", value)
    return value


def apply_styles(worksheet):
    """Applies all formatting and conditional coloring."""
    log_info(logger, "Applying professional formatting and styles...")

    header_row = worksheet[1]
    for cell in header_row:
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row in worksheet.iter_rows(min_row=2):
        for cell in row:
            cell.font = CELL_FONT
            cell.alignment = Alignment(
                wrap_text=True, vertical="top", horizontal="left"
            )

    for i, column in enumerate(worksheet.columns, 1):
        max_length = 0
        for cell in column:
            if cell.value:
                try:
                    max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
        adjusted_width = max_length + 2
        worksheet.column_dimensions[get_column_letter(i)].width = min(
            adjusted_width, 70
        )


def generate_excel(all_results, output_path, template_path):
    """
    Generates a formatted Excel file by cloning the template and merging new data.
    """
    try:
        if not all_results:
            raise ExcelGenerationError(
                "No data was processed to generate an Excel file."
            )

        new_data_df = pd.DataFrame(all_results).applymap(sanitize_for_excel)
        new_data_df["merge_key"] = new_data_df["file_name"].apply(
            lambda x: Path(x).stem
        )
        new_data_df.set_index("merge_key", inplace=True)

        if not template_path.exists():
            raise ExcelGenerationError(f"Template file not found at: {template_path}")

        shutil.copy(template_path, output_path)

        workbook = openpyxl.load_workbook(output_path)
        worksheet = workbook.active

        header = [cell.value for cell in worksheet[1]]
        desc_col_idx = (
            header.index(DESCRIPTION_COLUMN_NAME)
            if DESCRIPTION_COLUMN_NAME in header
            else -1
        )
        meta_col_idx = (
            header.index(META_COLUMN_NAME) if META_COLUMN_NAME in header else -1
        )
        author_col_idx = (
            header.index(AUTHOR_COLUMN_NAME) if AUTHOR_COLUMN_NAME in header else -1
        )

        if desc_col_idx == -1:
            raise ExcelGenerationError(
                f"Template missing required column: '{DESCRIPTION_COLUMN_NAME}'"
            )

        for row_num, row_cells in enumerate(worksheet.iter_rows(min_row=2), start=2):
            desc_val = row_cells[desc_col_idx].value
            if not desc_val:
                continue

            # Allow template short descriptions prefixed with "Processed:" (case-insensitive) to
            # merge correctly with new data indexed by file name.
            row_text = re.sub(r"^Processed:\s*", "", str(desc_val), flags=re.IGNORECASE)
            row_key = Path(row_text).stem
            if row_key in new_data_df.index:
                new_row_data = new_data_df.loc[row_key]

                if meta_col_idx != -1 and META_COLUMN_NAME in new_row_data:
                    worksheet.cell(row=row_num, column=meta_col_idx + 1).value = (
                        new_row_data[META_COLUMN_NAME]
                    )
                if author_col_idx != -1 and AUTHOR_COLUMN_NAME in new_row_data:
                    worksheet.cell(row=row_num, column=author_col_idx + 1).value = (
                        new_row_data[AUTHOR_COLUMN_NAME]
                    )

                if fill := STATUS_FILLS.get(new_row_data["processing_status"]):
                    for cell in row_cells:
                        cell.fill = fill

        apply_styles(worksheet)
        workbook.save(output_path)

        log_info(
            logger, f"Successfully created cloned and updated Excel file: {output_path}"
        )
        return str(output_path)

    except Exception as e:
        log_error(logger, f"Excel generation failed: {e}", exc_info=True)
        raise ExcelGenerationError(f"Failed to generate Excel file: {e}")
