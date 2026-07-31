from pos_erp.ui.animations import Animations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
from pos_erp.services.finance_service import FinanceService

class ExpensesView(QWidget):
    """
    إدارة تسجيل المصروفات اليومية والتشغيلية وخصمها من الصناديق.
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
        title = QLabel("إدارة المصروفات والنثريات")
        title.setProperty("cssClass", "view-title")
        top_layout.addWidget(title)
        top_layout.addStretch()

        add_btn = QPushButton("➕ تسجيل مصروف جديد")
        add_btn.setProperty("cssClass", "danger")
        add_btn.clicked.connect(self.add_expense_quick)
        top_layout.addWidget(add_btn)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["فئة المصروف", "المبلغ", "تاريخ الصرف", "الملاحظات والبيان"])
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
        expenses = FinanceService.get_expenses()
        self.table.setRowCount(0) # Clear previous rows to prevent leaks
            Animations.pop_in(self.table, 500)
        self.table.setRowCount(len(expenses))
        for row, e in enumerate(expenses):
            self.table.setItem(row, 0, QTableWidgetItem(e.category))
            self.table.setItem(row, 1, QTableWidgetItem(f"{e.amount:,.2f} ج.س"))
            self.table.setItem(row, 2, QTableWidgetItem(str(e.date)))
            self.table.setItem(row, 3, QTableWidgetItem(e.notes or "-"))

    def add_expense_quick(self):
        data = {'category': 'مصاريف تشغيلية متنوعة', 'amount': 250.0, 'notes': 'مصروف تجريبي مسجل بالسيستم'}
        success, msg = FinanceService.add_expense(data, self.current_user.id)
        if success:
            QMessageBox.information(self, "نجاح", msg)
            self.load_data()
        else:
            QMessageBox.critical(self, "خطأ", msg)
