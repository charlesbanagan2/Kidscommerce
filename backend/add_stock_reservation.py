"""
Add Stock Reservation System
- Adds reserved_stock column to product table
- Creates order_stock_reservation tracking table
- Enables real-time stock management
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def add_stock_reservation_system():
    with app.app_context():
        try:
            print("Adding stock reservation system...")
            
            # Add reserved_stock column to product table
            print("1. Adding reserved_stock column to product table...")
            db.session.execute(text("""
                ALTER TABLE product 
                ADD COLUMN IF NOT EXISTS reserved_stock INTEGER DEFAULT 0
            """))
            
            # Create order_stock_reservation table
            print("2. Creating order_stock_reservation table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS order_stock_reservation (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES "order"(id) ON DELETE CASCADE,
                    product_id INTEGER REFERENCES product(id) ON DELETE CASCADE,
                    quantity INTEGER NOT NULL,
                    reserved_at TIMESTAMP DEFAULT NOW(),
                    released_at TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'active',
                    CONSTRAINT unique_active_reservation UNIQUE (order_id, product_id, status)
                )
            """))
            
            # Create indexes for performance
            print("3. Creating indexes...")
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_reservation_order 
                ON order_stock_reservation(order_id)
            """))
            
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_reservation_product 
                ON order_stock_reservation(product_id)
            """))
            
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_reservation_status 
                ON order_stock_reservation(status)
            """))
            
            # Initialize reserved_stock for existing products
            print("4. Initializing reserved_stock values...")
            db.session.execute(text("""
                UPDATE product 
                SET reserved_stock = 0 
                WHERE reserved_stock IS NULL
            """))
            
            db.session.commit()
            
            print("\n[OK] Stock reservation system installed successfully!")
            print("\nNext steps:")
            print("1. Update app.py with stock reservation logic")
            print("2. Update templates to show available stock")
            print("3. Update mobile app to handle reserved_stock")
            print("4. Restart Flask server")

        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] {e}")
            print("\nIf column already exists, this is normal.")
            return False
        
        return True

if __name__ == '__main__':
    add_stock_reservation_system()
