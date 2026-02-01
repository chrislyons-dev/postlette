"""Tests for Slice 2 — Bold transform (selection only)."""

from PySide6.QtGui import QTextCursor

from main import PostletteWindow
from unicode_styles import apply_bold


class TestApplyBoldFunction:
    """Pure function tests for the bold mapping."""

    def test_uppercase_letters(self) -> None:
        result = apply_bold("ABCXYZ")
        assert result == "\U0001d400\U0001d401\U0001d402\U0001d417\U0001d418\U0001d419"

    def test_lowercase_letters(self) -> None:
        result = apply_bold("abcxyz")
        assert result == "\U0001d41a\U0001d41b\U0001d41c\U0001d431\U0001d432\U0001d433"

    def test_digits(self) -> None:
        result = apply_bold("0123456789")
        expected = "".join(chr(0x1D7CE + i) for i in range(10))
        assert result == expected

    def test_mixed_alphanumeric(self) -> None:
        result = apply_bold("Hi5")
        assert result == "\U0001d407\U0001d422\U0001d7d3"

    def test_leaves_punctuation_unchanged(self) -> None:
        result = apply_bold("Hello, world!")
        assert result[5] == ","
        assert result[6] == " "
        assert result[-1] == "!"

    def test_leaves_whitespace_unchanged(self) -> None:
        result = apply_bold("a b\tc\n")
        assert " " in result
        assert "\t" in result
        assert result.endswith("\n")

    def test_leaves_emoji_unchanged(self) -> None:
        assert apply_bold("\U0001f600") == "\U0001f600"

    def test_leaves_non_latin_unchanged(self) -> None:
        assert apply_bold("\u00e9\u00f1\u00fc") == "\u00e9\u00f1\u00fc"

    def test_empty_string(self) -> None:
        assert apply_bold("") == ""

    def test_all_ascii_letters_mapped(self) -> None:
        import string

        result = apply_bold(string.ascii_letters)
        # Every character should be different from input
        for original, bolded in zip(string.ascii_letters, result, strict=True):
            assert original != bolded, f"{original!r} was not mapped"

    def test_all_digits_mapped(self) -> None:
        result = apply_bold("0123456789")
        for original, bolded in zip("0123456789", result, strict=True):
            assert original != bolded, f"{original!r} was not mapped"


class TestBoldInEditor:
    """Integration tests for bold applied via the editor."""

    def test_bold_selected_text(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_bold()
        assert window.editor.toPlainText() == apply_bold("Hello")

    def test_bold_partial_selection(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello World")
        cursor = window.editor.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(5, QTextCursor.MoveMode.KeepAnchor)
        window.editor.setTextCursor(cursor)
        window._apply_bold()
        assert window.editor.toPlainText() == apply_bold("Hello") + " World"

    def test_bold_no_selection_does_nothing(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello")
        cursor = window.editor.textCursor()
        cursor.setPosition(2)  # cursor in middle, no selection
        window.editor.setTextCursor(cursor)
        window._apply_bold()
        assert window.editor.toPlainText() == "Hello"

    def test_bold_no_selection_shows_hint(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello")
        cursor = window.editor.textCursor()
        cursor.setPosition(0)
        window.editor.setTextCursor(cursor)
        window._apply_bold()
        assert window.status_bar.currentMessage() == "Select text to style."

    def test_bold_preserves_surrounding_text(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("aaa bbb ccc")
        cursor = window.editor.textCursor()
        cursor.setPosition(4)
        cursor.setPosition(7, QTextCursor.MoveMode.KeepAnchor)
        window.editor.setTextCursor(cursor)
        window._apply_bold()
        text = window.editor.toPlainText()
        assert text.startswith("aaa ")
        assert text.endswith(" ccc")
        assert apply_bold("bbb") in text

    def test_bold_preserves_selection(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_bold()
        cursor = window.editor.textCursor()
        assert cursor.hasSelection()
        assert cursor.selectedText() == apply_bold("Hello")

    def test_bold_punctuation_in_selection_unchanged(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hi, world!")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_bold()
        text = window.editor.toPlainText()
        assert "," in text
        assert " " in text
        assert "!" in text

    def test_char_count_updates_after_bold(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hi")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_bold()
        # Bold chars are multi-byte in UTF-8 but still 2 Python chars
        assert window.char_count_label.text() == "2 chars"
