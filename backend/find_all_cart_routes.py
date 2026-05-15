import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all routes with 'cart' in them
cart_routes = re.findall(r"@app\.route\('([^']*cart[^']*)'[^)]*\)", content, re.IGNORECASE)
print("=" * 80)
print("ALL CART ROUTES FOUND:")
print("=" * 80)
for route in cart_routes:
    print(f"  - {route}")

# Find all routes with 'buy' in them
buy_routes = re.findall(r"@app\.route\('([^']*buy[^']*)'[^)]*\)", content, re.IGNORECASE)
print("\n" + "=" * 80)
print("ALL BUY ROUTES FOUND:")
print("=" * 80)
for route in buy_routes:
    print(f"  - {route}")

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print(f"Total cart routes: {len(cart_routes)}")
print(f"Total buy routes: {len(buy_routes)}")

if len(cart_routes) == 0 and len(buy_routes) == 0:
    print("\n[!] No cart or buy routes found!")
    print("    Your app might be API-only (mobile only)")
