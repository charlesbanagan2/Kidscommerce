import os
from supabase import create_client

# Supabase credentials
SUPABASE_URL = "https://ykgwqdboucsiaedgtivx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlrZ3dxZGJvdWNzaWFlZGd0aXZ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU1NzU5NzksImV4cCI6MjA2MTE1MTk3OX0.Ql-Uw-Ql-Uw-Ql-Uw-Ql-Uw-Ql-Uw-Ql-Uw-Ql-Uw"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Query for the user
    response = supabase.table('user').select('*').eq('email', 'juanrider@gmail.com').execute()
    
    if response.data:
        user = response.data[0]
        print("✓ User found in Supabase!")
        print(f"ID: {user.get('id')}")
        print(f"Email: {user.get('email')}")
        print(f"Password: {user.get('password')}")
        print(f"Role: {user.get('role')}")
        print(f"Status: {user.get('status')}")
        print(f"Password starts with $2b$: {user.get('password', '').startswith('$2b$')}")
    else:
        print("✗ User NOT found in Supabase database!")
        print("The user exists in local SQLite but not in Supabase.")
        
except Exception as e:
    print(f"Error: {e}")
