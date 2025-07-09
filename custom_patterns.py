# custom_patterns.py
# This file stores user-defined regex patterns.

MODEL_PATTERNS = [
    r'\\\\\\\\bFS-\\\\\\\\d+[A-Z]*\\\\\\\\b',
    r'\\\\\\\\bKM-\\\\\\\\d+[A-Z]*\\\\\\\\b',
    r'\\\\\\\\bECOSYS\\\\\\\\s+[A-Z]+\\\\\\\\d+[a-z]*\\\\\\\\b',
    r'\\\\\\\\bTASKalfa\\\\\\\\s+\\\\\\\\d+[a-z]*\\\\\\\\b',
    r'\\\\\\\\bPF-\\\\\\\\d+\\\\\\\\b',
    r'\\\\\\\\bDF-\\\\\\\\d+\\\\\\\\b',
    r'\\\\\\\\bMK-\\\\\\\\d+\\\\\\\\b',
    r'\\\\\\\\bDV-\\\\\\\\d+\\\\\\\\b',
    r'\\\\\\\\bTASKalfa\\\\\\\\ Pro\\\\\\\\ \\\\\\\\d+c\\\\\\\\b',
    r'\\bTASKalfa\\ Pro\\ \\d+c\\b',
]

QA_NUMBER_PATTERNS = [
]
