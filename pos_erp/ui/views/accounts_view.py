from pos_erp.ui.animations import Animations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from pos_erp.services.finance_service import FinanceService

class AccountsView(QWidget):
    """
    إدارة الصناديق النقدية، الحسابات البنكية، والأرصدة المالية.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        title = QLabel("الحسابات المالية والصناديق والبنوك")
        title.setProperty("cssClass", "view-title")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["اسم الحساب / الصندوق", "نوع الحساب", "رقم الحساب المرجعي", "الرصيد المتاح الحالي"])
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
        accounts = FinanceService.get_accounts()
        self.table.setRowCount(0)
        Animations.pop_in(self.table, 500) # Clear previous rows to prevent leaks
        self.table.setRowCount(len(accounts))
        for row, a in enumerate(accounts):
            self.table.setItem(row, 0, QTableWidgetItem(a.name))
            self.table.setItem(row, 1, QTableWidgetItem(a.account_type))
            self.table.setItem(row, 2, QTableWidgetItem(a.account_number or "-"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{a.balance:,.2f} ج.س"))
