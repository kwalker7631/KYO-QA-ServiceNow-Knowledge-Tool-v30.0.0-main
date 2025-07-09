# data_harvesters.py - Enhanced model detection and custom patterns
# Updated: 2024-07-08 - Added fallback patterns and better comma-separated list handling
import re
import importlib
import sys
from pathlib import Path
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
        default_content = '''# custom_patterns.py
# This file stores user-defined regex patterns.

MODEL_PATTERNS = [
    # Common additional patterns for better coverage
    r'\\bFS-\\d+[A-Z]*\\b',          # FS-1135MFP, FS-C5250DN
    r'\\bKM-\\d+[A-Z]*\\b',          # KM-2560, KM-C2520
    r'\\bECOSYS\\s+[A-Z]+\\d+[a-z]*\\b',  # ECOSYS P3055dn, ECOSYS MA2100cfx
    r'\\bTASKalfa\\s+\\d+[a-z]*\\b', # TASKalfa 8000i, TASKalfa 3212i
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
            print(f"✅ Created enhanced custom_patterns.py with better default patterns")
        except Exception as e:
            print(f"❌ Failed to create custom_patterns.py: {e}")
            return False
    return True

def get_combined_patterns(pattern_name: str, default_patterns: list) -> list:
    """Enhanced pattern loading with better error handling and fallbacks."""
    custom_patterns = []
    
    # Ensure the custom patterns file exists
    if not ensure_custom_patterns_file():
        print(f"⚠️ Using only default patterns for {pattern_name}")
        return default_patterns
    
    try:
        # Remove from sys.modules if already loaded to force fresh reload
        if 'custom_patterns' in sys.modules:
            del sys.modules['custom_patterns']
        
        # Import the custom patterns module
        custom_mod = importlib.import_module("custom_patterns")
        
        # Get the specific pattern list
        custom_patterns = getattr(custom_mod, pattern_name, [])
        
        print(f"✅ Loaded {len(custom_patterns)} custom {pattern_name}")
            
    except ImportError as e:
        print(f"⚠️ Could not import custom_patterns.py: {e}")
    except SyntaxError as e:
        print(f"❌ Syntax error in custom_patterns.py: {e}")
        print(f"   Please check the file format and fix any syntax issues")
    except AttributeError as e:
        print(f"⚠️ Attribute error in custom_patterns.py: {e}")
        print(f"   Make sure {pattern_name} is defined in the file")
    except Exception as e:
        print(f"❌ Unexpected error loading custom patterns: {e}")
    
    # Combine patterns: custom patterns first, then default patterns not already in custom
    combined_patterns = []
    
    # Add custom patterns
    for pattern in custom_patterns:
        if pattern and pattern not in combined_patterns:
            combined_patterns.append(pattern)
    
    # Add default patterns that aren't already included
    for pattern in default_patterns:
        if pattern and pattern not in combined_patterns:
            combined_patterns.append(pattern)
    
    total_custom = len(custom_patterns)
    total_default = len(default_patterns)
    total_combined = len(combined_patterns)
    
    print(f"📊 Pattern summary for {pattern_name}: {total_custom} custom + {total_default} default = {total_combined} total")
    
    return combined_patterns

def is_excluded(text: str) -> bool:
    """Checks if a string contains any of the unwanted exclusion patterns."""
    return any(p.lower() in text.lower() for p in EXCLUSION_PATTERNS)

def clean_model_string(model_str: str) -> str:
    """Applies standardization rules to a found model string."""
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', model_str.strip())
    
    # Apply standardization rules
    for rule, replacement in STANDARDIZATION_RULES.items():
        cleaned = cleaned.replace(rule, replacement)
    
    return cleaned

def extract_models_with_fallback_patterns(text: str, filename: str) -> set:
    """Enhanced model extraction with fallback patterns for better coverage."""
    models = set()
    
    # Primary patterns from configuration
    patterns = get_combined_patterns("MODEL_PATTERNS", DEFAULT_MODEL_PATTERNS)
    
    # Search in both text content and filename
    search_contents = [text, filename.replace("_", " ")]
    
    for content in search_contents:
        if not content:
            continue
            
        for pattern in patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Handle both string matches and tuple matches (from groups)
                    if isinstance(match, tuple):
                        match = match[0] if match else ""
                    
                    if match and not is_excluded(match):
                        cleaned_match = clean_model_string(match)
                        if cleaned_match:
                            models.add(cleaned_match)
                            
            except re.error as e:
                print(f"❌ Invalid regex pattern '{pattern}': {e}")
                continue
            except Exception as e:
                print(f"❌ Error processing pattern '{pattern}': {e}")
                continue
    
    # FALLBACK: If no models found with configured patterns, try aggressive fallback patterns
    if not models:
        print(f"🔍 No models found with configured patterns, trying fallback patterns...")
        models.update(extract_with_fallback_patterns(text, filename))
    
    return models

def extract_with_fallback_patterns(text: str, filename: str) -> set:
    """Fallback patterns for when primary patterns fail - handles comma-separated lists."""
    models = set()
    
    # Aggressive fallback patterns designed to catch common formats
    fallback_patterns = [
        # Basic word-number combinations
        r'\b[A-Z]{2,}[-\s]+[A-Z0-9]{2,}\b',           # FS-1135MFP, ECOSYS P3055dn
        r'\b[A-Z]{2,}[A-Z0-9]*\d+[a-z]*\b',          # TASKalfa8000i, KM2560
        r'\b[A-Z]{2,}\s+[A-Z0-9]+[a-z]*\b',          # ECOSYS P3055dn, TASKalfa 8000i
        
        # Known manufacturer prefixes (case insensitive)
        r'(?i)\bFS[-\s]*[A-Z0-9]+[a-z]*\b',          # FS-1135MFP, fs-c5250dn
        r'(?i)\bKM[-\s]*[A-Z0-9]+[a-z]*\b',          # KM-2560, km-c2520
        r'(?i)\bTASKalfa\s*[A-Z0-9]+[a-z]*\b',       # TASKalfa 8000i, taskalfa 3212i
        r'(?i)\bECOSYS\s*[A-Z0-9]+[a-z]*\b',         # ECOSYS P3055dn, ecosys ma2100cfx
        r'(?i)\bPF[-\s]*\d+\b',                      # PF-740, pf-770
        r'(?i)\bDF[-\s]*\d+\b',                      # DF-780
        r'(?i)\bMK[-\s]*\d+\b',                      # MK-726
        
        # Generic patterns for comma-separated lists
        r'\b[A-Z]{2,}[A-Z0-9\-\s]+[A-Z0-9][a-z]*(?=\s*,|\s*$|\s*\))',  # Items in comma-separated lists
    ]
    
    search_contents = [text, filename.replace("_", " ")]
    
    for content in search_contents:
        if not content:
            continue
            
        for pattern in fallback_patterns:
            try:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match else ""
                    
                    # Additional filtering for fallback matches
                    if (match and 
                        len(match.strip()) >= 3 and  # Minimum length
                        not is_excluded(match) and
                        re.search(r'\d', match)):     # Must contain at least one digit
                        
                        cleaned_match = clean_model_string(match)
                        if cleaned_match:
                            models.add(cleaned_match)
                            print(f"  🎯 Fallback found: {cleaned_match}")
                            
            except re.error as e:
                print(f"❌ Invalid fallback pattern '{pattern}': {e}")
                continue
            except Exception as e:
                print(f"❌ Error processing fallback pattern '{pattern}': {e}")
                continue
    
    return models

def harvest_models(text: str, filename: str) -> list:
    """Enhanced model harvesting with better debugging and fallback patterns."""
    print(f"\n🔍 Harvesting models from: {filename}")
    print(f"   Text length: {len(text)} characters")
    
    # Extract models using enhanced method
    models = extract_models_with_fallback_patterns(text, filename)
    
    # Convert to sorted list
    found_models = sorted(list(models))
    
    if found_models:
        print(f"✅ Found {len(found_models)} models: {', '.join(found_models)}")
    else:
        print(f"❌ No models found")
        # Show a sample of the text for debugging
        text_sample = text[:200].replace('\n', ' ').strip()
        print(f"   Text sample: {text_sample}...")
    
    return found_models

def harvest_qa_numbers(text: str, filename: str) -> list:
    """Finds all unique QA numbers from text and filename."""
    qa_numbers = set()
    
    # Get combined patterns (custom + default)
    patterns = get_combined_patterns("QA_NUMBER_PATTERNS", DEFAULT_QA_PATTERNS)
    
    if not patterns:
        return []
    
    # Search in both text content and filename
    search_contents = [text, filename.replace("_", " ")]
    
    for content in search_contents:
        if not content:
            continue
            
        for pattern in patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Handle both string matches and tuple matches (from groups)
                    if isinstance(match, tuple):
                        match = match[0] if match else ""
                    
                    if match and not is_excluded(match):
                        qa_numbers.add(match.strip())
                        
            except re.error as e:
                print(f"❌ Invalid regex pattern '{pattern}': {e}")
                continue
            except Exception as e:
                print(f"❌ Error processing QA pattern '{pattern}': {e}")
                continue
    
    return sorted(list(qa_numbers))

def harvest_author(text: str) -> str:
    """Finds the author and returns an empty string if it's an unwanted name."""
    # Search for a line that looks like "Author: John Doe"
    match = re.search(r"^Author:\s*(.*)", text, re.MULTILINE | re.IGNORECASE)
    if match:
        author = match.group(1).strip()
        # Ensure the found author is not in the unwanted list
        if author and author not in UNWANTED_AUTHORS:
            return author
    return ""  # Return empty string if no author is found or if it's unwanted

def harvest_all_data(text: str, filename: str) -> dict:
    """Enhanced main harvester function with better debugging and error handling."""
    print(f"\n🔍 Starting data harvest for: {filename}")
    print(f"   Text length: {len(text)} characters")
    
    # Harvest models with enhanced detection
    models_list = harvest_models(text, filename)
    models_str = ", ".join(models_list) if models_list else "Not Found"
    
    # Harvest QA numbers (optional)
    qa_numbers = harvest_qa_numbers(text, filename)
    qa_str = ", ".join(qa_numbers) if qa_numbers else ""
    
    # Harvest author
    author_str = harvest_author(text)
    
    result = {
        "models": models_str,
        "author": author_str,
        "qa_numbers": qa_str  # Optional field
    }
    
    print(f"📋 Harvest results:")
    print(f"   Models: {result['models']}")
    print(f"   Author: {result['author'] or 'Not Found'}")
    if qa_str:
        print(f"   QA Numbers: {qa_str}")
    
    return result

def test_patterns():
    """Test function to verify pattern loading and matching."""
    print("🧪 Testing enhanced patterns system...")
    
    # Test text with various model formats including comma-separated lists
    test_text = """
    Document contains the following equipment:
    TASKalfa 8000i printer
    ECOSYS P3055dn device  
    FS-C8025DN, KM-2560, KM-C2520
    PF-740 paper feeder
    Additional models: FS-1135MFP, TASKalfa 3212i, ECOSYS MA2100cfx
    Compatible with: FS-1120D, FS-1320D, FS-1370DN, ECOSYS P2040dn, ECOSYS P2040dw, 
    TASKalfa 3212i, TASKalfa 4012i, TASKalfa 5012i, KM-2810, KM-2820
    QA-12345 test case
    SB-67890 service bulletin
    """
    
    print(f"\nTest text:\n{test_text}")
    
    # Test harvesting
    result = harvest_all_data(test_text, "test_document.pdf")
    
    print(f"\n🏁 Test complete!")
    return result

if __name__ == "__main__":
    # Run tests when script is executed directly
    test_patterns()
