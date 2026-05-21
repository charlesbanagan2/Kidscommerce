#!/usr/bin/env python3
"""
Fix: Change product status check from 'active' to 'approved' in cart endpoints
Problem: Products have status 'approved' but code checks for 'active', causing 404 errors
"""
import re

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Count occurrences before fix
before_count = len(re.findall(r"product\.get\('status'\)\s*[!=]=\s*'active'", content))
print(f"Found {before_count} occurrences of status == 'active' checks")

# Fix 1: Change != 'active' to != 'approved' (for error checks)
content = re.sub(
    r"(product\.get\('status'\))\s*!=\s*'active'",
    r"\1 != 'approved'",
    content
)

# Fix 2: Change == 'active' to == 'approved' (for positive checks)
content = re.sub(
    r"(product\.get\('status'\))\s*==\s*'active'",
    r"\1 == 'approved'",
    content
)

# Count after fix
after_count = len(re.findall(r"product\.get\('status'\)\s*[!=]=\s*'approved'", content))

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ Fixed {before_count} occurrences")
print(f"✓ Now checking for 'approved' status instead of 'active'")
print(f"✓ Verified {after_count} occurrences now use 'approved'")
print("\nFix applied! Product ID 32 should now be addable to cart.")
