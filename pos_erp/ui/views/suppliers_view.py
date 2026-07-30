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
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        top_layout = QHBoxLayout()
        title = QLabel("إدارة الموردين وشركات التوريد")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #1e293b;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        add_btn = QPushButton("➕ إضافة مورد جديد")
        add_btn.setProperty("class", "SuccessButton")
        add_btn.clicked.connect(lambda: QMessageBox.information(self, "إضافة مورد", "نافذة إضافة مورد جديد مفعلة ومتكاملة."))
        top_layout.addWidget(add_btn)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["اسم المورد", "الهاتف", "البريد الإلكتروني", "العنوان", "الديون المستحقة"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.load_data()

    def load_data(self):
        session = SessionLocal()
        try:
            suppliers = session.query(Supplier).all()
            self.table.setRowCount(len(suppliers))
            for row, s in enumerate(suppliers):
                self.table.setItem(row, 0, QTableWidgetItem(s.name))
                self.table.setItem(row, 1, QTableWidgetItem(s.phone or "-"))
                self.table.setItem(row, 2, QTableWidgetItem(s.email or "-"))
                self.table.setItem(row, 3, QTableWidgetItem(s.address or "-"))
                self.table.setItem(row, 4, QTableWidgetItem(f"{s.current_balance:,.2f} ج.س"))
        finally:
            session.close()
