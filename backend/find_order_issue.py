#!/usr/bin/env python3
"""
Find the checkout endpoint and check Order model fields
"""
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find Order model definition
order_model_pattern = r"class Order\(db\.Model\):.*?(?=\nclass |\nif __name__|$)"
match = re.search(order_model_pattern, content, re.DOTALL)

if match:
    print("Order Model Fields:")
    print("=" * 80)
    lines = match.group(0).split('\n')[:50]
    for line in lines:
        if 'db.Column' in line:
            print(line.strip())
    print("=" * 80)

# Find checkout endpoint Order creation
checkout_pattern = r"def api_buyer_checkout\(\):.*?(?=\n@app\.route|\ndef [a-z_]+\(|\nif __name__|$)"
match = re.search(checkout_pattern, content, re.DOTALL)

if match:
    print("\nCheckout endpoint - looking for Order creation:")
    print("=" * 80)
    lines = match.group(0).split('\n')
    for i, line in enumerate(lines):
        if 'Order(' in line or 'insert_data' in line and 'order' in line.lower():
            # Print context around Order creation
            start = max(0, i-5)
            end = min(len(lines), i+20)
            for j in range(start, end):
                print(f"{j:4d}: {lines[j]}")
            print("=" * 80)
            break
