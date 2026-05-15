"""
Remove early rider earnings credit from mark-delivered endpoint
Rider should only get earnings when buyer confirms (completed status)
"""

import re

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and remove the credit_wallet block in api_rider_mark_delivered
# This credits rider when marking as delivered - we need to remove this
pattern = r"        # Credit rider earnings \(delivery fee based on province ranking\).*?except Exception as e:\s+app\.logger\.error\(f\"Failed to credit rider earnings: \{e\}\"\)\s+"

content = re.sub(pattern, '', content, flags=re.DOTALL)

# Add a comment explaining the change
content = content.replace(
    "        if not update_result:\n            return jsonify({'error': 'Failed to mark order as delivered'}), 500\n        \n        # Notify buyer",
    "        if not update_result:\n            return jsonify({'error': 'Failed to mark order as delivered'}), 500\n        \n        # NOTE: Rider earnings will be credited when buyer confirms receipt (status='completed')\n        # This is handled by _release_commissions() function\n        \n        # Notify buyer"
)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("(+) Removed early rider earnings credit from mark-delivered endpoint")
print("(+) Rider earnings will now only be credited when buyer confirms receipt")
print("\nFlow:")
print("1. Rider marks as delivered -> Order status = 'delivered'")
print("2. Buyer confirms receipt -> Order status = 'completed'")
print("3. _release_commissions() called -> Rider gets delivery_fee")
