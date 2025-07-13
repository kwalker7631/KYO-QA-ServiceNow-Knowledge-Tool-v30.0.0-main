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
    "Needs Review": PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid"),
    "Failed": PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"),
    "Protected": PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid"),
    "Corrupted": PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"),
    "OCR Failed": PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"),
    "No Text Found": PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"),
}

DEFAULT_TEMPLATE_PATH = Path("Sample_Set/kb_knowledge_Template.xlsx")

def _load_default_headers(path=DEFAULT_TEMPLATE_PATH):
    try:
        import zipfile, xml.etree.ElementTree as ET
        with zipfile.ZipFile(path) as z:
            shared = ET.fromstring(z.read("xl/sharedStrings.xml"))
            strings = [t.text for t in shared.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')]
            sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
            ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            first_row = sheet.find('.//m:sheetData/m:row', ns)
            headers = []
            for c in first_row:
                v = c.find('m:v', ns)
                if v is None:
                    headers.append("")
                elif c.get('t') == 's':
                    headers.append(strings[int(v.text)])
                else:
                    headers.append(v.text)
            return headers
    except Exception:
        return []

DEFAULT_TEMPLATE_HEADERS = _load_default_headers()

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
            cell.alignment = Alignment(wrap_text=True, vertical="top", horizontal="left")

    for i, column in enumerate(worksheet.columns, 1):
        max_length = 0
        for cell in column:
            if cell.value:
                try: max_length = max(max_length, len(str(cell.value)))
                except: pass
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[get_column_letter(i)].width = min(adjusted_width, 70)

def generate_excel(all_results, output_path, template_path):
    """
    Generates a formatted Excel file by cloning the template and merging new data.
    """
    try:
        if not all_results:
            raise ExcelGenerationError("No data was processed to generate an Excel file.")
        
        new_data_df = pd.DataFrame(all_results).applymap(sanitize_for_excel)
        new_data_df['merge_key'] = new_data_df['file_name'].apply(lambda x: Path(x).stem)
        new_data_df.set_index('merge_key', inplace=True)

        if not template_path.exists():
            raise ExcelGenerationError(f"Template file not found at: {template_path}")
        
        shutil.copy(template_path, output_path)
        
        workbook = openpyxl.load_workbook(output_path)
        worksheet = workbook.active

        header = [cell.value for cell in worksheet[1]]
        desc_col_idx = header.index(DESCRIPTION_COLUMN_NAME) if DESCRIPTION_COLUMN_NAME in header else -1
        meta_col_idx = header.index(META_COLUMN_NAME) if META_COLUMN_NAME in header else -1
        author_col_idx = header.index(AUTHOR_COLUMN_NAME) if AUTHOR_COLUMN_NAME in header else -1

        if desc_col_idx == -1:
            raise ExcelGenerationError(f"Template missing required column: '{DESCRIPTION_COLUMN_NAME}'")

        matched_keys = set()
        for row_num, row_cells in enumerate(worksheet.iter_rows(min_row=2), start=2):
            desc_val = row_cells[desc_col_idx].value
            if not desc_val:
                continue

            row_key = Path(str(desc_val)).stem
            if row_key in new_data_df.index:
                matched_keys.add(row_key)
                new_row_data = new_data_df.loc[row_key]

                if meta_col_idx != -1 and META_COLUMN_NAME in new_row_data:
                    worksheet.cell(row=row_num, column=meta_col_idx + 1).value = new_row_data[META_COLUMN_NAME]
                if author_col_idx != -1 and AUTHOR_COLUMN_NAME in new_row_data:
                    worksheet.cell(row=row_num, column=author_col_idx + 1).value = new_row_data[AUTHOR_COLUMN_NAME]

                if fill := STATUS_FILLS.get(new_row_data['processing_status']):
                    for cell in row_cells:
                        cell.fill = fill

        missing_keys = [k for k in new_data_df.index if k not in matched_keys]
        if missing_keys:
            log_info(logger, f"Appending {len(missing_keys)} new row(s) to template")
        for key in missing_keys:
            new_row_data = new_data_df.loc[key]
            new_row = [new_row_data.get(col, "") for col in header]
            worksheet.append(new_row)
            row_cells = list(worksheet.iter_rows(min_row=worksheet.max_row, max_row=worksheet.max_row))[0]
            if fill := STATUS_FILLS.get(new_row_data['processing_status']):
                for cell in row_cells:
                    cell.fill = fill

        apply_styles(worksheet)
        workbook.save(output_path)

        log_info(logger, f"Successfully created cloned and updated Excel file: {output_path}")
        return str(output_path)

    except Exception as e:
        log_error(logger, f"Excel generation failed: {e}", exc_info=True)
        raise ExcelGenerationError(f"Failed to generate Excel file: {e}")
