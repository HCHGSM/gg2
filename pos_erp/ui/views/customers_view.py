from pos_erp.ui.dialogs import CustomerForm
from pos_erp.services.crm_service import CRMService
from pos_erp.ui.animations import ToastManager
from pos_erp.ui.worker import Worker
from PySide6.QtCore import QThreadPool
from pos_erp.ui.animations import Animations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Customer

class CustomersView(QWidget):
    """
    إدارة قاعدة بيانات العملاء، بيانات الاتصال، وأرصدة الديون والحسابات.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        top_layout = QHBoxLayout()
        title = QLabel("إدارة العملاء والحسابات التجارية")
        title.setProperty("cssClass", "view-title")
        top_layout.addWidget(title)
        top_layout.addStretch()

        add_btn = QPushButton("➕ إضافة عميل جديد")
        add_btn.setProperty("cssClass", "success")
        add_btn.clicked.connect(self.show_add_dialog)
        top_layout.addWidget(add_btn)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["اسم العميل", "رقم الهاتف", "البريد الإلكتروني", "العنوان", "الرصيد الحالي / المديونية"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)
        
        self.load_data()

    def load_data(self):
        session = SessionLocal()
        try:
            customers = session.query(Customer).all()
            self.table.setRowCount(0) # Clear previous rows to prevent leaks
            Animations.pop_in(self.table, 500)
            self.table.setRowCount(len(customers))
            for row, c in enumerate(customers):
                self.table.setItem(row, 0, QTableWidgetItem(c.name))
                self.table.setItem(row, 1, QTableWidgetItem(c.phone or "-"))
                self.table.setItem(row, 2, QTableWidgetItem(c.email or "-"))
                self.table.setItem(row, 3, QTableWidgetItem(c.address or "-"))
                self.table.setItem(row, 4, QTableWidgetItem(f"{c.current_balance:,.2f} ج.س"))
        finally:
            session.close()

    def show_add_dialog(self):
        dialog = CustomerForm(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                ToastManager.show_error(self.window(), "اسم العميل مطلوب")
                return
            success, msg = CRMService.add_customer(data)
            if success:
                ToastManager.show_success(self.window(), msg)
                self.load_data()
            else:
                ToastManager.show_error(self.window(), msg)
