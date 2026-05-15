#!/usr/bin/env python3
"""
Fix checkout authentication and routing issues
"""
import re

# Read the app.py file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the checkout endpoint
checkout_pattern = r"(@app\.route\(['\"]\/api\/v1\/buyer\/checkout['\"].*?\n@token_required.*?\ndef.*?\(.*?\):.*?)(?=\n@app\.route|\nif __name__|$)"

match = re.search(checkout_pattern, content, re.DOTALL)

if match:
    print("Found checkout endpoint:")
    print("=" * 80)
    lines = match.group(1).split('\n')
    for i, line in enumerate(lines[:50], 1):
        print(f"{i:3d}: {line}")
    print("=" * 80)
else:
    print("Checkout endpoint not found with pattern")
    
# Search for token_required decorator
print("\nSearching for token_required decorator...")
token_pattern = r"def token_required\(f\):.*?return decorated"
match = re.search(token_pattern, content, re.DOTALL)
if match:
    print("Found token_required:")
    print(match.group(0)[:500])
