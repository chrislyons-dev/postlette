"""Tests for list insertion and continuation."""

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent, QTextCursor

from main import PostletteWindow


class TestListInsertion:
    def test_insert_bullets_selection(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("a\nb\nc")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._insert_list("Bullets")
        assert window.editor.toPlainText() == "• a\n• b\n• c"

    def test_insert_numbers_selection(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("a\nb\nc")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._insert_list("Numbers")
        assert window.editor.toPlainText() == "1. a\n2. b\n3. c"

    def test_insert_dashes_current_line(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("hello")
        cursor = window.editor.textCursor()
        cursor.setPosition(0)
        window.editor.setTextCursor(cursor)
        window._insert_list("Dashes")
        assert window.editor.toPlainText() == "- hello"

    def test_switch_list_type_replaces_prefixes(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("• bold\n• italics\n• both")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._insert_list("Numbers")
        assert window.editor.toPlainText() == "1. bold\n2. italics\n3. both"

    def test_switch_list_type_single_line(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("• item")
        cursor = window.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        window.editor.setTextCursor(cursor)
        window._insert_list("Dashes")
        assert window.editor.toPlainText() == "- item"


class TestUnstyleRemovesLists:
    def test_unstyle_strips_list_prefixes(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("1. First\n• Second\n- Third")
        cursor = window.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        window.editor.setTextCursor(cursor)
        window._apply_unstyle()
        assert window.editor.toPlainText() == "First\nSecond\nThird"


class TestListContinuation:
    def _press_enter(self, window: PostletteWindow) -> None:
        event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
        window.editor.keyPressEvent(event)

    def test_continue_numbered_list(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("1. item")
        cursor = window.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        window.editor.setTextCursor(cursor)
        self._press_enter(window)
        assert window.editor.toPlainText() == "1. item\n2. "

    def test_continue_bulleted_list(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("• item")
        cursor = window.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        window.editor.setTextCursor(cursor)
        self._press_enter(window)
        assert window.editor.toPlainText() == "• item\n• "

    def test_exit_empty_list_item(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("• ")
        cursor = window.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        window.editor.setTextCursor(cursor)
        self._press_enter(window)
        assert window.editor.toPlainText() == "\n"
