import sys
import os

os.environ['POS_ERP_DB_PATH'] = ':memory:'
sys.path.insert(0, os.path.abspath('.'))

from pos_erp.database.db import SessionLocal, init_db, engine
from pos_erp.database.models import Base, FiscalYear, Account, JournalEntryLine
from pos_erp.services.period_closing_service import PeriodClosingService
from pos_erp.services.general_ledger_service import GeneralLedgerService

def test_closing():
    Base.metadata.create_all(bind=engine)
    init_db()
    from seed_advanced import seed_new_settings
    seed_new_settings()
    
    session = SessionLocal()
    fy = session.query(FiscalYear).first()
    
    # Simulate some income
    from pos_erp.services.accounting_service import AccountingService
    from datetime import datetime
    
    AccountingService.post_journal_entry(
        session=session,
        date=fy.start_date,
        reference='TEST-INC',
        notes='Test Income',
        user_id=1,
        lines_data=[
            {'account_code': '1001', 'debit': 5000.0, 'credit': 0.0},
            {'account_code': '4000', 'debit': 0.0, 'credit': 5000.0}
        ]
    )
    
    AccountingService.post_journal_entry(
        session=session,
        date=fy.end_date,
        reference='TEST-EXP',
        notes='Test Expense',
        user_id=1,
        lines_data=[
            {'account_code': '5100', 'debit': 2000.0, 'credit': 0.0},
            {'account_code': '1001', 'debit': 0.0, 'credit': 2000.0}
        ]
    )
    session.commit()
    
    # Net income should be 3000
    is_data = GeneralLedgerService.get_income_statement(start_date=fy.start_date, end_date=fy.end_date)
    print(f"Revenue: {is_data['total_revenue']}, Expense: {is_data['total_expense']}")
    
    # check db lines
    lines = session.query(JournalEntryLine).all()
    for l in lines:
        print(f"Line: {l.account.account_type} {l.debit}/{l.credit} - Date: {l.journal_entry.date}")
        
    print(f"Net Income Before Close: {is_data['net_income']}")
    
    # Close FY
    PeriodClosingService.close_fiscal_year(session, fy.id, 1)
    session.commit()
    
    # Retained Earnings should be 3000
    retained_earnings = session.query(Account).filter_by(code='3100').first()
    print(f"Retained Earnings After Close: {retained_earnings.balance}")
    
    if retained_earnings.balance != 3000.0:
        print("ERROR: Retained Earnings calculation failed.")
        sys.exit(1)
        
    # Attempt to post to closed year should fail
    try:
        AccountingService.post_journal_entry(
            session=session,
            date=fy.start_date,
            reference='FAIL-TEST',
            notes='Should Fail',
            user_id=1,
            lines_data=[
                {'account_code': '1001', 'debit': 100.0, 'credit': 0.0},
                {'account_code': '4000', 'debit': 0.0, 'credit': 100.0}
            ]
        )
        print("ERROR: Allowed posting to closed fiscal year!")
        sys.exit(1)
    except ValueError as e:
        print(f"Success: Blocked posting to closed year ({str(e)})")
        
    print("--- FISCAL YEAR CLOSING TEST PASSED ---")

if __name__ == '__main__':
    test_closing()
