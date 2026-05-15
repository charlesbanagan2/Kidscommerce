filepath = r'C:\Users\mnban\Documents\kids\backend\app.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find product_detail route
found = False
for i, line in enumerate(lines):
    if "@app.route('/product/<int:product_id>')" in line:
        print(f"Found product_detail at line {i+1}\n")
        print("="*80)
        
        # Print next 80 lines
        for j in range(i, min(i+80, len(lines))):
            print(f"{j+1}: {lines[j].rstrip()}")
        
        print("="*80)
        
        # Save to file
        with open(r'C:\Users\mnban\Documents\kids\current_route.txt', 'w', encoding='utf-8') as f:
            for j in range(i, min(i+100, len(lines))):
                f.write(f"{j+1}: {lines[j]}")
        
        print("\nSaved to current_route.txt")
        found = True
        break

if not found:
    print("product_detail route not found!")
