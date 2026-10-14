"""
DESKTOP APP UI/UX DESIGN SYSTEM (THEME TOKENS & STYLESHEET)
Strict implementation matching the Modern Educational SaaS Desktop Design System.
100% Light, Blue-focused (#2F80ED), Clean, Soft Rounded UI.
"""

# ==============================================================================
# 1. DESIGN TOKENS (PYTHON CONSTANTS)
# ==============================================================================
COLOR_PRIMARY = "#2F80ED"
COLOR_PRIMARY_HOVER = "#1F6FDB"
COLOR_PRIMARY_ACTIVE = "#185FC0"
COLOR_PRIMARY_LIGHT = "#93C5FD"
COLOR_PRIMARY_BG = "#EFF6FF"
COLOR_PRIMARY_VERY_LIGHT = "#F7FAFF"

COLOR_BG = "#F5F8FC"
COLOR_SURFACE = "#FFFFFF"
COLOR_SURFACE_SECONDARY = "#F8FAFC"

COLOR_TEXT_PRIMARY = "#172B4D"
COLOR_TEXT_SECONDARY = "#64748B"
COLOR_TEXT_MUTED = "#94A3B8"
COLOR_TEXT_DISABLED = "#CBD5E1"

COLOR_BORDER_DEFAULT = "#E5EAF0"
COLOR_BORDER_LIGHT = "#EEF2F6"
COLOR_BORDER_FOCUS = "#2F80ED"

COLOR_SUCCESS = "#22C55E"
COLOR_SUCCESS_BG = "#ECFDF3"
COLOR_WARNING = "#F59E0B"
COLOR_WARNING_BG = "#FFF7E6"
COLOR_ERROR = "#EF4444"
COLOR_ERROR_BG = "#FEF2F2"
COLOR_INFO = "#3B82F6"

RADIUS_SM = "8px"
RADIUS_INPUT = "10px"
RADIUS_BUTTON = "10px"
RADIUS_CARD = "14px"
RADIUS_PANEL = "16px"
RADIUS_MODAL = "16px"
RADIUS_PILL = "999px"

