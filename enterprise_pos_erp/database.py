# -*- coding: utf-8 -*-
"""
=============================================================================
Module: enterprise_pos_erp/database.py
Description: Enterprise Database Schema using SQLAlchemy ORM.
             Includes 15+ relational tables with strict constraints, indexes,
             foreign keys, and automated seeding of commercial data.
=============================================================================
"""

import os
from datetime import datetime, date
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Date, Index
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
import bcrypt

DB_PATH = os.path.expanduser('~/enterprise_pos_erp.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
Base = declarative_base()

class RolePermission(Base):
    __tablename__ = 'role_permissions'
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    users = relationship('User', back_populates='role')
    permissions = relationship('Permission', secondary='role_permissions', back_populates='roles')

class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(100), unique=True, nullable=False, index=True)
    module = Column(String(50), nullable=True)
    
    roles = relationship('Role', secondary='role_permissions', back_populates='permissions')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    role = relationship('Role', back_populates='users')
    sales = relationship('Sale', back_populates='user')
    purchases = relationship('Purchase', back_populates='user')
    logs = relationship('AuditLog', back_populates='user')

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship('Product', back_populates='category')

class Warehouse(Base):
    __tablename__ = 'warehouses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    movements = relationship('InventoryMovement', back_populates='warehouse')

