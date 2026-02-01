"""Shared fixtures for Postlette tests."""

import sys

import pytest
from PySide6.QtWidgets import QApplication

from main import PostletteWindow


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Single QApplication instance shared across the entire test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture()
def window(qapp: QApplication) -> PostletteWindow:
    """Fresh PostletteWindow for each test."""
    return PostletteWindow()
