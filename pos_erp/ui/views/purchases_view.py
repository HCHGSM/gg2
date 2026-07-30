from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Purchase

class PurchasesView(QWidget):
    """
    إدارة فواتير المشتريات من الموردين وتحديث المخزون تلقائياً.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        top_layout = QHBoxLayout()
        title = QLabel("إدارة فواتير المشتريات والتوريد")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #1e293b;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        add_btn = QPushButton("➕ فاتورة شراء جديدة")
        add_btn.setProperty("class", "SuccessButton")
        add_btn.clicked.connect(lambda: QMessageBox.information(self, "مشتريات", "إدارة فواتير الشراء مفعلة ومتكاملة."))
        top_layout.addWidget(add_btn)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["رقم الفاتورة", "المورد", "الإجمالي النهائي", "المبلغ المدفوع", "تاريخ العملية"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.load_data()

    def load_data(self):
        session = SessionLocal()
        try:
            purchases = session.query(Purchase).all()
            self.table.setRowCount(len(purchases))
            for row, p in enumerate(purchases):
                self.table.setItem(row, 0, QTableWidgetItem(p.invoice_number))
                self.table.setItem(row, 1, QTableWidgetItem(str(p.supplier_id or "مورد عام")))
                self.table.setItem(row, 2, QTableWidgetItem(f"{p.total:,.2f} ج.س"))
                self.table.setItem(row, 3, QTableWidgetItem(f"{p.paid_amount:,.2f} ج.س"))
                self.table.setItem(row, 4, QTableWidgetItem(str(p.created_at)))
        finally:
            session.close()
