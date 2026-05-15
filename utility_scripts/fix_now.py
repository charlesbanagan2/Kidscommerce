with open('backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}\n")

# Find all product_detail routes
routes = []
for i, line in enumerate(lines):
    if "@app.route('/product/<int:product_id>')" in line:
        routes.append(i)
        print(f"Found route at line {i+1}")

if len(routes) >= 2:
    print(f"\nDuplicate found! Removing second occurrence at line {routes[1]+1}")
    
    # Find the end of the second function
    start_line = routes[1]
    end_line = start_line + 1
    
    # Find next function or route
    for i in range(start_line + 1, len(lines)):
        if lines[i].startswith('@app.route') or lines[i].startswith('if __name__') or lines[i].startswith('socketio.run'):
            end_line = i
            break
    
    # Remove the duplicate
    new_lines = lines[:start_line] + lines[end_line:]
    
    # Write back
    with open('backend/app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Removed lines {start_line+1} to {end_line}")
    print(f"New file has {len(new_lines)} lines (removed {len(lines) - len(new_lines)} lines)")
    print("\nDone! Restart Flask server now.")
else:
    print("No duplicate found")
