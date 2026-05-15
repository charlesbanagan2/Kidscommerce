filepath = r'C:\Users\mnban\Documents\kids\backend\app.py'

# Read new route
with open(r'C:\Users\mnban\Documents\kids\new_product_detail_route.txt', 'r', encoding='utf-8') as f:
    new_route = f.read()

# Read app.py
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find existing product_detail route
start = content.find("@app.route('/product/<int:product_id>')")
if start == -1:
    print("Route not found!")
    exit(1)

# Find the end of the function (next @app.route or if __name__)
end = content.find("\n@app.route", start + 50)
if end == -1:
    end = content.find("\nif __name__", start)
if end == -1:
    end = content.find("\nsocketio.run", start)
if end == -1:
    print("Could not find end of function!")
    exit(1)

# Replace
new_content = content[:start] + new_route + "\n\n" + content[end:]

# Backup
with open(filepath + '.backup', 'w', encoding='utf-8') as f:
    f.write(content)

# Write new
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS! product_detail route replaced")
print(f"Backup saved to: {filepath}.backup")
print("\nRestart Flask server now!")
