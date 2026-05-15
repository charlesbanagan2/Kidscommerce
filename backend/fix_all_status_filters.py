"""
Fix all product status filters to include 'active' status
This will make all active products visible to buyers
"""
import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('app.py.backup', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Created backup: app.py.backup")

# Replace patterns
replacements = [
    # Pattern 1: filter_by(status='approved')
    (r"Product\.query\.filter_by\(status='approved'\)", 
     "Product.query.filter(Product.status.in_(['approved', 'active']))"),
    
    # Pattern 2: .filter_by(status='approved')
    (r"\.filter_by\(status='approved'\)", 
     ".filter(Product.status.in_(['approved', 'active']))"),
]

changes = 0
for pattern, replacement in replacements:
    new_content, count = re.subn(pattern, replacement, content)
    if count > 0:
        content = new_content
        changes += count
        print(f"✓ Replaced {count} occurrence(s) of: {pattern}")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Total changes: {changes}")
print("✅ File updated successfully!")
print("\nRestart your Flask server to see the changes.")
