# ocr_utils.py - Enhanced OCR utilities with robust error handling and corrected file path handling
import fitz  # PyMuPDF
import os
from pathlib import Path
from logging_utils import setup_logger, log_info, log_error, log_warning
import pytesseract
from PIL import Image
import io
import cv2  # OpenCV for image processing
import numpy as np
from custom_exceptions import (
    PDFProtectionError, PDFCorruptionError, OCRProcessingError, 
    TesseractNotFoundError, PDFExtractionError
)

# Try to import pikepdf for robust PDF protection detection
try:
    import pikepdf
    PIKEPDF_AVAILABLE = True
except ImportError:
    PIKEPDF_AVAILABLE = False

logger = setup_logger("ocr_utils")

def init_tesseract():
    """Initialize Tesseract OCR if available."""
    try:
        portable_path = Path(__file__).parent / "tesseract" / "tesseract.exe"
        if portable_path.exists():
            pytesseract.pytesseract.tesseract_cmd = str(portable_path)
            log_info(logger, f"Portable Tesseract found at: {portable_path}")
            return True
        
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                log_info(logger, f"Tesseract found at: {path}")
                return True
        
        try:
            output = os.popen("tesseract --version").read()
            if "tesseract" in output.lower():
                log_info(logger, "Tesseract found in system PATH")
                return True
        except Exception:
            pass
            
        log_warning(logger, "Tesseract OCR not found. Image-based OCR will be disabled.")
        return False
    except ImportError:
        log_warning(logger, "pytesseract or Pillow not installed. Image-based OCR disabled.")
        return False
    except Exception as e:
        log_error(logger, f"An unexpected error occurred during Tesseract initialization: {e}")
        return False

TESSERACT_AVAILABLE = init_tesseract()

def check_pdf_protection(pdf_path):
    """
    Check if a PDF is password-protected or encrypted using multiple methods.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        tuple: (is_protected, protection_type, error_message)
    """
    pdf_path = Path(pdf_path)
    
    # Method 1: Try pikepdf first (most reliable for password detection)
    if PIKEPDF_AVAILABLE:
        try:
            # FIX: Convert Path object to string for robust file handling
            with pikepdf.open(str(pdf_path)) as pdf:
                if pdf.is_encrypted:
                    return True, "encrypted", "PDF is password-protected (detected by pikepdf)"
                return False, "none", None
        except pikepdf.PasswordError:
            return True, "password", "PDF requires password to open"
        except pikepdf.PdfError as e:
            if "password" in str(e).lower() or "encrypt" in str(e).lower():
                return True, "encrypted", f"PDF is protected: {str(e)}"
            # Continue to other methods if it's not a protection issue
        except Exception as e:
            log_warning(logger, f"pikepdf check failed for {pdf_path.name}: {e}")
    
    # Method 2: Try PyMuPDF as fallback
    try:
        # FIX: Convert Path object to string for robust file handling
        with fitz.open(str(pdf_path)) as doc:
            if doc.is_encrypted:
                return True, "encrypted", "PDF is encrypted (detected by PyMuPDF)"
            if hasattr(doc, 'needs_pass') and doc.needs_pass:
                return True, "password", "PDF requires password (detected by PyMuPDF)"
            return False, "none", None
    except Exception as e:
        if "password" in str(e).lower() or "encrypt" in str(e).lower():
            return True, "unknown", f"PDF appears protected: {str(e)}"
        # If it's not a protection issue, it might be corruption
        return False, "none", None
    
    return False, "none", None

def process_single_document(pdf_path):
    """
    Process a single PDF document with comprehensive error handling.
    
    Args:
        pdf_path: Path to the PDF file to process
        
    Returns:
        tuple: (status, failure_reason, extracted_text)
        - status: "success", "protected", "corrupted", "ocr_failed", "no_text", "error"
        - failure_reason: Human-readable string explaining any failure, None if success
        - extracted_text: Extracted text content, empty string if failed
    """
    pdf_path = Path(pdf_path)
    
    try:
        # Step 1: Check for PDF protection first
        is_protected, protection_type, error_msg = check_pdf_protection(pdf_path)
        if is_protected:
            log_warning(logger, f"Protected PDF detected: {pdf_path.name} - {error_msg}")
            return "protected", f"File is password protected: {error_msg}", ""
        
        # Step 2: Try direct text extraction first
        try:
            # FIX: Convert Path object to string for robust file handling
            with fitz.open(str(pdf_path)) as doc:
                if not doc.is_pdf:
                    return "corrupted", "File is not a valid PDF document", ""
                
                text = "".join(page.get_text() for page in doc)
                
                if text and len(text.strip()) > 50:
                    log_info(logger, f"Direct text extraction successful for {pdf_path.name}")
                    return "success", None, text
                    
        except Exception as e:
            if "password" in str(e).lower() or "encrypt" in str(e).lower():
                return "protected", f"PDF requires password: {str(e)}", ""
            elif "corrupt" in str(e).lower() or "damaged" in str(e).lower():
                return "corrupted", f"PDF file appears corrupted: {str(e)}", ""
            else:
                log_warning(logger, f"Direct text extraction failed for {pdf_path.name}: {e}")
        
        # Step 3: Fallback to OCR if direct extraction failed
        if not TESSERACT_AVAILABLE:
            return "ocr_failed", "No text found in PDF and Tesseract OCR is not available", ""
        
        log_info(logger, f"Attempting OCR on {pdf_path.name}")
        ocr_text, ocr_failure = extract_text_with_ocr(pdf_path)
        
        if ocr_failure:
            return "ocr_failed", ocr_failure, ""
        elif not ocr_text or len(ocr_text.strip()) < 10:
            return "no_text", "OCR completed but no readable text was found", ""
        else:
            log_info(logger, f"OCR extraction successful for {pdf_path.name}")
            return "success", None, ocr_text
            
    except PDFProtectionError as e:
        return "protected", str(e), ""
    except PDFCorruptionError as e:
        return "corrupted", str(e), ""
    except Exception as e:
        log_error(logger, f"Unexpected error processing {pdf_path.name}: {e}")
        return "error", f"Unexpected processing error: {str(e)}", ""

