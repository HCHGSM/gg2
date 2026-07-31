import os
import sys
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base, Role, User, Account, Warehouse, Setting
import bcrypt


def _default_app_root():
    """Where the app's persistent data/ directory should live."""
    if getattr(sys, 'frozen', False):
        local_app_data = os.environ.get('LOCALAPPDATA')
        if local_app_data:
            return os.path.join(local_app_data, 'SmartPOS_ERP')
        # On Linux/Mac frozen
        return os.path.expanduser('~/.local/share/SmartPOS_ERP')
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# DB location is configurable via POS_ERP_DB_PATH (useful for tests / packaging).
# Default: a data/ directory next to the app (source root, or next to the .exe
# when packaged), NOT the user's home directory or the PyInstaller temp dir.
DEFAULT_DB_PATH = os.path.join(_default_app_root(), 'data', 'pos_erp.db')
DB_PATH = os.environ.get('POS_ERP_DB_PATH', DEFAULT_DB_PATH)
if DB_PATH != ':memory:':
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    engine = create_engine(
        DATABASE_URL, 
        echo=False, 
        future=True, 
        connect_args={'check_same_thread': False, 'timeout': 15}
    )
else:
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        DATABASE_URL, 
        echo=False, 
        future=True, 
        connect_args={'check_same_thread': False}
    )

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if DB_PATH != ':memory:':
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA cache_size=-64000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

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
            # Default password can be overridden via POS_ERP_ADMIN_PASSWORD (env var)
            # instead of being fixed in source. Still defaults to 'admin123' for a
            # frictionless first run, but every fresh install should change it
            # immediately after first login (enforced by a UI prompt — see users_view).
            default_admin_pwd = os.environ.get('POS_ERP_ADMIN_PASSWORD', 'admin123')
            hashed_pwd = bcrypt.hashpw(default_admin_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
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
            accounts_to_add = [
                Account(code='1001', name='Main Cash Drawer', account_type='ASSET', balance=5000.0),
                Account(code='1002', name='Company Bank Account', account_type='ASSET', balance=50000.0),
                Account(code='1100', name='Accounts Receivable', account_type='ASSET', balance=0.0),
                Account(code='1200', name='Inventory', account_type='ASSET', balance=0.0),
                Account(code='2000', name='Accounts Payable', account_type='LIABILITY', balance=0.0),
                Account(code='2100', name='Tax Payable', account_type='LIABILITY', balance=0.0),
                Account(code='3000', name='Owner Equity', account_type='EQUITY', balance=0.0),
                Account(code='3100', name='Retained Earnings', account_type='EQUITY', balance=0.0),
                Account(code='4000', name='Sales Revenue', account_type='REVENUE', balance=0.0),
                Account(code='4100', name='Other Revenue', account_type='REVENUE', balance=0.0),
                Account(code='5000', name='Cost of Goods Sold', account_type='EXPENSE', balance=0.0),
                Account(code='5100', name='Operating Expenses', account_type='EXPENSE', balance=0.0),
                Account(code='5200', name='Discounts Given', account_type='EXPENSE', balance=0.0),
            ]
            session.add_all(accounts_to_add)
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
