import re
import shutil
from datetime import datetime

# Backup
backup_file = f'app.py.backup.web_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy('app.py', backup_file)
print(f"Backup: {backup_file}")

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Web add_to_cart
old1 = r'''@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    try:
        quantity = int(request.form.get('quantity', 1))
        
        if quantity <= 0:
            flash('Invalid quantity', 'error')
            return redirect(request.referrer or url_for('index'))
        
        cart_item = Cart(
            user_id=session['user_id'],
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
        db.session.commit()'''

new1 = r'''@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    try:
        quantity = int(request.form.get('quantity', 1))
        
        if quantity <= 0:
            flash('Invalid quantity', 'error')
            return redirect(request.referrer or url_for('index'))
        
        # Check if already in cart
        existing_cart_item = Cart.query.filter_by(
            user_id=session['user_id'],
            product_id=product_id
        ).first()
        
        if existing_cart_item:
            existing_cart_item.quantity += quantity
            db.session.commit()
            flash(f'Cart updated! Total: {existing_cart_item.quantity}', 'success')
        else:
            cart_item = Cart(
                user_id=session['user_id'],
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
            db.session.commit()'''

if old1 in content:
    content = content.replace(old1, new1)
    print("[OK] Fixed web add_to_cart")
else:
    print("[X] Could not find web add_to_cart pattern")

# Fix 2: Web buy_now
old2 = r'''@app.route('/buy-now/<int:product_id>', methods=['POST'])
@login_required
def buy_now(product_id):
    try:
        quantity = int(request.form.get('quantity', 1))
        
        if quantity <= 0:
            flash('Invalid quantity', 'error')
            return redirect(request.referrer or url_for('product_detail', product_id=product_id))
        
        available = get_available_stock(product_id)
        if quantity > available:
            flash(f'Only {available} items available in stock', 'error')
            return redirect(url_for('product_detail', product_id=product_id))
        
        cart_item = Cart(
            user_id=session['user_id'],
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
        db.session.commit()'''

new2 = r'''@app.route('/buy-now/<int:product_id>', methods=['POST'])
@login_required
def buy_now(product_id):
    try:
        quantity = int(request.form.get('quantity', 1))
        
        if quantity <= 0:
            flash('Invalid quantity', 'error')
            return redirect(request.referrer or url_for('product_detail', product_id=product_id))
        
        available = get_available_stock(product_id)
        if quantity > available:
            flash(f'Only {available} items available in stock', 'error')
            return redirect(url_for('product_detail', product_id=product_id))
        
        # Check if already in cart
        existing_cart_item = Cart.query.filter_by(
            user_id=session['user_id'],
            product_id=product_id
        ).first()
        
        if existing_cart_item:
            existing_cart_item.quantity = quantity
            db.session.commit()
        else:
            cart_item = Cart(
                user_id=session['user_id'],
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
            db.session.commit()'''

if old2 in content:
    content = content.replace(old2, new2)
    print("[OK] Fixed web buy_now")
else:
    print("[X] Could not find web buy_now pattern")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nDone! Run VERIFY_FIXES.bat to confirm")
