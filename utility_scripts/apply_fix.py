filepath = r'C:\Users\mnban\Documents\kids\backend\app.py'

# Read new route
with open(r'C:\Users\mnban\Documents\kids\fixed_product_detail_route.txt', 'r', encoding='utf-8') as f:
    new_route = f.read()

# Read app.py
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find existing product_detail route
start = content.find("@app.route('/product/<int:product_id>')")
if start == -1:
    print("Route not found!")
    exit(1)

print(f"Found route at position {start}")

# Find the end of the function (next @app.route or if __name__)
search_from = start + 100
end = content.find("\n@app.route", search_from)
if end == -1:
    end = content.find("\nif __name__", search_from)
if end == -1:
    end = content.find("\nsocketio.run", search_from)
if end == -1:
    print("Could not find end of function!")
    exit(1)

print(f"Function ends at position {end}")

# Replace
new_content = content[:start] + new_route + "\n\n" + content[end:]

# Write new
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("\nSUCCESS! product_detail route replaced (no joinedload)")
print("Restart Flask server now!")
