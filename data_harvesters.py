# data_harvesters.py - Enhanced model detection with post-processing filter and forced pattern reloading
# Updated: 2024-07-09 - FIX: Corrected regex syntax in the default pattern file creation.
import re
import importlib
import sys
from pathlib import Path

# Import the custom_patterns module here so we can reload it
import custom_patterns
from config import (
    MODEL_PATTERNS as DEFAULT_MODEL_PATTERNS,
    QA_NUMBER_PATTERNS as DEFAULT_QA_PATTERNS,
    EXCLUSION_PATTERNS,
    UNWANTED_AUTHORS,
    STANDARDIZATION_RULES,
)

def ensure_custom_patterns_file():
    """Ensure custom_patterns.py exists with proper structure."""
    custom_patterns_path = Path("custom_patterns.py")
    
    if not custom_patterns_path.exists():
        # FIX: Corrected the regex syntax from \\b to \b in the default content.
        default_content = '''# custom_patterns.py
# This file stores user-defined regex patterns.

MODEL_PATTERNS = [
    # Common additional patterns for better coverage
    r'\\bFS-\\d+[A-Z]*\\b',          # FS-1135MFP, FS-C5250DN
    r'\\bKM-\\d+[A-Z]*\\b',          # KM-2560, KM-C2520
    r'\\bECOSYS\\s+[A-Z]+\\d+[a-z]*\\b',  # ECOSYS P3055dn, ECOSYS MA2100cfx
    r'\\bTASKalfa\\s+\\d+[a-z]*i?\\b', # TASKalfa 8000i, TASKalfa 3212i
    r'\\bPF-\\d+\\b',                # PF-740, PF-770
    r'\\bDF-\\d+\\b',                # DF-780
    r'\\bMK-\\d+\\b',                # MK-726
    r'\\bDV-\\d+\\b',                # DV-1150, DV-1160
]

QA_NUMBER_PATTERNS = [
    r'\\bQA-\\d+\\b',                # QA-12345
    r'\\bSB-\\d+\\b',                # SB-67890
]
'''
        try:
            custom_patterns_path.write_text(default_content, encoding='utf-8')
            print(f"✅ Created enhanced custom_patterns.py with correct default patterns")
        except Exception as e:
            print(f"❌ Failed to create custom_patterns.py: {e}")
            return False
    return True

def get_combined_patterns(pattern_name: str, default_patterns: list) -> list:
    """
    Loads patterns from custom_patterns.py, forcing a reload to get the latest changes.
    """
    custom_patterns_list = []
    
    if not ensure_custom_patterns_file():
        print(f"⚠️ Using only default patterns for {pattern_name}")
        return default_patterns
    
    try:
        # Force a reload of the custom_patterns module to ensure the latest
        # patterns from the file are used, especially during re-runs.
        importlib.reload(custom_patterns)
        
        custom_patterns_list = getattr(custom_patterns, pattern_name, [])
        print(f"✅ Reloaded and loaded {len(custom_patterns_list)} custom {pattern_name}")
            
    except Exception as e:
        print(f"❌ Unexpected error reloading custom patterns: {e}")
    
    # Combine patterns: custom patterns first, then default patterns not already in custom
    combined_patterns = []
    for pattern in custom_patterns_list:
        if pattern and pattern not in combined_patterns:
            combined_patterns.append(pattern)
    
    for pattern in default_patterns:
        if pattern and pattern not in combined_patterns:
            combined_patterns.append(pattern)
    
    print(f"📊 Pattern summary for {pattern_name}: {len(custom_patterns_list)} custom + {len(default_patterns)} default = {len(combined_patterns)} total")
    return combined_patterns

def is_excluded(text: str) -> bool:
    """Checks if a string contains any of the unwanted exclusion patterns."""
    return any(p.lower() in text.lower() for p in EXCLUSION_PATTERNS)

def clean_model_string(model_str: str) -> str:
    """Applies standardization rules to a found model string."""
    cleaned = re.sub(r'\s+', ' ', model_str.strip())
    for rule, replacement in STANDARDIZATION_RULES.items():
        cleaned = cleaned.replace(rule, replacement)
    return cleaned

def extract_models_with_fallback_patterns(text: str, filename: str) -> set:
    """Enhanced model extraction with fallback patterns for better coverage."""
    models = set()
    patterns = get_combined_patterns("MODEL_PATTERNS", DEFAULT_MODEL_PATTERNS)
    search_contents = [text, filename.replace("_", " ")]
    
    for content in search_contents:
        if not content:
            continue
        for pattern in patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match else ""
                    if match and not is_excluded(match):
                        cleaned_match = clean_model_string(match)
                        if cleaned_match:
                            models.add(cleaned_match)
            except re.error as e:
                print(f"❌ Invalid regex pattern '{pattern}': {e}")
                continue
    
    if not models:
        # This fallback logic is intentionally left out of the main fix for now
        # to ensure that files correctly go to review if primary patterns fail.
        pass
    
    return models

def harvest_models(text: str, filename: str) -> list:
    """
    Enhanced model harvesting with a post-processing filter to remove invalid results.
    """
    print(f"\n🔍 Harvesting models from: {filename}")
    
    all_found_models = extract_models_with_fallback_patterns(text, filename)
    
    final_models = set()
    for model in all_found_models:
        model_stripped = model.strip()
        
        if len(model_stripped) <= 2:
            print(f"   - Filtering out short model: '{model_stripped}'")
            continue

        has_digit = any(char.isdigit() for char in model_stripped)
        has_hyphen = '-' in model_stripped

        if not has_digit and not has_hyphen:
            print(f"   - Filtering out model with no digits or hyphen: '{model_stripped}'")
            continue
        
        final_models.add(model_stripped)

    found_models = sorted(list(final_models))
    
    if found_models:
        print(f"✅ Found {len(found_models)} valid models: {', '.join(found_models)}")
    else:
        print(f"❌ No valid models found after filtering.")
        text_sample = text[:200].replace('\n', ' ').strip()
        print(f"   Text sample: {text_sample}...")
    
    return found_models

def harvest_qa_numbers(text: str, filename: str) -> list:
    """Finds all unique QA numbers from text and filename."""
    qa_numbers = set()
    patterns = get_combined_patterns("QA_NUMBER_PATTERNS", DEFAULT_QA_PATTERNS)
    
    if not patterns:
        return []
    
    search_contents = [text, filename.replace("_", " ")]
    for content in search_contents:
        if not content:
            continue
        for pattern in patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match else ""
                    if match and not is_excluded(match):
                        qa_numbers.add(match.strip())
            except re.error as e:
                print(f"❌ Invalid regex pattern '{pattern}': {e}")
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
    """Main harvester function that orchestrates the data extraction and filtering."""
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
    
    print(f"📋 Final Harvest results:")
    print(f"   Models: {result['models']}")
    print(f"   Author: {result['author'] or 'Not Found'}")
    if qa_str:
        print(f"   QA Numbers: {qa_str}")
    
    return result

if __name__ == "__main__":
    test_text = """
    Document contains the following equipment:
    TASKalfa 8000i printer, BF, DF, PF-740
    ECOSYS P3055dn device  
    FS-C8025DN, KM-2560, KM-C2520, and also DP.
    """
    print("🧪 Testing enhanced harvesting with filtering...")
    harvest_all_data(test_text, "test_document.pdf")
