import re
import shutil
from datetime import datetime

backup_file = f'app.py.backup.final_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('app.py', backup_file)
print(f"Backup: {backup_file}")

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# FIX 1: /add-to-cart - Add duplicate check before creating cart item
# Find where it creates cart item without checking for existing
pattern1 = re.compile(
    r"(# Check available stock \(considering reserved orders\).*?)"
    r"(\s+cart_item = Cart\(\s+user_id=session\['user_id'\],\s+product_id=product_id,\s+quantity=quantity\s+\)\s+db\.session\.add\(cart_item\)\s+db\.session\.commit\(\))",
    re.DOTALL
)

replacement1 = r'''\1
    
    # CHECK FOR EXISTING CART ITEM - FIX DUPLICATES
    existing_cart = Cart.query.filter_by(
        user_id=session['user_id'],
        product_id=product_id
    ).first()
    
    if existing_cart:
        # Merge quantity
        existing_cart.quantity += quantity
        db.session.commit()
        flash(f'Cart updated! Total quantity: {existing_cart.quantity}', 'success')
    else:
        # Create new
        cart_item = Cart(
            user_id=session['user_id'],
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
        db.session.commit()'''

match1 = pattern1.search(content)
if match1:
    content = pattern1.sub(replacement1, content, count=1)
    print("[OK] Fixed /add-to-cart")
else:
    print("[X] Pattern not found for /add-to-cart")

# FIX 2: /buy-now - Add duplicate check before creating cart item
# Find where it creates cart item for buy now
pattern2 = re.compile(
    r"(# Stock guard \(uses order reservations, not cart contents\).*?)"
    r"(\s+cart_item = Cart\(\s+user_id=session\['user_id'\],\s+product_id=product_id,\s+quantity=req_qty\s+\)\s+db\.session\.add\(cart_item\)\s+db\.session\.commit\(\))",
    re.DOTALL
)

replacement2 = r'''\1
    
    # CHECK FOR EXISTING CART ITEM - FIX DUPLICATES
    existing_cart = Cart.query.filter_by(
        user_id=session['user_id'],
        product_id=product_id
    ).first()
    
    if existing_cart:
        # Replace quantity for buy now
        existing_cart.quantity = req_qty
        db.session.commit()
    else:
        # Create new
        cart_item = Cart(
            user_id=session['user_id'],
            product_id=product_id,
            quantity=req_qty
        )
        db.session.add(cart_item)
        db.session.commit()'''

match2 = pattern2.search(content)
if match2:
    content = pattern2.sub(replacement2, content, count=1)
    print("[OK] Fixed /buy-now")
else:
    print("[X] Pattern not found for /buy-now")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nDone! Run VERIFY_FIXES.bat")
