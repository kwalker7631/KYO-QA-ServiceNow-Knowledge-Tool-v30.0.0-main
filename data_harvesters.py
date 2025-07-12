# data_harvesters.py - Enhanced model detection with more robust patterns and smarter filtering.
# This version is designed to fix the model extraction failures.

import re
import importlib
from pathlib import Path

# Import the custom_patterns module so we can reload it
try:
    import custom_patterns
except ImportError:
    # Create a dummy module if it doesn't exist to prevent launch errors
    from types import ModuleType
    custom_patterns = ModuleType("custom_patterns")
    custom_patterns.MODEL_PATTERNS = []
    custom_patterns.QA_NUMBER_PATTERNS = []

from config import (
    MODEL_PATTERNS as DEFAULT_MODEL_PATTERNS,
    QA_NUMBER_PATTERNS as DEFAULT_QA_PATTERNS,
    EXCLUSION_PATTERNS,
    UNWANTED_AUTHORS,
    STANDARDIZATION_RULES,
)

def ensure_custom_patterns_file():
    """Ensures custom_patterns.py exists. If not, creates it with robust defaults."""
    custom_patterns_path = Path("custom_patterns.py")
    if custom_patterns_path.exists():
        return True

    print("🔧 custom_patterns.py not found. Creating with enhanced default patterns.")
    # --- FIX: Added more comprehensive default patterns ---
    default_content = '''# custom_patterns.py
# This file stores user-defined regex patterns for Kyocera models.
# Use raw strings (r'...') for all patterns.

MODEL_PATTERNS = [
    # General TASKalfa and ECOSYS
    r'\\bTASKalfa\\s+\\d+[a-z]*i?\\b',          # e.g., TASKalfa 8000i, TASKalfa 3212i
    r'\\bECOSYS\\s+[A-Z]+\\d+[a-z]*\\b',      # e.g., ECOSYS P3055dn, ECOSYS MA2100cfx

    # FS-Series (including FS-C)
    r'\\bFS-C?\\d+[A-Z]*[a-z]*\\b',         # e.g., FS-C5250DN, FS-1135MFP

    # KM-Series
    r'\\bKM-\\d+[A-Z]*\\b',                  # e.g., KM-2560, KM-C2520

    # Accessories (PF, DF, etc.)
    r'\\b(PF|DF|MK|DV|AK|JS)-\\d+\\w*\\b',   # e.g., PF-740, DF-780, MK-726

    # Newer TASKalfa Pro series
    r'\\bTASKalfa\\s+Pro\\s+\\d+c?\\b',      # e.g., TASKalfa Pro 15000c
]

QA_NUMBER_PATTERNS = [
    r'\\bQA[-_]?\\w+\\b',                     # e.g., QA-12345, QA_I168
    r'\\bSB[-_]?\\w+\\b',                     # e.g., SB-67890
]
'''
    try:
        custom_patterns_path.write_text(default_content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"❌ Failed to create custom_patterns.py: {e}")
        return False

def get_combined_patterns(pattern_name: str, default_patterns: list) -> list:
    """Loads patterns from custom_patterns.py, forcing a reload to get the latest changes."""
    custom_patterns_list = []
    
    if not ensure_custom_patterns_file():
        print(f"⚠️ Using only default patterns for {pattern_name}")
        return default_patterns
    
    try:
        importlib.reload(custom_patterns)
        custom_patterns_list = getattr(custom_patterns, pattern_name, [])
        print(f"✅ Reloaded and loaded {len(custom_patterns_list)} custom {pattern_name} patterns.")
    except Exception as e:
        print(f"❌ Unexpected error reloading custom patterns: {e}")
    
    combined = list(dict.fromkeys(custom_patterns_list + default_patterns))
    print(f"📊 Pattern summary for {pattern_name}: {len(combined)} total unique patterns.")
    return combined

def is_excluded(text: str) -> bool:
    """Checks if a string contains any of the unwanted exclusion patterns."""
    return any(p.lower() in text.lower() for p in EXCLUSION_PATTERNS)

