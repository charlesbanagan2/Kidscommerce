#!/usr/bin/env python3
"""Find the checkout endpoint in app.py"""

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
for i, line in enumerate(lines, 1):
    if '/api/v1/buyer/checkout' in line and '@app.route' in line:
        # Print 100 lines starting from this route
        print(f"Found at line {i}")
        print("=" * 80)
        for j in range(max(0, i-1), min(len(lines), i+100)):
            print(f"{j+1:5d}: {lines[j]}", end='')
        break
