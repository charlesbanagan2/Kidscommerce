import re
import shutil
from datetime import datetime

# Backup
backup_file = f'app.py.backup.status_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('app.py', backup_file)
print(f"Backup: {backup_file}")

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: product.status != 'approved' -> product.status not in ['approved', 'active']
pattern1 = r"product\.status\s*!=\s*['\"]approved['\"]"
replacement1 = "product.status not in ['approved', 'active']"
count1 = len(re.findall(pattern1, content))
content = re.sub(pattern1, replacement1, content)
print(f"[OK] Fixed {count1} instances of: product.status != 'approved'")

# Pattern 2: product.status == 'approved' -> product.status in ['approved', 'active']
pattern2 = r"product\.status\s*==\s*['\"]approved['\"]"
replacement2 = "product.status in ['approved', 'active']"
count2 = len(re.findall(pattern2, content))
content = re.sub(pattern2, replacement2, content)
print(f"[OK] Fixed {count2} instances of: product.status == 'approved'")

# Pattern 3: if product.status != 'active' (should allow both)
pattern3 = r"if\s+product\.status\s*!=\s*['\"]active['\"]"
replacement3 = "if product.status not in ['approved', 'active']"
count3 = len(re.findall(pattern3, content))
content = re.sub(pattern3, replacement3, content)
print(f"[OK] Fixed {count3} instances of: if product.status != 'active'")

# Pattern 4: .get('status') != 'active' for API routes
pattern4 = r"\.get\(['\"]status['\"]\)\s*!=\s*['\"]active['\"]"
replacement4 = ".get('status') not in ['approved', 'active']"
count4 = len(re.findall(pattern4, content))
content = re.sub(pattern4, replacement4, content)
print(f"[OK] Fixed {count4} instances of: .get('status') != 'active'")

# Pattern 5: .get('status') == 'active' for API routes
pattern5 = r"\.get\(['\"]status['\"]\)\s*==\s*['\"]active['\"]"
replacement5 = ".get('status') in ['approved', 'active']"
count5 = len(re.findall(pattern5, content))
content = re.sub(pattern5, replacement5, content)
print(f"[OK] Fixed {count5} instances of: .get('status') == 'active'")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

total = count1 + count2 + count3 + count4 + count5
print(f"\n[SUCCESS] Fixed {total} total product status checks")
print("\nNow 'active' and 'approved' products are both available to buyers")
print("Restart Flask server and test!")
