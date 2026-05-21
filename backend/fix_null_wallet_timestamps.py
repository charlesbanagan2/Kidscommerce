"""
Fix NULL created_at timestamps in wallet_transaction table
by setting them to the order's completion timestamp
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, WalletTransaction, Order
from datetime import datetime

def main():
    print("\n" + "="*70)
    print("  🔧 FIX NULL WALLET TRANSACTION TIMESTAMPS")
    print("="*70)
    
    with app.app_context():
        # Find all wallet transactions with NULL created_at
        null_transactions = WalletTransaction.query.filter(
            WalletTransaction.created_at.is_(None)
        ).all()
        
        print(f"\n📊 Found {len(null_transactions)} transactions with NULL created_at")
        
        if not null_transactions:
            print("✅ No NULL timestamps found - all transactions are properly dated!")
            return
        
        fixed_count = 0
        failed_count = 0
        
        for wt in null_transactions:
            print(f"\n🔍 Transaction ID {wt.id}:")
            print(f"   User ID: {wt.user_id}")
            print(f"   Amount: ₱{wt.amount:.2f}")
            print(f"   Source: {wt.source}")
            print(f"   Order ID: {wt.order_id}")
            
            # Try to get the order's completion timestamp
            if wt.order_id:
                order = Order.query.get(wt.order_id)
                if order:
                    # Use order's updated_at or created_at as fallback
                    timestamp = order.updated_at or order.created_at
                    
                    if timestamp:
                        print(f"   ✅ Setting created_at to order timestamp: {timestamp}")
                        wt.created_at = timestamp
                        fixed_count += 1
                    else:
                        print(f"   ⚠️  Order has no timestamp - using current time")
                        wt.created_at = datetime.utcnow()
                        fixed_count += 1
                else:
                    print(f"   ⚠️  Order #{wt.order_id} not found - using current time")
                    wt.created_at = datetime.utcnow()
                    fixed_count += 1
            else:
                print(f"   ⚠️  No order_id - using current time")
                wt.created_at = datetime.utcnow()
                fixed_count += 1
        
        # Commit all changes
        if fixed_count > 0:
            try:
                db.session.commit()
                print("\n" + "="*70)
                print(f"✅ Successfully fixed {fixed_count} transactions!")
                print("="*70)
            except Exception as e:
                db.session.rollback()
                print("\n" + "="*70)
                print(f"❌ Error committing changes: {e}")
                print("="*70)
        else:
            print("\n" + "="*70)
            print("⚠️  No transactions were fixed")
            print("="*70)

if __name__ == '__main__':
    main()
