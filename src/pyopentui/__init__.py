"""
PyOpenTUI - Python port of OpenTUI
Native terminal UI framework
"""

from .types import (
    RGBA,
    TextAttributes,
    ThemeMode,
    CursorStyle,
    MousePointerStyle,
    CursorStyleOptions,
)
from .renderable import Renderable, BaseRenderable, RootRenderable, LayoutEvents, RenderableEvents
from .renderer import CliRenderer
from .renderables import (
    BoxRenderable,
    TextRenderable,
    ScrollBox,
    ScrollBar,
    Input,
    Textarea,
)

__version__ = "0.1.0"

__all__ = [
    "RGBA",
    "TextAttributes",
    "ThemeMode",
    "CursorStyle",
    "MousePointerStyle",
    "CursorStyleOptions",
    "Renderable",
    "BaseRenderable",
    "RootRenderable",
    "LayoutEvents",
    "RenderableEvents",
    "CliRenderer",
    "BoxRenderable",
    "TextRenderable",
    "ScrollBox",
    "ScrollBar",
    "Input",
    "Textarea",
]
