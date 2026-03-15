"""Built-in renderable components."""

from __future__ import annotations
from typing import Any, Callable, List, Optional

from .buffer import Buffer
from .renderable import Renderable
from .types import RGBA, TextAttributes


class BoxRenderable(Renderable):
    """A box container with optional border and background."""

    def __init__(
        self,
        ctx: Any,
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
        border: bool = False,
        border_color: Optional[RGBA] = None,
        background_color: Optional[RGBA] = None,
        title: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, width=width, height=height, **kwargs)

        self._border = border
        self._border_color = border_color or RGBA.from_values(1, 1, 1, 1)
        self._background_color = background_color
        self._title = title

    def render_self(self, buffer: Buffer, delta_time: float) -> None:
        if self._background_color:
            buffer.fill_rect(
                self.x,
                self.y,
                self.width,
                self.height,
                " ",
                self._border_color,
                self._background_color,
            )

        if self._border and self.width > 1 and self.height > 1:
            buffer.draw_frame(
                self.x,
                self.y,
                self.width,
                self.height,
                self._title,
                self._border_color,
                self._background_color,
            )


class TextRenderable(Renderable):
    """A text display component."""

    def __init__(
        self,
        ctx: Any,
        text: str = "",
        *,
        color: Optional[RGBA] = None,
        background_color: Optional[RGBA] = None,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        align: str = "left",
        wrap: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, **kwargs)

        self._text = text
        self._color = color or RGBA.from_values(1, 1, 1, 1)
        self._background_color = background_color
        self._bold = bold
        self._italic = italic
        self._underline = underline
        self._align = align
        self._wrap = wrap

        self._calculate_size()

    def _calculate_size(self) -> None:
        if self._text:
            lines = self._text.split("\n")
            max_width = max(len(line) for line in lines)
            self._width_value = max_width
            self._height_value = len(lines)
        else:
            self._width_value = 0
            self._height_value = 0

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        self._calculate_size()
        self.request_render()

    def render_self(self, buffer: Buffer, delta_time: float) -> None:
        if not self._text:
            return

        attributes = TextAttributes.NONE
        if self._bold:
            attributes |= TextAttributes.BOLD
        if self._italic:
            attributes |= TextAttributes.ITALIC
        if self._underline:
            attributes |= TextAttributes.UNDERLINE

        lines = self._text.split("\n")

        for i, line in enumerate(lines):
            if self.y + i >= buffer.height:
                break

            x_offset = 0
            if self._align == "center":
                x_offset = (self.width - len(line)) // 2
            elif self._align == "right":
                x_offset = self.width - len(line)

            buffer.write_text(
                self.x + max(0, x_offset),
                self.y + i,
                line,
                self._color,
                self._background_color,
                attributes,
            )


class ScrollBox(Renderable):
    """A scrollable box container."""

    def __init__(
        self,
        ctx: Any,
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
        scroll_x: int = 0,
        scroll_y: int = 0,
        show_scrollbar: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, width=width, height=height, overflow="hidden", **kwargs)

        self._scroll_x = scroll_x
        self._scroll_y = scroll_y
        self._show_scrollbar = show_scrollbar
        self._content_width = 0
        self._content_height = 0

    @property
    def scroll_x(self) -> int:
        return self._scroll_x

    @scroll_x.setter
    def scroll_x(self, value: int) -> None:
        self._scroll_x = max(0, value)
        self.request_render()

    @property
    def scroll_y(self) -> int:
        return self._scroll_y

    @scroll_y.setter
    def scroll_y(self, value: int) -> None:
        self._scroll_y = max(0, value)
        self.request_render()

    def scroll_to(self, x: int, y: int) -> None:
        self._scroll_x = max(0, x)
        self._scroll_y = max(0, y)
        self.request_render()

    def on_mouse_event(self, event: Any) -> None:
        if event.type == "scroll":
            if event.button == 4:
                self.scroll_y = max(0, self._scroll_y - 1)
            elif event.button == 5:
                self.scroll_y += 1


class Input(Renderable):
    """A text input component."""

    def __init__(
        self,
        ctx: Any,
        *,
        placeholder: str = "",
        value: str = "",
        max_length: Optional[int] = None,
        password: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, **kwargs)

        self._placeholder = placeholder
        self._value = value
        self._max_length = max_length
        self._password = password
        self._cursor_position = len(value)
        self._focusable = True

        self._calculate_size()

    def _calculate_size(self) -> None:
        display_text = self._value if not self._password else "*" * len(self._value)
        self._width_value = max(len(self._placeholder), len(display_text), 1)
        self._height_value = 1

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        if self._max_length:
            value = value[: self._max_length]
        self._value = value
        self._cursor_position = min(self._cursor_position, len(value))
        self._calculate_size()
        self.request_render()

    def render_self(self, buffer: Buffer, delta_time: float) -> None:
        display_text = self._value if not self._password else "*" * len(self._value)

        if not display_text:
            buffer.write_text(self.x, self.y, self._placeholder, RGBA.from_values(0.5, 0.5, 0.5, 1))
        else:
            buffer.write_text(self.x, self.y, display_text, RGBA.from_values(1, 1, 1, 1))

    def handle_key_press(self, key: Any) -> bool:
        if key.name == "backspace":
            if self._cursor_position > 0:
                self._value = (
                    self._value[: self._cursor_position - 1] + self._value[self._cursor_position :]
                )
                self._cursor_position -= 1
            return True
        elif key.name == "left":
            self._cursor_position = max(0, self._cursor_position - 1)
            return True
        elif key.name == "right":
            self._cursor_position = min(len(self._value), self._cursor_position + 1)
            return True
        elif key.name == "home":
            self._cursor_position = 0
            return True
        elif key.name == "end":
            self._cursor_position = len(self._value)
            return True
        elif len(key.sequence) == 1:
            new_value = (
                self._value[: self._cursor_position]
                + key.sequence
                + self._value[self._cursor_position :]
            )
            if not self._max_length or len(new_value) <= self._max_length:
                self._value = new_value
                self._cursor_position += 1
            return True

        return False


