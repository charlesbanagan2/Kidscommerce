import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('SUPABASE_DB_HOST')
DB_NAME = os.getenv('SUPABASE_DB_NAME')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')

print("=" * 60)
print("DIRECT DATABASE TEST - CHECKING ORDERS")
print("=" * 60)
print(f"Host: {DB_HOST}")
print(f"Database: {DB_NAME}")
print(f"User: {DB_USER}")
print()

try:
    # Connect to database
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    
    print("✅ Connected to database!")
    print()
    
    cursor = conn.cursor()
    
    # Test 1: Check if user exists
    print("Test 1: Checking if juanbuyer@gmail.com exists...")
    cursor.execute("""
        SELECT id, email, first_name, last_name, role 
        FROM "user" 
        WHERE email = 'juanbuyer@gmail.com'
    """)
    user = cursor.fetchone()
    
    if user:
        user_id, email, first_name, last_name, role = user
        print(f"✅ User found!")
        print(f"   ID: {user_id}")
        print(f"   Name: {first_name} {last_name}")
        print(f"   Email: {email}")
        print(f"   Role: {role}")
        print()
        
        # Test 2: Count orders for this user
        print(f"Test 2: Counting orders for user_id={user_id}...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM "order" 
            WHERE buyer_id = %s
        """, (user_id,))
        count = cursor.fetchone()[0]
        print(f"✅ Found {count} orders")
        print()
        
        if count > 0:
            # Test 3: Get first 5 orders
            print("Test 3: Fetching first 5 orders...")
            cursor.execute("""
                SELECT id, status, total_amount, created_at, payment_method
                FROM "order" 
                WHERE buyer_id = %s
                ORDER BY created_at DESC
                LIMIT 5
            """, (user_id,))
            orders = cursor.fetchall()
            
            for order in orders:
                order_id, status, total, created_at, payment = order
                print(f"  Order #{order_id}")
                print(f"    Status: {status}")
                print(f"    Total: ₱{total}")
                print(f"    Date: {created_at}")
                print(f"    Payment: {payment}")
                print()
        else:
            print("⚠️ No orders found!")
            print("Possible reasons:")
            print("  1. Orders were deleted")
            print("  2. Wrong buyer_id in orders table")
            print("  3. Orders exist but for different user")
    else:
        print("❌ User not found!")
        print("juanbuyer@gmail.com does not exist in database")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
