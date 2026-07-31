from pos_erp.ui.dialogs import ProductForm
from pos_erp.ui.animations import ToastManager
from pos_erp.ui.animations import Animations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QFormLayout, QDoubleSpinBox
)
from pos_erp.services.product_service import ProductService

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
        from pos_erp.services.crm_service import CRMService
        categories = ProductService.get_categories()
        suppliers = CRMService.get_all_suppliers()
        dialog = ProductForm(self, product=None, categories=categories, suppliers=suppliers)
        if dialog.exec():
            data = dialog.get_data()
            if not data['name']:
                ToastManager.show_warning(self.window(), "اسم المنتج مطلوب إجباريأ!")
                return
            success, msg = ProductService.add_product(data, self.current_user.id)
            if success:
                ToastManager.show_success(self.window(), msg)
                self.load_data()
            else:
                ToastManager.show_error(self.window(), msg)
