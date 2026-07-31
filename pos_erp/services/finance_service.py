from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Expense, Revenue, Account, AuditLog
from pos_erp.services.accounting_service import AccountingService
from datetime import datetime

class FinanceService:
    @staticmethod
    def add_expense(data, user_id=None):
        session = SessionLocal()
        try:
            exp = Expense(**data, user_id=user_id)
            session.add(exp)
            
            # Post double-entry journal (Debit Expense, Credit Cash)
            AccountingService.post_journal_entry(
                session=session,
                date=datetime.utcnow(),
                reference=data.get('reference', 'EXPENSE'),
                notes=f"Expense: {data['category']}",
                user_id=user_id,
                lines_data=[
                    {'account_code': '5100', 'debit': data['amount'], 'credit': 0.0}, # Operating Expense
                    {'account_code': '1001', 'debit': 0.0, 'credit': data['amount']}  # Cash
                ]
            )

            session.commit()
            if user_id:
                session.add(AuditLog(user_id=user_id, action='ADD_EXPENSE', details=f"Recorded expense {data['amount']} ({data['category']})"))
                session.commit()
            return True, "تم تسجيل المصروف بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def add_revenue(data, user_id=None):
        session = SessionLocal()
        try:
            rev = Revenue(**data, user_id=user_id)
            session.add(rev)
            
            # Post double-entry journal (Debit Cash, Credit Other Revenue)
            AccountingService.post_journal_entry(
                session=session,
                date=datetime.utcnow(),
                reference=data.get('reference', 'REVENUE'),
                notes=f"Revenue: {data['category']}",
                user_id=user_id,
                lines_data=[
                    {'account_code': '1001', 'debit': data['amount'], 'credit': 0.0}, # Cash
                    {'account_code': '4100', 'debit': 0.0, 'credit': data['amount']}  # Other Revenue
                ]
            )

            session.commit()
            if user_id:
                session.add(AuditLog(user_id=user_id, action='ADD_REVENUE', details=f"Recorded revenue {data['amount']} ({data['category']})"))
                session.commit()
            return True, "تم تسجيل الإيراد بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def get_accounts():
        session = SessionLocal()
        try:
            return session.query(Account).all()
        finally:
            session.close()

    @staticmethod
    def get_expenses():
        session = SessionLocal()
        try:
            return session.query(Expense).order_by(Expense.date.desc()).all()
        finally:
            session.close()

    @staticmethod
    def get_revenues():
        session = SessionLocal()
        try:
            return session.query(Revenue).order_by(Revenue.date.desc()).all()
        finally:
            session.close()
