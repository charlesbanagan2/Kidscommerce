"""
Patch script to fix app.py initialization order
"""

def patch_app_py():
    app_path = r"c:\Users\mnban\Documents\kids\backend\app.py"
    
    with open(app_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and comment out line 88
    for i, line in enumerate(lines):
        if i == 87:  # Line 88 (0-indexed)
            if 'register_notification_api(app)' in line:
                lines[i] = '# MOVED: ' + line
                print("OK: Commented out line 88")
                break
    
    # Find where to add the proper initialization (after Notification model)
    for i, line in enumerate(lines):
        if 'class Notification(db.Model):' in line:
            # Find end of Notification class
            indent_level = len(line) - len(line.lstrip())
            for j in range(i+1, len(lines)):
                current_line = lines[j].strip()
                if current_line and not lines[j].startswith(' ' * (indent_level + 1)):
                    # Found end of class, insert here
                    insert_code = """
# Initialize Notification and Chat APIs (after models are defined)
try:
    register_notification_api(app, db, Notification, User)
    print("[OK] Notification API initialized")
except Exception as e:
    print(f"[ERROR] Notification API: {e}")

try:
    from unified_chat_api import register_unified_chat
    register_unified_chat(app, db, socketio)
    print("[OK] Unified Chat initialized")
except Exception as e:
    print(f"[ERROR] Unified Chat: {e}")

"""
                    lines.insert(j, insert_code)
                    print(f"OK: Added initialization at line {j+1}")
                    break
            break
    
    with open(app_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("OK: app.py patched successfully!")

if __name__ == '__main__':
    print("=" * 60)
    print("PATCHING APP.PY")
    print("=" * 60)
    patch_app_py()
    print("\nDone! Now run: python app.py")
