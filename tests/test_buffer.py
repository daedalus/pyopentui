"""Tests for the Buffer class."""

import pytest
from pyopentui.buffer import Buffer, OptimizedBuffer, Cell
from pyopentui.types import RGBA, TextAttributes


class TestCell:
    def test_default_cell(self):
        cell = Cell()
        assert cell.char == " "
        assert cell.fg is None
        assert cell.bg is None
        assert cell.attributes == TextAttributes.NONE

    def test_cell_with_values(self):
        cell = Cell("a", RGBA.from_values(1, 0, 0), RGBA.from_values(0, 0, 1), TextAttributes.BOLD)
        assert cell.char == "a"
        assert cell.fg == RGBA.from_values(1, 0, 0)
        assert cell.bg == RGBA.from_values(0, 0, 1)
        assert cell.attributes == TextAttributes.BOLD

    def test_cell_copy(self):
        cell = Cell(
            "x", RGBA.from_values(1, 1, 1), RGBA.from_values(0, 0, 0), TextAttributes.ITALIC
        )
        copy = cell.copy()
        assert copy.char == cell.char
        assert copy.fg == cell.fg
        assert copy.bg == cell.bg
        assert copy.attributes == cell.attributes


class TestBuffer:
    def test_buffer_creation(self):
        buf = Buffer(80, 24)
        assert buf.width == 80
        assert buf.height == 24

    def test_clear_buffer(self):
        buf = Buffer(10, 10)
        buf.clear()
        cell = buf.get_cell(0, 0)
        assert cell is not None
        assert cell.char == " "

    def test_get_set_cell(self):
        buf = Buffer(10, 10)
        buf.set_cell(5, 5, "X", RGBA.from_values(1, 0, 0))
        cell = buf.get_cell(5, 5)
        assert cell is not None
        assert cell.char == "X"

    def test_out_of_bounds(self):
        buf = Buffer(10, 10)
        assert buf.get_cell(-1, 0) is None
        assert buf.get_cell(0, -1) is None
        assert buf.get_cell(10, 0) is None
        assert buf.get_cell(0, 10) is None

    def test_write_text(self):
        buf = Buffer(20, 5)
        width = buf.write_text(0, 0, "Hello")
        assert width == 5
        cell = buf.get_cell(0, 0)
        assert cell.char == "H"
        cell = buf.get_cell(4, 0)
        assert cell.char == "o"

    def test_write_text_truncation(self):
        buf = Buffer(3, 1)
        width = buf.write_text(0, 0, "Hello")
        assert width == 3

    def test_fill_rect(self):
        buf = Buffer(10, 10)
        buf.fill_rect(2, 2, 3, 3, "#", RGBA.from_values(1, 0, 0), RGBA.from_values(0, 0, 1))

        assert buf.get_cell(2, 2).char == "#"
        assert buf.get_cell(4, 4).char == "#"
        assert buf.get_cell(1, 2).char == " "

    def test_draw_frame(self):
        buf = Buffer(10, 10)
        buf.draw_frame(0, 0, 10, 10, "Title", RGBA.from_values(1, 1, 1))

        assert buf.get_cell(0, 0).char == "┌"
        assert buf.get_cell(9, 0).char == "┐"
        assert buf.get_cell(0, 9).char == "└"
        assert buf.get_cell(9, 9).char == "┘"

    def test_draw_frame_small(self):
        buf = Buffer(10, 10)
        buf.draw_frame(0, 0, 1, 1)

        assert buf.get_cell(0, 0).char == " "

    def test_cursor(self):
        buf = Buffer(10, 10)
        buf.set_cursor(5, 5)
        assert buf.cursor_x == 5
        assert buf.cursor_y == 5

    def test_cursor_bounds(self):
        buf = Buffer(10, 10)
        buf.set_cursor(100, 100)
        assert buf.cursor_x == 9
        assert buf.cursor_y == 9

    def test_resize(self):
        buf = Buffer(10, 10)
        buf.resize(20, 30)
        assert buf.width == 20
        assert buf.height == 30


class TestOptimizedBuffer:
    def test_optimized_buffer_creation(self):
        buf = OptimizedBuffer(80, 24)
        assert buf.width == 80
        assert buf.height == 24

    def test_scissor_stack(self):
        buf = OptimizedBuffer(10, 10)
        buf.push_scissor_rect(0, 0, 5, 5)
        assert len(buf._scissor_stack) == 1

        buf.pop_scissor_rect()
        assert len(buf._scissor_stack) == 0

    def test_opacity_stack(self):
        buf = OptimizedBuffer(10, 10)
        buf.push_opacity(0.5)
        assert len(buf._opacity_stack) == 1
        assert buf._opacity_stack[-1] == 0.5

        buf.pop_opacity()
        assert len(buf._opacity_stack) == 0


class TestBufferRendering:
    def test_render_to_string(self):
        buf = Buffer(5, 2)
        buf.write_text(0, 0, "Hello")
        output = buf.render_to_string()
        assert "Hello" in output
