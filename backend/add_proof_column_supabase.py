import os
from dotenv import load_dotenv
import psycopg2

# Load Supabase credentials
load_dotenv('supabase.env')

db_url = os.getenv('SUPABASE_DB_URL')
if not db_url:
    db_user = os.getenv('SUPABASE_DB_USER', 'postgres')
    db_password = os.getenv('SUPABASE_DB_PASSWORD')
    db_host = os.getenv('SUPABASE_DB_HOST')
    db_port = os.getenv('SUPABASE_DB_PORT', '6543')
    db_name = os.getenv('SUPABASE_DB_NAME', 'postgres')
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Add proof_photo_url column
    cursor.execute('ALTER TABLE "order" ADD COLUMN IF NOT EXISTS proof_photo_url TEXT')
    conn.commit()
    
    print("Successfully added proof_photo_url column to order table")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
