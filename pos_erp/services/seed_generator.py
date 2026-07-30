from datetime import datetime, timedelta
import random
from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Product, Customer, Supplier, Category, Warehouse, Sale, SaleItem

class SeedGenerator:
    """
    مولد بيانات تجريبية ضخمة ومحاكاة عمليات البيع والمخزون للاختبار التجاري.
    """
    @staticmethod
    def generate_bulk_data():
        session = SessionLocal()
        try:
            if session.query(Product).count() > 15:
                return # Already seeded

            # Categories
            categories = ['إلكترونيات وأجهزة', 'مواد غذائية', 'ملابس وأزياء', 'أدوات منزلية', 'عطور ومستحضرات']
            cat_objs = []
            for c_name in categories:
                cat = session.query(Category).filter_by(name=c_name).first()
                if not cat:
                    cat = Category(name=c_name, description=f"تصنيف {c_name} التجاري")
                    session.add(cat)
                    session.flush()
                cat_objs.append(cat)

            # Suppliers
            suppliers = ['شركة التوريدات الكبرى', 'مؤسسة النور التجارية', 'وكالة الأفق للاستيراد']
            sup_objs = []
            for s_name in suppliers:
                sup = session.query(Supplier).filter_by(name=s_name).first()
                if not sup:
                    sup = Supplier(name=s_name, phone='0123456789', email=f'info@{s_name.replace(" ", "")}.com', address='الخرطوم')
                    session.add(sup)
                    session.flush()
                sup_objs.append(sup)

            # Bulk Products
            products_data = [
                ("آيفون 15 برو ماكس", "APP-15-PM", "111222333", 45000.0, 55000.0, 25.0),
                ("لابتوب ماك بوك برو M3", "MAC-M3-01", "111222444", 65000.0, 78000.0, 15.0),
                ("شاشة سمارت 55 بوصة", "SAM-TV-55", "111222555", 18000.0, 23000.0, 10.0),
                ("سماعات أريرا بلوتوث", "AIR-BT-99", "111222666", 2500.0, 3800.0, 50.0),
                ("عبوة أرز بسمتي 5 كيلو", "RICE-5KG-01", "222333111", 6000.0, 7500.0, 100.0),
                ("زيت زتون ممتاز 1 لتر", "OIL-OLIVE-1L", "222333222", 4000.0, 5200.0, 80.0),
                ("بن كولومبي فاخر 250جم", "COFFEE-COL-25", "222333333", 3000.0, 4500.0, 60.0),
                ("عطر شانيل بلو الأصلي", "PERF-CHAN-01", "333444111", 12000.0, 16500.0, 30.0),
            ]

            for name, sku, barcode, p_price, s_price, qty in products_data:
                if not session.query(Product).filter_by(sku=sku).first():
                    prod = Product(
                        name=name,
                        sku=sku,
                        barcode=barcode,
                        category_id=random.choice(cat_objs).id,
                        supplier_id=random.choice(sup_objs).id,
                        purchase_price=p_price,
                        selling_price=s_price,
                        quantity=qty,
                        min_stock=5.0,
                        tax_rate=15.0
                    )
                    session.add(prod)

            session.commit()
            return True, "تم توليد البيانات التجريبية بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
