#!/usr/bin/env python3
"""Fix API endpoint to use product.stock instead of get_available_stock()"""

import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the pattern in /api/products endpoint
# Pattern: 'stock': get_available_stock(p.id) or similar
pattern1 = r"'stock':\s*get_available_stock\(p\.id\)"
replacement1 = "'stock': p.stock"

pattern2 = r"'stock':\s*get_available_stock\(product\.id\)"
replacement2 = "'stock': product.stock"

# Apply replacements
content = re.sub(pattern1, replacement1, content)
content = re.sub(pattern2, replacement2, content)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed API endpoint to use product.stock")
print("✓ Changed 'stock': get_available_stock(p.id) → 'stock': p.stock")
print("✓ Changed 'stock': get_available_stock(product.id) → 'stock': product.stock")
