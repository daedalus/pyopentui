"""Tests for renderable components."""

import pytest
from unittest.mock import MagicMock


class MockRenderer:
    def __init__(self):
        self._width = 80
        self._height = 24
        self._request_render_called = False

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def request_render(self):
        self._request_render_called = True


class TestRenderableBasics:
    def test_base_renderable_creation(self):
        from pyopentui.renderable import BaseRenderable

        r = BaseRenderable("test-id")
        assert r.id == "test-id"
        assert r.visible is True
        assert r.is_dirty is False

    def test_base_renderable_auto_id(self):
        from pyopentui.renderable import BaseRenderable

        r1 = BaseRenderable()
        r2 = BaseRenderable()
        assert r1.id != r2.id

    def test_mark_dirty_clean(self):
        from pyopentui.renderable import BaseRenderable

        r = BaseRenderable()
        assert r.is_dirty is False
        r.mark_dirty()
        assert r.is_dirty is True
        r.mark_clean()
        assert r.is_dirty is False

    def test_visible_property(self):
        from pyopentui.renderable import BaseRenderable

        r = BaseRenderable()
        assert r.visible is True
        r.visible = False
        assert r.visible is False

    def test_event_system(self):
        from pyopentui.renderable import BaseRenderable

        r = BaseRenderable()
        callback_called = []

        def callback(*args):
            callback_called.append(args)

        r.on("test-event", callback)
        r.emit("test-event", "arg1", "arg2")

        assert len(callback_called) == 1
        assert callback_called[0] == ("arg1", "arg2")

        r.off("test-event", callback)
        r.emit("test-event", "arg1")
        assert len(callback_called) == 1


class TestRenderable:
    def test_renderable_creation(self):
        from pyopentui.renderable import Renderable

        ctx = MockRenderer()
        r = Renderable(ctx, id="test", width=10, height=5)

        assert r.id == "test"
        assert r._width == 10
        assert r._height == 5
        r.focusable = True
        assert r.focusable is True
        assert r._visible is True

    def test_renderable_has_number(self):
        from pyopentui.renderable import Renderable

        ctx = MockRenderer()
        r1 = Renderable(ctx)
        r2 = Renderable(ctx)

        assert r1.num != r2.num

    def test_renderable_request_render(self):
        from pyopentui.renderable import Renderable

        ctx = MockRenderer()
        r = Renderable(ctx)

        r.request_render()
        assert ctx._request_render_called is True

    def test_renderable_visible(self):
        from pyopentui.renderable import Renderable

        ctx = MockRenderer()
        r = Renderable(ctx, visible=True)
        assert r.visible is True

        r.visible = False
        assert r.visible is False

    def test_renderable_opacity(self):
        from pyopentui.renderable import Renderable

        ctx = MockRenderer()
        r = Renderable(ctx, opacity=0.5)
        assert r.opacity == 0.5

        r.opacity = 0.8
        assert r.opacity == 0.8

        r.opacity = 1.5
        assert r.opacity == 1.0

        r.opacity = -0.5
        assert r.opacity == 0.0

    def test_renderable_focus(self):
        from pyopentui.renderable import Renderable, RenderableEvents

        ctx = MockRenderer()
        r = Renderable(ctx)
        r.focusable = True

        assert r.focused is False
        r.focus()
        assert r.focused is True

        r.blur()
        assert r.focused is False

    def test_renderable_not_focusable(self):
        from pyopentui.renderable import Renderable

        ctx = MockRenderer()
        r = Renderable(ctx)
        r.focusable = False

        r.focus()
        assert r.focused is False

    def test_renderable_children(self):
        from pyopentui.renderable import Renderable

        ctx = MockRenderer()
        parent = Renderable(ctx, id="parent")
        child = Renderable(ctx, id="child")

        parent.add(child)

        assert parent.get_children_count() == 1
        assert parent.get_renderable("child") == child
        assert child in parent.get_children()

    def test_renderable_remove_child(self):
        from pyopentui.renderable import Renderable

        ctx = MockRenderer()
        parent = Renderable(ctx, id="parent")
        child = Renderable(ctx, id="child")

        parent.add(child)
        parent.remove("child")

        assert parent.get_children_count() == 0
        assert parent.get_renderable("child") is None

    def test_renderable_destroy(self):
        from pyopentui.renderable import Renderable

        ctx = MockRenderer()
        r = Renderable(ctx)

        r.destroy()
        assert r.is_destroyed is True


class TestRootRenderable:
    def test_root_renderable_creation(self):
        from pyopentui.renderable import RootRenderable

        class MockCtx:
            width = 80
            height = 24

        ctx = MockCtx()
        root = RootRenderable(ctx, 80, 24)

        assert root.id == "__root__"
        assert root._width == 80
        assert root._height == 24

    def test_root_renderable_resize(self):
        from pyopentui.renderable import RootRenderable
        from pyopentui.renderer import CliRenderer

        renderer = MagicMock(spec=CliRenderer)
        renderer.width = 80
        renderer.height = 24

        root = RootRenderable(renderer, 80, 24)
        root.resize(100, 30)

        assert root.width == 100
        assert root.height == 30
