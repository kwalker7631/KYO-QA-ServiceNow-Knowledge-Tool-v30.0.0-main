import re
import importlib


def test_model_patterns_compile():
    import custom_patterns
    for pattern in custom_patterns.MODEL_PATTERNS:
        re.compile(pattern)



def test_qa_patterns_compile():
    import custom_patterns
    for pattern in custom_patterns.QA_NUMBER_PATTERNS:
        re.compile(pattern)