class Textarea(Renderable):
    """A multi-line text input component."""

    def __init__(
        self,
        ctx: Any,
        *,
        value: str = "",
        placeholder: str = "",
        max_lines: Optional[int] = None,
        line_wrap: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, **kwargs)

        self._value = value
        self._placeholder = placeholder
        self._max_lines = max_lines
        self._line_wrap = line_wrap
        self._cursor_line = 0
        self._cursor_col = 0
        self._focusable = True

        self._calculate_size()

    def _calculate_size(self) -> None:
        lines = self._value.split("\n")
        if self._max_lines:
            lines = lines[: self._max_lines]

        max_width = max(len(line) for line in lines) if lines else 0
        self._width_value = max(max_width, len(self._placeholder), 1)
        self._height_value = max(len(lines), 1)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value
        self._calculate_size()
        self.request_render()

    def render_self(self, buffer: Buffer, delta_time: float) -> None:
        lines = self._value.split("\n")

        if not lines or (len(lines) == 1 and not lines[0]):
            buffer.write_text(self.x, self.y, self._placeholder, RGBA.from_values(0.5, 0.5, 0.5, 1))
        else:
            for i, line in enumerate(lines):
                if self.y + i >= buffer.height:
                    break
                buffer.write_text(self.x, self.y + i, line, RGBA.from_values(1, 1, 1, 1))

    def handle_key_press(self, key: Any) -> bool:
        lines = self._value.split("\n")

        if key.name == "backspace":
            if self._cursor_col > 0:
                lines[self._cursor_line] = (
                    lines[self._cursor_line][: self._cursor_col - 1]
                    + lines[self._cursor_line][self._cursor_col :]
                )
                self._cursor_col -= 1
            elif self._cursor_line > 0:
                self._cursor_col = len(lines[self._cursor_line - 1])
                lines[self._cursor_line - 1] += lines[self._cursor_line]
                del lines[self._cursor_line]
                self._cursor_line -= 1
            self._value = "\n".join(lines)
            self._calculate_size()
            return True
        elif key.name == "enter":
            lines.insert(self._cursor_line + 1, "")
            self._cursor_line += 1
            self._cursor_col = 0
            self._value = "\n".join(lines)
            self._calculate_size()
            return True
        elif key.name == "up":
            self._cursor_line = max(0, self._cursor_line - 1)
            self._cursor_col = min(self._cursor_col, len(lines[self._cursor_line]))
            return True
        elif key.name == "down":
            self._cursor_line = min(len(lines) - 1, self._cursor_line + 1)
            self._cursor_col = min(self._cursor_col, len(lines[self._cursor_line]))
            return True
        elif key.name == "left":
            if self._cursor_col > 0:
                self._cursor_col -= 1
            elif self._cursor_line > 0:
                self._cursor_line -= 1
                self._cursor_col = len(lines[self._cursor_line])
            return True
        elif key.name == "right":
            if self._cursor_col < len(lines[self._cursor_line]):
                self._cursor_col += 1
            elif self._cursor_line < len(lines) - 1:
                self._cursor_line += 1
                self._cursor_col = 0
            return True
        elif len(key.sequence) == 1:
            lines[self._cursor_line] = (
                lines[self._cursor_line][: self._cursor_col]
                + key.sequence
                + lines[self._cursor_line][self._cursor_col :]
            )
            self._cursor_col += 1
            self._value = "\n".join(lines)
            self._calculate_size()
            return True

        return False


class ScrollBar(Renderable):
    """A scrollbar component."""

    def __init__(
        self,
        ctx: Any,
        *,
        orientation: str = "vertical",
        value: float = 0,
        max_value: float = 100,
        step: float = 1,
        **kwargs: Any,
    ) -> None:
        super().__init__(ctx, **kwargs)

        self._orientation = orientation
        self._value = value
        self._max_value = max_value
        self._step = step

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, val: float) -> None:
        self._value = max(0, min(val, self._max_value))
        self.request_render()

    def render_self(self, buffer: Buffer, delta_time: float) -> None:
        if self._orientation == "vertical":
            self._render_vertical(buffer)
        else:
            self._render_horizontal(buffer)

    def _render_vertical(self, buffer: Buffer) -> None:
        bar_length = max(1, self.height - 2)
        thumb_position = (
            int((self._value / self._max_value) * (bar_length - 1)) if self._max_value > 0 else 0
        )

        for i in range(self.height):
            if i == 0:
                buffer.set_cell(self.x, self.y + i, "▲")
            elif i == self.height - 1:
                buffer.set_cell(self.x, self.y + i, "▼")
            elif i - 1 == thumb_position:
                buffer.set_cell(self.x, self.y + i, "█")
            else:
                buffer.set_cell(self.x, self.y + i, "│")

    def _render_horizontal(self, buffer: Buffer) -> None:
        bar_length = max(1, self.width - 2)
        thumb_position = (
            int((self._value / self._max_value) * (bar_length - 1)) if self._max_value > 0 else 0
        )

        for i in range(self.width):
            if i == 0:
                buffer.set_cell(self.x + i, self.y, "◄")
            elif i == self.width - 1:
                buffer.set_cell(self.x + i, self.y, "►")
            elif i - 1 == thumb_position:
                buffer.set_cell(self.x + i, self.y, "█")
            else:
                buffer.set_cell(self.x + i, self.y, "─")
