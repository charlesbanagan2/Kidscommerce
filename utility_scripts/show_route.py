with open(r'C:\Users\mnban\Documents\kids\backend\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find product_detail route
for i, line in enumerate(lines):
    if "@app.route('/product/<int:product_id>')" in line:
        # Show 60 lines of the function
        print(f"Found at line {i+1}:\n")
        for j in range(i, min(i+60, len(lines))):
            print(f"{j+1}: {lines[j].rstrip()}")
        
        # Save to file
        with open(r'C:\Users\mnban\Documents\kids\product_detail_route.txt', 'w', encoding='utf-8') as f:
            for j in range(i, min(i+80, len(lines))):
                f.write(f"{j+1}: {lines[j]}")
        
        print("\n\nFull route saved to product_detail_route.txt")
        break
