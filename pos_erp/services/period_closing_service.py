from sqlalchemy import func
from pos_erp.database.models import FiscalYear, AccountingPeriod, Account, JournalEntry, JournalEntryLine
from pos_erp.services.accounting_service import AccountingService

class PeriodClosingService:
    @staticmethod
    def close_accounting_period(session, period_id):
        period = session.get(AccountingPeriod, period_id)
        if not period:
            raise ValueError("Accounting Period not found")
        if period.is_closed:
            raise ValueError("Period is already closed")
        
        period.is_closed = True

    @staticmethod
    def close_fiscal_year(session, fiscal_year_id, user_id):
        fy = session.get(FiscalYear, fiscal_year_id)
        if not fy:
            raise ValueError("Fiscal Year not found")
        if fy.is_closed:
            raise ValueError("Fiscal Year is already closed")
            
        # Get balances for all Revenue and Expense accounts for this FY
        # A simple approach: query all lines within FY dates
        query = session.query(JournalEntryLine).join(JournalEntry).join(Account).filter(
            func.date(JournalEntry.date) >= fy.start_date,
            func.date(JournalEntry.date) <= fy.end_date,
            Account.account_type.in_(['REVENUE', 'EXPENSE'])
        )
        lines = query.all()
        
        account_balances = {}
        for l in lines:
            if l.account.code not in account_balances:
                account_balances[l.account.code] = {'account': l.account, 'debit': 0.0, 'credit': 0.0}
            account_balances[l.account.code]['debit'] += l.debit
            account_balances[l.account.code]['credit'] += l.credit
            
        je_lines = []
        net_income = 0.0
        
        for code, data in account_balances.items():
            acc = data['account']
            if acc.account_type == 'REVENUE':
                # Revenue has credit balance. To close it, we Debit it.
                balance = data['credit'] - data['debit']
                if balance != 0:
                    je_lines.append({'account_code': code, 'debit': balance, 'credit': 0.0})
                    net_income += balance
            elif acc.account_type == 'EXPENSE':
                # Expense has debit balance. To close it, we Credit it.
                balance = data['debit'] - data['credit']
                if balance != 0:
                    je_lines.append({'account_code': code, 'debit': 0.0, 'credit': balance})
                    net_income -= balance
                    
        # Post the net difference to Retained Earnings
        if net_income > 0:
            je_lines.append({'account_code': '3100', 'debit': 0.0, 'credit': net_income})
        elif net_income < 0:
            je_lines.append({'account_code': '3100', 'debit': abs(net_income), 'credit': 0.0})
            
        if je_lines:
            AccountingService.post_journal_entry(
                session=session,
                date=fy.end_date,
                reference=f"CLOSING-{fy.name}",
                notes=f"Year End Closing for {fy.name}",
                user_id=user_id,
                lines_data=je_lines
            )
            
        fy.is_closed = True
