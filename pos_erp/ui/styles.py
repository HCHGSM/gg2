from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

def apply_card_shadow(widget):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(25)
    shadow.setColor(QColor(0, 0, 0, 40))
    shadow.setOffset(0, 8)
    widget.setGraphicsEffect(shadow)

# ---------------------------------------------------------
# PREMIUM 2026 DARK THEME (Default)
# Inspired by Linear, Notion, and Windows 11 Fluent Design
# ---------------------------------------------------------
DARK_THEME = """
QWidget {
    font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Cairo', 'Tajawal', system-ui, sans-serif;
    font-size: 14px;
    color: #F4F4F5;
    background-color: #09090B;
}

QMainWindow {
    background-color: #09090B;
}

/* Sidebar & Headers */
QFrame#Sidebar {
    background-color: #18181B;
    border-left: 1px solid #27272A; /* RTL border */
    border-right: none;
}

QFrame#Header {
    background-color: #09090B;
    border-bottom: 1px solid #27272A;
}

/* Cards */
QFrame#Card, QFrame#ProductCard {
    background-color: #18181B;
    border: 1px solid #27272A;
    border-radius: 16px;
}

QFrame#ProductCard:hover {
    border: 1px solid #6366F1;
    background-color: #27272A;
}

QFrame#TotalsCard {
    background-color: #09090B;
    border: 1px solid #27272A;
    border-radius: 16px;
}

/* Typography */
QLabel[cssClass="view-title"] {
    font-size: 28px;
    font-weight: 800;
    color: #FFFFFF;
    background: transparent;
    letter-spacing: -0.5px;
}

QLabel[cssClass="card-title"] {
    font-size: 14px;
    font-weight: 600;
    color: #A1A1AA;
    background: transparent;
}

QLabel[cssClass="card-value"] {
    font-size: 32px;
    font-weight: 800;
    color: #FFFFFF;
    background: transparent;
    letter-spacing: -1px;
}

/* Buttons */
QPushButton {
    background-color: #27272A;
    border: 1px solid #3F3F46;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
    color: #F4F4F5;
}

QPushButton:hover {
    background-color: #3F3F46;
    border-color: #52525B;
}

QPushButton:pressed {
    background-color: #18181B;
}

QPushButton[cssClass="primary"] {
    background-color: #6366F1;
    color: #FFFFFF;
    border: none;
}
QPushButton[cssClass="primary"]:hover {
    background-color: #4F46E5;
}

QPushButton[cssClass="success"] {
    background-color: #10B981;
    color: #FFFFFF;
    border: none;
}
QPushButton[cssClass="success"]:hover {
    background-color: #059669;
}

QPushButton[cssClass="danger"] {
    background-color: #EF4444;
    color: #FFFFFF;
    border: none;
}
QPushButton[cssClass="danger"]:hover {
    background-color: #DC2626;
}

QPushButton[cssClass="pay-btn"] {
    background-color: #6366F1;
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 800;
    padding: 18px;
    border-radius: 12px;
    border: none;
}
QPushButton[cssClass="pay-btn"]:hover {
    background-color: #4F46E5;
}

/* Sidebar Navigation Buttons */
QPushButton#SidebarBtn {
    text-align: right;
    padding: 14px 18px;
    border: none;
    border-radius: 10px;
    background: transparent;
    font-size: 15px;
    font-weight: 600;
    color: #A1A1AA;
}
QPushButton#SidebarBtn:hover {
    background-color: #27272A;
    color: #FFFFFF;
}
QPushButton#SidebarBtn:checked {
    background-color: #3730A3;
    color: #FFFFFF;
}

/* Inputs & Form Controls */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #18181B;
    border: 1px solid #3F3F46;
    border-radius: 10px;
    padding: 10px 14px;
    color: #F4F4F5;
    selection-background-color: #6366F1;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
    border: 1px solid #6366F1;
    background-color: #27272A;
}

/* Modern Tables */
QTableWidget {
    background-color: #18181B;
    border: 1px solid #27272A;
    border-radius: 16px;
    gridline-color: transparent;
    alternate-background-color: #09090B;
    selection-background-color: #3730A3;
    selection-color: #FFFFFF;
    outline: none;
}

QTableWidget::item {
    padding: 16px;
    border-bottom: 1px solid #27272A;
}

QHeaderView::section {
    background-color: #09090B;
    color: #A1A1AA;
    font-weight: 700;
    font-size: 13px;
    padding: 16px;
    border: none;
    border-bottom: 1px solid #27272A;
    text-align: right;
}

/* Scrollbars */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #3F3F46;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #52525B;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

# ---------------------------------------------------------
# PREMIUM 2026 LIGHT THEME (Optional)
# ---------------------------------------------------------
LIGHT_THEME = """
QWidget {
    font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Cairo', 'Tajawal', system-ui, sans-serif;
    font-size: 14px;
    color: #09090B;
    background-color: #F4F4F5;
}

