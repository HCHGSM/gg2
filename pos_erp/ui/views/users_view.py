from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import User

class UsersView(QWidget):
    """
    إدارة المستخدمين وصلاحياتهم وسجل نشاطاتهم في النظام.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel("إدارة المستخدمين وصلاحيات النظام")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #1e293b;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["اسم المستخدم", "الاسم الكامل", "البريد الإلكتروني", "حالة الحساب", "آخر تسجيل دخول"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.load_data()

    def load_data(self):
        session = SessionLocal()
        try:
            users = session.query(User).all()
            self.table.setRowCount(len(users))
            for row, u in enumerate(users):
                self.table.setItem(row, 0, QTableWidgetItem(u.username))
                self.table.setItem(row, 1, QTableWidgetItem(u.full_name))
                self.table.setItem(row, 2, QTableWidgetItem(u.email or "-"))
                self.table.setItem(row, 3, QTableWidgetItem("🟢 نشط" if u.is_active else "🔴 معطل"))
                self.table.setItem(row, 4, QTableWidgetItem(str(u.last_login or "لم يسجل دخول بعد")))
        finally:
            session.close()
