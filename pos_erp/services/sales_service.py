from sqlalchemy.orm import joinedload
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Sale, SaleItem, Product, Customer, AuditLog
from pos_erp.services.inventory_costing_service import InventoryCostingService
from pos_erp.services.accounting_service import AccountingService

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
            
            product = session.get(Product, product_id)
            if not product:
                raise ValueError(f"Product not found: {product_id}")
            
            qty = item['quantity']
            unit_price = item['unit_price']
            if product.quantity < qty:
                raise ValueError(f"الكمية غير متوفرة في المخزون للمنتج: {product.name}")

            item_cost_total, unit_cost_calculated = InventoryCostingService.process_out(
                session=session,
                product_id=product_id,
                quantity=qty,
                reference=invoice_number,
                user_id=user_id,
                notes=f"Sale Invoice {invoice_number}"
            )

            item_disc = item.get('discount', 0.0)
            item_tax = item.get('tax', 0.0)
            item_total = (qty * unit_price) - item_disc + item_tax
            item_gross_profit = (qty * unit_price) - item_disc - item_cost_total
            item_gross_margin = (item_gross_profit / ((qty * unit_price) - item_disc)) * 100 if ((qty * unit_price) - item_disc) > 0 else 0.0

            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product_id,
                quantity=qty,
                unit_price=unit_price,
                unit_cost=unit_cost_calculated,
                cost_total=item_cost_total,
                discount=item_disc,
                tax=item_tax,
                total=item_total,
                gross_profit=item_gross_profit,
                gross_margin=item_gross_margin
            )
            session.add(sale_item)

        if sale.customer_id and paid_amount < total:
            customer = session.get(Customer, sale.customer_id)
            if customer:
                customer.current_balance += (total - paid_amount)

        # Generate Double Entry Journal
        je_lines = []
        cogs_amount = 0.0
        
        for item in sale.items:
            cogs_amount += item.quantity * item.unit_cost

        # 1. Debit Cash/Bank (Paid)
        if paid_amount > 0:
            cash_acc_code = '1001' if sale.payment_method == 'CASH' else '1002'
            je_lines.append({'account_code': cash_acc_code, 'debit': paid_amount, 'credit': 0.0})
            
        # 2. Debit Accounts Receivable (Unpaid)
        if paid_amount < total:
            je_lines.append({'account_code': '1100', 'debit': total - paid_amount, 'credit': 0.0})
            
        # 3. Credit Sales Revenue (Subtotal)
        if subtotal > 0:
            je_lines.append({'account_code': '4000', 'debit': 0.0, 'credit': subtotal})
            
        # 4. Debit Discounts Given
        if discount > 0:
            je_lines.append({'account_code': '5200', 'debit': discount, 'credit': 0.0})
            
        # 5. Credit Tax Payable
        if tax_amount > 0:
            je_lines.append({'account_code': '2100', 'debit': 0.0, 'credit': tax_amount})
            
        # COGS Entries
        if cogs_amount > 0:
            je_lines.append({'account_code': '5000', 'debit': cogs_amount, 'credit': 0.0})  # Debit COGS
            je_lines.append({'account_code': '1200', 'debit': 0.0, 'credit': cogs_amount})  # Credit Inventory
            
        AccountingService.post_journal_entry(
            session=session,
            date=datetime.utcnow(),
            reference=invoice_number,
            notes=f"Sale Invoice {invoice_number}",
            user_id=user_id,
            lines_data=je_lines
        )

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
    def return_sale(sale_id, user_id):
        session = SessionLocal()
        try:
            sale = session.query(Sale).options(joinedload(Sale.items)).filter_by(id=sale_id).first()
            if not sale:
                return False, "الفاتورة غير موجودة"
            if sale.status == 'RETURNED':
                return False, "الفاتورة مسترجعة بالفعل"
            
            # Reverse Inventory and COGS
            for item in sale.items:
                product = session.get(Product, item.product_id)
                if product:
                    # Put back at exactly the cost it went out to avoid costing skew
                    InventoryCostingService.process_in(
                        session=session,
                        product_id=product.id,
                        quantity=item.quantity,
                        unit_cost=item.unit_cost,
                        reference=f"RET-{sale.invoice_number}",
                        user_id=user_id,
                        notes=f"Return Sale Invoice {sale.invoice_number}"
                    )
            
            # Reverse Customer Balance
            if sale.customer_id and sale.paid_amount < sale.total:
                customer = session.get(Customer, sale.customer_id)
                if customer:
                    customer.current_balance -= (sale.total - sale.paid_amount)
            
            # Reverse Journal Entry
            je_lines = []
            cogs_amount = sum(item.quantity * item.unit_cost for item in sale.items)

            if sale.paid_amount > 0:
                cash_acc_code = '1001' if sale.payment_method == 'CASH' else '1002'
                je_lines.append({'account_code': cash_acc_code, 'debit': 0.0, 'credit': sale.paid_amount})
                
            if sale.paid_amount < sale.total:
                je_lines.append({'account_code': '1100', 'debit': 0.0, 'credit': sale.total - sale.paid_amount})
                
            if sale.subtotal > 0:
                je_lines.append({'account_code': '4000', 'debit': sale.subtotal, 'credit': 0.0})
                
            if sale.discount > 0:
                je_lines.append({'account_code': '5200', 'debit': 0.0, 'credit': sale.discount})
                
            if sale.tax_amount > 0:
                je_lines.append({'account_code': '2100', 'debit': sale.tax_amount, 'credit': 0.0})
                
            if cogs_amount > 0:
                je_lines.append({'account_code': '5000', 'debit': 0.0, 'credit': cogs_amount})
                je_lines.append({'account_code': '1200', 'debit': cogs_amount, 'credit': 0.0})
                
            AccountingService.post_journal_entry(
                session=session,
                date=datetime.utcnow(),
                reference=f"RET-{sale.invoice_number}",
                notes=f"Return Sale Invoice {sale.invoice_number}",
                user_id=user_id,
                lines_data=je_lines
            )
            
            sale.status = 'RETURNED'
            
            session.add(AuditLog(
                user_id=user_id, action='RETURN_SALE',
                details=f"Returned invoice {sale.invoice_number}"
            ))
            session.commit()
            return True, "تم استرجاع الفاتورة بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def get_all_sales():
        session = SessionLocal()
        try:
            return session.query(Sale).order_by(Sale.created_at.desc()).all()
        finally:
            session.close()
