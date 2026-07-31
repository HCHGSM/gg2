import sys
import os
import unittest
from datetime import datetime

# Enforce a fresh temporary database for enterprise testing
os.environ['POS_ERP_DB_PATH'] = ':memory:'
sys.path.insert(0, os.path.abspath('.'))

from pos_erp.database.db import SessionLocal, init_db, engine
from pos_erp.database.models import Base, FiscalYear, Account, User, Product, Supplier, Customer, Category, Setting
from pos_erp.services.auth_service import AuthService
from pos_erp.services.product_service import ProductService
from pos_erp.services.purchase_service import PurchaseService
from pos_erp.services.sales_service import SalesService
from pos_erp.services.general_ledger_service import GeneralLedgerService
from pos_erp.services.inventory_costing_service import InventoryCostingService
from pos_erp.services.period_closing_service import PeriodClosingService
from pos_erp.services.finance_service import FinanceService
from pos_erp.services.report_service import ReportService
from pos_erp.services.backup_service import BackupService

class EnterpriseERPSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        init_db()
        from seed_advanced import seed_new_settings
        seed_new_settings()
        
    def setUp(self):
        self.session = SessionLocal()

    def tearDown(self):
        self.session.close()

    def test_01_authentication(self):
        user, msg = AuthService.authenticate('admin', 'admin123')
        self.assertIsNotNone(user)
        
        user_fail, msg_fail = AuthService.authenticate('admin', 'wrong')
        self.assertIsNone(user_fail)
        
        success, msg = AuthService.change_password(user.id, 'admin123', 'newpass123')
        self.assertTrue(success)
        
        # Revert
        AuthService.change_password(user.id, 'newpass123', 'admin123')

    def test_02_product_lifecycle(self):
        # Product Update & Delete
        user, _ = AuthService.authenticate('admin', 'admin123')
        success, msg = ProductService.add_product({'name': 'Test Del', 'purchase_price': 10, 'selling_price': 20, 'quantity': 0}, user_id=user.id)
        self.assertTrue(success)
        
        prod = self.session.query(Product).filter_by(name='Test Del').first()
        success, msg = ProductService.update_product(prod.id, {'name': 'Test Del Updated'}, user_id=user.id)
        self.assertTrue(success)
        
        success, msg = ProductService.delete_product(prod.id, user_id=user.id)
        self.assertTrue(success)

    def test_03_finance_lifecycle(self):
        user, _ = AuthService.authenticate('admin', 'admin123')
        
        # Inject equity to test expense
        from pos_erp.services.accounting_service import AccountingService
        AccountingService.post_journal_entry(
            self.session, datetime.utcnow(), 'EQUITY', 'Init', user.id,
            [
                {'account_code': '1001', 'debit': 1000.0, 'credit': 0.0},
                {'account_code': '3000', 'debit': 0.0, 'credit': 1000.0}
            ]
        )
        self.session.commit()
        
        # Add Expense
        success, msg = FinanceService.add_expense({'category': 'Rent', 'amount': 500.0, 'reference': 'EXP-001'}, user_id=user.id)
        self.assertTrue(success)
        
        # Add Revenue
        success, msg = FinanceService.add_revenue({'category': 'Consulting', 'amount': 300.0, 'reference': 'REV-001'}, user_id=user.id)
        self.assertTrue(success)
        
        exps = FinanceService.get_expenses()
        self.assertTrue(len(exps) > 0)
        
        revs = FinanceService.get_revenues()
        self.assertTrue(len(revs) > 0)
        
        accs = FinanceService.get_accounts()
        self.assertTrue(len(accs) > 0)

    def test_04_double_entry_and_costing(self):
        user, _ = AuthService.authenticate('admin', 'admin123')
        
        supplier = Supplier(name='Enterprise Vendor', current_balance=0.0)
        customer = Customer(name='Enterprise Client', current_balance=0.0)
        category = Category(name='Enterprise Goods')
        self.session.add_all([supplier, customer, category])
        self.session.commit()
        
        ProductService.add_product({
            'name': 'Enterprise Server',
            'sku': 'ENT-SRV',
            'category_id': category.id,
            'supplier_id': supplier.id,
            'purchase_price': 0.0,
            'selling_price': 5000.0,
            'quantity': 0.0,
        }, user_id=user.id)
        prod = self.session.query(Product).filter_by(sku='ENT-SRV').first()
        
        # Inject cash
        from pos_erp.services.accounting_service import AccountingService
        AccountingService.post_journal_entry(
            self.session, datetime.utcnow(), 'EQUITY-INJ', 'Init Cap', user.id,
            [
                {'account_code': '1001', 'debit': 50000.0, 'credit': 0.0},
                {'account_code': '3000', 'debit': 0.0, 'credit': 50000.0}
            ]
        )
        self.session.commit()
        
        purchase_data = {
            'supplier_id': supplier.id, 'subtotal': 10000.0, 'discount': 0.0,
            'tax_amount': 0.0, 'total': 10000.0, 'paid_amount': 10000.0, 'payment_method': 'CASH'
        }
        success, inv, msg = PurchaseService.create_purchase(purchase_data, [{'product_id': prod.id, 'quantity': 10, 'unit_price': 1000.0}], user_id=user.id)
        self.assertTrue(success)
        
        sale_data = {
            'customer_id': customer.id, 'subtotal': 10000.0, 'discount': 0.0,
            'tax_amount': 0.0, 'total': 10000.0, 'paid_amount': 10000.0, 'payment_method': 'CASH'
        }
        success, s_inv, msg = SalesService.create_sale(sale_data, [{'product_id': prod.id, 'quantity': 2, 'unit_price': 5000.0}], user_id=user.id)
        self.assertTrue(success)
        
        from pos_erp.database.models import Sale
        sale_rec = self.session.query(Sale).filter_by(invoice_number=s_inv).first()
        success, msg = SalesService.return_sale(sale_rec.id, user_id=user.id)
        self.assertTrue(success)

    def test_05_fifo_costing(self):
        user, _ = AuthService.authenticate('admin', 'admin123')
        
        # Switch to FIFO
        setting = self.session.query(Setting).filter_by(key='costing_method').first()
        setting.value = 'FIFO'
        self.session.commit()
        
        ProductService.add_product({'name': 'FIFO Prod', 'purchase_price': 0, 'selling_price': 20, 'quantity': 0}, user_id=user.id)
        prod = self.session.query(Product).filter_by(name='FIFO Prod').first()
        
        # Buy 5 @ 10
        PurchaseService.create_purchase(
            {'supplier_id': None, 'subtotal': 50.0, 'discount': 0.0, 'tax_amount': 0.0, 'total': 50.0, 'paid_amount': 0.0, 'payment_method': 'CASH'},
            [{'product_id': prod.id, 'quantity': 5, 'unit_price': 10.0}], user_id=user.id
        )
        
        # Buy 5 @ 20
        PurchaseService.create_purchase(
            {'supplier_id': None, 'subtotal': 100.0, 'discount': 0.0, 'tax_amount': 0.0, 'total': 100.0, 'paid_amount': 0.0, 'payment_method': 'CASH'},
            [{'product_id': prod.id, 'quantity': 5, 'unit_price': 20.0}], user_id=user.id
        )
        
        # Sell 7 units
        success, s_inv, msg = SalesService.create_sale(
            {'customer_id': None, 'subtotal': 140.0, 'discount': 0.0, 'tax_amount': 0.0, 'total': 140.0, 'paid_amount': 0.0, 'payment_method': 'CASH'},
            [{'product_id': prod.id, 'quantity': 7, 'unit_price': 20.0}], user_id=user.id
        )
        self.assertTrue(success)
        
        # FIFO cost should be: 5 @ 10 + 2 @ 20 = 50 + 40 = 90
        # Check Journal Entries COGS
        from pos_erp.database.models import Sale, SaleItem
        sale = self.session.query(Sale).filter_by(invoice_number=s_inv).first()
        self.assertEqual(sale.items[0].cost_total, 90.0)
        
        # Revert Setting to Weighted Average
        setting.value = 'WEIGHTED_AVERAGE'
        self.session.commit()

    def test_06_standard_costing(self):
        user, _ = AuthService.authenticate('admin', 'admin123')
        setting = self.session.query(Setting).filter_by(key='costing_method').first()
        setting.value = 'STANDARD'
        self.session.commit()
        
        ProductService.add_product({'name': 'STD Prod', 'purchase_price': 15.0, 'selling_price': 30.0, 'quantity': 0}, user_id=user.id)
        prod = self.session.query(Product).filter_by(name='STD Prod').first()
        
        # Buy @ 10
        PurchaseService.create_purchase(
            {'supplier_id': None, 'subtotal': 50.0, 'discount': 0.0, 'tax_amount': 0.0, 'total': 50.0, 'paid_amount': 0.0, 'payment_method': 'CASH'},
            [{'product_id': prod.id, 'quantity': 5, 'unit_price': 10.0}], user_id=user.id
        )
        
        # Standard cost remains 15.0
        prod2 = self.session.query(Product).filter_by(name='STD Prod').first()
        self.assertEqual(prod2.purchase_price, 15.0)

    def test_07_reports(self):
        stats = ReportService.get_dashboard_stats()
        self.assertTrue('net_profit' in stats)
        cf = ReportService.get_cash_flow()
        self.assertTrue('inflows' in cf)
        tb = ReportService.get_trial_balance()
        self.assertTrue('is_balanced' in tb)

    def test_08_fiscal_year_closing(self):
        fy = self.session.query(FiscalYear).first()
        PeriodClosingService.close_fiscal_year(self.session, fy.id, 1)
        self.session.commit()
        self.assertTrue(fy.is_closed)

if __name__ == '__main__':
    unittest.main()
