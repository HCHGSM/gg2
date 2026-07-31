from datetime import datetime
from sqlalchemy.exc import IntegrityError
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Purchase, PurchaseItem, Product, Supplier, Account, AuditLog
from pos_erp.services.inventory_costing_service import InventoryCostingService
from pos_erp.services.accounting_service import AccountingService

MAX_INVOICE_RETRIES = 5

class PurchaseService:
    @staticmethod
    def _generate_invoice_number(session):
        count = session.query(Purchase).count() + 1
        return f"PUR-{datetime.now().strftime('%Y%m%d')}-{count:04d}"

    @staticmethod
    def _build_purchase(session, purchase_data, items_data, user_id, invoice_number):
        subtotal = purchase_data.get('subtotal', 0.0)
        discount = purchase_data.get('discount', 0.0)
        tax_amount = purchase_data.get('tax_amount', 0.0)
        total = purchase_data.get('total', 0.0)
        paid_amount = purchase_data.get('paid_amount', total)

        purchase = Purchase(
            invoice_number=invoice_number,
            supplier_id=purchase_data.get('supplier_id'),
            user_id=user_id,
            subtotal=subtotal,
            discount=discount,
            tax_amount=tax_amount,
            total=total,
            paid_amount=paid_amount,
            status='COMPLETED',
            notes=purchase_data.get('notes', '')
        )
        session.add(purchase)
        session.flush()

        for item in items_data:
            product_id = item['product_id']
            qty = item['quantity']
            unit_price = item['unit_price'] # This is unit_cost for purchase
            item_total = (qty * unit_price)

            purchase_item = PurchaseItem(
                purchase_id=purchase.id,
                product_id=product_id,
                quantity=qty,
                unit_price=unit_price,
                total=item_total
            )
            session.add(purchase_item)

            product = session.get(Product, product_id)
            if product:
                InventoryCostingService.process_in(
                    session=session,
                    product_id=product_id,
                    quantity=qty,
                    unit_cost=unit_price,
                    reference=invoice_number,
                    user_id=user_id,
                    notes=f"Purchase Invoice {invoice_number}"
                )

        if purchase.supplier_id and paid_amount < total:
            supplier = session.get(Supplier, purchase.supplier_id)
            if supplier:
                supplier.current_balance += (total - paid_amount)

        # Check Cash Balance before journal posting
        if paid_amount > 0:
            cash_acc_code = '1001' if purchase_data.get('payment_method', 'CASH') == 'CASH' else '1002'
            account = session.query(Account).filter_by(code=cash_acc_code).first()
            if account and account.balance < paid_amount:
                raise ValueError(f"الرصيد غير كافٍ في حساب {account.name}")

        je_lines = []
        # 1. Debit Inventory (Total Cost of goods purchased before tax/discount)
        inventory_value = sum((item['quantity'] * item['unit_price']) for item in items_data)
        if inventory_value > 0:
            je_lines.append({'account_code': '1200', 'debit': inventory_value, 'credit': 0.0})
            
        # 2. Debit Tax Receivable / Tax Expense (Simplifying to use Tax Payable debit)
        if tax_amount > 0:
            je_lines.append({'account_code': '2100', 'debit': tax_amount, 'credit': 0.0})
            
        # 3. Credit Purchase Discounts Received
        if discount > 0:
            je_lines.append({'account_code': '4100', 'debit': 0.0, 'credit': discount})  # Using Other Revenue for Discount Received
            
        # 4. Credit Cash (Paid)
        if paid_amount > 0:
            cash_acc_code = '1001' if purchase_data.get('payment_method', 'CASH') == 'CASH' else '1002'
            je_lines.append({'account_code': cash_acc_code, 'debit': 0.0, 'credit': paid_amount})
            
        # 5. Credit Accounts Payable (Unpaid)
        if paid_amount < total:
            je_lines.append({'account_code': '2000', 'debit': 0.0, 'credit': total - paid_amount})
            
        AccountingService.post_journal_entry(
            session=session,
            date=datetime.utcnow(),
            reference=invoice_number,
            notes=f"Purchase Invoice {invoice_number}",
            user_id=user_id,
            lines_data=je_lines
        )

        session.add(AuditLog(
            user_id=user_id, action='CREATE_PURCHASE',
            details=f"Created purchase invoice {invoice_number} for total {total}"
        ))
        return invoice_number

    @staticmethod
    def create_purchase(purchase_data, items_data, user_id):
        last_error = "تعذر إنشاء رقم فاتورة فريد، حاول مرة أخرى"
        for attempt in range(MAX_INVOICE_RETRIES):
            session = SessionLocal()
            try:
                invoice_number = PurchaseService._generate_invoice_number(session)
                PurchaseService._build_purchase(session, purchase_data, items_data, user_id, invoice_number)
                session.commit()
                return True, invoice_number, "تم إتمام عملية الشراء بنجاح"
            except IntegrityError:
                session.rollback()
                continue
            except ValueError as ve:
                session.rollback()
                return False, "", str(ve)
            except Exception as e:
                session.rollback()
                return False, "", str(e)
            finally:
                session.close()
        return False, "", last_error

    @staticmethod
    def get_all_purchases():
        session = SessionLocal()
        try:
            return session.query(Purchase).order_by(Purchase.created_at.desc()).all()
        finally:
            session.close()