def clean_model_string(model_str: str) -> str:
    """Applies standardization rules to a found model string."""
    cleaned = re.sub(r'\s+', ' ', model_str.strip())
    for rule, replacement in STANDARDIZATION_RULES.items():
        cleaned = cleaned.replace(rule, replacement)
    return cleaned

def harvest_models(text: str, filename: str) -> list:
    """Enhanced model harvesting with smarter filtering and more robust patterns."""
    print(f"\n🔍 Harvesting models from: {filename}")
    
    # Use the improved pattern loader
    patterns = get_combined_patterns("MODEL_PATTERNS", DEFAULT_MODEL_PATTERNS)
    
    # Search both the document text and the filename itself
    search_contents = [text, filename.replace("_", " ")]
    
    # --- Stage 1: Find all potential matches ---
    all_found_models = set()
    for content in search_contents:
        if not content: continue
        for pattern in patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Handle cases where regex returns tuples (from capture groups)
                    match_str = match[0] if isinstance(match, tuple) else match
                    if match_str and not is_excluded(match_str):
                        cleaned_match = clean_model_string(match_str)
                        if cleaned_match:
                            all_found_models.add(cleaned_match)
            except re.error as e:
                print(f"❌ Invalid regex pattern skipped: '{pattern}' -> {e}")
                continue

    # --- Stage 2: Apply smarter filtering ---
    final_models = set()
    for model in all_found_models:
        # Rule: Must contain at least one digit
        if not any(char.isdigit() for char in model):
            print(f"   - Filtering out (no digits): '{model}'")
            continue
        
        # Rule: Must be a reasonable length (e.g., more than 3 characters)
        if len(model) <= 3:
            print(f"   - Filtering out (too short): '{model}'")
            continue
            
        final_models.add(model)

    found_models = sorted(list(final_models))
    
    if found_models:
        print(f"✅ Found {len(found_models)} valid models: {', '.join(found_models)}")
    else:
        print("❌ No valid models found after filtering.")
        text_sample = text[:200].replace('\n', ' ').strip()
        print(f"   Text sample: {text_sample}...")
    
    return found_models

def harvest_qa_numbers(text: str, filename: str) -> list:
    """Finds all unique QA/SB numbers from text and filename."""
    qa_numbers = set()
    patterns = get_combined_patterns("QA_NUMBER_PATTERNS", DEFAULT_QA_PATTERNS)
    
    search_contents = [text, filename.replace("_", " ")]
    for content in search_contents:
        if not content: continue
        for pattern in patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if match and not is_excluded(match):
                        qa_numbers.add(match.strip())
            except re.error as e:
                print(f"❌ Invalid QA regex pattern skipped: '{pattern}' -> {e}")
                continue
    
    return sorted(list(qa_numbers))

def harvest_author(text: str) -> str:
    """Finds the author and returns an empty string if it's an unwanted name."""
    match = re.search(r"^Author:\s*(.*)", text, re.MULTILINE | re.IGNORECASE)
    if match:
        author = match.group(1).strip()
        if author and author not in UNWANTED_AUTHORS:
            return author
    return ""

def harvest_all_data(text: str, filename: str) -> dict:
    """Main harvester function that orchestrates the data extraction."""
    models_list = harvest_models(text, filename)
    models_str = ", ".join(models_list) if models_list else "Not Found"
    
    qa_numbers = harvest_qa_numbers(text, filename)
    qa_str = ", ".join(qa_numbers) if qa_numbers else ""
    
    author_str = harvest_author(text)
    
    result = {
        "models": models_str,
        "author": author_str,
        "qa_numbers": qa_str
    }
    
    print("📋 Final Harvest results:")
    print(f"   Models: {result['models']}")
    print(f"   Author: {result['author'] or 'Not Found'}")
    if qa_str:
        print(f"   QA Numbers: {qa_str}")
    
    return result
