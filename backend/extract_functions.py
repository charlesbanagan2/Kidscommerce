import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract full add-to-cart function
match1 = re.search(r"@app\.route\('/add-to-cart/<int:product_id>'\).*?(?=\n@app\.route)", content, re.DOTALL)
if match1:
    with open('extracted_add_to_cart.txt', 'w', encoding='utf-8') as f:
        f.write(match1.group(0))
    print("[OK] Extracted /add-to-cart to: extracted_add_to_cart.txt")
    print(f"     Length: {len(match1.group(0))} chars")
else:
    print("[X] Could not extract /add-to-cart")

# Extract full buy-now function
match2 = re.search(r"@app\.route\('/buy-now/<int:product_id>'.*?\).*?(?=\n@app\.route)", content, re.DOTALL)
if match2:
    with open('extracted_buy_now.txt', 'w', encoding='utf-8') as f:
        f.write(match2.group(0))
    print("[OK] Extracted /buy-now to: extracted_buy_now.txt")
    print(f"     Length: {len(match2.group(0))} chars")
else:
    print("[X] Could not extract /buy-now")

print("\nOpen the .txt files to see the full functions")
