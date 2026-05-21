"""
Helper script to generate JWT tokens for testing
Run this to get tokens for buyer, seller, and rider users
"""

import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment
load_dotenv('.env')

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL', '').strip().strip('"').strip("'")

def generate_token(user_id, role):
    """Generate a JWT token for a user"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=30)  # 30 day expiration
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token

def get_test_users():
    """Get test users from database"""
    print("Connecting to database...")
    engine = create_engine(SUPABASE_DB_URL)
    
    with engine.connect() as conn:
        # Get one user of each role
        print("\nFetching test users...\n")
        
        roles = ['buyer', 'seller', 'rider']
        tokens = {}
        
        for role in roles:
            result = conn.execute(text(f"""
                SELECT id, first_name, last_name, email, role
                FROM "user"
                WHERE role = :role AND status = 'active'
                LIMIT 1
            """), {'role': role})
            
            user = result.fetchone()
            
            if user:
                user_id, first_name, last_name, email, user_role = user
                token = generate_token(user_id, user_role)
                
                tokens[role] = {
                    'id': user_id,
                    'name': f"{first_name} {last_name}",
                    'email': email,
                    'token': token
                }
                
                print(f"✅ {role.upper()}")
                print(f"   ID: {user_id}")
                print(f"   Name: {first_name} {last_name}")
                print(f"   Email: {email}")
                print(f"   Token: {token}")
                print()
            else:
                print(f"❌ No {role} user found in database")
                print()
        
        return tokens

def print_test_config(tokens):
    """Print configuration for test script"""
    print("\n" + "=" * 70)
    print("COPY THIS TO test_unified_chat_api.py")
    print("=" * 70)
    print("\nTEST_USERS = {")
    
    for role in ['buyer', 'seller', 'rider']:
        if role in tokens:
            print(f"    '{role}': {{")
            print(f"        'id': {tokens[role]['id']},")
            print(f"        'token': '{tokens[role]['token']}',")
            print(f"        'role': '{role}'")
            print(f"    }},")
        else:
            print(f"    '{role}': {{")
            print(f"        'id': None,")
            print(f"        'token': None,  # No {role} user found")
            print(f"        'role': '{role}'")
            print(f"    }},")
    
    print("}")
    print("\n" + "=" * 70)

def get_product_and_order_ids():
    """Get sample product and order IDs"""
    print("\nFetching sample product and order IDs...\n")
    engine = create_engine(SUPABASE_DB_URL)
    
    with engine.connect() as conn:
        # Get a product
        result = conn.execute(text("SELECT id, name FROM product WHERE status = 'active' LIMIT 1"))
        product = result.fetchone()
        
        if product:
            print(f"✅ PRODUCT")
            print(f"   ID: {product[0]}")
            print(f"   Name: {product[1]}")
            print(f"\n   TEST_PRODUCT_ID = {product[0]}")
        else:
            print("❌ No active product found")
            print("   TEST_PRODUCT_ID = 1  # UPDATE THIS")
        
        print()
        
        # Get an order
        result = conn.execute(text('SELECT id, status FROM "order" LIMIT 1'))
        order = result.fetchone()
        
        if order:
            print(f"✅ ORDER")
            print(f"   ID: {order[0]}")
            print(f"   Status: {order[1]}")
            print(f"\n   TEST_ORDER_ID = {order[0]}")
        else:
            print("❌ No order found")
            print("   TEST_ORDER_ID = 1  # UPDATE THIS")

def main():
    print("=" * 70)
    print("JWT TOKEN GENERATOR FOR TESTING")
    print("=" * 70)
    
    if not JWT_SECRET_KEY:
        print("\n❌ ERROR: JWT_SECRET_KEY not found in .env file")
        return
    
    if not SUPABASE_DB_URL:
        print("\n❌ ERROR: SUPABASE_DB_URL not found in .env file")
        return
    
    try:
        tokens = get_test_users()
        get_product_and_order_ids()
        print_test_config(tokens)
        
        print("\n✅ Tokens generated successfully!")
        print("\nNext steps:")
        print("1. Copy the TEST_USERS configuration above")
        print("2. Paste it into test_unified_chat_api.py (replace existing TEST_USERS)")
        print("3. Update TEST_PRODUCT_ID and TEST_ORDER_ID if needed")
        print("4. Run: python test_unified_chat_api.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
