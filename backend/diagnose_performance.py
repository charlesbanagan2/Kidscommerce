"""
Database Performance Diagnostic Tool
Run this to check your current Supabase PostgreSQL setup
"""
from app import app, db
from sqlalchemy import text
import time

def check_indexes():
    """Check which indexes exist"""
    print("\n" + "="*60)
    print("CHECKING DATABASE INDEXES")
    print("="*60)
    
    query = text("""
        SELECT 
            tablename, 
            indexname,
            indexdef
        FROM pg_indexes 
        WHERE schemaname = 'public'
        AND tablename IN ('user', 'product', 'order', 'order_item', 'cart', 'notification')
        ORDER BY tablename, indexname;
    """)
    
    with app.app_context():
        result = db.session.execute(query)
        indexes = result.fetchall()
        
        if not indexes:
            print("⚠️  WARNING: No custom indexes found!")
            print("   Run: python add_indexes.py")
        else:
            current_table = None
            for row in indexes:
                if row[0] != current_table:
                    current_table = row[0]
                    print(f"\n📊 Table: {current_table}")
                print(f"   ✓ {row[1]}")
            print(f"\n✓ Total indexes found: {len(indexes)}")

def check_connection_pool():
    """Check connection pool settings"""
    print("\n" + "="*60)
    print("CHECKING CONNECTION POOL SETTINGS")
    print("="*60)
    
    with app.app_context():
        pool = db.engine.pool
        print(f"Pool size: {pool.size()}")
        print(f"Checked out connections: {pool.checkedout()}")
        print(f"Overflow: {pool.overflow()}")
        print(f"Pool timeout: {getattr(pool, '_timeout', 'N/A')}")
        
        if pool.size() < 10:
            print("⚠️  WARNING: Pool size is small. Consider increasing to 20.")

def test_query_performance():
    """Test common query performance"""
    print("\n" + "="*60)
    print("TESTING QUERY PERFORMANCE")
    print("="*60)
    
    with app.app_context():
        # Test 1: Product listing
        start = time.time()
        from app import Product
        products = Product.query.filter_by(status='active').limit(50).all()
        elapsed = time.time() - start
        print(f"\n1. Product listing (50 items): {elapsed:.3f}s")
        if elapsed > 0.5:
            print("   ⚠️  SLOW - Should be < 0.5s")
        else:
            print("   ✓ Good")
        
        # Test 2: Order query
        start = time.time()
        from app import Order
        orders = Order.query.order_by(Order.created_at.desc()).limit(20).all()
        elapsed = time.time() - start
        print(f"\n2. Recent orders (20 items): {elapsed:.3f}s")
        if elapsed > 0.3:
            print("   ⚠️  SLOW - Should be < 0.3s")
        else:
            print("   ✓ Good")
        
        # Test 3: User lookup
        start = time.time()
        from app import User
        user = User.query.filter_by(email='admin@kidscommerce.com').first()
        elapsed = time.time() - start
        print(f"\n3. User email lookup: {elapsed:.3f}s")
        if elapsed > 0.1:
            print("   ⚠️  SLOW - Should be < 0.1s")
        else:
            print("   ✓ Good")

def check_database_stats():
    """Check database statistics"""
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    
    with app.app_context():
        # Count records
        from app import Product, Order, User, Cart
        
        print(f"\nRecord counts:")
        print(f"  Users: {User.query.count()}")
        print(f"  Products: {Product.query.count()}")
        print(f"  Orders: {Order.query.count()}")
        print(f"  Cart items: {Cart.query.count()}")
        
        # Check for missing indexes on large tables
        product_count = Product.query.count()
        if product_count > 100:
            print(f"\n⚠️  You have {product_count} products - indexes are CRITICAL")

def main():
    print("\n" + "="*60)
    print("SUPABASE POSTGRESQL PERFORMANCE DIAGNOSTIC")
    print("="*60)
    
    try:
        check_indexes()
        check_connection_pool()
        check_database_stats()
        test_query_performance()
        
        print("\n" + "="*60)
        print("RECOMMENDATIONS")
        print("="*60)
        print("\n1. If indexes are missing:")
        print("   → Run: python add_indexes.py")
        print("\n2. If queries are slow:")
        print("   → Check PERFORMANCE_OPTIMIZATION.md")
        print("\n3. If connection pool is small:")
        print("   → Already fixed in app.py - restart server")
        print("\n4. If still slow:")
        print("   → Check Supabase Dashboard → Performance")
        print("   → Verify you're using pooled connection string")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Make sure your Flask app is properly configured.")

if __name__ == '__main__':
    main()
