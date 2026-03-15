"""Tests for the CLI renderer and terminal."""

import pytest
from io import StringIO
from pyopentui.renderer import CliRenderer, MouseEvent, KeyEvent
from pyopentui.terminal import Terminal, InputReader, EventEmitter


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

    def test_renderer_terminal_instance(self):
        renderer = CliRenderer(80, 24)
        assert renderer._terminal is not None
        assert isinstance(renderer._terminal, Terminal)

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
        renderer = CliRenderer(80, 24)
        assert renderer._dirty is True

    def test_renderer_request_render(self):
        renderer = CliRenderer(80, 24)
        renderer._dirty = False
        renderer.request_render()
        assert renderer._dirty is True

    def test_renderer_stop(self):
        renderer = CliRenderer(80, 24)
        renderer._running = True
        renderer.stop()
        assert renderer.is_running is False


class TestTerminal:
    def test_terminal_creation(self):
        term = Terminal()
        assert term.stdin is not None
        assert term.stdout is not None

    def test_terminal_isatty(self):
        term = Terminal()
        result = term.isatty()
        assert isinstance(result, bool)

    def test_terminal_write(self):
        term = Terminal(stdin=None, stdout=StringIO())
        term.write("test")
        output = term.stdout.getvalue()
        assert output == "test"

    def test_terminal_flush(self):
        term = Terminal(stdin=None, stdout=StringIO())
        term.write("test")
        term.flush()
        assert True

    def test_terminal_cursor_methods(self):
        term = Terminal(stdin=None, stdout=StringIO())
        term.hide_cursor()
        term.show_cursor()
        term.home_cursor()
        term.set_cursor(5, 10)
        output = term.stdout.getvalue()
        assert "\033[?25l" in output
        assert "\033[?25h" in output
        assert "\033[H" in output
        assert "\033[5;10H" in output

    def test_terminal_clear_screen(self):
        term = Terminal(stdin=None, stdout=StringIO())
        term.clear_screen()
        output = term.stdout.getvalue()
        assert "\033[2J" in output

    def test_terminal_alternate_screen(self):
        term = Terminal(stdin=None, stdout=StringIO())
        term.enter_alternate_screen()
        term.exit_alternate_screen()
        output = term.stdout.getvalue()
        assert "\033[?1049h" in output
        assert "\033[?1049l" in output

    def test_terminal_mouse_tracking(self):
        term = Terminal(stdin=None, stdout=StringIO())
        term.enable_mouse_tracking()
        term.disable_mouse_tracking()
        output = term.stdout.getvalue()
        assert "\033[?1000h" in output
        assert "\033[?1000l" in output

    def test_terminal_line_wrap(self):
        term = Terminal(stdin=None, stdout=StringIO())
        term.disable_line_wrap()
        term.enable_line_wrap()
        output = term.stdout.getvalue()
        assert "\033[?7l" in output
        assert "\033[?7h" in output

    def test_terminal_background_color(self):
        term = Terminal(stdin=None, stdout=StringIO())
        term.set_background_color(255, 128, 64)
        output = term.stdout.getvalue()
        assert "\033[48;2;255;128;64m" in output

    def test_terminal_reset(self):
        term = Terminal(stdin=None, stdout=StringIO())
        term.reset()
        output = term.stdout.getvalue()
        assert "\033[0m" in output
        assert "\033c" in output

    def test_terminal_setup_screen(self):
        term = Terminal(stdin=None, stdout=StringIO())
        term.setup_screen(100, 100, 100)
        output = term.stdout.getvalue()
        assert "\033[?1049h" in output
        assert "\033[48;2;100;100;100m" in output
        assert "\033[2J" in output
        assert "\033[?7l" in output

    def test_terminal_restore_screen(self):
        term = Terminal(stdin=None, stdout=StringIO())
        term.restore_screen()
        output = term.stdout.getvalue()
        assert "\033[?7h" in output
        assert "\033[0m" in output
        assert "\033[?1049l" in output


class TestEventEmitter:
    def test_event_emitter_on_off(self):
        emitter = EventEmitter()
        calls = []

        def handler():
            calls.append(1)

        emitter.on("test", handler)
        emitter.emit("test")
        assert len(calls) == 1

        emitter.off("test", handler)
        emitter.emit("test")
        assert len(calls) == 1


class TestInputReader:
    def test_input_reader_creation(self):
        term = Terminal(stdin=None, stdout=StringIO())
        reader = InputReader(term)
        assert reader.terminal is term

    def test_input_reader_key_map(self):
        term = Terminal(stdin=None, stdout=StringIO())
        reader = InputReader(term)
        assert reader._key_map.get("\r") == "enter"
        assert reader._key_map.get("\n") == "enter"
        assert reader._key_map.get("\t") == "tab"
        assert reader._key_map.get("\x7f") == "backspace"
        assert reader._key_map.get("\x1b") == "escape"
        assert reader._key_map.get(" ") == "space"
