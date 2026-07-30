# -*- coding: utf-8 -*-
"""
=============================================================================
Module: enterprise_pos_erp/services.py
Description: Comprehensive business logic and transaction controllers for
             Authentication, POS Sales, Inventory movements, and Finance.
=============================================================================
"""

import bcrypt
from datetime import datetime
from enterprise_pos_erp.database import SessionLocal, User, Product, Sale, SaleItem, InventoryMovement, Customer, Supplier, Expense, Account, Transaction, AuditLog

class AuthService:
    @staticmethod
    def authenticate(username, password):
        session = SessionLocal()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                return None, "اسم المستخدم غير موجود"
            if not user.is_active:
                return None, "الحساب معطل، يرجى مراجعة الإدارة"
            
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                user.last_login = datetime.utcnow()
                session.commit()
                log = AuditLog(user_id=user.id, action='LOGIN', details=f"User {username} logged in successfully.")
                session.add(log)
                session.commit()
                return user, "تم تسجيل الدخول بنجاح"
            else:
                return None, "كلمة المرور غير صحيحة"
        except Exception as e:
            return None, f"خطأ في المصادقة: {str(e)}"
        finally:
            session.close()

class ProductService:
    @staticmethod
    def get_all_products():
        session = SessionLocal()
        try:
            return session.query(Product).all()
        finally:
            session.close()

    @staticmethod
    def add_product(data, user_id=None):
        session = SessionLocal()
        try:
            product = Product(**data)
            session.add(product)
            session.commit()
            
            if product.quantity > 0:
                movement = InventoryMovement(
                    product_id=product.id,
                    movement_type='IN',
                    quantity=product.quantity,
                    unit_cost=product.purchase_price,
                    reference='Initial Stock',
                    user_id=user_id,
                    notes='Opening stock on creation'
                )
                session.add(movement)
                session.commit()

            if user_id:
                session.add(AuditLog(user_id=user_id, action='ADD_PRODUCT', details=f"Added product: {product.name}"))
                session.commit()
            return True, "تم إضافة المنتج بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

class SalesService:
    @staticmethod
    def create_sale(sale_data, items_data, user_id):
        session = SessionLocal()
        try:
            count = session.query(Sale).count() + 1
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
            
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
            session.flush()

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

                product = session.get(Product, product_id)
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

            # Update Cash Account
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

            session.add(AuditLog(user_id=user_id, action='CREATE_SALE', details=f"Created invoice {invoice_number} for total {total}"))
            session.commit()
            return True, invoice_number, "تم إتمام عملية البيع بنجاح"
        except Exception as e:
            session.rollback()
            return False, "", str(e)
        finally:
            session.close()

    @staticmethod
    def get_all_sales():
        session = SessionLocal()
        try:
            return session.query(Sale).order_by(Sale.created_at.desc()).all()
        finally:
            session.close()
