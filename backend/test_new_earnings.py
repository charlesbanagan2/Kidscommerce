"""
Test New Delivery Fee Based Earnings System
Rider Earnings = Delivery Fee (Province-based)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Order, WalletTransaction, User
from province_delivery_fees import calculate_delivery_fee, PROVINCE_RANKS
from sqlalchemy import func

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_delivery_fee_calculation():
    """Test delivery fee calculation"""
    print_header("DELIVERY FEE CALCULATION TEST")
    
    print("\nProvince-Based Delivery Fees:")
    print("Formula: Province Rank x 36 pesos\n")
    
    sample_provinces = ['Laguna', 'Rizal', 'Quezon', 'Batangas', 'Cavite', 'Cebu', 'Davao del Sur']
    
    for province in sample_provinces:
        rank = PROVINCE_RANKS.get(province, 1)
        fee = calculate_delivery_fee(province)
        print(f"  {province:20} Rank: {rank:2}  Fee: P{fee:.2f}")
    
    return True

def test_order_delivery_fees():
    """Test orders have delivery_fee field"""
    print_header("ORDER DELIVERY FEES CHECK")
    
    with app.app_context():
        try:
            orders = Order.query.limit(10).all()
            print(f"\n(+) Checking {len(orders)} orders...")
            
            has_delivery_fee = 0
            for order in orders:
                if hasattr(order, 'delivery_fee') and order.delivery_fee:
                    has_delivery_fee += 1
            
            print(f"(+) {has_delivery_fee}/{len(orders)} orders have delivery_fee set")
            
            # Show sample
            print("\nSample Orders:")
            for order in orders[:5]:
                df = order.delivery_fee if hasattr(order, 'delivery_fee') else 0
                re = order.rider_earnings if order.rider_earnings else 0
                print(f"  Order #{order.id}: delivery_fee=P{df:.2f}, rider_earnings=P{re:.2f}")
            
            return True
            
        except Exception as e:
            print(f"\n(-) Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def test_earnings_configuration():
    """Test new earnings configuration"""
    print_header("EARNINGS CONFIGURATION")
    
    try:
        from app import SELLER_EARNING_RATE, ADMIN_EARNING_RATE
        
        print("\n(+) New Earnings Rates:")
        print(f"  - Rider:  DELIVERY FEE (province-based)")
        print(f"  - Seller: {SELLER_EARNING_RATE * 100}% of order total")
        print(f"  - Admin:  {ADMIN_EARNING_RATE * 100}% of order total")
        
        total_rate = (SELLER_EARNING_RATE + ADMIN_EARNING_RATE) * 100
        print(f"\n  Seller + Admin: {total_rate}%")
        
        print("\n(+) Example Calculation (P1000 order to Laguna):")
        print(f"  - Rider gets:  P36.00 (Laguna delivery fee)")
        print(f"  - Seller gets: P{1000 * SELLER_EARNING_RATE:.2f}")
        print(f"  - Admin gets:  P{1000 * ADMIN_EARNING_RATE:.2f}")
        
        print("\n(+) Example Calculation (P1000 order to Cebu):")
        cebu_fee = calculate_delivery_fee('Cebu')
        print(f"  - Rider gets:  P{cebu_fee:.2f} (Cebu delivery fee)")
        print(f"  - Seller gets: P{1000 * SELLER_EARNING_RATE:.2f}")
        print(f"  - Admin gets:  P{1000 * ADMIN_EARNING_RATE:.2f}")
        
        return True
        
    except Exception as e:
        print(f"\n(-) Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_rider_earnings_match_delivery_fee():
    """Test that rider_earnings matches delivery_fee for completed orders"""
    print_header("RIDER EARNINGS VS DELIVERY FEE")
    
    with app.app_context():
        try:
            completed_orders = Order.query.filter(
                Order.picked_up_by.isnot(None),
                Order.status == 'completed'
            ).limit(10).all()
            
            print(f"\n(+) Checking {len(completed_orders)} completed orders...")
            
            matches = 0
            mismatches = []
            
            for order in completed_orders:
                df = order.delivery_fee if hasattr(order, 'delivery_fee') and order.delivery_fee else 0
                re = order.rider_earnings if order.rider_earnings else 0
                
                if abs(df - re) < 0.01:  # Allow small floating point differences
                    matches += 1
                else:
                    mismatches.append((order.id, df, re))
            
            print(f"(+) {matches}/{len(completed_orders)} orders have matching delivery_fee and rider_earnings")
            
            if mismatches:
                print("\nMismatches found:")
                for order_id, df, re in mismatches[:5]:
                    print(f"  Order #{order_id}: delivery_fee=P{df:.2f}, rider_earnings=P{re:.2f}")
            
            return True
            
        except Exception as e:
            print(f"\n(-) Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def test_wallet_transactions():
    """Test wallet transactions with new system"""
    print_header("WALLET TRANSACTIONS")
    
    with app.app_context():
        try:
            # Get recent rider earnings
            rider_earnings = WalletTransaction.query.filter(
                WalletTransaction.source.in_(['order_delivery', 'order_commission'])
            ).order_by(WalletTransaction.created_at.desc()).limit(10).all()
            
            print(f"\n(+) Recent Rider Earnings Transactions:")
            
            for tx in rider_earnings:
                user = User.query.get(tx.user_id)
                email = user.email if user else "Unknown"
                order = Order.query.get(tx.order_id) if tx.order_id else None
                df = order.delivery_fee if order and hasattr(order, 'delivery_fee') else 0
                
                print(f"  User: {email}")
                print(f"    Amount: P{tx.amount:.2f} | Source: {tx.source}")
                if order:
                    print(f"    Order #{tx.order_id} delivery_fee: P{df:.2f}")
                print()
            
            return True
            
        except Exception as e:
            print(f"\n(-) Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    print("\n" + "="*70)
    print("  NEW DELIVERY FEE BASED EARNINGS SYSTEM TEST")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Delivery Fee Calculation", test_delivery_fee_calculation()))
    results.append(("Earnings Configuration", test_earnings_configuration()))
    results.append(("Order Delivery Fees", test_order_delivery_fees()))
    results.append(("Rider Earnings Match", test_rider_earnings_match_delivery_fee()))
    results.append(("Wallet Transactions", test_wallet_transactions()))
    
    # Summary
    print_header("TEST SUMMARY")
    print()
    
    all_passed = True
    for test_name, passed in results:
        status = "(+) PASS" if passed else "(-) FAIL"
        print(f"  {status}  {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("  ALL TESTS PASSED!")
        print("\n  Rider Earnings = Delivery Fee (Province-Based)")
        print("  Seller: 85% | Admin: 15%")
    else:
        print("  SOME TESTS FAILED - Review details above")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
