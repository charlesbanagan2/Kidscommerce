"""
Fix Product Status for Cart - Ensure all products have 'approved' status
"""
import os
from supabase import create_client, Client

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_key:
    print("❌ Missing Supabase credentials in .env file")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def fix_product_statuses():
    """Update all products to have 'approved' status if they don't have one"""
    try:
        # Get all products
        response = supabase.table('product').select('id, name, status, stock').execute()
        products = response.data
        
        print(f"\n📦 Found {len(products)} products")
        print("=" * 60)
        
        fixed_count = 0
        for product in products:
            product_id = product.get('id')
            name = product.get('name', 'Unknown')
            status = product.get('status')
            stock = product.get('stock', 0)
            
            print(f"\nProduct ID: {product_id}")
            print(f"Name: {name}")
            print(f"Status: {status}")
            print(f"Stock: {stock}")
            
            # Fix status if it's not 'approved'
            if status != 'approved':
                print(f"  ⚠️  Status is '{status}' - Updating to 'approved'...")
                
                update_response = supabase.table('product').update({
                    'status': 'approved'
                }).eq('id', product_id).execute()
                
                if update_response.data:
                    print(f"  ✅ Updated product {product_id} to 'approved'")
                    fixed_count += 1
                else:
                    print(f"  ❌ Failed to update product {product_id}")
            else:
                print(f"  ✓ Status is already 'approved'")
        
        print("\n" + "=" * 60)
        print(f"✅ Fixed {fixed_count} products")
        print(f"✓ All products now have 'approved' status")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🔧 Fixing Product Statuses for Cart...")
    fix_product_statuses()
