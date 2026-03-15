#!/usr/bin/env python3
"""PyOpenTUI Showcase - Demonstrates all features."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pyopentui import (
    CliRenderer,
    BoxRenderable,
    TextRenderable,
    ScrollBox,
    Input,
    Textarea,
    ScrollBar,
    RGBA,
    TextAttributes,
)


def create_demo():
    renderer = CliRenderer(100, 35)
    renderer.setup()

    root = renderer.root

    header = BoxRenderable(
        renderer,
        x=1,
        y=1,
        width=98,
        height=3,
        border=True,
        border_color=RGBA.from_hex("#00ff00"),
        background_color=RGBA.from_hex("#1a1a2e"),
    )

    title = TextRenderable(
        renderer,
        "╔══════════════════════════════════════════════════════════════════╗\n"
        "║           🎨 PyOpenTUI Showcase - All Features Demo            ║\n"
        "╚══════════════════════════════════════════════════════════════════╝",
        color=RGBA.from_hex("#00ff00"),
        bold=True,
    )

    header.add(title)
    root.add(header)

    left_panel = BoxRenderable(
        renderer,
        x=1,
        y=5,
        width=47,
        height=28,
        border=True,
        border_color=RGBA.from_hex("#ff6b6b"),
        background_color=RGBA.from_hex("#16213e"),
    )

    left_title = TextRenderable(
        renderer,
        "📦 Box Components",
        color=RGBA.from_hex("#ff6b6b"),
        bold=True,
    )
    left_panel.add(left_title)

    box1 = BoxRenderable(
        renderer,
        x=2,
        y=3,
        width=20,
        height=6,
        border=True,
        border_color=RGBA.from_hex("#4ecdc4"),
        background_color=RGBA.from_hex("#1a1a2e"),
        title="Simple Box",
    )
    box1_text = TextRenderable(
        renderer,
        "Box with border\nand title!",
        color=RGBA.from_hex("#4ecdc4"),
    )
    box1.add(box1_text)
    left_panel.add(box1)

    box2 = BoxRenderable(
        renderer,
        x=24,
        y=3,
        width=20,
        height=6,
        border=True,
        border_color=RGBA.from_hex("#ffe66d"),
        background_color=RGBA.from_hex("#1a1a2e"),
    )
    box2_text = TextRenderable(
        renderer,
        "Colored Box\nYellow border\nDark bg",
        color=RGBA.from_hex("#ffe66d"),
    )
    box2.add(box2_text)
    left_panel.add(box2)

    box3 = BoxRenderable(
        renderer,
        x=2,
        y=11,
        width=20,
        height=8,
        border=True,
        border_color=RGBA.from_hex("#95e1d3"),
        background_color=RGBA.from_hex("#0f0f23"),
    )
    box3_title = TextRenderable(
        renderer,
        "Text Styles",
        color=RGBA.from_hex("#95e1d3"),
        bold=True,
    )
    box3.add(box3_title)

    bold_text = TextRenderable(
        renderer,
        "This is BOLD text",
        color=RGBA.from_hex("#ffffff"),
        bold=True,
    )
    box3.add(bold_text)

    italic_text = TextRenderable(
        renderer,
        "This is italic text",
        color=RGBA.from_hex("#aaaaaa"),
        italic=True,
    )
    box3.add(italic_text)

    underline_text = TextRenderable(
        renderer,
        "This is underline",
        color=RGBA.from_hex("#666666"),
        underline=True,
    )
    box3.add(underline_text)

    left_panel.add(box3)

    input_box = BoxRenderable(
        renderer,
        x=24,
        y=11,
        width=20,
        height=8,
        border=True,
        border_color=RGBA.from_hex("#a8e6cf"),
        background_color=RGBA.from_hex("#1a1a2e"),
        title="Input",
    )

    input_field = Input(
        renderer,
        placeholder="Type here...",
        max_length=15,
    )
    input_box.add(input_field)

    right_box = TextRenderable(
        renderer,
        "Input focused!",
        color=RGBA.from_hex("#a8e6cf"),
    )
    input_box.add(right_box)
    left_panel.add(input_box)

    root.add(left_panel)

    right_panel = BoxRenderable(
        renderer,
        x=50,
        y=5,
        width=49,
        height=28,
        border=True,
        border_color=RGBA.from_hex("#6c5ce7"),
        background_color=RGBA.from_hex("#16213e"),
    )

    right_title = TextRenderable(
        renderer,
        "📝 Text & Components",
        color=RGBA.from_hex("#6c5ce7"),
        bold=True,
    )
    right_panel.add(right_title)

    colors_box = BoxRenderable(
        renderer,
        x=2,
        y=3,
        width=44,
        height=8,
        border=True,
        border_color=RGBA.from_hex("#fd79a8"),
        background_color=RGBA.from_hex("#1a1a2e"),
        title="Color Palette",
    )

    colors = [
        ("#ff6b6b", "Red"),
        ("#4ecdc4", "Cyan"),
        ("#ffe66d", "Yellow"),
        ("#95e1d3", "Mint"),
        ("#a8e6cf", "Green"),
        ("#6c5ce7", "Purple"),
    ]

    for i, (color, name) in enumerate(colors):
        x_pos = 2 + (i % 3) * 14
        y_pos = 2 + (i // 3) * 3

        color_box = BoxRenderable(
            renderer,
            x=x_pos,
            y=y_pos,
            width=12,
            height=2,
            background_color=RGBA.from_hex(color),
        )
        color_text = TextRenderable(
            renderer,
            name,
            color=RGBA.from_hex("#000000"),
            bold=True,
        )
        color_box.add(color_text)
        colors_box.add(color_box)

    right_panel.add(colors_box)

    scrollbox = ScrollBox(
        renderer,
        x=2,
        y=13,
        width=20,
        height=7,
    )

    for i in range(15):
        line = TextRenderable(
            renderer,
            f"Scroll line {i + 1}",
            color=RGBA.from_hex("#6c5ce7" if i % 2 == 0 else "#a29bfe"),
        )
        scrollbox.add(line)

    right_panel.add(scrollbox)

    scrollbar = ScrollBar(
        renderer,
        x=23,
        y=13,
        height=7,
        value=50,
        max_value=100,
    )
    right_panel.add(scrollbar)

    textarea_box = BoxRenderable(
        renderer,
        x=27,
        y=13,
        width=19,
        height=7,
        border=True,
        border_color=RGBA.from_hex("#00b894"),
        background_color=RGBA.from_hex("#1a1a2e"),
        title="Textarea",
    )

    textarea = Textarea(
        renderer,
        value="Multi-line\ntext input\nwidget here!",
    )
    textarea_box.add(textarea)
    right_panel.add(textarea_box)

    root.add(right_panel)

    footer = BoxRenderable(
        renderer,
        x=1,
        y=33,
        width=98,
        height=1,
        background_color=RGBA.from_hex("#0f0f23"),
    )

    footer_text = TextRenderable(
        renderer,
        "↑↓←→ Navigate  |  Type in input  |  Press ESC to exit",
        color=RGBA.from_hex("#666666"),
    )
    footer.add(footer_text)
    root.add(footer)

    def on_key(event):
        if event.name == "escape":
            renderer.stop()
            return True
        return False

    renderer.on("key", on_key)

    return renderer


def main():
    demo = create_demo()

    try:
        demo.run()
    except KeyboardInterrupt:
        pass
    finally:
        demo.cleanup()
        print("\n\nThanks for trying PyOpenTUI! 🚀")


if __name__ == "__main__":
    main()
