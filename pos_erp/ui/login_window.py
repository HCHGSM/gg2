from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QCheckBox
)
from PySide6.QtCore import Qt
from pos_erp.services.auth_service import AuthService

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("تسجيل الدخول - نظام المبيعات المتكامل")
        self.resize(450, 380)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setStyleSheet("""
            #loginCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        card_layout = QVBoxLayout(card)

        title_label = QLabel("تسجيل الدخول للنظام")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e293b; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم (مثال: admin)")
        self.username_input.setFixedHeight(40)
        card_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(40)
        card_layout.addWidget(self.password_input)

        self.remember_check = QCheckBox("تذكرني")
        card_layout.addWidget(self.remember_check)

        login_btn = QPushButton("دخول")
        login_btn.setObjectName("loginBtn")
        login_btn.setFixedHeight(42)
        login_btn.setStyleSheet("""
            QPushButton#loginBtn {
                background-color: #3b82f6;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                font-size: 15px;
            }
            QPushButton#loginBtn:hover {
                background-color: #2563eb;
            }
        """)
        login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(login_btn)

        main_layout.addWidget(card)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم المستخدم وكلمة المرور")
            return

        user, msg = AuthService.authenticate(username, password)
        if user:
            self.on_login_success(user)
            self.close()
        else:
            QMessageBox.critical(self, "خطأ في تسجيل الدخول", msg)
