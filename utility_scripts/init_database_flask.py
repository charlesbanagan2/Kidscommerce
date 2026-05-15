#!/usr/bin/env python3
"""
Kids E-Commerce Platform - Database Setup (Flask-based)
This version uses Flask's SQLAlchemy to create the database schema.
Requires the Flask backend to be running.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def setup_database():
    """Initialize the database using Flask app context"""
    
    print("\n" + "="*60)
    print("Kids E-Commerce Platform - Database Setup")
    print("="*60 + "\n")
    
    print("This script will:")
    print("  1. Load Flask app configuration")
    print("  2. Create all database tables")
    print("  3. Verify the database setup")
    print()
    
    # Import Flask app
    print("Loading Flask app...", end=" ", flush=True)
    try:
        from app import app, db
        print("✓")
    except Exception as e:
        print(f"✗\nFailed to load Flask app: {e}")
        print("\nMake sure you're in the workspace root directory")
        return False
    
    # Create tables
    print("Creating database tables...", end=" ", flush=True)
    try:
        with app.app_context():
            db.create_all()
        print("✓")
    except Exception as e:
        print(f"✗\nFailed to create tables: {e}")
        return False
    
    # Verify tables
    print("Verifying database setup...", end=" ", flush=True)
    try:
        with app.app_context():
            # Try to count tables
            from sqlalchemy import text, inspect
            
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            table_count = len(tables)
        
        print(f"✓\n")
        print(f"Created {table_count} tables:")
        
        # Show critical tables
        critical_tables = ['user', 'product', 'order', 'cart', 'category']
        for table in tables:
            if table in critical_tables:
                print(f"  ✓ {table}")
        
        return True
        
    except Exception as e:
        print(f"✗\nVerification failed: {e}")
        return False

def show_next_steps():
    print("\n" + "="*60)
    print("✓ DATABASE SETUP COMPLETE")
    print("="*60)
    
    print("\nConnection Details:")
    print("  Database: kids_ecommerce")
    print("  Host: 127.0.0.1:3306")
    print("  User: root")
    print("  Type: MySQL")
    
    print("\nUsed By:")
    print("  ✓ Backend Flask API (http://127.0.0.1:5000)")
    print("  ✓ Mobile App (Flutter)")
    print("  ✓ Website UI")
    print("  ✓ Admin Panel")
    
    print("\nNext Steps:")
    print("\n1. Start the Flask Backend (if not already running):")
    print("   cd backend")
    print("   python app.py")
    
    print("\n2. Build and Run Flutter App:")
    print("   cd mobile_app")
    print("   flutter run")
    
    print("\n3. Access Applications:")
    print("   API:     http://127.0.0.1:5000/api/v1")
    print("   Website: http://127.0.0.1:5000")
    print("   Admin:   http://127.0.0.1:5000/admin")
    print()

if __name__ == "__main__":
    try:
        if setup_database():
            show_next_steps()
        else:
            print("\nDatabase setup failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
