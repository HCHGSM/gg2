import unittest
from pos_erp.database.db import SessionLocal, init_db
from pos_erp.database.models import Sale
from pos_erp.services.sales_service import SalesService
from pos_erp.services.report_service import ReportService
from pos_erp.services.receipt_service import ReceiptService
from pos_erp.services.backup_service import BackupService

class TestComprehensive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_dashboard_stats(self):
        stats = ReportService.get_dashboard_stats()
        self.assertIn('total_sales', stats)
        self.assertIn('net_profit', stats)
        self.assertIn('products_count', stats)

    def test_backup_service(self):
        success, msg = BackupService.create_backup()
        self.assertTrue(success)

    def test_receipt_formatting(self):
        session = SessionLocal()
        try:
            class DummySale:
                invoice_number = "INV-001"
                created_at = "2026-07-30"
                payment_method = "CASH"
                subtotal = 1000.0
                tax_amount = 150.0
                total = 1150.0
                paid_amount = 1150.0
            
            receipt = ReceiptService.generate_receipt_text(DummySale(), [])
            self.assertIn("INV-001", receipt)
            self.assertIn("1,150.00", receipt)
        finally:
            session.close()

if __name__ == '__main__':
    unittest.main()
