"""Tests for Slice 4 — Unstyle (reversible transforms)."""

import string

from PySide6.QtGui import QTextCursor

from main import (
    PostletteWindow,
    apply_bold,
    apply_bold_italic,
    apply_italic,
    apply_unstyle,
)


class TestApplyUnstyleFunction:
    """Pure function tests for the unstyle mapping."""

    def test_unstyle_plain_ascii_unchanged(self) -> None:
        text = "Hello, world! 123"
        assert apply_unstyle(text) == text

    def test_unstyle_empty_string(self) -> None:
        assert apply_unstyle("") == ""

    def test_unstyle_emoji_unchanged(self) -> None:
        assert apply_unstyle("\U0001f600") == "\U0001f600"

    def test_unstyle_non_latin_unchanged(self) -> None:
        assert apply_unstyle("\u00e9\u00f1\u00fc") == "\u00e9\u00f1\u00fc"

    def test_unstyle_mixed_styled_and_plain(self) -> None:
        styled = apply_bold("Hello") + ", world!"
        assert apply_unstyle(styled) == "Hello, world!"


class TestRoundTripBold:
    """Bold → Unstyle should recover the original text."""

    def test_round_trip_letters(self) -> None:
        original = string.ascii_letters
        assert apply_unstyle(apply_bold(original)) == original

    def test_round_trip_digits(self) -> None:
        original = "0123456789"
        assert apply_unstyle(apply_bold(original)) == original

    def test_round_trip_mixed(self) -> None:
        original = "Hello World 42!"
        assert apply_unstyle(apply_bold(original)) == original


class TestRoundTripItalic:
    """Italic → Unstyle should recover the original text."""

    def test_round_trip_letters(self) -> None:
        original = string.ascii_letters
        assert apply_unstyle(apply_italic(original)) == original

    def test_round_trip_with_digits(self) -> None:
        """Digits aren't styled by italic, so unstyle should still pass through."""
        original = "abc123"
        assert apply_unstyle(apply_italic(original)) == original

    def test_round_trip_italic_h(self) -> None:
        """The italic 'h' (Planck constant U+210E) must round-trip correctly."""
        assert apply_unstyle(apply_italic("h")) == "h"


class TestRoundTripBoldItalic:
    """Bold-Italic → Unstyle should recover the original text."""

    def test_round_trip_letters(self) -> None:
        original = string.ascii_letters
        assert apply_unstyle(apply_bold_italic(original)) == original

    def test_round_trip_with_digits(self) -> None:
        original = "abc123"
        assert apply_unstyle(apply_bold_italic(original)) == original


class TestRoundTripComprehensive:
    """Cross-style round-trip guarantees."""

    def test_all_styles_round_trip_full_ascii(self) -> None:
        """Every styled character from every style map must unstyle back to original."""
        original = string.ascii_letters + string.digits
        for style_fn in (apply_bold, apply_italic, apply_bold_italic):
            styled = style_fn(original)
            result = apply_unstyle(styled)
            assert result == original, f"{style_fn.__name__} failed round-trip"

    def test_double_unstyle_is_idempotent(self) -> None:
        styled = apply_bold("Hello")
        once = apply_unstyle(styled)
        twice = apply_unstyle(once)
        assert once == twice == "Hello"

    def test_unstyle_does_not_affect_punctuation_and_whitespace(self) -> None:
        original = "Hello, world!\n\tGoodbye."
        styled = apply_bold(original)
        assert apply_unstyle(styled) == original


class TestUnstyleInEditor:
    """Integration tests for unstyle applied via the editor."""

    def test_unstyle_bold_text(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_bold()

        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_unstyle()
        assert window.editor.toPlainText() == "Hello"

    def test_unstyle_italic_text(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_italic()

        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_unstyle()
        assert window.editor.toPlainText() == "Hello"

    def test_unstyle_bold_italic_text(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_bold_italic()

        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_unstyle()
        assert window.editor.toPlainText() == "Hello"

    def test_unstyle_no_selection_does_nothing(self, window: PostletteWindow) -> None:
        styled = apply_bold("Hello")
        window.editor.setPlainText(styled)
        cursor = window.editor.textCursor()
        cursor.setPosition(0)
        window.editor.setTextCursor(cursor)
        window._apply_unstyle()
        assert window.editor.toPlainText() == styled

    def test_unstyle_partial_selection(self, window: PostletteWindow) -> None:
        bold_hello = apply_bold("Hello")
        bold_world = apply_bold("World")
        window.editor.setPlainText(bold_hello + " " + bold_world)
        # Select only "Hello" portion (bold chars are 2 UTF-16 units each)
        cursor = window.editor.textCursor()
        cursor.setPosition(0)
        utf16_len = len(bold_hello.encode("utf-16-le")) // 2
        cursor.setPosition(utf16_len, QTextCursor.MoveMode.KeepAnchor)
        window.editor.setTextCursor(cursor)
        window._apply_unstyle()
        text = window.editor.toPlainText()
        assert text.startswith("Hello")
        assert text.endswith(bold_world)

    def test_unstyle_plain_text_unchanged(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello World")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_unstyle()
        assert window.editor.toPlainText() == "Hello World"
