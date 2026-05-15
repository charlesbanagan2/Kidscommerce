"""
Fix credit_wallet to use direct database inserts instead of Supabase REST API
This allows it to work outside of request context (e.g., in background jobs)
"""

import re

print("=" * 70)
print("  FIXING credit_wallet FUNCTION")
print("=" * 70)

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the credit_wallet function
old_pattern = r"def credit_wallet\(user_id: int, amount: float, source: str, order_id: int = None\):.*?insert_data\('wallet_transaction', tx_data\)"

new_function = '''def credit_wallet(user_id: int, amount: float, source: str, order_id: int = None):
    """Credit user wallet using direct database insert (works outside request context)."""
    if amount == 0:
        return
    try:
        # Use direct ORM insert instead of Supabase REST API
        from datetime import datetime
        tx = WalletTransaction(
            user_id=user_id,
            order_id=order_id,
            amount=float(amount),
            type='credit',
            source=source,
            created_at=datetime.utcnow()
        )
        db.session.add(tx)
        db.session.flush()  # Flush but don't commit (caller will commit)
        app.logger.info(f"Credited {amount} to user {user_id} from {source}")
    except Exception as e:
        app.logger.error(f"Failed to credit wallet: {e}")
        raise'''

content = re.sub(old_pattern, new_function, content, flags=re.DOTALL)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n(+) Updated credit_wallet to use direct database inserts")
print("(+) Function now works outside of request context")
print("\nChanges:")
print("  - Removed Supabase REST API dependency")
print("  - Uses direct ORM WalletTransaction model")
print("  - Flushes but doesn't commit (caller commits)")
print("\nRestart backend to apply changes")
