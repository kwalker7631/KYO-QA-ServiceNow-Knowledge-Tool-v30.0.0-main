# test_custom_patterns.py - Complete test and fix script for custom patterns
import sys
from pathlib import Path
import importlib
import re

def run_custom_patterns_diagnostic():
    """Complete diagnostic and fix routine for custom patterns system."""
    print("🔧 CUSTOM PATTERNS DIAGNOSTIC & FIX TOOL")
    print("=" * 60)
    
    issues_found = []
    fixes_applied = []
    
    # 1. Check if custom_patterns.py exists
    custom_patterns_path = Path("custom_patterns.py")
    print(f"\n1. File Existence Check:")
    print(f"   Path: {custom_patterns_path.absolute()}")
    print(f"   Exists: {custom_patterns_path.exists()}")
    
    if not custom_patterns_path.exists():
        print("   ❌ ISSUE: custom_patterns.py does not exist")
        issues_found.append("Missing custom_patterns.py file")
        
        # Create default file
        default_content = '''# custom_patterns.py
# This file stores user-defined regex patterns.

MODEL_PATTERNS = [
    # Add your custom model patterns here
    # Example: r'\\bFS-\\d+DN\\b',
]

QA_NUMBER_PATTERNS = [
    # Add your custom QA number patterns here  
    # Example: r'\\bQA-\\d+\\b',
]
'''
        try:
            custom_patterns_path.write_text(default_content, encoding='utf-8')
            print("   ✅ FIX: Created default custom_patterns.py")
            fixes_applied.append("Created default custom_patterns.py")
        except Exception as e:
            print(f"   ❌ FAILED to create file: {e}")
            return False
    
    # 2. Check file content and format
    print(f"\n2. File Content Check:")
    try:
        content = custom_patterns_path.read_text(encoding='utf-8')
        print(f"   Size: {len(content)} characters")
        
        # Check for required sections
        if "MODEL_PATTERNS = [" not in content:
            print("   ❌ ISSUE: Missing MODEL_PATTERNS section")
            issues_found.append("Missing MODEL_PATTERNS section")
        else:
            print("   ✅ MODEL_PATTERNS section found")
            
        if "QA_NUMBER_PATTERNS = [" not in content:
            print("   ❌ ISSUE: Missing QA_NUMBER_PATTERNS section")  
            issues_found.append("Missing QA_NUMBER_PATTERNS section")
        else:
            print("   ✅ QA_NUMBER_PATTERNS section found")
            
        # Show preview
        lines = content.split('\n')
        print(f"   Content preview (first 5 lines):")
        for i, line in enumerate(lines[:5]):
            print(f"     {i+1}: {line}")
            
    except Exception as e:
        print(f"   ❌ ISSUE: Could not read file: {e}")
        issues_found.append(f"File read error: {e}")
        return False
    
    # 3. Test importing the module
    print(f"\n3. Import Test:")
    try:
        # Clear from cache to force fresh import
        if 'custom_patterns' in sys.modules:
            del sys.modules['custom_patterns']
            print("   Cleared module from cache")
        
        # Try importing
        import custom_patterns as custom_module
        print("   ✅ Import successful")
        
        # Check attributes
        for attr_name in ["MODEL_PATTERNS", "QA_NUMBER_PATTERNS"]:
            if hasattr(custom_module, attr_name):
                attr_value = getattr(custom_module, attr_name)
                print(f"   ✅ {attr_name}: {len(attr_value)} patterns")
                
                # Show sample patterns
                if attr_value:
                    print(f"      Sample: {attr_value[0]}")
                else:
                    print(f"      (empty list)")
            else:
                print(f"   ❌ ISSUE: Missing {attr_name} attribute")
                issues_found.append(f"Missing {attr_name} attribute")
                
    except SyntaxError as e:
        print(f"   ❌ ISSUE: Syntax error in file: {e}")
        issues_found.append(f"Syntax error: {e}")
        
        # Try to fix common syntax issues
        print(f"   🔧 Attempting to fix syntax issues...")
        try:
            content = custom_patterns_path.read_text(encoding='utf-8')
            
            # Fix common issues
            fixed_content = content
            
            # Fix unescaped backslashes in regex patterns
            import re as regex_module
            pattern_matches = regex_module.findall(r"r'([^']*)'", content)
            for match in pattern_matches:
                if '\\' in match and '\\\\' not in match:
                    # Need to escape backslashes
                    fixed_match = match.replace('\\', '\\\\')
                    fixed_content = fixed_content.replace(f"r'{match}'", f"r'{fixed_match}'")
            
            if fixed_content != content:
                # Backup original
                backup_path = custom_patterns_path.with_suffix('.py.backup')
                backup_path.write_text(content, encoding='utf-8')
                
                # Write fixed content
                custom_patterns_path.write_text(fixed_content, encoding='utf-8')
                print(f"   ✅ FIX: Fixed syntax issues (backup saved to {backup_path})")
                fixes_applied.append("Fixed syntax issues")
                
                # Test import again
                if 'custom_patterns' in sys.modules:
                    del sys.modules['custom_patterns']
                import custom_patterns as custom_module
                print("   ✅ Import successful after fix")
            
        except Exception as fix_e:
            print(f"   ❌ Could not fix syntax: {fix_e}")
            
    except ImportError as e:
        print(f"   ❌ ISSUE: Import error: {e}")
        issues_found.append(f"Import error: {e}")
    except Exception as e:
        print(f"   ❌ ISSUE: Unexpected error: {e}")
        issues_found.append(f"Unexpected error: {e}")
    
    # 4. Test pattern combination function
    print(f"\n4. Pattern Combination Test:")
    try:
        from data_harvesters import get_combined_patterns
        from config import MODEL_PATTERNS as DEFAULT_MODEL_PATTERNS
        
        combined = get_combined_patterns("MODEL_PATTERNS", DEFAULT_MODEL_PATTERNS)
        print(f"   ✅ Pattern combination successful")
        print(f"   Default patterns: {len(DEFAULT_MODEL_PATTERNS)}")
        print(f"   Combined patterns: {len(combined)}")
        custom_count = len(combined) - len(DEFAULT_MODEL_PATTERNS)
        print(f"   Custom patterns added: {custom_count}")
        
        if custom_count == 0:
            print("   ⚠️ WARNING: No custom patterns are being loaded")
            issues_found.append("No custom patterns loaded")
        
    except Exception as e:
        print(f"   ❌ ISSUE: Pattern combination failed: {e}")
        issues_found.append(f"Pattern combination error: {e}")
    
    # 5. Test actual pattern matching
    print(f"\n5. Pattern Matching Test:")
    test_text = """
    Test document with various models:
    TASKalfa 8000i
    ECOSYS P3055dn  
    PF-740
    FS-C8025DN
    KM-C2520
    QA-12345
    SB-67890
    Custom-123
    """
    
    try:
        from data_harvesters import harvest_all_data
        result = harvest_all_data(test_text, "test_file.pdf")
        print(f"   ✅ Pattern matching test completed")
        print(f"   Found models: {result.get('models', 'None')}")
        
        if result.get('models') == 'Not Found':
            print("   ⚠️ WARNING: No models found with current patterns")
            issues_found.append("No models found in test")
        
    except Exception as e:
        print(f"   ❌ ISSUE: Pattern matching failed: {e}")
        issues_found.append(f"Pattern matching error: {e}")
    
    # 6. Summary and recommendations
    print(f"\n" + "=" * 60)
    print(f"DIAGNOSTIC SUMMARY")
    print(f"=" * 60)
    
    if not issues_found:
        print("✅ No issues found! Custom patterns system is working correctly.")
    else:
        print(f"❌ Found {len(issues_found)} issues:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
    
    if fixes_applied:
        print(f"\n🔧 Applied {len(fixes_applied)} fixes:")
        for i, fix in enumerate(fixes_applied, 1):
            print(f"   {i}. {fix}")
    
    print(f"\n📋 RECOMMENDATIONS:")
    
    if "Missing custom_patterns.py file" in issues_found and "Created default custom_patterns.py" in fixes_applied:
        print("   1. ✅ Custom patterns file created. You can now add patterns through the UI.")
    
    if any("syntax" in issue.lower() for issue in issues_found):
        print("   2. ⚠️ Check custom_patterns.py for syntax errors")
        print("      - Make sure regex patterns are properly formatted")
        print("      - Use r'pattern' format for raw strings")
        print("      - Escape backslashes properly (\\\\d instead of \\d)")
    
    if "No custom patterns loaded" in issues_found:
        print("   3. 📝 Add some custom patterns:")
        print("      - Open the Pattern Manager in the UI")
        print("      - Add patterns like: r'\\bFS-\\d+DN\\b'")
        print("      - Save the patterns")
    
    if "No models found in test" in issues_found:
        print("   4. 🔍 Check your patterns:")
        print("      - Test patterns in the Pattern Manager")
        print("      - Make sure patterns match your document formats")
    
    print(f"\n🎯 NEXT STEPS:")
    print("   1. Run your application")
    print("   2. Open the Pattern Manager (Patterns button)")
    print("   3. Add or edit custom patterns") 
    print("   4. Test patterns against sample text")
    print("   5. Save patterns and re-run processing")
    
    return len(issues_found) == 0

def create_sample_patterns():
    """Create some sample patterns for testing."""
    print(f"\n🎯 Creating sample patterns for testing...")
    
    sample_patterns = {
        "MODEL_PATTERNS": [
            r'\bFS-\d+DN\b',
            r'\bKM-\d+\b', 
            r'\bKM-C\d+\b',
            r'\bKM-C\d+E\b',
            r'\bEP\ C\d+DN\b',
            r'\bFS-C\d+DN\b',
            r'\bKM-\d+w\b',
        ],
        "QA_NUMBER_PATTERNS": [
            r'\bQA-\d+\b',
            r'\bSB-\d+\b',
        ]
    }
    
    custom_patterns_path = Path("custom_patterns.py")
    
    # Build file content
    content_lines = [
        "# custom_patterns.py",
        "# This file stores user-defined regex patterns.",
        ""
    ]
    
    for pattern_type, patterns in sample_patterns.items():
        content_lines.append(f"{pattern_type} = [")
        for pattern in patterns:
            # Escape backslashes for file storage
            safe_pattern = pattern.replace("\\", "\\\\")
            content_lines.append(f"    r'{safe_pattern}',")
        content_lines.append("]")
        content_lines.append("")
    
    try:
        content = "\n".join(content_lines)
        custom_patterns_path.write_text(content, encoding='utf-8')
        print(f"   ✅ Created sample patterns file with {len(sample_patterns['MODEL_PATTERNS'])} model patterns")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create sample patterns: {e}")
        return False

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Run diagnostic and fix issues")
    print("2. Create sample patterns for testing")
    print("3. Both")
    
    choice = input("\nEnter choice (1, 2, or 3): ").strip()
    
    if choice in ["1", "3"]:
        success = run_custom_patterns_diagnostic()
        
    if choice in ["2", "3"]:
        if input(f"\nCreate sample patterns? (y/n): ").lower().startswith('y'):
            create_sample_patterns()
    
    input(f"\nPress Enter to exit...")
