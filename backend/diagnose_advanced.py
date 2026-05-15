"""
Advanced Performance Diagnostic - Find the Real Bottleneck
"""
from app import app, db
from sqlalchemy import text
import time
import sys

def test_connection_speed():
    """Test raw connection speed to Supabase"""
    print("\n" + "="*60)
    print("1. TESTING DATABASE CONNECTION SPEED")
    print("="*60)
    
    with app.app_context():
        # Test 1: Simple query
        start = time.time()
        result = db.session.execute(text("SELECT 1"))
        result.fetchone()
        elapsed = time.time() - start
        print(f"\nSimple SELECT 1: {elapsed*1000:.1f}ms")
        
        if elapsed > 0.1:
            print("⚠️  HIGH LATENCY - Network/connection issue")
            print("   → Check if using pooled connection string (:6543)")
            print("   → Check Supabase region (should be close to you)")
        else:
            print("✓ Connection speed is good")
        
        # Test 2: Count query
        start = time.time()
        result = db.session.execute(text("SELECT COUNT(*) FROM product"))
        count = result.fetchone()[0]
        elapsed = time.time() - start
        print(f"\nCOUNT(*) on product table: {elapsed*1000:.1f}ms ({count} products)")
        
        if elapsed > 0.2:
            print("⚠️  SLOW - Possible missing index or large table")
        else:
            print("✓ Count query is fast")

def test_orm_queries():
    """Test SQLAlchemy ORM query performance"""
    print("\n" + "="*60)
    print("2. TESTING ORM QUERY PERFORMANCE")
    print("="*60)
    
    with app.app_context():
        from app import Product, User, Order
        
        # Test 1: Product query with relationships (N+1 problem?)
        print("\n📦 Testing Product.query.filter_by(status='active').all()...")
        start = time.time()
        products = Product.query.filter_by(status='active').limit(20).all()
        query_time = time.time() - start
        
        # Now access relationships (this might trigger N+1)
        start = time.time()
        for p in products:
            _ = p.seller.first_name  # Access seller relationship
            _ = p.category.name      # Access category relationship
        relationship_time = time.time() - start
        
        total_time = query_time + relationship_time
        print(f"   Query time: {query_time*1000:.1f}ms")
        print(f"   Relationship access: {relationship_time*1000:.1f}ms")
        print(f"   TOTAL: {total_time*1000:.1f}ms")
        
        if relationship_time > query_time:
            print("   ⚠️  N+1 PROBLEM DETECTED!")
            print("   → Relationships are loaded lazily (extra queries per item)")
            print("   → Solution: Use joinedload() for eager loading")
        
        # Test 2: Order query
        print("\n📋 Testing Order.query.order_by(created_at.desc()).all()...")
        start = time.time()
        orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        query_time = time.time() - start
        
        start = time.time()
        for o in orders:
            _ = o.buyer.first_name
            _ = len(o.items)  # Access order items
        relationship_time = time.time() - start
        
        total_time = query_time + relationship_time
        print(f"   Query time: {query_time*1000:.1f}ms")
        print(f"   Relationship access: {relationship_time*1000:.1f}ms")
        print(f"   TOTAL: {total_time*1000:.1f}ms")
        
        if relationship_time > query_time * 2:
            print("   ⚠️  N+1 PROBLEM DETECTED!")

def test_index_usage():
    """Check if indexes are being used"""
    print("\n" + "="*60)
    print("3. CHECKING INDEX USAGE")
    print("="*60)
    
    with app.app_context():
        # Test if product status index is used
        query = text("""
            EXPLAIN (FORMAT JSON) 
            SELECT * FROM product WHERE status = 'active' LIMIT 20
        """)
        result = db.session.execute(query)
        plan = result.fetchone()[0]
        
        print("\nQuery plan for: SELECT * FROM product WHERE status = 'active'")
        
        # Check if index scan is used
        plan_str = str(plan)
        if 'Index Scan' in plan_str or 'Bitmap Index Scan' in plan_str:
            print("✓ Using index scan (GOOD)")
        elif 'Seq Scan' in plan_str:
            print("⚠️  Using sequential scan (BAD - index not being used)")
            print("   → Indexes exist but PostgreSQL chose not to use them")
            print("   → Possible reasons: table too small, outdated statistics")
        
        # Show actual plan
        import json
        print("\nDetailed plan:")
        print(json.dumps(plan, indent=2)[:500] + "...")

