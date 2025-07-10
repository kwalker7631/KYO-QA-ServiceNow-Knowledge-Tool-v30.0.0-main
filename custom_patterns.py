# custom_patterns.py
# This file stores user-defined regex patterns.

MODEL_PATTERNS = [
    r'\bFS-\d+[A-Z]*\b',         # e.g. FS-C5250DN
    r'\bKM-\d+[A-Z]*\b',         # e.g. KM-2560 or KM-C2520
    r'\bECOSYS\s+[A-Z]+\d+[a-z]*\b',  # e.g. ECOSYS P3055dn
    r'\bTASKalfa\s+\d+[a-z]*\b',      # e.g. TASKalfa 8000i
    r'\bPF-\d+\b',              # PF-740 add-on units
    r'\bDF-\d+\b',              # DF-780 document feeders
    r'\bMK-\d+\b',              # MK-726 maintenance kit
    r'\bDV-\d+\b',              # DV-1150 developer units
    r'\bTASKalfa Pro \d+c\b',   # TASKalfa Pro 15000c
    r'\bTASKalfa Pro \d+c\b',   # Duplicate pattern kept for compatibility
]

# Add QA tracking number patterns here if needed, e.g. r'\bQA-\d+\b'
QA_NUMBER_PATTERNS = []
