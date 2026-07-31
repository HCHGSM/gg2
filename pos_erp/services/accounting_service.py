from datetime import datetime
from pos_erp.database.models import JournalEntry, JournalEntryLine, Account

class AccountingService:
    @staticmethod
    def post_journal_entry(session, date, reference, notes, user_id, lines_data):
        """
        lines_data: list of dicts with {'account_code': str, 'debit': float, 'credit': float}
        """
        # Ensure debits equal credits
        total_debit = round(sum(l.get('debit', 0.0) for l in lines_data), 4)
        total_credit = round(sum(l.get('credit', 0.0) for l in lines_data), 4)
        
        if total_debit != total_credit:
            raise ValueError(f"Journal Entry not balanced! Debits: {total_debit}, Credits: {total_credit}")
            
        if total_debit == 0.0 and total_credit == 0.0:
            return None # Nothing to post
            
        je_date = date or datetime.utcnow()
        
        # Check if period is closed
        from pos_erp.database.models import FiscalYear, AccountingPeriod
        fy = session.query(FiscalYear).filter(FiscalYear.start_date <= je_date, FiscalYear.end_date >= je_date).first()
        if fy and fy.is_closed:
            raise ValueError(f"Cannot post to a closed Fiscal Year ({fy.name})")
            
        period = session.query(AccountingPeriod).filter(AccountingPeriod.start_date <= je_date, AccountingPeriod.end_date >= je_date).first()
        if period and period.is_closed:
            raise ValueError(f"Cannot post to a closed Accounting Period ({period.name})")
            
        je = JournalEntry(
            date=date or datetime.utcnow(),
            reference=reference,
            notes=notes,
            user_id=user_id
        )
        session.add(je)
        session.flush()
        
        for line in lines_data:
            if line.get('debit', 0.0) == 0.0 and line.get('credit', 0.0) == 0.0:
                continue
                
            account_code = line['account_code']
            account = session.query(Account).filter_by(code=account_code).first()
            if not account:
                raise ValueError(f"Account with code {account_code} not found")
                
            jel = JournalEntryLine(
                journal_entry_id=je.id,
                account_id=account.id,
                debit=line.get('debit', 0.0),
                credit=line.get('credit', 0.0)
            )
            session.add(jel)
            
            # Update cached balance (Assets/Expenses are Debit normal, Liab/Equity/Rev are Credit normal)
            if account.account_type in ['ASSET', 'EXPENSE']:
                account.balance += (jel.debit - jel.credit)
            else:
                account.balance += (jel.credit - jel.debit)
                
        return je

