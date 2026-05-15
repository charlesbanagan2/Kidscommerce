#!/usr/bin/env python3
"""Debug registration error"""

import sys
import os
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app import app, db
from sqlalchemy import text
import bcrypt
import traceback

with app.app_context():
    try:
        # Hash password
        password = 'password123'
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Try to insert buyer
        db.session.execute(
            text("""
                INSERT INTO user (email, password, first_name, last_name, phone, role, status)
                VALUES (:email, :password, :first_name, :last_name, :phone, :role, :status)
            """),
            {
                "email": "debug.buyer@test.com",
                "password": hashed,
                "first_name": "Debug",
                "last_name": "Buyer",
                "phone": "+1234567890",
                "role": "buyer",
                "status": "active"
            }
        )
        db.session.commit()
        
        print("✅ Direct INSERT successful!")
        
        # Verify
        result = db.session.execute(
            text("SELECT id, email, role FROM user WHERE email = 'debug.buyer@test.com'")
        )
        user = result.fetchone()
        if user:
            print(f"✅ User verified: {user}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        db.session.rollback()
