# processing_engine.py - Definitive fix for data pipeline and review process.

import time
import json
from pathlib import Path
import shutil

# Local Imports
from ocr_utils import process_single_document, _is_ocr_needed
from data_harvesters import harvest_all_data
from excel_generator import generate_excel
from custom_exceptions import FileLockError
from config import (
    PDF_TXT_DIR, CACHE_DIR, OUTPUT_DIR, META_COLUMN_NAME, AUTHOR_COLUMN_NAME
)

def clear_review_folder():
    """Clear any existing review files before a new run."""
    if PDF_TXT_DIR.exists():
        for f in PDF_TXT_DIR.glob("*.txt"):
            try: f.unlink()
            except OSError as e: print(f"Error deleting review file {f}: {e}")

def get_cache_path(pdf_path: Path) -> Path:
    """Generate a unique cache file path for a given PDF."""
    try: return CACHE_DIR / f"{pdf_path.stem}_{pdf_path.stat().st_size}.json"
    except FileNotFoundError: return CACHE_DIR / f"{pdf_path.stem}_unknown.json"

def process_single_pdf(pdf_path: Path, progress_queue, ignore_cache: bool = False) -> dict:
    """Processes a single PDF, with robust error handling and review file creation."""
    pdf_path = Path(pdf_path)
    filename = pdf_path.name
    cache_path = get_cache_path(pdf_path)

    progress_queue.put({"type": "log", "msg": f"Starting: {filename}"})

    if not ignore_cache and cache_path.exists():
        try:
            cached_data = json.loads(cache_path.read_text(encoding='utf-8'))
            if "processing_status" in cached_data and META_COLUMN_NAME in cached_data:
                progress_queue.put({"type": "log", "msg": f"Cache hit for: {filename}"})
                if cached_data.get("review_info"):
                    progress_queue.put({"type": "review_item", "data": cached_data["review_info"]})
                if cached_data.get("ocr_used"):
                    progress_queue.put({"type": "increment_counter", "counter": "ocr"})
                progress_queue.put({"type": "file_complete", "status": cached_data["processing_status"]})
                return cached_data
        except (json.JSONDecodeError, KeyError):
            progress_queue.put({"type": "log", "msg": f"Cache corrupt for {filename}, reprocessing."})

    result = {
        "file_name": filename,
        META_COLUMN_NAME: "",
        AUTHOR_COLUMN_NAME: "",
        "qa_numbers": "",
        "processing_status": "Failed",
        "failure_reason": "",
        "ocr_used": False,
        "review_info": None,
        "qa_numbers": "",
        "Short description": f"Processed: {filename}",
        QA_NUMBERS_KEY: "",
    }
    start_time = time.time()

    try:
        ocr_needed = _is_ocr_needed(str(pdf_path.resolve()))
        result['ocr_used'] = ocr_needed
        led_status = "OCR" if ocr_needed else "Processing"
        progress_queue.put({"type": "status", "msg": f"{led_status}: {filename}", "led": led_status})
        if ocr_needed: progress_queue.put({"type": "increment_counter", "counter": "ocr"})

        status, reason, text = process_single_document(pdf_path)

        if status == "success":
            progress_queue.put({"type": "status", "msg": f"Extracting data: {filename}", "led": "AI"})
            data = harvest_all_data(text, filename)
            result[META_COLUMN_NAME] = data["models"]
            result[AUTHOR_COLUMN_NAME] = data["author"]
            result["qa_numbers"] = data["qa_numbers"]

            if result[META_COLUMN_NAME] == "Not Found":
                result["processing_status"] = "Needs Review"
                result["failure_reason"] = "No model patterns were found in the document."
                
                # --- DEFINITIVE FIX: Reliably create the text file for review ---
                review_txt_path = PDF_TXT_DIR / f"{pdf_path.stem}.txt"
                review_txt_path.write_text(text, encoding='utf-8')
                
                # Pass the full path to the text file in the review info
                result["review_info"] = {
                    "filename": filename, 
                    "reason": result["failure_reason"], 
                    "txt_path": str(review_txt_path.resolve()), # Use absolute path
                    "pdf_path": str(pdf_path.resolve())
                }
                progress_queue.put({"type": "review_item", "data": result["review_info"]})
            else:
                result["processing_status"] = "Success"
        else:
            status_map = {"protected": "Protected", "corrupted": "Corrupted", "ocr_failed": "OCR Failed", "no_text": "No Text Found"}
            result["processing_status"] = status_map.get(status, "Failed")
            result["failure_reason"] = reason
            result[META_COLUMN_NAME] = f"Error: {result['processing_status']}"

    except Exception as e:
        result["processing_status"] = "Failed"; result["failure_reason"] = f"A critical error occurred: {e}"
        result[META_COLUMN_NAME] = "Error: Critical Failure"
        progress_queue.put({"type": "log", "tag": "error", "msg": f"CRITICAL ERROR on {filename}: {e}"})

    result['processing_time'] = time.time() - start_time
    
    try: cache_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    except Exception as e: progress_queue.put({"type": "log", "tag": "warning", "msg": f"Failed to write cache for {filename}: {e}"})
    
    progress_queue.put({"type": "file_complete", "status": result["processing_status"]})
    return result

def run_processing_job(job_info, progress_queue, cancel_event, pause_event):
    """The main orchestrator for a processing job."""
    try:
        excel_path = Path(job_info["excel_path"])
        input_path = job_info["input_path"]
        is_rerun = job_info.get("is_rerun", False)
        
        if not is_rerun: clear_review_folder()
        
        files_to_process = [Path(f) for f in input_path] if isinstance(input_path, list) else list(Path(input_path).glob("*.pdf"))

        if not files_to_process:
            progress_queue.put({"type": "log", "msg": "No PDF files found."}); progress_queue.put({"type": "finish", "status": "No Files"}); return

        progress_queue.put({"type": "log", "msg": f"Found {len(files_to_process)} files."})

        all_results = []
        for i, pdf_file in enumerate(files_to_process):
            if cancel_event.is_set(): progress_queue.put({"type": "log", "msg": "Job cancelled."}); break
            while pause_event.is_set(): time.sleep(0.5)
            progress_queue.put({"type": "progress", "current": i + 1, "total": len(files_to_process)})
            result = process_single_pdf(pdf_file, progress_queue, ignore_cache=is_rerun)
            all_results.append(result)

        if cancel_event.is_set(): progress_queue.put({"type": "finish", "status": "Cancelled"}); return

        progress_queue.put({"type": "status", "msg": "Generating Excel report...", "led": "Saving"})
        
        ts = time.strftime("%Y%m%d-%H%M%S")
        output_filename = f"Processed_{excel_path.stem}_{ts}.xlsx"
        output_path = OUTPUT_DIR / output_filename

        final_excel_path = generate_excel(all_results, output_path, template_path=excel_path)

        progress_queue.put({"type": "result_path", "path": final_excel_path})
        progress_queue.put({"type": "enable_open_result"})
        progress_queue.put({"type": "log", "tag": "success", "msg": f"Job complete. Report saved to: {output_filename}"})
        progress_queue.put({"type": "finish", "status": "Complete"})

    except FileLockError as e:
        progress_queue.put({"type": "log", "tag": "error", "msg": str(e)}); progress_queue.put({"type": "finish", "status": "Error: File Locked"})
    except Exception as e:
        import traceback
        progress_queue.put({"type": "log", "tag": "error", "msg": f"Critical job error: {e}\n{traceback.format_exc()}"}); progress_queue.put({"type": "finish", "status": f"Error: {e}"})
