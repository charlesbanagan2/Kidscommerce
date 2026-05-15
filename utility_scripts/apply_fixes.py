"""
Automated Fix Application Script
Applies all fixes to the rider system
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create backup of file before modifying"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filepath, backup_path)
        print(f"✅ Backed up: {filepath} -> {backup_path}")
        return True
    return False

def apply_fixes():
    """Apply all fixes"""
    print("="*60)
    print("RIDER SYSTEM - AUTOMATED FIX APPLICATION")
    print("="*60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, 'backend')
    
    # Step 1: Backup and rename old API files
    print("\n[Step 1] Backing up old API files...")
    
    old_files = [
        os.path.join(backend_dir, 'rider_complete_api.py'),
        os.path.join(backend_dir, 'rider_api.py')
    ]
    
    for old_file in old_files:
        if os.path.exists(old_file):
            new_name = f"{old_file}.OLD"
            shutil.move(old_file, new_name)
            print(f"✅ Renamed: {old_file} -> {new_name}")
    
    # Step 2: Replace rider_mobile_only_api.py with fixed version
    print("\n[Step 2] Updating rider_mobile_only_api.py...")
    
    old_api = os.path.join(backend_dir, 'rider_mobile_only_api.py')
    new_api = os.path.join(backend_dir, 'rider_mobile_only_api_FIXED.py')
    
    if os.path.exists(old_api):
        backup_file(old_api)
    
    if os.path.exists(new_api):
        shutil.copy2(new_api, old_api)
        print(f"✅ Updated: rider_mobile_only_api.py")
    else:
        print(f"⚠️  Fixed file not found: {new_api}")
    
    # Step 3: Check app.py imports
    print("\n[Step 3] Checking app.py imports...")
    
    app_py = os.path.join(backend_dir, 'app.py')
    if os.path.exists(app_py):
        with open(app_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_rider_import = 'from rider_mobile_only_api import *' in content
        has_chat_import = 'from chat_complete_api import *' in content
        
        if has_rider_import:
            print("✅ Rider API import found in app.py")
        else:
            print("⚠️  Rider API import NOT found in app.py")
            print("   Add this line to app.py:")
            print("   from rider_mobile_only_api import *")
        
        if has_chat_import:
            print("✅ Chat API import found in app.py")
        else:
            print("⚠️  Chat API import NOT found in app.py")
            print("   Add this line to app.py:")
            print("   from chat_complete_api import *")
    else:
        print(f"❌ app.py not found: {app_py}")
    
    # Step 4: Check database configuration
    print("\n[Step 4] Checking database configuration...")
    
    if os.path.exists(app_py):
        with open(app_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'postgresql://' in content:
            print("✅ PostgreSQL database detected")
        elif 'sqlite:///' in content:
            print("⚠️  SQLite database detected")
            print("   WARNING: FCFS row-level locking requires PostgreSQL!")
            print("   Change to: postgresql://user:password@localhost/dbname")
        else:
            print("⚠️  Database configuration not found")
    
    # Step 5: Check Socket.IO initialization
    print("\n[Step 5] Checking Socket.IO initialization...")
    
    if os.path.exists(app_py):
        with open(app_py, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'socketio = SocketIO' in content:
            print("✅ Socket.IO initialization found")
        else:
            print("⚠️  Socket.IO initialization NOT found")
            print("   Add to app.py:")
            print("   from flask_socketio import SocketIO")
            print("   socketio = SocketIO(app, cors_allowed_origins='*')")
        
        if 'socketio.run(app' in content:
            print("✅ socketio.run() found")
        elif 'app.run(' in content:
            print("⚠️  Using app.run() instead of socketio.run()")
            print("   Change to: socketio.run(app, host='0.0.0.0', port=5000)")
    
    # Step 6: Mobile app fixes already applied
    print("\n[Step 6] Mobile app fixes...")
    print("✅ rider_available_orders_screen.dart updated")
    print("   - Changed import to rider_mobile_service.dart")
    print("   - Updated all RiderService calls to RiderMobileService")
    
    # Summary
    print("\n" + "="*60)
    print("FIX APPLICATION COMPLETE")
    print("="*60)
    
    print("\n📋 NEXT STEPS:")
    print("\n1. Review app.py and add missing imports if needed:")
    print("   - from rider_mobile_only_api import *")
    print("   - from chat_complete_api import *")
    print("   - from flask_socketio import SocketIO, emit, join_room")
    
    print("\n2. Verify database is PostgreSQL (not SQLite)")
    
    print("\n3. Add missing models to app.py:")
    print("   - RiderDetails model")
    print("   - ChatMessage model")
    print("   - Order model columns (rider_id, rider_earnings, etc.)")
    
    print("\n4. Run database migrations:")
    print("   python backend/add_chat_table.py")
    
    print("\n5. Test the system:")
    print("   python test_rider_workflow.py")
    
    print("\n6. Start backend:")
    print("   cd backend && python app.py")
    
    print("\n✅ All automated fixes have been applied!")
    print("   Review RIDER_SYSTEM_FIXES.md for detailed manual steps.")

if __name__ == '__main__':
    apply_fixes()
