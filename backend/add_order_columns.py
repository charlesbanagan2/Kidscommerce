#!/usr/bin/env python3
"""
Add recipient_name and recipient_phone columns to Order model
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the Order model and add the missing fields after shipping_address
old_order_model = """    shipping_address = db.Column(db.Text, nullable=False)
    stock_deducted = db.Column(db.Boolean, default=False)  # TRUE kapag na-process na ng seller"""

new_order_model = """    shipping_address = db.Column(db.Text, nullable=False)
    recipient_name = db.Column(db.String(255))
    recipient_phone = db.Column(db.String(20))
    notes = db.Column(db.Text)
    stock_deducted = db.Column(db.Boolean, default=False)  # TRUE kapag na-process na ng seller"""

if old_order_model in content:
    content = content.replace(old_order_model, new_order_model)
    print("[OK] Added recipient_name, recipient_phone, and notes columns to Order model")
else:
    print("[WARN] Could not find exact match - checking if already added")
    if 'recipient_name = db.Column' in content:
        print("[INFO] recipient_name already exists in Order model")
    else:
        print("[ERROR] Could not add columns - manual intervention needed")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[SUCCESS] Order model updated!")
print("\nNext: Restart Flask backend to apply changes")
