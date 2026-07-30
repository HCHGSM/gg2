from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Product, Category, InventoryMovement, AuditLog

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
            
            # Record initial inventory movement if quantity > 0
            if product.quantity > 0:
                movement = InventoryMovement(
                    product_id=product.id,
                    movement_type='IN',
                    quantity=product.quantity,
                    unit_cost=product.purchase_price,
                    reference='Initial Stock',
                    user_id=user_id,
                    notes='Opening stock on product creation'
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

    @staticmethod
    def update_product(product_id, data, user_id=None):
        session = SessionLocal()
        try:
            product = session.query(Product).get(product_id)
            if not product:
                return False, "المنتج غير موجود"
            for key, value in data.items():
                setattr(product, key, value)
            session.commit()
            if user_id:
                session.add(AuditLog(user_id=user_id, action='UPDATE_PRODUCT', details=f"Updated product ID: {product_id}"))
                session.commit()
            return True, "تم تعديل المنتج بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def delete_product(product_id, user_id=None):
        session = SessionLocal()
        try:
            product = session.query(Product).get(product_id)
            if not product:
                return False, "المنتج غير موجود"
            session.delete(product)
            session.commit()
            if user_id:
                session.add(AuditLog(user_id=user_id, action='DELETE_PRODUCT', details=f"Deleted product ID: {product_id}"))
                session.commit()
            return True, "تم حذف المنتج بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def get_categories():
        session = SessionLocal()
        try:
            return session.query(Category).all()
        finally:
            session.close()

    @staticmethod
    def add_category(name, description=""):
        session = SessionLocal()
        try:
            cat = Category(name=name, description=description)
            session.add(cat)
            session.commit()
            return True, "تم إضافة التصنيف بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
