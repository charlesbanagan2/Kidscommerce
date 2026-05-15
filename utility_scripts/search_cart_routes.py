filepath = r'C:\Users\mnban\Documents\kids\backend\app.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

routes_to_find = ['add_to_cart', 'buy_now', 'add-to-cart-ajax']

for route_name in routes_to_find:
    print(f"\n{'='*70}")
    print(f"Searching for: {route_name}")
    print('='*70)
    
    for i, line in enumerate(lines):
        if f"def {route_name}" in line or f"'{route_name}" in line or f'"{route_name}"' in line:
            print(f"\nFound at line {i+1}:")
            # Show 60 lines
            for j in range(i, min(i+60, len(lines))):
                print(f"{j+1}: {lines[j].rstrip()}")
            break
