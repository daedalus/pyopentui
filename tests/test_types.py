"""Tests for the RGBA color class."""

import pytest
from pyopentui.types import RGBA, ColorInput


class TestRGBA:
    def test_from_values(self):
        color = RGBA.from_values(0.5, 0.5, 0.5, 1.0)
        assert color.r == 0.5
        assert color.g == 0.5
        assert color.b == 0.5
        assert color.a == 1.0

    def test_from_ints(self):
        color = RGBA.from_ints(128, 64, 32, 255)
        assert color.r == pytest.approx(128 / 255)
        assert color.g == pytest.approx(64 / 255)
        assert color.b == pytest.approx(32 / 255)
        assert color.a == pytest.approx(1.0)

    def test_from_hex_short(self):
        color = RGBA.from_hex("#fff")
        assert color.r == 1.0
        assert color.g == 1.0
        assert color.b == 1.0

    def test_from_hex_long(self):
        color = RGBA.from_hex("#ff8800")
        assert color.r == pytest.approx(1.0)
        assert color.g == pytest.approx(0.5333, abs=0.01)
        assert color.b == 0.0

    def test_from_hex_with_alpha(self):
        color = RGBA.from_hex("#ff880080")
        assert color.r == pytest.approx(1.0)
        assert color.g == pytest.approx(0.5333, abs=0.01)
        assert color.b == 0.0
        assert color.a == pytest.approx(0.5, abs=0.01)

    def test_to_ints(self):
        color = RGBA.from_values(0.5, 0.25, 0.75, 1.0)
        r, g, b, a = color.to_ints()
        assert r == 128
        assert g == 64
        assert b == 191
        assert a == 255

    def test_equals(self):
        color1 = RGBA.from_values(0.5, 0.5, 0.5, 1.0)
        color2 = RGBA.from_values(0.5, 0.5, 0.5, 1.0)
        color3 = RGBA.from_values(0.5, 0.5, 0.5, 0.5)

        assert color1.equals(color2)
        assert not color1.equals(color3)
        assert not color1.equals(None)

    def test_equality_operator(self):
        color1 = RGBA.from_values(0.5, 0.5, 0.5, 1.0)
        color2 = RGBA.from_values(0.5, 0.5, 0.5, 1.0)
        color3 = RGBA.from_values(0.5, 0.5, 0.5, 0.5)

        assert color1 == color2
        assert color1 != color3
        assert color1 != "not a color"

    def test_hashable(self):
        color1 = RGBA.from_values(0.5, 0.5, 0.5, 1.0)
        color2 = RGBA.from_values(0.5, 0.5, 0.5, 1.0)

        assert hash(color1) == hash(color2)

    def test_invalid_hex(self):
        color = RGBA.from_hex("invalid")
        assert color.r == 1.0
        assert color.g == 0.0
        assert color.b == 1.0

    def test_repr(self):
        color = RGBA.from_values(0.5, 0.5, 0.5, 1.0)
        assert repr(color) == "RGBA(0.50, 0.50, 0.50, 1.00)"


class TestTextAttributes:
    def test_constants(self):
        from pyopentui.types import (
            TEXT_ATTRIBUTES_NONE,
            TEXT_ATTRIBUTES_BOLD,
            TEXT_ATTRIBUTES_DIM,
            TEXT_ATTRIBUTES_ITALIC,
            TEXT_ATTRIBUTES_UNDERLINE,
            TEXT_ATTRIBUTES_BLINK,
            TEXT_ATTRIBUTES_INVERSE,
            TEXT_ATTRIBUTES_HIDDEN,
            TEXT_ATTRIBUTES_STRIKETHROUGH,
        )

        assert TEXT_ATTRIBUTES_NONE == 0
        assert TEXT_ATTRIBUTES_BOLD == 1
        assert TEXT_ATTRIBUTES_DIM == 2
        assert TEXT_ATTRIBUTES_ITALIC == 4
        assert TEXT_ATTRIBUTES_UNDERLINE == 8
        assert TEXT_ATTRIBUTES_BLINK == 16
        assert TEXT_ATTRIBUTES_INVERSE == 32
        assert TEXT_ATTRIBUTES_HIDDEN == 64
        assert TEXT_ATTRIBUTES_STRIKETHROUGH == 128
