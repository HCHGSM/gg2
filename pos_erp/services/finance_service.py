from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Expense, Revenue, Account, Transaction, AuditLog

class FinanceService:
    @staticmethod
    def add_expense(data, user_id=None):
        session = SessionLocal()
        try:
            exp = Expense(**data, user_id=user_id)
            session.add(exp)
            
            # Deduct from cash account
            cash_account = session.query(Account).filter_by(account_type='CASH').first()
            if cash_account:
                cash_account.balance -= data['amount']
                tx = Transaction(
                    account_id=cash_account.id,
                    transaction_type='WITHDRAWAL',
                    amount=data['amount'],
                    reference=data.get('reference', 'EXPENSE'),
                    user_id=user_id,
                    notes=f"Expense: {data['category']}"
                )
                session.add(tx)

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
            
            cash_account = session.query(Account).filter_by(account_type='CASH').first()
            if cash_account:
                cash_account.balance += data['amount']
                tx = Transaction(
                    account_id=cash_account.id,
                    transaction_type='DEPOSIT',
                    amount=data['amount'],
                    reference=data.get('reference', 'REVENUE'),
                    user_id=user_id,
                    notes=f"Revenue: {data['category']}"
                )
                session.add(tx)

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
