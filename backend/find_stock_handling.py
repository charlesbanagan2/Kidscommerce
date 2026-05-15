#!/usr/bin/env python3
"""
Find checkout endpoint stock handling
"""
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find api_buyer_checkout function
pattern = r"def api_buyer_checkout\(\):.*?(?=\n@app\.route|\ndef [a-z_]+\(|\nif __name__|$)"
match = re.search(pattern, content, re.DOTALL)

if match:
    lines = match.group(0).split('\n')
    
    # Find stock-related lines
    print("=== Stock Handling in Checkout ===\n")
    for i, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in ['stock', 'reserve', 'deduct', 'broadcast', 'order_item']):
            # Print context
            start = max(0, i-2)
            end = min(len(lines), i+3)
            for j in range(start, end):
                marker = ">>>" if j == i else "   "
                print(f"{marker} {j:4d}: {lines[j]}")
            print()
