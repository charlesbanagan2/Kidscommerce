"""
Performance optimization: Add database indexes for Supabase PostgreSQL
Run this once to dramatically improve query performance
"""
import sys
import io
from app import app, db
from sqlalchemy import text

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def add_indexes():
    """Add critical indexes to improve query performance"""

    indexes = [
        # User table indexes
        "CREATE INDEX IF NOT EXISTS idx_user_email ON \"user\"(email);",
        "CREATE INDEX IF NOT EXISTS idx_user_role ON \"user\"(role);",
        "CREATE INDEX IF NOT EXISTS idx_user_status ON \"user\"(status);",

        # Product table indexes
        "CREATE INDEX IF NOT EXISTS idx_product_seller_id ON product(seller_id);",
        "CREATE INDEX IF NOT EXISTS idx_product_status ON product(status);",
        "CREATE INDEX IF NOT EXISTS idx_product_category_id ON product(category_id);",
        "CREATE INDEX IF NOT EXISTS idx_product_status_stock ON product(status, stock);",

        # Order table indexes
        "CREATE INDEX IF NOT EXISTS idx_order_buyer_id ON \"order\"(buyer_id);",
        "CREATE INDEX IF NOT EXISTS idx_order_status ON \"order\"(status);",
        "CREATE INDEX IF NOT EXISTS idx_order_created_at ON \"order\"(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_order_rider_id ON \"order\"(rider_id);",
        "CREATE INDEX IF NOT EXISTS idx_order_picked_up_by ON \"order\"(picked_up_by);",

        # OrderItem table indexes
        "CREATE INDEX IF NOT EXISTS idx_order_item_order_id ON order_item(order_id);",
        "CREATE INDEX IF NOT EXISTS idx_order_item_product_id ON order_item(product_id);",

        # Cart table indexes
        "CREATE INDEX IF NOT EXISTS idx_cart_user_id ON cart(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_cart_product_id ON cart(product_id);",

        # Notification table indexes
        "CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notification(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notification(is_read);",
        "CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notification(created_at DESC);",

        # SellerApplication table indexes
        "CREATE INDEX IF NOT EXISTS idx_seller_application_user_id ON seller_application(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_seller_application_status ON seller_application(status);",

        # Review table indexes
        "CREATE INDEX IF NOT EXISTS idx_review_product_id ON review(product_id);",
        "CREATE INDEX IF NOT EXISTS idx_review_user_id ON review(user_id);",

        # WalletTransaction table indexes
        "CREATE INDEX IF NOT EXISTS idx_wallet_transaction_user_id ON wallet_transaction(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_wallet_transaction_order_id ON wallet_transaction(order_id);",
        "CREATE INDEX IF NOT EXISTS idx_wallet_transaction_created_at ON wallet_transaction(created_at DESC);",

        # Composite indexes for common queries
        "CREATE INDEX IF NOT EXISTS idx_product_status_created ON product(status, created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_order_buyer_status ON \"order\"(buyer_id, status);",
        "CREATE INDEX IF NOT EXISTS idx_notification_user_read ON notification(user_id, is_read);",
        "CREATE INDEX IF NOT EXISTS idx_wallet_user_type_created ON wallet_transaction(user_id, type, created_at DESC);",
    ]

    with app.app_context():
        print("Adding database indexes for performance optimization...")
        success_count = 0
        error_count = 0

        for idx_sql in indexes:
            try:
                db.session.execute(text(idx_sql))
                db.session.commit()
                success_count += 1
                index_name = idx_sql.split('idx_')[1].split(' ON')[0] if 'idx_' in idx_sql else 'unknown'
                print(f"[OK] {index_name}")
            except Exception as e:
                db.session.rollback()
                error_count += 1
                print(f"[ERROR] {str(e)[:100]}")

        print(f"\n[OK] Successfully created {success_count} indexes")
        if error_count > 0:
            print(f"[WARNING] {error_count} indexes failed (may already exist)")
        print("\nPerformance optimization complete!")

if __name__ == '__main__':
    add_indexes()
