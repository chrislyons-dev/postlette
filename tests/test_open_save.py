"""Tests for open/save behavior (text files, dirty tracking, dialogs)."""

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox

from main import PostletteWindow


class TestDirtyTracking:
    def test_dirty_flag_updates_on_edit(self, window: PostletteWindow) -> None:
        assert window.windowTitle() == "Postlette — Untitled"
        window.editor.setPlainText("Hello")
        assert window._dirty is True
        assert window.windowTitle() == "Postlette — Untitled*"

    def test_dirty_clears_after_save(self, window: PostletteWindow, tmp_path: Path) -> None:
        target = tmp_path / "note.txt"
        window.editor.setPlainText("Hello")
        window._save_to_path(target)
        assert window._dirty is False
        assert window.windowTitle() == "Postlette — note.txt"

    def test_confirm_discard_prompt(self, qapp, monkeypatch) -> None:
        window = PostletteWindow()
        window.editor.setPlainText("Hello")

        monkeypatch.setattr(
            QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.No
        )
        assert window._confirm_discard_changes() is False

        monkeypatch.setattr(
            QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Yes
        )
        assert window._confirm_discard_changes() is True


class TestOpenFile:
    def test_open_replaces_editor_text(
        self, window: PostletteWindow, tmp_path: Path, monkeypatch
    ) -> None:
        target = tmp_path / "open.txt"
        target.write_text("Opened text", encoding="utf-8")

        def fake_open(*_args, **_kwargs):
            return str(target), "Text files (*.txt)"

        monkeypatch.setattr(QFileDialog, "getOpenFileName", fake_open)

        window.editor.setPlainText("Old text")
        window._open_file()
        assert window.editor.toPlainText() == "Opened text"
        assert window.windowTitle() == "Postlette — open.txt"

    def test_open_invalid_encoding_sets_status(
        self, window: PostletteWindow, tmp_path: Path, monkeypatch
    ) -> None:
        target = tmp_path / "bad.txt"
        target.write_bytes(b"\xff\xfe\x00\x00")

        def fake_open(*_args, **_kwargs):
            return str(target), "Text files (*.txt)"

        monkeypatch.setattr(QFileDialog, "getOpenFileName", fake_open)
        window._open_file()
        assert window.status_bar.currentMessage() == "Could not open file. Invalid encoding."

    def test_open_with_dirty_cancel(
        self, window: PostletteWindow, tmp_path: Path, monkeypatch
    ) -> None:
        target = tmp_path / "open.txt"
        target.write_text("Opened text", encoding="utf-8")
        called = {"open": False}

        def fake_confirm(*_args, **_kwargs):
            return False

        def fake_open(*_args, **_kwargs):
            called["open"] = True
            return str(target), "Text files (*.txt)"

        monkeypatch.setattr(window, "_confirm_discard_changes", fake_confirm)
        monkeypatch.setattr(QFileDialog, "getOpenFileName", fake_open)

        window.editor.setPlainText("Dirty")
        window._open_file()
        assert called["open"] is False
        assert window.editor.toPlainText() == "Dirty"


class TestSaveFile:
    def test_save_as_appends_txt_extension(
        self, window: PostletteWindow, tmp_path: Path, monkeypatch
    ) -> None:
        target = tmp_path / "note"

        def fake_save(*_args, **_kwargs):
            return str(target), "Text files (*.txt)"

        monkeypatch.setattr(QFileDialog, "getSaveFileName", fake_save)

        window.editor.setPlainText("Hello")
        window._save_file_as()
        expected = tmp_path / "note.txt"
        assert expected.exists()
        assert expected.read_text(encoding="utf-8") == "Hello"
        assert window.windowTitle() == "Postlette — note.txt"

    def test_save_overwrites_existing_path(self, window: PostletteWindow, tmp_path: Path) -> None:
        target = tmp_path / "save.txt"
        target.write_text("Old", encoding="utf-8")

        window.editor.setPlainText("New")
        window._save_to_path(target)
        assert target.read_text(encoding="utf-8") == "New"
        assert window.windowTitle() == "Postlette — save.txt"

    def test_save_uses_existing_path(
        self, window: PostletteWindow, tmp_path: Path, monkeypatch
    ) -> None:
        target = tmp_path / "existing.txt"
        window._current_path = target

        def fake_save(*_args, **_kwargs):
            raise AssertionError("Save dialog should not be called.")

        monkeypatch.setattr(QFileDialog, "getSaveFileName", fake_save)

        window.editor.setPlainText("Hello")
        window._save_file()
        assert target.read_text(encoding="utf-8") == "Hello"
