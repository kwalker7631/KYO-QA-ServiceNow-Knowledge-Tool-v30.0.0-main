import logging
logging.getLogger(__name__).setLevel(logging.DEBUG)

"""UI style constants and helpers."""

from dataclasses import dataclass

@dataclass
class StyleConfig:
    high_contrast: bool = False

