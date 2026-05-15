filepath = r'C:\Users\mnban\Documents\kids\backend\app.py'

# Read complete route
with open(r'C:\Users\mnban\Documents\kids\complete_product_detail.txt', 'r', encoding='utf-8') as f:
    new_route = f.read()

# Read app.py
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find existing product_detail route
start = content.find("@app.route('/product/<int:product_id>')")
if start == -1:
    print("ERROR: Route not found!")
    exit(1)

print(f"Found route at position {start}")

# Find the end of the function
search_from = start + 100
end = content.find("\n@app.route", search_from)
if end == -1:
    end = content.find("\nif __name__", search_from)
if end == -1:
    end = content.find("\nsocketio.run", search_from)
if end == -1:
    # Try to find next function definition
    end = content.find("\ndef ", search_from)
if end == -1:
    print("ERROR: Could not find end of function!")
    exit(1)

print(f"Function ends at position {end}")

# Replace
new_content = content[:start] + new_route + "\n\n" + content[end:]

# Write
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("\n✓ SUCCESS! Complete product_detail route installed")
print("✓ Includes: available_stock, media_items, avg_rating, reviews")
print("\nRestart Flask server now!")
