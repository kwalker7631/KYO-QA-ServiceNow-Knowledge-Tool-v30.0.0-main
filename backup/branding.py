import logging
logging.getLogger(__name__).setLevel(logging.DEBUG)

"""Simple container for Kyocera brand colors."""

from dataclasses import dataclass

@dataclass
class KyoceraColors:
    kyocera_red: str = "#DA291C"
    kyocera_black: str = "#231F20"
    accent_blue: str = "#0078D4"
    success_green: str = "#107C10"
    warning_orange: str = "#FFA500"
    fail_red: str = "#DA291C"
    status_processing_bg: str = "#DDEEFF"
    status_default_bg: str = "#F8F8F8"
    highlight_blue: str = "#0078D4"

