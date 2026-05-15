import re

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    content = ''.join(lines)

# Find all references
matches = list(re.finditer(r'delivery_personnel|DeliveryPersonnel', content, re.IGNORECASE))
print(f"Found {len(matches)} references to delivery_personnel\n")
print("=" * 80)

for match in matches:
    line_num = content[:match.start()].count('\n') + 1
    start_line = max(0, line_num - 3)
    end_line = min(len(lines), line_num + 3)
    
    print(f"\nLine {line_num}:")
    print("-" * 80)
    for i in range(start_line, end_line):
        prefix = ">>> " if i == line_num - 1 else "    "
        print(f"{prefix}{i+1:5d}: {lines[i]}", end='')
    print("-" * 80)
