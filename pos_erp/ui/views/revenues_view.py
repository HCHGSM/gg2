from pos_erp.ui.animations import Animations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
from pos_erp.services.finance_service import FinanceService

class RevenuesView(QWidget):
    """
    إدارة وتسجيل الإيرادات الأخرى غير الناتجة عن المبيعات المباشرة.
    """
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        top_layout = QHBoxLayout()
        title = QLabel("إدارة الإيرادات الأخرى والواردات")
        title.setProperty("cssClass", "view-title")
        top_layout.addWidget(title)
        top_layout.addStretch()

        add_btn = QPushButton("➕ تسجيل إيراد جديد")
        add_btn.setProperty("cssClass", "success")
        add_btn.clicked.connect(self.add_revenue_quick)
        top_layout.addWidget(add_btn)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["فئة الإيراد", "المبلغ", "التاريخ", "الملاحظات والبيان"])
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
        revenues = FinanceService.get_revenues()
        self.table.setRowCount(0) # Clear previous rows to prevent leaks
            Animations.pop_in(self.table, 500)
        self.table.setRowCount(len(revenues))
        for row, r in enumerate(revenues):
            self.table.setItem(row, 0, QTableWidgetItem(r.category))
            self.table.setItem(row, 1, QTableWidgetItem(f"{r.amount:,.2f} ج.س"))
            self.table.setItem(row, 2, QTableWidgetItem(str(r.date)))
            self.table.setItem(row, 3, QTableWidgetItem(r.notes or "-"))

    def add_revenue_quick(self):
        data = {'category': 'إيرادات أرباح استثمارية', 'amount': 1000.0, 'notes': 'إيراد تجريبي مسجل بالسيستم'}
        success, msg = FinanceService.add_revenue(data, self.current_user.id)
        if success:
            QMessageBox.information(self, "نجاح", msg)
            self.load_data()
        else:
            QMessageBox.critical(self, "خطأ", msg)
