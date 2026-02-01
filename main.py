"""Postlette — Unicode polish for social posts."""

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
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

        # Window icon — light variant (dark marks) for the light UI background
        icon_path = Path(__file__).parent / "docs" / "images" / "logo-light.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        self._build_ui()
        self._update_char_count()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

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

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Editor
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Start typing your post...")
        self.editor.setFont(QFont("Segoe UI", 12))
        self.editor.textChanged.connect(self._update_char_count)
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

        # Keyboard shortcut: Ctrl+Shift+C to copy
        copy_action = QAction(self)
        copy_action.setShortcut("Ctrl+Shift+C")
        copy_action.triggered.connect(self._copy_to_clipboard)
        self.addAction(copy_action)

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
