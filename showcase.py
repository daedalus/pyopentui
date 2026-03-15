#!/usr/bin/env python3
"""PyOpenTUI Interactive Showcase using new native terminal renderer."""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pyopentui import CliRenderer, BoxRenderable, TextRenderable, RGBA


def main():
    import os

    os.write(1, b"Creating renderer...\n")
    renderer = CliRenderer(80, 24)
    os.write(1, b"Renderer created\n")

    try:
        os.write(1, b"Setting up renderer...\n")
        renderer.setup()
        os.write(1, b"Setup complete, adding elements...\n")

        root = renderer.root

        root = renderer.root

        # Header
        header = BoxRenderable(
            renderer,
            x=1,
            y=1,
            width=78,
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

        # Counter
        counter = 0
        counter_box = BoxRenderable(
            renderer,
            x=25,
            y=8,
            width=30,
            height=8,
            border=True,
            border_color=RGBA.from_hex("#ff6b6b"),
            background_color=RGBA.from_hex("#16213e"),
            title="Counter",
        )

        counter_text = TextRenderable(
            renderer,
            f"Count: {counter}",
            color=RGBA.from_hex("#ffffff"),
            bold=True,
        )
        counter_box.add(counter_text)
        root.add(counter_box)

        # Instructions
        instructions = BoxRenderable(
            renderer,
            x=10,
            y=18,
            width=60,
            height=4,
            border=True,
            border_color=RGBA.from_hex("#6c5ce7"),
            background_color=RGBA.from_hex("#16213e"),
            title="Controls",
        )

        inst_text = TextRenderable(
            renderer,
            "SPACE/ENTER: Increment | R: Reset | ESC: Quit",
            color=RGBA.from_hex("#aaaaaa"),
        )
        instructions.add(inst_text)
        root.add(instructions)

        # Key handler
        def on_key(event):
            nonlocal counter
            if event.name == "escape":
                renderer.stop()
                return True
            elif event.name == "enter" or event.sequence == " ":
                counter += 1
                counter_text._text = f"Count: {counter}"
            elif event.name == "backspace" or event.sequence == "r":
                counter = 0
                counter_text._text = f"Count: {counter}"
            return True

        renderer.on("key", on_key)

        # Run loop
        os.write(1, b"Starting run loop...\n")
        os.write(1, f"is_running = {renderer.is_running}\n".encode())

        while renderer.is_running:
            os.write(1, b"In loop...\n")
            renderer.process_input()
            renderer.render()
            renderer.present()
            import time

            time.sleep(0.05)

    except KeyboardInterrupt:
        os.write(1, b"KeyboardInterrupt\n")
        pass
    except Exception as e:
        os.write(1, f"Exception: {e}\n".encode())
        import traceback

        traceback.print_exc()
    finally:
        os.write(1, b"Cleaning up...\n")
        renderer.cleanup()
        os.write(1, b"\nThanks for trying PyOpenTUI!\n")


if __name__ == "__main__":
    main()
