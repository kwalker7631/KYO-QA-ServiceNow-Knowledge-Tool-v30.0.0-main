# debug_data_harvesting.py - Debug why models aren't being found
import re
from pathlib import Path

def test_sample_text():
    """Test with sample text that should contain models."""
    
    # Sample text with common model formats
    sample_texts = [
        # Format 1: Space-separated
        """
        Equipment models: TASKalfa 8000i, ECOSYS P3055dn, FS-C8025DN
        Additional models: KM-C2520, PF-740, MK-726
        """,
        
        # Format 2: Comma-separated list
        """
        Models: FS-1135MFP, KM-1820, TASKalfa 3010i, ECOSYS M3040dn, PF-770, DF-780
        """,
        
        # Format 3: Mixed with other text
        """
        This service bulletin covers the following printer models:
        - TASKalfa 6052ci
        - ECOSYS P4040dn  
        - FS-C5250DN
        - KM-2560, KM-3060, KM-4060
        - Paper feed unit PF-760
        """,
        
        # Format 4: User's specific issue - comma separated
        """
        Compatible with: FS-1120D, FS-1320D, FS-1370DN, ECOSYS P2040dn, ECOSYS P2040dw, 
        TASKalfa 3212i, TASKalfa 4012i, TASKalfa 5012i, KM-2810, KM-2820
        """,
        
        # Format 5: Technical document format
        """
        QA-12345: Service Information
        Models affected: ECOSYS MA2100cfx, ECOSYS MA2100cwfx, TASKalfa 3253ci
        Paper feeder: PF-740 (optional)
        Developer: DV-1150, DV-1160
        """
    ]
    
    print("🔍 TESTING DATA HARVESTING WITH SAMPLE TEXTS")
    print("=" * 60)
    
    # Test each sample
    for i, sample_text in enumerate(sample_texts, 1):
        print(f"\n--- Test {i} ---")
        print(f"Text: {sample_text.strip()[:100]}...")
        
        try:
            from data_harvesters import harvest_all_data
            result = harvest_all_data(sample_text, f"test_sample_{i}.pdf")
            
            print(f"Result: {result.get('models', 'ERROR')}")
            
            if result.get('models') == 'Not Found':
                print(f"❌ FAILED to find models in sample {i}")
                debug_patterns_on_text(sample_text, f"Sample {i}")
            else:
                print(f"✅ SUCCESS: Found models in sample {i}")
                
        except Exception as e:
            print(f"❌ ERROR in sample {i}: {e}")
            import traceback
            traceback.print_exc()

def debug_patterns_on_text(text, label):
    """Debug why patterns aren't matching specific text."""
    print(f"\n🔍 DEBUGGING PATTERNS FOR {label}")
    print("-" * 40)
    
    # Test with default patterns first
    try:
        from config import MODEL_PATTERNS as DEFAULT_MODEL_PATTERNS
        print(f"Testing {len(DEFAULT_MODEL_PATTERNS)} default patterns...")
        
        found_with_defaults = []
        for i, pattern in enumerate(DEFAULT_MODEL_PATTERNS):
            try:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    found_with_defaults.extend(matches)
                    print(f"  ✅ Pattern {i+1}: {pattern} -> Found: {matches}")
                else:
                    print(f"  ❌ Pattern {i+1}: {pattern} -> No matches")
            except re.error as e:
                print(f"  💥 Pattern {i+1}: {pattern} -> INVALID: {e}")
        
        if found_with_defaults:
            print(f"📊 Default patterns found: {found_with_defaults}")
        else:
            print(f"❌ NO MATCHES with default patterns")
            
    except Exception as e:
        print(f"❌ Error testing default patterns: {e}")
    
    # Test with custom patterns
    try:
        from data_harvesters import get_combined_patterns
        combined_patterns = get_combined_patterns("MODEL_PATTERNS", DEFAULT_MODEL_PATTERNS)
        print(f"\nTesting {len(combined_patterns)} combined patterns...")
        
        found_with_combined = []
        for i, pattern in enumerate(combined_patterns):
            try:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    found_with_combined.extend(matches)
                    print(f"  ✅ Combined {i+1}: {pattern} -> Found: {matches}")
            except re.error as e:
                print(f"  💥 Combined {i+1}: {pattern} -> INVALID: {e}")
        
        if found_with_combined:
            print(f"📊 Combined patterns found: {found_with_combined}")
        else:
            print(f"❌ NO MATCHES with combined patterns")
            
    except Exception as e:
        print(f"❌ Error testing combined patterns: {e}")
    
    # Suggest new patterns based on the text
    suggest_patterns_for_text(text, label)

