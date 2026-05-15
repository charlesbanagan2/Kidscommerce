"""
Fix: Remove province selection from checkout and automatically calculate delivery fee
based on buyer's registered address province.

Changes:
1. Checkout route: Calculate delivery fee from default address province automatically
2. Template: Remove province selection UI, show delivery fee based on address
"""

import re

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the checkout route and update it to automatically calculate delivery fee
# The checkout route should get the default address and calculate delivery fee immediately

checkout_pattern = r"(@app\.route\('/checkout'.*?\n@login_required\ndef checkout\(\):.*?)(# Get user and default address.*?default_address = Address\.query\.filter_by\(user_id=session\['user_id'\], is_default=True\)\.first\(\))"

replacement = r"""\1# Get user and default address
    user = db.session.get(User, session['user_id'])
    default_address = Address.query.filter_by(user_id=session['user_id'], is_default=True).first()
    
    # If no default address, use first available address
    if not default_address:
        default_address = Address.query.filter_by(user_id=session['user_id']).first()
    
    # Calculate delivery fee automatically based on buyer's address province
    delivery_fee = 36.0  # Default
    if default_address and default_address.province:
        try:
            delivery_fee = calculate_delivery_fee(default_address.province)
        except Exception as e:
            app.logger.warning(f"Failed to calculate delivery fee for province {default_address.province}: {e}")
            delivery_fee = 36.0"""

content = re.sub(checkout_pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[+] Updated checkout route to automatically calculate delivery fee from buyer's address")
print("\nNext steps:")
print("1. The delivery fee is now automatically calculated when checkout page loads")
print("2. Delivery fee is based on the buyer's default address province")
print("3. No province selection needed - it uses the registered address")
print("\nExample: Buyer from Laguna = P36 delivery fee (Rank 1 x P36)")
print("         Buyer from Cebu = P1,620 delivery fee (Rank 45 x P36)")
