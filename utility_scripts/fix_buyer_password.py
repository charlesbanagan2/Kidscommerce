#!/usr/bin/env python3
"""Fix buyer account password to use bcrypt"""

import sys
import os
import bcrypt

backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from app import app, db
from sqlalchemy import text

with app.app_context():
    # Generate bcrypt hash
    password = 'password123'
    bcrypt_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print(f"New bcrypt hash: {bcrypt_hash}")
    print()
    
    # Update the password
    db.session.execute(
        text("UPDATE user SET password = :password WHERE email = 'buyer@test.com'"),
        {"password": bcrypt_hash}
    )
    db.session.commit()
    
    print("✅ Password updated to bcrypt format!")
    
    # Verify
    result = db.session.execute(
        text("SELECT password FROM user WHERE email = 'buyer@test.com'")
    )
    new_hash = result.fetchone()[0]
    print(f"✅ Updated password hash: {new_hash[:20]}...")
