import sys
import os
import time

sys.path.insert(0, os.path.abspath('.'))

# Force the database path to a file so we can backup and restore
DB_FILE = os.path.abspath('acceptance_pos_erp.db')
os.environ['POS_ERP_DB_PATH'] = DB_FILE

from pos_erp.database.db import SessionLocal, init_db, engine
from pos_erp.database.models import User, Supplier, Customer, Category, Product, Account, Sale, Purchase
from pos_erp.services.auth_service import AuthService
from pos_erp.services.product_service import ProductService
from pos_erp.services.purchase_service import PurchaseService
from pos_erp.services.sales_service import SalesService
from pos_erp.services.report_service import ReportService
from pos_erp.services.backup_service import BackupService
import bcrypt

def log_step(step_num, description, expected, actual, passed):
    status = "PASS" if passed else "FAIL"
    print(f"\n--- STEP {step_num}: {description} ---")
    print(f"Expected : {expected}")
    print(f"Actual   : {actual}")
    print(f"Status   : {status}")
    if not passed:
        print(">>> ACCEPTANCE TEST FAILED! ABORTING! <<<")
        sys.exit(1)

def run_acceptance_test():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    # 0. Start application / init DB
    init_db()
    
    # 1. Create administrator
    session = SessionLocal()
    # init_db creates a default admin (admin / admin123)
    admin_user, msg = AuthService.authenticate('admin', 'admin123')
    log_step(1, "Create administrator & Authenticate", 
             "admin user authenticated successfully", 
             f"User: {admin_user.username if admin_user else None}", 
             admin_user is not None)
    
    # 2. Create supplier
    new_supplier = Supplier(name='Global Tech Supplies', phone='123456789', current_balance=0.0)
    session.add(new_supplier)
    session.commit()
    session.refresh(new_supplier)
    log_step(2, "Create supplier", 
             "Supplier 'Global Tech Supplies' exists", 
             f"Supplier ID: {new_supplier.id}, Name: {new_supplier.name}", 
             new_supplier.id is not None)
    supplier_id = new_supplier.id

    # 3. Create customer
    new_customer = Customer(name='VIP Client', phone='987654321', current_balance=0.0)
    session.add(new_customer)
    session.commit()
    session.refresh(new_customer)
    log_step(3, "Create customer", 
             "Customer 'VIP Client' exists", 
             f"Customer ID: {new_customer.id}, Name: {new_customer.name}", 
             new_customer.id is not None)
    customer_id = new_customer.id

    # 4. Create category
    ProductService.add_category("Electronics", "Electronic Devices")
    cat = session.query(Category).filter_by(name="Electronics").first()
    log_step(4, "Create category", 
             "Category 'Electronics' exists", 
             f"Category ID: {cat.id if cat else None}", 
             cat is not None)
    
    # 5. Create product
    ProductService.add_product({
        'name': 'Laptop Pro',
        'sku': 'LP-001',
        'category_id': cat.id,
        'supplier_id': supplier_id,
        'purchase_price': 0.0,
        'selling_price': 1500.0,
        'quantity': 0.0,
    }, user_id=admin_user.id)
    
    prod = session.query(Product).filter_by(sku='LP-001').first()
    log_step(5, "Create product", 
             "Product 'Laptop Pro' exists with qty 0", 
             f"Product ID: {prod.id}, Qty: {prod.quantity}", 
             prod is not None and prod.quantity == 0)
    product_id = prod.id

    # Get initial cash balance
    cash_account = session.query(Account).filter_by(code='1001').first()
    initial_cash = cash_account.balance

    # 6. Purchase stock
    purchase_data = {
        'supplier_id': supplier_id,
        'subtotal': 5000.0,
        'discount': 0.0,
        'tax_amount': 0.0,
        'total': 5000.0,
        'paid_amount': 5000.0, # Fully paid
        'payment_method': 'CASH'
    }
    purchase_items = [{
        'product_id': product_id,
        'quantity': 10.0,
        'unit_price': 500.0 # Cost per unit
    }]
    success, p_inv, msg = PurchaseService.create_purchase(purchase_data, purchase_items, user_id=admin_user.id)
    log_step(6, "Purchase stock", 
             "Purchase created successfully", 
             f"Success: {success}, Invoice: {p_inv}", 
             success == True)

    # 7. Verify inventory
    session.expire_all()
    prod = session.query(Product).filter_by(sku='LP-001').first()
    log_step(7, "Verify inventory after purchase", 
             "Product Qty = 10, Avg Cost = 500.0", 
             f"Qty: {prod.quantity}, Cost: {prod.purchase_price}", 
             prod.quantity == 10.0 and prod.purchase_price == 500.0)

    # 8-11. Sell products, apply discount, apply tax, complete payment
    sale_data = {
        'customer_id': customer_id,
        'subtotal': 3000.0,
        'discount': 200.0,
        'tax_amount': 280.0,
        'total': 3080.0,
        'paid_amount': 2000.0,
        'payment_method': 'CASH'
    }
    sale_items = [{
        'product_id': product_id,
        'quantity': 2.0,
        'unit_price': 1500.0,
        'discount': 200.0,
        'tax': 280.0
    }]
    success, s_inv, msg = SalesService.create_sale(sale_data, sale_items, user_id=admin_user.id)
    log_step("8-11", "Sell products (Discount, Tax, Partial Payment)", 
             "Sale created successfully", 
             f"Success: {success}, Invoice: {s_inv}", 
             success == True)
    
    # 12. Verify customer balance
    session.expire_all()
    customer = session.get(Customer, customer_id)
    log_step(12, "Verify customer balance", 
             "Customer balance = 1080.0", 
             f"Balance: {customer.current_balance}", 
             customer.current_balance == 1080.0)

    # 13. Verify cash balance
    expected_cash = initial_cash - 5000.0 + 2000.0
    cash_account = session.query(Account).filter_by(code='1001').first()
    log_step(13, "Verify cash balance", 
             f"Cash balance = {expected_cash}", 
             f"Balance: {cash_account.balance}", 
             cash_account.balance == expected_cash)

    # 14. Verify inventory quantity
    prod = session.query(Product).filter_by(sku='LP-001').first()
    log_step(14, "Verify inventory quantity", 
             "Product Qty = 8", 
             f"Qty: {prod.quantity}", 
             prod.quantity == 8.0)
    
    # 15. Return one invoice
    sale_to_return = session.query(Sale).filter_by(invoice_number=s_inv).first()
    success, msg = SalesService.return_sale(sale_to_return.id, user_id=admin_user.id)
    log_step(15, "Return one invoice", 
             "Return successful", 
             f"Success: {success}, Msg: {msg}", 
             success == True)

    # 16. Verify inventory restoration
    session.expire_all()
    prod = session.query(Product).filter_by(sku='LP-001').first()
    log_step(16, "Verify inventory restoration", 
             "Product Qty = 10", 
             f"Qty: {prod.quantity}", 
             prod.quantity == 10.0)

    # 17. Verify profit
    stats = ReportService.get_dashboard_stats()
    log_step(17, "Verify profit", 
             "Net profit = 0.0 (since sale was returned)", 
             f"Profit: {stats['net_profit']}", 
             stats['net_profit'] == 0.0)

    # 18. Generate reports
    tb = ReportService.get_trial_balance()
    excel_path = 'test_sales_report.xlsx'
    success, msg = ReportService.export_sales_excel(excel_path)
    log_step(18, "Generate reports", 
             "Trial Balance & Excel created", 
             f"TB valid: {'total_assets' in tb}, Excel exists: {os.path.exists(excel_path)}", 
             'total_assets' in tb and success and os.path.exists(excel_path))

    # 19. Backup database
    success, msg, backup_path = BackupService.create_backup()
    log_step(19, "Backup database", 
             "Backup created", 
             f"Success: {success}, Path: {backup_path}", 
             success and os.path.exists(backup_path))

    # 20. Restore backup
    # Mutate DB to prove restore works
    session.delete(prod)
    session.commit()
    session.expire_all()
    
    success, msg = BackupService.restore_backup(backup_path)
    log_step(20, "Restore backup", 
             "Restore successful", 
             f"Success: {success}, Msg: {msg}", 
             success == True)

    # 21. Restart application
    engine.dispose()
    session.close()
    SessionLocal.remove()
    
    # re-init to simulate restart
    from pos_erp.database.db import engine as new_engine
    session2 = SessionLocal()

    # 22. Verify all data remains correct
    expected_cash_reverted = initial_cash - 5000.0
    restored_prod = session2.query(Product).filter_by(sku='LP-001').first()
    restored_cash = session2.query(Account).filter_by(code='1001').first()
    log_step(22, "Verify all data remains correct after restart", 
             f"Product Qty = 10, Cash = {expected_cash_reverted}", 
             f"Product Qty: {restored_prod.quantity if restored_prod else None}, Cash: {restored_cash.balance if restored_cash else None}", 
             restored_prod is not None and restored_prod.quantity == 10.0 and restored_cash.balance == expected_cash_reverted)

    print("\n=======================================================")
    print("ALL 22 ACCEPTANCE TEST SCENARIOS PASSED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == '__main__':
    run_acceptance_test()
