#!/usr/bin/env python3
"""PyOpenTUI Curses Demo - Uses curses for terminal handling."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pyopentui import CursesRenderer, BoxRenderable, TextRenderable, Input, Textarea, RGBA


def main():
    renderer = CursesRenderer()

    renderer.on("key", lambda e: handle_key(renderer, e))
    renderer.on("escape", lambda: renderer.stop())

    renderer.setup()
    root = renderer.root

    header = BoxRenderable(
        renderer,
        x=0,
        y=0,
        width="100%",
        height=3,
        border=True,
        border_color=RGBA.from_hex("#00ff00"),
        background_color=RGBA.from_hex("#1a1a2e"),
    )
    title = TextRenderable(
        renderer,
        "PyOpenTUI Curses Demo - Press ESC to quit",
        color=RGBA.from_hex("#00ff00"),
        bold=True,
    )
    header.add(title)
    root.add(header)

    input_box = BoxRenderable(
        renderer,
        x=1,
        y=4,
        width="40%",
        height=8,
        border=True,
        border_color=RGBA.from_hex("#4ecdc4"),
        background_color=RGBA.from_hex("#16213e"),
        title="Type here",
    )
    input_field = Input(
        renderer,
        x=1,
        y=1,
        placeholder="Type and press Enter...",
        max_length=30,
    )
    input_box.add(input_field)
    root.add(input_box)
    input_field.focus()

    output_box = BoxRenderable(
        renderer,
        x=45,
        y=4,
        width=40,
        height=15,
        border=True,
        border_color=RGBA.from_hex("#ffe66d"),
        background_color=RGBA.from_hex("#16213e"),
        title="History",
    )
    output_text = Textarea(
        renderer,
        x=1,
        y=1,
        value="",
        placeholder="Entered text appears here...",
    )
    output_box.add(output_text)
    root.add(output_box)

    focusables = [input_field]
    current_focus = 0

    renderer.request_render()
    renderer.run()


def handle_key(renderer, event):
    pass


if __name__ == "__main__":
    main()
