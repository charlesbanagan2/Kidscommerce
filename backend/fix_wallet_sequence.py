"""
Fix wallet_transaction sequence and manually insert rider earnings
"""

from app import app, db
from sqlalchemy import text

print("=" * 70)
print("  FIXING WALLET TRANSACTION SEQUENCE")
print("=" * 70)

with app.app_context():
    # 1. Fix the sequence
    print("\n[1] Fixing wallet_transaction sequence...")
    try:
        # Get the max ID
        max_id = db.session.execute(text('SELECT MAX(id) FROM wallet_transaction')).scalar() or 0
        print(f"   Current max ID: {max_id}")
        
        # Reset the sequence
        db.session.execute(text(f"SELECT setval('wallet_transaction_id_seq', {max_id + 1}, false)"))
        db.session.commit()
        print(f"   (+) Sequence reset to {max_id + 1}")
    except Exception as e:
        print(f"   (-) Error: {e}")
        db.session.rollback()
    
    # 2. Manually insert rider earnings for completed orders
    print("\n[2] Manually inserting rider earnings...")
    
    uncommissioned = db.session.execute(text('''
        SELECT o.id, o.rider_id, o.delivery_fee
        FROM "order" o
        WHERE o.status IN ('completed', 'received')
        AND o.rider_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM wallet_transaction wt
            WHERE wt.order_id = o.id
            AND wt.user_id = o.rider_id
            AND wt.source = 'order_delivery'
        )
    ''')).fetchall()
    
    if not uncommissioned:
        print("   (+) No uncommissioned orders found")
    else:
        print(f"   Found {len(uncommissioned)} orders to process")
        
        for order_id, rider_id, delivery_fee in uncommissioned:
            try:
                db.session.execute(text('''
                    INSERT INTO wallet_transaction (user_id, order_id, amount, type, source, created_at)
                    VALUES (:user_id, :order_id, :amount, 'credit', 'order_delivery', NOW())
                '''), {
                    'user_id': rider_id,
                    'order_id': order_id,
                    'amount': delivery_fee or 36.0
                })
                print(f"   (+) Order #{order_id}: Credited P{delivery_fee or 36.0} to rider {rider_id}")
            except Exception as e:
                print(f"   (-) Order #{order_id}: Error - {e}")
                db.session.rollback()
                continue
        
        db.session.commit()
    
    # 3. Verify results
    print("\n[3] Verification...")
    
    delivery_tx = db.session.execute(text(
        "SELECT COUNT(*) FROM wallet_transaction WHERE source = 'order_delivery'"
    )).scalar()
    
    total_delivery_amount = db.session.execute(text(
        "SELECT SUM(amount) FROM wallet_transaction WHERE source = 'order_delivery'"
    )).scalar() or 0
    
    print(f"   Delivery earnings transactions: {delivery_tx}")
    print(f"   Total delivery earnings: P{total_delivery_amount}")
    
    # Show rider earnings
    rider_earnings = db.session.execute(text('''
        SELECT u.email, SUM(wt.amount) as total, COUNT(*) as count
        FROM wallet_transaction wt
        JOIN "user" u ON u.id = wt.user_id
        WHERE wt.source = 'order_delivery'
        GROUP BY u.id, u.email
        ORDER BY total DESC
    ''')).fetchall()
    
    if rider_earnings:
        print(f"\n   Rider Earnings Breakdown:")
        for email, total, count in rider_earnings:
            print(f"     {email}: P{total} ({count} deliveries)")

print("\n" + "=" * 70)
print("  COMPLETE")
print("=" * 70)
