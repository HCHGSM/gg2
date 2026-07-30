import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base, Role, Permission, User, Account, Warehouse, Setting
import bcrypt

DB_PATH = os.path.expanduser('~/pos_erp.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False, future=True)
session_factory = sessionmaker(bind=engine, expire_on_commit=False)
SessionLocal = scoped_session(session_factory)

def init_db():
    Base.metadata.create_all(bind=engine)
    seed_initial_data()

def seed_initial_data():
    session = SessionLocal()
    try:
        # Check if roles exist
        if session.query(Role).count() == 0:
            admin_role = Role(name='Admin', description='Administrator with full access')
            cashier_role = Role(name='Cashier', description='Cashier with POS access')
            manager_role = Role(name='Manager', description='Inventory & Sales Manager')
            session.add_all([admin_role, cashier_role, manager_role])
            session.commit()

        # Check if default admin user exists
        if session.query(User).count() == 0:
            admin_role = session.query(Role).filter_by(name='Admin').first()
            hashed_pwd = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin_user = User(
                username='admin',
                email='admin@pos.com',
                password_hash=hashed_pwd,
                full_name='System Administrator',
                role_id=admin_role.id,
                is_active=True
            )
            session.add(admin_user)
            session.commit()

        # Check default accounts
        if session.query(Account).count() == 0:
            main_cash = Account(name='Main Cash Drawer', account_type='CASH', balance=5000.0, account_number='CASH-001')
            main_bank = Account(name='Company Bank Account', account_type='BANK', balance=50000.0, account_number='BANK-999')
            session.add_all([main_cash, main_bank])
            session.commit()

        # Check default warehouse
        if session.query(Warehouse).count() == 0:
            main_wh = Warehouse(name='Main Warehouse', location='Headquarters', description='Primary storage warehouse')
            session.add_all([main_wh])
            session.commit()

        # Check default settings
        default_settings = {
            'company_name': 'شركة الأفق الذكي للتجارة والأنظمة',
            'company_phone': '+249912345678',
            'company_email': 'info@smartpos.sd',
            'company_address': 'الخرطوم، السودان',
            'tax_rate': '15.0',
            'currency': 'ج.س',
            'language': 'ar',
            'theme': 'light',
            'receipt_footer': 'شكراً لتعاملكم معنا - نسعد بتزيين خدمتكم'
        }
        for k, v in default_settings.items():
            if not session.query(Setting).filter_by(key=k).first():
                session.add(Setting(key=k, value=v))
        session.commit()

        # Seed bulk realistic products & categories for commercial use
        from pos_erp.services.seed_generator import SeedGenerator
        SeedGenerator.generate_bulk_data()

    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()
