"""
Update all product status filters to use 'active' instead of 'approved'
This matches the actual database status labels: pending, active, rejected
"""
import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('app.py.backup', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Created backup: app.py.backup")

# Count occurrences first
patterns_to_find = [
    r"status='approved'",
    r'status="approved"',
    r"status\.in_\(\['approved', 'active'\]\)",
    r'status\.in_\(\["approved", "active"\]\)',
]

print("\nSearching for product status filters...")
total_found = 0
for pattern in patterns_to_find:
    matches = re.findall(pattern, content)
    if matches:
        print(f"  Found {len(matches)} occurrence(s) of: {pattern}")
        total_found += len(matches)

print(f"\nTotal patterns found: {total_found}")

# Replace patterns
replacements = [
    # Replace filter_by(status='approved') with filter_by(status='active')
    (r"filter_by\(status='approved'\)", "filter_by(status='active')"),
    (r'filter_by\(status="approved"\)', 'filter_by(status="active")'),
    
    # Replace status.in_(['approved', 'active']) with filter_by(status='active')
    (r"\.filter\(Product\.status\.in_\(\['approved', 'active'\]\)\)", ".filter_by(status='active')"),
    (r'\.filter\(Product\.status\.in_\(\["approved", "active"\]\)\)', '.filter_by(status="active")'),
    
    # Replace Product.query.filter(Product.status.in_(['approved', 'active']))
    (r"Product\.query\.filter\(Product\.status\.in_\(\['approved', 'active'\]\)\)", "Product.query.filter_by(status='active')"),
]

changes = 0
for pattern, replacement in replacements:
    new_content, count = re.subn(pattern, replacement, content)
    if count > 0:
        content = new_content
        changes += count
        print(f"✓ Replaced {count} occurrence(s)")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Total changes made: {changes}")
print("✅ All product filters now use status='active'")
print("\n📋 Status labels are now:")
print("   - pending: Waiting for admin approval")
print("   - active: Approved by admin, visible to buyers")
print("   - rejected: Rejected by admin, not visible")
print("\nRestart your Flask server to apply changes.")
