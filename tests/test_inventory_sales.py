import unittest
from pos_erp.database.db import SessionLocal, init_db
from pos_erp.services.product_service import ProductService
from pos_erp.services.sales_service import SalesService
from pos_erp.services.finance_service import FinanceService

class TestInventoryAndSales(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_stock_deduction_on_sale(self):
        session = SessionLocal()
        try:
            # Add product with known stock
            prod_data = {
                'name': 'Laptop Dell XPS',
                'sku': 'DELL-XPS-01',
                'barcode': '987654321',
                'purchase_price': 1000.0,
                'selling_price': 1500.0,
                'quantity': 10.0,
                'min_stock': 2.0,
                'tax_rate': 15.0
            }
            ProductService.add_product(prod_data)
            products = ProductService.get_all_products()
            target_prod = [p for p in products if p.sku == 'DELL-XPS-01'][0]
            
            initial_qty = target_prod.quantity
            
            sale_data = {
                'subtotal': 1500.0,
                'discount': 0.0,
                'tax_amount': 225.0,
                'total': 1725.0,
                'paid_amount': 1725.0,
                'payment_method': 'CASH',
                'notes': 'Unit test sale'
            }
            items_data = [{
                'product_id': target_prod.id,
                'quantity': 2.0,
                'unit_price': 1500.0,
                'discount': 0.0,
                'tax': 225.0
            }]
            
            success, inv_no, msg = SalesService.create_sale(sale_data, items_data, 1)
            self.assertTrue(success)
            
            # Verify stock deduction
            session.expire_all()
            updated_prod = session.query(ProductService).get if hasattr(ProductService, 'get') else None
            # Check via ProductService
            updated_products = ProductService.get_all_products()
            updated_target = [p for p in updated_products if p.sku == 'DELL-XPS-01'][0]
            self.assertEqual(updated_target.quantity, initial_qty - 2.0)
        finally:
            session.close()

if __name__ == '__main__':
    unittest.main()
