# PyOpenTUI

A Python port of OpenTUI - a native terminal UI framework.

## Overview

PyOpenTUI is a terminal UI framework that provides a component-based architecture for building complex terminal applications. It's a pure Python implementation with no external dependencies.

## Features

- Component-based architecture with renderable elements
- Flexible layout system
- Keyboard and mouse input handling
- Color and text styling with ANSI escape codes
- Built-in components: Box, Text, ScrollBox, Input, Textarea, ScrollBar
- Event-driven rendering

## Installation

```bash
pip install pyopentui
```

Or install in development mode:

```bash
pip install -e .
```

## Quick Start

```python
from pyopentui import (
    CliRenderer,
    BoxRenderable,
    TextRenderable,
    RGBA,
)

# Create a renderer
renderer = CliRenderer(80, 24)

# Set up the terminal
renderer.setup()

# Create root and components
root = renderer.root
box = BoxRenderable(renderer, width=40, height=10, border=True)
text = TextRenderable(renderer, "Hello, World!")

# Add components
root.add(box)
box.add(text)

# Run the application
renderer.run()
```

## Components

### BoxRenderable

A container with optional border and background.

```python
box = BoxRenderable(
    renderer,
    width=40,
    height=10,
    border=True,
    border_color=RGBA.from_hex("#ffffff"),
    background_color=RGBA.from_hex("#000000"),
    title="My Box"
)
```

### TextRenderable

Display text with styling.

```python
text = TextRenderable(
    renderer,
    "Hello, World!",
    color=RGBA.from_hex("#00ff00"),
    bold=True,
    align="center"
)
```

### ScrollBox

A scrollable container.

```python
scrollbox = ScrollBox(
    renderer,
    width=20,
    height=10,
    show_scrollbar=True
)
```

### Input

Single-line text input.

```python
input_field = Input(
    renderer,
    placeholder="Enter your name...",
    max_length=50
)
```

### Textarea

Multi-line text input.

```python
textarea = Textarea(
    renderer,
    value="Initial text",
    max_lines=10
)
```

## Color System

PyOpenTUI uses RGBA colors with values from 0.0 to 1.0:

```python
from pyopentui import RGBA

# Create colors
red = RGBA.from_values(1.0, 0.0, 0.0)
green = RGBA.from_ints(0, 255, 0)
blue = RGBA.from_hex("#0000ff")

# Access components
r, g, b, a = blue.to_ints()
```

## Text Attributes

Text can be styled with attributes:

```python
from pyopentui import TextAttributes

attributes = (
    TextAttributes.BOLD | 
    TextAttributes.ITALIC | 
    TextAttributes.UNDERLINE
)
```

## Events

The renderer emits events that you can listen to:

```python
renderer.on("key", lambda event: print(f"Key pressed: {event.name}"))
renderer.on("resize", lambda w, h: print(f"Resized to {w}x{h}"))
renderer.on("mouse", lambda event: print(f"Mouse: {event.type} at {event.x},{event.y}"))
```

## Architecture

The library follows a component-based architecture:

- **Renderable**: Base class for all UI components
- **RootRenderable**: Top-level container
- **Buffer**: Terminal output buffer
- **CliRenderer**: Main renderer handling terminal I/O

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## License

MIT
