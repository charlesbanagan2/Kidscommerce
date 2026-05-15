import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find add-to-cart function
match1 = re.search(r"@app\.route\('/add-to-cart/<int:product_id>'.*?\ndef [^(]+\([^)]*\):.*?(?=\n@app\.route|\nif __name__)", content, re.DOTALL)
if match1:
    print("=" * 80)
    print("FOUND: /add-to-cart/<int:product_id>")
    print("=" * 80)
    lines = match1.group(0).split('\n')[:30]
    print('\n'.join(lines))
    print("\n... (showing first 30 lines)\n")
else:
    print("[X] /add-to-cart NOT FOUND")

print("\n")

# Find buy-now function
match2 = re.search(r"@app\.route\('/buy-now/<int:product_id>'.*?\ndef [^(]+\([^)]*\):.*?(?=\n@app\.route|\nif __name__)", content, re.DOTALL)
if match2:
    print("=" * 80)
    print("FOUND: /buy-now/<int:product_id>")
    print("=" * 80)
    lines = match2.group(0).split('\n')[:30]
    print('\n'.join(lines))
    print("\n... (showing first 30 lines)\n")
else:
    print("[X] /buy-now NOT FOUND")
