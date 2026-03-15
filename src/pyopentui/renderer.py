"""CLI Renderer for terminal output and input handling."""

from __future__ import annotations
import sys
import os
import select
import termios
import tty
from typing import Any, Callable, Dict, List, Optional, Set
from threading import Thread, Event as ThreadEvent

from .ansi import ANSI
from .buffer import Buffer, OptimizedBuffer
from .renderable import Renderable, RootRenderable
from .types import RGBA, CursorStyle, CursorStyleOptions, MousePointerStyle, ThemeMode


class MouseEvent:
    def __init__(
        self,
        type: str,
        x: int,
        y: int,
        button: int = 0,
        modifiers: Optional[Dict[str, bool]] = None,
    ) -> None:
        self.type = type
        self.x = x
        self.y = y
        self.button = button
        self.modifiers = modifiers or {"shift": False, "alt": False, "ctrl": False}


class KeyEvent:
    def __init__(
        self,
        name: str,
        sequence: str,
        ctrl: bool = False,
        meta: bool = False,
        shift: bool = False,
    ) -> None:
        self.name = name
        self.sequence = sequence
        self.ctrl = ctrl
        self.meta = meta
        self.shift = shift


class CliRenderer:
    """Main CLI renderer for terminal UI."""

    def __init__(
        self,
        width: int = 80,
        height: int = 24,
        stdin: Optional[Any] = None,
        stdout: Optional[Any] = None,
    ) -> None:
        self._width = width
        self._height = height
        self._stdin = stdin or sys.stdin
        self._stdout = stdout or sys.stdout
        self._running = False
        self._destroyed = False
        self._dirty = True

        self._buffer = OptimizedBuffer(width, height)
        self._next_buffer = OptimizedBuffer(width, height)
        self._last_frame_content: Optional[str] = None

        self._background_color = RGBA.from_values(0, 0, 0, 1)
        self._root: Optional[RootRenderable] = None

        self._listeners: Dict[str, List[Callable]] = {}
        self._input_handlers: List[Callable[[str], bool]] = []

        self._target_fps = 30
        self._max_fps = 60
        self._frame_time = 1.0 / self._target_fps

        self._last_frame_time = 0.0
        self._frame_count = 0
        self._fps = 0
        self._last_fps_time = 0.0

        self._use_alternate_screen = False  # Disabled for better compatibility
        self._use_mouse = False

        self._current_focused_renderable: Optional[Renderable] = None

        self._cursor_x = 0
        self._cursor_y = 0
        self._cursor_visible = True
        self._cursor_style: CursorStyleOptions = CursorStyleOptions()

        self._theme_mode: Optional[ThemeMode] = None
        self._debug_overlay_enabled = False

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def buffer(self) -> Buffer:
        return self._buffer

    @property
    def root(self) -> Optional[RootRenderable]:
        return self._root

    def setup(self) -> None:
        """Set up the terminal for rendering."""
        if self._use_alternate_screen:
            self._stdout.write(ANSI.set_alternate_screen(True))

        self._stdout.write(ANSI.clear_screen())
        self._stdout.write(ANSI.set_cursor_position(1, 1))

        if self._use_mouse:
            self._stdout.write(ANSI.enable_mouse_tracking())

        self._stdout.write(ANSI.set_cursor_visible(True))
        self._stdout.flush()

        try:
            self._old_term_settings = termios.tcgetattr(self._stdin.fileno())
            tty.setcbreak(self._stdin.fileno())
        except termios.error:
            pass

        self._root = RootRenderable(self, self._width, self._height)

    def cleanup(self) -> None:
        """Clean up the terminal after rendering."""
        self._stdout.write(ANSI.set_cursor_position(1, 1))
        self._stdout.write(ANSI.set_alternate_screen(False))
        self._stdout.write(ANSI.disable_mouse_tracking())
        self._stdout.write(ANSI.set_cursor_visible(True))
        self._stdout.write(ANSI.RESET)
        self._stdout.write("\n")
        self._stdout.flush()

        if hasattr(self, "_old_term_settings"):
            try:
                termios.tcsetattr(self._stdin.fileno(), termios.TCSADRAIN, self._old_term_settings)
            except termios.error:
                pass

    def on(self, event: str, callback: Callable) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def off(self, event: str, callback: Callable) -> None:
        if event in self._listeners:
            self._listeners[event] = [cb for cb in self._listeners[event] if cb != callback]

    def emit(self, event: str, *args: Any) -> None:
        if event in self._listeners:
            for callback in self._listeners[event]:
                callback(*args)

    def add_input_handler(self, handler: Callable[[str], bool]) -> None:
        self._input_handlers.append(handler)

    def remove_input_handler(self, handler: Callable[[str], bool]) -> None:
        self._input_handlers = [h for h in self._input_handlers if h != handler]

    def request_render(self) -> None:
        self._dirty = True

    def resize(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self._buffer.resize(width, height)
        self._next_buffer.resize(width, height)

        if self._root:
            self._root.resize(width, height)

        self.request_render()
        self.emit("resize", width, height)

    def set_background_color(self, color: RGBA) -> None:
        self._background_color = color
        self._buffer.clear(color)
        self.request_render()

    def set_cursor_position(self, x: int, y: int, visible: bool = True) -> None:
        self._cursor_x = x
        self._cursor_y = y
        self._cursor_visible = visible

    def set_cursor_style(self, options: CursorStyleOptions) -> None:
        self._cursor_style = options

    def set_mouse_pointer(self, style: MousePointerStyle) -> None:
        pass

    def focus_renderable(self, renderable: Renderable) -> None:
        if self._current_focused_renderable:
            self._current_focused_renderable.blur()
        self._current_focused_renderable = renderable
        renderable.focus()

    @property
    def current_focused_renderable(self) -> Optional[Renderable]:
        return self._current_focused_renderable

    def add_to_hit_grid(self, x: int, y: int, width: int, height: int, id: int) -> None:
        pass

    def push_hit_grid_scissor_rect(self, x: int, y: int, width: int, height: int) -> None:
        pass

    def pop_hit_grid_scissor_rect(self) -> None:
        pass

    def clear_hit_grid_scissor_rects(self) -> None:
        pass

    def hit_test(self, x: int, y: int) -> int:
        return 0

    def render(self) -> None:
        if not self._dirty or not self._root:
            return

        self._buffer.clear(self._background_color)

        delta_time = 0.016
        self._root.render(self._buffer, delta_time)

        self._dirty = False

    def present(self) -> None:
        """Output the buffer to the terminal."""
        output = self._buffer.render_to_string()
        output = ANSI.set_cursor_position(1, 1) + output
        self._stdout.write(output)
        self._stdout.flush()

    def read_input(self, timeout: float = 0.01) -> List[str]:
        """Read input from the terminal."""
        sequences = []

        if select.select([self._stdin], [], [], timeout)[0]:
            try:
                data = self._stdin.read(1)
                if data:
                    sequence = self._parse_sequence(data)
                    if sequence:
                        sequences.append(sequence)
            except (IOError, OSError):
                pass

        return sequences

    def _parse_sequence(self, data: str) -> Optional[str]:
        if ord(data) == 27:
            seq = data
            while select.select([self._stdin], [], [], 0.001)[0]:
                try:
                    char = self._stdin.read(1)
                    if char:
                        seq += char
                except (IOError, OSError):
                    break
            return seq

        return data if data else None

    def process_input(self) -> None:
        """Process input events."""
        sequences = self.read_input()

        for sequence in sequences:
            handled = False

            for handler in self._input_handlers:
                if handler(sequence):
                    handled = True
                    break

            if not handled:
                self._handle_sequence(sequence)

    def _handle_sequence(self, sequence: str) -> None:
        if sequence == "\x1b[A":
            self.emit("key", KeyEvent("up", sequence))
        elif sequence == "\x1b[B":
            self.emit("key", KeyEvent("down", sequence))
        elif sequence == "\x1b[C":
            self.emit("key", KeyEvent("right", sequence))
        elif sequence == "\x1b[D":
            self.emit("key", KeyEvent("left", sequence))
        elif sequence == "\r":
            self.emit("key", KeyEvent("enter", sequence))
        elif sequence == "\x7f":
            self.emit("key", KeyEvent("backspace", sequence))
        elif sequence == "\t":
            self.emit("key", KeyEvent("tab", sequence))
        elif sequence == "\x1b":
            self.emit("key", KeyEvent("escape", sequence))
        elif sequence.startswith("\x1b[M"):
            self._handle_mouse_event(sequence)
        elif len(sequence) == 1:
            self.emit("key", KeyEvent(sequence, sequence))

    def _handle_mouse_event(self, sequence: str) -> None:
        if len(sequence) < 6:
            return

        try:
            btn = ord(sequence[3]) - 32
            x = ord(sequence[4]) - 33
            y = ord(sequence[5]) - 33

            event_type = "move"
            if btn == 0:
                event_type = "down"
            elif btn == 1:
                event_type = "up"
            elif btn == 32:
                event_type = "move"
            elif btn == 64:
                event_type = "scroll"
                btn = 4
            elif btn == 65:
                event_type = "scroll"
                btn = 5

            event = MouseEvent(event_type, x, y, btn)
            self.emit("mouse", event)
        except (ValueError, IndexError):
            pass

    def run(self) -> None:
        """Main run loop."""
        self._running = True

        try:
            self.setup()

            while self._running and not self._destroyed:
                self.process_input()
                self.render()
                self.present()

                import time

                time.sleep(self._frame_time)

        finally:
            self.cleanup()

    def stop(self) -> None:
        """Stop the renderer."""
        self._running = False

    def destroy(self) -> None:
        """Destroy the renderer."""
        self._destroyed = True
        if self._root:
            self._root.destroy()
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_destroyed(self) -> bool:
        return self._destroyed


async def create_cli_renderer(**config: Any) -> CliRenderer:
    """Create a new CLI renderer."""
    width = config.get("width", 80)
    height = config.get("height", 24)

    renderer = CliRenderer(width, height)
    renderer.setup()

    return renderer
