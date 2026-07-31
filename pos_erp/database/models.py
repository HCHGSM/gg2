# -*- coding: utf-8 -*-
"""
=============================================================================
Project: Ultra-Advanced Enterprise POS & ERP System
File: pos_erp/database/models.py
Description: SQLAlchemy ORM Models for Users, Roles, Permissions, Products,
             Categories, Warehouses, Suppliers, Customers, Sales, SaleItems,
             Purchases, PurchaseItems, InventoryMovements, Expenses, Revenues,
             Accounts, Transactions, AuditLogs, and System Settings.
Author: Senior Enterprise Software Architect
=============================================================================
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Date
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class RolePermission(Base):
    """Junction table linking Roles and Permissions for fine-grained access control."""
    __tablename__ = 'role_permissions'
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)

class Role(Base):
    """System Roles defining user permission groups (e.g. Admin, Cashier, Manager)."""
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # NOTE: no cascade delete here on purpose — deleting a Role must never
    # silently delete the Users assigned to it. Role deletion/reassignment
    # is handled explicitly at the service layer.
    users = relationship('User', back_populates='role')
    permissions = relationship('Permission', secondary='role_permissions', back_populates='roles')

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"

class Permission(Base):
    """Granular system permissions for security and access enforcement."""
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(100), unique=True, nullable=False, index=True)
    module = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    roles = relationship('Role', secondary='role_permissions', back_populates='permissions')

    def __repr__(self):
        return f"<Permission(code='{self.code}')>"

class User(Base):
    """System User accounts with secure password hashing, status, and audit linkage."""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    role = relationship('Role', back_populates='users')
    sales = relationship('Sale', back_populates='user')
    purchases = relationship('Purchase', back_populates='user')
    logs = relationship('AuditLog', back_populates='user')

    def __repr__(self):
        return f"<User(username='{self.username}', full_name='{self.full_name}')>"

class Category(Base):
    """Product Categories for hierarchical catalog organization."""
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    products = relationship('Product', back_populates='category')

    def __repr__(self):
        return f"<Category(name='{self.name}')>"

class Warehouse(Base):
    """Warehouses / Storage locations for inventory management and transfers."""
    __tablename__ = 'warehouses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    location = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    movements = relationship('InventoryMovement', back_populates='warehouse')

    def __repr__(self):
        return f"<Warehouse(name='{self.name}')>"

class Supplier(Base):
    """Suppliers and vendors providing merchandise and raw materials."""
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

    def __repr__(self):
        return f"<Supplier(name='{self.name}')>"

class Customer(Base):
    """Customers/Clients database with loyalty tracking and account balances."""
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

    def __repr__(self):
        return f"<Customer(name='{self.name}', phone='{self.phone}')>"

class Product(Base):
    """Merchandise items with SKU, barcode, pricing, stock levels, and expiry tracking."""
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=True, index=True)
    barcode = Column(String(100), unique=True, nullable=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True, index=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True, index=True)
    purchase_price = Column(Float, nullable=False, default=0.0)
    selling_price = Column(Float, nullable=False, default=0.0)
    wholesale_price = Column(Float, nullable=False, default=0.0)
    quantity = Column(Float, nullable=False, default=0.0)
    min_stock = Column(Float, nullable=False, default=5.0)
    tax_rate = Column(Float, nullable=False, default=0.0)
    unit = Column(String(30), default='Piece')
    expiry_date = Column(Date, nullable=True)
    image_path = Column(String(255), nullable=True)
    track_inventory = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship('Category', back_populates='products')
    supplier = relationship('Supplier', back_populates='products')
    sale_items = relationship('SaleItem', back_populates='product', cascade='all, delete-orphan')
    purchase_items = relationship('PurchaseItem', back_populates='product', cascade='all, delete-orphan')
    inventory_movements = relationship('InventoryMovement', back_populates='product', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Product(name='{self.name}', sku='{self.sku}', qty={self.quantity})>"

class InventoryBatch(Base):
    __tablename__ = 'inventory_batches'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    quantity_initial = Column(Float, nullable=False)
    quantity_remaining = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class InventoryMovement(Base):
    """Audit log for all stock ins, outs, transfers, and physical inventory counts."""
    __tablename__ = 'inventory_movements'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=True, index=True)
    movement_type = Column(String(30), nullable=False) # 'IN', 'OUT', 'TRANSFER', 'ADJUSTMENT'
    quantity = Column(Float, nullable=False)
    unit_cost = Column(Float, default=0.0)
    reference = Column(String(100), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    product = relationship('Product', back_populates='inventory_movements')
    warehouse = relationship('Warehouse', back_populates='movements')

class Sale(Base):
    """POS & Sales invoices header with payment status, taxes, and customer association."""
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
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

    def __repr__(self):
        return f"<Sale(invoice='{self.invoice_number}', total={self.total})>"

class SaleItem(Base):
    """Line items for sales invoices."""
    __tablename__ = 'sale_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = Column(Integer, ForeignKey('sales.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False, default=0.0)
    cost_total = Column(Float, nullable=False, default=0.0)
    discount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    gross_profit = Column(Float, nullable=False, default=0.0)
    gross_margin = Column(Float, nullable=False, default=0.0)
    
    sale = relationship('Sale', back_populates='items')
    product = relationship('Product', back_populates='sale_items')

class Purchase(Base):
    """Purchase orders and supplier invoices header."""
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    subtotal = Column(Float, nullable=False, default=0.0)
    discount = Column(Float, nullable=False, default=0.0)
    tax_amount = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    paid_amount = Column(Float, nullable=False, default=0.0)
    status = Column(String(30), default='COMPLETED') # COMPLETED, CANCELLED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    supplier = relationship('Supplier', back_populates='purchases')
    user = relationship('User', back_populates='purchases')
    items = relationship('PurchaseItem', back_populates='purchase', cascade='all, delete-orphan')

class PurchaseItem(Base):
    """Line items for purchase orders."""
    __tablename__ = 'purchase_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_id = Column(Integer, ForeignKey('purchases.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    purchase = relationship('Purchase', back_populates='items')
    product = relationship('Product', back_populates='purchase_items')

class Expense(Base):
    """Operational expenses and cash outflows."""
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Revenue(Base):
    """Non-sales revenues and cash inflows."""
    __tablename__ = 'revenues'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Account(Base):
    """Financial accounts for double-entry Chart of Accounts."""
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, index=True, nullable=True)
    name = Column(String(100), unique=True, nullable=False)
    account_type = Column(String(30), nullable=False) # 'ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE'
    balance = Column(Float, nullable=False, default=0.0)
    account_number = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

class JournalEntry(Base):
    """Balanced Journal Entries."""
    __tablename__ = 'journal_entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    reference = Column(String(100), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    lines = relationship('JournalEntryLine', back_populates='journal_entry', cascade='all, delete-orphan')

class JournalEntryLine(Base):
    """Lines of a Journal Entry."""
    __tablename__ = 'journal_entry_lines'
    id = Column(Integer, primary_key=True, autoincrement=True)
    journal_entry_id = Column(Integer, ForeignKey('journal_entries.id', ondelete='CASCADE'), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)
    debit = Column(Float, nullable=False, default=0.0)
    credit = Column(Float, nullable=False, default=0.0)
    cost_center_id = Column(Integer, ForeignKey('cost_centers.id'), nullable=True, index=True)
    
    journal_entry = relationship('JournalEntry', back_populates='lines')
    account = relationship('Account')

class AuditLog(Base):
    """System-wide audit trail recording user actions for security compliance."""
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship('User', back_populates='logs')

class Setting(Base,):
    """Global system configuration key-value store."""
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)


class FiscalYear(Base):
    __tablename__ = 'fiscal_years'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_closed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AccountingPeriod(Base):
    __tablename__ = 'accounting_periods'
    id = Column(Integer, primary_key=True, autoincrement=True)
    fiscal_year_id = Column(Integer, ForeignKey('fiscal_years.id'), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_closed = Column(Boolean, default=False)

class CostCenter(Base):
    __tablename__ = 'cost_centers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

class Currency(Base):
    __tablename__ = 'currencies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    symbol = Column(String(10), nullable=False)
    is_base = Column(Boolean, default=False)
    exchange_rate = Column(Float, nullable=False, default=1.0)

class TaxGroup(Base):
    __tablename__ = 'tax_groups'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    rate = Column(Float, nullable=False, default=0.0)
    is_inclusive = Column(Boolean, default=False)

class BankAccount(Base):
    __tablename__ = 'bank_accounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)
    bank_name = Column(String(100), nullable=False)
    account_number = Column(String(100), nullable=False)
    routing_number = Column(String(100), nullable=True)

class Cheque(Base):
    __tablename__ = 'cheques'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False, index=True)
    cheque_number = Column(String(50), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    issue_date = Column(Date, nullable=False)
    clearance_date = Column(Date, nullable=True)
    status = Column(String(30), default='PENDING') # PENDING, CLEARED, BOUNCED, CANCELLED
    reference = Column(String(100), nullable=True)
