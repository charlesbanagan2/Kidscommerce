import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find add_to_cart function
match1 = re.search(r"@app\.route\('/cart/add/<int:product_id>', methods=\['POST'\]\).*?(?=\n@app\.route|\nif __name__)", content, re.DOTALL)
if match1:
    print("=" * 80)
    print("FOUND: Web add_to_cart")
    print("=" * 80)
    print(match1.group(0)[:500])
    print("\n... (truncated)\n")
else:
    print("[X] Web add_to_cart NOT FOUND")

# Find buy_now function
match2 = re.search(r"@app\.route\('/buy-now/<int:product_id>', methods=\['POST'\]\).*?(?=\n@app\.route|\nif __name__)", content, re.DOTALL)
if match2:
    print("=" * 80)
    print("FOUND: Web buy_now")
    print("=" * 80)
    print(match2.group(0)[:500])
    print("\n... (truncated)\n")
else:
    print("[X] Web buy_now NOT FOUND")

# Check if they already have the fix
if "existing_cart_item = Cart.query.filter_by" in content:
    print("\n[!] Pattern 'existing_cart_item = Cart.query.filter_by' found in file")
    print("    This means the fix might already be there, or partially applied")
