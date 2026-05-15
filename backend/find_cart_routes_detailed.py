import re

# Read the app.py file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find cart-related routes
routes_to_find = [
    r"@app\.route\('/cart/add.*?\ndef\s+\w+.*?(?=@app\.route|if __name__|$)",
    r"@app\.route\('/buy-now.*?\ndef\s+\w+.*?(?=@app\.route|if __name__|$)",
    r"@app\.route\('/api/v1/cart/add.*?\ndef\s+\w+.*?(?=@app\.route|if __name__|$)",
    r"@app\.route\('/api/v1/buy-now.*?\ndef\s+\w+.*?(?=@app\.route|if __name__|$)",
]

print("=" * 80)
print("FOUND CART ROUTES - Need to add duplicate checking")
print("=" * 80)

for pattern in routes_to_find:
    matches = re.finditer(pattern, content, re.DOTALL)
    for match in matches:
        route_code = match.group(0)[:500]  # First 500 chars
        line_num = content[:match.start()].count('\n') + 1
        print(f"\nLine {line_num}:")
        print(route_code)
        print("..." if len(match.group(0)) > 500 else "")
        print("-" * 80)
