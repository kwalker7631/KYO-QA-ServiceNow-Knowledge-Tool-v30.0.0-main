# Ensure openpyxl stub is available for unit tests
try:  # pragma: no cover - optional dependency
    import openpyxl  # noqa: F401
except Exception:
    import types, sys
    openpyxl = types.ModuleType("openpyxl")
    styles = types.ModuleType("styles")
    Alignment = type("Alignment", (), {})
    Font = type("Font", (), {})
    class PatternFill:
        def __init__(self, *a, **k):
            pass
    styles.Alignment = Alignment
    styles.Font = Font
    styles.PatternFill = PatternFill
    openpyxl.styles = styles
    utils = types.ModuleType("utils")
    utils.get_column_letter = lambda x: "A"
    utils.dataframe = types.ModuleType("dataframe")
    utils.dataframe.dataframe_to_rows = lambda df: []
    openpyxl.utils = utils
    worksheet = types.ModuleType("worksheet")
    copier = types.ModuleType("copier")
    copier.WorksheetCopy = object
    worksheet.copier = copier
    openpyxl.worksheet = worksheet
    sys.modules.setdefault("openpyxl.worksheet", worksheet)
    sys.modules.setdefault("openpyxl.worksheet.copier", copier)
    sys.modules.setdefault("openpyxl.utils.dataframe", utils.dataframe)
    sys.modules.setdefault("openpyxl.utils", utils)
    sys.modules.setdefault("openpyxl.styles", styles)
    sys.modules.setdefault("openpyxl", openpyxl)

# Provide a lightweight pandas stub for the test environment
try:  # pragma: no cover - only for tests
    import pandas  # type: ignore  # noqa: F401
except Exception:  # pragma: no cover
    import types
    import sys

    class _DF(list):
        def to_dict(self, *_, **__):
            return list(self)

    pandas = types.ModuleType("pandas")

    def DataFrame(data):
        df = _DF(data)
        df.columns = []
        return df

    pandas.DataFrame = DataFrame
    sys.modules.setdefault("pandas", pandas)
