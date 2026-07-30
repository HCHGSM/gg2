LIGHT_THEME = """
/* ==========================================================================
   Ultra-Modern Vibrant SaaS Light Theme (Inspired by Stripe, Odoo, Linear)
   ========================================================================== */

QWidget {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Cairo', Arial, sans-serif;
    font-size: 14px;
    color: #1e293b;
    background-color: #f8fafc;
}

QMainWindow {
    background-color: #f1f5f9;
}

/* Sidebar Navigation - Deep Elegant Gradient Slate */
#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0f172a, stop:1 #1e293b);
    border-right: 1px solid #334155;
}

#sidebar QLabel {
    color: #f8fafc;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 0.5px;
    padding: 10px 15px;
}

#sidebar QPushButton {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    text-align: left;
    padding: 12px 18px;
    border-radius: 8px;
    margin: 3px 10px;
    font-weight: 600;
    font-size: 14px;
}

#sidebar QPushButton:hover {
    background-color: rgba(59, 130, 246, 0.15);
    color: #ffffff;
}

#sidebar QPushButton:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #6366f1);
    color: #ffffff;
    font-weight: 700;
}

/* Header Bar */
#header {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 12px 24px;
}

/* Gorgeous Vibrant Cards */
.Card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
}

/* Vibrant Buttons with Gradients & Glow */
QPushButton.PrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 14px;
}
QPushButton.PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
}

QPushButton.SuccessButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 14px;
}
QPushButton.SuccessButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #047857);
}

QPushButton.DangerButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #dc2626);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 14px;
}
QPushButton.DangerButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #dc2626, stop:1 #b91c1c);
}

QPushButton.WarningButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
}
QPushButton.WarningButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #b45309);
}

/* Tables & Data Grids */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    gridline-color: #f1f5f9;
    selection-background-color: #eff6ff;
    selection-color: #1e293b;
}

QHeaderView::section {
    background-color: #f8fafc;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #cbd5e1;
    font-weight: bold;
    color: #475569;
}

/* Form Inputs */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #3b82f6;
    background-color: #ffffff;
}
"""

DARK_THEME = """
/* ==========================================================================
   Ultra-Modern Vibrant SaaS Dark Theme (Deep Midnight Obsidian & Neon Accents)
   ========================================================================== */

QWidget {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Cairo', Arial, sans-serif;
    font-size: 14px;
    color: #f1f5f9;
    background-color: #0b0f19;
}

QMainWindow {
    background-color: #030712;
}

#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0f172a, stop:1 #020617);
    border-right: 1px solid #1e293b;
}

#sidebar QLabel {
    color: #38bdf8;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 0.5px;
    padding: 10px 15px;
}

#sidebar QPushButton {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    text-align: left;
    padding: 12px 18px;
    border-radius: 8px;
    margin: 3px 10px;
    font-weight: 600;
    font-size: 14px;
}

#sidebar QPushButton:hover {
    background-color: rgba(56, 189, 248, 0.15);
    color: #38bdf8;
}

#sidebar QPushButton:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #2563eb);
    color: #ffffff;
    font-weight: 700;
}

#header {
    background-color: #0f172a;
    border-bottom: 1px solid #1e293b;
    padding: 12px 24px;
}

.Card {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 20px;
}

QPushButton.PrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #2563eb);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 14px;
}
QPushButton.PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369a1, stop:1 #1d4ed8);
}

QPushButton.SuccessButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #047857);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 14px;
}
QPushButton.SuccessButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #047857, stop:1 #065f46);
}

QPushButton.DangerButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #dc2626, stop:1 #b91c1c);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 14px;
}
QPushButton.DangerButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b91c1c, stop:1 #991b1b);
}

QPushButton.WarningButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #b45309);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
}
QPushButton.WarningButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b45309, stop:1 #92400e);
}

QTableWidget {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    gridline-color: #1e293b;
    selection-background-color: #1e293b;
    selection-color: #38bdf8;
    color: #f1f5f9;
}

QHeaderView::section {
    background-color: #1e293b;
    padding: 10px;
    border: none;
    font-weight: bold;
    color: #38bdf8;
}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    color: #f1f5f9;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #38bdf8;
    background-color: #0f172a;
}
"""
