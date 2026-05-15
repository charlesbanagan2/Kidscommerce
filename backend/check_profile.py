#!/usr/bin/env python3
"""
Check user profile endpoint
"""
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the profile endpoint
profile_pattern = r"(@app\.route\(['\"]\/api\/v1\/buyer\/profile['\"].*?\ndef.*?\(.*?\):.*?)(?=\n@app\.route|\nif __name__|$)"

match = re.search(profile_pattern, content, re.DOTALL)

if match:
    print("Found profile endpoint:")
    print("=" * 80)
    lines = match.group(1).split('\n')
    for i, line in enumerate(lines[:80], 1):
        print(f"{i:3d}: {line}")
    print("=" * 80)
else:
    print("Profile endpoint not found")
