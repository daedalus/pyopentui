"""ANSI escape code handling for terminal output."""

from typing import Optional

from .types import RGBA


class ANSI:
    SWITCH_TO_ALTERNATE_SCREEN = "\x1b[?1049h"
    SWITCH_TO_MAIN_SCREEN = "\x1b[?1049l"
    RESET = "\x1b[0m"

    @staticmethod
    def scroll_down(lines: int) -> str:
        return f"\x1b[{lines}T"

    @staticmethod
    def scroll_up(lines: int) -> str:
        return f"\x1b[{lines}S"

    @staticmethod
    def move_cursor(row: int, col: int) -> str:
        return f"\x1b[{row};{col}H"

    @staticmethod
    def move_cursor_and_clear(row: int, col: int) -> str:
        return f"\x1b[{row};{col}H\x1b[J"

    @staticmethod
    def set_rgb_background(r: int, g: int, b: int) -> str:
        return f"\x1b[48;2;{r};{g};{b}m"

    @staticmethod
    def set_rgb_foreground(r: int, g: int, b: int) -> str:
        return f"\x1b[38;2;{r};{g};{b}m"

    RESET_BACKGROUND = "\x1b[49m"
    RESET_FOREGROUND = "\x1b[39m"

    BRACKETED_PASTE_START = "\x1b[200~"
    BRACKETED_PASTE_END = "\x1b[201~"

    @staticmethod
    def set_cursor_visible(visible: bool) -> str:
        return "\x1b[?25h" if visible else "\x1b[?25l"

    @staticmethod
    def save_cursor_position() -> str:
        return "\x1b[s"

    @staticmethod
    def restore_cursor_position() -> str:
        return "\x1b[u"

    @staticmethod
    def clear_screen() -> str:
        return "\x1b[2J"

    @staticmethod
    def clear_line() -> str:
        return "\x1b[2K"

    @staticmethod
    def set_attribute(attr: int) -> str:
        return f"\x1b[{attr}m"

    @staticmethod
    def set_bold(enabled: bool = True) -> str:
        return "\x1b[1m" if enabled else "\x1b[22m"

    @staticmethod
    def set_italic(enabled: bool = True) -> str:
        return "\x1b[3m" if enabled else "\x1b[23m"

    @staticmethod
    def set_underline(enabled: bool = True) -> str:
        return "\x1b[4m" if enabled else "\x1b[24m"

    @staticmethod
    def set_inverse(enabled: bool = True) -> str:
        return "\x1b[7m" if enabled else "\x1b[27m"

    @staticmethod
    def set_blink(enabled: bool = True) -> str:
        return "\x1b[5m" if enabled else "\x1b[25m"

    @staticmethod
    def set_cursor_style(style: str, blinking: bool = True) -> str:
        style_map = {
            "block": 1,
            "underline": 3,
            "bar": 5,
            "blink_block": 1,
            "blink_underline": 3,
            "blink_bar": 5,
        }
        base = style_map.get(style, 1)
        if not blinking:
            base += 1
        return f"\x1b[{base} q"

    @staticmethod
    def set_alternate_screen(enabled: bool = True) -> str:
        return ANSI.SWITCH_TO_ALTERNATE_SCREEN if enabled else ANSI.SWITCH_TO_MAIN_SCREEN

    @staticmethod
    def enable_mouse_tracking() -> str:
        return "\x1b[?1000h\x1b[?1002h\x1b[?1015h\x1b[?1006h"

    @staticmethod
    def disable_mouse_tracking() -> str:
        return "\x1b[?1000l\x1b[?1002l\x1b[?1015l\x1b[?1006l"

    @staticmethod
    def enable_bracketed_paste() -> str:
        return ANSI.BRACKETED_PASTE_START

    @staticmethod
    def disable_bracketed_paste() -> str:
        return ANSI.BRACKETED_PASTE_END


def color_to_ansi_fg(color: RGBA) -> str:
    r, g, b, _ = color.to_ints()
    return ANSI.set_rgb_foreground(r, g, b)


def color_to_ansi_bg(color: RGBA) -> str:
    r, g, b, _ = color.to_ints()
    return ANSI.set_rgb_background(r, g, b)
