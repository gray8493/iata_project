"""AITA - root pytest bootstrap for the monorepo `tests/` tree.

Forces Qt into offscreen mode so the PyQt6 system tests can build real
widgets on CI machines without a display.
"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def qapp():
    """A single QApplication for the whole session (Qt forbids more than one)."""
    pytest.importorskip("PyQt6")
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
