from pos_erp.database.db import SessionLocal
from pos_erp.database.models import Product, InventoryMovement

class InventoryValuationService:
    @staticmethod
    def get_stock_valuation():
        session = SessionLocal()
        try:
            products = session.query(Product).all()
            valuation = []
            total_value = 0.0
            
            for p in products:
                val = p.quantity * p.purchase_price
                total_value += val
                valuation.append({
                    'product': p.name,
                    'sku': p.sku,
                    'quantity': p.quantity,
                    'unit_cost': p.purchase_price,
                    'total_value': val
                })
            
            return {
                'items': valuation,
                'total_value': total_value
            }
        finally:
            session.close()

    @staticmethod
    def recalculate_moving_average(product_id):
        # A utility to repair costing if data is corrupted
        session = SessionLocal()
        try:
            movements = session.query(InventoryMovement).filter_by(product_id=product_id).order_by(InventoryMovement.created_at.asc()).all()
            qty = 0.0
            total_cost = 0.0
            
            for m in movements:
                if m.movement_type == 'IN':
                    # Recalculate average
                    new_qty = qty + m.quantity
                    if new_qty > 0:
                        avg_cost = (total_cost + (m.quantity * m.unit_cost)) / new_qty
                        total_cost += (m.quantity * m.unit_cost)
                        qty = new_qty
                        # Update product
                        product = session.get(Product, product_id)
                        product.purchase_price = avg_cost
                elif m.movement_type == 'OUT':
                    qty -= m.quantity
                    product = session.get(Product, product_id)
                    total_cost -= (m.quantity * product.purchase_price)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
