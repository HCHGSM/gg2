# -*- coding: utf-8 -*-
"""
=============================================================================
Hardcore Enterprise POS & ERP Desktop GUI (PySide6)
Strictly functional, high-performance, real-time calculation interface.
=============================================================================
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QSplitter, QStackedWidget, QDialog, QFormLayout, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from hardcore_erp.core.database import init_hardcore_db, get_db_connection
from hardcore_erp.core.services import HardcoreAuth, HardcoreInventory, HardcoreSales, HardcoreAnalytics

STRICT_QSS = """
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    color: #0f172a;
    background-color: #f8fafc;
}
QMainWindow {
    background-color: #f1f5f9;
}
#sidebar {
    background-color: #0f172a;
    border-right: 1px solid #334155;
}
#sidebar QPushButton {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    text-align: left;
    padding: 14px 20px;
    border-radius: 8px;
    margin: 4px 10px;
    font-weight: 700;
}
#sidebar QPushButton:hover {
    background-color: #1e293b;
    color: #38bdf8;
}
#sidebar QPushButton:checked {
    background-color: #0284c7;
    color: #ffffff;
}
QPushButton.Primary {
    background-color: #0284c7;
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
}
QPushButton.Primary:hover { background-color: #0369a1; }

QPushButton.Success {
    background-color: #059669;
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
}
QPushButton.Success:hover { background-color: #047857; }

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    gridline-color: #f1f5f9;
}
QHeaderView::section {
    background-color: #f1f5f9;
    padding: 10px;
    font-weight: bold;
    color: #334155;
    border: none;
    border-bottom: 2px solid #cbd5e1;
}
QLineEdit, QComboBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px;
}
"""

class LoginWindow(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("تسجيل الدخول - Hardcore Enterprise POS")
        self.resize(420, 380)
        self.setStyleSheet("background-color: #0f172a;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setStyleSheet("background-color: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 25px;")
        cl = QVBoxLayout(card)

        title = QLabel("Enterprise Hardcore POS")
        title.setStyleSheet("font-size: 20px; font-weight: 900; color: #38bdf8;")
        title.setAlignment(Qt.AlignCenter)
        cl.addWidget(title)

        sub = QLabel("نظام الحسابات والمخزون الصارم")
        sub.setStyleSheet("font-size: 12px; color: #94a3b8; margin-bottom: 20px;")
        sub.setAlignment(Qt.AlignCenter)
        cl.addWidget(sub)

        self.user_in = QLineEdit()
        self.user_in.setPlaceholderText("اسم المستخدم (admin)")
        cl.addWidget(self.user_in)

        self.pwd_in = QLineEdit()
        self.pwd_in.setPlaceholderText("كلمة المرور (admin123)")
        self.pwd_in.setEchoMode(QLineEdit.Password)
        cl.addWidget(self.pwd_in)

        btn = QPushButton("دخول النظام الآمن")
        btn.setProperty("class", "Primary")
        btn.clicked.connect(self.login)
        cl.addWidget(btn)

        layout.addWidget(card)

    def login(self):
        u = self.user_in.text().strip()
        p = self.pwd_in.text().strip()
        user, msg = HardcoreAuth.authenticate(u, p)
        if user:
            self.on_success(user)
            self.close()
        else:
            QMessageBox.critical(self, "خطأ", msg)

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_metrics()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        title = QLabel("لوحة المؤشرات الحية والحسابات الدقيقة")
        title.setStyleSheet("font-size: 22px; font-weight: 900; color: #0f172a;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(15)

        self.c_sales = self.card("إجمالي المبيعات الفعلية", "0.00 ج.س", "#0284c7")
        self.c_profit = self.card("صافي الأرباح التقديرية", "0.00 ج.س", "#059669")
        self.c_cash = self.card("إجمالي النقدية والبنوك", "0.00 ج.س", "#7c3aed")
        self.c_invoices = self.card("عدد الفواتير المصدرة", "0", "#d97706")

        grid.addWidget(self.c_sales['widget'], 0, 0)
        grid.addWidget(self.c_profit['widget'], 0, 1)
        grid.addWidget(self.c_cash['widget'], 1, 0)
        grid.addWidget(self.c_invoices['widget'], 1, 1)
        layout.addLayout(grid)

        recent = QLabel("سجل الفواتير والعمليات الحقيقية")
        recent.setStyleSheet("font-size: 16px; font-weight: 800; margin-top: 15px;")
        layout.addWidget(recent)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["رقم الفاتورة", "المجموع الفرعي", "الضريبة (15%)", "الإجمالي النهائي", "التاريخ والوقت"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def card(self, title, val, color):
        f = QFrame()
        f.setStyleSheet(f"background: white; border-right: 6px solid {color}; border-radius: 10px; border: 1px solid #cbd5e1; padding: 15px;")
        vl = QVBoxLayout(f)
        t = QLabel(title)
        t.setStyleSheet("color: #64748b; font-weight: 700; font-size: 12px;")
        vl.addWidget(t)
        v = QLabel(val)
        v.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 900;")
        vl.addWidget(v)
        return {'widget': f, 'val': v}

    def load_metrics(self):
        m = HardcoreAnalytics.get_dashboard_metrics()
        self.c_sales['val'].setText(f"{m['total_sales']:,.2f} ج.س")
        self.c_profit['val'].setText(f"{m['net_profit']:,.2f} ج.س")
        self.c_cash['val'].setText(f"{m['total_cash']:,.2f} ج.س")
        self.c_invoices['val'].setText(str(m['invoices_count']))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT invoice_number, subtotal, tax_amount, total, created_at FROM sales ORDER BY id DESC LIMIT 20")
        rows = cur.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            self.table.setItem(r_idx, 0, QTableWidgetItem(row['invoice_number']))
            self.table.setItem(r_idx, 1, QTableWidgetItem(f"{row['subtotal']:,.2f} ج.س"))
            self.table.setItem(r_idx, 2, QTableWidgetItem(f"{row['tax_amount']:,.2f} ج.س"))
            self.table.setItem(r_idx, 3, QTableWidgetItem(f"{row['total']:,.2f} ج.س"))
            self.table.setItem(r_idx, 4, QTableWidgetItem(row['created_at']))

class POSView(QWidget):
    def __init__(self, current_user, on_sale_completed):
        super().__init__()
        self.current_user = current_user
        self.on_sale_completed = on_sale_completed
        self.cart = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Left: Cart & Checkout
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.addWidget(QLabel("سلة المبيعات الحالية (خصم مخزون فوري)"))

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["المنتج", "السعر", "الكمية", "الإجمالي"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ll.addWidget(self.cart_table)

        self.sub_lbl = QLabel("المجموع الفرعي: 0.00 ج.س")
        self.tax_lbl = QLabel("الضريبة (15%): 0.00 ج.س")
        self.tot_lbl = QLabel("الإجمالي النهائي الواجب سداده: 0.00 ج.س")
        self.tot_lbl.setStyleSheet("font-size: 16px; font-weight: 900; color: #0284c7;")

        ll.addWidget(self.sub_lbl)
        ll.addWidget(self.tax_lbl)
        ll.addWidget(self.tot_lbl)

        btn = QPushButton("إتمام البيع وخصم المخزون فوراً")
        btn.setProperty("class", "Success")
        btn.setFixedHeight = 45
        btn.clicked.connect(self.checkout)
        ll.addWidget(btn)

        # Right: Products
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.addWidget(QLabel("كتالوج المنتجات المتاحة (انقر نقراً مزدوجاً للإضافة)"))

        self.prod_table = QTableWidget()
        self.prod_table.setColumnCount(4)
        self.prod_table.setHorizontalHeaderLabels(["معرف", "الاسم", "السعر", "المخزون المتاح"])
        self.prod_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.prod_table.cellDoubleClicked.connect(self.add_to_cart)
        rl.addWidget(self.prod_table)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([500, 500])
        layout.addWidget(splitter)

        self.load_products()

    def load_products(self):
        self.products = HardcoreInventory.get_products()
        self.prod_table.setRowCount(len(self.products))
        for r, p in enumerate(self.products):
            self.prod_table.setItem(r, 0, QTableWidgetItem(str(p['id'])))
            self.prod_table.setItem(r, 1, QTableWidgetItem(p['name']))
            self.prod_table.setItem(r, 2, QTableWidgetItem(f"{p['selling_price']:,.2f} ج.س"))
            self.prod_table.setItem(r, 3, QTableWidgetItem(str(p['quantity'])))

    def add_to_cart(self, row, col):
        p = self.products[row]
        if p['quantity'] <= 0:
            QMessageBox.warning(self, "خطأ مخزون", f"المنتج '{p['name']}' نفد تماماً من المخزون!")
            return

        for item in self.cart:
            if item['id'] == p['id']:
                if item['qty'] + 1 > p['quantity']:
                    QMessageBox.warning(self, "خطأ كمية", "الكمية المطلوبة تتجاوز المخزون الفعلي!")
                    return
                item['qty'] += 1
                self.update_cart_display()
                return

        self.cart.append({'id': p['id'], 'name': p['name'], 'price': p['selling_price'], 'qty': 1, 'max_qty': p['quantity']})
        self.update_cart_display()

    def update_cart_display(self):
        self.cart_table.setRowCount(len(self.cart))
        sub = 0.0
        for r, i in enumerate(self.cart):
            tot = i['price'] * i['qty']
            sub += tot
            self.cart_table.setItem(r, 0, QTableWidgetItem(i['name']))
            self.cart_table.setItem(r, 1, QTableWidgetItem(f"{i['price']:,.2f}"))
            self.cart_table.setItem(r, 2, QTableWidgetItem(str(i['qty'])))
            self.cart_table.setItem(r, 3, QTableWidgetItem(f"{tot:,.2f}"))

        tax = sub * 0.15
        tot_all = sub + tax
        self.sub_lbl.setText(f"المجموع الفرعي: {sub:,.2f} ج.س")
        self.tax_lbl.setText(f"الضريبة (15%): {tax:,.2f} ج.س")
        self.tot_lbl.setText(f"الإجمالي النهائي الواجب سداده: {tot_all:,.2f} ج.س")

    def checkout(self):
        if not self.cart:
            QMessageBox.warning(self, "تنبيه", "سلة المشتريات فارغة!")
            return

        cart_payload = [{'id': i['id'], 'qty': i['qty']} for i in self.cart]
        success, inv_no, msg = HardcoreSales.create_sale(self.current_user['id'], cart_payload, 'CASH')
        
        if success:
            QMessageBox.information(self, "نجاح تام", msg)
            self.cart = []
            self.update_cart_display()
            self.load_products()
            self.on_sale_completed()
        else:
            QMessageBox.critical(self, "خطأ محاسبي", f"تعذر تنفيذ العملية:\n{msg}")

class MainWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Hardcore Enterprise ERP & POS Mega Suite")
        self.resize(1280, 768)
        self.setStyleSheet(STRICT_QSS)

        central = QWidget()
        self.setCentralWidget(central)
        ml = QHBoxLayout(central)
        ml.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sl = QVBoxLayout(sidebar)

        logo = QLabel("Hardcore ERP")
        logo.setStyleSheet("color: #38bdf8; font-size: 18px; font-weight: 900; padding: 15px;")
        sl.addWidget(logo)

        self.dash_view = DashboardView()
        self.pos_view = POSView(self.current_user, lambda: self.dash_view.load_metrics())

        self.stack = QStackedWidget()
        self.stack.addWidget(self.dash_view)
        self.stack.addWidget(self.pos_view)

        b1 = QPushButton("📊 لوحة المؤشرات الحية")
        b1.setCheckable(True)
        b1.setChecked(True)
        b1.clicked.connect(lambda: self.switch(0, b1))
        sl.addWidget(b1)

        b2 = QPushButton("💳 نقطة البيع الصارمة (POS)")
        b2.setCheckable(True)
        b2.clicked.connect(lambda: self.switch(1, b2))
        sl.addWidget(b2)

        self.nav_btns = [b1, b2]
        sl.addStretch()

        ml.addWidget(sidebar)
        ml.addWidget(self.stack)

    def switch(self, idx, btn):
        for b in self.nav_btns:
            b.setChecked(False)
        btn.setChecked(True)
        self.stack.setCurrentIndex(idx)
        if idx == 0:
            self.dash_view.load_metrics()

def main():
    init_hardcore_db()
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)

    win = None
    def on_login(user):
        nonlocal win
        win = MainWindow(user)
        win.show()

    login = LoginWindow(on_login)
    login.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
