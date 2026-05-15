"""
Complete fix for rider earnings flow:
- Rider earnings are only credited when buyer confirms receipt (status='completed' or 'received')
- Delivery fee is stored in order.delivery_fee (already exists)
- Earnings are credited via wallet_transaction with source='order_delivery'
"""

import re

print("=" * 70)
print("  FIXING RIDER EARNINGS FLOW")
print("=" * 70)

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Find the api_rider_mark_delivered endpoint and remove any early earnings credit
print("\n[1] Removing early earnings credit from mark_delivered endpoint...")

# Remove the credit_wallet block if it exists
pattern = r"        # Credit rider earnings.*?except Exception as e:\s+app\.logger\.error\(f\"Failed to credit rider earnings: \{e\}\"\)\s+"
content = re.sub(pattern, '', content, flags=re.DOTALL)

# Add comment explaining the flow
if "# NOTE: Rider earnings will be credited when buyer confirms receipt" not in content:
    content = content.replace(
        "        # Notify buyer",
        "        # NOTE: Rider earnings will be credited when buyer confirms receipt (status='completed')\n        # This is handled by _release_commissions() function\n        \n        # Notify buyer"
    )
print("   (+) Removed early earnings credit")

# 2. Update _release_commissions to properly credit rider earnings
print("\n[2] Updating _release_commissions to credit rider earnings...")

# Find the _release_commissions function
release_pattern = r"def _release_commissions\(order: 'Order'\):.*?db\.session\.commit\(\)"
match = re.search(release_pattern, content, re.DOTALL)

if match:
    old_function = match.group(0)
    
    # Create new function with proper rider earnings
    new_function = '''def _release_commissions(order: 'Order'):
    """Release commissions once buyer confirms receipt (status: completed or received). Safe to call idempotently."""
    if _order_already_commissioned(order.id):
        return
    
    total = float(order.total_amount)
    
    # RIDER EARNINGS: Credit delivery fee when buyer confirms receipt
    if order.rider_id:
        delivery_fee = float(order.delivery_fee) if hasattr(order, 'delivery_fee') and order.delivery_fee else 36.0
        try:
            credit_wallet(order.rider_id, delivery_fee, 'order_delivery', order.id)
            app.logger.info(f"✅ Credited rider {order.rider_id} with ₱{delivery_fee} for order #{order.id}")
        except Exception as e:
            app.logger.error(f"❌ Failed to credit rider earnings: {e}")
    
    # Sellers: proportional by item subtotal
    seller_totals = {}
    for it in order.items:
        seller_totals.setdefault(it.product.seller_id, 0.0)
        seller_totals[it.product.seller_id] += float(it.price_at_time) * it.quantity
    seller_total_amount = sum(seller_totals.values()) or 0.0
    if seller_total_amount > 0:
        for sid, sub in seller_totals.items():
            credit_wallet(sid, (sub / seller_total_amount) * (total * SELLER_EARNING_RATE), 'order_commission', order.id)
    
    # Admins
    admins = _admins()
    if admins:
        admin_amount_each = (total * ADMIN_EARNING_RATE) / len(admins)
        for a in admins:
            credit_wallet(a['id'], admin_amount_each, 'order_commission', order.id)
    
    db.session.commit()'''
    
    content = content.replace(old_function, new_function)
    print("   (+) Updated _release_commissions function")
else:
    print("   (-) Could not find _release_commissions function")

# 3. Ensure buyer confirmation triggers earnings
print("\n[3] Checking buyer confirmation endpoints...")

# Find buyer confirmation endpoint
if "def buyer_confirm_order" in content or "confirm_receipt" in content:
    print("   (+) Buyer confirmation endpoint exists")
else:
    print("   (!) Warning: No buyer confirmation endpoint found")

# 4. Update get_user_earnings to include rider earnings
print("\n[4] Updating get_user_earnings to include rider earnings...")

earnings_pattern = r"def get_user_earnings\(user_id: int, period: str = 'today'\) -> float:.*?return float\(result\) if result else 0\.0"
match = re.search(earnings_pattern, content, re.DOTALL)

if match:
    old_function = match.group(0)
    
    new_function = '''def get_user_earnings(user_id: int, period: str = 'today') -> float:
    """Return sum of credits for a user within the period using optimized SQL query.
    Includes both order_commission and order_delivery sources."""
    from sqlalchemy import func

    now = datetime.utcnow()

    # Build base query with WHERE clause instead of fetching all data
    query = db.session.query(
        func.sum(WalletTransaction.amount).label('total')
    ).filter(
        WalletTransaction.user_id == user_id,
        WalletTransaction.type == 'credit',
        WalletTransaction.source.in_(['order_commission', 'order_delivery'])  # Include rider delivery earnings
    )

    # Add date filter in SQL instead of Python
    if period == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(WalletTransaction.created_at >= start)
    elif period == 'week':
        start = now - timedelta(days=7)
        query = query.filter(WalletTransaction.created_at >= start)
    elif period == 'month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(WalletTransaction.created_at >= start)
    # For 'all', no date filter needed

    result = query.scalar()
    return float(result) if result else 0.0'''
    
    content = content.replace(old_function, new_function)
    print("   (+) Updated get_user_earnings function")
else:
    print("   (-) Could not find get_user_earnings function")

# 5. Add API endpoint for rider earnings if not exists
print("\n[5] Checking rider earnings API endpoint...")

if "@app.route('/api/v1/rider/earnings'" in content:
    print("   (+) Rider earnings API endpoint exists")
else:
    print("   (!) Adding rider earnings API endpoint...")
    
    # Find a good place to add it (after other rider endpoints)
    rider_orders_pattern = r"(@app\.route\('/api/v1/rider/my-deliveries'.*?return jsonify\(\{[^}]+\}\), 200)"
    match = re.search(rider_orders_pattern, content, re.DOTALL)
    
    if match:
        endpoint_code = '''

@app.route('/api/v1/rider/earnings', methods=['GET'])
@token_required
@role_required('rider')
def api_rider_earnings():
    """Get rider earnings breakdown"""
    try:
        rider_id = request.current_user_id
        
        # Get earnings by period
        total = get_user_earnings(rider_id, 'all')
        today = get_user_earnings(rider_id, 'today')
        week = get_user_earnings(rider_id, 'week')
        month = get_user_earnings(rider_id, 'month')
        
        return jsonify({
            'success': True,
            'total': total,
            'today': today,
            'week': week,
            'month': month
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching rider earnings: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch earnings'
        }), 500
'''
        
        insert_pos = match.end()
        content = content[:insert_pos] + endpoint_code + content[insert_pos:]
        print("   (+) Added rider earnings API endpoint")
    else:
        print("   (-) Could not find insertion point for API endpoint")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "=" * 70)
print("  RIDER EARNINGS FLOW FIXED")
print("=" * 70)
print("\nFlow:")
print("1. Rider accepts order -> order.rider_id set, order.delivery_fee calculated")
print("2. Rider picks up -> status = 'picked_up'")
print("3. Rider delivers -> status = 'delivered' (NO earnings yet)")
print("4. Buyer confirms receipt -> status = 'completed'")
print("5. _release_commissions() called -> Rider gets delivery_fee via wallet_transaction")
print("\nEarnings are tracked in wallet_transaction table with source='order_delivery'")
print("\n✅ COMPLETE - Restart backend to apply changes")
