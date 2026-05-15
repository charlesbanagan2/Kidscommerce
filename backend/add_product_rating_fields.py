"""
Migration script to add rating and review_count fields to Product table
and populate them with existing review data.
"""

from app import app, db, Product, Review
from sqlalchemy import text, func

def add_product_rating_fields():
    """Add rating and review_count columns to product table"""
    with app.app_context():
        try:
            # Add columns if they don't exist
            with db.engine.connect() as conn:
                # Check if columns exist
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='product' 
                    AND column_name IN ('rating', 'review_count')
                """))
                existing_columns = {row[0] for row in result}
                
                # Add rating column if it doesn't exist
                if 'rating' not in existing_columns:
                    print("Adding 'rating' column to product table...")
                    conn.execute(text("""
                        ALTER TABLE product 
                        ADD COLUMN rating FLOAT DEFAULT 0.0
                    """))
                    conn.commit()
                    print("[OK] Added 'rating' column")
                else:
                    print("[INFO] 'rating' column already exists")
                
                # Add review_count column if it doesn't exist
                if 'review_count' not in existing_columns:
                    print("Adding 'review_count' column to product table...")
                    conn.execute(text("""
                        ALTER TABLE product 
                        ADD COLUMN review_count INTEGER DEFAULT 0
                    """))
                    conn.commit()
                    print("[OK] Added 'review_count' column")
                else:
                    print("[INFO] 'review_count' column already exists")
            
            # Now populate the fields with existing review data
            print("\nCalculating ratings from existing reviews...")
            products = Product.query.all()
            updated_count = 0
            
            for product in products:
                # Calculate average rating
                avg_rating = db.session.query(func.avg(Review.rating)).filter(
                    Review.product_id == product.id,
                    Review.status == 'published'
                ).scalar() or 0.0
                
                # Count reviews
                review_count = db.session.query(func.count(Review.id)).filter(
                    Review.product_id == product.id,
                    Review.status == 'published'
                ).scalar() or 0
                
                # Update product if there are reviews
                if review_count > 0:
                    with db.engine.connect() as conn:
                        conn.execute(
                            text("UPDATE product SET rating = :rating, review_count = :count WHERE id = :id"),
                            {'rating': float(avg_rating), 'count': review_count, 'id': product.id}
                        )
                        conn.commit()
                    updated_count += 1
                    print(f"  Product #{product.id} ({product.name}): {avg_rating:.1f} stars ({review_count} reviews)")
            
            print(f"\n[OK] Migration complete! Updated {updated_count} products with review data.")
            
        except Exception as e:
            print(f"[ERROR] Error during migration: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("Product Rating Fields Migration")
    print("=" * 60)
    add_product_rating_fields()
