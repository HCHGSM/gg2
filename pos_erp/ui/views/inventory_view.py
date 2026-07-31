from pos_erp.ui.animations import Animations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
)
from PySide6.QtCore import Qt
from pos_erp.services.product_service import ProductService

class InventoryView(QWidget):
    """
    إدارة ومراقبة حركة المخزون، تقييم البضاعة، وتنبيهات النقص الفورية.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        top_layout = QHBoxLayout()
        title = QLabel("إدارة المخزون وتقييم المستودعات")
        title.setProperty("cssClass", "view-title")
        top_layout.addWidget(title)
        top_layout.addStretch()

        refresh_btn = QPushButton("🔄 تحديث حالة المخزون")
        refresh_btn.setProperty("cssClass", "primary")
        refresh_btn.clicked.connect(self.load_data)
        top_layout.addWidget(refresh_btn)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["اسم المنتج", "الكمية الحالية", "الحد الأدنى", "حالة المخزون", "سعر الشراء", "إجمالي قيمة المخزون"])
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
        products = ProductService.get_all_products()
        self.table.setRowCount(0)
        Animations.pop_in(self.table, 500) # Clear previous rows to prevent leaks
        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(p.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(p.quantity)))
            self.table.setItem(row, 2, QTableWidgetItem(str(p.min_stock)))
            
            status = "⚠️ منخفض (يحتاج توريد)" if p.quantity <= p.min_stock else "✅ متوفر طبيعي"
            status_item = QTableWidgetItem(status)
            if p.quantity <= p.min_stock:
                status_item.setForeground(Qt.red)
            self.table.setItem(row, 3, status_item)
            
            self.table.setItem(row, 4, QTableWidgetItem(f"{p.purchase_price:,.2f} ج.س"))
            total_valuation = p.purchase_price * p.quantity
            self.table.setItem(row, 5, QTableWidgetItem(f"{total_valuation:,.2f} ج.س"))
