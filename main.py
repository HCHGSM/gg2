import os
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from pos_erp.database.db import init_db
from pos_erp.ui.login_window import LoginWindow
from pos_erp.ui.main_window import MainWindow


def _resource_path(relative_path):
    """Resolve a bundled resource path whether running from source or from a
    frozen PyInstaller onefile exe (which extracts data to sys._MEIPASS)."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def main():
    # Initialize database and seed default data
    init_db()

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)

    icon_path = _resource_path(os.path.join('assets', 'icons', 'app_icon.ico'))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    main_window = None

    def on_login_success(user):
        nonlocal main_window
        main_window = MainWindow(user)
        main_window.show()

    login_win = LoginWindow(on_login_success)
    login_win.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
