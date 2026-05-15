"""Add proof_photo_url column to orders table"""
from app import app, db

with app.app_context():
    try:
        # Add proof_photo_url column
        db.session.execute(db.text("""
            ALTER TABLE "order" 
            ADD COLUMN IF NOT EXISTS proof_photo_url VARCHAR(500);
        """))
        db.session.commit()
        print("[OK] Added proof_photo_url column to orders table")
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] {e}")
