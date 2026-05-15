#!/usr/bin/env python3
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the checkout function
pattern = r"def api_buyer_checkout\(\):.*?(?=\n@app\.route|\ndef [a-z_]+\()"
match = re.search(pattern, content, re.DOTALL)

if match:
    lines = match.group(0).split('\n')
    
    # Find the reserve_stock section
    for i, line in enumerate(lines):
        if 'reserve_stock' in line or 'Reserve stock' in line:
            start = max(0, i-3)
            end = min(len(lines), i+20)
            print(f"=== Found at line {i} ===")
            for j in range(start, end):
                print(f"{j:4d}: {lines[j]}")
            print("\n")
