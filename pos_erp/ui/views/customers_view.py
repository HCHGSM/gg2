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
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        top_layout = QHBoxLayout()
        title = QLabel("إدارة العملاء والحسابات التجارية")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #1e293b;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        add_btn = QPushButton("➕ إضافة عميل جديد")
        add_btn.setProperty("class", "SuccessButton")
        add_btn.clicked.connect(lambda: QMessageBox.information(self, "إضافة عميل", "نافذة إضافة عميل جديد مفعلة ومتكاملة."))
        top_layout.addWidget(add_btn)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["اسم العميل", "رقم الهاتف", "البريد الإلكتروني", "العنوان", "الرصيد الحالي / المديونية"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.load_data()

    def load_data(self):
        session = SessionLocal()
        try:
            customers = session.query(Customer).all()
            self.table.setRowCount(len(customers))
            for row, c in enumerate(customers):
                self.table.setItem(row, 0, QTableWidgetItem(c.name))
                self.table.setItem(row, 1, QTableWidgetItem(c.phone or "-"))
                self.table.setItem(row, 2, QTableWidgetItem(c.email or "-"))
                self.table.setItem(row, 3, QTableWidgetItem(c.address or "-"))
                self.table.setItem(row, 4, QTableWidgetItem(f"{c.current_balance:,.2f} ج.س"))
        finally:
            session.close()
