import types
import sys
import pathlib
import importlib.util

config = types.ModuleType("config")
config.BRAND_COLORS = {}
config.ASSETS_DIR = pathlib.Path(".")
original_config = sys.modules.get("config")
sys.modules["config"] = config

processing_engine = types.ModuleType("processing_engine")
processing_engine.run_processing_job = lambda *a, **k: None
original_pe = sys.modules.get("processing_engine")
sys.modules["processing_engine"] = processing_engine

file_utils = types.ModuleType("file_utils")
file_utils.open_file = lambda *a, **k: None
file_utils.ensure_folders = lambda: None
file_utils.cleanup_temp_files = lambda: None
original_fu = sys.modules.get("file_utils")
sys.modules["file_utils"] = file_utils

kyo_review_tool = types.ModuleType("kyo_review_tool")
kyo_review_tool.ReviewWindow = object
original_review = sys.modules.get("kyo_review_tool")
sys.modules["kyo_review_tool"] = kyo_review_tool

version = types.ModuleType("version")
version.VERSION = "0"
original_version = sys.modules.get("version")
sys.modules["version"] = version

logging_utils = types.ModuleType("logging_utils")
logging_utils.setup_logger = lambda name: None
original_logging = sys.modules.get("logging_utils")
sys.modules["logging_utils"] = logging_utils

gui_components = types.ModuleType("gui_components")
for name in (
    "create_main_header",
    "create_io_section",
    "create_process_controls",
    "create_status_and_log_section",
):
    setattr(gui_components, name, lambda *a, **k: None)
original_gc = sys.modules.get("gui_components")
sys.modules["gui_components"] = gui_components

spec = importlib.util.spec_from_file_location("kyo_app", "kyo_qa_tool_app.py")
kyo_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kyo_app)
if original_config is not None:
    sys.modules["config"] = original_config
else:
    del sys.modules["config"]
if original_pe is not None:
    sys.modules["processing_engine"] = original_pe
else:
    del sys.modules["processing_engine"]
if original_fu is not None:
    sys.modules["file_utils"] = original_fu
else:
    del sys.modules["file_utils"]
if original_review is not None:
    sys.modules["kyo_review_tool"] = original_review
else:
    del sys.modules["kyo_review_tool"]
if original_version is not None:
    sys.modules["version"] = original_version
else:
    del sys.modules["version"]
if original_logging is not None:
    sys.modules["logging_utils"] = original_logging
else:
    del sys.modules["logging_utils"]
if original_gc is not None:
    sys.modules["gui_components"] = original_gc
else:
    del sys.modules["gui_components"]


def test_get_remaining_seconds():
    remaining = kyo_app.get_remaining_seconds(
        start_time=1, total_files=5, processed_files=2, now=31
    )
    assert remaining == 45


def test_get_remaining_seconds_no_progress():
    remaining = kyo_app.get_remaining_seconds(
        start_time=1, total_files=5, processed_files=0, now=2
    )
    assert remaining == 0
