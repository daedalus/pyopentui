#!/usr/bin/env python3
"""Minimal PyOpenTUI test."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pyopentui import CliRenderer, BoxRenderable, TextRenderable, RGBA
from pyopentui.ansi import ANSI


def main():
    if not sys.stdin.isatty():
        print("Error: Need terminal")
        sys.exit(1)

    renderer = CliRenderer(40, 12)

    try:
        renderer.setup()

        root = renderer.root

        # Simple box
        box = BoxRenderable(
            renderer,
            x=5,
            y=3,
            width=30,
            height=6,
            border=True,
            border_color=RGBA.from_hex("#00ff00"),
            background_color=RGBA.from_hex("#1a1a2e"),
        )

        text = TextRenderable(
            renderer,
            "Hello PyOpenTUI!",
            color=RGBA.from_hex("#ffffff"),
            bold=True,
        )
        box.add(text)
        root.add(box)

        # Handle ESC to quit
        def on_key(event):
            if event.name == "escape":
                renderer.stop()
                return True
            return False

        renderer.on("key", on_key)

        # Render loop - keep rendering until ESC
        while renderer.is_running:
            renderer.process_input()
            renderer._dirty = True  # Force render for testing
            renderer.render()
            renderer.present()
            import time

            time.sleep(0.033)  # ~30fps

    except KeyboardInterrupt:
        pass
    finally:
        renderer.cleanup()
        print("\nDone!")


if __name__ == "__main__":
    main()
