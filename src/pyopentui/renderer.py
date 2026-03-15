"""
Native terminal renderer for PyOpenTUI.
Works in SSH, hardware TTY, and all terminal environments.
"""

from __future__ import annotations
import sys
import os
import signal
from typing import Any, Callable, Dict, List, Optional

from .ansi import ANSI
from .buffer import Buffer, OptimizedBuffer
from .renderable import Renderable, RootRenderable
from .types import RGBA, CursorStyleOptions


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


class NativeCliRenderer:
    """CLI renderer using native terminal bindings - works in SSH."""

    def __init__(
        self,
        width: int = 80,
        height: int = 24,
        stdin=None,
        stdout=None,
    ):
        from .terminal import Terminal, InputReader, detect_ssh, get_terminal_size

        self._width = width
        self._height = height

        # Use terminal size if available
        w, h = get_terminal_size()
        if w > 0 and h > 0:
            self._width = w
            self._height = h

        self._stdin = stdin or sys.stdin
        self._stdout = stdout or sys.stdout

        # Use native terminal
        self._terminal = Terminal(self._stdin, self._stdout)
        self._input_reader = InputReader(self._terminal)

        self._running = False
        self._destroyed = False
        self._dirty = True

        self._buffer = OptimizedBuffer(self._width, self._height)
        self._next_buffer = OptimizedBuffer(self._width, self._height)
        self._last_frame_content: Optional[str] = None
        self._last_buffer_hash: Optional[int] = None

        self._background_color = RGBA.from_values(0, 0, 0, 1)
        self._root: Optional[RootRenderable] = None

        self._listeners: Dict[str, List[Callable]] = {}
        self._input_handlers: List[Callable[[str], bool]] = []

        self._target_fps = 30
        self._frame_time = 1.0 / self._target_fps

        self._use_alternate_screen = True
        self._use_mouse = True

        # Detect SSH
        self._is_ssh = detect_ssh()

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

    def on(self, event: str, callback: Callable) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def off(self, event: str, callback: Callable) -> None:
        if event in self._listeners:
            self._listeners[event] = [cb for cb in self._listeners[event] if cb != callback]

    def emit(self, event: str, *args, **kwargs) -> None:
        if event in self._listeners:
            for cb in self._listeners[event]:
                cb(*args, **kwargs)

    def add_input_handler(self, handler: Callable[[str], bool]) -> None:
        self._input_handlers.append(handler)

    def remove_input_handler(self, handler: Callable[[str], bool]) -> None:
        self._input_handlers = [h for h in self._input_handlers if h != handler]

    def request_render(self) -> None:
        self._dirty = True

    def setup(self) -> None:
        """Set up terminal for rendering."""
        # Try to set up raw mode, but continue even if it fails
        self._terminal.setup()

        if self._use_alternate_screen:
            self._terminal.enter_alternate_screen()

        if self._use_mouse:
            self._terminal.enable_mouse_tracking()

        self._terminal.hide_cursor()
        self._terminal.clear_screen()
        self._terminal.home_cursor()

        self._root = RootRenderable(self, self._width, self._height)

        # Mark as running so the loop will execute
        self._running = True

    def cleanup(self) -> None:
        """Clean up terminal after rendering."""
        self._terminal.set_cursor(1, 1)
        self._terminal.show_cursor()

        if self._use_alternate_screen:
            self._terminal.exit_alternate_screen()

        if self._use_mouse:
            self._terminal.disable_mouse_tracking()

        self._terminal.reset()
        self._terminal.cleanup()

    def render(self) -> None:
        if not self._dirty or not self._root:
            return

        self._buffer.clear(self._background_color)

        delta_time = 0.016
        self._root.render(self._buffer, delta_time)

        self._dirty = False

    def present(self) -> None:
        """Output the buffer to the terminal only if content changed."""
        buffer_content = self._buffer.render_to_string()

        # Only output if content changed
        if buffer_content != self._last_frame_content:
            self._last_frame_content = buffer_content
            output = ANSI.set_cursor_position(1, 1) + buffer_content
            self._terminal.write(output)

    def process_input(self) -> None:
        """Process input events."""
        key = self._input_reader.read_key()

        if key:
            event = KeyEvent(
                name=key.get("name", "unknown"),
                sequence=key.get("raw", ""),
            )

            # Check handlers
            for handler in self._input_handlers:
                if handler(key.get("raw", "")):
                    return

            # Emit key event
            self.emit("key", event)

            # Handle special keys
            if key.get("name") == "escape":
                self.emit("escape")
            elif key.get("name") == "enter":
                self.emit("enter")
            elif key.get("name") == "backspace":
                self.emit("backspace")
            elif key.get("name") == "up":
                self.emit("up")
            elif key.get("name") == "down":
                self.emit("down")
            elif key.get("name") == "left":
                self.emit("left")
            elif key.get("name") == "right":
                self.emit("right")

    def _handle_resize(self, signum=None, frame=None) -> None:
        """Handle terminal resize."""
        new_width, new_height = self._terminal.get_size()
        if new_width != self._width or new_height != self._height:
            self._width = new_width
            self._height = new_height
            self._buffer = OptimizedBuffer(self._width, self._height)
            if self._root:
                self._root._width = new_width
                self._root._height = new_height
            self._dirty = True

    def run(self) -> None:
        """Main run loop."""
        self._running = True

        old_handler = None
        if hasattr(signal, "SIGWINCH"):
            old_handler = signal.signal(signal.SIGWINCH, self._handle_resize)

        try:
            self.setup()
            self._handle_resize()

            while self._running and not self._destroyed:
                self.process_input()

                if self._dirty:
                    self.render()
                    self.present()

                import time

                time.sleep(self._frame_time)

        finally:
            if old_handler is not None:
                signal.signal(signal.SIGWINCH, old_handler)
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


