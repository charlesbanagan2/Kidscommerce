"""Remove duplicate /api/categories endpoints"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find all occurrences of @app.route('/api/categories'
category_route_lines = []
for i, line in enumerate(lines):
    if "@app.route('/api/categories'" in line:
        category_route_lines.append(i)

print(f"Found {len(category_route_lines)} /api/categories endpoints at lines: {category_route_lines}")

if len(category_route_lines) > 1:
    # Keep only the first one, remove the rest
    # We need to find the end of each function and remove them
    
    # Start from the last duplicate and work backwards
    for route_line in reversed(category_route_lines[1:]):
        # Find the end of this function (next @app.route or end of file)
        end_line = len(lines)
        for i in range(route_line + 1, len(lines)):
            if lines[i].startswith('@app.route'):
                end_line = i
                break
        
        # Remove lines from route_line to end_line
        print(f"Removing duplicate from line {route_line} to {end_line}")
        del lines[route_line:end_line]

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Duplicates removed successfully!")
