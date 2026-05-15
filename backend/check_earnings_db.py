"""
Direct Database Check for Order Earnings
Quick verification of earnings data in the database
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Order, WalletTransaction, User
from sqlalchemy import func

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def check_wallet_transactions():
    """Check wallet transactions table"""
    print_header("WALLET TRANSACTIONS CHECK")
    
    with app.app_context():
        try:
            # Total transactions
            total_count = WalletTransaction.query.count()
            print(f"\n(+) Total wallet transactions: {total_count}")
            
            # Transactions by type
            print("\nTransactions by Type:")
            types = db.session.query(
                WalletTransaction.type,
                func.count(WalletTransaction.id),
                func.sum(WalletTransaction.amount)
            ).group_by(WalletTransaction.type).all()
            
            for tx_type, count, total in types:
                print(f"  - {tx_type}: {count} transactions, Total: P{total or 0:.2f}")
            
            # Transactions by source
            print("\nTransactions by Source:")
            sources = db.session.query(
                WalletTransaction.source,
                func.count(WalletTransaction.id),
                func.sum(WalletTransaction.amount)
            ).group_by(WalletTransaction.source).all()
            
            for source, count, total in sources:
                print(f"  - {source}: {count} transactions, Total: P{total or 0:.2f}")
            
            # Recent transactions
            print("\nRecent Transactions (Last 5):")
            recent = WalletTransaction.query.order_by(
                WalletTransaction.created_at.desc()
            ).limit(5).all()
            
            for tx in recent:
                user = User.query.get(tx.user_id)
                username = user.email if user else "Unknown"
                print(f"  - User: {username} | Amount: P{tx.amount:.2f} | Type: {tx.type} | Source: {tx.source}")
            
            return True
            
        except Exception as e:
            print(f"\n(-) Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def check_rider_earnings():
    """Check rider-specific earnings"""
    print_header("RIDER EARNINGS CHECK")
    
    with app.app_context():
        try:
            # Find riders
            riders = User.query.filter_by(role='rider').all()
            print(f"\n(+) Found {len(riders)} riders in system")
            
            if not riders:
                print("(!) No riders found in database")
                return True
            
            print("\nRider Earnings Summary:")
            for rider in riders:
                # Get rider's earnings
                earnings = db.session.query(
                    func.sum(WalletTransaction.amount)
                ).filter(
                    WalletTransaction.user_id == rider.id,
                    WalletTransaction.type == 'credit'
                ).scalar()
                
                total_earnings = float(earnings) if earnings else 0.0
                
                # Get number of deliveries
                deliveries = Order.query.filter_by(picked_up_by=rider.id).count()
                completed = Order.query.filter_by(
                    picked_up_by=rider.id,
                    status='completed'
                ).count()
                
                print(f"\n  Rider: {rider.email} (ID: {rider.id})")
                print(f"  - Total Earnings: P{total_earnings:.2f}")
                print(f"  - Total Deliveries: {deliveries}")
                print(f"  - Completed: {completed}")
                
                # Show recent earnings
                recent_earnings = WalletTransaction.query.filter(
                    WalletTransaction.user_id == rider.id,
                    WalletTransaction.type == 'credit'
                ).order_by(WalletTransaction.created_at.desc()).limit(3).all()
                
                if recent_earnings:
                    print(f"  - Recent Earnings:")
                    for tx in recent_earnings:
                        print(f"    * P{tx.amount:.2f} from {tx.source} (Order #{tx.order_id})")
            
            return True
            
        except Exception as e:
            print(f"\n(-) Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def check_orders_with_earnings():
    """Check orders and their earnings"""
    print_header("ORDERS WITH EARNINGS CHECK")
    
    with app.app_context():
        try:
            # Orders with riders
            orders_with_riders = Order.query.filter(
                Order.picked_up_by.isnot(None)
            ).all()
            
            print(f"\n(+) Found {len(orders_with_riders)} orders with riders assigned")
            
            if not orders_with_riders:
                print("(!) No orders with riders found")
                return True
            
            # Group by status
            print("\nOrders by Status:")
            statuses = db.session.query(
                Order.status,
                func.count(Order.id)
            ).filter(
                Order.picked_up_by.isnot(None)
            ).group_by(Order.status).all()
            
            for status, count in statuses:
                print(f"  - {status}: {count} orders")
            
            # Check completed orders
            completed_orders = Order.query.filter(
                Order.picked_up_by.isnot(None),
                Order.status == 'completed'
            ).all()
            
            if completed_orders:
                print(f"\nCompleted Orders with Riders ({len(completed_orders)}):")
                for order in completed_orders[:5]:  # Show first 5
                    rider = User.query.get(order.picked_up_by)
                    rider_name = rider.email if rider else "Unknown"
                    
                    # Check if earnings were credited
                    earnings_tx = WalletTransaction.query.filter_by(
                        user_id=order.picked_up_by,
                        order_id=order.id
                    ).first()
                    
                    earnings_status = "(+) Credited" if earnings_tx else "(-) NOT CREDITED"
                    earnings_amount = f"P{earnings_tx.amount:.2f}" if earnings_tx else "P0.00"
                    
                    print(f"\n  Order #{order.id}:")
                    print(f"  - Rider: {rider_name}")
                    print(f"  - Total: P{order.total_amount:.2f}")
                    print(f"  - Earnings: {earnings_amount} {earnings_status}")
            
            return True
            
        except Exception as e:
            print(f"\n(-) Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def check_earnings_rates():
    """Check earnings rate configuration"""
    print_header("EARNINGS RATES CONFIGURATION")
    
    try:
        from app import RIDER_EARNING_RATE, SELLER_EARNING_RATE, ADMIN_EARNING_RATE
        
        print("\n(+) Earnings Rates:")
        print(f"  - Rider:  {RIDER_EARNING_RATE * 100}% of order total")
        print(f"  - Seller: {SELLER_EARNING_RATE * 100}% of order total")
        print(f"  - Admin:  {ADMIN_EARNING_RATE * 100}% of order total")
        
        total_rate = (RIDER_EARNING_RATE + SELLER_EARNING_RATE + ADMIN_EARNING_RATE) * 100
        print(f"\n  Total: {total_rate}%")
        
        if total_rate == 100:
            print("  (+) Rates add up to 100%")
        else:
            print(f"  (!) Warning: Rates add up to {total_rate}%, not 100%")
        
        # Example calculation
        print("\n(+) Example Calculation (P1000 order):")
        print(f"  - Rider gets:  P{1000 * RIDER_EARNING_RATE:.2f}")
        print(f"  - Seller gets: P{1000 * SELLER_EARNING_RATE:.2f}")
        print(f"  - Admin gets:  P{1000 * ADMIN_EARNING_RATE:.2f}")
        
        return True
        
    except Exception as e:
        print(f"\n(-) Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*70)
    print("  ORDER EARNINGS DATABASE CHECK")
    print("="*70)
    
    results = []
    
    # Run checks
    results.append(("Earnings Rates", check_earnings_rates()))
    results.append(("Wallet Transactions", check_wallet_transactions()))
    results.append(("Rider Earnings", check_rider_earnings()))
    results.append(("Orders with Earnings", check_orders_with_earnings()))
    
    # Summary
    print_header("SUMMARY")
    print()
    
    all_passed = True
    for check_name, passed in results:
        status = "(+) PASS" if passed else "(-) FAIL"
        print(f"  {status}  {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("  ALL CHECKS PASSED!")
    else:
        print("  SOME CHECKS FAILED - Review details above")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
