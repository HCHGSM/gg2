from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

def apply_card_shadow(widget, is_dark=False):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(20)
    if is_dark:
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
    else:
        # Claude light theme has very subtle, soft shadows
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
    widget.setGraphicsEffect(shadow)

DARK_THEME = """
QWidget {
    font-family: 'Inter', 'Tajawal', 'Segoe UI', system-ui, sans-serif;
    font-size: 15px;
    color: #F4F4F5;
    background-color: #09090B;
}

QMainWindow {
    background-color: #09090B;
}

QFrame#Sidebar {
    background-color: #18181B;
    border-left: 1px solid #27272A;
    border-right: none;
}

QFrame#Header {
    background-color: #09090B;
    border-bottom: 1px solid #27272A;
}

QFrame#Card, QFrame#ProductCard {
    background-color: #18181B;
    border: 1px solid #27272A;
    border-radius: 12px;
}

QFrame#ProductCard:hover {
    border: 1px solid #6366F1;
    background-color: #27272A;
}

QFrame#TotalsCard {
    background-color: #09090B;
    border: 1px solid #27272A;
    border-radius: 12px;
}

QLabel[cssClass="view-title"] {
    font-size: 26px;
    font-weight: 800;
    color: #FFFFFF;
    background: transparent;
}

QLabel[cssClass="card-title"] {
    font-size: 15px;
    font-weight: 600;
    color: #A1A1AA;
    background: transparent;
}

QLabel[cssClass="card-value"] {
    font-size: 32px;
    font-weight: 800;
    color: #FFFFFF;
    background: transparent;
}

QPushButton {
    background-color: #27272A;
    border: 1px solid #3F3F46;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
    color: #F4F4F5;
}

QPushButton:hover {
    background-color: #3F3F46;
    border-color: #52525B;
}

QPushButton[cssClass="primary"], QPushButton[cssClass="pay-btn"] {
    background-color: #FFFFFF;
    color: #000000;
    border: none;
}
QPushButton[cssClass="primary"]:hover, QPushButton[cssClass="pay-btn"]:hover {
    background-color: #E4E4E7;
}

QPushButton[cssClass="success"] {
    background-color: #10B981;
    color: #FFFFFF;
    border: none;
}

QPushButton[cssClass="danger"] {
    background-color: #EF4444;
    color: #FFFFFF;
    border: none;
}

QPushButton#SidebarBtn {
    text-align: right;
    padding: 12px 16px;
    border: none;
    border-radius: 8px;
    background: transparent;
    font-size: 16px;
    font-weight: 600;
    color: #A1A1AA;
}
QPushButton#SidebarBtn:hover {
    background-color: #27272A;
    color: #FFFFFF;
}
QPushButton#SidebarBtn:checked {
    background-color: #FFFFFF;
    color: #000000;
}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #18181B;
    border: 1px solid #3F3F46;
    border-radius: 8px;
    padding: 10px 14px;
    color: #F4F4F5;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
    border: 1px solid #FFFFFF;
    background-color: #27272A;
}

QTableWidget {
    background-color: #18181B;
    border: 1px solid #27272A;
    border-radius: 12px;
    gridline-color: transparent;
    alternate-background-color: #09090B;
    selection-background-color: #3F3F46;
    selection-color: #FFFFFF;
    outline: none;
}

QTableWidget::item {
    padding: 14px;
    border-bottom: 1px solid #27272A;
}

QHeaderView::section {
    background-color: #09090B;
    color: #A1A1AA;
    font-weight: 700;
    font-size: 14px;
    padding: 14px;
    border: none;
    border-bottom: 1px solid #27272A;
    text-align: right;
}
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
"""

# CLAUDE AI INSPIRED LIGHT THEME
LIGHT_THEME = """
QWidget {
    font-family: 'Inter', 'Tajawal', 'Segoe UI', system-ui, sans-serif;
    font-size: 15px;
    color: #201E1D;
    background-color: #FFFFFF;
}

QMainWindow {
    background-color: #FFFFFF;
}

QFrame#Sidebar {
    background-color: #F3F3EE;
    border-left: 1px solid #E6E4DD;
    border-right: none;
}

QFrame#Header {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E6E4DD;
}

QFrame#Card, QFrame#ProductCard {
    background-color: #FFFFFF;
    border: 1px solid #E6E4DD;
    border-radius: 12px;
}

QFrame#ProductCard:hover {
    border: 1px solid #D97757;
    background-color: #FCFCFA;
}

QFrame#TotalsCard {
    background-color: #F9F8F6;
    border: 1px solid #E6E4DD;
    border-radius: 12px;
}

QLabel[cssClass="view-title"] {
    font-size: 26px;
    font-weight: 800;
    color: #201E1D;
    background: transparent;
}

QLabel[cssClass="card-title"] {
    font-size: 15px;
    font-weight: 600;
    color: #797671;
    background: transparent;
}

QLabel[cssClass="card-value"] {
    font-size: 32px;
    font-weight: 800;
    color: #D97757;
    background: transparent;
}

QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #E6E4DD;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
    color: #201E1D;
}

QPushButton:hover {
    background-color: #F9F8F6;
    border-color: #CFCDBB;
}

QPushButton:pressed {
    background-color: #E6E4DD;
}

QPushButton[cssClass="primary"], QPushButton[cssClass="pay-btn"] {
    background-color: #201E1D;
    color: #FFFFFF;
    border: none;
}
QPushButton[cssClass="primary"]:hover, QPushButton[cssClass="pay-btn"]:hover {
    background-color: #4A4744;
}

QPushButton[cssClass="success"] {
    background-color: #D97757;
    color: #FFFFFF;
    border: none;
}
QPushButton[cssClass="success"]:hover {
    background-color: #C06649;
}

QPushButton[cssClass="danger"] {
    background-color: #E5484D;
    color: #FFFFFF;
    border: none;
}
QPushButton[cssClass="danger"]:hover {
    background-color: #CE4045;
}

QPushButton#SidebarBtn {
    text-align: right;
    padding: 12px 16px;
    border: none;
    border-radius: 8px;
    background: transparent;
    font-size: 16px;
    font-weight: 600;
    color: #797671;
}
QPushButton#SidebarBtn:hover {
    background-color: #E6E4DD;
    color: #201E1D;
}
QPushButton#SidebarBtn:checked {
    background-color: #201E1D;
    color: #FFFFFF;
}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #E6E4DD;
    border-radius: 8px;
    padding: 10px 14px;
    color: #201E1D;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
    border: 1px solid #D97757;
}

QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E6E4DD;
    border-radius: 12px;
    gridline-color: transparent;
    alternate-background-color: #F9F8F6;
    selection-background-color: #F3F3EE;
    selection-color: #201E1D;
    outline: none;
}

QTableWidget::item {
    padding: 14px;
    border-bottom: 1px solid #E6E4DD;
}

QHeaderView::section {
    background-color: #F9F8F6;
    color: #797671;
    font-weight: 700;
    font-size: 14px;
    padding: 14px;
    border: none;
    border-bottom: 1px solid #E6E4DD;
    text-align: right;
}

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
"""
