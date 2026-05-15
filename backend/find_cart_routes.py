import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
# Find all cart-related routes
patterns = [
    r"@app\.route\('/cart/add.*?\n.*?def\s+(\w+)",
    r"@app\.route\('/api/v1/cart/add.*?\n.*?def\s+(\w+)",
    r"def\s+(add_to_cart|cart_add|buy_now)\(",
]

for pattern in patterns:
    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
    for match in matches:
        # Find line number
        line_num = content[:match.start()].count('\n') + 1
        print(f"Line {line_num}: {match.group(0)[:100]}")
