from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QParallelAnimationGroup, QPropertyAnimation, QEasingCurve
from pos_erp.ui.styles import LIGHT_THEME, DARK_THEME
from pos_erp.ui.animations import Animations
from pos_erp.ui.views.dashboard_view import DashboardView
from pos_erp.ui.views.pos_view import POSView
from pos_erp.ui.views.products_view import ProductsView
from pos_erp.ui.views.inventory_view import InventoryView
from pos_erp.ui.views.customers_view import CustomersView
from pos_erp.ui.views.suppliers_view import SuppliersView
from pos_erp.ui.views.purchases_view import PurchasesView
from pos_erp.ui.views.expenses_view import ExpensesView
from pos_erp.ui.views.revenues_view import RevenuesView
from pos_erp.ui.views.accounts_view import AccountsView
from pos_erp.ui.views.reports_view import ReportsView
from pos_erp.ui.views.settings_view import SettingsView
from pos_erp.ui.views.users_view import UsersView

class MainWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.dark_mode = True # Default to 2026 Dark Theme
        self.sidebar_expanded = True
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Smart ERP - Enterprise 2026")
        self.resize(1440, 900)
        self.setStyleSheet(DARK_THEME)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Premium Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)
        sidebar_layout.setSpacing(6)

        # Logo Area
        logo_layout = QHBoxLayout()
        logo_icon = QLabel("✧")
        logo_icon.setStyleSheet("font-size: 28px; color: #6366F1; background: transparent;")
        self.logo_label = QLabel("Smart ERP")
        self.logo_label.setStyleSheet("font-size: 22px; font-weight: 900; background: transparent;")
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(self.logo_label)
        logo_layout.addStretch()
        sidebar_layout.addLayout(logo_layout)
        sidebar_layout.addSpacing(30)

        self.nav_buttons = []
        views = [
            ("📊", "لوحة التحكم", 0),
            ("🛒", "نقطة البيع (POS)", 1),
            ("📦", "المنتجات", 2),
            ("🏢", "المخزون", 3),
            ("👥", "العملاء", 4),
            ("🤝", "الموردين", 5),
            ("🛍️", "المشتريات", 6),
            ("💸", "المصروفات", 7),
            ("💰", "الإيرادات", 8),
            ("🏦", "الحسابات", 9),
            ("📈", "التقارير", 10),
            ("⚙️", "الإعدادات", 11),
            ("🔐", "المستخدمين", 12)
        ]

        for icon, text, index in views:
            btn = QPushButton(f"  {icon}    {text}")
            btn.setObjectName("SidebarBtn")
            btn.setProperty("icon_only", f" {icon} ")
            btn.setProperty("full_text", f"  {icon}    {text}")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=index: self.switch_view(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # --- Content Area ---
        content_wrapper = QWidget()
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Modern Header
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)

        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedSize(45, 45)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setStyleSheet("font-size: 22px; border: none; background: transparent; border-radius: 22px;")
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        header_layout.addWidget(self.toggle_btn)
        
        header_layout.addStretch()

        # User Info Pill
        user_pill = QFrame()
        user_pill.setStyleSheet("background-color: transparent; border: 1px solid #3F3F46; border-radius: 20px; padding: 5px 15px;")
        user_pill_layout = QHBoxLayout(user_pill)
        user_pill_layout.setContentsMargins(0, 0, 0, 0)
        
        user_icon = QLabel("👤")
        user_info = QLabel(self.current_user.full_name)
        user_info.setStyleSheet("font-weight: 600; background: transparent; border: none;")
        user_pill_layout.addWidget(user_icon)
        user_pill_layout.addWidget(user_info)
        header_layout.addWidget(user_pill)
        header_layout.addSpacing(15)

        theme_btn = QPushButton("🌓")
        theme_btn.setFixedSize(45, 45)
        theme_btn.setCursor(Qt.PointingHandCursor)
        theme_btn.setStyleSheet("font-size: 20px; border: none; background: transparent; border-radius: 22px;")
        theme_btn.setToolTip("تغيير المظهر")
        theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(theme_btn)

        logout_btn = QPushButton("🚪")
        logout_btn.setFixedSize(45, 45)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("font-size: 20px; border: none; background: transparent; border-radius: 22px; color: #EF4444;")
        logout_btn.setToolTip("تسجيل الخروج")
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)

        content_layout.addWidget(header)

        # Stacked Widget for Views
        self.stacked_widget = QStackedWidget()
        
        self.stacked_widget.addWidget(DashboardView())
        self.stacked_widget.addWidget(POSView(self.current_user))
        self.stacked_widget.addWidget(ProductsView(self.current_user))
        self.stacked_widget.addWidget(InventoryView())
        self.stacked_widget.addWidget(CustomersView())
        self.stacked_widget.addWidget(SuppliersView())
        self.stacked_widget.addWidget(PurchasesView())
        self.stacked_widget.addWidget(ExpensesView(self.current_user))
        self.stacked_widget.addWidget(RevenuesView(self.current_user))
        self.stacked_widget.addWidget(AccountsView())
        self.stacked_widget.addWidget(ReportsView())
        self.stacked_widget.addWidget(SettingsView())
        self.stacked_widget.addWidget(UsersView())

        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_wrapper)

        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)

    def toggle_sidebar(self):
        target_width = 80 if self.sidebar_expanded else 280
        
        self.anim_group = QParallelAnimationGroup()
        
        anim1 = QPropertyAnimation(self.sidebar, b"minimumWidth")
        anim1.setDuration(300)
        anim1.setEndValue(target_width)
        anim1.setEasingCurve(QEasingCurve.OutQuart)
        
        anim2 = QPropertyAnimation(self.sidebar, b"maximumWidth")
        anim2.setDuration(300)
        anim2.setEndValue(target_width)
        anim2.setEasingCurve(QEasingCurve.OutQuart)
        
        self.anim_group.addAnimation(anim1)
        self.anim_group.addAnimation(anim2)
        self.anim_group.start()
        
        if self.sidebar_expanded:
            self.logo_label.hide()
            for btn in self.nav_buttons:
                btn.setText(btn.property("icon_only"))
        else:
            self.logo_label.show()
            for btn in self.nav_buttons:
                btn.setText(btn.property("full_text"))
                
        self.sidebar_expanded = not self.sidebar_expanded

    def switch_view(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
            
        current_widget = self.stacked_widget.widget(index)
        if hasattr(current_widget, 'load_data'):
            current_widget.load_data()
            
        # Fade transition
        Animations.fade_in(current_widget, 300)
        self.stacked_widget.setCurrentIndex(index)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet(DARK_THEME)
        else:
            self.setStyleSheet(LIGHT_THEME)

    def logout(self):
        from pos_erp.ui.login_window import LoginWindow
        self.close()
        self.login_win = LoginWindow(self.on_login_success)
        self.login_win.show()

    def on_login_success(self, user):
        self.new_main = MainWindow(user)
        self.new_main.show()
        self.login_win.close()
