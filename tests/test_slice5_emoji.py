"""Tests for Slice 5 — Emoji picker dialog."""

from PySide6.QtWidgets import QDialog

from main import EMOJI_DATA, EmojiPickerDialog, PostletteWindow


class TestEmojiData:
    """Validate the emoji data list."""

    def test_has_at_least_50_entries(self) -> None:
        assert len(EMOJI_DATA) >= 50

    def test_entries_are_tuples_of_two_strings(self) -> None:
        for entry in EMOJI_DATA:
            assert isinstance(entry, tuple)
            assert len(entry) == 2
            emoji, keywords = entry
            assert isinstance(emoji, str)
            assert isinstance(keywords, str)

    def test_emoji_are_non_empty(self) -> None:
        for emoji, _ in EMOJI_DATA:
            assert len(emoji) > 0

    def test_keywords_are_non_empty(self) -> None:
        for _, keywords in EMOJI_DATA:
            assert len(keywords.strip()) > 0

    def test_no_duplicate_emoji(self) -> None:
        emojis = [e for e, _ in EMOJI_DATA]
        assert len(emojis) == len(set(emojis))


class TestEmojiPickerDialog:
    """Tests for the dialog widget itself."""

    def test_dialog_creates(self, qapp: None, window: PostletteWindow) -> None:
        dialog = EmojiPickerDialog(window)
        assert dialog.windowTitle() == "Emoji"

    def test_dialog_has_search_field(self, window: PostletteWindow) -> None:
        dialog = EmojiPickerDialog(window)
        assert dialog.search_field is not None
        assert dialog.search_field.placeholderText() == "Search emoji..."

    def test_dialog_has_emoji_buttons(self, window: PostletteWindow) -> None:
        dialog = EmojiPickerDialog(window)
        assert len(dialog._emoji_buttons) == len(EMOJI_DATA)

    def test_all_buttons_show_emoji_text(self, window: PostletteWindow) -> None:
        dialog = EmojiPickerDialog(window)
        emoji_set = {e for e, _ in EMOJI_DATA}
        for btn, _ in dialog._emoji_buttons:
            assert btn.text() in emoji_set

    def test_search_filters_buttons(self, window: PostletteWindow) -> None:
        dialog = EmojiPickerDialog(window)
        dialog._filter_emoji("fire")
        # Use isHidden() — isVisible() requires the parent dialog to be shown
        shown = [btn for btn, _ in dialog._emoji_buttons if not btn.isHidden()]
        hidden = [btn for btn, _ in dialog._emoji_buttons if btn.isHidden()]
        assert len(shown) >= 1
        assert len(hidden) >= 1

    def test_empty_search_shows_all(self, window: PostletteWindow) -> None:
        dialog = EmojiPickerDialog(window)
        dialog._filter_emoji("fire")
        dialog._filter_emoji("")
        shown = [btn for btn, _ in dialog._emoji_buttons if not btn.isHidden()]
        assert len(shown) == len(EMOJI_DATA)

    def test_search_is_case_insensitive(self, window: PostletteWindow) -> None:
        dialog = EmojiPickerDialog(window)
        dialog._filter_emoji("FIRE")
        shown = [btn for btn, _ in dialog._emoji_buttons if not btn.isHidden()]
        assert len(shown) >= 1

    def test_search_no_results(self, window: PostletteWindow) -> None:
        dialog = EmojiPickerDialog(window)
        dialog._filter_emoji("zzzznonexistent")
        shown = [btn for btn, _ in dialog._emoji_buttons if not btn.isHidden()]
        assert len(shown) == 0

    def test_select_sets_emoji_and_accepts(self, window: PostletteWindow) -> None:
        dialog = EmojiPickerDialog(window)
        dialog._select("\U0001f525")
        assert dialog.selected_emoji == "\U0001f525"
        assert dialog.result() == QDialog.DialogCode.Accepted


class TestEmojiInsertInEditor:
    """Integration tests for emoji insertion via the picker."""

    def test_insert_emoji_into_empty_editor(self, window: PostletteWindow) -> None:
        window._insert_text("\U0001f525")
        assert window.editor.toPlainText() == "\U0001f525"

    def test_insert_emoji_at_cursor(self, window: PostletteWindow) -> None:
        window.editor.setPlainText("Hello World")
        cursor = window.editor.textCursor()
        cursor.setPosition(5)
        window.editor.setTextCursor(cursor)
        window._insert_text("\U0001f600")
        assert window.editor.toPlainText() == "Hello\U0001f600 World"

    def test_char_count_updates_after_emoji(self, window: PostletteWindow) -> None:
        window._insert_text("\U0001f525")
        # Fire emoji is 1 Python char
        assert window.char_count_label.text() == "1 chars"

    def test_multiple_emoji_insert(self, window: PostletteWindow) -> None:
        window._insert_text("\U0001f525")
        window._insert_text("\U0001f600")
        window._insert_text("\u2764\ufe0f")
        text = window.editor.toPlainText()
        assert "\U0001f525" in text
        assert "\U0001f600" in text
        assert "\u2764" in text
