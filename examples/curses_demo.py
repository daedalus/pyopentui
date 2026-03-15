#!/usr/bin/env python3
"""PyOpenTUI Curses Demo - Uses curses for terminal handling."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pyopentui import CursesRenderer, BoxRenderable, TextRenderable, Input, Textarea, RGBA, Theme
from pyopentui.renderer import KeyEvent


def main():
    renderer = CursesRenderer()

    output_text = None
    input_field = None
    input_field2 = None
    focusables = []
    current_focus = 0

    def on_key(event):
        nonlocal current_focus

        if event.name == "escape":
            renderer.stop()
            return True
        elif event.name == "tab":
            focusables[current_focus].blur()
            current_focus = (current_focus + 1) % len(focusables)
            focusables[current_focus].focus()
            renderer.request_render()
            return True
        elif event.name == "enter":
            if input_field and input_field.value:
                text = input_field.value
                if output_text.value:
                    output_text.value = output_text.value + "\n" + text
                else:
                    output_text.value = text
                input_field.value = ""
                renderer.request_render()
            return True
        else:
            focused = focusables[current_focus]
            if hasattr(focused, "handle_key_press"):
                handled = focused.handle_key_press(event)
                if handled:
                    renderer.request_render()
            return True

    renderer.on("key", on_key)

    renderer.setup()
    root = renderer.root

    header = BoxRenderable(
        renderer,
        x=0,
        y=0,
        width="100%",
        height=3,
        border=True,
        border_color=Theme.BOX_HEADER,
        background_color=Theme.BG_TERTIARY,
    )
    title = TextRenderable(
        renderer,
        "PyOpenTUI Curses Demo - Press ESC to quit",
        color=Theme.BOX_HEADER,
        bold=True,
    )
    header.add(title)
    root.add(header)

    input_box = BoxRenderable(
        renderer,
        x=1,
        y=4,
        width=40,
        height=8,
        border=True,
        border_color=Theme.BOX_INPUT,
        background_color=Theme.BG_SECONDARY,
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
    focusables.append(input_field)

    output_box = BoxRenderable(
        renderer,
        x=45,
        y=4,
        width=40,
        height=15,
        border=True,
        border_color=Theme.BOX_HISTORY,
        background_color=Theme.BG_SECONDARY,
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

    input_box2 = BoxRenderable(
        renderer,
        x=1,
        y=14,
        width=40,
        height=8,
        border=True,
        border_color=Theme.BOX_SECONDARY,
        background_color=Theme.BG_SECONDARY,
        title="Another input",
    )
    input_field2 = Input(
        renderer,
        x=1,
        y=1,
        placeholder="Tab to switch here...",
        max_length=30,
    )
    input_box2.add(input_field2)
    root.add(input_box2)
    focusables.append(input_field2)

    if focusables:
        focusables[0].focus()
        current_focus = 0

    renderer.request_render()
    renderer.run()
    print("\nThanks for trying PyOpenTUI!")


if __name__ == "__main__":
    main()
