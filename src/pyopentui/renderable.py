"""Renderable base classes for the TUI framework."""

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .renderer import CliRenderer

from .buffer import Buffer, OptimizedBuffer
from .types import RGBA, TextAttributes


class LayoutEvents:
    LAYOUT_CHANGED = "layout-changed"
    ADDED = "added"
    REMOVED = "removed"
    RESIZED = "resized"


class RenderableEvents:
    FOCUSED = "focused"
    BLURRED = "blurred"


RenderEventCallback = Callable[[Buffer, float], None]


class BaseRenderable:
    """Base class for all renderable components."""

    _renderable_number: int = 1

    def __init__(self, id: Optional[str] = None) -> None:
        self._id: str = id or f"renderable-{BaseRenderable._renderable_number}"
        BaseRenderable._renderable_number += 1
        self._dirty: bool = False
        self._visible: bool = True
        self._listeners: Dict[str, List[Callable]] = {}

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def is_dirty(self) -> bool:
        return self._dirty

    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._visible = value

    def mark_dirty(self) -> None:
        self._dirty = True

    def mark_clean(self) -> None:
        self._dirty = False

    def on(self, event: str, callback: Callable) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def off(self, event: str, callback: Callable) -> None:
        if event in self._listeners:
            self._listeners[event] = [cb for cb in self._listeners[event] if cb != callback]

    def emit(self, event: str, *args: Any) -> None:
        if event in self._listeners:
            for callback in self._listeners[event]:
                callback(*args)

    def add(self, obj: Any, index: Optional[int] = None) -> int:
        raise NotImplementedError()

    def remove(self, id: str) -> None:
        raise NotImplementedError()

    def insert_before(self, obj: Any, anchor: Any) -> int:
        raise NotImplementedError()

    def get_children(self) -> List[Any]:
        raise NotImplementedError()

    def get_children_count(self) -> int:
        raise NotImplementedError()

    def get_renderable(self, id: str) -> Optional[BaseRenderable]:
        raise NotImplementedError()

    def request_render(self) -> None:
        raise NotImplementedError()

    def find_descendant_by_id(self, id: str) -> Optional[BaseRenderable]:
        raise NotImplementedError()


