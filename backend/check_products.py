"""
Diagnostic script to check product table and database connection
Run this with: python check_products.py
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

# Load environment variables
load_dotenv()

SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')

print("=" * 60)
print("DATABASE CONNECTION DIAGNOSTIC")
print("=" * 60)

if not SUPABASE_DB_URL:
    print("❌ ERROR: SUPABASE_DB_URL not found in .env file")
    exit(1)

# Mask password in output
masked_url = SUPABASE_DB_URL.split('@')[0].split(':')[:-1]
print(f"✓ Database URL found: {':'.join(masked_url)}:****@...")

try:
    # Create engine
    engine = create_engine(SUPABASE_DB_URL)
    print("✓ SQLAlchemy engine created successfully")
    
    # Test connection
    with engine.connect() as conn:
        print("✓ Database connection successful!")
        
        # Check if product table exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Found {len(tables)} tables in database")
        
        if 'product' in tables:
            print("✓ 'product' table exists")
            
            # Count products
            result = conn.execute(text("SELECT COUNT(*) FROM product"))
            total_count = result.scalar()
            print(f"   Total products: {total_count}")
            
            # Count by status
            result = conn.execute(text("""
                SELECT status, COUNT(*) as count 
                FROM product 
                GROUP BY status
            """))
            print("\n   Products by status:")
            for row in result:
                print(f"   - {row[0]}: {row[1]}")
            
            # Check for approved/active products
            result = conn.execute(text("""
                SELECT COUNT(*) FROM product 
                WHERE status IN ('approved', 'active')
            """))
            approved_count = result.scalar()
            print(f"\n   ✓ Approved/Active products: {approved_count}")
            
            if approved_count == 0:
                print("\n⚠️  WARNING: No approved or active products found!")
                print("   This is why the homepage shows 'No products available'")
                print("\n   SOLUTION: You need to:")
                print("   1. Add products as a seller, OR")
                print("   2. Approve existing pending products as admin, OR")
                print("   3. Run a seed script to populate sample products")
            else:
                # Show sample products
                result = conn.execute(text("""
                    SELECT id, name, status, stock 
                    FROM product 
                    WHERE status IN ('approved', 'active')
                    LIMIT 5
                """))
                print("\n   Sample products:")
                for row in result:
                    print(f"   - ID {row[0]}: {row[1]} (status: {row[2]}, stock: {row[3]})")
        else:
            print("❌ 'product' table does NOT exist")
            print("   You need to run database migrations or create tables")
            
        # Check RLS policies
        print("\n🔒 Checking Row Level Security (RLS)...")
        result = conn.execute(text("""
            SELECT schemaname, tablename, policyname, permissive, roles, cmd
            FROM pg_policies 
            WHERE tablename = 'product'
        """))
        policies = list(result)
        if policies:
            print(f"   Found {len(policies)} RLS policies on 'product' table:")
            for policy in policies:
                print(f"   - {policy[2]} ({policy[5]}): {policy[3]}")
        else:
            print("   ℹ️  No RLS policies found (this is OK for direct connection)")
            
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    print("\nPossible causes:")
    print("1. Database credentials are incorrect")
    print("2. Database server is not accessible")
    print("3. Firewall blocking connection")
    print("4. RLS policies blocking access")

print("\n" + "=" * 60)
