"""Tests for Slice 0 — app skeleton, editor, copy, status bar, char count."""

from PySide6.QtWidgets import QApplication, QPlainTextEdit, QPushButton, QStatusBar

from main import PostletteWindow


class TestWindowSetup:
    def test_window_title(self, window: PostletteWindow) -> None:
        assert window.windowTitle() == "Postlette — Untitled"

    def test_minimum_size(self, window: PostletteWindow) -> None:
        assert window.minimumWidth() == 520
        assert window.minimumHeight() == 400

    def test_window_icon_loads(self, window: PostletteWindow) -> None:
        assert not window.windowIcon().isNull()


class TestEditor:
    def test_editor_exists(self, window: PostletteWindow) -> None:
        assert isinstance(window.editor, QPlainTextEdit)

    def test_editor_starts_empty(self, window: PostletteWindow) -> None:
        assert window.editor.toPlainText() == ""

    def test_editor_has_placeholder(self, window: PostletteWindow) -> None:
        assert window.editor.placeholderText() != ""


class TestCopyButton:
    def test_copy_button_exists(self, window: PostletteWindow) -> None:
        assert isinstance(window.copy_btn, QPushButton)

    def test_copy_button_label(self, window: PostletteWindow) -> None:
        assert window.copy_btn.text() == "Copy"

    def test_copy_empty_editor(self, window: PostletteWindow) -> None:
        window._copy_to_clipboard()
        assert QApplication.clipboard().text() == ""

    def test_copy_puts_text_on_clipboard(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello, world!")
        window._copy_to_clipboard()
        assert QApplication.clipboard().text() == "Hello, world!"

    def test_copy_preserves_unicode(self, window: PostletteWindow) -> None:
        text = "Caf\u00e9 \u2014 na\u00efve"
        window.editor.setPlainText(text)
        window._copy_to_clipboard()
        assert QApplication.clipboard().text() == text


class TestStatusBar:
    def test_status_bar_exists(self, window: PostletteWindow) -> None:
        assert isinstance(window.status_bar, QStatusBar)

    def test_status_bar_shows_ready_on_launch(self, window: PostletteWindow) -> None:
        assert window.status_bar.currentMessage() == "Ready"

    def test_status_bar_shows_copied_after_copy(self, window: PostletteWindow) -> None:
        window._copy_to_clipboard()
        assert window.status_bar.currentMessage() == "Copied"


class TestCharCount:
    def test_char_count_zero_on_empty(self, window: PostletteWindow) -> None:
        assert window.char_count_label.text() == "0 chars"

    def test_char_count_updates_on_typing(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello")
        assert window.char_count_label.text() == "5 chars"

    def test_char_count_handles_unicode(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("\u2014\u2014\u2014")  # 3 em dashes
        assert window.char_count_label.text() == "3 chars"

    def test_char_count_updates_on_clear(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("something")
        window.editor.setPlainText("")
        assert window.char_count_label.text() == "0 chars"

    def test_char_count_multiline(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("line1\nline2\n")
        # "line1\nline2\n" = 12 characters
        assert window.char_count_label.text() == "12 chars"
