#!/usr/bin/env python3
"""PyOpenTUI Showcase - ASCII preview of all features."""

import sys
import os
import time
import select

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

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
from pyopentui.terminal import Terminal


def render_showcase():
    buf = Buffer(100, 35)
    buf.clear(RGBA.from_hex("#0f0f23"))

    title = """
╔══════════════════════════════════════════════════════════════════╗
║           PyOpenTUI Showcase - All Features Demo            ║
╚══════════════════════════════════════════════════════════════════╝"""

    buf.write_text(1, 1, title, RGBA.from_hex("#00ff00"), attributes=TextAttributes.BOLD)

    buf.draw_frame(
        1, 7, 47, 25, "Box Components", RGBA.from_hex("#ff6b6b"), RGBA.from_hex("#16213e")
    )

    buf.draw_frame(3, 9, 18, 5, "Simple Box", RGBA.from_hex("#4ecdc4"), RGBA.from_hex("#1a1a2e"))
    buf.write_text(4, 11, "Box with border", RGBA.from_hex("#4ecdc4"))
    buf.write_text(4, 12, "and title!", RGBA.from_hex("#4ecdc4"))

    buf.draw_frame(23, 9, 18, 5, None, RGBA.from_hex("#ffe66d"), RGBA.from_hex("#1a1a2e"))
    buf.write_text(24, 11, "Colored Box", RGBA.from_hex("#ffe66d"))
    buf.write_text(24, 12, "Yellow border", RGBA.from_hex("#ffe66d"))
    buf.write_text(24, 13, "Dark bg", RGBA.from_hex("#ffe66d"))

    buf.draw_frame(3, 16, 18, 7, "Text Styles", RGBA.from_hex("#95e1d3"), RGBA.from_hex("#0f0f23"))
    buf.write_text(
        4, 18, "This is BOLD text", RGBA.from_hex("#ffffff"), attributes=TextAttributes.BOLD
    )
    buf.write_text(
        4, 19, "This is italic text", RGBA.from_hex("#aaaaaa"), attributes=TextAttributes.ITALIC
    )
    buf.write_text(
        4, 20, "This is underline", RGBA.from_hex("#666666"), attributes=TextAttributes.UNDERLINE
    )

    buf.draw_frame(23, 16, 18, 7, "Input", RGBA.from_hex("#a8e6cf"), RGBA.from_hex("#1a1a2e"))
    buf.write_text(24, 18, "┌───────────────┐", RGBA.from_hex("#a8e6cf"))
    buf.write_text(24, 19, "│ Type here... │", RGBA.from_hex("#666666"))
    buf.write_text(24, 20, "└───────────────┘", RGBA.from_hex("#a8e6cf"))
    buf.write_text(25, 21, "Input focused!", RGBA.from_hex("#a8e6cf"))

    buf.draw_frame(
        50, 7, 48, 25, "Text & Components", RGBA.from_hex("#6c5ce7"), RGBA.from_hex("#16213e")
    )

    buf.draw_frame(
        52, 9, 43, 7, "Color Palette", RGBA.from_hex("#fd79a8"), RGBA.from_hex("#1a1a2e")
    )

    colors = [
        (54, 11, "#ff6b6b", "Red"),
        (68, 11, "#4ecdc4", "Cyan"),
        (82, 11, "#ffe66d", "Yellow"),
        (54, 14, "#95e1d3", "Mint"),
        (68, 14, "#a8e6cf", "Green"),
        (82, 14, "#6c5ce7", "Purple"),
    ]
    for x, y, color, name in colors:
        buf.fill_rect(x, y, 10, 2, " ", None, RGBA.from_hex(color))
        buf.write_text(x + 1, y + 1, name, RGBA.from_hex("#000000"), attributes=TextAttributes.BOLD)

    buf.draw_frame(52, 18, 20, 8, "ScrollBox", RGBA.from_hex("#6c5ce7"), RGBA.from_hex("#1a1a2e"))
    for i in range(6):
        color = "#6c5ce7" if i % 2 == 0 else "#a29bfe"
        buf.write_text(54, 20 + i, f"  Scroll line {i + 1}", RGBA.from_hex(color))
    buf.write_text(54, 25, "  ↓ Scroll line 7", RGBA.from_hex("#a29bfe"))

    buf.set_cell(73, 18, "│", RGBA.from_hex("#6c5ce7"))
    buf.set_cell(73, 19, "│", RGBA.from_hex("#6c5ce7"))
    buf.set_cell(73, 20, "▓", RGBA.from_hex("#6c5ce7"))
    buf.set_cell(73, 21, "│", RGBA.from_hex("#6c5ce7"))
    buf.set_cell(73, 22, "│", RGBA.from_hex("#6c5ce7"))
    buf.set_cell(73, 23, "│", RGBA.from_hex("#6c5ce7"))
    buf.set_cell(73, 24, "▼", RGBA.from_hex("#6c5ce7"))

    buf.draw_frame(76, 18, 18, 8, "Textarea", RGBA.from_hex("#00b894"), RGBA.from_hex("#1a1a2e"))
    buf.write_text(78, 20, "Multi-line", RGBA.from_hex("#00b894"))
    buf.write_text(78, 21, "text input", RGBA.from_hex("#00b894"))
    buf.write_text(78, 22, "widget here!", RGBA.from_hex("#00b894"))

    buf.fill_rect(1, 33, 98, 1, " ", None, RGBA.from_hex("#0f0f23"))
    buf.write_text(
        1, 33, "↑↓←→ Navigate  |  Type in input  |  Press ESC to exit", RGBA.from_hex("#666666")
    )

    return buf


def main():
    term = Terminal()

    # Set up screen using library methods
    term.setup_screen(15, 15, 35)

    buf = render_showcase()
    output = buf.render_to_string()
    term.write(output)
    term.flush()

    # Wait for user input or timeout
    try:
        if select.select([sys.stdin], [], [], 3)[0]:
            sys.stdin.read(1)
    except:
        time.sleep(5)

    # Restore screen using library method
    term.restore_screen()
    term.flush()


if __name__ == "__main__":
    main()
