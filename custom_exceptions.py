# custom_exceptions.py - Enhanced Custom exception classes for KYO QA Tool

class KYOQAToolError(Exception):
    """Base exception for all KYO QA Tool errors."""
    pass

class FileLockError(KYOQAToolError):
    """Raised when a file is locked by another process."""
    pass

class ExcelGenerationError(KYOQAToolError):
    """Raised when Excel file generation fails."""
    pass

class PDFExtractionError(KYOQAToolError):
    """Raised when PDF text extraction fails."""
    pass

class PDFProtectionError(KYOQAToolError):
    """Raised when a PDF is password-protected or encrypted."""
    pass

class PDFCorruptionError(KYOQAToolError):
    """Raised when a PDF file appears to be corrupted."""
    pass

class OCRProcessingError(KYOQAToolError):
    """Raised when OCR processing fails."""
    pass

class PatternMatchError(KYOQAToolError):
    """Raised when pattern matching fails."""
    pass

class ConfigurationError(KYOQAToolError):
    """Raised when there's a configuration issue."""
    pass

class TesseractNotFoundError(KYOQAToolError):
    """Raised when Tesseract OCR is not available."""
    pass