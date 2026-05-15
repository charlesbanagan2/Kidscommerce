import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from sqlalchemy import text

with app.app_context():
    # Check current status
    result = db.session.execute(
        text('SELECT id, email, first_name, last_name, role, status FROM "user" WHERE email = :email AND role = :role'),
        {'email': 'juanrider@gmail.com', 'role': 'rider'}
    ).fetchone()
    
    if result:
        print(f"Found user:")
        print(f"  ID: {result[0]}")
        print(f"  Email: {result[1]}")
        print(f"  Name: {result[2]} {result[3]}")
        print(f"  Role: {result[4]}")
        print(f"  Current Status: {result[5]}")
        
        # Update status to active
        db.session.execute(
            text('UPDATE "user" SET status = :status WHERE email = :email AND role = :role'),
            {'status': 'active', 'email': 'juanrider@gmail.com', 'role': 'rider'}
        )
        db.session.commit()
        
        # Verify update
        updated = db.session.execute(
            text('SELECT status FROM "user" WHERE email = :email'),
            {'email': 'juanrider@gmail.com'}
        ).fetchone()
        
        print(f"\n[OK] Status updated to: {updated[0]}")
        print(f"[OK] User juanrider@gmail.com can now log in!")
    else:
        print("User not found with email juanrider@gmail.com and role rider")
    
    # Show all riders
    print("\n" + "="*70)
    print("All riders in database:")
    print("="*70)
    riders = db.session.execute(
        text('SELECT id, email, first_name, last_name, status FROM "user" WHERE role = :role ORDER BY id'),
        {'role': 'rider'}
    ).fetchall()
    
    for r in riders:
        status_icon = "[OK]" if r[4] == 'active' else "[PENDING]" if r[4] == 'pending' else "[REJECTED]"
        print(f"{status_icon} ID {r[0]}: {r[2]} {r[3]} ({r[1]}) - {r[4]}")
