"""
Backfill rider earnings for completed orders that haven't been commissioned
"""

from app import app, db, Order, _release_commissions
from sqlalchemy import text

print("=" * 70)
print("  BACKFILLING RIDER EARNINGS")
print("=" * 70)

with app.app_context():
    # Find uncommissioned completed orders
    uncommissioned = db.session.execute(text('''
        SELECT o.id, o.rider_id, o.delivery_fee, o.status, o.total_amount
        FROM "order" o
        WHERE o.status IN ('completed', 'received')
        AND o.rider_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM wallet_transaction wt
            WHERE wt.order_id = o.id
            AND wt.user_id = o.rider_id
            AND wt.source IN ('order_delivery', 'order_commission')
        )
    ''')).fetchall()
    
    if not uncommissioned:
        print("\n(+) No uncommissioned orders found - all earnings are up to date!")
    else:
        print(f"\n[Found {len(uncommissioned)} uncommissioned orders]")
        
        success_count = 0
        error_count = 0
        
        for order_data in uncommissioned:
            order_id, rider_id, delivery_fee, status, total_amount = order_data
            
            print(f"\nProcessing Order #{order_id}:")
            print(f"  Rider ID: {rider_id}")
            print(f"  Delivery Fee: P{delivery_fee}")
            print(f"  Total Amount: P{total_amount}")
            print(f"  Status: {status}")
            
            try:
                # Get the order object
                order = db.session.get(Order, order_id)
                if not order:
                    print(f"  (-) Order not found")
                    error_count += 1
                    continue
                
                # Call _release_commissions to credit all earnings
                _release_commissions(order)
                
                print(f"  (+) Successfully commissioned!")
                success_count += 1
                
            except Exception as e:
                print(f"  (-) Error: {e}")
                error_count += 1
                db.session.rollback()
        
        print("\n" + "=" * 70)
        print("  BACKFILL SUMMARY")
        print("=" * 70)
        print(f"\n  Total orders processed: {len(uncommissioned)}")
        print(f"  Successful: {success_count}")
        print(f"  Errors: {error_count}")
        
        # Show updated stats
        if success_count > 0:
            print("\n[Updated Earnings Stats]")
            
            delivery_tx = db.session.execute(text(
                "SELECT COUNT(*) FROM wallet_transaction WHERE source = 'order_delivery'"
            )).scalar()
            
            total_delivery_amount = db.session.execute(text(
                "SELECT SUM(amount) FROM wallet_transaction WHERE source = 'order_delivery'"
            )).scalar() or 0
            
            print(f"  Delivery earnings transactions: {delivery_tx}")
            print(f"  Total delivery earnings: P{total_delivery_amount}")
            
            # Show rider earnings
            rider_earnings = db.session.execute(text('''
                SELECT u.email, SUM(wt.amount) as total
                FROM wallet_transaction wt
                JOIN user u ON u.id = wt.user_id
                WHERE wt.source = 'order_delivery'
                GROUP BY u.id, u.email
                ORDER BY total DESC
            ''')).fetchall()
            
            if rider_earnings:
                print(f"\n  Rider Earnings Breakdown:")
                for email, total in rider_earnings:
                    print(f"    {email}: P{total}")

print("\n" + "=" * 70)
print("  BACKFILL COMPLETE")
print("=" * 70)
