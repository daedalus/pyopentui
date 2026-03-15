#!/usr/bin/env python3
"""Minimal PyOpenTUI test."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pyopentui import CliRenderer, BoxRenderable, TextRenderable, RGBA


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

        # Force render
        renderer._dirty = True
        renderer.render()
        renderer.present()

        # Keep running
        import time

        for _ in range(100):
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        renderer.cleanup()
        print("\nDone!")


if __name__ == "__main__":
    main()
