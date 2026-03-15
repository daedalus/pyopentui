from __future__ import annotations
import re
import sys
from typing import Any, Optional, Union


class RGBA:
    __slots__ = ("r", "g", "b", "a")

    def __init__(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @staticmethod
    def from_values(r: float, g: float, b: float, a: float = 1.0) -> RGBA:
        return RGBA(r, g, b, a)

    @staticmethod
    def from_ints(r: int, g: int, b: int, a: int = 255) -> RGBA:
        return RGBA(r / 255.0, g / 255.0, b / 255.0, a / 255.0)

    @staticmethod
    def from_hex(hex_color: str) -> RGBA:
        hex_color = hex_color.lstrip("#")

        if len(hex_color) == 3:
            hex_color = "".join(c * 2 for c in hex_color)
        elif len(hex_color) == 4:
            hex_color = "".join(c * 2 for c in hex_color)

        if not re.match(r"^[0-9A-Fa-f]{6}$", hex_color) and not re.match(
            r"^[0-9A-Fa-f]{8}$", hex_color
        ):
            print(f"Invalid hex color: {hex_color}, defaulting to magenta", file=sys.stderr)
            return RGBA(1, 0, 1, 1)

        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        a = int(hex_color[6:8], 16) / 255.0 if len(hex_color) == 8 else 1.0

        return RGBA(r, g, b, a)

    def to_ints(self) -> tuple[int, int, int, int]:
        return (round(self.r * 255), round(self.g * 255), round(self.b * 255), round(self.a * 255))

    def equals(self, other: Optional[RGBA]) -> bool:
        if other is None:
            return False
        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a

    def __repr__(self) -> str:
        return f"RGBA({self.r:.2f}, {self.g:.2f}, {self.b:.2f}, {self.a:.2f})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, RGBA):
            return False
        return self.equals(other)

    def __hash__(self) -> int:
        return hash((round(self.r, 4), round(self.g, 4), round(self.b, 4), round(self.a, 4)))


ColorInput = Union[str, RGBA]


TEXT_ATTRIBUTES_NONE = 0
TEXT_ATTRIBUTES_BOLD = 1 << 0
TEXT_ATTRIBUTES_DIM = 1 << 1
TEXT_ATTRIBUTES_ITALIC = 1 << 2
TEXT_ATTRIBUTES_UNDERLINE = 1 << 3
TEXT_ATTRIBUTES_BLINK = 1 << 4
TEXT_ATTRIBUTES_INVERSE = 1 << 5
TEXT_ATTRIBUTES_HIDDEN = 1 << 6
TEXT_ATTRIBUTES_STRIKETHROUGH = 1 << 7


class TextAttributes:
    NONE = TEXT_ATTRIBUTES_NONE
    BOLD = TEXT_ATTRIBUTES_BOLD
    DIM = TEXT_ATTRIBUTES_DIM
    ITALIC = TEXT_ATTRIBUTES_ITALIC
    UNDERLINE = TEXT_ATTRIBUTES_UNDERLINE
    BLINK = TEXT_ATTRIBUTES_BLINK
    INVERSE = TEXT_ATTRIBUTES_INVERSE
    HIDDEN = TEXT_ATTRIBUTES_HIDDEN
    STRIKETHROUGH = TEXT_ATTRIBUTES_STRIKETHROUGH


ThemeMode = str
CursorStyle = str
MousePointerStyle = str


class CursorStyleOptions:
    def __init__(
        self,
        style: CursorStyle = "block",
        blinking: bool = True,
        color: Optional[RGBA] = None,
        cursor: Optional[MousePointerStyle] = None,
    ) -> None:
        self.style = style
        self.blinking = blinking
        self.color = color
        self.cursor = cursor


class DebugOverlayCorner:
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3


WidthMethod = str
