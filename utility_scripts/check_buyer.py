#!/usr/bin/env python3
"""Check buyer account in database"""

import sys
import os
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app import app, db
from sqlalchemy import text

with app.app_context():
    result = db.session.execute(
        text("SELECT id, email, password, role, status FROM user WHERE email = 'buyer@test.com'")
    )
    buyer = result.fetchone()
    
    if buyer:
        print("✅ Buyer found in database:")
        print(f"   ID: {buyer[0]}")
        print(f"   Email: {buyer[1]}")
        print(f"   Password hash starts with: {buyer[2][:10] if buyer[2] else 'NULL'}")
        print(f"   Role: {buyer[3]}")
        print(f"   Status: {buyer[4]}")
    else:
        print("❌ Buyer not found")
