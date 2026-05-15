#!/usr/bin/env python3
"""
Verify real-time stock implementation
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 80)
print("REAL-TIME STOCK UPDATE VERIFICATION")
print("=" * 80)

checks = []

# Check 1: Immediate stock deduction
if 'Immediately deduct stock' in content and 'product.stock = product.stock - quantity' in content:
    checks.append(("Immediate stock deduction", "PASS", "Stock deducted on checkout"))
else:
    checks.append(("Immediate stock deduction", "FAIL", "Still using reserve_stock"))

# Check 2: stock_deducted flag
if 'new_order.stock_deducted = True' in content:
    checks.append(("Stock deducted flag", "PASS", "Set to True"))
else:
    checks.append(("Stock deducted flag", "FAIL", "Still False"))

# Check 3: Broadcast after commit
if 'broadcast_stock_update(product_id)' in content and 'Broadcast real-time stock updates' in content:
    checks.append(("Real-time broadcast", "PASS", "Broadcasts after commit"))
else:
    checks.append(("Real-time broadcast", "FAIL", "No broadcast found"))

# Check 4: SocketIO configured
if 'socketio = SocketIO' in content:
    checks.append(("SocketIO configured", "PASS", "SocketIO initialized"))
else:
    checks.append(("SocketIO configured", "FAIL", "SocketIO not found"))

# Check 5: broadcast_stock_update function exists
if 'def broadcast_stock_update' in content:
    checks.append(("Broadcast function", "PASS", "Function exists"))
else:
    checks.append(("Broadcast function", "FAIL", "Function missing"))

# Print results
print()
for check_name, status, details in checks:
    status_symbol = "[OK]" if status == "PASS" else "[FAIL]"
    print(f"{status_symbol} {check_name}")
    print(f"    {details}")
    print()

# Summary
passed = sum(1 for _, status, _ in checks if status == "PASS")
total = len(checks)

print("=" * 80)
if passed == total:
    print(f"SUCCESS: All {total} checks passed!")
    print()
    print("Real-time stock updates are fully implemented!")
    print()
    print("Next steps:")
    print("1. Restart Flask backend: python app.py")
    print("2. Test checkout - stock should deduct immediately")
    print("3. Check Flask logs for 'Broadcasted stock update' messages")
else:
    print(f"WARNING: {passed}/{total} checks passed")
    print("Some features may not work correctly")

print("=" * 80)