class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, index=True)
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    opening_balance = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    tax_number = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship('Product', back_populates='supplier')
    purchases = relationship('Purchase', back_populates='supplier')

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, index=True)
    phone = Column(String(50), nullable=True, index=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    opening_balance = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    loyalty_points = Column(Integer, default=0)
    tax_number = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sales = relationship('Sale', back_populates='customer')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=True, index=True)
    barcode = Column(String(100), unique=True, nullable=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    purchase_price = Column(Float, nullable=False, default=0.0)
    selling_price = Column(Float, nullable=False, default=0.0)
    wholesale_price = Column(Float, nullable=False, default=0.0)
    quantity = Column(Float, nullable=False, default=0.0)
    min_stock = Column(Float, nullable=False, default=5.0)
    tax_rate = Column(Float, nullable=False, default=15.0)
    unit = Column(String(30), default='Piece')
    expiry_date = Column(Date, nullable=True)
    image_path = Column(String(255), nullable=True)
    track_inventory = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    category = relationship('Category', back_populates='products')
    supplier = relationship('Supplier', back_populates='products')
    sale_items = relationship('SaleItem', back_populates='product')
    purchase_items = relationship('PurchaseItem', back_populates='product')
    inventory_movements = relationship('InventoryMovement', back_populates='product')

class InventoryMovement(Base):
    __tablename__ = 'inventory_movements'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=True)
    movement_type = Column(String(30), nullable=False) # 'IN', 'OUT', 'TRANSFER', 'ADJUSTMENT'
    quantity = Column(Float, nullable=False)
    unit_cost = Column(Float, default=0.0)
    reference = Column(String(100), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    product = relationship('Product', back_populates='inventory_movements')
    warehouse = relationship('Warehouse', back_populates='movements')

class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subtotal = Column(Float, nullable=False, default=0.0)
    discount = Column(Float, nullable=False, default=0.0)
    tax_amount = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    paid_amount = Column(Float, nullable=False, default=0.0)
    change_amount = Column(Float, nullable=False, default=0.0)
    payment_method = Column(String(30), default='CASH') # CASH, BANK, MIXED, CREDIT
    status = Column(String(30), default='COMPLETED') # COMPLETED, CANCELLED, RETURNED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    customer = relationship('Customer', back_populates='sales')
    user = relationship('User', back_populates='sales')
    items = relationship('SaleItem', back_populates='sale', cascade='all, delete-orphan')

class SaleItem(Base):
    __tablename__ = 'sale_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = Column(Integer, ForeignKey('sales.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    
    sale = relationship('Sale', back_populates='items')
    product = relationship('Product', back_populates='sale_items')

class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subtotal = Column(Float, nullable=False, default=0.0)
    discount = Column(Float, nullable=False, default=0.0)
    tax_amount = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    paid_amount = Column(Float, nullable=False, default=0.0)
    status = Column(String(30), default='COMPLETED')
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    supplier = relationship('Supplier', back_populates='purchases')
    user = relationship('User', back_populates='purchases')
    items = relationship('PurchaseItem', back_populates='purchase', cascade='all, delete-orphan')

class PurchaseItem(Base):
    __tablename__ = 'purchase_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_id = Column(Integer, ForeignKey('purchases.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    purchase = relationship('Purchase', back_populates='items')
    product = relationship('Product', back_populates='purchase_items')

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    notes = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Revenue(Base):
    __tablename__ = 'revenues'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    notes = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    account_type = Column(String(30), nullable=False) # 'CASH', 'BANK'
    balance = Column(Float, nullable=False, default=0.0)
    account_number = Column(String(100), nullable=True)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    transaction_type = Column(String(30), nullable=False) # 'DEPOSIT', 'WITHDRAWAL', 'TRANSFER'
    amount = Column(Float, nullable=False)
    reference = Column(String(100), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship('User', back_populates='logs')

class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        # Seed Roles
        if session.query(Role).count() == 0:
            admin_role = Role(name='Administrator', description='Full system administrator')
            cashier_role = Role(name='Cashier', description='POS terminal operator')
            session.add_all([admin_role, cashier_role])
            session.commit()

        # Seed Admin User
        if session.query(User).count() == 0:
            admin_role = session.query(Role).filter_by(name='Administrator').first()
            hashed_pwd = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = User(
                username='admin',
                email='admin@enterprise.sd',
                password_hash=hashed_pwd,
                full_name='مدير النظام العام',
                role_id=admin_role.id,
                is_active=True
            )
            session.add(admin)
            session.commit()

        # Seed Accounts
        if session.query(Account).count() == 0:
            cash = Account(name='الصندوق النقدي الرئيسي', account_type='CASH', balance=25000.0, account_number='ACC-CASH-01')
            bank = Account(name='حساب الشركة البنكي', account_type='BANK', balance=150000.0, account_number='ACC-BANK-99')
            session.add_all([cash, bank])
            session.commit()

        # Seed Warehouse
        if session.query(Warehouse).count() == 0:
            wh = Warehouse(name='المستودع الرئيسي', location='الفرع الرئيسي - الخرطوم', is_default=True)
            session.add(wh)
            session.commit()

        # Seed Categories
        if session.query(Category).count() == 0:
            cats = [
                Category(name='إلكترونيات وأجهزة ذكية'),
                Category(name='مواد غذائية أساسية'),
                Category(name='عطور ومستحضرات تجميل'),
                Category(name='أدوات مكتبية ومكتبيات')
            ]
            session.add_all(cats)
            session.commit()

        # Seed Suppliers
        if session.query(Supplier).count() == 0:
            sup = Supplier(name='شركة التوريدات العالمية المحدودة', phone='+249912345678', address='الخرطوم')
            session.add(sup)
            session.commit()

        # Seed Products
        if session.query(Product).count() == 0:
            cat = session.query(Category).first()
            sup = session.query(Supplier).first()
            prods = [
                Product(name='لابتوب ديل XPS 15 احترافي', sku='DELL-XPS-15', barcode='1122334455', category_id=cat.id if cat else None, supplier_id=sup.id if sup else None, purchase_price=85000.0, selling_price=105000.0, quantity=15.0, min_stock=3.0, tax_rate=15.0),
                Product(name='آيفون 15 برو ماكس 256 جيجا', sku='APPLE-15PM', barcode='2233445566', category_id=cat.id if cat else None, supplier_id=sup.id if sup else None, purchase_price=120000.0, selling_price=145000.0, quantity=10.0, min_stock=2.0, tax_rate=15.0),
                Product(name='طابعة إيصالات حرارية POS 80مم', sku='POS-PRN-80', barcode='3344556677', category_id=cat.id if cat else None, supplier_id=sup.id if sup else None, purchase_price=18000.0, selling_price=24000.0, quantity=25.0, min_stock=5.0, tax_rate=15.0),
                Product(name='قارئ باركود لاسلكي متطور', sku='BC-SCANNER', barcode='4455667788', category_id=cat.id if cat else None, supplier_id=sup.id if sup else None, purchase_price=8000.0, selling_price=12000.0, quantity=40.0, min_stock=5.0, tax_rate=15.0),
                Product(name='عبوة أرز بسمتي فاخر 5 كيلو', sku='RICE-5KG', barcode='5566778899', category_id=cat.id if cat else None, supplier_id=sup.id if sup else None, purchase_price=6000.0, selling_price=8500.0, quantity=100.0, min_stock=10.0, tax_rate=15.0),
            ]
            session.add_all(prods)
            session.commit()

        # Seed Settings
        if session.query(Setting).count() == 0:
            settings = [
                Setting(key='company_name', value='شركة الأفق الذكي لأنظمة الأعمال والتقنية'),
                Setting(key='company_phone', value='+249912345678'),
                Setting(key='tax_rate', value='15.0'),
                Setting(key='currency', value='ج.س')
            ]
            session.add_all(settings)
            session.commit()

    except Exception as e:
        session.rollback()
        print(f"Database Seeding Error: {e}")
    finally:
        session.close()
