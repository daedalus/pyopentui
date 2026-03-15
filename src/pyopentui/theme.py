"""Color theme for PyOpenTUI based on showcase.png"""

from .types import RGBA


class Theme:
    """Color theme inspired by showcase.png"""

    # Background colors
    BG_PRIMARY = RGBA.from_hex("#0f0f23")
    BG_SECONDARY = RGBA.from_hex("#16213e")
    BG_TERTIARY = RGBA.from_hex("#1a1a2e")

    # Accent colors
    GREEN = RGBA.from_hex("#00ff00")
    RED = RGBA.from_hex("#ff6b6b")
    CYAN = RGBA.from_hex("#4ecdc4")
    YELLOW = RGBA.from_hex("#ffe66d")
    MINT = RGBA.from_hex("#95e1d3")
    LIGHT_GREEN = RGBA.from_hex("#a8e6cf")
    PURPLE = RGBA.from_hex("#6c5ce7")
    PINK = RGBA.from_hex("#fd79a8")

    # Text colors
    TEXT_PRIMARY = RGBA.from_hex("#ffffff")
    TEXT_SECONDARY = RGBA.from_hex("#aaaaaa")
    TEXT_MUTED = RGBA.from_hex("#666666")

    # Border colors for boxes
    BOX_HEADER = GREEN
    BOX_INPUT = CYAN
    BOX_HISTORY = YELLOW
    BOX_SECONDARY = RED
    BOX_CONTROLS = PURPLE


__all__ = ["Theme"]
