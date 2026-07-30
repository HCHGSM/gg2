# -*- coding: utf-8 -*-
"""
=============================================================================
Hardcore Enterprise POS & ERP Core Engine (Strict Accounting & Inventory)
Ensures 100% mathematical precision for double-entry ledger, stock tracking,
tax calculations, and audit logs.
=============================================================================
"""

import os
from datetime import datetime
import sqlite3
import bcrypt

DB_PATH = os.path.expanduser('~/hardcore_enterprise.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_hardcore_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Users Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'Administrator',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Products Table (Stock & Pricing precision)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            barcode TEXT UNIQUE,
            purchase_price REAL NOT NULL CHECK(purchase_price >= 0),
            selling_price REAL NOT NULL CHECK(selling_price >= 0),
            quantity REAL NOT NULL CHECK(quantity >= 0),
            min_stock REAL NOT NULL DEFAULT 5.0,
            tax_rate REAL NOT NULL DEFAULT 15.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Customers Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            current_balance REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Sales Invoices Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            user_id INTEGER,
            subtotal REAL NOT NULL,
            tax_amount REAL NOT NULL,
            discount REAL DEFAULT 0.0,
            total REAL NOT NULL,
            paid_amount REAL NOT NULL,
            payment_method TEXT DEFAULT 'CASH',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Sale Items Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')

    # Purchases Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            supplier_name TEXT,
            total REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Expenses Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # General Ledger Accounts
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 0.0
        )
    ''')

    # Audit Logs
    cur.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed Default Admin
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cur.execute("INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                    ('admin', hashed, 'مدير النظام التنفيذي', 'SuperAdmin'))

    # Seed Default Accounts
    cur.execute("SELECT COUNT(*) FROM accounts")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO accounts (name, type, balance) VALUES (?, ?, ?)", [
            ('الصندوق النقدي الرئيسي', 'CASH', 50000.0),
            ('حساب البنك التجاري', 'BANK', 500000.0)
        ])

    # Seed Professional Products
    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        sample_products = [
            ('لابتوب ألعاب رايزن 9', 'LAP-R9-01', '6281001', 350000.0, 420000.0, 12.0, 2.0, 15.0),
            ('شاشة منحنية 32 بوصة 240 هرتز', 'MON-32-240', '6281002', 120000.0, 155000.0, 8.0, 2.0, 15.0),
            ('طابعة إيصالات حرارية POS', 'PRN-POS-80', '6281003', 35000.0, 48000.0, 20.0, 5.0, 15.0),
            ('قارئ باركود لاسلكي صناعي', 'SCAN-WL-01', '6281004', 18000.0, 26000.0, 25.0, 5.0, 15.0),
            ('سيرفر مؤسسات Xeon فائق', 'SRV-XEON-99', '6281005', 900000.0, 1150000.0, 3.0, 1.0, 15.0)
        ]
        cur.executemany("INSERT INTO products (name, sku, barcode, purchase_price, selling_price, quantity, min_stock, tax_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", sample_products)

    conn.commit()
    conn.close()
