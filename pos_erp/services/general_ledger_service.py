from sqlalchemy.orm import joinedload
from sqlalchemy import func
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Account, JournalEntry, JournalEntryLine

class GeneralLedgerService:
    @staticmethod
    def get_ledger(account_code, start_date=None, end_date=None):
        session = SessionLocal()
        try:
            account = session.query(Account).filter_by(code=account_code).first()
            if not account:
                return None
                
            query = session.query(JournalEntryLine).join(JournalEntry).filter(JournalEntryLine.account_id == account.id)
            
            # Calculate Opening Balance
            opening_balance = 0.0
            if start_date:
                past_lines = session.query(JournalEntryLine).join(JournalEntry).filter(
                    JournalEntryLine.account_id == account.id,
                    JournalEntry.date < start_date
                ).all()
                if account.account_type in ['ASSET', 'EXPENSE']:
                    opening_balance = sum(l.debit - l.credit for l in past_lines)
                else:
                    opening_balance = sum(l.credit - l.debit for l in past_lines)
                    
            if start_date:
                query = query.filter(func.date(JournalEntry.date) >= start_date)
            if end_date:
                query = query.filter(func.date(JournalEntry.date) <= end_date)
                
            lines = query.options(joinedload(JournalEntryLine.journal_entry)).order_by(JournalEntry.date.asc()).all()
            
            transactions = []
            running_balance = opening_balance
            
            for line in lines:
                if account.account_type in ['ASSET', 'EXPENSE']:
                    running_balance += (line.debit - line.credit)
                else:
                    running_balance += (line.credit - line.debit)
                    
                transactions.append({
                    'date': line.journal_entry.date,
                    'reference': line.journal_entry.reference,
                    'notes': line.journal_entry.notes,
                    'debit': line.debit,
                    'credit': line.credit,
                    'balance': running_balance
                })
                
            return {
                'account': account,
                'opening_balance': opening_balance,
                'transactions': transactions,
                'closing_balance': running_balance
            }
        finally:
            session.close()

    @staticmethod
    def get_income_statement(start_date=None, end_date=None):
        session = SessionLocal()
        try:
            query = session.query(JournalEntryLine).join(JournalEntry).join(Account)
            if start_date:
                query = query.filter(func.date(JournalEntry.date) >= start_date)
            if end_date:
                query = query.filter(func.date(JournalEntry.date) <= end_date)
                
            rev_lines = query.filter(Account.account_type == 'REVENUE').all()
            exp_lines = query.filter(Account.account_type == 'EXPENSE').all()
            
            total_revenue = sum(l.credit - l.debit for l in rev_lines)
            total_expense = sum(l.debit - l.credit for l in exp_lines)
            
            return {
                'total_revenue': total_revenue,
                'total_expense': total_expense,
                'net_income': total_revenue - total_expense
            }
        finally:
            session.close()

    @staticmethod
    def get_balance_sheet(as_of_date=None):
        session = SessionLocal()
        try:
            query = session.query(JournalEntryLine).join(JournalEntry).join(Account)
            if as_of_date:
                query = query.filter(func.date(JournalEntry.date) <= as_of_date)
                
            asset_lines = query.filter(Account.account_type == 'ASSET').all()
            liability_lines = query.filter(Account.account_type == 'LIABILITY').all()
            equity_lines = query.filter(Account.account_type == 'EQUITY').all()
            
            total_assets = sum(l.debit - l.credit for l in asset_lines)
            total_liabilities = sum(l.credit - l.debit for l in liability_lines)
            total_equity = sum(l.credit - l.debit for l in equity_lines)
            
            # Retained earnings = Net Income from all time up to as_of_date
            is_data = GeneralLedgerService.get_income_statement(end_date=as_of_date)
            total_equity += is_data['net_income']
            
            return {
                'total_assets': total_assets,
                'total_liabilities': total_liabilities,
                'total_equity': total_equity,
                'is_balanced': round(total_assets, 2) == round(total_liabilities + total_equity, 2)
            }
        finally:
            session.close()
