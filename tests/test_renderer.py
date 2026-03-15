"""Tests for the CLI renderer."""

import pytest
from pyopentui.renderer import CliRenderer, MouseEvent, KeyEvent


class TestKeyEvent:
    def test_key_event_creation(self):
        key = KeyEvent("a", "a")
        assert key.name == "a"
        assert key.sequence == "a"
        assert key.ctrl is False
        assert key.meta is False
        assert key.shift is False

    def test_key_event_with_modifiers(self):
        key = KeyEvent("c", "c", ctrl=True, meta=True, shift=True)
        assert key.ctrl is True
        assert key.meta is True
        assert key.shift is True


class TestMouseEvent:
    def test_mouse_event_creation(self):
        event = MouseEvent("click", 10, 5, 0)
        assert event.type == "click"
        assert event.x == 10
        assert event.y == 5
        assert event.button == 0

    def test_mouse_event_with_modifiers(self):
        event = MouseEvent("move", 5, 5, 0, {"shift": True, "ctrl": True, "alt": False})
        assert event.modifiers["shift"] is True
        assert event.modifiers["ctrl"] is True
        assert event.modifiers["alt"] is False


class TestCliRenderer:
    def test_renderer_creation(self):
        renderer = CliRenderer(80, 24)
        assert renderer.width == 80
        assert renderer.height == 24

    def test_renderer_initial_state(self):
        renderer = CliRenderer()
        assert renderer.is_running is False
        assert renderer.is_destroyed is False
        assert renderer.buffer is not None

    def test_renderer_buffer_dimensions(self):
        renderer = CliRenderer(100, 50)
        assert renderer.buffer.width == 100
        assert renderer.buffer.height == 50

    def test_renderer_resize(self):
        renderer = CliRenderer(80, 24)
        renderer.resize(100, 40)
        assert renderer.width == 100
        assert renderer.height == 40
        assert renderer.buffer.width == 100
        assert renderer.buffer.height == 40

    def test_renderer_set_background_color(self):
        from pyopentui.types import RGBA

        renderer = CliRenderer(80, 24)
        color = RGBA.from_values(0.1, 0.1, 0.1, 1.0)
        renderer.set_background_color(color)
        assert renderer._background_color == color

    def test_renderer_cursor(self):
        renderer = CliRenderer(80, 24)
        renderer.set_cursor_position(10, 5, True)
        assert renderer._cursor_x == 10
        assert renderer._cursor_y == 5
        assert renderer._cursor_visible is True

    def test_renderer_event_system(self):
        renderer = CliRenderer(80, 24)

        events_received = []

        def callback(*args):
            events_received.append(args)

        renderer.on("test-event", callback)
        renderer.emit("test-event", "arg1", "arg2")

        assert len(events_received) == 1
        assert events_received[0] == ("arg1", "arg2")

    def test_renderer_input_handlers(self):
        renderer = CliRenderer(80, 24)

        handler_called = []

        def handler(sequence):
            handler_called.append(sequence)
            return True

        renderer.add_input_handler(handler)

        renderer._input_handlers[0]("test")

        assert len(handler_called) == 1

    def test_renderer_dirty_flag(self):
        from pyopentui.renderer import CliRenderer

        renderer = CliRenderer(80, 24)
        assert renderer._dirty is True
        assert renderer._dirty is not None

    def test_renderer_focusable(self):
        from pyopentui.renderable import Renderable
        from pyopentui.renderer import CliRenderer

        renderer = CliRenderer(80, 24)

        class TestRenderable(Renderable):
            pass

        r1 = TestRenderable(renderer)
        r1._focusable = True
        r2 = TestRenderable(renderer)
        r2._focusable = False

        renderer.focus_renderable(r1)

        renderer.focus_renderable(r2)
