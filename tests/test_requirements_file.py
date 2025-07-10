import pathlib


def test_no_extract_package():
    requirements = pathlib.Path('requirements.txt').read_text().splitlines()
    assert 'extract' not in requirements, "requirements.txt should not contain the 'extract' package"
