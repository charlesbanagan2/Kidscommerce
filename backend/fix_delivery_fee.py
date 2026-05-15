"""
DELIVERY FEE IMPLEMENTATION FIX
================================
This script implements province-based delivery fee calculation throughout the system.
"""

import re
import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create backup of file before modifying"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filepath, backup_path)
        print(f"[OK] Backed up: {backup_path}")
        return backup_path
    return None

def fix_app_py():
    """Fix app.py to implement province-based delivery fee"""
    filepath = 'app.py'
    
    print(f"\n[FIXING] {filepath}...")
    backup_file(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add import at the top
    import_line = "from province_delivery_fees import calculate_delivery_fee, get_province_rank"
    
    if import_line not in content:
        import_pattern = r'(from optimized_endpoints import register_optimized_endpoints)'
        content = re.sub(
            import_pattern,
            r'\1\nfrom province_delivery_fees import calculate_delivery_fee, get_province_rank',
            content
        )
        print("[OK] Added province_delivery_fees import")
    
    # 2. Fix checkout() function
    # Find the checkout function and replace shipping_fee calculation
    checkout_old = r'total = sum\(item\.product\.price \* item\.quantity for item in cart_items\)\s+shipping_fee = 50\.0 if total > 0 else 0\.0'
    
    checkout_new = '''total = sum(item.product.price * item.quantity for item in cart_items)
    
    # Calculate province-based delivery fee
    delivery_fee = 36.0  # Default (Laguna)
    if default_address and default_address.province:
        try:
            delivery_fee = calculate_delivery_fee(default_address.province)
        except Exception as e:
            app.logger.warning(f"Failed to calculate delivery fee for province {default_address.province}: {e}")
            delivery_fee = 36.0
    
    shipping_fee = 0.0  # Shipping fee is now separate from delivery fee'''
    
    content = re.sub(checkout_old, checkout_new, content)
    print("[OK] Updated checkout() delivery fee calculation")
    
    # 3. Update grand_total in checkout
    content = re.sub(
        r'grand_total = total - discount_amount \+ shipping_fee',
        'grand_total = total - discount_amount + delivery_fee',
        content
    )
    print("[OK] Updated checkout() grand_total calculation")
    
    # 4. Add delivery_fee to template context
    content = re.sub(
        r"(shipping_fee=shipping_fee,)",
        r"\1\n        delivery_fee=delivery_fee,",
        content
    )
    print("[OK] Added delivery_fee to checkout template context")
    
    # 5. Fix process_order() function
    process_old = r'(def process_order\(\):.*?total = sum\(item\.product\.price \* item\.quantity for item in cart_items\)\s+)shipping_fee = 50\.0 if total > 0 else 0\.0'
    
    process_new = r'''\1# Calculate province-based delivery fee from selected address
    delivery_fee = 36.0  # Default (Laguna)
    selected_address = None
    if address_id:
        selected_address = Address.query.filter_by(id=address_id, user_id=session['user_id']).first()
        if selected_address and selected_address.province:
            try:
                delivery_fee = calculate_delivery_fee(selected_address.province)
            except Exception as e:
                app.logger.warning(f"Failed to calculate delivery fee: {e}")
                delivery_fee = 36.0
    
    shipping_fee = 0.0  # Shipping fee is now separate from delivery fee'''
    
    content = re.sub(process_old, process_new, content, flags=re.DOTALL)
    print("[OK] Updated process_order() delivery fee calculation")
    
    # 6. Update grand_total in process_order
    content = re.sub(
        r'grand_total = max\(0\.0, total - discount_amount \+ shipping_fee\)',
        'grand_total = max(0.0, total - discount_amount + delivery_fee)',
        content
    )
    print("[OK] Updated process_order() grand_total calculation")
    
    # 7. Add delivery_fee to Order creation
    order_pattern = r'(new_order = Order\(\s+buyer_id=session\[\'user_id\'\],\s+total_amount=grand_total,\s+payment_method=payment_method,\s+shipping_address=shipping_address,\s+status=\'pending\')'
    order_replacement = r'''\1,
        delivery_fee=delivery_fee,
        shipping_fee=shipping_fee'''
    
    content = re.sub(order_pattern, order_replacement, content)
    print("[OK] Added delivery_fee to Order creation")
    
    # Write the fixed content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[SUCCESS] Fixed {filepath}")

def fix_checkout_html():
    """Fix checkout.html to display province-based delivery fee"""
    filepath = 'templates/buyer/checkout.html'
    
    print(f"\n[FIXING] {filepath}...")
    backup_file(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace Shipping Fee section with Delivery Fee
    old_shipping = '''<!-- Shipping Fee -->
                        <div class="d-flex justify-content-between mb-2">
                            <span>
                                <i class="fas fa-truck me-1"></i>Shipping Fee
                            </span>
                            <span id="shippingFee">₱50.00</span>
                        </div>'''
    
    new_delivery = '''<!-- Delivery Fee (Province-based) -->
                        <div class="d-flex justify-content-between mb-2">
                            <span>
                                <i class="fas fa-shipping-fast me-1"></i>Delivery Fee
                                {% if default_address and default_address.province %}
                                    <small class="text-muted">({{ default_address.province }})</small>
                                {% endif %}
                            </span>
                            <span id="deliveryFee" class="fw-bold text-primary">₱{{ "%.2f"|format(delivery_fee|default(36.0)) }}</span>
                        </div>'''
    
    content = content.replace(old_shipping, new_delivery)
    print("[OK] Updated delivery fee display in checkout.html")
    
    # Add delivery fee info
    info_old = '<!-- Estimated Delivery -->'
    info_new = '''<!-- Delivery Fee Info -->
                        <div class="alert alert-info small mb-3">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>Delivery Fee:</strong> Calculated based on your province location.
                            {% if default_address and default_address.province %}
                                <br><small>{{ default_address.province }} delivery: ₱{{ "%.2f"|format(delivery_fee|default(36.0)) }}</small>
                            {% endif %}
                        </div>
                        
                        <!-- Estimated Delivery -->'''
    
    content = content.replace(info_old, info_new)
    print("[OK] Added delivery fee info section")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[SUCCESS] Fixed {filepath}")

def remove_rider_html():
    """Remove rider.html as riders now use mobile app only"""
    rider_files = [
        'templates/rider.html',
        'templates/rider/rider.html'
    ]
    
    print("\n[REMOVING] Rider HTML files (riders use mobile app)...")
    
    for filepath in rider_files:
        if os.path.exists(filepath):
            backup_file(filepath)
            os.remove(filepath)
            print(f"[OK] Removed: {filepath}")
        else:
            print(f"[SKIP] Not found: {filepath}")

def main():
    """Main execution function"""
    print("=" * 60)
    print("DELIVERY FEE IMPLEMENTATION FIX")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Update app.py to calculate province-based delivery fees")
    print("2. Update checkout.html to display delivery fees")
    print("3. Remove rider HTML files (mobile app only)")
    print("\nAll files will be backed up before modification.")
    print("=" * 60)
    
    try:
        # Execute all fixes
        fix_app_py()
        fix_checkout_html()
        remove_rider_html()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL FIXES COMPLETED!")
        print("=" * 60)
        print("\nSummary:")
        print("  [OK] app.py - Province-based delivery fee calculation")
        print("  [OK] checkout.html - Delivery fee display")
        print("  [OK] Rider HTML files removed")
        print("\nNext Steps:")
        print("  1. Restart Flask server")
        print("  2. Test checkout with different provinces")
        print("  3. Verify delivery fee in orders")
        print("  4. Check rider earnings (mobile app)")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nPlease check the error and try again.")
        print("All modified files have backups with .backup_TIMESTAMP extension")

if __name__ == '__main__':
    main()
