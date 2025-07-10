# custom_patterns.py
# This file stores user-defined regex patterns.

MODEL_PATTERNS = [
    r"\bFS-\d+[A-Z]*\b",
    r"\bKM-\d+[A-Z]*\b",
    r"\bKM-C\d+[A-Z]*\b",
    r"\bECOSYS\s+[A-Z]+\d+\w*\b",
    r"\bTASKalfa\s+\d+\w*\b",
    r"\b(?:PF|DF|MK|DV)-\d+\b",
    r"\bTASKalfa Pro \d+c\b",
]

QA_NUMBER_PATTERNS = [
    r"\bQA-\d+\b",
    r"\bSB-\d+\b",
]
