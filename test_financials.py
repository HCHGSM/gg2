import sys
import os

sys.path.insert(0, os.path.abspath('.'))

from pos_erp.services.general_ledger_service import GeneralLedgerService
from pos_erp.services.inventory_valuation_service import InventoryValuationService
from pos_erp.database.db import SessionLocal, init_db

def test_financial_statements():
    os.environ['POS_ERP_DB_PATH'] = 'test_financials.db'
    if os.path.exists('test_financials.db'): os.remove('test_financials.db')
    
    # We must trigger table creation
    from pos_erp.database.models import Base
    from pos_erp.database.db import engine
    Base.metadata.create_all(bind=engine)
    
    init_db()
    print("--- STARTING FINANCIAL STATEMENTS TEST ---")
    
    is_data = GeneralLedgerService.get_income_statement()
    print(f"Income Statement - Revenue: {is_data['total_revenue']}, Expense: {is_data['total_expense']}, Net Income: {is_data['net_income']}")
    
    bs_data = GeneralLedgerService.get_balance_sheet()
    print(f"Balance Sheet - Assets: {bs_data['total_assets']}, Liab: {bs_data['total_liabilities']}, Equity: {bs_data['total_equity']}")
    print(f"Balance Sheet Balanced? {bs_data['is_balanced']}")
    
    ledger = GeneralLedgerService.get_ledger('1001') # Cash
    if ledger:
        print(f"Cash Ledger - Closing Balance: {ledger['closing_balance']}")
    
    val = InventoryValuationService.get_stock_valuation()
    print(f"Inventory Valuation Total: {val['total_value']}")
    
    if not bs_data['is_balanced']:
        print("ERROR: BALANCE SHEET OUT OF BALANCE!")
        sys.exit(1)
        
    print("--- FINANCIAL STATEMENTS TEST COMPLETE ---")

if __name__ == '__main__':
    test_financial_statements()