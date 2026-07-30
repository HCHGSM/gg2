from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QSplitter, QGridLayout, QComboBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from pos_erp.services.product_service import ProductService
from pos_erp.services.sales_service import SalesService

class POSView(QWidget):
    """
    نقطة بيع متقدمة (POS) تدعم البحث بالباركود والسريع، إدارة السلة، حساب الضريبة،
    الخصومات، واختيار طرق الدفع وإصدار الفواتير الفورية.
    """
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.cart_items = []
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Left side: Cart & Checkout Panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("نقطة البيع السريع (POS Terminal)")
        title.setStyleSheet("font-size: 20px; font-weight: 800; color: #1e293b;")
        left_layout.addWidget(title)

        # Cart Table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["المنتج", "السعر", "الكمية", "الإجمالي", "إجراء"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        left_layout.addWidget(self.cart_table)

        # Payment Method & Totals
        totals_frame = QWidget()
        totals_layout = QVBoxLayout(totals_frame)
        totals_layout.setContentsMargins(0, 10, 0, 0)

        self.lbl_subtotal = QLabel("المجموع الفرعي: 0.00 ج.س")
        self.lbl_tax = QLabel("الضريبة المضافة (15%): 0.00 ج.س")
        self.lbl_total = QLabel("الإجمالي النهائي الواجب سداده: 0.00 ج.س")
        self.lbl_total.setStyleSheet("font-size: 18px; font-weight: 800; color: #2563eb;")

        totals_layout.addWidget(self.lbl_subtotal)
        totals_layout.addWidget(self.lbl_tax)
        totals_layout.addWidget(self.lbl_total)

        pay_method_layout = QHBoxLayout()
        pay_method_layout.addWidget(QLabel("طريقة الدفع:"))
        self.pay_method_combo = QComboBox()
        self.pay_method_combo.addItems(["نقدي (CASH)", "تحويل بنكي (BANK)", "بطاقة ائتمان"])
        pay_method_layout.addWidget(self.pay_method_combo)
        totals_layout.addLayout(pay_method_layout)

        left_layout.addWidget(totals_frame)

        # Checkout Button (Vibrant Success)
        checkout_btn = QPushButton("إتمام البيع وإصدار الفواتير (F4)")
        checkout_btn.setProperty("class", "SuccessButton")
        checkout_btn.setFixedHeight(50)
        checkout_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
                color: white;
                font-weight: 800;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #047857);
            }
        """)
        checkout_btn.clicked.connect(self.checkout)
        left_layout.addWidget(checkout_btn)

        # Right side: Product Catalog & Search
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 مسح الباركود أو البحث بالاسم أو الكود (SKU)...")
        self.search_input.setFixedHeight(42)
        self.search_input.textChanged.connect(self.filter_products)
        search_layout.addWidget(self.search_input)
        right_layout.addLayout(search_layout)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["المنتج", "السعر", "المخزون", "إضافة للسلة"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.products_table)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([550, 450])

        main_layout.addWidget(splitter)
        self.load_products()

    def load_products(self):
        self.all_products = ProductService.get_all_products()
        self.populate_products_table(self.all_products)

    def populate_products_table(self, products):
        self.products_table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.products_table.setItem(row, 0, QTableWidgetItem(p.name))
            self.products_table.setItem(row, 1, QTableWidgetItem(f"{p.selling_price:,.2f} ج.س"))
            self.products_table.setItem(row, 2, QTableWidgetItem(str(p.quantity)))
            
            btn = QPushButton("➕ إضافة")
            btn.setProperty("class", "PrimaryButton")
            btn.clicked.connect(lambda checked, prod=p: self.add_to_cart(prod))
            self.products_table.setCellWidget(row, 3, btn)

    def filter_products(self, text):
        filtered = [p for p in self.all_products if text.lower() in p.name.lower() or (p.barcode and text in p.barcode) or (p.sku and text in p.sku)]
        self.populate_products_table(filtered)

    def add_to_cart(self, product):
        if product.quantity <= 0:
            QMessageBox.warning(self, "تنبيه مخزون", f"المنتج '{product.name}' نفد تماماً من المخزون!")
            return

        for item in self.cart_items:
            if item['product'].id == product.id:
                if item['quantity'] + 1 > product.quantity:
                    QMessageBox.warning(self, "تنبيه كمية", "لا يمكن إضافة المزيد، الكمية تتجاوز المتاح بالمخزون!")
                    return
                item['quantity'] += 1
                self.update_cart_display()
                return

        self.cart_items.append({
            'product': product,
            'quantity': 1,
            'unit_price': product.selling_price,
            'discount': 0.0,
            'tax': product.selling_price * (product.tax_rate / 100.0)
        })
        self.update_cart_display()

    def update_cart_display(self):
        self.cart_table.setRowCount(len(self.cart_items))
        subtotal = 0.0
        tax_total = 0.0

        for row, item in enumerate(self.cart_items):
            p = item['product']
            qty = item['quantity']
            price = item['unit_price']
            total = (qty * price) + item['tax']
            subtotal += qty * price
            tax_total += item['tax']

            self.cart_table.setItem(row, 0, QTableWidgetItem(p.name))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{price:,.2f}"))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(qty)))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{total:,.2f}"))

            del_btn = QPushButton("🗑️ حذف")
            del_btn.setProperty("class", "DangerButton")
            del_btn.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 4, del_btn)

        self.lbl_subtotal.setText(f"المجموع الفرعي: {subtotal:,.2f} ج.س")
        self.lbl_tax.setText(f"الضريبة (15%): {tax_total:,.2f} ج.س")
        self.lbl_total.setText(f"الإجمالي النهائي الواجب سداده: {subtotal + tax_total:,.2f} ج.س")

    def remove_from_cart(self, row):
        if 0 <= row < len(self.cart_items):
            self.cart_items.pop(row)
            self.update_cart_display()

    def checkout(self):
        if not self.cart_items:
            QMessageBox.warning(self, "سلة فارغة", "يرجى إضافة منتجات إلى السلة أولاً قبل إتمام عملية البيع!")
            return

        subtotal = sum(i['quantity'] * i['unit_price'] for i in self.cart_items)
        tax_amount = sum(i['tax'] for i in self.cart_items)
        total = subtotal + tax_amount

        method_text = self.pay_method_combo.currentText()
        payment_method = 'CASH' if 'نقدي' in method_text else 'BANK'

        sale_data = {
            'subtotal': subtotal,
            'discount': 0.0,
            'tax_amount': tax_amount,
            'total': total,
            'paid_amount': total,
            'payment_method': payment_method,
            'notes': 'POS Terminal Sale'
        }

        items_data = [{
            'product_id': i['product'].id,
            'quantity': i['quantity'],
            'unit_price': i['unit_price'],
            'discount': i['discount'],
            'tax': i['tax']
        } for i in self.cart_items]

        success, invoice_no, msg = SalesService.create_sale(sale_data, items_data, self.current_user.id)
        if success:
            QMessageBox.information(self, "نجاح العملية", f"تم إتمام الفاتورة بنجاح!\nرقم الفاتورة: {invoice_no}")
            self.cart_items.clear()
            self.update_cart_display()
            self.load_products()
        else:
            QMessageBox.critical(self, "خطأ في البيع", f"تعذر إتمام عملية البيع: {msg}")
