import sys

filepath = r'C:\Users\mnban\Documents\kids\backend\app.py'

try:
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    
    # Find all @app.route('/product/<int:product_id>')
    found = []
    for i, line in enumerate(lines):
        if "@app.route('/product/<int:product_id>')" in line:
            found.append(i)
            print(f"Route found at line {i+1}: {line.strip()}")
    
    if len(found) < 2:
        print("\nNo duplicate found!")
        sys.exit(0)
    
    print(f"\nDuplicate detected! Will remove second occurrence at line {found[1]+1}")
    
    # Find end of second function (look for next @app.route or if __name__)
    start = found[1]
    end = start + 1
    
    for i in range(start + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith('@app.route') or stripped.startswith('if __name__') or stripped.startswith('socketio.run'):
            end = i
            break
        if i == len(lines) - 1:
            end = len(lines)
    
    print(f"Removing lines {start+1} to {end}")
    print(f"\nPreview of removed content:")
    print("="*60)
    for i in range(start, min(start+10, end)):
        print(f"{i+1}: {lines[i].rstrip()}")
    print("="*60)
    
    # Create new content
    new_lines = lines[:start] + lines[end:]
    
    # Backup original
    with open(filepath + '.backup', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"\nBackup saved to: {filepath}.backup")
    
    # Write fixed version
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\nSUCCESS! Removed {len(lines) - len(new_lines)} lines")
    print(f"New file: {len(new_lines)} lines")
    print("\nNow restart your Flask server!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
