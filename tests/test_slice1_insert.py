"""Tests for Slice 1 — text insertion tools (em dash, separator)."""

from PySide6.QtGui import QTextCursor

from main import PostletteWindow


class TestInsertAtCursor:
    def test_insert_into_empty_editor(self, window: PostletteWindow) -> None:
        window._insert_text("—")
        assert window.editor.toPlainText() == "—"

    def test_insert_at_end(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello")
        # Move cursor to end
        cursor = window.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        window.editor.setTextCursor(cursor)
        window._insert_text("—")
        assert window.editor.toPlainText() == "Hello—"

    def test_insert_at_middle(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("HelloWorld")
        cursor = window.editor.textCursor()
        cursor.setPosition(5)
        window.editor.setTextCursor(cursor)
        window._insert_text(" ")
        assert window.editor.toPlainText() == "Hello World"

    def test_insert_at_beginning(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("World")
        cursor = window.editor.textCursor()
        cursor.setPosition(0)
        window.editor.setTextCursor(cursor)
        window._insert_text("Hello ")
        assert window.editor.toPlainText() == "Hello World"


class TestInsertReplacesSelection:
    def test_replace_selection_with_em_dash(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello World")
        cursor = window.editor.textCursor()
        cursor.setPosition(5)
        cursor.setPosition(11, QTextCursor.MoveMode.KeepAnchor)
        window.editor.setTextCursor(cursor)
        window._insert_text("—")
        assert window.editor.toPlainText() == "Hello—"

    def test_replace_all_text(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("old text")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._insert_text("new text")
        assert window.editor.toPlainText() == "new text"

    def test_replace_partial_selection(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("abcdef")
        cursor = window.editor.textCursor()
        cursor.setPosition(2)
        cursor.setPosition(4, QTextCursor.MoveMode.KeepAnchor)
        window.editor.setTextCursor(cursor)
        window._insert_text("XX")
        assert window.editor.toPlainText() == "abXXef"


class TestEmDash:
    def test_em_dash_character(self, window: PostletteWindow) -> None:
        window._insert_text("—")
        assert window.editor.toPlainText() == "\u2014"

    def test_em_dash_in_sentence(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("hello world")
        cursor = window.editor.textCursor()
        cursor.setPosition(5)
        window.editor.setTextCursor(cursor)
        window._insert_text(" — ")
        assert window.editor.toPlainText() == "hello —  world"


class TestSeparator:
    def test_separator_content(self, window: PostletteWindow) -> None:
        window._insert_text("────────")
        assert window.editor.toPlainText() == "────────"
        assert len(window.editor.toPlainText()) == 8

    def test_separator_on_own_line(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("above\n\nbelow")
        cursor = window.editor.textCursor()
        cursor.setPosition(6)  # after "above\n"
        window.editor.setTextCursor(cursor)
        window._insert_text("────────")
        assert window.editor.toPlainText() == "above\n────────\nbelow"


class TestInsertSideEffects:
    def test_char_count_updates_after_insert(self, window: PostletteWindow) -> None:
        window._insert_text("────────")
        assert window.char_count_label.text() == "8 chars"

    def test_multiple_inserts_accumulate(self, window: PostletteWindow) -> None:
        window._insert_text("A")
        window._insert_text("B")
        window._insert_text("C")
        assert window.editor.toPlainText() == "ABC"
        assert window.char_count_label.text() == "3 chars"

    def test_cursor_position_after_insert(self, window: PostletteWindow) -> None:
        """Cursor should be positioned after the inserted text."""
        window._insert_text("Hello")
        cursor = window.editor.textCursor()
        assert cursor.position() == 5

    def test_sequential_inserts_at_cursor(self, window: PostletteWindow) -> None:
        """Each insert should append at the cursor left by the previous insert."""
        window._insert_text("Hello")
        window._insert_text(" World")
        assert window.editor.toPlainText() == "Hello World"
