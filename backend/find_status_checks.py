import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all lines checking product.status
patterns = [
    r"product\.status\s*!=\s*['\"]approved['\"]",
    r"product\.status\s*==\s*['\"]approved['\"]",
    r"product\.status\s*!=\s*['\"]active['\"]",
    r"product\.status\s*==\s*['\"]active['\"]",
]

print("=" * 80)
print("PRODUCT STATUS CHECKS FOUND")
print("=" * 80)

for i, line in enumerate(content.split('\n'), 1):
    for pattern in patterns:
        if re.search(pattern, line):
            print(f"Line {i}: {line.strip()}")
            break

print("=" * 80)
