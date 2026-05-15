filepath = r'C:\Users\mnban\Documents\kids\backend\app.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find product_detail route
for i, line in enumerate(lines):
    if "@app.route('/product/<int:product_id>')" in line:
        print(f"Current product_detail route (starting at line {i+1}):\n")
        print("="*70)
        
        # Show next 70 lines
        for j in range(i, min(i+70, len(lines))):
            print(f"{j+1}: {lines[j].rstrip()}")
        
        print("="*70)
        
        # Check for key fixes
        route_text = ''.join(lines[i:min(i+70, len(lines))])
        
        print("\nChecking for fixes:")
        if 'try:' in route_text and 'get_available_stock' in route_text and 'except:' in route_text:
            print("  [OK] Has try/except for stock calculation")
        else:
            print("  [MISSING] No try/except for stock - will fail!")
        
        if 'clean_img' in route_text or 'replace(' in route_text:
            print("  [OK] Has image path cleaning")
        else:
            print("  [MISSING] No image path cleaning")
        
        if 'media_items' in route_text:
            print("  [OK] Has media_items")
        else:
            print("  [MISSING] No media_items")
        
        break
else:
    print("product_detail route NOT FOUND!")
