"""Terminal buffer for rendering text with colors and attributes."""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import sys

from .types import RGBA, TextAttributes


try:
    import unicodedata

    def get_char_width(c: str) -> int:
        return unicodedata.east_asian_width(c) in ("F", "W")
except ImportError:

    def get_char_width(c: str) -> int:
        ord_c = ord(c)
        if ord_c >= 0x1100 and ord_c <= 0x115F:
            return 1
        if ord_c >= 0x2329 and ord_c <= 0x232A:
            return 1
        if ord_c >= 0x2E80 and ord_c <= 0x303E:
            return 1
        if ord_c >= 0x3040 and ord_c <= 0xA4CF:
            return 1
        if ord_c >= 0xAC00 and ord_c <= 0xD7A3:
            return 1
        if ord_c >= 0xF900 and ord_c <= 0xFAFF:
            return 1
        if ord_c >= 0xFE10 and ord_c <= 0xFE19:
            return 1
        if ord_c >= 0xFE30 and ord_c <= 0xFE6F:
            return 1
        if ord_c >= 0xFF00 and ord_c <= 0xFF60:
            return 1
        if ord_c >= 0xFFE0 and ord_c <= 0xFFE6:
            return 1
        if ord_c >= 0x20000 and ord_c <= 0x2FFFD:
            return 1
        if ord_c >= 0x30000 and ord_c <= 0x3FFFD:
            return 1
        return 0


class Cell:
    __slots__ = ("char", "fg", "bg", "attributes")

    def __init__(
        self,
        char: str = " ",
        fg: Optional[RGBA] = None,
        bg: Optional[RGBA] = None,
        attributes: int = TextAttributes.NONE,
    ) -> None:
        self.char = char
        self.fg = fg
        self.bg = bg
        self.attributes = attributes

    def copy(self) -> Cell:
        return Cell(
            self.char,
            self.fg,
            self.bg,
            self.attributes,
        )

    def equals_style(self, other: Cell) -> bool:
        return self.fg == other.fg and self.bg == other.bg and self.attributes == other.attributes


