from datetime import datetime
from sqlalchemy.exc import IntegrityError
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Sale, SaleItem, Product, Customer, Account, Transaction, InventoryMovement, AuditLog

MAX_INVOICE_RETRIES = 5


class SalesService:
    @staticmethod
    def _generate_invoice_number(session):
        # Not perfectly atomic under heavy concurrency (two terminals can still
        # compute the same next number in the same instant); the retry loop in
        # create_sale() below handles that by regenerating and re-committing on
        # a unique-constraint collision, rather than letting the sale fail.
        count = session.query(Sale).count() + 1
        return f"INV-{datetime.now().strftime('%Y%m%d')}-{count:04d}"

    @staticmethod
    def _build_sale(session, sale_data, items_data, user_id, invoice_number):
        """Builds and stages one sale + its items/side effects. Raises on error;
        does not commit or close the session - the caller owns the transaction
        so it can retry on invoice-number collisions."""
        subtotal = sale_data.get('subtotal', 0.0)
        discount = sale_data.get('discount', 0.0)
        tax_amount = sale_data.get('tax_amount', 0.0)
        total = sale_data.get('total', 0.0)
        paid_amount = sale_data.get('paid_amount', total)
        change_amount = max(0.0, paid_amount - total)

        sale = Sale(
            invoice_number=invoice_number,
            customer_id=sale_data.get('customer_id'),
            user_id=user_id,
            subtotal=subtotal,
            discount=discount,
            tax_amount=tax_amount,
            total=total,
            paid_amount=paid_amount,
            change_amount=change_amount,
            payment_method=sale_data.get('payment_method', 'CASH'),
            status='COMPLETED',
            notes=sale_data.get('notes', '')
        )
        session.add(sale)
        session.flush()  # get sale.id

        for item in items_data:
            product_id = item['product_id']
            qty = item['quantity']
            unit_price = item['unit_price']
            item_disc = item.get('discount', 0.0)
            item_tax = item.get('tax', 0.0)
            item_total = (qty * unit_price) - item_disc + item_tax

            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product_id,
                quantity=qty,
                unit_price=unit_price,
                discount=item_disc,
                tax=item_tax,
                total=item_total
            )
            session.add(sale_item)

            product = session.query(Product).get(product_id)
            if product:
                if product.quantity < qty:
                    raise ValueError(f"الكمية غير متوفرة في المخزون للمنتج: {product.name}")
                product.quantity -= qty

                movement = InventoryMovement(
                    product_id=product_id,
                    movement_type='OUT',
                    quantity=qty,
                    unit_cost=product.purchase_price,
                    reference=invoice_number,
                    user_id=user_id,
                    notes=f"Sale Invoice {invoice_number}"
                )
                session.add(movement)

        if sale.customer_id and paid_amount < total:
            customer = session.query(Customer).get(sale.customer_id)
            if customer:
                customer.current_balance += (total - paid_amount)

        account_type = 'CASH' if sale.payment_method == 'CASH' else 'BANK'
        account = session.query(Account).filter_by(account_type=account_type).first()
        if account and paid_amount > 0:
            account.balance += paid_amount
            tx = Transaction(
                account_id=account.id,
                transaction_type='DEPOSIT',
                amount=paid_amount,
                reference=invoice_number,
                user_id=user_id,
                notes=f"Payment for Sale {invoice_number}"
            )
            session.add(tx)

        session.add(AuditLog(
            user_id=user_id, action='CREATE_SALE',
            details=f"Created invoice {invoice_number} for total {total}"
        ))
        return invoice_number

    @staticmethod
    def create_sale(sale_data, items_data, user_id):
        last_error = "تعذر إنشاء رقم فاتورة فريد، حاول مرة أخرى"
        for attempt in range(MAX_INVOICE_RETRIES):
            session = SessionLocal()
            try:
                invoice_number = SalesService._generate_invoice_number(session)
                SalesService._build_sale(session, sale_data, items_data, user_id, invoice_number)
                session.commit()
                return True, invoice_number, "تم إتمام عملية البيع بنجاح"
            except IntegrityError:
                session.rollback()
                continue
            except Exception as e:
                session.rollback()
                return False, "", str(e)
            finally:
                session.close()
        return False, "", last_error

    @staticmethod
    def get_all_sales():
        session = SessionLocal()
        try:
            return session.query(Sale).order_by(Sale.created_at.desc()).all()
        finally:
            session.close()
