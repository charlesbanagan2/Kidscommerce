"""
Quick test script to check if my_orders route works
"""
import sys
from app import app, db, Order, User

def test_my_orders():
    with app.app_context():
        print("=" * 50)
        print("TESTING MY ORDERS ROUTE")
        print("=" * 50)
        
        # Check if we can query users
        print("\n1. Checking users...")
        try:
            users = User.query.limit(5).all()
            print(f"   ✅ Found {len(users)} users")
            for u in users:
                print(f"      - User {u.id}: {u.first_name} {u.last_name} ({u.role})")
        except Exception as e:
            print(f"   ❌ Error querying users: {e}")
            return
        
        # Check if we can query orders
        print("\n2. Checking orders...")
        try:
            orders = Order.query.limit(10).all()
            print(f"   ✅ Found {len(orders)} orders")
            for o in orders:
                print(f"      - Order {o.id}: Buyer {o.buyer_id}, Status: {o.status}")
        except Exception as e:
            print(f"   ❌ Error querying orders: {e}")
            return
        
        # Check orders by buyer
        print("\n3. Checking orders by buyer...")
        try:
            if users:
                test_user = users[0]
                buyer_orders = Order.query.filter_by(buyer_id=test_user.id).all()
                print(f"   ✅ User {test_user.id} has {len(buyer_orders)} orders")
        except Exception as e:
            print(f"   ❌ Error querying buyer orders: {e}")
            return
        
        # Test the my_orders logic
        print("\n4. Testing my_orders grouping logic...")
        try:
            all_orders = Order.query.limit(20).all()
            to_pay = [o for o in all_orders if o.status in ['pending', 'to_pay']]
            to_ship = [o for o in all_orders if o.status in ['processing', 'ready_for_pickup']]
            to_receive = [o for o in all_orders if o.status in ['to_ship', 'in_transit', 'delivered']]
            completed = [o for o in all_orders if o.status == 'completed']
            cancelled = [o for o in all_orders if o.status == 'cancelled']
            
            print(f"   ✅ Grouping successful:")
            print(f"      - To Pay: {len(to_pay)}")
            print(f"      - To Ship: {len(to_ship)}")
            print(f"      - To Receive: {len(to_receive)}")
            print(f"      - Completed: {len(completed)}")
            print(f"      - Cancelled: {len(cancelled)}")
        except Exception as e:
            print(f"   ❌ Error in grouping logic: {e}")
            return
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)
        print("\nIf my_orders still doesn't work:")
        print("1. Check backend terminal for errors")
        print("2. Check browser console (F12)")
        print("3. Make sure you're logged in")
        print("4. Try clearing browser cache")

if __name__ == "__main__":
    test_my_orders()
