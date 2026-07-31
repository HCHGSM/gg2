from pos_erp.ui.worker import Worker
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QLineEdit, QGridLayout, QComboBox, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox
from pos_erp.services.product_service import ProductService
from pos_erp.services.sales_service import SalesService
from pos_erp.ui.styles import apply_card_shadow
from pos_erp.ui.animations import ToastManager, Animations

class POSView(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.cart_items = []
        self.all_products = []
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(24)

        # --- Left Side: Touch Optimized Product Grid ---
        products_widget = QWidget()
        products_layout = QVBoxLayout(products_widget)
        products_layout.setContentsMargins(0, 0, 0, 0)
        products_layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        title = QLabel("نقطة البيع (Terminal)")
        title.setProperty("cssClass", "view-title")
        header_layout.addWidget(title)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 البحث بالاسم أو الباركود...")
        self.search_input.setFixedWidth(300)
        self.search_input.setFixedHeight(45)
        self.search_input.textChanged.connect(self.filter_products)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        products_layout.addLayout(header_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.products_grid = QGridLayout(self.grid_container)
        self.products_grid.setSpacing(20)
        self.products_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        scroll.setWidget(self.grid_container)
        products_layout.addWidget(scroll)

        main_layout.addWidget(products_widget, stretch=7)

        # --- Right Side: Smart Cart ---
        cart_frame = QFrame()
        cart_frame.setObjectName("Card")
        cart_frame.setFixedWidth(420)
        apply_card_shadow(cart_frame)
        
        cart_layout = QVBoxLayout(cart_frame)
        cart_layout.setContentsMargins(24, 24, 24, 24)
        cart_layout.setSpacing(20)

        cart_title = QLabel("الفاتورة الحالية")
        cart_title.setProperty("cssClass", "view-title")
        cart_title.setStyleSheet("font-size: 20px;")
        cart_layout.addWidget(cart_title)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["المنتج", "السعر", "الكمية", "🗑️"])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setShowGrid(False)
        self.cart_table.setStyleSheet("border: none; border-radius: 0px;")
        cart_layout.addWidget(self.cart_table)

        # Totals Section
        totals_card = QFrame()
        totals_card.setObjectName("TotalsCard")
        totals_layout = QVBoxLayout(totals_card)
        totals_layout.setContentsMargins(20, 20, 20, 20)

        def make_row(label_text):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-size: 15px; color: #A1A1AA; font-weight: 600;")
            val = QLabel("0.00")
            val.setStyleSheet("font-size: 15px; color: #F4F4F5; font-weight: 600;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            return row, val

        r1, self.lbl_subtotal = make_row("المجموع الفرعي:")
        r2, self.lbl_tax = make_row("الضريبة (15%):")
        
        totals_layout.addLayout(r1)
        totals_layout.addLayout(r2)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #3F3F46;")
        totals_layout.addWidget(line)
        
        total_row = QHBoxLayout()
        t_lbl = QLabel("الإجمالي النهائي:")
        t_lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #F4F4F5;")
        self.lbl_total = QLabel("0.00")
        self.lbl_total.setProperty("cssClass", "card-value")
        self.lbl_total.setStyleSheet("color: #6366F1; font-size: 28px;")
        total_row.addWidget(t_lbl)
        total_row.addStretch()
        total_row.addWidget(self.lbl_total)
        totals_layout.addLayout(total_row)
        
        cart_layout.addWidget(totals_card)

        # Payment
        self.pay_method_combo = QComboBox()
        self.pay_method_combo.addItems(["CASH - الدفع نقداً", "BANK - بطاقة بنكية"])
        self.pay_method_combo.setFixedHeight(50)
        self.pay_method_combo.setStyleSheet("font-size: 16px; font-weight: bold;")
        cart_layout.addWidget(self.pay_method_combo)

        checkout_btn = QPushButton("إصدار الفاتورة ➔")
        checkout_btn.setProperty("cssClass", "pay-btn")
        checkout_btn.setCursor(Qt.PointingHandCursor)
        checkout_btn.clicked.connect(self.checkout)
        cart_layout.addWidget(checkout_btn)

        main_layout.addWidget(cart_frame)
        self.load_data()

    def load_data(self):
        worker = Worker(self._fetch_products)
        worker.signals.result.connect(self._on_products_fetched)
        QThreadPool.globalInstance().start(worker)

    def _fetch_products(self):
        return ProductService.get_all_products()

    def _on_products_fetched(self, products):
        self.all_products = products
        self.filter_products("")

    def filter_products(self, text):
        filtered = [p for p in self.all_products if text.lower() in p.name.lower() or (p.barcode and text in p.barcode)]
        self.populate_products_grid(filtered)

    def populate_products_grid(self, products):
        # Clear Grid
        while self.products_grid.count():
            item = self.products_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        row, col = 0, 0
        for p in products:
            card = QFrame()
            card.setObjectName("ProductCard")
            card.setFixedSize(220, 160)
            card.setCursor(Qt.PointingHandCursor)
            
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 15, 15, 15)
            
            name = QLabel(p.name)
            name.setWordWrap(True)
            name.setStyleSheet("font-weight: 800; font-size: 16px; color: #F4F4F5;")
            name.setAlignment(Qt.AlignTop)
            
            bottom_layout = QHBoxLayout()
            price = QLabel(f"{p.selling_price:,.2f}")
            price.setStyleSheet("color: #10B981; font-weight: 800; font-size: 18px;")
            
            stock = QLabel(f"📦 {p.quantity}")
            stock.setStyleSheet("color: #A1A1AA; font-size: 14px; font-weight: bold;")
            
            bottom_layout.addWidget(price)
            bottom_layout.addStretch()
            bottom_layout.addWidget(stock)
            
            card_layout.addWidget(name)
            card_layout.addStretch()
            card_layout.addLayout(bottom_layout)
            
            # Make the entire card clickable
            card.mousePressEvent = lambda event, prod=p: self.add_to_cart(prod)
            
            self.products_grid.addWidget(card, row, col)
            col += 1
            if col > 3: # 4 columns
                col = 0
                row += 1

    def add_to_cart(self, product):
        if product.quantity <= 0:
            ToastManager.show_error(self, f"المنتج '{product.name}' نفد تماماً من المخزون!")
            return

        for item in self.cart_items:
            if item['product'].id == product.id:
                if item['quantity'] >= product.quantity:
                    ToastManager.show_error(self, "لا يمكن إضافة المزيد، تتجاوز المخزون!")
                    return
                item['quantity'] += 1
                item['tax'] = (item['quantity'] * item['unit_price']) * (product.tax_rate / 100)
                self.update_cart_display()
                return

        tax_amount = product.selling_price * (product.tax_rate / 100)
        self.cart_items.append({
            'product': product,
            'quantity': 1,
            'unit_price': product.selling_price,
            'tax': tax_amount
        })
        self.update_cart_display()

    def update_cart_display(self):
        self.cart_table.setRowCount(0)
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

            name_item = QTableWidgetItem(p.name)
            name_item.setToolTip(p.name)
            
            self.cart_table.setItem(row, 0, name_item)
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{price:,.2f}"))
            
            # Qty control layout
            qty_widget = QWidget()
            qty_layout = QHBoxLayout(qty_widget)
            qty_layout.setContentsMargins(0, 0, 0, 0)
            qty_lbl = QLabel(f"x{qty}")
            qty_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
            qty_layout.addWidget(qty_lbl)
            self.cart_table.setCellWidget(row, 2, qty_widget)

            del_btn = QPushButton("✕")
            del_btn.setProperty("cssClass", "danger")
            del_btn.setFixedSize(30, 30)
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 3, del_btn)

        Animations.count_number(self.lbl_subtotal, 0, subtotal, True, duration=400)
        Animations.count_number(self.lbl_tax, 0, tax_total, True, duration=400)
        Animations.count_number(self.lbl_total, 0, subtotal + tax_total, True, duration=500)

    def remove_from_cart(self, row):
        if 0 <= row < len(self.cart_items):
            self.cart_items.pop(row)
            self.update_cart_display()

    def checkout(self):
        if not self.cart_items:
            QMessageBox.warning(self, "سلة فارغة", "يرجى إضافة منتجات إلى السلة أولاً!")
            return

        subtotal = sum(i['quantity'] * i['unit_price'] for i in self.cart_items)
        tax_amount = sum(i['tax'] for i in self.cart_items)
        total = subtotal + tax_amount

        method_text = self.pay_method_combo.currentText()
        payment_method = 'CASH' if 'CASH' in method_text else 'BANK'

        sale_data = {
            'subtotal': subtotal,
            'discount': 0.0,
            'tax_amount': tax_amount,
            'total': total,
            'paid_amount': total,
            'payment_method': payment_method,
            'notes': 'POS Sale'
        }

        items_data = []
        for i in self.cart_items:
            items_data.append({
                'product_id': i['product'].id,
                'quantity': i['quantity'],
                'unit_price': i['unit_price'],
                'discount': 0.0,
                'tax': i['tax']
            })

        success, invoice_no, msg = SalesService.create_sale(sale_data, items_data, self.current_user.id)
        
        if success:
            QMessageBox.information(self, "نجاح", f"تم إتمام الفاتورة بنجاح!\nرقم الفاتورة: {invoice_no}")
            self.cart_items.clear()
            self.update_cart_display()
            self.load_data()
        else:
            QMessageBox.critical(self, "خطأ", f"تعذر إتمام عملية البيع: {msg}")