# ==============================================================================
# 2. GLOBAL QSS STYLESHEET
# ==============================================================================
LIGHT_THEME_QSS = f"""
/* --- GLOBAL CANVAS & TYPOGRAPHY --- */
* {{
    font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', Arial, sans-serif;
    font-size: 13px;
    color: {COLOR_TEXT_PRIMARY};
    outline: none;
}}

QMainWindow, QDialog {{
    background-color: {COLOR_BG};
}}

QWidget#CentralCanvas, QWidget#MainContentPane {{
    background-color: {COLOR_BG};
}}

/* --- CARDS & PANELS --- */
QFrame.Card, QFrame#TableContainerCard, QFrame#ActionToolbarCard, QFrame#ProgressCard, QFrame.ContentCard {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER_DEFAULT};
    border-radius: {RADIUS_CARD};
}}

QFrame#HeaderBar {{
    background-color: {COLOR_SURFACE};
    border-bottom: 1px solid {COLOR_BORDER_LIGHT};
}}

QFrame#Sidebar {{
    background-color: {COLOR_SURFACE};
    border-right: 1px solid {COLOR_BORDER_DEFAULT};
}}

/* --- TYPOGRAPHY CLASSES --- */
QLabel.PageTitle {{
    font-size: 24px;
    font-weight: 700;
    color: {COLOR_TEXT_PRIMARY};
}}

QLabel.SectionTitle {{
    font-size: 20px;
    font-weight: 600;
    color: {COLOR_TEXT_PRIMARY};
}}

QLabel.CardTitle {{
    font-size: 16px;
    font-weight: 600;
    color: {COLOR_TEXT_PRIMARY};
}}

QLabel.BodyText {{
    font-size: 14px;
    font-weight: 400;
    color: {COLOR_TEXT_PRIMARY};
}}

QLabel.SmallText {{
    font-size: 13px;
    font-weight: 400;
    color: {COLOR_TEXT_SECONDARY};
}}

QLabel.CaptionText {{
    font-size: 12px;
    font-weight: 400;
    color: {COLOR_TEXT_MUTED};
}}

/* --- BUTTONS --- */
QPushButton {{
    font-size: 14px;
    font-weight: 600;
    border-radius: {RADIUS_BUTTON};
    padding: 0px 18px;
    min-height: 40px;
    max-height: 40px;
}}

QPushButton.PrimaryBtn, QPushButton#PrimaryBtn {{
    background-color: {COLOR_PRIMARY};
    color: #FFFFFF;
    border: none;
}}

QPushButton.PrimaryBtn:hover, QPushButton#PrimaryBtn:hover {{
    background-color: {COLOR_PRIMARY_HOVER};
}}

QPushButton.PrimaryBtn:pressed, QPushButton#PrimaryBtn:pressed {{
    background-color: {COLOR_PRIMARY_ACTIVE};
}}

QPushButton.PrimaryBtn:disabled, QPushButton#PrimaryBtn:disabled {{
    background-color: {COLOR_TEXT_DISABLED};
    color: #FFFFFF;
}}

QPushButton.SecondaryBtn, QPushButton#SecondaryBtn {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_PRIMARY};
    border: 1px solid {COLOR_PRIMARY};
}}

QPushButton.SecondaryBtn:hover, QPushButton#SecondaryBtn:hover {{
    background-color: {COLOR_PRIMARY_BG};
}}

QPushButton.GhostBtn, QPushButton#GhostBtn {{
    background-color: transparent;
    color: {COLOR_TEXT_SECONDARY};
    border: none;
}}

QPushButton.GhostBtn:hover, QPushButton#GhostBtn:hover {{
    background-color: #F1F5F9;
    color: {COLOR_TEXT_PRIMARY};
}}

QPushButton.DangerBtn, QPushButton#DangerBtn {{
    background-color: {COLOR_ERROR};
    color: #FFFFFF;
    border: none;
}}

QPushButton.DangerBtn:hover, QPushButton#DangerBtn:hover {{
    background-color: #DC2626;
}}

QPushButton.AIBtn, QPushButton#AIBtn {{
    background-color: {COLOR_PRIMARY};
    color: #FFFFFF;
    border: none;
    border-radius: {RADIUS_BUTTON};
    font-size: 13px;
    font-weight: 600;
    padding: 0px 18px;
    min-height: 38px;
    max-height: 38px;
}}

QPushButton.AIBtn:hover, QPushButton#AIBtn:hover {{
    background-color: {COLOR_PRIMARY_HOVER};
}}

QPushButton.AIBtn:pressed, QPushButton#AIBtn:pressed {{
    background-color: {COLOR_PRIMARY_ACTIVE};
}}

QPushButton.ToolbarActionBtn {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_TEXT_PRIMARY};
    border: 1px solid {COLOR_BORDER_DEFAULT};
    border-radius: {RADIUS_BUTTON};
    font-size: 13px;
    font-weight: 600;
    padding: 0px 14px;
    min-height: 40px;
}}

QPushButton.ToolbarActionBtn:hover {{
    background-color: {COLOR_PRIMARY_BG};
    border-color: {COLOR_PRIMARY_LIGHT};
    color: {COLOR_PRIMARY};
}}

QPushButton#BatchGradeBtn {{
    background-color: {COLOR_PRIMARY};
    color: #FFFFFF;
    border: none;
    border-radius: {RADIUS_BUTTON};
    font-size: 13px;
    font-weight: 600;
    padding: 0px 18px;
    min-height: 40px;
}}

QPushButton#BatchGradeBtn:hover {{
    background-color: {COLOR_PRIMARY_HOVER};
}}

/* --- FORM INPUTS & SELECTORS --- */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER_DEFAULT};
    border-radius: {RADIUS_INPUT};
    padding: 0px 12px;
    min-height: 38px;
    font-size: 13px;
    color: {COLOR_TEXT_PRIMARY};
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1.5px solid {COLOR_PRIMARY};
    background-color: #FFFFFF;
}}

QTextEdit, QPlainTextEdit {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER_DEFAULT};
    border-radius: {RADIUS_INPUT};
    padding: 10px 12px;
    font-size: 13px;
    color: {COLOR_TEXT_PRIMARY};
    line-height: 1.4;
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1.5px solid {COLOR_PRIMARY};
}}

/* --- MODERN SPINBOX STYLING --- */
QSpinBox, QDoubleSpinBox {{
    padding-right: 28px;
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid {COLOR_BORDER_DEFAULT};
    border-bottom: 1px solid {COLOR_BORDER_LIGHT};
    background-color: {COLOR_SURFACE_SECONDARY};
    border-top-right-radius: {RADIUS_INPUT};
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
    background-color: {COLOR_PRIMARY_BG};
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 24px;
    border-left: 1px solid {COLOR_BORDER_DEFAULT};
    background-color: {COLOR_SURFACE_SECONDARY};
    border-bottom-right-radius: {RADIUS_INPUT};
}}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {COLOR_PRIMARY_BG};
}}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid {COLOR_TEXT_SECONDARY};
}}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {COLOR_TEXT_SECONDARY};
}}

/* --- COMBOBOX DROPDOWN --- */
QComboBox::drop-down {{
    border: none;
    width: 24px;
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER_DEFAULT};
    border-radius: {RADIUS_INPUT};
    selection-background-color: {COLOR_PRIMARY_BG};
    selection-color: {COLOR_PRIMARY};
    color: {COLOR_TEXT_PRIMARY};
    padding: 4px;
}}

/* --- PROGRESS BAR (CLEAN 8PX NO NATIVE GLITCH) --- */
QProgressBar {{
    background-color: #E8EEF6;
    border-radius: 4px;
    border: none;
    max-height: 8px;
    min-height: 8px;
    qproperty-textVisible: false;
}}

QProgressBar::chunk {{
    background-color: {COLOR_PRIMARY};
    border-radius: 4px;
}}

/* --- TABLE SYSTEM (CLEAN 52PX ROWS, NO HEAVY VERTICAL BORDERS) --- */
QTableWidget, QTableView {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER_DEFAULT};
    border-radius: {RADIUS_CARD};
    gridline-color: transparent;
    font-size: 14px;
    color: {COLOR_TEXT_PRIMARY};
    selection-background-color: {COLOR_PRIMARY_BG};
    selection-color: {COLOR_PRIMARY};
}}

QHeaderView::section {{
    background-color: {COLOR_SURFACE_SECONDARY};
    color: {COLOR_TEXT_SECONDARY};
    font-size: 12px;
    font-weight: 600;
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid {COLOR_BORDER_LIGHT};
}}

QTableWidget::item {{
    border-bottom: 1px solid {COLOR_BORDER_LIGHT};
    padding: 6px 12px;
}}

QTableWidget::item:hover {{
    background-color: {COLOR_SURFACE_SECONDARY};
}}

/* --- TABS --- */
QTabWidget::pane {{
    border: 1px solid {COLOR_BORDER_DEFAULT};
    border-radius: {RADIUS_CARD};
    background-color: {COLOR_SURFACE};
    padding: 16px;
}}

QTabBar::tab {{
    background-color: {COLOR_SURFACE_SECONDARY};
    color: {COLOR_TEXT_SECONDARY};
    border: 1px solid {COLOR_BORDER_DEFAULT};
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 600;
    margin-right: 6px;
}}

QTabBar::tab:selected {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_PRIMARY};
    border-bottom: 2px solid {COLOR_PRIMARY};
}}

/* --- CLEAN SCROLLBARS --- */
QScrollBar:vertical {{
    border: none;
    background: {COLOR_SURFACE_SECONDARY};
    width: 6px;
    border-radius: 3px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {COLOR_BORDER_DEFAULT};
    border-radius: 3px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLOR_TEXT_MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""
