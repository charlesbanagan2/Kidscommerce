#!/usr/bin/env python3
"""
Verify all fixes are correctly applied
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 80)
print("VERIFICATION REPORT")
print("=" * 80)

checks = []

# Check 1: Decorator order
if "@app.route('/api/v1/buyer/checkout', methods=['POST'])\n@token_required\n@active_user_required\ndef api_buyer_checkout():" in content:
    checks.append(("Checkout decorator order", "PASS", "token_required before active_user_required"))
else:
    checks.append(("Checkout decorator order", "FAIL", "Incorrect order or not found"))

# Check 2: Profile uses ORM
if "user = db.session.get(User, request.current_user_id)" in content and \
   "'first_name': user.first_name," in content:
    checks.append(("Profile GET uses ORM", "PASS", "Direct ORM access confirmed"))
else:
    checks.append(("Profile GET uses ORM", "FAIL", "Still using get_data_by_id"))

# Check 3: Profile PUT uses ORM
if "user.first_name = data['first_name']" in content and \
   "db.session.commit()" in content:
    checks.append(("Profile PUT uses ORM", "PASS", "Direct ORM updates confirmed"))
else:
    checks.append(("Profile PUT uses ORM", "FAIL", "Still using update_data_by_id"))

# Print results
for check_name, status, details in checks:
    status_symbol = "[OK]" if status == "PASS" else "[FAIL]"
    print(f"\n{status_symbol} {check_name}")
    print(f"    {details}")

print("\n" + "=" * 80)

# Summary
passed = sum(1 for _, status, _ in checks if status == "PASS")
total = len(checks)

if passed == total:
    print(f"SUCCESS: All {total} checks passed!")
    print("\nYou can now restart the backend server:")
    print("  python app.py")
else:
    print(f"WARNING: {passed}/{total} checks passed")
    print("Some fixes may not have been applied correctly")

print("=" * 80)
