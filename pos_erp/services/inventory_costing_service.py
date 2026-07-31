from pos_erp.database.models import Setting, Product, InventoryBatch, InventoryMovement

class InventoryCostingService:
    @staticmethod
    def get_costing_method(session):
        setting = session.query(Setting).filter_by(key='costing_method').first()
        return setting.value if setting else 'WEIGHTED_AVERAGE'

    @staticmethod
    def process_in(session, product_id, quantity, unit_cost, reference=None, user_id=None, notes=None):
        method = InventoryCostingService.get_costing_method(session)
        product = session.get(Product, product_id)
        
        batch = InventoryBatch(
            product_id=product_id,
            quantity_initial=quantity,
            quantity_remaining=quantity,
            unit_cost=unit_cost
        )
        session.add(batch)

        if method == 'WEIGHTED_AVERAGE':
            old_qty = max(product.quantity, 0) # Protect against negative qty messing up average
            old_cost = product.purchase_price
            new_qty = old_qty + quantity
            if new_qty > 0:
                product.purchase_price = ((old_qty * old_cost) + (quantity * unit_cost)) / new_qty
        elif method == 'STANDARD':
            pass # Standard cost is set manually by admin

        product.quantity += quantity

        movement = InventoryMovement(
            product_id=product_id,
            movement_type='IN',
            quantity=quantity,
            unit_cost=unit_cost,
            reference=reference,
            user_id=user_id,
            notes=notes
        )
        session.add(movement)

    @staticmethod
    def process_out(session, product_id, quantity, reference=None, user_id=None, notes=None):
        method = InventoryCostingService.get_costing_method(session)
        product = session.get(Product, product_id)
        
        total_cost = 0.0
        
        if method == 'STANDARD':
            total_cost = product.purchase_price * quantity
            unit_cost = product.purchase_price
        elif method == 'WEIGHTED_AVERAGE':
            total_cost = product.purchase_price * quantity
            unit_cost = product.purchase_price
        elif method == 'FIFO':
            remaining_qty = quantity
            batches = session.query(InventoryBatch).filter(
                InventoryBatch.product_id == product_id,
                InventoryBatch.quantity_remaining > 0
            ).order_by(InventoryBatch.created_at.asc()).with_for_update().all()
            
            for batch in batches:
                if remaining_qty <= 0:
                    break
                if batch.quantity_remaining >= remaining_qty:
                    total_cost += remaining_qty * batch.unit_cost
                    batch.quantity_remaining -= remaining_qty
                    remaining_qty = 0
                else:
                    total_cost += batch.quantity_remaining * batch.unit_cost
                    remaining_qty -= batch.quantity_remaining
                    batch.quantity_remaining = 0
            
            if remaining_qty > 0:
                total_cost += remaining_qty * product.purchase_price
            
            unit_cost = (total_cost / quantity) if quantity > 0 else 0.0

        product.quantity -= quantity

        movement = InventoryMovement(
            product_id=product_id,
            movement_type='OUT',
            quantity=quantity,
            unit_cost=unit_cost,
            reference=reference,
            user_id=user_id,
            notes=notes
        )
        session.add(movement)
        
        return total_cost, unit_cost
