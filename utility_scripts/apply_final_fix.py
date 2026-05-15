filepath = r'C:\Users\mnban\Documents\kids\backend\app.py'

# Read final fixed route
with open(r'C:\Users\mnban\Documents\kids\final_fixed_route.txt', 'r', encoding='utf-8') as f:
    new_route = f.read()

# Read app.py
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find existing product_detail route
start = content.find("@app.route('/product/<int:product_id>')")
if start == -1:
    print("ERROR: Route not found!")
    exit(1)

# Find the end
search_from = start + 100
end = content.find("\n@app.route", search_from)
if end == -1:
    end = content.find("\nif __name__", search_from)
if end == -1:
    end = content.find("\nsocketio.run", search_from)
if end == -1:
    end = content.find("\ndef ", search_from)

if end == -1:
    print("ERROR: Could not find end!")
    exit(1)

# Replace
new_content = content[:start] + new_route + "\n\n" + content[end:]

# Write
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS! Final fixed route installed")
print("\nKey fix: Checks if get_available_stock returns 0")
print("         and uses product.stock as fallback")
print("\nRestart Flask server now!")
