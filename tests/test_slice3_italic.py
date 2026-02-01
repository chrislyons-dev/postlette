"""Tests for Slice 3 — Italic and Bold-Italic transforms (selection only)."""

import string

from PySide6.QtGui import QTextCursor

from main import PostletteWindow, apply_bold_italic, apply_italic


class TestApplyItalicFunction:
    """Pure function tests for the italic mapping."""

    def test_uppercase_letters(self) -> None:
        result = apply_italic("ABC")
        assert result == "\U0001d434\U0001d435\U0001d436"

    def test_lowercase_letters(self) -> None:
        result = apply_italic("abc")
        assert result == "\U0001d44e\U0001d44f\U0001d450"

    def test_italic_h_is_planck_constant(self) -> None:
        """Italic 'h' uses U+210E (PLANCK CONSTANT), not the unassigned U+1D455."""
        result = apply_italic("h")
        assert result == "\u210e"

    def test_digits_unchanged(self) -> None:
        result = apply_italic("0123456789")
        assert result == "0123456789"

    def test_mixed_text(self) -> None:
        result = apply_italic("Hi 5!")
        # H and i are italicized, space/5/! are unchanged
        assert result[2] == " "
        assert result[3] == "5"
        assert result[4] == "!"

    def test_leaves_punctuation_unchanged(self) -> None:
        for ch in ".,;:!?@#$%^&*()-_+=[]{}|\\/<>~`\"'":
            assert apply_italic(ch) == ch, f"{ch!r} should be unchanged"

    def test_leaves_emoji_unchanged(self) -> None:
        assert apply_italic("\U0001f600") == "\U0001f600"

    def test_leaves_non_latin_unchanged(self) -> None:
        assert apply_italic("\u00e9\u00f1\u00fc") == "\u00e9\u00f1\u00fc"

    def test_empty_string(self) -> None:
        assert apply_italic("") == ""

    def test_all_ascii_letters_mapped(self) -> None:
        result = apply_italic(string.ascii_letters)
        for original, styled in zip(string.ascii_letters, result, strict=True):
            assert original != styled, f"{original!r} was not mapped"


class TestApplyBoldItalicFunction:
    """Pure function tests for the bold-italic mapping."""

    def test_uppercase_letters(self) -> None:
        result = apply_bold_italic("ABC")
        assert result == "\U0001d468\U0001d469\U0001d46a"

    def test_lowercase_letters(self) -> None:
        result = apply_bold_italic("abc")
        assert result == "\U0001d482\U0001d483\U0001d484"

    def test_digits_unchanged(self) -> None:
        result = apply_bold_italic("0123456789")
        assert result == "0123456789"

    def test_leaves_punctuation_unchanged(self) -> None:
        for ch in ".,;:!?":
            assert apply_bold_italic(ch) == ch, f"{ch!r} should be unchanged"

    def test_leaves_emoji_unchanged(self) -> None:
        assert apply_bold_italic("\U0001f600") == "\U0001f600"

    def test_empty_string(self) -> None:
        assert apply_bold_italic("") == ""

    def test_all_ascii_letters_mapped(self) -> None:
        result = apply_bold_italic(string.ascii_letters)
        for original, styled in zip(string.ascii_letters, result, strict=True):
            assert original != styled, f"{original!r} was not mapped"

    def test_bold_italic_differs_from_bold_and_italic(self) -> None:
        """Bold-italic should produce different codepoints than bold or italic alone."""
        from main import apply_bold

        text = "Hello"
        assert apply_bold_italic(text) != apply_bold(text)
        assert apply_bold_italic(text) != apply_italic(text)


class TestItalicInEditor:
    """Integration tests for italic applied via the editor."""

    def test_italic_selected_text(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_italic()
        assert window.editor.toPlainText() == apply_italic("Hello")

    def test_italic_no_selection_does_nothing(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello")
        cursor = window.editor.textCursor()
        cursor.setPosition(0)
        window.editor.setTextCursor(cursor)
        window._apply_italic()
        assert window.editor.toPlainText() == "Hello"

    def test_italic_partial_selection(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello World")
        cursor = window.editor.textCursor()
        cursor.setPosition(6)
        cursor.setPosition(11, QTextCursor.MoveMode.KeepAnchor)
        window.editor.setTextCursor(cursor)
        window._apply_italic()
        assert window.editor.toPlainText() == "Hello " + apply_italic("World")

    def test_italic_preserves_digits_in_selection(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("abc123")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_italic()
        text = window.editor.toPlainText()
        assert text.endswith("123")


class TestBoldItalicInEditor:
    """Integration tests for bold-italic applied via the editor."""

    def test_bold_italic_selected_text(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_bold_italic()
        assert window.editor.toPlainText() == apply_bold_italic("Hello")

    def test_bold_italic_no_selection_does_nothing(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello")
        cursor = window.editor.textCursor()
        cursor.setPosition(0)
        window.editor.setTextCursor(cursor)
        window._apply_bold_italic()
        assert window.editor.toPlainText() == "Hello"

    def test_bold_italic_preserves_digits(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("abc123")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_bold_italic()
        text = window.editor.toPlainText()
        assert text.endswith("123")
