#!/usr/bin/env python3
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find api_buyer_checkout and look for db.session.commit()
pattern = r"def api_buyer_checkout\(\):.*?(?=\n@app\.route|\ndef [a-z_]+\()"
match = re.search(pattern, content, re.DOTALL)

if match:
    lines = match.group(0).split('\n')
    
    for i, line in enumerate(lines):
        if 'db.session.commit()' in line:
            start = max(0, i-5)
            end = min(len(lines), i+15)
            print(f"=== Commit at line {i} ===")
            for j in range(start, end):
                marker = ">>>" if j == i else "   "
                print(f"{marker} {j:4d}: {lines[j]}")
            print("\n")
