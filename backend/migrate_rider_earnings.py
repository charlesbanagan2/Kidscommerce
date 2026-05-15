"""
Database migration to ensure rider earnings structure is correct
"""

from app import app, db
from sqlalchemy import text, inspect

print("=" * 70)
print("  RIDER EARNINGS DATABASE MIGRATION")
print("=" * 70)

with app.app_context():
    inspector = inspect(db.engine)
    
    # 1. Check order table has necessary columns
    print("\n[1] Checking order table columns...")
    order_columns = {col['name'] for col in inspector.get_columns('order')}
    
    required_columns = {
        'rider_id': 'INTEGER',
        'delivery_fee': 'FLOAT DEFAULT 36.0',
        'rider_earnings': 'FLOAT DEFAULT 0.0'
    }
    
    for col_name, col_type in required_columns.items():
        if col_name not in order_columns:
            print(f"   Adding column: {col_name}")
            try:
                db.session.execute(text(f'ALTER TABLE "order" ADD COLUMN {col_name} {col_type}'))
                db.session.commit()
                print(f"   (+) Added {col_name}")
            except Exception as e:
                print(f"   (-) Error adding {col_name}: {e}")
                db.session.rollback()
        else:
            print(f"   (+) Column {col_name} exists")
    
    # 2. Check wallet_transaction table
    print("\n[2] Checking wallet_transaction table...")
    try:
        wallet_columns = {col['name'] for col in inspector.get_columns('wallet_transaction')}
        print(f"   (+) wallet_transaction table exists with columns: {wallet_columns}")
        
        # Verify it has the necessary columns
        required_wallet_cols = ['id', 'user_id', 'order_id', 'amount', 'type', 'source', 'created_at']
        missing = set(required_wallet_cols) - wallet_columns
        if missing:
            print(f"   (-) Missing columns: {missing}")
        else:
            print(f"   (+) All required columns present")
            
    except Exception as e:
        print(f"   (-) Error checking wallet_transaction: {e}")
    
    # 3. Update existing orders to have delivery_fee if null
    print("\n[3] Updating existing orders with null delivery_fee...")
    try:
        result = db.session.execute(text('''
            UPDATE "order" 
            SET delivery_fee = 36.0 
            WHERE delivery_fee IS NULL OR delivery_fee = 0
        '''))
        db.session.commit()
        print(f"   (+) Updated {result.rowcount} orders")
    except Exception as e:
        print(f"   (-) Error updating orders: {e}")
        db.session.rollback()
    
    # 4. Check for any orders that should have been commissioned but weren't
    print("\n[4] Checking for uncommissioned completed orders...")
    try:
        from sqlalchemy import func
        
        # Find completed orders with riders that don't have wallet transactions
        uncommissioned = db.session.execute(text('''
            SELECT o.id, o.rider_id, o.delivery_fee, o.status
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
        
        if uncommissioned:
            print(f"   (!) Found {len(uncommissioned)} uncommissioned orders:")
            for order in uncommissioned:
                print(f"       Order #{order[0]}: Rider {order[1]}, Fee: P{order[2]}, Status: {order[3]}")
            print(f"   Run _release_commissions() for these orders to credit earnings")
        else:
            print(f"   (+) All completed orders have been commissioned")
            
    except Exception as e:
        print(f"   (-) Error checking uncommissioned orders: {e}")
    
    # 5. Summary
    print("\n" + "=" * 70)
    print("  MIGRATION SUMMARY")
    print("=" * 70)
    
    # Count total wallet transactions
    try:
        total_tx = db.session.execute(text('SELECT COUNT(*) FROM wallet_transaction')).scalar()
        delivery_tx = db.session.execute(text(
            "SELECT COUNT(*) FROM wallet_transaction WHERE source = 'order_delivery'"
        )).scalar()
        
        print(f"\n  Total wallet transactions: {total_tx}")
        print(f"  Delivery earnings transactions: {delivery_tx}")
        
        # Count riders with earnings
        riders_with_earnings = db.session.execute(text('''
            SELECT COUNT(DISTINCT user_id) 
            FROM wallet_transaction 
            WHERE source IN ('order_delivery', 'order_commission')
        ''')).scalar()
        
        print(f"  Riders with earnings: {riders_with_earnings}")
        
    except Exception as e:
        print(f"  Error getting summary: {e}")

print("\n" + "=" * 70)
print("  MIGRATION COMPLETE")
print("=" * 70)
print("\nNext steps:")
print("1. Restart the backend server")
print("2. Test the flow:")
print("   - Rider delivers order (status = 'delivered')")
print("   - Buyer confirms receipt (status = 'completed')")
print("   - Check rider earnings in mobile app")
