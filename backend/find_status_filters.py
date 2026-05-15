import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
# Find all occurrences of status='approved' filtering
patterns = [
    r"filter_by\(status='approved'\)",
    r"status == 'approved'",
    r"\.status\.in_\(\['approved'\]\)",
]

print("Finding all product status filters in app.py:\n")
print("=" * 60)

for i, line in enumerate(content.split('\n'), 1):
    for pattern in patterns:
        if re.search(pattern, line):
            print(f"Line {i}: {line.strip()}")
            break
