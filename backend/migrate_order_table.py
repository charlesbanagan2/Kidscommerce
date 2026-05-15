#!/usr/bin/env python3
"""
Add recipient_name, recipient_phone, and notes columns to order table
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text as _sa_text, inspect as sa_inspect

with app.app_context():
    try:
        inspector = sa_inspect(db.engine)
        cols = {c['name'] for c in inspector.get_columns('order')}
        
        print("Current Order table columns:")
        for col in sorted(cols):
            print(f"  - {col}")
        
        stmts = []
        
        if 'recipient_name' not in cols:
            stmts.append('ALTER TABLE "order" ADD COLUMN recipient_name VARCHAR(255)')
            print("\n[ADDING] recipient_name column")
        else:
            print("\n[SKIP] recipient_name already exists")
        
        if 'recipient_phone' not in cols:
            stmts.append('ALTER TABLE "order" ADD COLUMN recipient_phone VARCHAR(20)')
            print("[ADDING] recipient_phone column")
        else:
            print("[SKIP] recipient_phone already exists")
        
        if 'notes' not in cols:
            stmts.append('ALTER TABLE "order" ADD COLUMN notes TEXT')
            print("[ADDING] notes column")
        else:
            print("[SKIP] notes already exists")
        
        if stmts:
            print(f"\nExecuting {len(stmts)} ALTER TABLE statements...")
            for stmt in stmts:
                print(f"  {stmt}")
                db.session.execute(_sa_text(stmt))
            db.session.commit()
            print("\n[SUCCESS] Database migration completed!")
        else:
            print("\n[INFO] No migration needed - all columns exist")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        sys.exit(1)
