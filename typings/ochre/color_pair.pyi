"""
This type stub file was generated by pyright.
"""

from dataclasses import dataclass
from typing import Optional
from .spaces import Color

"""A color pair of foreground and background colors."""
@dataclass(frozen=True)
class ColorPair:
    """A color pair of foreground and background colors."""
    foreground: Optional[Color] = ...
    background: Optional[Color] = ...

