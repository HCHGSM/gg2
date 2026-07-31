from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QCheckBox
)
from PySide6.QtCore import Qt
from pos_erp.services.auth_service import AuthService
from pos_erp.ui.styles import DARK_THEME, apply_card_shadow
from pos_erp.ui.animations import Animations

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Smart ERP - Login")
        self.resize(1000, 600)
        self.setStyleSheet(DARK_THEME)
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Branding Side
        brand_frame = QFrame()
        brand_frame.setStyleSheet("background-color: #09090B;")
        brand_layout = QVBoxLayout(brand_frame)
        brand_layout.setAlignment(Qt.AlignCenter)
        
        logo = QLabel("✧")
        logo.setStyleSheet("font-size: 80px; color: #6366F1; font-weight: 900;")
        logo.setAlignment(Qt.AlignCenter)
        brand_layout.addWidget(logo)
        
        brand_title = QLabel("Smart ERP 2026")
        brand_title.setStyleSheet("font-size: 36px; font-weight: 900; color: #FFFFFF; letter-spacing: -1px;")
        brand_title.setAlignment(Qt.AlignCenter)
        brand_layout.addWidget(brand_title)
        
        brand_sub = QLabel("نظام إدارة المؤسسات الحديث والموثوق")
        brand_sub.setStyleSheet("font-size: 16px; color: #A1A1AA;")
        brand_sub.setAlignment(Qt.AlignCenter)
        brand_layout.addWidget(brand_sub)
        
        main_layout.addWidget(brand_frame, stretch=1)

        # Right Login Side
        login_wrapper = QFrame()
        login_wrapper.setStyleSheet("background-color: #18181B;")
        wrapper_layout = QVBoxLayout(login_wrapper)
        wrapper_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(24)

        title = QLabel("تسجيل الدخول")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: #FFFFFF;")
        card_layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم (admin)")
        self.username_input.setFixedHeight(50)
        self.username_input.setStyleSheet("font-size: 15px;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور (admin123)")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(50)
        self.password_input.setStyleSheet("font-size: 15px;")

        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.handle_login)

        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)

        self.show_pass_cb = QCheckBox("إظهار كلمة المرور")
        self.show_pass_cb.setStyleSheet("color: #A1A1AA; font-size: 14px;")
        self.show_pass_cb.stateChanged.connect(self.toggle_password)
        card_layout.addWidget(self.show_pass_cb)
        
        self.login_btn = QPushButton("الدخول إلى النظام ➔")
        self.login_btn.setProperty("cssClass", "primary")
        self.login_btn.setFixedHeight(55)
        self.login_btn.setStyleSheet("font-size: 16px; font-weight: bold; border-radius: 12px;")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_btn)

        self.card = card
        wrapper_layout.addWidget(card)
        main_layout.addWidget(login_wrapper, stretch=1)
        
        Animations.fade_in(self, 800)

    def toggle_password(self, state):
        if state == Qt.Checked.value:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم المستخدم وكلمة المرور")
            return

        user, msg = AuthService.authenticate(username, password)
        if user:
            Animations.fade_out(self, 400, lambda: self.on_login_success(user))
        else:
            Animations.shake(self.card)
            QMessageBox.critical(self, "خطأ في تسجيل الدخول", msg)
