#!/usr/bin/env python3
"""PyOpenTUI Interactive Showcase using new native terminal renderer."""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pyopentui import CliRenderer, BoxRenderable, TextRenderable, RGBA


def main():
    import time

    renderer = CliRenderer(80, 24)

    terminal = renderer._terminal
    terminal.make_nonblocking()

    try:
        renderer.setup()

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

        # Initial render
        renderer.request_render()
        renderer.render()
        renderer.present()

        # Run loop - use terminal.read_key for SSH-compatible input
        while renderer.is_running:
            key = terminal.read_key(0.02)

            if key:
                name = key.get("name", "")
                raw = key.get("raw", "")

                if name == "escape":
                    renderer.stop()
                elif name == "enter" or raw == " ":
                    counter += 1
                    counter_text._text = f"Count: {counter}"
                    renderer.request_render()
                elif name == "backspace" or raw == "r":
                    counter = 0
                    counter_text._text = f"Count: {counter}"
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