def suggest_patterns_for_text(text, label):
    """Analyze text and suggest patterns that might work."""
    print(f"\n💡 PATTERN SUGGESTIONS FOR {label}")
    print("-" * 40)
    
    # Look for potential model patterns
    potential_models = []
    
    # Pattern 1: Word-number combinations
    word_number_matches = re.findall(r'\b[A-Z]{2,8}[-\s]*[A-Z0-9]{2,8}[a-z]*\b', text, re.IGNORECASE)
    if word_number_matches:
        potential_models.extend(word_number_matches)
        print(f"Found word-number patterns: {word_number_matches}")
    
    # Pattern 2: All caps words with numbers
    caps_number_matches = re.findall(r'\b[A-Z]{2,}[A-Z0-9]*\d+[A-Za-z]*\b', text)
    if caps_number_matches:
        potential_models.extend(caps_number_matches)
        print(f"Found caps-number patterns: {caps_number_matches}")
    
    # Pattern 3: Specific known prefixes
    known_prefixes = ['FS-', 'KM-', 'TASKalfa', 'ECOSYS', 'PF-', 'DF-', 'MK-', 'DV-']
    for prefix in known_prefixes:
        prefix_matches = re.findall(f'{re.escape(prefix)}[A-Z0-9]+[a-z]*', text, re.IGNORECASE)
        if prefix_matches:
            potential_models.extend(prefix_matches)
            print(f"Found {prefix} patterns: {prefix_matches}")
    
    # Remove duplicates and suggest patterns
    unique_models = list(set(potential_models))
    if unique_models:
        print(f"\n🎯 Suggested new patterns to add:")
        for model in unique_models[:5]:  # Show first 5
            # Create a pattern for this specific model format
            escaped = re.escape(model)
            # Replace digits with \d+ for generalization
            pattern = re.sub(r'\\?\d+', r'\\d+', escaped)
            print(f"   r'\\b{pattern}\\b'  # For models like: {model}")
    else:
        print(f"❌ Could not identify potential model patterns in text")

def test_real_failure_case():
    """Test with a user-provided failure case."""
    print(f"\n🎯 TESTING USER'S SPECIFIC FAILURE CASE")
    print("=" * 50)
    
    # Ask user to paste some text from a failed document
    print("Please paste a sample of text from a document that failed:")
    print("(Or press Enter to skip)")
    
    try:
        user_text = input().strip()
        if user_text:
            print(f"\n🔍 Analyzing your text...")
            debug_patterns_on_text(user_text, "User's Failed Document")
        else:
            print("Skipped user input test")
    except KeyboardInterrupt:
        print("\nSkipped user input test")

def check_exclusion_issues():
    """Check if exclusion patterns are too aggressive."""
    print(f"\n🚫 CHECKING EXCLUSION PATTERNS")
    print("=" * 40)
    
    try:
        from config import EXCLUSION_PATTERNS
        from data_harvesters import is_excluded
        
        print(f"Current exclusion patterns: {EXCLUSION_PATTERNS}")
        
        # Test if exclusions are blocking valid models
        test_models = [
            "TASKalfa 8000i", "ECOSYS P3055dn", "FS-C8025DN", 
            "KM-C2520", "PF-740", "CVE-2023-1234", "CWE-79", "TK-1150"
        ]
        
        for model in test_models:
            excluded = is_excluded(model)
            status = "❌ EXCLUDED" if excluded else "✅ ALLOWED"
            print(f"  {status}: {model}")
            
    except Exception as e:
        print(f"❌ Error checking exclusions: {e}")

if __name__ == "__main__":
    print("🐛 DATA HARVESTING DEBUGGER")
    print("This will help identify why models aren't being found")
    print("=" * 60)
    
    # Run all tests
    test_sample_text()
    check_exclusion_issues()
    test_real_failure_case()
    
    print(f"\n📋 SUMMARY & NEXT STEPS:")
    print("1. Check the test results above")
    print("2. If patterns aren't matching, add suggested patterns to custom_patterns.py")
    print("3. If exclusions are blocking models, check EXCLUSION_PATTERNS in config.py")
    print("4. If all tests pass but real documents fail, the issue is in OCR text extraction")
    
    input(f"\nPress Enter to exit...")
