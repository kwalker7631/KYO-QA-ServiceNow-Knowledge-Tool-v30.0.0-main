import re


def test_custom_config_multiline():
    with open('ocr_utils.py', 'r', encoding='utf-8') as f:
        content = f.read()
    # ensure multi-line custom_config definition is present
    assert 'custom_config = (' in content
    # ensure no stray quote characters after the configuration string
    pattern = re.compile(r"custom_config = \(.*?\)\n", re.DOTALL)
    match = pattern.search(content)
    assert match, 'custom_config assignment not found'
    assignment = match.group(0)
    assert "'" not in assignment.split('\n')[-2].strip(), 'stray quote found after custom_config'