class Renderable(BaseRenderable):
    """Main renderable class with layout support."""

    renderables_by_number: Dict[int, "Renderable"] = {}

    def __init__(
        self,
        ctx: CliRenderer,
        *,
        id: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        x: int = 0,
        y: int = 0,
        flex_grow: float = 0,
        flex_shrink: float = 1,
        flex_direction: str = "column",
        flex_wrap: str = "nowrap",
        align_items: str = "stretch",
        justify_content: str = "flex-start",
        align_self: str = "auto",
        position: str = "relative",
        overflow: str = "visible",
        position_top: Optional[int] = None,
        position_right: Optional[int] = None,
        position_bottom: Optional[int] = None,
        position_left: Optional[int] = None,
        margin: Optional[int] = None,
        padding: Optional[int] = None,
        z_index: int = 0,
        visible: bool = True,
        buffered: bool = False,
        live: bool = False,
        opacity: float = 1.0,
    ) -> None:
        super().__init__(id)

        self._ctx = ctx
        self._num = Renderable._renderable_number
        Renderable.renderables_by_number[self._num] = self
        Renderable._renderable_number += 1

        self._x = x
        self._y = y
        self._width: int = width or 0
        self._height: int = height or 0
        self._width_value: int = 0
        self._height_value: int = 0

        self._flex_grow = flex_grow
        self._flex_shrink = flex_shrink
        self._flex_direction = flex_direction
        self._flex_wrap = flex_wrap
        self._align_items = align_items
        self._justify_content = justify_content
        self._align_self = align_self
        self._position = position
        self._overflow = overflow
        self._position_top = position_top
        self._position_right = position_right
        self._position_bottom = position_bottom
        self._position_left = position_left
        self._margin = margin
        self._padding = padding

        self._z_index = z_index
        self._visible = visible
        self._buffered = buffered
        self._live = live
        self._live_count = 1 if live and visible else 0
        self._opacity = max(0, min(1, opacity))

        self._focusable = False
        self._focused = False

        self.parent: Optional[Renderable] = None
        self._children: List[Renderable] = []
        self._renderable_map: Dict[str, Renderable] = {}

        self._frame_buffer: Optional[OptimizedBuffer] = None
        if self._buffered:
            self._create_frame_buffer()

        self._render_before: Optional[RenderEventCallback] = None
        self._render_after: Optional[RenderEventCallback] = None

        self._mouse_listeners: Dict[str, Callable] = {}
        self._key_listeners: Dict[str, Callable] = {}

    @property
    def num(self) -> int:
        return self._num

    @property
    def ctx(self) -> CliRenderer:
        return self._ctx

    @property
    def x(self) -> int:
        if self.parent:
            return self.parent.x + self._x
        return self._x

    @property
    def y(self) -> int:
        if self.parent:
            return self.parent.y + self._y
        return self._y

    @property
    def width(self) -> int:
        return self._width_value

    @width.setter
    def width(self, value: int) -> None:
        self._width = value
        self._width_value = value
        self.mark_dirty()

    @property
    def height(self) -> int:
        return self._height_value

    @height.setter
    def height(self, value: int) -> None:
        self._height = value
        self._height_value = value
        self.mark_dirty()

    @property
    def z_index(self) -> int:
        return self._z_index

    @z_index.setter
    def z_index(self, value: int) -> None:
        self._z_index = value

    @property
    def focusable(self) -> bool:
        return self._focusable

    @focusable.setter
    def focusable(self, value: bool) -> None:
        self._focusable = value

    @property
    def focused(self) -> bool:
        return self._focused

    @property
    def live(self) -> bool:
        return self._live

    @live.setter
    def live(self, value: bool) -> None:
        self._live = value

    @property
    def opacity(self) -> float:
        return self._opacity

    @opacity.setter
    def opacity(self, value: float) -> None:
        self._opacity = max(0, min(1, value))

    def _create_frame_buffer(self) -> None:
        if self._width_value > 0 and self._height_value > 0:
            self._frame_buffer = OptimizedBuffer(self._width_value, self._height_value)

    def _handle_frame_buffer_resize(self, width: int, height: int) -> None:
        if not self._buffered:
            return
        if width <= 0 or height <= 0:
            return
        if self._frame_buffer:
            self._frame_buffer.resize(width, height)
        else:
            self._create_frame_buffer()

    def request_render(self) -> None:
        self.mark_dirty()
        self._ctx.request_render()

    def focus(self) -> None:
        if self._focused or not self._focusable:
            return
        self._focused = True
        self.request_render()
        self.emit(RenderableEvents.FOCUSED)

    def blur(self) -> None:
        if not self._focused:
            return
        self._focused = False
        self.request_render()
        self.emit(RenderableEvents.BLURRED)

    def add(self, obj: "Renderable", index: Optional[int] = None) -> int:
        if obj is None:
            return -1

        if not isinstance(obj, Renderable):
            return -1

        if obj.parent:
            obj.parent.remove(obj.id)

        obj.parent = self
        self._renderable_map[obj.id] = obj

        if index is not None:
            self._children.insert(index, obj)
        else:
            self._children.append(obj)

        self.request_render()
        return len(self._children) - 1

    def remove(self, id: str) -> None:
        if id not in self._renderable_map:
            return

        obj = self._renderable_map[id]
        obj.parent = None
        self._children = [c for c in self._children if c.id != id]
        del self._renderable_map[id]
        self.request_render()

    def insert_before(self, obj: "Renderable", anchor: "Renderable") -> int:
        if obj is None or anchor is None:
            return -1

        if anchor.id not in self._renderable_map:
            return -1

        if obj.parent:
            obj.parent.remove(obj.id)

        obj.parent = self
        self._renderable_map[obj.id] = obj

        anchor_index = self._children.index(anchor)
        self._children.insert(anchor_index, obj)

        self.request_render()
        return anchor_index

    def get_children(self) -> List[Any]:
        return list(self._children)

    def get_children_count(self) -> int:
        return len(self._children)

    def get_renderable(self, id: str) -> Optional["Renderable"]:
        return self._renderable_map.get(id)

    def find_descendant_by_id(self, id: str) -> Optional["Renderable"]:
        if self._id == id:
            return self
        for child in self._children:
            found = child.find_descendant_by_id(id)
            if found:
                return found
        return None

    def get_layout_node(self) -> Any:
        return None

    def update_from_layout(self) -> None:
        pass

    def on_resize(self, width: int, height: int) -> None:
        self._width_value = width
        self._height_value = height
        self._handle_frame_buffer_resize(width, height)

    def update_layout(self, delta_time: float, render_list: Optional[List[Any]] = None) -> None:
        if not self.visible:
            return

        self.on_update(delta_time)

        if render_list is not None:
            render_list.append({"action": "render", "renderable": self})

    def render(self, buffer: Buffer, delta_time: float) -> None:
        render_buffer = buffer
        if self._buffered and self._frame_buffer:
            render_buffer = self._frame_buffer

        if self._render_before:
            self._render_before(render_buffer, delta_time)

        self.render_self(render_buffer, delta_time)

        if self._render_after:
            self._render_after(render_buffer, delta_time)

        self.mark_clean()

        if self._buffered and self._frame_buffer:
            buffer.draw_frame_buffer(self.x, self.y, self._frame_buffer)

    def on_update(self, delta_time: float) -> None:
        pass

    def render_self(self, buffer: Buffer, delta_time: float) -> None:
        pass

    def process_mouse_event(self, event: Any) -> None:
        if event.type in self._mouse_listeners:
            self._mouse_listeners[event.type](event)

        self.on_mouse_event(event)

        if self.parent:
            self.parent.process_mouse_event(event)

    def on_mouse_event(self, event: Any) -> None:
        pass

    def set_mouse_handler(self, event_type: str, handler: Callable) -> None:
        self._mouse_listeners[event_type] = handler

    def set_key_handler(self, event_type: str, handler: Callable) -> None:
        self._key_listeners[event_type] = handler

    def destroy(self) -> None:
        self._is_destroyed = True

        if self.parent:
            self.parent.remove(self.id)

        if self._frame_buffer:
            self._frame_buffer = None

        for child in list(self._children):
            child.destroy()

        self._children = []
        self._renderable_map.clear()

        if self.num in Renderable.renderables_by_number:
            del Renderable.renderables_by_number[self.num]

        self.blur()
        self._listeners.clear()

    @property
    def is_destroyed(self) -> bool:
        return getattr(self, "_is_destroyed", False)


