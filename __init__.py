"""Package initializer for the Kyocera QA tool."""
import sys
import importlib
from pathlib import Path
import logging

logging.getLogger(__name__).setLevel(logging.DEBUG)

pkg_dir = Path(__file__).parent
if str(pkg_dir) not in sys.path:
    sys.path.insert(0, str(pkg_dir))

for _mod in ("config", "branding", "styles"):
    if _mod not in sys.modules:
        try:
            sys.modules[_mod] = importlib.import_module(f"{_mod}")
        except Exception:
            pass

