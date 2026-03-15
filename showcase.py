#!/usr/bin/env python3
"""PyOpenTUI Interactive Showcase - Works in SSH."""

import sys
import os
import time
import select

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pyopentui import (
    BoxRenderable,
    TextRenderable,
    ScrollBox,
    Input,
    Textarea,
    ScrollBar,
    RGBA,
    TextAttributes,
)
from pyopentui.buffer import Buffer
from pyopentui.renderable import RootRenderable
from pyopentui.ansi import ANSI


class SimpleTUI:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buf = Buffer(width, height)
        self.running = False

        class MockCtx:
            def __init__(self, w, h):
                self.width = w
                self.height = h
                self._background_color = RGBA.from_hex("#0f0f23")

            def request_render(self):
                pass

            def focus(self, r):
                pass

            def blur(self):
                pass

            def emit(self, name, data):
                pass

        self.ctx = MockCtx(width, height)
        self.root = RootRenderable(self.ctx, width, height)

    def start(self):
        self.running = True

        # Enable alternate screen
        sys.stdout.write("\033[?1049h")
        sys.stdout.write(ANSI.clear_screen())
        sys.stdout.flush()

        self._setup_ui()

        while self.running:
            self._process_input()
            self._render()
            time.sleep(0.05)  # ~20fps

        self._cleanup()

    def _setup_ui(self):
        header = BoxRenderable(
            self.ctx,
            x=1,
            y=1,
            width=98,
            height=3,
            border=True,
            border_color=RGBA.from_hex("#00ff00"),
            background_color=RGBA.from_hex("#1a1a2e"),
        )
        title = TextRenderable(
            self.ctx,
            "PyOpenTUI Interactive Demo",
            color=RGBA.from_hex("#00ff00"),
            bold=True,
        )
        header.add(title)
        self.root.add(header)

        self.counter = 0
        self.counter_text = None

        counter_box = BoxRenderable(
            self.ctx,
            x=35,
            y=10,
            width=30,
            height=8,
            border=True,
            border_color=RGBA.from_hex("#ff6b6b"),
            background_color=RGBA.from_hex("#16213e"),
            title="Counter",
        )

        self.counter_text = TextRenderable(
            self.ctx,
            "Count: 0",
            color=RGBA.from_hex("#ffffff"),
            bold=True,
        )
        counter_box.add(self.counter_text)
        self.root.add(counter_box)

        self.key_label = TextRenderable(
            self.ctx,
            "Last key: None",
            color=RGBA.from_hex("#aaaaaa"),
        )
        self.root.add(self.key_label)

    def _process_input(self):
        try:
            if select.select([sys.stdin], [], [], 0.01)[0]:
                ch = sys.stdin.read(1)
                if ch:
                    self._handle_key(ch)
        except:
            pass

    def _handle_key(self, ch):
        if ch == "q" or ch == "\x1b":  # q or ESC
            self.running = False
        elif ch == " " or ch == "\n":  # Space or Enter
            self.counter += 1
            self.counter_text._text = f"Count: {self.counter}"
        elif ch == "r":
            self.counter = 0
            self.counter_text._text = f"Count: {self.counter}"

        self.key_label._text = f"Last key: {repr(ch)}"

    def _render(self):
        self.buf.clear(RGBA.from_hex("#0f0f23"))
        self.root.render(self.buf, 0.016)

        output = ANSI.set_cursor_position(1, 1) + self.buf.render_to_string()
        sys.stdout.write(output)
        sys.stdout.flush()

    def _cleanup(self):
        sys.stdout.write(ANSI.set_cursor_position(1, 1))
        sys.stdout.write("\n\n\033[0m")
        sys.stdout.write("\033[?1049l")
        sys.stdout.flush()
        print("Thanks for trying PyOpenTUI!")


def main():
    if not sys.stdin.isatty():
        print("Error: Need interactive terminal")
        sys.exit(1)

    tui = SimpleTUI(100, 35)
    tui.start()


if __name__ == "__main__":
    main()
