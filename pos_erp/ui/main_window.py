from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QFrame
)
from PySide6.QtCore import Qt
from pos_erp.ui.styles import LIGHT_THEME, DARK_THEME
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
        self.dark_mode = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("نظام المبيعات المتكامل (POS & ERP) - الإصدار التجاري الاحترافي")
        self.resize(1280, 768)
        self.setStyleSheet(LIGHT_THEME)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(6)

        logo_label = QLabel("Smart POS & ERP")
        logo_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; margin-bottom: 20px; padding-left: 10px;")
        sidebar_layout.addWidget(logo_label)

        self.nav_buttons = []
        views = [
            ("لوحة التحكم", 0),
            ("نقطة البيع (POS)", 1),
            ("المنتجات", 2),
            ("المخزون", 3),
            ("العملاء", 4),
            ("الموردين", 5),
            ("المشتريات", 6),
            ("المصروفات", 7),
            ("الإيرادات", 8),
            ("الحسابات", 9),
            ("التقارير", 10),
            ("الإعدادات", 11),
            ("المستخدمين", 12)
        ]

        for text, index in views:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=index: self.switch_view(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        theme_btn = QPushButton("الوضع الليلي / النهاري")
        theme_btn.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(theme_btn)

        main_layout.addWidget(sidebar)

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

        main_layout.addWidget(self.stacked_widget)

        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)

    def switch_view(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.stacked_widget.setCurrentIndex(index)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet(DARK_THEME)
        else:
            self.setStyleSheet(LIGHT_THEME)
