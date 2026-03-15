"""Tests for the ANSI escape code module."""

import pytest
from pyopentui.ansi import ANSI, color_to_ansi_fg, color_to_ansi_bg
from pyopentui.types import RGBA


class TestANSI:
    def test_move_cursor(self):
        assert ANSI.move_cursor(1, 1) == "\x1b[1;1H"
        assert ANSI.move_cursor(10, 20) == "\x1b[10;20H"

    def test_move_cursor_and_clear(self):
        result = ANSI.move_cursor_and_clear(5, 10)
        assert "\x1b[5;10H" in result
        assert "\x1b[J" in result

    def test_scroll_down(self):
        assert ANSI.scroll_down(5) == "\x1b[5T"

    def test_scroll_up(self):
        assert ANSI.scroll_up(3) == "\x1b[3S"

    def test_rgb_foreground(self):
        assert ANSI.set_rgb_foreground(255, 128, 64) == "\x1b[38;2;255;128;64m"

    def test_rgb_background(self):
        assert ANSI.set_rgb_background(255, 128, 64) == "\x1b[48;2;255;128;64m"

    def test_cursor_visible(self):
        assert ANSI.set_cursor_visible(True) == "\x1b[?25h"
        assert ANSI.set_cursor_visible(False) == "\x1b[?25l"

    def test_bracketed_paste(self):
        assert ANSI.BRACKETED_PASTE_START == "\x1b[200~"
        assert ANSI.BRACKETED_PASTE_END == "\x1b[201~"

    def test_alternate_screen(self):
        assert ANSI.set_alternate_screen(True) == "\x1b[?1049h"
        assert ANSI.set_alternate_screen(False) == "\x1b[?1049l"

    def test_bold(self):
        assert ANSI.set_bold(True) == "\x1b[1m"
        assert ANSI.set_bold(False) == "\x1b[22m"

    def test_italic(self):
        assert ANSI.set_italic(True) == "\x1b[3m"
        assert ANSI.set_italic(False) == "\x1b[23m"

    def test_underline(self):
        assert ANSI.set_underline(True) == "\x1b[4m"
        assert ANSI.set_underline(False) == "\x1b[24m"

    def test_inverse(self):
        assert ANSI.set_inverse(True) == "\x1b[7m"
        assert ANSI.set_inverse(False) == "\x1b[27m"

    def test_clear_screen(self):
        assert ANSI.clear_screen() == "\x1b[2J"

    def test_clear_line(self):
        assert ANSI.clear_line() == "\x1b[2K"

    def test_mouse_tracking(self):
        assert "h" in ANSI.enable_mouse_tracking()
        assert "l" in ANSI.disable_mouse_tracking()


class TestColorToAnsi:
    def test_color_to_ansi_fg(self):
        color = RGBA.from_values(1.0, 0.5, 0.0, 1.0)
        result = color_to_ansi_fg(color)
        assert "\x1b[38;2;" in result

    def test_color_to_ansi_bg(self):
        color = RGBA.from_values(0.0, 0.0, 0.0, 1.0)
        result = color_to_ansi_bg(color)
        assert "\x1b[48;2;" in result
