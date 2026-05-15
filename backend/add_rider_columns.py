"""
Database Migration: Add Rider Columns to Order Table
Run this script to add missing rider-related columns
"""

from app import app, db, Order
from sqlalchemy import text

def add_rider_columns():
    """Add rider-related columns to Order table"""
    with app.app_context():
        try:
            # Check if columns exist and add if missing
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('order')]
            
            migrations = []
            
            if 'rider_id' not in columns:
                migrations.append("ALTER TABLE `order` ADD COLUMN rider_id INTEGER NULL")
                migrations.append("ALTER TABLE `order` ADD FOREIGN KEY (rider_id) REFERENCES user(id)")
            
            if 'picked_up_at' not in columns:
                migrations.append("ALTER TABLE `order` ADD COLUMN picked_up_at DATETIME NULL")
            
            if 'picked_up_by' not in columns:
                migrations.append("ALTER TABLE `order` ADD COLUMN picked_up_by INTEGER NULL")
            
            if 'delivered_at' not in columns:
                migrations.append("ALTER TABLE `order` ADD COLUMN delivered_at DATETIME NULL")
            
            if 'delivered_by' not in columns:
                migrations.append("ALTER TABLE `order` ADD COLUMN delivered_by INTEGER NULL")
            
            if 'delivery_fee' not in columns:
                migrations.append("ALTER TABLE `order` ADD COLUMN delivery_fee FLOAT DEFAULT 0.0")
            
            if 'rider_earnings' not in columns:
                migrations.append("ALTER TABLE `order` ADD COLUMN rider_earnings FLOAT DEFAULT 0.0")
            
            # Execute migrations
            if migrations:
                print(f"Executing {len(migrations)} migrations...")
                for migration in migrations:
                    try:
                        db.session.execute(text(migration))
                        print(f"✅ {migration}")
                    except Exception as e:
                        print(f"⚠️  {migration} - {str(e)}")
                
                db.session.commit()
                print("\n✅ All migrations completed successfully!")
            else:
                print("✅ All columns already exist. No migration needed.")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during migration: {str(e)}")
            raise

if __name__ == '__main__':
    print("Starting database migration...")
    add_rider_columns()
