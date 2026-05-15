# Shopee-Style Inventory Management Functions
# Add these functions to app.py or import them

def deduct_stock_immediately(product_id, quantity):
    """
    Shopee-style: Immediately deduct stock when order is placed.
    Returns True if successful, False if insufficient stock.
    """
    from app import db, Product, broadcast_stock_update
    
    try:
        # Use row-level locking to prevent race conditions
        product = db.session.query(Product).filter_by(id=product_id).with_for_update().first()
        
        if not product:
            return False
        
        if product.stock < quantity:
            return False
        
        # Immediately deduct from stock
        product.stock = product.stock - quantity
        
        # Broadcast update to all connected clients
        try:
            broadcast_stock_update(product_id)
        except Exception:
            pass
        
        return True
    except Exception as e:
        print(f"Error deducting stock: {e}")
        return False


def restore_stock_on_cancel(order_id):
    """
    Shopee-style: Restore stock when order is cancelled.
    Only restores if order was in 'pending', 'to_pay', or 'processing' status.
    Returns list of product IDs that had stock restored.
    """
    from app import db, Order, Product, broadcast_stock_update
    
    try:
        order = db.session.get(Order, order_id)
        if not order:
            return []
        
        # Only restore stock for orders that haven't been shipped/completed
        if order.status not in ['pending', 'to_pay', 'processing']:
            return []
        
        restored_products = []
        
        for item in order.items:
            product = db.session.get(Product, item.product_id)
            if product:
                # Add quantity back to stock
                product.stock = product.stock + item.quantity
                restored_products.append(product.id)
                
                # Broadcast update
                try:
                    broadcast_stock_update(product.id)
                except Exception:
                    pass
        
        db.session.commit()
        return restored_products
        
    except Exception as e:
        db.session.rollback()
        print(f"Error restoring stock: {e}")
        return []
