"""
Native terminal renderer for PyOpenTUI.
Works in SSH, hardware TTY, and all terminal environments.
"""

from __future__ import annotations
import sys
import os
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
        output = ANSI.set_cursor_position(1, 1) + self._buffer.render_to_string()

        # Only output if content changed
        if output != self._last_frame_content:
            self._last_frame_content = output
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

    def run(self) -> None:
        """Main run loop."""
        self._running = True

        try:
            self.setup()

            while self._running and not self._destroyed:
                self.process_input()

                if self._dirty:
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


# Alias for backward compatibility
CliRenderer = NativeCliRenderer
