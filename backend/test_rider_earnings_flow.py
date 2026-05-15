"""
Test script to verify rider earnings flow is working correctly
"""

from app import app, db, Order, User, WalletTransaction, _release_commissions
from datetime import datetime

print("=" * 70)
print("  TESTING RIDER EARNINGS FLOW")
print("=" * 70)

with app.app_context():
    # Find a delivered order with a rider
    test_order = Order.query.filter(
        Order.status == 'delivered',
        Order.rider_id.isnot(None)
    ).first()
    
    if not test_order:
        print("\n(-) No delivered orders with riders found for testing")
        print("    Create a test order first")
    else:
        print(f"\n[Test Order]")
        print(f"  Order ID: #{test_order.id}")
        print(f"  Status: {test_order.status}")
        print(f"  Rider ID: {test_order.rider_id}")
        print(f"  Delivery Fee: P{test_order.delivery_fee}")
        print(f"  Total Amount: P{test_order.total_amount}")
        
        # Check current rider earnings
        rider = User.query.get(test_order.rider_id)
        if rider:
            print(f"\n[Rider Info]")
            print(f"  Name: {rider.first_name} {rider.last_name}")
            print(f"  Email: {rider.email}")
            
            # Check wallet transactions
            transactions = WalletTransaction.query.filter_by(
                user_id=rider.id,
                order_id=test_order.id
            ).all()
            
            print(f"\n[Current Wallet Transactions for this order]")
            if transactions:
                for tx in transactions:
                    print(f"  - Amount: P{tx.amount}, Source: {tx.source}, Type: {tx.type}")
            else:
                print("  - No transactions yet")
            
            # Simulate buyer confirmation
            print(f"\n[Simulating Buyer Confirmation]")
            print(f"  Changing order status from '{test_order.status}' to 'completed'...")
            
            test_order.status = 'completed'
            db.session.commit()
            
            print(f"  Calling _release_commissions()...")
            try:
                _release_commissions(test_order)
                print(f"  (+) Success!")
                
                # Check new transactions
                new_transactions = WalletTransaction.query.filter_by(
                    user_id=rider.id,
                    order_id=test_order.id
                ).all()
                
                print(f"\n[New Wallet Transactions]")
                for tx in new_transactions:
                    print(f"  - Amount: P{tx.amount}, Source: {tx.source}, Type: {tx.type}, Created: {tx.created_at}")
                
                # Calculate total earnings
                from sqlalchemy import func
                total_earnings = db.session.query(
                    func.sum(WalletTransaction.amount)
                ).filter(
                    WalletTransaction.user_id == rider.id,
                    WalletTransaction.type == 'credit',
                    WalletTransaction.source.in_(['order_delivery', 'order_commission'])
                ).scalar() or 0
                
                print(f"\n[Rider Total Earnings]")
                print(f"  Total: P{total_earnings}")
                
            except Exception as e:
                print(f"  (-) Error: {e}")
                import traceback
                traceback.print_exc()

print("\n" + "=" * 70)
print("  TEST COMPLETE")
print("=" * 70)
