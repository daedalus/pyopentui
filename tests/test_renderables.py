"""Tests for built-in renderable components."""

import pytest
from unittest.mock import MagicMock, patch


class MockRenderer:
    def __init__(self):
        self._width = 80
        self._height = 24
        self._request_render_called = False

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def request_render(self):
        self._request_render_called = True


class MockBuffer:
    def __init__(self, width=80, height=24):
        self.width = width
        self.height = height

    def clear(self, color=None):
        pass

    def fill_rect(self, x, y, w, h, char, fg, bg):
        pass

    def draw_frame(self, x, y, w, h, title, fg, bg):
        pass

    def write_text(self, x, y, text, fg, bg, attr=0):
        return len(text)

    def set_cell(self, x, y, char, fg=None, bg=None, attr=0):
        pass


class TestBoxRenderable:
    def test_box_creation(self):
        from pyopentui.renderables import BoxRenderable

        ctx = MockRenderer()
        box = BoxRenderable(ctx, width=10, height=5)

        assert box._width == 10
        assert box._height == 5
        assert box._border is False
        assert box._visible is True

    def test_box_with_border(self):
        from pyopentui.renderables import BoxRenderable

        ctx = MockRenderer()
        box = BoxRenderable(ctx, width=10, height=5, border=True)

        assert box._border is True


class TestTextRenderable:
    def test_text_multiline(self):
        from pyopentui.renderables import TextRenderable

        ctx = MockRenderer()
        text = TextRenderable(ctx, "Line 1\nLine 2\nLine 3")

        assert text._text == "Line 1\nLine 2\nLine 3"
        assert text._visible is True

    def test_text_setter(self):
        from pyopentui.renderables import TextRenderable

        ctx = MockRenderer()
        text = TextRenderable(ctx, "Hello")

        text.text = "World"
        assert text.text == "World"

    def test_text_with_style(self):
        from pyopentui.renderables import TextRenderable
        from pyopentui.types import TextAttributes

        ctx = MockRenderer()
        text = TextRenderable(ctx, "Bold Text", bold=True, italic=True)

        assert text._bold is True
        assert text._italic is True


class TestScrollBox:
    def test_scrollbox_creation(self):
        from pyopentui.renderables import ScrollBox

        ctx = MockRenderer()
        scrollbox = ScrollBox(ctx, width=20, height=10)

        assert scrollbox._width == 20
        assert scrollbox._height == 10
        assert scrollbox.scroll_x == 0
        assert scrollbox.scroll_y == 0
        assert scrollbox._visible is True

    def test_scrollbox_setters(self):
        from pyopentui.renderables import ScrollBox

        ctx = MockRenderer()
        scrollbox = ScrollBox(ctx, width=20, height=10)

        scrollbox.scroll_x = 5
        assert scrollbox.scroll_x == 5

        scrollbox.scroll_y = 10
        assert scrollbox.scroll_y == 10


class TestInput:
    def test_input_creation(self):
        from pyopentui.renderables import Input

        ctx = MockRenderer()
        input_field = Input(ctx, placeholder="Enter text...")

        assert input_field.value == ""
        assert input_field._placeholder == "Enter text..."
        assert input_field.focusable is True

    def test_input_with_value(self):
        from pyopentui.renderables import Input

        ctx = MockRenderer()
        input_field = Input(ctx, value="test value")

        assert input_field.value == "test value"

    def test_input_max_length(self):
        from pyopentui.renderables import Input

        ctx = MockRenderer()
        input_field = Input(ctx, max_length=5)

        input_field.value = "123456789"
        assert input_field.value == "12345"

    def test_input_key_handling(self):
        from pyopentui.renderables import Input
        from pyopentui.renderer import KeyEvent

        ctx = MockRenderer()
        input_field = Input(ctx, value="Hello")

        key = KeyEvent("a", "a")
        result = input_field.handle_key_press(key)
        assert result is True
        assert input_field.value == "Helloa"

    def test_input_backspace(self):
        from pyopentui.renderables import Input
        from pyopentui.renderer import KeyEvent

        ctx = MockRenderer()
        input_field = Input(ctx, value="Hello")

        key = KeyEvent("backspace", "\x7f")
        result = input_field.handle_key_press(key)
        assert result is True
        assert input_field.value == "Hell"

    def test_input_cursor_movement(self):
        from pyopentui.renderables import Input
        from pyopentui.renderer import KeyEvent

        ctx = MockRenderer()
        input_field = Input(ctx, value="Hello")

        input_field._cursor_position = 3

        key = KeyEvent("left", "\x1b[D")
        input_field.handle_key_press(key)
        assert input_field._cursor_position == 2

        key = KeyEvent("right", "\x1b[C")
        input_field.handle_key_press(key)
        assert input_field._cursor_position == 3


class TestTextarea:
    def test_textarea_creation(self):
        from pyopentui.renderables import Textarea

        ctx = MockRenderer()
        textarea = Textarea(ctx)

        assert textarea.value == ""
        assert textarea.focusable is True

    def test_textarea_with_value(self):
        from pyopentui.renderables import Textarea

        ctx = MockRenderer()
        textarea = Textarea(ctx, value="Line 1\nLine 2")

        assert textarea.value == "Line 1\nLine 2"
        assert textarea.height == 2

    def test_textarea_multiline(self):
        from pyopentui.renderables import Textarea
        from pyopentui.renderer import KeyEvent

        ctx = MockRenderer()
        textarea = Textarea(ctx, value="Line 1")

        key = KeyEvent("enter", "\r")
        textarea.handle_key_press(key)

        assert "\n" in textarea.value

    def test_textarea_cursor_navigation(self):
        from pyopentui.renderables import Textarea
        from pyopentui.renderer import KeyEvent

        ctx = MockRenderer()
        textarea = Textarea(ctx, value="Line 1\nLine 2")

        key = KeyEvent("up", "\x1b[A")
        textarea.handle_key_press(key)
        assert textarea._cursor_line == 0

        key = KeyEvent("down", "\x1b[B")
        textarea.handle_key_press(key)
        assert textarea._cursor_line == 1


class TestScrollBar:
    def test_scrollbar_creation(self):
        from pyopentui.renderables import ScrollBar

        ctx = MockRenderer()
        scrollbar = ScrollBar(ctx, height=10, orientation="vertical")

        assert scrollbar._height == 10
        assert scrollbar._orientation == "vertical"
        assert scrollbar.value == 0
        assert scrollbar._visible is True

    def test_scrollbar_value_bounds(self):
        from pyopentui.renderables import ScrollBar

        ctx = MockRenderer()
        scrollbar = ScrollBar(ctx, max_value=100)

        scrollbar.value = 50
        assert scrollbar.value == 50

        scrollbar.value = 150
        assert scrollbar.value == 100

        scrollbar.value = -10
        assert scrollbar.value == 0
