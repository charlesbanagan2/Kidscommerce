#!/usr/bin/env python3
"""
Check all columns in order table and add missing ones
"""

import os
import psycopg2
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, 'mobile_app', 'lib', 'kids_commercedb', 'supabase.env')
load_dotenv(env_path)

DB_HOST = os.getenv('SUPABASE_DB_HOST')
DB_NAME = os.getenv('SUPABASE_DB_NAME')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')

# Columns from the Order model in app.py
REQUIRED_COLUMNS = [
    'id', 'buyer_id', 'rider_id', 'total_amount', 'status', 
    'payment_method', 'payment_status', 'shipping_address', 
    'stock_deducted', 'return_reason', 'created_at', 'updated_at',
    'coupon_id', 'discount_amount', 'qr_code', 'tracking_number',
    'batch_code', 'label_generated_at', 'packed_at', 'picked_up_at',
    'delivered_at', 'packed_by', 'picked_up_by', 'delivered_by',
    'shipping_notes', 'delivery_notes'
]

def check_and_add_columns():
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, port=DB_PORT, sslmode='require'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Checking order table columns...")
    
    # Get existing columns
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'order'
        ORDER BY column_name
    """)
    existing_columns = {row[0] for row in cursor.fetchall()}
    
    print(f"  Existing columns: {len(existing_columns)}")
    
    # Check for missing columns
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in existing_columns]
    
    if missing_columns:
        print(f"\n  Missing columns: {missing_columns}")
        
        # Add missing columns
        for col in missing_columns:
            print(f"  Adding '{col}'...")
            if col in ['created_at', 'updated_at', 'label_generated_at', 'packed_at', 'picked_up_at', 'delivered_at']:
                cursor.execute(f'ALTER TABLE "order" ADD COLUMN {col} TIMESTAMPTZ;')
            elif col in ['id', 'buyer_id', 'rider_id', 'coupon_id', 'packed_by', 'picked_up_by', 'delivered_by']:
                cursor.execute(f'ALTER TABLE "order" ADD COLUMN {col} INTEGER;')
            elif col in ['total_amount', 'discount_amount']:
                cursor.execute(f'ALTER TABLE "order" ADD COLUMN {col} DECIMAL(10,2);')
            elif col in ['stock_deducted']:
                cursor.execute(f'ALTER TABLE "order" ADD COLUMN {col} BOOLEAN DEFAULT FALSE;')
            elif col in ['status', 'payment_method', 'payment_status']:
                cursor.execute(f'ALTER TABLE "order" ADD COLUMN {col} VARCHAR(50);')
            elif col in ['shipping_address', 'return_reason', 'qr_code', 'tracking_number', 'batch_code', 'shipping_notes', 'delivery_notes']:
                cursor.execute(f'ALTER TABLE "order" ADD COLUMN {col} TEXT;')
            print(f"    Done!")
    else:
        print("  All required columns exist!")
    
    cursor.close()
    conn.close()
    print("\nCheck complete!")

if __name__ == '__main__':
    check_and_add_columns()
