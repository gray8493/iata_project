"""AITA reusable, non-blocking UI components (widgets shared by windows & dialogs)."""
from .toast import ToastNotification, show_toast
from .app_avatar import make_aita_avatar_pixmap
from .spinner import CircularSpinner, SpinnerOverlay, start_spinner, stop_spinner
from .code_editor import CodeEditor, LineNumberArea
from .multiline_field import MultiLineField, line_stats, text_warnings, visualize_hidden_chars
from .table_actions import (
    make_action_cell, make_row_button, preview_multiline, preview_tooltip, text_color_for_value,
)

__all__ = [
    "ToastNotification", "show_toast",
    "make_aita_avatar_pixmap",
    "CircularSpinner", "SpinnerOverlay", "start_spinner", "stop_spinner",
    "CodeEditor", "LineNumberArea",
    "MultiLineField", "line_stats", "text_warnings", "visualize_hidden_chars",
    "make_action_cell", "make_row_button", "preview_multiline", "preview_tooltip",
    "text_color_for_value",
]
