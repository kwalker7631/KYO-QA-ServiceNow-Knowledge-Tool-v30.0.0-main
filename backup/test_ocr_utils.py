import re

def test_custom_config_string():
    with open('ocr_utils.py', 'r', encoding='utf-8') as f:
        content = f.read()
    # Find the custom_config assignment
    pattern = re.compile(r"custom_config\s*=\s*r'([^']+)'")
    match = pattern.search(content)
    assert match, 'custom_config assignment not found'
    config_value = match.group(1)
    assert config_value.endswith('/\\|'), 'custom_config should end with /\\|'
    assert '"' not in config_value, 'double quote found in custom_config'