class RootRenderable(Renderable):
    """Root renderable that serves as the top-level container."""

    def __init__(self, ctx: CliRenderer, width: int, height: int) -> None:
        super().__init__(
            ctx,
            id="__root__",
            width=width,
            height=height,
            z_index=0,
            visible=True,
        )
        self._render_list: List[Any] = []

    def render(self, buffer: Buffer, delta_time: float) -> None:
        if not self.visible:
            return

        self._width_value = self._ctx.width
        self._height_value = self._ctx.height

        self.calculate_layout()

        self._render_list = []
        self.update_layout(delta_time, self._render_list)

        for cmd in self._render_list:
            if cmd.get("action") == "render":
                renderable = cmd.get("renderable")
                if renderable and not renderable.is_destroyed:
                    renderable.render(buffer, delta_time)

    def calculate_layout(self) -> None:
        pass

    def update_layout(self, delta_time: float, render_list: Optional[List[Any]] = None) -> None:
        if render_list is None:
            render_list = []
        if not self.visible:
            return

        self.on_update(delta_time)

        render_list.append({"action": "render", "renderable": self})

        sorted_children = sorted(self._children, key=lambda c: c.z_index)
        for child in sorted_children:
            child.update_layout(delta_time, render_list)

    def resize(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self._width_value = width
        self._height_value = height
        self.emit(LayoutEvents.RESIZED, {"width": width, "height": height})
