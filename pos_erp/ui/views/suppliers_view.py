from pos_erp.ui.dialogs import SupplierForm
from pos_erp.services.crm_service import CRMService
from pos_erp.ui.animations import ToastManager
from pos_erp.ui.worker import Worker
from PySide6.QtCore import QThreadPool
from pos_erp.ui.animations import Animations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Supplier

class SuppliersView(QWidget):
    """
    إدارة الموردين، سجل التوريدات، والمدفوعات والديون المستحقة.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        top_layout = QHBoxLayout()
        title = QLabel("إدارة الموردين وشركات التوريد")
        title.setProperty("cssClass", "view-title")
        top_layout.addWidget(title)
        top_layout.addStretch()

        add_btn = QPushButton("➕ إضافة مورد جديد")
        add_btn.setProperty("cssClass", "success")
        add_btn.clicked.connect(self.show_add_dialog)
        top_layout.addWidget(add_btn)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["اسم المورد", "الهاتف", "البريد الإلكتروني", "العنوان", "الديون المستحقة"])
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
            suppliers = session.query(Supplier).all()
            self.table.setRowCount(0)
        Animations.pop_in(self.table, 500) # Clear previous rows to prevent leaks
            self.table.setRowCount(len(suppliers))
            for row, s in enumerate(suppliers):
                self.table.setItem(row, 0, QTableWidgetItem(s.name))
                self.table.setItem(row, 1, QTableWidgetItem(s.phone or "-"))
                self.table.setItem(row, 2, QTableWidgetItem(s.email or "-"))
                self.table.setItem(row, 3, QTableWidgetItem(s.address or "-"))
                self.table.setItem(row, 4, QTableWidgetItem(f"{s.current_balance:,.2f} ج.س"))
        finally:
            session.close()

    def show_add_dialog(self):
        dialog = SupplierForm(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                ToastManager.show_error(self.window(), "اسم المورد مطلوب")
                return
            success, msg = CRMService.add_supplier(data)
            if success:
                ToastManager.show_success(self.window(), msg)
                self.load_data()
            else:
                ToastManager.show_error(self.window(), msg)