def check_table_statistics():
    """Check if table statistics are up to date"""
    print("\n" + "="*60)
    print("4. CHECKING TABLE STATISTICS")
    print("="*60)
    
    with app.app_context():
        query = text("""
            SELECT 
                schemaname,
                tablename,
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze,
                n_live_tup as row_count
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
            AND tablename IN ('product', 'order', 'user', 'order_item')
            ORDER BY tablename;
        """)
        
        result = db.session.execute(query)
        stats = result.fetchall()
        
        print("\nTable statistics:")
        for row in stats:
            print(f"\n📊 {row[1]}:")
            print(f"   Rows: {row[6]}")
            print(f"   Last analyze: {row[4] or 'Never'}")
            
            if row[4] is None:
                print("   ⚠️  NEVER ANALYZED - Statistics are missing!")
                print("   → Run: ANALYZE " + row[1])

def check_connection_pool_status():
    """Check current connection pool status"""
    print("\n" + "="*60)
    print("5. CONNECTION POOL STATUS")
    print("="*60)
    
    with app.app_context():
        pool = db.engine.pool
        print(f"\nPool configuration:")
        print(f"   Size: {pool.size()}")
        print(f"   Checked out: {pool.checkedout()}")
        print(f"   Overflow: {pool.overflow()}")
        print(f"   Max overflow: {getattr(pool, '_max_overflow', 'N/A')}")
        
        # Check active connections in database
        query = text("""
            SELECT count(*) as active_connections
            FROM pg_stat_activity
            WHERE datname = current_database()
            AND state = 'active';
        """)
        result = db.session.execute(query)
        active = result.fetchone()[0]
        print(f"   Active DB connections: {active}")
        
        if active > 50:
            print("   ⚠️  HIGH CONNECTION COUNT - May hit limits")

def check_slow_queries():
    """Check for slow queries in pg_stat_statements"""
    print("\n" + "="*60)
    print("6. CHECKING FOR SLOW QUERIES")
    print("="*60)
    
    with app.app_context():
        try:
            query = text("""
                SELECT 
                    LEFT(query, 100) as query_preview,
                    calls,
                    ROUND(mean_exec_time::numeric, 2) as avg_ms,
                    ROUND(total_exec_time::numeric, 2) as total_ms
                FROM pg_stat_statements
                WHERE query NOT LIKE '%pg_stat_statements%'
                ORDER BY mean_exec_time DESC
                LIMIT 5;
            """)
            result = db.session.execute(query)
            slow_queries = result.fetchall()
            
            if slow_queries:
                print("\nTop 5 slowest queries:")
                for i, row in enumerate(slow_queries, 1):
                    print(f"\n{i}. {row[0]}...")
                    print(f"   Calls: {row[1]}, Avg: {row[2]}ms, Total: {row[3]}ms")
                    
                    if row[2] > 100:
                        print(f"   ⚠️  VERY SLOW (avg {row[2]}ms)")
            else:
                print("\n✓ No slow queries found")
                
        except Exception as e:
            print(f"\n⚠️  pg_stat_statements not available")
            print("   (This is normal - requires Supabase Pro or manual setup)")

def main():
    print("\n" + "="*60)
    print("ADVANCED PERFORMANCE DIAGNOSTIC")
    print("Finding the Real Bottleneck...")
    print("="*60)
    
    try:
        test_connection_speed()
        test_orm_queries()
        test_index_usage()
        check_table_statistics()
        check_connection_pool_status()
        check_slow_queries()
        
        print("\n" + "="*60)
        print("DIAGNOSIS COMPLETE")
        print("="*60)
        print("\nMost Common Issues Found:")
        print("1. N+1 Query Problem - Use joinedload()")
        print("2. High Network Latency - Use pooled connection")
        print("3. Missing Statistics - Run ANALYZE on tables")
        print("4. Sequential Scans - Tables too small for indexes")
        print("\nSee recommendations above for specific fixes.")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
