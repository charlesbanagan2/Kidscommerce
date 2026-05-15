#!/usr/bin/env python3
"""
Fix checkout to immediately deduct stock and broadcast updates
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the checkout endpoint and check current stock handling
import re

# Look for the order creation and stock handling
pattern = r"(# Create order items and deduct stock.*?db\.session\.commit\(\))"
matches = list(re.finditer(pattern, content, re.DOTALL))

if matches:
    print(f"Found {len(matches)} stock handling sections")
    for i, match in enumerate(matches[:2], 1):
        print(f"\n=== Section {i} ===")
        lines = match.group(0).split('\n')[:30]
        for j, line in enumerate(lines, 1):
            print(f"{j:3d}: {line}")
else:
    print("Stock handling section not found")

# Check if broadcast_stock_update exists
if 'def broadcast_stock_update' in content:
    print("\n[OK] broadcast_stock_update function exists")
else:
    print("\n[WARN] broadcast_stock_update function not found")

# Check if SocketIO is configured
if 'socketio = SocketIO' in content:
    print("[OK] SocketIO is configured")
else:
    print("[WARN] SocketIO not configured")
