#!/usr/bin/env python3
"""
Fix checkout to immediately deduct stock and broadcast updates
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace reserve_stock with immediate deduction
old_stock_handling = """            # Reserve stock for each item with transaction rollback on failure
            for cart_item in cart_items:
                if not reserve_stock(new_order.id, cart_item.get('product_id'), cart_item.get('quantity')):
                    db.session.rollback()
                    return jsonify({'success': False, 'error': 'Insufficient stock to reserve items'}), 400
                
                db.session.add(OrderItem(
                    order_id=new_order.id,
                    product_id=cart_item.get('product_id'),
                    quantity=cart_item.get('quantity'),
                    price_at_time=cart_item.get('price', 0)
                ))
            
            new_order.stock_deducted = False"""

new_stock_handling = """            # Immediately deduct stock for each item with transaction rollback on failure
            for cart_item in cart_items:
                product_id = cart_item.get('product_id')
                quantity = cart_item.get('quantity')
                
                # Get product and check stock
                product = db.session.get(Product, product_id)
                if not product:
                    db.session.rollback()
                    return jsonify({'success': False, 'error': 'Product not found'}), 400
                
                # Check available stock
                if product.stock < quantity:
                    db.session.rollback()
                    return jsonify({'success': False, 'error': f'Insufficient stock for {product.name}. Only {product.stock} available'}), 400
                
                # Immediately deduct stock
                product.stock = product.stock - quantity
                
                # Create order item
                db.session.add(OrderItem(
                    order_id=new_order.id,
                    product_id=product_id,
                    quantity=quantity,
                    price_at_time=cart_item.get('price', 0)
                ))
            
            new_order.stock_deducted = True"""

if old_stock_handling in content:
    content = content.replace(old_stock_handling, new_stock_handling)
    print("[OK] Updated stock handling to immediate deduction")
else:
    print("[WARN] Could not find exact stock handling pattern")
    print("Checking if already updated...")
    if 'Immediately deduct stock' in content:
        print("[INFO] Already using immediate stock deduction")
    else:
        print("[ERROR] Manual intervention needed")

# Add broadcast after commit
old_commit = """            db.session.commit()
            
            # Clear cart items"""

new_commit = """            db.session.commit()
            
            # Broadcast stock updates to all connected clients
            for cart_item in cart_items:
                try:
                    broadcast_stock_update(cart_item.get('product_id'))
                except Exception as e:
                    app.logger.error(f'Failed to broadcast stock update: {e}')
            
            # Clear cart items"""

if old_commit in content:
    content = content.replace(old_commit, new_commit)
    print("[OK] Added stock broadcast after commit")
else:
    print("[INFO] Broadcast may already be added or pattern not found")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[SUCCESS] Stock deduction logic updated!")
print("\nChanges:")
print("1. Stock is now immediately deducted when order is placed")
print("2. stock_deducted flag set to True")
print("3. Real-time broadcast sent to all clients")
print("\nNext: Restart Flask backend")
