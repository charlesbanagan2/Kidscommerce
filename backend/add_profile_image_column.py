"""
Add profile_image column to user table
"""
from app import app, db
from sqlalchemy import text

def add_profile_image_column():
    with app.app_context():
        try:
            # Check if column exists
            result = db.session.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'user' AND column_name = 'profile_image'"
            ))
            if result.fetchone():
                print("[INFO] profile_image column already exists")
                return
            
            # Add the column
            db.session.execute(text(
                "ALTER TABLE \"user\" ADD COLUMN profile_image VARCHAR(255)"
            ))
            db.session.commit()
            print("[OK] Added profile_image column to user table")
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Failed to add profile_image column: {e}")

if __name__ == '__main__':
    add_profile_image_column()
