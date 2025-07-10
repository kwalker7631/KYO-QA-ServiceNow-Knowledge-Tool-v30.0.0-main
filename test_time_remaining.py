import types
import sys
import pathlib
import importlib.util

config = types.ModuleType('config')
config.BRAND_COLORS = {}
config.ASSETS_DIR = pathlib.Path('.')
sys.modules['config'] = config

processing_engine = types.ModuleType('processing_engine')
processing_engine.run_processing_job = lambda *a, **k: None
sys.modules['processing_engine'] = processing_engine

file_utils = types.ModuleType('file_utils')
file_utils.open_file = lambda *a, **k: None
file_utils.ensure_folders = lambda: None
file_utils.cleanup_temp_files = lambda: None
sys.modules['file_utils'] = file_utils

kyo_review_tool = types.ModuleType('kyo_review_tool')
kyo_review_tool.ReviewWindow = object
sys.modules['kyo_review_tool'] = kyo_review_tool

version = types.ModuleType('version')
version.VERSION = '0'
sys.modules['version'] = version

logging_utils = types.ModuleType('logging_utils')
logging_utils.setup_logger = lambda name: None
sys.modules['logging_utils'] = logging_utils

gui_components = types.ModuleType('gui_components')
for name in ('create_main_header','create_io_section','create_process_controls'):
    setattr(gui_components, name, lambda *a, **k: None)
sys.modules['gui_components'] = gui_components

spec = importlib.util.spec_from_file_location('kyo_app', 'kyo_qa_tool_app.py')
kyo_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kyo_app)

def test_get_remaining_seconds():
    remaining = kyo_app.get_remaining_seconds(start_time=1, total_files=5, processed_files=2, now=31)
    assert remaining == 45
