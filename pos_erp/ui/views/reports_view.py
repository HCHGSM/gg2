import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox
from pos_erp.services.report_service import ReportService

class ReportsView(QWidget):
    """
    التقارير التحليلية الشاملة وتصدير البيانات إلى Excel و PDF.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        title = QLabel("التقارير التحليلية المتقدمة والتصدير")
        title.setProperty("cssClass", "view-title")
        layout.addWidget(title)

        btn_layout = QHBoxLayout()
        export_sales_btn = QPushButton("📥 تصدير تقرير المبيعات الشامل (Excel)")
        export_sales_btn.setProperty("cssClass", "primary")
        export_sales_btn.clicked.connect(self.export_sales)
        btn_layout.addWidget(export_sales_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def export_sales(self):
        path = os.path.expanduser('~/sales_comprehensive_report.xlsx')
        success, msg = ReportService.export_sales_excel(path)
        if success:
            QMessageBox.information(self, "نجاح التصدير", f"{msg}\nالمسار: {path}")
        else:
            QMessageBox.critical(self, "خطأ", msg)
