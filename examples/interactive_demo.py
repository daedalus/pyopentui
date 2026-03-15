#!/usr/bin/env python3
"""PyOpenTUI Interactive Showcase using new native terminal renderer."""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pyopentui import CliRenderer, BoxRenderable, TextRenderable, Input, Textarea, RGBA
from pyopentui.renderer import KeyEvent


def main():
    renderer = CliRenderer()

    terminal = renderer._terminal
    terminal.make_nonblocking()

    try:
        renderer.setup()

        root = renderer.root

        # Header - full width, fixed height
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
            "PyOpenTUI Interactive Demo - Press ESC to quit",
            color=RGBA.from_hex("#00ff00"),
            bold=True,
        )
        header.add(title)
        root.add(header)

        # Input box for typing - left side
        input_box = BoxRenderable(
            renderer,
            x=1,
            y=4,
            width="40%",
            height="50%",
            border=True,
            border_color=RGBA.from_hex("#4ecdc4"),
            background_color=RGBA.from_hex("#16213e"),
            title="Type here",
        )
        input_field = Input(
            renderer,
            x=1,
            y=1,
            placeholder="Type text and press Enter...",
            max_length=30,
        )
        input_box.add(input_field)
        root.add(input_box)
        input_field.focus()

        # Output text area - right side
        output_box = BoxRenderable(
            renderer,
            x="45%",
            y=4,
            width="54%",
            height="80%",
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
            placeholder="Entered text will appear here...",
        )
        output_box.add(output_text)
        root.add(output_box)

        # Second input box - below first
        input_box2 = BoxRenderable(
            renderer,
            x=1,
            y="56%",
            width="40%",
            height="24%",
            border=True,
            border_color=RGBA.from_hex("#ff6b6b"),
            background_color=RGBA.from_hex("#16213e"),
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

        # Collect all focusable elements
        focusables = [input_field, input_field2]
        current_focus = 0

        # Instructions - bottom
        instructions = BoxRenderable(
            renderer,
            x=1,
            y="92%",
            width="98%",
            height=3,
            border=True,
            border_color=RGBA.from_hex("#6c5ce7"),
            background_color=RGBA.from_hex("#16213e"),
            title="Controls",
        )
        inst_text = TextRenderable(
            renderer,
            "TYPE: Add text | ENTER: Append to history | TAB: Switch focus | ESC: Quit",
            color=RGBA.from_hex("#aaaaaa"),
        )
        instructions.add(inst_text)
        root.add(instructions)

        # Initial render
        renderer.request_render()
        renderer.render()
        renderer.present()

        # Run loop
        while renderer.is_running:
            # Check for terminal resize
            new_width, new_height = terminal.get_size()
            if new_width != renderer.width or new_height != renderer.height:
                renderer._width = new_width
                renderer._height = new_height
                renderer._buffer = type(renderer._buffer)(new_width, new_height)
                if renderer._root:
                    renderer._root._width = new_width
                    renderer._root._height = new_height
                renderer.request_render()

            key = terminal.read_key(0.02)

            if key:
                name = key.get("name", "")
                raw = key.get("raw", "")

                if name == "escape":
                    renderer.stop()
                elif name == "tab":
                    # Switch focus
                    focusables[current_focus].blur()
                    current_focus = (current_focus + 1) % len(focusables)
                    focusables[current_focus].focus()
                    renderer.request_render()
                elif name == "enter":
                    # Append input value to output
                    text = input_field.value
                    if text:
                        current_value = output_text.value
                        if current_value:
                            output_text.value = current_value + "\n" + text
                        else:
                            output_text.value = text
                        input_field.value = ""  # Clear input
                        renderer.request_render()
                else:
                    # Pass key to focused element - convert dict to KeyEvent
                    focused = focusables[current_focus]
                    if hasattr(focused, "handle_key_press"):
                        key_event = KeyEvent(
                            name=key.get("name", ""),
                            sequence=key.get("raw", ""),
                        )
                        handled = focused.handle_key_press(key_event)
                        if handled:
                            renderer.request_render()

            if renderer._dirty:
                renderer.render()
                renderer.present()

            time.sleep(0.05)

    except KeyboardInterrupt:
        pass
    finally:
        renderer.cleanup()
        try:
            import subprocess

            subprocess.run(
                ["stty", "sane"],
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=subprocess.DEVNULL,
                timeout=1,
            )
        except:
            pass
        print("\nThanks for trying PyOpenTUI!")
        sys.stdout.flush()
        sys.stderr.flush()


if __name__ == "__main__":
    main()
