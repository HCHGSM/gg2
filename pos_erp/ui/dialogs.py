from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QFrame, QDoubleSpinBox, QComboBox, QTextEdit, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from pos_erp.ui.animations import Animations, ToastManager

class ModernDialog(QDialog):
    def __init__(self, parent=None, title="Dialog"):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(450)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.card = QFrame()
        self.card.setStyleSheet("background-color: #18181B; border: 1px solid #3F3F46; border-radius: 16px;")
        Animations.apply_soft_shadow(self.card)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(25, 25, 25, 25)
        card_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF; background: transparent; border: none;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("background-color: transparent; border: none; color: #A1A1AA; font-size: 16px;")
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)
        
        card_layout.addLayout(header_layout)
        
        # Scrollable Form Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        self.form_container = QWidget()
        self.form_container.setStyleSheet("background: transparent;")
        self.form_layout = QFormLayout(self.form_container)
        self.form_layout.setSpacing(15)
        self.form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.scroll.setWidget(self.form_container)
        
        card_layout.addWidget(self.scroll)
        
        # Footer
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setFixedWidth(100)
        
        self.save_btn = QPushButton("حفظ")
        self.save_btn.setProperty("cssClass", "primary")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setFixedWidth(120)
        
        footer_layout.addWidget(cancel_btn)
        footer_layout.addWidget(self.save_btn)
        
        card_layout.addLayout(footer_layout)
        main_layout.addWidget(self.card)
        
        Animations.pop_in(self.card, 400)

    def add_input(self, name, label, widget):
        widget.setObjectName(name)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #A1A1AA; font-weight: 600; background: transparent; border: none;")
        self.form_layout.addRow(lbl, widget)

    def get_data(self):
        data = {}
        for i in range(self.form_layout.rowCount()):
            item = self.form_layout.itemAt(i, QFormLayout.FieldRole)
            if not item: continue
            w = item.widget()
            if not w: continue
            
            key = w.objectName()
            if isinstance(w, QLineEdit):
                data[key] = w.text().strip()
            elif isinstance(w, QDoubleSpinBox) or isinstance(w, QSpinBox):
                data[key] = w.value()
            elif isinstance(w, QComboBox):
                data[key] = w.currentData()
            elif isinstance(w, QTextEdit):
                data[key] = w.toPlainText().strip()
        return data

class CustomerForm(ModernDialog):
    def __init__(self, parent=None, customer=None):
        title = "تعديل بيانات العميل" if customer else "إضافة عميل جديد"
        super().__init__(parent, title)
        
        name_input = QLineEdit()
        phone_input = QLineEdit()
        email_input = QLineEdit()
        address_input = QLineEdit()
        tax_input = QLineEdit()
        
        if customer:
            name_input.setText(customer.name or "")
            phone_input.setText(customer.phone or "")
            email_input.setText(customer.email or "")
            address_input.setText(customer.address or "")
            tax_input.setText(customer.tax_number or "")
            
        self.add_input("name", "اسم العميل:", name_input)
        self.add_input("phone", "رقم الهاتف:", phone_input)
        self.add_input("email", "البريد الإلكتروني:", email_input)
        self.add_input("tax_number", "الرقم الضريبي:", tax_input)
        self.add_input("address", "العنوان:", address_input)

class SupplierForm(ModernDialog):
    def __init__(self, parent=None, supplier=None):
        title = "تعديل بيانات المورد" if supplier else "إضافة مورد جديد"
        super().__init__(parent, title)
        
        name_input = QLineEdit()
        contact_input = QLineEdit()
        phone_input = QLineEdit()
        email_input = QLineEdit()
        address_input = QLineEdit()
        tax_input = QLineEdit()
        
        if supplier:
            name_input.setText(supplier.name or "")
            contact_input.setText(supplier.contact_person or "")
            phone_input.setText(supplier.phone or "")
            email_input.setText(supplier.email or "")
            address_input.setText(supplier.address or "")
            tax_input.setText(supplier.tax_number or "")
            
        self.add_input("name", "اسم المورد/الشركة:", name_input)
        self.add_input("contact_person", "مسؤول التواصل:", contact_input)
        self.add_input("phone", "رقم الهاتف:", phone_input)
        self.add_input("email", "البريد الإلكتروني:", email_input)
        self.add_input("tax_number", "الرقم الضريبي:", tax_input)
        self.add_input("address", "العنوان:", address_input)

class ProductForm(ModernDialog):
    def __init__(self, parent=None, product=None, categories=[], suppliers=[]):
        title = "تعديل منتج" if product else "إضافة منتج جديد"
        super().__init__(parent, title)
        
        name_in = QLineEdit()
        sku_in = QLineEdit()
        barcode_in = QLineEdit()
        
        cat_combo = QComboBox()
        cat_combo.addItem("بدون تصنيف", None)
        for c in categories:
            cat_combo.addItem(c.name, c.id)
            
        sup_combo = QComboBox()
        sup_combo.addItem("بدون مورد", None)
        for s in suppliers:
            sup_combo.addItem(s.name, s.id)
            
        price_in = QDoubleSpinBox()
        price_in.setMaximum(999999999.0)
        
        sell_in = QDoubleSpinBox()
        sell_in.setMaximum(999999999.0)
        
        qty_in = QDoubleSpinBox()
        qty_in.setMaximum(999999.0)
        
        min_in = QDoubleSpinBox()
        min_in.setMaximum(999999.0)
        
        tax_in = QDoubleSpinBox()
        tax_in.setMaximum(100.0)
        
        if product:
            name_in.setText(product.name or "")
            sku_in.setText(product.sku or "")
            barcode_in.setText(product.barcode or "")
            
            if product.category_id:
                idx = cat_combo.findData(product.category_id)
                if idx >= 0: cat_combo.setCurrentIndex(idx)
            if product.supplier_id:
                idx = sup_combo.findData(product.supplier_id)
                if idx >= 0: sup_combo.setCurrentIndex(idx)
                
            price_in.setValue(product.purchase_price)
            sell_in.setValue(product.selling_price)
            qty_in.setValue(product.quantity)
            qty_in.setEnabled(False) # Qty shouldn't be edited manually here, but via purchases/adjustments
            min_in.setValue(product.min_stock)
            tax_in.setValue(product.tax_rate)
            
        self.add_input("name", "اسم المنتج:", name_in)
        self.add_input("sku", "رمز SKU:", sku_in)
        self.add_input("barcode", "الباركود:", barcode_in)
        self.add_input("category_id", "التصنيف:", cat_combo)
        self.add_input("supplier_id", "المورد المفضل:", sup_combo)
        if not product:
            self.add_input("quantity", "الرصيد الافتتاحي:", qty_in)
            self.add_input("purchase_price", "تكلفة الوحدة:", price_in)
        self.add_input("selling_price", "سعر البيع:", sell_in)
        self.add_input("min_stock", "الحد الأدنى للتنبيه:", min_in)
        self.add_input("tax_rate", "نسبة الضريبة %:", tax_in)