class Buffer:
    """Terminal buffer for rendering."""

    def __init__(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self._cells: List[List[Cell]] = [[Cell() for _ in range(width)] for _ in range(height)]
        self._default_fg = RGBA.from_values(1, 1, 1, 1)
        self._default_bg = RGBA.from_values(0, 0, 0, 0)
        self._cursor_x = 0
        self._cursor_y = 0

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def cursor_x(self) -> int:
        return self._cursor_x

    @property
    def cursor_y(self) -> int:
        return self._cursor_y

    def resize(self, width: int, height: int) -> None:
        old_height = self._height
        self._width = width
        self._height = height

        if height > old_height:
            for _ in range(height - old_height):
                self._cells.append([Cell() for _ in range(width)])
        elif height < old_height:
            self._cells = self._cells[:height]

        for row in self._cells:
            if len(row) < width:
                row.extend([Cell() for _ in range(width - len(row))])
            elif len(row) > width:
                del row[width:]

    def clear(self, bg: Optional[RGBA] = None) -> None:
        bg = bg or self._default_bg
        for y in range(self._height):
            for x in range(self._width):
                self._cells[y][x] = Cell(" ", self._default_fg, bg, TextAttributes.NONE)

    def set_cursor(self, x: int, y: int) -> None:
        self._cursor_x = max(0, min(x, self._width - 1))
        self._cursor_y = max(0, min(y, self._height - 1))

    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        if 0 <= x < self._width and 0 <= y < self._height:
            return self._cells[y][x]
        return None

    def set_cell(
        self,
        x: int,
        y: int,
        char: str,
        fg: Optional[RGBA] = None,
        bg: Optional[RGBA] = None,
        attributes: int = TextAttributes.NONE,
    ) -> None:
        if 0 <= x < self._width and 0 <= y < self._height:
            self._cells[y][x] = Cell(
                char, fg or self._default_fg, bg or self._default_bg, attributes
            )

    def write_text(
        self,
        x: int,
        y: int,
        text: str,
        fg: Optional[RGBA] = None,
        bg: Optional[RGBA] = None,
        attributes: int = TextAttributes.NONE,
    ) -> int:
        fg = fg or self._default_fg
        bg = bg or self._default_bg
        x_offset = 0

        for char in text:
            if x + x_offset >= self._width:
                break
            self.set_cell(x + x_offset, y, char, fg, bg, attributes)
            width = get_char_width(char)
            if width > 0 and x_offset + width < self._width:
                x_offset += width
            else:
                x_offset += 1

        return x_offset

    def fill_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        char: str = " ",
        fg: Optional[RGBA] = None,
        bg: Optional[RGBA] = None,
        attributes: int = TextAttributes.NONE,
    ) -> None:
        for row in range(y, min(y + height, self._height)):
            for col in range(x, min(x + width, self._width)):
                self.set_cell(col, row, char, fg, bg, attributes)

    def draw_frame(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        title: Optional[str] = None,
        fg: Optional[RGBA] = None,
        bg: Optional[RGBA] = None,
    ) -> None:
        if width < 2 or height < 2:
            return

        fg = fg or self._default_fg
        bg = bg or self._default_bg

        corners = {
            "top_left": "┌",
            "top_right": "┐",
            "bottom_left": "└",
            "bottom_right": "┘",
        }
        h_line = "─"
        v_line = "│"

        self.set_cell(x, y, corners["top_left"], fg, bg)
        self.set_cell(x + width - 1, y, corners["top_right"], fg, bg)
        self.set_cell(x, y + height - 1, corners["bottom_left"], fg, bg)
        self.set_cell(x + width - 1, y + height - 1, corners["bottom_right"], fg, bg)

        for col in range(x + 1, x + width - 1):
            self.set_cell(col, y, h_line, fg, bg)
            self.set_cell(col, y + height - 1, h_line, fg, bg)

        for row in range(y + 1, y + height - 1):
            self.set_cell(x, row, v_line, fg, bg)
            self.set_cell(x + width - 1, row, v_line, fg, bg)

        if title:
            title_width = min(len(title), width - 2)
            title_start = x + (width - title_width) // 2
            for i, char in enumerate(title[:title_width]):
                self.set_cell(title_start + i, y, char, fg, bg)

    def render_to_string(self) -> str:
        from .ansi import ANSI, color_to_ansi_fg, color_to_ansi_bg

        output: List[str] = []
        current_fg_id: int = id(None)
        current_bg_id: int = id(None)
        current_attrs = 0

        for y in range(self._height):
            line_parts: List[str] = []
            for x in range(self._width):
                cell = self._cells[y][x]

                fg_id = id(cell.fg)
                bg_id = id(cell.bg)

                fg_changed = fg_id != current_fg_id
                bg_changed = bg_id != current_bg_id
                attrs_changed = cell.attributes != current_attrs

                if fg_changed or bg_changed or attrs_changed:
                    if line_parts:
                        output.append("".join(line_parts))
                        line_parts = []

                    escape_parts = [ANSI.RESET]

                    if fg_changed and cell.fg:
                        escape_parts.append(color_to_ansi_fg(cell.fg))
                        current_fg_id = fg_id

                    if bg_changed and cell.bg:
                        escape_parts.append(color_to_ansi_bg(cell.bg))
                        current_bg_id = bg_id

                    if attrs_changed:
                        if cell.attributes & TextAttributes.BOLD:
                            escape_parts.append(ANSI.set_bold(True))
                        else:
                            escape_parts.append(ANSI.set_bold(False))

                        if cell.attributes & TextAttributes.ITALIC:
                            escape_parts.append(ANSI.set_italic(True))
                        else:
                            escape_parts.append(ANSI.set_italic(False))

                        if cell.attributes & TextAttributes.UNDERLINE:
                            escape_parts.append(ANSI.set_underline(True))
                        else:
                            escape_parts.append(ANSI.set_underline(False))

                    current_attrs = cell.attributes

                    output.append("".join(escape_parts))

                line_parts.append(cell.char if cell.char else " ")

            if line_parts:
                output.append("".join(line_parts))
            output.append("\n")

        output.append(ANSI.RESET)
        return "".join(output)


class OptimizedBuffer(Buffer):
    """Optimized buffer with additional features."""

    def __init__(self, width: int, height: int) -> None:
        super().__init__(width, height)
        self._scissor_stack: List[Tuple[int, int, int, int]] = []
        self._opacity_stack: List[float] = []

    def push_scissor_rect(self, x: int, y: int, width: int, height: int) -> None:
        self._scissor_stack.append((x, y, width, height))

    def pop_scissor_rect(self) -> None:
        if self._scissor_stack:
            self._scissor_stack.pop()

    def push_opacity(self, opacity: float) -> None:
        self._opacity_stack.append(opacity)

    def pop_opacity(self) -> None:
        if self._opacity_stack:
            self._opacity_stack.pop()

    def draw_frame_buffer(self, x: int, y: int, source: Buffer) -> None:
        for row in range(source.height):
            for col in range(source.width):
                src_cell = source.get_cell(col, row)
                if src_cell:
                    dst_x = x + col
                    dst_y = y + row
                    if 0 <= dst_x < self._width and 0 <= dst_y < self._height:
                        self.set_cell(
                            dst_x,
                            dst_y,
                            src_cell.char,
                            src_cell.fg,
                            src_cell.bg,
                            src_cell.attributes,
                        )
