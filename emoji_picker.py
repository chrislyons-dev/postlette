"""Emoji picker dialog for Postlette."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from emoji_data import EMOJI_DATA


class EmojiPickerDialog(QDialog):
    """Searchable grid of common Unicode emoji."""

    # Emitted value when an emoji is selected
    selected_emoji: str = ""

    COLUMNS = 8

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Emoji")
        self.setMinimumSize(360, 320)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Search field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search emoji...")
        self.search_field.textChanged.connect(self._filter_emoji)
        layout.addWidget(self.search_field)

        # Scrollable emoji grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(4)
        scroll.setWidget(self.grid_container)
        layout.addWidget(scroll)

        self._emoji_buttons: list[tuple[QPushButton, str]] = []
        self._populate_grid(EMOJI_DATA)

    def _populate_grid(self, emoji_list: list[tuple[str, str]]) -> None:
        # Clear existing buttons
        for btn, _ in self._emoji_buttons:
            btn.setParent(None)
        self._emoji_buttons.clear()

        for idx, (emoji, keywords) in enumerate(emoji_list):
            btn = QPushButton(emoji)
            btn.setFixedSize(36, 36)
            btn.setFont(QFont("Segoe UI Emoji", 16))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(keywords.split()[0])
            btn.setStyleSheet(
                "QPushButton { background: white; border: 1px solid transparent;"
                " border-radius: 4px; padding: 2px; }"
                "QPushButton:hover { border-color: #14B8A6; background: #F8FAFC; }"
            )
            btn.clicked.connect(lambda checked=False, e=emoji: self._select(e))
            row, col = divmod(idx, self.COLUMNS)
            self.grid_layout.addWidget(btn, row, col)
            self._emoji_buttons.append((btn, keywords))

    def _filter_emoji(self, query: str) -> None:
        query_lower = query.lower().strip()
        for btn, keywords in self._emoji_buttons:
            btn.setVisible(not query_lower or query_lower in keywords)

    def _select(self, emoji: str) -> None:
        self.selected_emoji = emoji
        self.accept()
