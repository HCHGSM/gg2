from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from pos_erp.services.report_service import ReportService
from pos_erp.services.sales_service import SalesService

class DashboardView(QWidget):
    """
    لوحة التحكم الرئيسية المتقدمة لعرض مؤشرات الأداء الحية، الإيرادات، الأرباح،
    تنبيهات المخزون المنخفض، وأحدث العمليات والفواتير.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()
        
        # Refresh timer every 30 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_data)
        self.timer.start(30000)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Header with Refresh button
        header_layout = QHBoxLayout()
        title = QLabel("لوحة التحكم والتحليلات المالية")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #1e293b; letter-spacing: -0.5px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()

        refresh_btn = QPushButton("تحديث البيانات")
        refresh_btn.setProperty("class", "PrimaryButton")
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)

        # Statistics Cards Grid (4 columns x 2 rows)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(18)

        self.card_sales = self.create_card("إجمالي المبيعات", "0.00 ج.س", "#3b82f6", "📈")
        self.card_profit = self.create_card("صافي الأرباح", "0.00 ج.س", "#10b981", "💰")
        self.card_purchases = self.create_card("إجمالي المشتريات", "0.00 ج.س", "#f59e0b", "🛒")
        self.card_expenses = self.create_card("إجمالي المصروفات", "0.00 ج.س", "#ef4444", "📉")
        
        self.card_revenues = self.create_card("الإيرادات الأخرى", "0.00 ج.س", "#6366f1", "💵")
        self.card_customers = self.create_card("إجمالي العملاء", "0", "#ec4899", "👥")
        self.card_suppliers = self.create_card("إجمالي الموردين", "0", "#14b8a6", "🏭")
        self.card_low_stock = self.create_card("تنبيهات نقص المخزون", "0", "#f97316", "⚠️")

        grid_layout.addWidget(self.card_sales['widget'], 0, 0)
        grid_layout.addWidget(self.card_profit['widget'], 0, 1)
        grid_layout.addWidget(self.card_purchases['widget'], 0, 2)
        grid_layout.addWidget(self.card_expenses['widget'], 0, 3)

        grid_layout.addWidget(self.card_revenues['widget'], 1, 0)
        grid_layout.addWidget(self.card_customers['widget'], 1, 1)
        grid_layout.addWidget(self.card_suppliers['widget'], 1, 2)
        grid_layout.addWidget(self.card_low_stock['widget'], 1, 3)

        layout.addLayout(grid_layout)

        # Recent Sales Table Section
        recent_label = QLabel("أحدث الفواتير والمعاملات المسجلة في النظام")
        recent_label.setStyleSheet("font-size: 18px; font-weight: 700; margin-top: 15px; color: #334155;")
        layout.addWidget(recent_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["رقم الفاتورة", "العميل", "الإجمالي النهائي", "المبلغ المدفوع", "طريقة الدفع", "وقت العملية"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("border-radius: 8px; font-size: 13px;")
        layout.addWidget(self.table)

    def create_card(self, title, value, color, icon):
        frame = QFrame()
        frame.setProperty("class", "Card")
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border-left: 6px solid {color};
                border-radius: 10px;
                border-top: 1px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                border-bottom: 1px solid #e2e8f0;
                padding: 15px;
            }}
        """)
        v_layout = QVBoxLayout(frame)
        v_layout.setContentsMargins(10, 5, 10, 5)
        
        top_row = QHBoxLayout()
        t_label = QLabel(title)
        t_label.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 700;")
        top_row.addWidget(t_label)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 18px;")
        top_row.addWidget(icon_lbl, alignment=Qt.AlignRight)
        v_layout.addLayout(top_row)

        v_val_label = QLabel(value)
        v_val_label.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 800; margin-top: 5px;")
        v_layout.addWidget(v_val_label)

        return {'widget': frame, 'value_label': v_val_label}

    def load_data(self):
        try:
            stats = ReportService.get_dashboard_stats()
            self.card_sales['value_label'].setText(f"{stats['total_sales']:,.2f} ج.س")
            self.card_profit['value_label'].setText(f"{stats['net_profit']:,.2f} ج.س")
            self.card_purchases['value_label'].setText(f"{stats['total_purchases']:,.2f} ج.س")
            self.card_expenses['value_label'].setText(f"{stats['total_expenses']:,.2f} ج.س")
            self.card_revenues['value_label'].setText(f"{stats['total_revenues']:,.2f} ج.س")
            self.card_customers['value_label'].setText(str(stats['customers_count']))
            self.card_suppliers['value_label'].setText(str(stats['suppliers_count']))
            self.card_low_stock['value_label'].setText(str(stats['low_stock_count']))

            sales = SalesService.get_all_sales()[:12] # Recent 12
            self.table.setRowCount(len(sales))
            for row, s in enumerate(sales):
                self.table.setItem(row, 0, QTableWidgetItem(s.invoice_number))
                self.table.setItem(row, 1, QTableWidgetItem(str(s.customer_id or "عميل نقدي افتراضي")))
                self.table.setItem(row, 2, QTableWidgetItem(f"{s.total:,.2f} ج.س"))
                self.table.setItem(row, 3, QTableWidgetItem(f"{s.paid_amount:,.2f} ج.س"))
                self.table.setItem(row, 4, QTableWidgetItem(s.payment_method))
                self.table.setItem(row, 5, QTableWidgetItem(str(s.created_at)))
        except Exception as e:
            print(f"Dashboard load error: {e}")
