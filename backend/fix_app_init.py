"""
Fix script for app.py - Updates notification API initialization
Run this after the migration completes
"""

import re

def fix_app_py():
    app_py_path = r"c:\Users\mnban\Documents\kids\backend\app.py"
    
    # Read the file
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the old initialization
    old_pattern = r'register_notification_api\(app\)'
    
    # Check if it's already been updated
    if 'register_notification_api(app, db, Notification, User)' in content:
        print("✅ app.py already updated!")
        return True
    
    # Find the line number
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'register_notification_api(app)' in line and 'from' not in line:
            print(f"Found at line {i+1}: {line.strip()}")
            
            # Check if we're before db initialization
            # We need to move this AFTER all models are defined
            
            # Comment out the early call
            lines[i] = '# ' + lines[i] + '  # Moved to after models are defined'
            
            # Find where to add the new call (after all models are defined)
            # Look for "class Notification(db.Model):" or similar
            for j in range(len(lines)-1, -1, -1):
                if 'class Notification(db.Model):' in lines[j]:
                    # Found Notification model, add initialization after it
                    # Find the end of the class (next class or function definition)
                    for k in range(j+1, len(lines)):
                        if lines[k].startswith('class ') or lines[k].startswith('def ') and not lines[k].startswith('    '):
                            # Insert before this line
                            insert_code = """
# Initialize Notification API (after models are defined)
try:
    register_notification_api(app, db, Notification, User)
except Exception as e:
    print(f"[WARNING] Notification API registration: {e}")
"""
                            lines.insert(k, insert_code)
                            print(f"✅ Added new initialization at line {k+1}")
                            break
                    break
            
            break
    
    # Write back
    new_content = '\n'.join(lines)
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ app.py updated successfully!")
    print("\nNext steps:")
    print("1. Run: python migrate_unified_chat.py")
    print("2. Add unified chat initialization to app.py")
    print("3. Restart server: python app.py")
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("FIXING APP.PY - Notification API Initialization")
    print("=" * 60)
    print()
    
    try:
        fix_app_py()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nManual fix needed:")
        print("1. Find line: register_notification_api(app)")
        print("2. Comment it out")
        print("3. After all models are defined, add:")
        print("   register_notification_api(app, db, Notification, User)")
