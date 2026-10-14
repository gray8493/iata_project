# Dialogs Package
from .session_dialog import SessionDialog
from .history_dialog import HistoryDialog
from .grading_guide_dialog import GradingGuideDialog
from .testcase_dialog import TestcaseDialog
from .settings_dialog import SettingsDialog
from .submission_detail_dialog import SubmissionDetailDialog
from .plagiarism_dialog import PlagiarismDialog

__all__ = [
    "SessionDialog",
    "HistoryDialog",
    "GradingGuideDialog",
    "TestcaseDialog",
    "SettingsDialog",
    "SubmissionDetailDialog",
    "PlagiarismDialog",
]
