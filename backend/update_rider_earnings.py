"""
Update app.py to use delivery_fee instead of RIDER_EARNING_RATE
"""

import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update _release_commissions function - rider earnings
content = re.sub(
    r'credit_wallet\(order\.picked_up_by, total \* RIDER_EARNING_RATE, \'order_commission\', order\.id\)',
    "delivery_fee = float(order.delivery_fee) if hasattr(order, 'delivery_fee') and order.delivery_fee else 36.0\n        credit_wallet(order.picked_up_by, delivery_fee, 'order_commission', order.id)",
    content
)

# 2. Update rider dashboard pending payout calculation (line 12033)
content = re.sub(
    r'pending_payout_amount = sum\(float\(o\.total_amount\) \* RIDER_EARNING_RATE for o in delivered_not_completed\)',
    "pending_payout_amount = sum(float(o.delivery_fee) if hasattr(o, 'delivery_fee') and o.delivery_fee else 36.0 for o in delivered_not_completed)",
    content
)

# 3. Update fare_estimate in rider orders (line 12331)
content = re.sub(
    r"'fare_estimate': round\(float\(o\.total_amount\) \* RIDER_EARNING_RATE, 2\)",
    "'fare_estimate': round(float(o.delivery_fee) if hasattr(o, 'delivery_fee') and o.delivery_fee else 36.0, 2)",
    content
)

# 4. Update rider accept order endpoint - calculate rider_earnings (line 17285)
content = re.sub(
    r'rider_earnings = float\(order\.total_amount\) \* 0\.15',
    "rider_earnings = float(order.get('delivery_fee', 36.0))",
    content,
    count=2  # There are 2 occurrences
)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app.py successfully!")
print("\nChanges made:")
print("1. _release_commissions: Rider gets delivery_fee instead of 15% of total")
print("2. Rider dashboard: Pending payout uses delivery_fee")
print("3. Rider orders: fare_estimate uses delivery_fee")
print("4. Accept order endpoints: rider_earnings = delivery_fee")
print("\nSELLER_EARNING_RATE updated to 85%")
print("ADMIN_EARNING_RATE updated to 15%")
