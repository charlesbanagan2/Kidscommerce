filepath = r'C:\Users\mnban\Documents\kids\backend\app.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find add_to_cart route
for i, line in enumerate(lines):
    if "@app.route('/cart/add" in line or "def add_to_cart" in line:
        print(f"Found at line {i+1}:\n")
        # Show next 50 lines
        for j in range(i, min(i+50, len(lines))):
            print(f"{j+1}: {lines[j].rstrip()}")
        print("\n" + "="*70 + "\n")
        break

# Also find buy_now route
for i, line in enumerate(lines):
    if "def buy_now" in line:
        print(f"Found buy_now at line {i+1}:\n")
        for j in range(i, min(i+50, len(lines))):
            print(f"{j+1}: {lines[j].rstrip()}")
        break
