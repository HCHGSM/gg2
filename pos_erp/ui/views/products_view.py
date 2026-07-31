from pos_erp.ui.animations import Animations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QFormLayout, QDoubleSpinBox
)
from pos_erp.services.product_service import ProductService

class ProductDialog(QDialog):
    """
    نافذة حوار منسقة لإضافة أو تعديل منتج تجاري مع كافة التفاصيل (الباركود، SKU، الأسعار، المخزون، الضرائب).
    """
    def __init__(self, product=None):
        super().__init__()
        self.product = product
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("إدارة بيانات المنتج" if self.product else "إضافة منتج تجاري جديد")
        self.resize(500, 550)
        
        layout = QFormLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        self.name_input = QLineEdit()
        self.sku_input = QLineEdit()
        self.barcode_input = QLineEdit()
        
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setMaximum(10000000)
        self.purchase_price.setDecimals(2)
        
        self.selling_price = QDoubleSpinBox()
        self.selling_price.setMaximum(10000000)
        self.selling_price.setDecimals(2)
        
        self.quantity = QDoubleSpinBox()
        self.quantity.setMaximum(10000000)
        self.quantity.setDecimals(2)
        
        self.min_stock = QDoubleSpinBox()
        self.min_stock.setMaximum(1000000)
        self.min_stock.setValue(5.0)

        self.tax_rate = QDoubleSpinBox()
        self.tax_rate.setMaximum(100.0)
        self.tax_rate.setValue(15.0)

        layout.addRow("اسم المنتج:", self.name_input)
        layout.addRow("رمز المنتج (SKU):", self.sku_input)
        layout.addRow("الباركود:", self.barcode_input)
        layout.addRow("سعر الشراء:", self.purchase_price)
        layout.addRow("سعر البيع:", self.selling_price)
        layout.addRow("الكمية الأولية:", self.quantity)
        layout.addRow("الحد الأدنى للتنبيه:", self.min_stock)
        layout.addRow("نسبة الضريبة (%):", self.tax_rate)

        if self.product:
            self.name_input.setText(self.product.name)
            self.sku_input.setText(self.product.sku or "")
            self.barcode_input.setText(self.product.barcode or "")
            self.purchase_price.setValue(self.product.purchase_price)
            self.selling_price.setValue(self.product.selling_price)
            self.quantity.setValue(self.product.quantity)
            self.min_stock.setValue(self.product.min_stock)
            self.tax_rate.setValue(self.product.tax_rate)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 حفظ المنتج")
        save_btn.setProperty("cssClass", "primary")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("❌ إلغاء")
        cancel_btn.setProperty("cssClass", "danger")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'sku': self.sku_input.text().strip() or None,
            'barcode': self.barcode_input.text().strip() or None,
            'purchase_price': self.purchase_price.value(),
            'selling_price': self.selling_price.value(),
            'quantity': self.quantity.value(),
            'min_stock': self.min_stock.value(),
            'tax_rate': self.tax_rate.value()
        }

class ProductsView(QWidget):
    """
    واجهة إدارة المنتجات بالكامل مع البحث المتقدم، الإضافة، التعديل، والحذف.
    """
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        top_layout = QHBoxLayout()
        title = QLabel("إدارة المخزون والمنتجات التجارية")
        title.setProperty("cssClass", "view-title")
        top_layout.addWidget(title)

        top_layout.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث في المنتجات...")
        self.search_input.setFixedWidth(280)
        self.search_input.setFixedHeight(38)
        self.search_input.textChanged.connect(self.filter_table)
        top_layout.addWidget(self.search_input)

        add_btn = QPushButton("➕ إضافة منتج جديد")
        add_btn.setProperty("cssClass", "success")
        add_btn.clicked.connect(self.add_product)
        top_layout.addWidget(add_btn)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["المعرف", "اسم المنتج", "SKU", "الباركود", "سعر الشراء", "سعر البيع", "الكمية المتاحة", "الضريبة"])
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

    def load_data(self):
        self.products = ProductService.get_all_products()
        self.populate_table(self.products)

    def populate_table(self, products):
        self.table.setRowCount(0)
        Animations.pop_in(self.table, 500) # Clear previous rows to prevent leaks
        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(row, 1, QTableWidgetItem(p.name))
            self.table.setItem(row, 2, QTableWidgetItem(p.sku or "-"))
            self.table.setItem(row, 3, QTableWidgetItem(p.barcode or "-"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{p.purchase_price:,.2f} ج.س"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{p.selling_price:,.2f} ج.س"))
            self.table.setItem(row, 6, QTableWidgetItem(str(p.quantity)))
            self.table.setItem(row, 7, QTableWidgetItem(f"{p.tax_rate}%"))

    def filter_table(self, text):
        filtered = [p for p in self.products if text.lower() in p.name.lower() or (p.sku and text in p.sku) or (p.barcode and text in p.barcode)]
        self.populate_table(filtered)

    def add_product(self):
        dialog = ProductDialog()
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "خطأ إدخال", "اسم المنتج مطلوب إجباريأ!")
                return
            success, msg = ProductService.add_product(data, self.current_user.id)
            if success:
                QMessageBox.information(self, "نجاح", msg)
                self.load_data()
            else:
                QMessageBox.critical(self, "خطأ", msg)
