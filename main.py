"""Postlette — Unicode polish for social posts."""

import sys
from collections.abc import Callable
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

# Unicode Mathematical Bold offsets
# A-Z → U+1D400..U+1D419, a-z → U+1D41A..U+1D433, 0-9 → U+1D7CE..U+1D7D7
_BOLD_MAP: dict[str, str] = {}
for _i, _c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"):
    _BOLD_MAP[_c] = chr(0x1D400 + _i)
for _i in range(10):
    _BOLD_MAP[str(_i)] = chr(0x1D7CE + _i)


def apply_bold(text: str) -> str:
    """Map A-Z, a-z, 0-9 to Unicode Mathematical Bold. Leave everything else unchanged."""
    return "".join(_BOLD_MAP.get(c, c) for c in text)


# Unicode Mathematical Italic offsets (letters only — no reliable italic digit set)
# A-Z → U+1D434..U+1D44D, a-z → U+1D44E..U+1D467
# Exception: italic 'h' is U+210E (PLANCK CONSTANT), not U+1D455 (unassigned).
_ITALIC_MAP: dict[str, str] = {}
for _i, _c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"):
    _ITALIC_MAP[_c] = chr(0x1D434 + _i)
_ITALIC_MAP["h"] = "\u210e"

# Unicode Mathematical Bold-Italic offsets (letters only)
# A-Z → U+1D468..U+1D481, a-z → U+1D482..U+1D49B
_BOLD_ITALIC_MAP: dict[str, str] = {}
for _i, _c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"):
    _BOLD_ITALIC_MAP[_c] = chr(0x1D468 + _i)


def apply_italic(text: str) -> str:
    """Map A-Z, a-z to Unicode Mathematical Italic. Leave everything else unchanged."""
    return "".join(_ITALIC_MAP.get(c, c) for c in text)


def apply_bold_italic(text: str) -> str:
    """Map A-Z, a-z to Unicode Mathematical Bold-Italic. Leave everything else unchanged."""
    return "".join(_BOLD_ITALIC_MAP.get(c, c) for c in text)


# Reverse map: styled Unicode char → original ASCII. Built from all style maps
# so unstyle works regardless of which style was applied.
_UNSTYLE_MAP: dict[str, str] = {}
for _style_map in (_BOLD_MAP, _ITALIC_MAP, _BOLD_ITALIC_MAP):
    for _ascii, _styled in _style_map.items():
        _UNSTYLE_MAP[_styled] = _ascii


def apply_unstyle(text: str) -> str:
    """Revert any Postlette-styled characters back to ASCII. Leave everything else unchanged."""
    return "".join(_UNSTYLE_MAP.get(c, c) for c in text)


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
