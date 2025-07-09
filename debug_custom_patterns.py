# debug_custom_patterns.py - Run this to debug your custom patterns issue
import sys
from pathlib import Path
import importlib
import json

def debug_custom_patterns():
    """Comprehensive debug script for custom patterns."""
    print("🔍 DEBUGGING CUSTOM PATTERNS SYSTEM")
    print("=" * 50)
    
    # Check if custom_patterns.py exists
    custom_patterns_path = Path("custom_patterns.py")
    print(f"\n1. Custom patterns file check:")
    print(f"   Path: {custom_patterns_path.absolute()}")
    print(f"   Exists: {custom_patterns_path.exists()}")
    
    if custom_patterns_path.exists():
        print(f"   Size: {custom_patterns_path.stat().st_size} bytes")
        print(f"   Content preview:")
        try:
            content = custom_patterns_path.read_text(encoding='utf-8')
            print(f"   {content[:200]}...")
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
    else:
        print("   ⚠️ File does not exist - creating default...")
        create_default_custom_patterns()
    
    # Test importing custom_patterns
    print(f"\n2. Import test:")
    try:
        if 'custom_patterns' in sys.modules:
            del sys.modules['custom_patterns']
        
        import custom_patterns as custom_module
        print(f"   ✅ Import successful")
        
        # Check for required attributes
        print(f"\n3. Pattern attributes check:")
        for attr_name in ["MODEL_PATTERNS", "QA_NUMBER_PATTERNS"]:
            if hasattr(custom_module, attr_name):
                attr_value = getattr(custom_module, attr_name)
                print(f"   ✅ {attr_name}: {len(attr_value)} patterns")
                if attr_value:
                    print(f"      First pattern: {attr_value[0]}")
            else:
                print(f"   ❌ Missing {attr_name}")
                
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    
    # Test the get_combined_patterns function
    print(f"\n4. Testing pattern combination:")
    try:
        from data_harvesters import get_combined_patterns
        from config import MODEL_PATTERNS as DEFAULT_MODEL_PATTERNS
        
        combined = get_combined_patterns("MODEL_PATTERNS", DEFAULT_MODEL_PATTERNS)
        print(f"   ✅ Combined patterns: {len(combined)} total")
        print(f"   Default patterns: {len(DEFAULT_MODEL_PATTERNS)}")
        custom_count = len(combined) - len(DEFAULT_MODEL_PATTERNS)
        print(f"   Custom patterns: {custom_count}")
        
        if combined:
            print(f"   Sample patterns:")
            for i, pattern in enumerate(combined[:3]):
                print(f"      {i+1}. {pattern}")
                
    except Exception as e:
        print(f"   ❌ Pattern combination failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test pattern matching
    print(f"\n5. Testing pattern matching:")
    test_text = """
    Sample document with models like:
    TASKalfa 8000i
    ECOSYS P3055dn
    PF-740
    FS-C8025DN
    QA-12345
    SB-67890
    """
    
    try:
        from data_harvesters import harvest_models
        found_models = harvest_models(test_text, "test_file.pdf")
        print(f"   ✅ Pattern matching test:")
        print(f"   Found models: {found_models}")
        
    except Exception as e:
        print(f"   ❌ Pattern matching failed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n6. Recommendations:")
    if not custom_patterns_path.exists():
        print("   📝 Create custom_patterns.py file")
    
    # Check if patterns are being saved correctly
    if custom_patterns_path.exists():
        try:
            content = custom_patterns_path.read_text(encoding='utf-8')
            if "MODEL_PATTERNS = [" not in content:
                print("   📝 File format may be incorrect")
            if len(content.strip()) < 50:
                print("   📝 File seems too small - may be empty or corrupted")
        except:
            pass
    
    print(f"\n✅ Debug complete!")

def create_default_custom_patterns():
    """Create a default custom_patterns.py file."""
    default_content = '''# custom_patterns.py
# This file stores user-defined regex patterns.

MODEL_PATTERNS = [
    # Add your custom model patterns here
    # Example: r'\\bCustom-\\d+\\b',
]

QA_NUMBER_PATTERNS = [
    # Add your custom QA number patterns here  
    # Example: r'\\bQA-\\d+\\b',
]
'''
    try:
        Path("custom_patterns.py").write_text(default_content, encoding='utf-8')
        print("   ✅ Created default custom_patterns.py")
    except Exception as e:
        print(f"   ❌ Failed to create default file: {e}")

if __name__ == "__main__":
    debug_custom_patterns()