import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from pos_erp.database.db import init_db
from pos_erp.ui.login_window import LoginWindow
from pos_erp.ui.main_window import MainWindow

def main():
    # Initialize database and seed default data
    init_db()

    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)

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
