"""
Add profile_picture column to user table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

print("="*60)
print("  Adding profile_picture column to user table")
print("="*60)

with app.app_context():
    try:
        # Check if column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'user' 
            AND column_name = 'profile_picture'
        """))
        
        if result.fetchone():
            print("\n[INFO] profile_picture column already exists")
        else:
            print("\n[INFO] Adding profile_picture column...")
            db.session.execute(text("""
                ALTER TABLE "user" 
                ADD COLUMN profile_picture VARCHAR(255)
            """))
            db.session.commit()
            print("[OK] profile_picture column added successfully!")
        
        # Verify
        result = db.session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'user' 
            ORDER BY ordinal_position
        """))
        
        print("\n[INFO] Current user table columns:")
        for row in result.fetchall():
            print(f"  - {row[0]}: {row[1]}")
        
        print("\n" + "="*60)
        print("  SUCCESS!")
        print("="*60)
        
    except Exception as e:
        db.session.rollback()
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
