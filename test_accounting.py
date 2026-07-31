import sys
import os

sys.path.insert(0, os.path.abspath('.'))
os.environ['POS_ERP_DB_PATH'] = ':memory:'

from pos_erp.database.db import SessionLocal, init_db
from pos_erp.database.models import Product, Sale, SaleItem, InventoryMovement, Account, Customer, Supplier, Purchase, Expense, Revenue
from pos_erp.services.sales_service import SalesService
from pos_erp.services.purchase_service import PurchaseService
from pos_erp.services.report_service import ReportService
from pos_erp.services.product_service import ProductService
from pos_erp.services.finance_service import FinanceService

def setup_test_db():
    init_db()

def test_accounting():
    setup_test_db()
    session = SessionLocal()
    
    print("--- STARTING ACCOUNTING AUDIT ---")
    cash_account = session.query(Account).filter_by(code='1001').first()
    print(f"Initial Cash Balance: {cash_account.balance if cash_account else 0.0}")
    
    # 1. Create a Product
    ProductService.add_product({
        'name': 'Test Product',
        'sku': 'TP-001',
        'purchase_price': 100.0,
        'selling_price': 150.0,
        'quantity': 50.0,
    }, user_id=1)
    
    prod = session.query(Product).filter_by(sku='TP-001').first()
    
    # 2. Make a Purchase
    purchase_data = {
        'subtotal': 1000.0,
        'discount': 0.0,
        'tax_amount': 0.0,
        'total': 1000.0,
        'paid_amount': 1000.0,
        'payment_method': 'CASH'
    }
    purchase_items = [{
        'product_id': prod.id,
        'quantity': 10.0,
        'unit_price': 100.0 # Same as before
    }]
    success, p_inv, msg = PurchaseService.create_purchase(purchase_data, purchase_items, user_id=1)
    print(f"Purchase Created: {success}, {msg}")
    
    session.expire_all()
    prod = session.query(Product).filter_by(sku='TP-001').first()
    print(f"Product Qty after purchase (Expected 60): {prod.quantity}")
    
    cash_account = session.query(Account).filter_by(code='1001').first()
    print(f"Cash Balance after purchase (Expected 4000): {cash_account.balance}")
    
    # 3. Make a Sale
    sale_data = {
        'subtotal': 300.0,
        'discount': 0.0,
        'tax_amount': 45.0,
        'total': 345.0,
        'paid_amount': 345.0,
        'payment_method': 'CASH'
    }
    sale_items = [{
        'product_id': prod.id,
        'quantity': 2.0,
        'unit_price': 150.0,
        'discount': 0.0,
        'tax': 45.0
    }]
    success, s_inv, msg = SalesService.create_sale(sale_data, sale_items, user_id=1)
    print(f"Sale Created: {success}, {msg}")
    
    session.expire_all()
    cash_account = session.query(Account).filter_by(code='1001').first()
    print(f"Cash Balance after sale (Expected 4345): {cash_account.balance}")
    
    prod = session.query(Product).filter_by(sku='TP-001').first()
    print(f"Product Qty after sale (Expected 58): {prod.quantity}")
    
    # 4. Check Profit
    stats = ReportService.get_dashboard_stats()
    # Gross Profit = Net Sales (300) - COGS (200) = 100
    # Net Profit = 100
    print(f"Stats -> Net Profit: {stats['net_profit']} (Expected: 100.0)")
    
    # 5. Make a Return
    sale = session.query(Sale).filter_by(invoice_number=s_inv).first()
    success, msg = SalesService.return_sale(sale.id, user_id=1)
    print(f"Sale Return: {success}, {msg}")
    
    session.expire_all()
    stats = ReportService.get_dashboard_stats()
    print(f"Stats after return -> Net Profit: {stats['net_profit']} (Expected: 0.0)")
    
    cash_account = session.query(Account).filter_by(code='1001').first()
    print(f"Cash Balance after return (Expected 4000): {cash_account.balance}")
    
    prod = session.query(Product).filter_by(sku='TP-001').first()
    print(f"Product Qty after return (Expected 60): {prod.quantity}")
    
    print("--- ACCOUNTING AUDIT COMPLETE ---")

if __name__ == '__main__':
    test_accounting()
