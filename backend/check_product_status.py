import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Get all products with their status
response = supabase.table('product').select('id, name, status, stock').limit(10).execute()

print("=" * 80)
print("PRODUCT STATUS CHECK")
print("=" * 80)
for product in response.data:
    print(f"ID: {product['id']:3} | Status: {product['status']:10} | Stock: {product.get('stock', 0):3} | {product['name'][:40]}")
print("=" * 80)
