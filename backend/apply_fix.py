#!/usr/bin/env python3
"""
Fix checkout endpoint decorator order
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: Swap decorator order for checkout endpoint
old_decorators = """@app.route('/api/v1/buyer/checkout', methods=['POST'])
@active_user_required
@token_required
def api_buyer_checkout():"""

new_decorators = """@app.route('/api/v1/buyer/checkout', methods=['POST'])
@token_required
@active_user_required
def api_buyer_checkout():"""

if old_decorators in content:
    content = content.replace(old_decorators, new_decorators)
    print("[OK] Fixed decorator order for checkout endpoint")
else:
    print("[WARN] Decorator pattern not found - may already be fixed")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[SUCCESS] All fixes applied!")
print("\nNext steps:")
print("1. Restart the Flask backend server")
print("2. Test checkout from mobile app")
