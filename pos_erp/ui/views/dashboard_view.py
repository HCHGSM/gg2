from pos_erp.ui.worker import Worker
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
from PySide6.QtCore import Qt
from pos_erp.services.report_service import ReportService
from pos_erp.services.sales_service import SalesService
from pos_erp.ui.styles import apply_card_shadow
from pos_erp.ui.animations import Animations

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def create_kpi_card(self, title, value, icon, color):
        card = QFrame()
        card.setObjectName("Card")
        card.setFixedHeight(140)
        apply_card_shadow(card)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        
        header_layout = QHBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setProperty("cssClass", "card-title")
        
        # Icon inside a colored circular background
        icon_container = QFrame()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet(f"background-color: {color}20; border-radius: 24px; border: none;") # 20 is hex alpha
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        lbl_icon = QLabel(icon)
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet(f"font-size: 22px; color: {color}; background: transparent; border: none;")
        icon_layout.addWidget(lbl_icon)
        
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(icon_container)
        
        lbl_value = QLabel(str(value))
        lbl_value.setProperty("cssClass", "card-value")
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        layout.addWidget(lbl_value)
        layout.addStretch()
        
        return card, lbl_value

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        title = QLabel("نظرة عامة (Overview)")
        title.setProperty("cssClass", "view-title")
        layout.addWidget(title)

        # KPI Grid
        grid = QGridLayout()
        grid.setSpacing(24)
        
        c1, self.lbl_sales = self.create_kpi_card("إجمالي المبيعات", "0.0", "💰", "#10B981")
        c2, self.lbl_purchases = self.create_kpi_card("إجمالي المشتريات", "0.0", "🛍️", "#F59E0B")
        c3, self.lbl_profit = self.create_kpi_card("صافي الأرباح", "0.0", "📈", "#6366F1")
        c4, self.lbl_low_stock = self.create_kpi_card("تنبيهات المخزون", "0", "⚠️", "#EF4444")
        
        grid.addWidget(c1, 0, 0)
        grid.addWidget(c2, 0, 1)
        grid.addWidget(c3, 0, 2)
        grid.addWidget(c4, 0, 3)
        layout.addLayout(grid)

        # Recent Sales Table
        table_frame = QFrame()
        table_frame.setObjectName("Card")
        apply_card_shadow(table_frame)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        
        header_area = QWidget()
        header_area.setStyleSheet("background: transparent;")
        header_area_layout = QHBoxLayout(header_area)
        header_area_layout.setContentsMargins(24, 24, 24, 16)
        
        lbl_recent = QLabel("أحدث المبيعات المكتملة")
        lbl_recent.setProperty("cssClass", "card-title")
        lbl_recent.setStyleSheet("font-size: 18px; font-weight: 800; color: #F4F4F5;") # Will adapt depending on theme if we use generic class, but let's keep it bold
        header_area_layout.addWidget(lbl_recent)
        table_layout.addWidget(header_area)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["رقم الفاتورة", "العميل", "الإجمالي", "المدفوع", "الحالة"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("border: none; border-radius: 0px;") # remove internal border inside card
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_frame)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        self.load_data()

    def load_data(self):
        def task():
            return ReportService.get_dashboard_stats(), SalesService.get_all_sales()[:10]
            
        worker = Worker(task)
        worker.signals.result.connect(self._on_data_loaded)
        QThreadPool.globalInstance().start(worker)

    def _on_data_loaded(self, result):
        stats, sales = result
        # Animated counters
        Animations.count_number(self.lbl_sales, 0, stats['total_sales'], True, duration=1000)
        Animations.count_number(self.lbl_purchases, 0, stats['total_purchases'], True, duration=1000)
        Animations.count_number(self.lbl_profit, 0, stats['net_profit'], True, duration=1000)
        Animations.count_number(self.lbl_low_stock, 0, stats['low_stock_count'], False, duration=1000)
        
        # Pop in cards
        Animations.pop_in(self.lbl_sales.parentWidget(), 500, 0)
        Animations.pop_in(self.lbl_purchases.parentWidget(), 500, 100)
        Animations.pop_in(self.lbl_profit.parentWidget(), 500, 200)
        Animations.pop_in(self.lbl_low_stock.parentWidget(), 500, 300)

        self.table.setRowCount(0)
        self.table.setRowCount(len(sales))
        for row, s in enumerate(sales):
            self.table.setItem(row, 0, QTableWidgetItem(s.invoice_number))
            self.table.setItem(row, 1, QTableWidgetItem(str(s.customer_id or "عميل نقدي")))
            self.table.setItem(row, 2, QTableWidgetItem(f"{s.total:,.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{s.paid_amount:,.2f}"))
            
            # Status Badge simulation
            status_item = QTableWidgetItem(s.status)
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, status_item)
            
        Animations.pop_in(self.table.parentWidget(), 500, 400)
