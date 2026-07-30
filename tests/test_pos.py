import unittest
from pos_erp.database.db import SessionLocal, init_db
from pos_erp.services.auth_service import AuthService
from pos_erp.services.product_service import ProductService
from pos_erp.services.sales_service import SalesService
from pos_erp.services.finance_service import FinanceService

class TestPOSTsystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_authentication_success(self):
        user, msg = AuthService.authenticate("admin", "admin123")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "admin")

    def test_authentication_failure(self):
        user, msg = AuthService.authenticate("admin", "wrongpassword")
        self.assertIsNone(user)

    def test_product_addition(self):
        data = {
            'name': 'اختبار منتج',
            'sku': 'TST-999',
            'barcode': '123456789',
            'purchase_price': 50.0,
            'selling_price': 100.0,
            'quantity': 20.0,
            'min_stock': 2.0,
            'tax_rate': 15.0
        }
        success, msg = ProductService.add_product(data)
        self.assertTrue(success)

    def test_finance_expense(self):
        data = {
            'category': 'ضيافة مكتب',
            'amount': 150.0,
            'notes': 'اختبار مصروفات'
        }
        success, msg = FinanceService.add_expense(data)
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main()
