# -*- coding: utf-8 -*-
"""
=============================================================================
Enterprise ERP & POS Core Engine - Massive Scale Architecture
Provides multi-warehouse inventory valuation, double-entry general ledger accounting,
POS touch terminal controller, CRM, HR, Manufacturing (BOM), and Purchasing.
=============================================================================
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session

DB_PATH = os.path.expanduser('~/enterprise_erp.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
Base = declarative_base()

class EnterpriseUser(Base):
    __tablename__ = 'ent_users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(60), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(String(50), default='Administrator')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EnterpriseProduct(Base):
    __tablename__ = 'ent_products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=True, index=True)
    barcode = Column(String(100), unique=True, nullable=True, index=True)
    category = Column(String(100), default='General')
    cost_price = Column(Float, nullable=False, default=0.0)
    sale_price = Column(Float, nullable=False, default=0.0)
    stock_qty = Column(Float, nullable=False, default=0.0)
    min_stock = Column(Float, nullable=False, default=5.0)
    tax_rate = Column(Float, nullable=False, default=15.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class EnterpriseAccount(Base):
    __tablename__ = 'ent_accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    account_type = Column(String(50), nullable=False) # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    balance = Column(Float, default=0.0)

class EnterpriseJournalEntry(Base):
    __tablename__  = 'ent_journal_entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_number = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class EnterpriseCustomer(Base):
    __tablename__ = 'ent_customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    balance = Column(Float, default=0.0)

class EnterpriseInvoice(Base):
    __tablename__ = 'ent_invoices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('ent_customers.id'), nullable=True)
    subtotal = Column(Float, nullable=False, default=0.0)
    tax = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    paid = Column(Float, nullable=False, default=0.0)
    payment_method = Column(String(30), default='CASH')
    status = Column(String(30), default='PAID')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

def init_enterprise_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if session.query(EnterpriseUser).count() == 0:
            import bcrypt
            pwd = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = EnterpriseUser(username='admin', password_hash=pwd, full_name='Enterprise Super Admin', role='SuperAdmin')
            session.add(admin)

        if session.query(EnterpriseAccount).count() == 0:
            session.add(EnterpriseAccount(account_code='1010', name='Main Cash Drawer', account_type='ASSET', balance=100000.0))
            session.add(EnterpriseAccount(account_code='1020', name='Corporate Bank Account', account_type='ASSET', balance=500000.0))
            session.add(EnterpriseAccount(account_code='4010', name='Sales Revenue', account_type='REVENUE', balance=0.0))

        if session.query(EnterpriseProduct).count() == 0:
            sample_prods = [
                EnterpriseProduct(name='Enterprise Server Blade X9', sku='SRV-X9', barcode='99887766', cost_price=120000.0, sale_price=160000.0, stock_qty=10.0),
                EnterpriseProduct(name='Enterprise POS Terminal Touch', sku='POS-T1', barcode='99887755', cost_price=8000.0, sale_price=12500.0, stock_qty=35.0),
                EnterpriseProduct(name='Thermal Receipt Printer 80mm', sku='PRN-80', barcode='99887744', cost_price=1500.0, sale_price=2400.0, stock_qty=50.0),
            ]
            session.add_all(sample_prods)

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Enterprise DB Init Error: {e}")
    finally:
        session.close()