QMainWindow {
    background-color: #F4F4F5;
}

/* Sidebar & Headers */
QFrame#Sidebar {
    background-color: #FFFFFF;
    border-left: 1px solid #E4E4E7;
    border-right: none;
}

QFrame#Header {
    background-color: #F4F4F5;
    border-bottom: 1px solid #E4E4E7;
}

/* Cards */
QFrame#Card, QFrame#ProductCard {
    background-color: #FFFFFF;
    border: 1px solid #E4E4E7;
    border-radius: 16px;
}

QFrame#ProductCard:hover {
    border: 1px solid #4F46E5;
    background-color: #F8FAFC;
}

QFrame#TotalsCard {
    background-color: #F4F4F5;
    border: 1px solid #E4E4E7;
    border-radius: 16px;
}

/* Typography */
QLabel[cssClass="view-title"] {
    font-size: 28px;
    font-weight: 800;
    color: #09090B;
    background: transparent;
    letter-spacing: -0.5px;
}

QLabel[cssClass="card-title"] {
    font-size: 14px;
    font-weight: 600;
    color: #71717A;
    background: transparent;
}

QLabel[cssClass="card-value"] {
    font-size: 32px;
    font-weight: 800;
    color: #09090B;
    background: transparent;
    letter-spacing: -1px;
}

/* Buttons */
QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #D4D4D8;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
    color: #18181B;
}

QPushButton:hover {
    background-color: #F4F4F5;
    border-color: #A1A1AA;
}

QPushButton:pressed {
    background-color: #E4E4E7;
}

QPushButton[cssClass="primary"] {
    background-color: #4F46E5;
    color: #FFFFFF;
    border: none;
}
QPushButton[cssClass="primary"]:hover {
    background-color: #4338CA;
}

QPushButton[cssClass="success"] {
    background-color: #10B981;
    color: #FFFFFF;
    border: none;
}
QPushButton[cssClass="success"]:hover {
    background-color: #059669;
}

QPushButton[cssClass="danger"] {
    background-color: #EF4444;
    color: #FFFFFF;
    border: none;
}
QPushButton[cssClass="danger"]:hover {
    background-color: #DC2626;
}

QPushButton[cssClass="pay-btn"] {
    background-color: #4F46E5;
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 800;
    padding: 18px;
    border-radius: 12px;
    border: none;
}
QPushButton[cssClass="pay-btn"]:hover {
    background-color: #4338CA;
}

/* Sidebar Navigation Buttons */
QPushButton#SidebarBtn {
    text-align: right;
    padding: 14px 18px;
    border: none;
    border-radius: 10px;
    background: transparent;
    font-size: 15px;
    font-weight: 600;
    color: #71717A;
}
QPushButton#SidebarBtn:hover {
    background-color: #F4F4F5;
    color: #09090B;
}
QPushButton#SidebarBtn:checked {
    background-color: #E0E7FF;
    color: #4F46E5;
}

/* Inputs & Form Controls */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #D4D4D8;
    border-radius: 10px;
    padding: 10px 14px;
    color: #09090B;
    selection-background-color: #4F46E5;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
    border: 1px solid #4F46E5;
    background-color: #FFFFFF;
}

/* Modern Tables */
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E4E4E7;
    border-radius: 16px;
    gridline-color: transparent;
    alternate-background-color: #FAFAFA;
    selection-background-color: #E0E7FF;
    selection-color: #09090B;
    outline: none;
}

QTableWidget::item {
    padding: 16px;
    border-bottom: 1px solid #E4E4E7;
}

QHeaderView::section {
    background-color: #F4F4F5;
    color: #71717A;
    font-weight: 700;
    font-size: 13px;
    padding: 16px;
    border: none;
    border-bottom: 1px solid #E4E4E7;
    text-align: right;
}

/* Scrollbars */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #D4D4D8;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #A1A1AA;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
