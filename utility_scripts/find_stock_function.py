filepath = r'C:\Users\mnban\Documents\kids\backend\app.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find get_available_stock function
for i, line in enumerate(lines):
    if 'def get_available_stock' in line:
        print(f"Found at line {i+1}:\n")
        # Show next 30 lines
        for j in range(i, min(i+30, len(lines))):
            print(f"{j+1}: {lines[j].rstrip()}")
        break
else:
    print("get_available_stock function not found!")
