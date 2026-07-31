from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Customer, Supplier, AuditLog

class CRMService:
    # --- CUSTOMERS ---
    @staticmethod
    def get_all_customers():
        session = SessionLocal()
        try:
            return session.query(Customer).order_by(Customer.name.asc()).all()
        finally:
            session.close()

    @staticmethod
    def add_customer(data, user_id=None):
        session = SessionLocal()
        try:
            customer = Customer(**data)
            session.add(customer)
            session.commit()
            if user_id:
                session.add(AuditLog(user_id=user_id, action='ADD_CUSTOMER', details=f"Added customer: {customer.name}"))
                session.commit()
            return True, "تم إضافة العميل بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def update_customer(customer_id, data, user_id=None):
        session = SessionLocal()
        try:
            customer = session.get(Customer, customer_id)
            if not customer:
                return False, "العميل غير موجود"
            for key, value in data.items():
                setattr(customer, key, value)
            session.commit()
            if user_id:
                session.add(AuditLog(user_id=user_id, action='UPDATE_CUSTOMER', details=f"Updated customer ID: {customer_id}"))
                session.commit()
            return True, "تم تعديل بيانات العميل بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def delete_customer(customer_id, user_id=None):
        session = SessionLocal()
        try:
            customer = session.get(Customer, customer_id)
            if not customer:
                return False, "العميل غير موجود"
            # Prevent deletion if customer has sales
            if customer.sales:
                return False, "لا يمكن حذف عميل لديه فواتير مبيعات مسجلة"
            session.delete(customer)
            session.commit()
            if user_id:
                session.add(AuditLog(user_id=user_id, action='DELETE_CUSTOMER', details=f"Deleted customer ID: {customer_id}"))
                session.commit()
            return True, "تم حذف العميل بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    # --- SUPPLIERS ---
    @staticmethod
    def get_all_suppliers():
        session = SessionLocal()
        try:
            return session.query(Supplier).order_by(Supplier.name.asc()).all()
        finally:
            session.close()

    @staticmethod
    def add_supplier(data, user_id=None):
        session = SessionLocal()
        try:
            supplier = Supplier(**data)
            session.add(supplier)
            session.commit()
            if user_id:
                session.add(AuditLog(user_id=user_id, action='ADD_SUPPLIER', details=f"Added supplier: {supplier.name}"))
                session.commit()
            return True, "تم إضافة المورد بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def update_supplier(supplier_id, data, user_id=None):
        session = SessionLocal()
        try:
            supplier = session.get(Supplier, supplier_id)
            if not supplier:
                return False, "المورد غير موجود"
            for key, value in data.items():
                setattr(supplier, key, value)
            session.commit()
            if user_id:
                session.add(AuditLog(user_id=user_id, action='UPDATE_SUPPLIER', details=f"Updated supplier ID: {supplier_id}"))
                session.commit()
            return True, "تم تعديل بيانات المورد بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def delete_supplier(supplier_id, user_id=None):
        session = SessionLocal()
        try:
            supplier = session.get(Supplier, supplier_id)
            if not supplier:
                return False, "المورد غير موجود"
            if supplier.purchases or supplier.products:
                return False, "لا يمكن حذف مورد مرتبط بمشتريات أو منتجات"
            session.delete(supplier)
            session.commit()
            if user_id:
                session.add(AuditLog(user_id=user_id, action='DELETE_SUPPLIER', details=f"Deleted supplier ID: {supplier_id}"))
                session.commit()
            return True, "تم حذف المورد بنجاح"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
