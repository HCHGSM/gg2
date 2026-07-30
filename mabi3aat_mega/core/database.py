# -*- coding: utf-8 -*-
"""
=============================================================================
Module: mabi3aat_mega/core/database.py
Description: Enterprise Database Engine for Mabi3aat Mega Suite.
             Covers Products, Categories, Shipping Zones, Online Orders,
             POS Sales, Expenses, Revenues, Accounts, and Audit Logs.
=============================================================================
"""

import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Date
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
import bcrypt

DB_PATH = os.path.expanduser('~/mabi3aat_mega.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), default='Administrator')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    products = relationship('Product', back_populates='category')

class ShippingZone(Base):
    __tablename__ = 'shipping_zones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    region_name = Column(String(100), unique=True, nullable=False)
    shipping_cost = Column(Float, nullable=False, default=0.0)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=True)
    barcode = Column(String(100), unique=True, nullable=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    cost_price = Column(Float, nullable=False, default=0.0)
    selling_price = Column(Float, nullable=False, default=0.0)
    quantity = Column(Float, nullable=False, default=0.0)
    min_stock = Column(Float, nullable=False, default=5.0)
    is_pinned = Column(Boolean, default=False) # For quick POS access
    sold_by_weight = Column(Boolean, default=False)
    tax_rate = Column(Float, default=15.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship('Category', back_populates='products')

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    balance = Column(Float, default=0.0)

class OnlineOrder(Base):
    __tablename__ = 'online_orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    buyer_name = Column(String(150), nullable=False)
    buyer_phone = Column(String(50), nullable=False)
    shipping_address = Column(Text, nullable=False)
    zone_id = Column(Integer, ForeignKey('shipping_zones.id'), nullable=True)
    shipping_cost = Column(Float, default=0.0)
    items_total = Column(Float, nullable=False, default=0.0)
    grand_total = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), default='قيد التجهيز') # قيد التجهيز, تم التعبئة, جاري التوصيل, تم التسليم, مكتمل
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    subtotal = Column(Float, nullable=False, default=0.0)
    discount = Column(Float, nullable=False, default=0.0)
    tax_amount = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    paid_amount = Column(Float, nullable=False, default=0.0)
    payment_method = Column(String(30), default='CASH')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_mabi3aat_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if session.query(User).count() == 0:
            hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = User(username='admin', password_hash=hashed, full_name='مدير النظام العام', role='SuperAdmin')
            session.add(admin)

        if session.query(Category).count() == 0:
            c1 = Category(name='إلكترونيات وهواتف')
            c2 = Category(name='مواد غذائية ومشروبات')
            c3 = Category(name='عطور ومستحضرات')
            session.add_all([c1, c2, c3])
            session.flush()

        if session.query(ShippingZone).count() == 0:
            z1 = ShippingZone(region_name='الخرطوم وسط', shipping_cost=2000.0)
            z2 = ShippingZone(region_name='بحري', shipping_cost=2500.0)
            z3 = ShippingZone(region_name='أمدرمان', shipping_cost=3000.0)
            session.add_all([z1, z2, z3])

        if session.query(Product).count() == 0:
            prods = [
                Product(name='آيفون 15 برو ماكس', sku='APP-15PM', barcode='112233', category_id=1, cost_price=120000.0, selling_price=145000.0, quantity=15.0, is_pinned=True),
                Product(name='لابتوب ماك بوك برو M3', sku='MAC-M3', barcode='112244', category_id=1, cost_price=150000.0, selling_price=185000.0, quantity=10.0, is_pinned=True),
                Product(name='عبوة أرز بسمتي فاخر 5ك', sku='RICE-5K', barcode='223311', category_id=2, cost_price=6000.0, selling_price=8500.0, quantity=50.0, is_pinned=True),
                Product(name='زيت زيتون بكر ممتاز 1لتر', sku='OIL-1L', barcode='223322', category_id=2, cost_price=4000.0, selling_price=5800.0, quantity=40.0, is_pinned=True),
                Product(name='عطر شانيل بلو الأصلي', sku='PERF-CH', barcode='334411', category_id=3, cost_price=15000.0, selling_price=22000.0, quantity=20.0, is_pinned=True),
            ]
            session.add_all(prods)

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Mabi3aat DB Init Error: {e}")
    finally:
        session.close()
