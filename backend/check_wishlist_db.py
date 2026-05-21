"""
Quick Database Check for Wishlist Data
Verifies wishlist table structure and data
"""

import sqlite3
import os
from datetime import datetime

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def log(message, color=RESET):
    """Print colored message"""
    print(f"{color}{message}{RESET}")

def check_database():
    """Check wishlist database structure and data"""
    
    # Find database file
    db_paths = [
        'instance/kids_marketplace.db',
        'kids_marketplace.db',
        '../instance/kids_marketplace.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        log("❌ Database file not found!", RED)
        log(f"Searched in: {db_paths}", YELLOW)
        return
    
    log(f"\n✅ Found database: {db_path}", GREEN)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if wishlist table exists
        log("\n" + "=" * 60, BLUE)
        log("📋 Checking Wishlist Table Structure", BLUE)
        log("=" * 60, BLUE)
        
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='wishlist'
        """)
        
        result = cursor.fetchone()
        if result:
            log("\n✅ Wishlist table exists", GREEN)
            log("\nTable Schema:", YELLOW)
            log(result[0])
        else:
            log("\n❌ Wishlist table does not exist!", RED)
            return
        
        # Get table info
        cursor.execute("PRAGMA table_info(wishlist)")
        columns = cursor.fetchall()
        
        log("\n" + "-" * 60, BLUE)
        log("Columns:", YELLOW)
        for col in columns:
            log(f"  • {col[1]} ({col[2]}) {'NOT NULL' if col[3] else ''} {'PRIMARY KEY' if col[5] else ''}")
        
        # Count total wishlist items
        log("\n" + "=" * 60, BLUE)
        log("📊 Wishlist Data Statistics", BLUE)
        log("=" * 60, BLUE)
        
        cursor.execute("SELECT COUNT(*) FROM wishlist")
        total_items = cursor.fetchone()[0]
        log(f"\nTotal wishlist items: {total_items}", GREEN if total_items > 0 else YELLOW)
        
        # Count items per user
        cursor.execute("""
            SELECT u.email, COUNT(w.id) as item_count
            FROM user u
            LEFT JOIN wishlist w ON u.id = w.user_id
            WHERE u.role = 'buyer'
            GROUP BY u.id, u.email
            HAVING item_count > 0
            ORDER BY item_count DESC
        """)
        
        user_counts = cursor.fetchall()
        if user_counts:
            log("\nWishlist items per user:", YELLOW)
            for email, count in user_counts:
                log(f"  • {email}: {count} items", GREEN)
        else:
            log("\nNo users have wishlist items yet", YELLOW)
        
        # Show recent wishlist items
        log("\n" + "=" * 60, BLUE)
        log("📦 Recent Wishlist Items (Last 10)", BLUE)
        log("=" * 60, BLUE)
        
        cursor.execute("""
            SELECT 
                w.id,
                u.email,
                p.name as product_name,
                w.created_at
            FROM wishlist w
            JOIN user u ON w.user_id = u.id
            JOIN product p ON w.product_id = p.id
            ORDER BY w.created_at DESC
            LIMIT 10
        """)
        
        recent_items = cursor.fetchall()
        if recent_items:
            log("")
            for item_id, email, product_name, created_at in recent_items:
                log(f"  [{item_id}] {email} → {product_name}", GREEN)
                log(f"      Added: {created_at}", YELLOW)
        else:
            log("\nNo wishlist items found", YELLOW)
        
        # Check for orphaned records
        log("\n" + "=" * 60, BLUE)
        log("🔍 Data Integrity Check", BLUE)
        log("=" * 60, BLUE)
        
        # Check for wishlist items with deleted products
        cursor.execute("""
            SELECT COUNT(*) FROM wishlist w
            LEFT JOIN product p ON w.product_id = p.id
            WHERE p.id IS NULL
        """)
        orphaned_products = cursor.fetchone()[0]
        
        if orphaned_products > 0:
            log(f"\n⚠️ Found {orphaned_products} wishlist items with deleted products", YELLOW)
        else:
            log("\n✅ No orphaned product references", GREEN)
        
        # Check for wishlist items with deleted users
        cursor.execute("""
            SELECT COUNT(*) FROM wishlist w
            LEFT JOIN user u ON w.user_id = u.id
            WHERE u.id IS NULL
        """)
        orphaned_users = cursor.fetchone()[0]
        
        if orphaned_users > 0:
            log(f"⚠️ Found {orphaned_users} wishlist items with deleted users", YELLOW)
        else:
            log("✅ No orphaned user references", GREEN)
        
        # Check for duplicates
        cursor.execute("""
            SELECT user_id, product_id, COUNT(*) as count
            FROM wishlist
            GROUP BY user_id, product_id
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()
        
        if duplicates:
            log(f"\n⚠️ Found {len(duplicates)} duplicate entries:", YELLOW)
            for user_id, product_id, count in duplicates:
                log(f"  • User {user_id}, Product {product_id}: {count} entries", RED)
        else:
            log("✅ No duplicate entries", GREEN)
        
        conn.close()
        
        log("\n" + "=" * 60, BLUE)
        log("✅ Database check completed!", GREEN)
        log("=" * 60, BLUE)
        
    except sqlite3.Error as e:
        log(f"\n❌ Database error: {e}", RED)
    except Exception as e:
        log(f"\n❌ Error: {e}", RED)

if __name__ == "__main__":
    log("\n" + "=" * 60, BLUE)
    log("🔍 Wishlist Database Checker", BLUE)
    log("=" * 60, BLUE)
    log(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", YELLOW)
    
    check_database()
    
    print()
