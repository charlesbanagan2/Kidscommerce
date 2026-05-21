"""
Fix address table - Add missing columns
Run this to fix the 'street_address' column error
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
load_dotenv()

from app import app, db
from sqlalchemy import text

def fix_address_table():
    """Add missing columns to address table"""
    print("\nFixing address table structure...")
    
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Check current columns
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'address'
                    ORDER BY ordinal_position
                """))
                
                current_columns = [row[0] for row in result]
                print(f"\nCurrent columns: {', '.join(current_columns)}")
                
                # Add missing columns
                columns_to_add = {
                    'street_address': 'TEXT',
                    'city': 'TEXT',
                    'province': 'TEXT',
                    'region': 'TEXT',
                    'barangay': 'TEXT',
                    'zip_code': 'TEXT'
                }
                
                print("\nAdding missing columns...")
                for col_name, col_type in columns_to_add.items():
                    if col_name not in current_columns:
                        try:
                            conn.execute(text(f'ALTER TABLE address ADD COLUMN {col_name} {col_type}'))
                            conn.commit()
                            print(f"   [OK] Added: {col_name}")
                        except Exception as e:
                            if 'already exists' in str(e).lower():
                                print(f"   [SKIP] {col_name} already exists")
                            else:
                                print(f"   [ERROR] Error adding {col_name}: {e}")
                    else:
                        print(f"   [OK] {col_name} already exists")
                
                # Verify final structure
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'address'
                    ORDER BY ordinal_position
                """))
                
                print("\nFinal address table structure:")
                for row in result:
                    print(f"   - {row[0]}: {row[1]}")
                
                print("\n[SUCCESS] Address table fixed successfully!")
                
        except Exception as e:
            print(f"\n[ERROR] {e}")
            return False
        
        return True

if __name__ == '__main__':
    fix_address_table()