def _is_ocr_needed(pdf_path):
    """Pre-checks a PDF to see if it's image-based and likely requires OCR."""
    try:
        # First check for protection
        is_protected, protection_type, error_msg = check_pdf_protection(pdf_path)
        if is_protected:
            raise PDFProtectionError(error_msg)
        
        # FIX: Convert Path object to string for robust file handling
        with fitz.open(str(pdf_path)) as doc:
            if not doc.is_pdf:
                raise PDFCorruptionError(f"File {Path(pdf_path).name} is not a valid PDF")
            
            text_length = sum(len(page.get_text("text")) for page in doc)
            if text_length < 150:
                return True
    except PDFProtectionError:
        raise  # Re-raise protection errors
    except Exception as e:
        log_warning(logger, f"Could not pre-check PDF {Path(pdf_path).name} for OCR needs: {e}")
        return True
    return False

def extract_text_from_pdf(pdf_path):
    """
    Legacy function for backward compatibility.
    Now returns the extracted text and logs any issues.
    """
    status, failure_reason, extracted_text = process_single_document(pdf_path)
    
    if status == "success":
        return extracted_text
    else:
        log_error(logger, f"Failed to extract text from {Path(pdf_path).name}: {failure_reason}")
        return ""

def extract_text_with_ocr(pdf_path):
    """
    Extract text from a PDF using advanced OCR preprocessing.
    
    Returns:
        tuple: (extracted_text, failure_reason)
    """
    if not TESSERACT_AVAILABLE:
        return "", "Tesseract OCR is not available on this system"
        
    all_text = []
    pdf_path = Path(pdf_path)
    
    try:
        # FIX: Convert Path object to string for robust file handling
        with fitz.open(str(pdf_path)) as doc:
            for page_num, page in enumerate(doc):
                try:
                    # Render page at high DPI for better OCR accuracy
                    pix = page.get_pixmap(dpi=300)
                    img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                    
                    # Convert to OpenCV format
                    if img_data.shape[2] == 4:  # RGBA
                        img_cv = cv2.cvtColor(img_data, cv2.COLOR_RGBA2BGR)
                    else:  # RGB
                        img_cv = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)

                    # Advanced image preprocessing for better OCR
                    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                    
                    # Apply adaptive thresholding
                    binary_img = cv2.adaptiveThreshold(
                        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                    )
                    
                    # Noise reduction
                    denoised = cv2.medianBlur(binary_img, 3)
                    
                    # OCR with optimized settings
                    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,;:!?-_()[]{}@#$%^&*+=<>/\|"'''
                    page_text = pytesseract.image_to_string(denoised, lang='eng', config=custom_config)
                    
                    if page_text.strip():
                        all_text.append(page_text.strip())
                        log_info(logger, f"OCR processed page {page_num+1} of {pdf_path.name} successfully")
                    else:
                        log_warning(logger, f"No text found on page {page_num+1} of {pdf_path.name}")
                    
                except Exception as e:
                    log_warning(logger, f"OCR failed for page {page_num+1} of {pdf_path.name}: {e}")
                    continue
                
        result = "\n\n".join(all_text)
        
        if result.strip():
            log_info(logger, f"OCR extraction complete for {pdf_path.name}: {len(result)} characters extracted")
            return result, None
        else:
            return "", "OCR completed but no readable text was extracted from any page"
            
    except Exception as e:
        log_error(logger, f"OCR extraction failed for {pdf_path.name}: {e}")
        return "", f"OCR processing failed: {str(e)}"
