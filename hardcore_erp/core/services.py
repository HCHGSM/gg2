# -*- coding: utf-8 -*-
"""
=============================================================================
Hardcore Enterprise POS & ERP Services
Strict transactional integrity, stock control, and financial calculations.
=============================================================================
"""

import bcrypt
from datetime import datetime
from hardcore_erp.core.database import get_db_connection

class HardcoreAuth:
    @staticmethod
    def authenticate(username, password):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()
        
        if not user:
            return None, "اسم المستخدم غير موجود"
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return user, "تم تسجيل الدخول بنجاح"
        return None, "كلمة المرور غير صحيحة"

class HardcoreInventory:
    @staticmethod
    def get_products():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products")
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def add_product(name, sku, barcode, cost, price, qty, min_s, tax):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO products (name, sku, barcode, purchase_price, selling_price, quantity, min_stock, tax_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, sku, barcode, cost, price, qty, min_s, tax))
            conn.commit()
            return True, "تم إضافة المنتج بنجاح والمخزون محدث"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

class HardcoreSales:
    @staticmethod
    def create_sale(user_id, cart_items, payment_method='CASH'):
        """
        Hardcore transactional sale creation:
        - Validates real-time stock
        - Computes precise subtotal, tax (15%), and grand total
        - Deducts stock immediately
        - Updates cash/bank account balance
        - Records immutable sale & item logs
        """
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            conn.execute("BEGIN TRANSACTION")

            subtotal = 0.0
            tax_amount = 0.0

            # Pre-validate stock and compute totals
            for item in cart_items:
                cur.execute("SELECT quantity, selling_price, name FROM products WHERE id = ?", (item['id'],))
                prod = cur.fetchone()
                if not prod:
                    raise ValueError(f"المنتج بمعرف {item['id']} غير موجود!")
                
                if prod['quantity'] < item['qty']:
                    raise ValueError(f"الكمية المطلوبة للمنتج '{prod['name']}' غير متوفرة! المتاح: {prod['quantity']}")
                
                item_total = prod['selling_price'] * item['qty']
                subtotal += item_total
                tax_amount += item_total * 0.15 # 15% Standard VAT

            grand_total = subtotal + tax_amount
            invoice_no = f"HC-INV-{int(datetime.now().timestamp())}"

            # Insert Sale Header
            cur.execute("""
                INSERT INTO sales (invoice_number, user_id, subtotal, tax_amount, total, paid_amount, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (invoice_no, user_id, subtotal, tax_amount, grand_total, grand_total, payment_method))
            sale_id = cur.lastrowid

            # Insert Items & Deduct Stock
            for item in cart_items:
                cur.execute("SELECT selling_price FROM products WHERE id = ?", (item['id'],))
                price = cur.fetchone()['selling_price']
                item_tot = price * item['qty']

                cur.execute("""
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total)
                    VALUES (?, ?, ?, ?, ?)
                """, (sale_id, item['id'], item['qty'], price, item_tot))

                cur.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (item['qty'], item['id']))

            # Update Cash/Bank Account Balance
            acc_name = 'الصندوق النقدي الرئيسي' if payment_method == 'CASH' else 'حساب البنك التجاري'
            cur.execute("UPDATE accounts SET balance = balance + ? WHERE name = ?", (grand_total, acc_name))

            # Audit Log
            cur.execute("INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
                        (user_id, 'CREATE_SALE', f"Generated invoice {invoice_no} for total {grand_total:,.2f}"))

            conn.commit()
            return True, invoice_no, f"تم إتمام الفاتورة بنجاح. رقم الفاتورة: {invoice_no}"
        except Exception as e:
            conn.rollback()
            return False, "", str(e)
        finally:
            conn.close()

class HardcoreAnalytics:
    @staticmethod
    def get_dashboard_metrics():
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT SUM(total), SUM(tax_amount) FROM sales")
        sales_row = cur.fetchone()
        total_sales = sales_row[0] or 0.0
        total_tax = sales_row[1] or 0.0

        cur.execute("SELECT SUM(amount) FROM expenses")
        total_expenses = cur.fetchone()[0] or 0.0

        cur.execute("SELECT COUNT(*) FROM products")
        products_count = cur.fetchone()[0] or 0

        cur.execute("SELECT COUNT(*) FROM sales")
        invoices_count = cur.fetchone()[0] or 0

        cur.execute("SELECT SUM(balance) FROM accounts")
        total_cash = cur.fetchone()[0] or 0.0

        conn.close()
        
        net_profit = total_sales - total_expenses - (total_sales * 0.65) # Approx cost basis + expenses

        return {
            'total_sales': total_sales,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'products_count': products_count,
            'invoices_count': invoices_count,
            'total_cash': total_cash
        }
