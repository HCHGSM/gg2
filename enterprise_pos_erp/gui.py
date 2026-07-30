# -*- coding: utf-8 -*-
"""
=============================================================================
Module: enterprise_pos_erp/gui.py
Description: Professional Enterprise Desktop GUI using PySide6 (Qt6).
             Features modern SaaS UI/UX, vibrant gradients, POS touch terminal,
             inventory management, live analytics dashboard, and reports.
=============================================================================
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QMessageBox, QSplitter, QStackedWidget, QDialog, QFormLayout, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from enterprise_pos_erp.database import init_db, SessionLocal, Product, Sale, Customer, Supplier, Expense, Account, User
from enterprise_pos_erp.services import AuthService, ProductService, SalesService

THEME_QSS = """
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    color: #1e293b;
    background-color: #f8fafc;
}
QMainWindow {
    background-color: #f1f5f9;
}
#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0f172a, stop:1 #1e293b);
    border-right: 1px solid #334155;
}
#sidebar QPushButton {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    text-align: left;
    padding: 12px 18px;
    border-radius: 8px;
    margin: 3px 10px;
    font-weight: 600;
}
#sidebar QPushButton:hover {
    background-color: rgba(59, 130, 246, 0.15);
    color: #ffffff;
}
#sidebar QPushButton:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #6366f1);
    color: #ffffff;
    font-weight: 700;
}
.Card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
}
QPushButton.PrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
}
QPushButton.PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
}
QPushButton.SuccessButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
}
QPushButton.SuccessButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #047857);
}
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    gridline-color: #f1f5f9;
}
QHeaderView::section {
    background-color: #f8fafc;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #cbd5e1;
    font-weight: bold;
    color: #475569;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 12px;
}
"""

class LoginWindow(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("تسجيل الدخول - Enterprise ERP & POS")
        self.resize(450, 400)
        self.setStyleSheet("background-color: #0f172a; color: white;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setStyleSheet("background-color: #1e293b; border-radius: 12px; border: 1px solid #334155;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Enterprise ERP")
        title.setStyleSheet("font-size: 22px; font-weight: 900; color: #38bdf8;")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        sub = QLabel("نظام الإدارة التجارية المتقدم")
        sub.setStyleSheet("font-size: 12px; color: #94a3b8; margin-bottom: 20px;")
        sub.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(sub)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("اسم المستخدم (admin)")
        self.user_input.setFixedHeight = 40
        card_layout.addWidget(self.user_input)

        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("كلمة المرور (admin123)")
        self.pwd_input.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.pwd_input)

        login_btn = QPushButton("تسجيل الدخول للنظام")
        login_btn.setProperty("class", "PrimaryButton")
        login_btn.setFixedHeight = 45
        login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(login_btn)

        main_layout.addWidget(card)

    def handle_login(self):
        username = self.user_input.text().strip()
        password = self.pwd_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم المستخدم وكلمة المرور")
            return

        user, msg = AuthService.authenticate(username, password)
        if user:
            self.on_success(user)
            self.close()
        else:
            QMessageBox.critical(self, "خطأ", msg)

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        title = QLabel("لوحة التحكم والتحليلات المالية الحية")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #1e293b;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(20)

        self.c_sales = self.create_card("إجمالي المبيعات", "0.00 ج.س", "#3b82f6")
        self.c_prods = self.create_card("المنتجات المسجلة", "0", "#10b981")
        self.c_invoices = self.create_card("إجمالي الفواتير", "0", "#f59e0b")

        grid.addWidget(self.c_sales['widget'], 0, 0)
        grid.addWidget(self.c_prods['widget'], 0, 1)
        grid.addWidget(self.c_invoices['widget'], 0, 2)
        layout.addLayout(grid)

        recent = QLabel("أحدث فواتير المبيعات")
        recent.setStyleSheet("font-size: 18px; font-weight: 700; margin-top: 15px;")
        layout.addWidget(recent)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["رقم الفاتورة", "الإجمالي", "المدفوع", "طريقة الدفع", "التاريخ"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def create_card(self, title, val, color):
        frame = QFrame()
        frame.setStyleSheet(f"background: white; border-top: 5px solid {color}; border-radius: 12px; border: 1px solid #e2e8f0; padding: 20px;")
        v = QVBoxLayout(frame)
        t = QLabel(title)
        t.setStyleSheet("color: #64748b; font-weight: 700;")
        v.addWidget(t)
        lbl = QLabel(val)
        lbl.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 900;")
        v.addWidget(lbl)
        return {'widget': frame, 'lbl': lbl}

    def load_data(self):
        session = SessionLocal()
        try:
            sales = session.query(Sale).all()
            total_sales = sum(s.total for s in sales)
            prods_count = session.query(Product).count()
            invoices_count = len(sales)

            self.c_sales['lbl'].setText(f"{total_sales:,.2f} ج.س")
            self.c_prods['lbl'].setText(str(prods_count))
            self.c_invoices['lbl'].setText(str(invoices_count))

            recent_sales = session.query(Sale).order_by(Sale.created_at.desc()).limit(15).all()
            self.table.setRowCount(len(recent_sales))
            for row, s in enumerate(recent_sales):
                self.table.setItem(row, 0, QTableWidgetItem(s.invoice_number))
                self.table.setItem(row, 1, QTableWidgetItem(f"{s.total:,.2f} ج.س"))
                self.table.setItem(row, 2, QTableWidgetItem(f"{s.paid_amount:,.2f} ج.س"))
                self.table.setItem(row, 3, QTableWidgetItem(s.payment_method))
                self.table.setItem(row, 4, QTableWidgetItem(str(s.created_at)))
        finally:
            session.close()

class POSView(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.cart = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Left: Cart
        left = QWidget()
        l_layout = QVBoxLayout(left)
        l_layout.addWidget(QLabel("سلة المبيعات الحالية"))
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["المنتج", "السعر", "الكمية", "الإجمالي"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l_layout.addWidget(self.cart_table)

        self.total_lbl = QLabel("الإجمالي النهائي: 0.00 ج.س")
        self.total_lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #2563eb;")
        l_layout.addWidget(self.total_lbl)

        checkout_btn = QPushButton("إتمام البيع وإصدار الفاتورة")
        checkout_btn.setProperty("class", "SuccessButton")
        checkout_btn.setFixedHeight = 45
        checkout_btn.clicked.connect(self.checkout)
        l_layout.addWidget(checkout_btn)

        # Right: Products
        right = QWidget()
        r_layout = QVBoxLayout(right)
        r_layout.addWidget(QLabel("كتالوج المنتجات السريعة"))

        self.prod_table = QTableWidget()
        self.prod_table.setColumnCount(3)
        self.prod_table.setHorizontalHeaderLabels(["المنتج", "السعر", "المخزون"])
        self.prod_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.prod_table.cellDoubleClicked.connect(self.add_to_cart)
        r_layout.addWidget(self.prod_table)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([500, 500])
        layout.addWidget(splitter)

        self.load_products()

    def load_products(self):
        self.products = ProductService.get_all_products()
        self.prod_table.setRowCount(len(self.products))
        for row, p in enumerate(self.products):
            self.prod_table.setItem(row, 0, QTableWidgetItem(p.name))
            self.prod_table.setItem(row, 1, QTableWidgetItem(f"{p.selling_price:,.2f}"))
            self.prod_table.setItem(row, 2, QTableWidgetItem(str(p.quantity)))

    def add_to_cart(self, row, col):
        p = self.products[row]
        if p.quantity <= 0:
            QMessageBox.warning(self, "تنبيه", "المنتج نفد من المخزون!")
            return

        for item in self.cart:
            if item['product'].id == p.id:
                if item['qty'] + 1 > p.quantity:
                    QMessageBox.warning(self, "تنبيه", "الكمية تتجاوز المتاح!")
                    return
                item['qty'] += 1
                self.update_cart()
                return

        self.cart.append({'product': p, 'qty': 1, 'price': p.selling_price})
        self.update_cart()

    def update_cart(self):
        self.cart_table.setRowCount(len(self.cart))
        subtotal = 0.0
        for row, item in enumerate(self.cart):
            tot = item['price'] * item['qty']
            subtotal += tot
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['product'].name))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{item['price']:,.2f}"))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item['qty'])))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{tot:,.2f}"))

        tax = subtotal * 0.15
        total = subtotal + tax
        self.total_lbl.setText(f"الإجمالي النهائي: {total:,.2f} ج.س")

    def checkout(self):
        if not self.cart:
            QMessageBox.warning(self, "تنبيه", "السلة فارغة!")
            return

        subtotal = sum(i['price'] * i['qty'] for i in self.cart)
        tax = subtotal * 0.15
        total = subtotal + tax

        sale_data = {
            'subtotal': subtotal,
            'tax_amount': tax,
            'total': total,
            'paid_amount': total,
            'payment_method': 'CASH',
            'notes': 'POS Desktop Sale'
        }
        items_data = [{
            'product_id': i['product'].id,
            'quantity': i['qty'],
            'unit_price': i['price'],
            'tax': (i['price'] * i['qty']) * 0.15
        } for i in self.cart]

        success, inv_no, msg = SalesService.create_sale(sale_data, items_data, self.current_user.id)
        if success:
            QMessageBox.information(self, "نجاح", f"تم إتمام الفاتورة برقم: {inv_no}")
            self.cart = []
            self.update_cart()
            self.load_products()
        else:
            QMessageBox.critical(self, "خطأ", msg)

class MainWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Enterprise ERP & POS Mega Suite")
        self.resize(1280, 768)
        self.setStyleSheet(THEME_QSS)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        s_layout = QVBoxLayout(sidebar)
        
        logo = QLabel("Enterprise ERP")
        logo.setStyleSheet("color: white; font-size: 18px; font-weight: 900; padding: 15px;")
        s_layout.addWidget(logo)

        self.buttons = []
        views = [
            ("📊 لوحة التحكم", 0),
            ("💳 نقطة البيع (POS)", 1)
        ]
        for text, idx in views:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=idx: self.switch_view(i))
            s_layout.addWidget(btn)
            self.buttons.append(btn)

        s_layout.addStretch()
        main_layout.addWidget(sidebar)

        # Stack
        self.stack = QStackedWidget()
        self.stack.addWidget(DashboardView())
        self.stack.addWidget(POSView(self.current_user))
        main_layout.addWidget(self.stack)

        if self.buttons:
            self.buttons[0].setChecked(True)

    def switch_view(self, idx):
        for i, b in enumerate(self.buttons):
            b.setChecked(i == idx)
        self.stack.setCurrentIndex(idx)

def main():
    init_db()
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    
    main_win = None
    def on_login(user):
        nonlocal main_win
        main_win = MainWindow(user)
        main_win.show()

    login = LoginWindow(on_login)
    login.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