try:
    import curses
    import threading

    class CursesRenderer:
        """CLI renderer using curses library - works in SSH and provides native terminal handling."""

        def __init__(self, width: int = 80, height: int = 24):
            self._width = width
            self._height = height
            self._running = False
            self._destroyed = False
            self._dirty = True
            self._background_color = RGBA.from_values(0, 0, 0, 1)
            self._root: Optional[RootRenderable] = None
            self._buffer = OptimizedBuffer(self._width, self._height)
            self._listeners: Dict[str, List[Callable]] = {}
            self._input_handlers: List[Callable[[str], bool]] = []
            self._target_fps = 30
            self._frame_time = 1.0 / self._target_fps
            self._curses_window = None
            self._thread: Optional[threading.Thread] = None
            self._colors_cache: Dict[tuple, int] = {}

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

        def on(self, event: str, callback: Callable) -> None:
            if event not in self._listeners:
                self._listeners[event] = []
            self._listeners[event].append(callback)

        def off(self, event: str, callback: Callable) -> None:
            if event in self._listeners:
                self._listeners[event] = [cb for cb in self._listeners[event] if cb != callback]

        def emit(self, event: str, *args, **kwargs) -> None:
            if event in self._listeners:
                for cb in self._listeners[event]:
                    cb(*args, **kwargs)

        def add_input_handler(self, handler: Callable[[str], bool]) -> None:
            self._input_handlers.append(handler)

        def remove_input_handler(self, handler: Callable[[str], bool]) -> None:
            self._input_handlers = [h for h in self._input_handlers if h != handler]

        def request_render(self) -> None:
            self._dirty = True

        def setup(self) -> None:
            self._root = RootRenderable(self, self._width, self._height)
            self._running = True

        def cleanup(self) -> None:
            self._running = False

        def _init_curses(self, stdscr) -> None:
            curses.curs_set(0)
            stdscr.nodelay(True)
            stdscr.keypad(True)
            curses.start_color()
            curses.use_default_colors()
            self._colors_cache = {}

        def _get_color(self, fg: RGBA, bg: RGBA) -> int:
            key = (fg.r, fg.g, fg.b, bg.r, bg.g, bg.b)
            if key in self._colors_cache:
                return self._colors_cache[key]

            color_id = len(self._colors_cache) + 1
            if color_id < curses.COLORS:
                r, g, b = int(fg.r * 255), int(fg.g * 255), int(fg.b * 255)
                curses.init_color(color_id, r, g, b)
                bg_r, bg_g, bg_b = int(bg.r * 255), int(bg.g * 255), int(bg.b * 255)
                bg_color_id = color_id + 100
                if bg_color_id < curses.COLORS:
                    curses.init_color(bg_color_id, bg_r, bg_g, bg_b)
                pair_id = color_id
                curses.init_pair(pair_id, color_id, -1)
                self._colors_cache[key] = curses.color_pair(pair_id)
                return curses.color_pair(pair_id)
            return 0

        def render(self) -> None:
            if not self._dirty or not self._root:
                return

            self._buffer.clear(self._background_color)
            delta_time = 0.016
            self._root.render(self._buffer, delta_time)
            self._dirty = False

        def present(self) -> None:
            if not self._curses_window:
                return

            h, w = self._curses_window.getmaxyx()
            if w != self._width or h != self._height:
                self._width = w
                self._height = h
                self._buffer = OptimizedBuffer(w, h)
                if self._root:
                    self._root._width = w
                    self._root._height = h
                self._dirty = True

            for y in range(min(self._height, h - 1)):
                for x in range(min(self._width, w - 1)):
                    cell = self._buffer.get_cell(x, y)
                    if cell:
                        try:
                            char = cell.char or " "
                            fg = cell.fg or RGBA.from_values(1, 1, 1, 1)
                            bg = cell.bg or RGBA.from_values(0, 0, 0, 1)
                            color = self._get_color(fg, bg)
                            self._curses_window.addch(y, x, char, color)
                        except curses.error:
                            pass

            self._curses_window.refresh()

        def _curses_loop(self, stdscr) -> None:
            self._curses_window = stdscr
            self._init_curses(stdscr)

            try:
                if not self._root:
                    self.setup()

                while self._running and not self._destroyed:
                    try:
                        key = stdscr.getch()
                        if key != -1:
                            key_name = self._key_to_name(key)
                            raw = chr(key) if 0 <= key < 256 else ""

                            for handler in self._input_handlers:
                                if handler(raw):
                                    break
                            else:
                                event = KeyEvent(name=key_name, sequence=raw)
                                self.emit("key", event)

                                if key_name == "escape":
                                    self.emit("escape")
                                elif key_name == "enter":
                                    self.emit("enter")
                                elif key_name == "backspace":
                                    self.emit("backspace")
                                elif key_name == "up":
                                    self.emit("up")
                                elif key_name == "down":
                                    self.emit("down")
                                elif key_name == "left":
                                    self.emit("left")
                                elif key_name == "right":
                                    self.emit("right")

                    except curses.error:
                        pass

                    if self._dirty:
                        self.render()
                        self.present()

                    curses.napms(int(self._frame_time * 1000))

            finally:
                self.cleanup()

        def _key_to_name(self, key: int) -> str:
            key_map = {
                27: "escape",
                10: "enter",
                curses.KEY_ENTER: "enter",
                curses.KEY_BACKSPACE: "backspace",
                127: "backspace",
                9: "tab",
                curses.KEY_UP: "up",
                curses.KEY_DOWN: "down",
                curses.KEY_LEFT: "left",
                curses.KEY_RIGHT: "right",
                curses.KEY_HOME: "home",
                curses.KEY_END: "end",
                curses.KEY_PPAGE: "pageup",
                curses.KEY_NPAGE: "pagedown",
                curses.KEY_DC: "delete",
            }
            if key in key_map:
                return key_map[key]
            if 0 <= key < 256:
                return chr(key)
            return "unknown"

        def run(self) -> None:
            curses.wrapper(self._curses_loop)

        def stop(self) -> None:
            self._running = False

        def destroy(self) -> None:
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

except ImportError:
    CursesRenderer = None


# Alias for backward compatibility
CliRenderer = NativeCliRenderer
