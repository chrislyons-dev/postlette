"""Postlette — Unicode polish for social posts."""

import sys
from collections.abc import Callable
from pathlib import Path
from typing import override

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from emoji_picker import EmojiPickerDialog
from unicode_styles import (
    apply_bold,
    apply_bold_italic,
    apply_italic,
    apply_unstyle,
)

# Brand palette
INK_NAVY = "#0F172A"
PAPER = "#F8FAFC"
SLATE = "#334155"
POLISH_TEAL = "#14B8A6"


class PostletteWindow(QMainWindow):
    """Main application window with a text editor and copy button."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Postlette")
        self.setMinimumSize(520, 400)
        self._current_path: Path | None = None
        self._dirty = False
        self._suspend_dirty = False

        # Window icon — light variant (dark marks) for the light UI background
        icon_path = Path(__file__).parent / "docs" / "images" / "logo-light.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self._build_ui()
        self._update_char_count()
        self._update_window_title()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

        open_btn = QPushButton("📂")
        open_btn.setToolTip("Open")
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.setProperty("class", "toolbar-btn")
        open_btn.clicked.connect(self._open_file)
        toolbar.addWidget(open_btn)

        save_btn = QPushButton("💾")
        save_btn.setToolTip("Save")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setProperty("class", "toolbar-btn")
        save_btn.clicked.connect(self._save_file)
        toolbar.addWidget(save_btn)

        em_dash_btn = QPushButton("Em Dash —")
        em_dash_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        em_dash_btn.setProperty("class", "toolbar-btn")
        em_dash_btn.clicked.connect(lambda: self._insert_text("—"))
        toolbar.addWidget(em_dash_btn)

        separator_btn = QPushButton("Separator ────")
        separator_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        separator_btn.setProperty("class", "toolbar-btn")
        separator_btn.clicked.connect(lambda: self._insert_text("────────"))
        toolbar.addWidget(separator_btn)

        bold_btn = QPushButton("Bold")
        bold_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bold_btn.setProperty("class", "toolbar-btn")
        bold_btn.clicked.connect(self._apply_bold)
        toolbar.addWidget(bold_btn)

        italic_btn = QPushButton("Italic")
        italic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        italic_btn.setProperty("class", "toolbar-btn")
        italic_btn.clicked.connect(self._apply_italic)
        toolbar.addWidget(italic_btn)

        bold_italic_btn = QPushButton("Bold-Italic")
        bold_italic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bold_italic_btn.setProperty("class", "toolbar-btn")
        bold_italic_btn.clicked.connect(self._apply_bold_italic)
        toolbar.addWidget(bold_italic_btn)

        unstyle_btn = QPushButton("Unstyle")
        unstyle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        unstyle_btn.setProperty("class", "toolbar-btn")
        unstyle_btn.clicked.connect(self._apply_unstyle)
        toolbar.addWidget(unstyle_btn)

        emoji_btn = QPushButton("Emoji")
        emoji_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        emoji_btn.setProperty("class", "toolbar-btn")
        emoji_btn.clicked.connect(self._open_emoji_picker)
        toolbar.addWidget(emoji_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Editor
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Start typing your post...")
        self.editor.setFont(QFont("Segoe UI", 12))
        self.editor.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.editor)

        # Copy button
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setFixedHeight(36)
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        layout.addWidget(self.copy_btn)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Persistent character count label on the right side of the status bar
        self.char_count_label = QLabel()
        self.status_bar.addPermanentWidget(self.char_count_label)
        self.status_bar.showMessage("Ready")

        # Keyboard shortcuts
        copy_action = QAction(self)
        copy_action.setShortcut("Ctrl+Shift+C")
        copy_action.triggered.connect(self._copy_to_clipboard)
        self.addAction(copy_action)

        bold_action = QAction(self)
        bold_action.setShortcut("Ctrl+B")
        bold_action.triggered.connect(self._apply_bold)
        self.addAction(bold_action)

        italic_action = QAction(self)
        italic_action.setShortcut("Ctrl+I")
        italic_action.triggered.connect(self._apply_italic)
        self.addAction(italic_action)

        bold_italic_action = QAction(self)
        bold_italic_action.setShortcut("Ctrl+Shift+B")
        bold_italic_action.triggered.connect(self._apply_bold_italic)
        self.addAction(bold_italic_action)

        unstyle_action = QAction(self)
        unstyle_action.setShortcut("Ctrl+Shift+U")
        unstyle_action.triggered.connect(self._apply_unstyle)
        self.addAction(unstyle_action)

        open_action = QAction(self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        self.addAction(open_action)

        save_action = QAction(self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_file)
        self.addAction(save_action)

        save_as_action = QAction(self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._save_file_as)
        self.addAction(save_as_action)

        self._apply_stylesheet()

    def _apply_stylesheet(self) -> None:
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {PAPER};
            }}
            QPlainTextEdit {{
                background-color: white;
                color: {INK_NAVY};
                border: 1px solid {SLATE};
                border-radius: 4px;
                padding: 8px;
                selection-background-color: {POLISH_TEAL};
                selection-color: white;
            }}
            QPlainTextEdit:focus {{
                border: 2px solid {POLISH_TEAL};
            }}
            QPushButton {{
                background-color: {INK_NAVY};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 600;
                font-size: 14px;
                padding: 6px 24px;
            }}
            QPushButton:hover {{
                background-color: {SLATE};
            }}
            QPushButton:pressed {{
                background-color: {POLISH_TEAL};
            }}
            QPushButton[class="toolbar-btn"] {{
                background-color: white;
                color: {INK_NAVY};
                border: 1px solid {SLATE};
                font-weight: 600;
                font-size: 12px;
                padding: 4px 12px;
            }}
            QPushButton[class="toolbar-btn"]:hover {{
                background-color: {PAPER};
                border-color: {POLISH_TEAL};
            }}
            QPushButton[class="toolbar-btn"]:pressed {{
                background-color: {POLISH_TEAL};
                color: white;
            }}
            QStatusBar {{
                background-color: {PAPER};
                color: {SLATE};
                font-size: 12px;
            }}
        """)

    def _apply_bold(self) -> None:
        """Apply Unicode bold to the selected text. Do nothing if no selection."""
        self._transform_selection(apply_bold)

    def _apply_italic(self) -> None:
        """Apply Unicode italic to the selected text. Do nothing if no selection."""
        self._transform_selection(apply_italic)

    def _apply_bold_italic(self) -> None:
        """Apply Unicode bold-italic to the selected text. Do nothing if no selection."""
        self._transform_selection(apply_bold_italic)

    def _apply_unstyle(self) -> None:
        """Revert styled characters in the selection back to ASCII."""
        self._transform_selection(apply_unstyle)

    def _open_emoji_picker(self) -> None:
        """Open the emoji picker dialog and insert the selected emoji at cursor."""
        dialog = EmojiPickerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_emoji:
            self._insert_text(dialog.selected_emoji)

    def _transform_selection(self, transform: Callable[[str], str]) -> None:
        """Apply a text transform to the current selection, preserving selection."""
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            self.status_bar.showMessage("Select text to style.", 3000)
            return
        start = cursor.selectionStart()
        selected = cursor.selectedText()
        transformed = transform(selected)
        cursor.insertText(transformed)
        # Re-select the transformed text. Qt cursor positions are in UTF-16 code
        # units, so supplementary-plane characters (e.g. math bold) count as 2.
        utf16_len = len(transformed.encode("utf-16-le")) // 2
        cursor.setPosition(start)
        cursor.setPosition(start + utf16_len, cursor.MoveMode.KeepAnchor)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _insert_text(self, text: str) -> None:
        """Insert text at the current cursor position, replacing any selection."""
        cursor = self.editor.textCursor()
        cursor.insertText(text)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _copy_to_clipboard(self) -> None:
        text = self.editor.toPlainText()
        QApplication.clipboard().setText(text)
        self.status_bar.showMessage("Copied", 3000)

    def _update_char_count(self) -> None:
        count = len(self.editor.toPlainText())
        self.char_count_label.setText(f"{count} chars")

    def _on_text_changed(self) -> None:
        self._update_char_count()
        if self._suspend_dirty:
            return
        if not self._dirty:
            self._dirty = True
            self._update_window_title()

    def _update_window_title(self) -> None:
        name = self._current_path.name if self._current_path else "Untitled"
        marker = "*" if self._dirty else ""
        self.setWindowTitle(f"Postlette — {name}{marker}")

    def _confirm_discard_changes(self) -> bool:
        if not self._dirty:
            return True
        reply = QMessageBox.question(
            self,
            "Discard changes?",
            "Discard unsaved changes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def _open_file(self) -> None:
        if not self._confirm_discard_changes():
            return
        start_dir = str(self._current_path.parent) if self._current_path else ""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open text file",
            start_dir,
            "Text files (*.txt)",
        )
        if not filename:
            return
        path = Path(filename)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            self.status_bar.showMessage("Could not open file. Invalid encoding.", 5000)
            return
        except OSError:
            self.status_bar.showMessage("Could not open file.", 5000)
            return
        self._suspend_dirty = True
        self.editor.setPlainText(text)
        self._suspend_dirty = False
        self._dirty = False
        self._current_path = path
        self.status_bar.showMessage(f"Opened: {path.name}", 3000)
        self._update_window_title()

    def _save_file(self) -> None:
        if self._current_path is None:
            self._save_file_as()
            return
        self._save_to_path(self._current_path)

    def _save_file_as(self) -> None:
        start_dir = str(self._current_path.parent) if self._current_path else ""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save text file",
            start_dir,
            "Text files (*.txt)",
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix == "":
            path = path.with_suffix(".txt")
        self._save_to_path(path)

    def _save_to_path(self, path: Path) -> None:
        try:
            path.write_text(self.editor.toPlainText(), encoding="utf-8")
        except OSError:
            self.status_bar.showMessage("Could not save file.", 5000)
            return
        self._current_path = path
        self._dirty = False
        self.status_bar.showMessage(f"Saved: {path.name}", 3000)
        self._update_window_title()

    @override
    def closeEvent(self, event) -> None:
        if self._confirm_discard_changes():
            event.accept()
        else:
            event.ignore()


def main() -> None:
    app = QApplication(sys.argv)

    # Set application-wide palette based on brand colors
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(PAPER))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(INK_NAVY))
    app.setPalette(palette)

    window = PostletteWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
