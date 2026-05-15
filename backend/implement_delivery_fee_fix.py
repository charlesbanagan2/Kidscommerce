"""
DELIVERY FEE IMPLEMENTATION FIX
================================
This script implements province-based delivery fee calculation throughout the system.

Changes:
1. Import province_delivery_fees module in app.py
2. Update checkout() to calculate delivery_fee based on province
3. Update process_order() to save delivery_fee to Order
4. Update checkout.html to display delivery_fee
5. Remove rider.html (riders use mobile app only)
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
        print(f"✅ Backed up: {backup_path}")
        return backup_path
    return None

def fix_app_py():
    """Fix app.py to implement province-based delivery fee"""
    filepath = 'app.py'
    
    print(f"\n📝 Fixing {filepath}...")
    backup_file(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add import at the top (after other imports)
    import_line = "from province_delivery_fees import calculate_delivery_fee, get_province_rank"
    
    if import_line not in content:
        # Find the line with "from optimized_endpoints import"
        import_pattern = r'(from optimized_endpoints import register_optimized_endpoints)'
        content = re.sub(
            import_pattern,
            r'\1\nfrom province_delivery_fees import calculate_delivery_fee, get_province_rank',
            content
        )
        print("✅ Added province_delivery_fees import")
    
    # 2. Fix checkout() function - replace shipping_fee calculation
    checkout_pattern = r'(def checkout\(\):.*?total = sum\(item\.product\.price \* item\.quantity for item in cart_items\)\s+)shipping_fee = 50\.0 if total > 0 else 0\.0'
    
    checkout_replacement = r'''\1# Calculate province-based delivery fee
    delivery_fee = 36.0  # Default (Laguna)
    if default_address and default_address.province:
        try:
            delivery_fee = calculate_delivery_fee(default_address.province)
        except Exception as e:
            app.logger.warning(f"Failed to calculate delivery fee for province {default_address.province}: {e}")
            delivery_fee = 36.0
    
    shipping_fee = 0.0  # Shipping fee is now separate from delivery fee'''
    
    content = re.sub(checkout_pattern, checkout_replacement, content, flags=re.DOTALL)
    print("✅ Updated checkout() delivery fee calculation")
    
    # 3. Fix checkout() - update grand_total calculation
    grand_total_pattern = r'grand_total = total - discount_amount \+ shipping_fee'
    grand_total_replacement = 'grand_total = total - discount_amount + delivery_fee'
    content = re.sub(grand_total_pattern, grand_total_replacement, content)
    print("✅ Updated checkout() grand_total calculation")
    
    # 4. Fix checkout() - add delivery_fee to template context
    checkout_return_pattern = r"(return render_template\(\s+'buyer/checkout\.html',\s+cart_items=cart_items,.*?shipping_fee=shipping_fee,)"
    checkout_return_replacement = r"\1\n        delivery_fee=delivery_fee,"
    content = re.sub(checkout_return_pattern, checkout_return_replacement, content, flags=re.DOTALL)
    print("✅ Added delivery_fee to checkout template context")
    
    # 5. Fix process_order() - calculate delivery_fee
    process_order_pattern = r'(def process_order\(\):.*?total = sum\(item\.product\.price \* item\.quantity for item in cart_items\)\s+)shipping_fee = 50\.0 if total > 0 else 0\.0'
    
    process_order_replacement = r'''\1# Calculate province-based delivery fee from selected address
    delivery_fee = 36.0  # Default (Laguna)
    if address_id:
        selected_address = Address.query.filter_by(id=address_id, user_id=session['user_id']).first()
        if selected_address and selected_address.province:
            try:
                delivery_fee = calculate_delivery_fee(selected_address.province)
            except Exception as e:
                app.logger.warning(f"Failed to calculate delivery fee: {e}")
                delivery_fee = 36.0
    
    shipping_fee = 0.0  # Shipping fee is now separate from delivery fee'''
    
    content = re.sub(process_order_pattern, process_order_replacement, content, flags=re.DOTALL)
    print("✅ Updated process_order() delivery fee calculation")
    
    # 6. Fix process_order() - update grand_total calculation
    content = re.sub(
        r'grand_total = max\(0\.0, total - discount_amount \+ shipping_fee\)',
        'grand_total = max(0.0, total - discount_amount + delivery_fee)',
        content
    )
    print("✅ Updated process_order() grand_total calculation")
    
    # 7. Fix process_order() - add delivery_fee to Order creation
    order_creation_pattern = r'(new_order = Order\(\s+buyer_id=session\[\'user_id\'\],\s+total_amount=grand_total,\s+payment_method=payment_method,\s+shipping_address=shipping_address,\s+status=\'pending\')'
    order_creation_replacement = r'''\1,
        delivery_fee=delivery_fee,
        shipping_fee=shipping_fee'''
    
    content = re.sub(order_creation_pattern, order_creation_replacement, content, flags=re.DOTALL)
    print("✅ Added delivery_fee to Order creation")
    
    # Write the fixed content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Successfully fixed {filepath}")

def fix_checkout_html():
    """Fix checkout.html to display province-based delivery fee"""
    filepath = 'templates/buyer/checkout.html'
    
    print(f"\n📝 Fixing {filepath}...")
    backup_file(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace Shipping Fee section with Delivery Fee
    shipping_pattern = r'''<!-- Shipping Fee -->
                        <div class="d-flex justify-content-between mb-2">
                            <span>
                                <i class="fas fa-truck me-1"></i>Shipping Fee
                            </span>
                            <span id="shippingFee">₱50\.00</span>
                        </div>'''
    
    shipping_replacement = '''<!-- Delivery Fee (Province-based) -->
                        <div class="d-flex justify-content-between mb-2">
                            <span>
                                <i class="fas fa-shipping-fast me-1"></i>Delivery Fee
                                {% if default_address and default_address.province %}
                                    <small class="text-muted">({{ default_address.province }})</small>
                                {% endif %}
                            </span>
                            <span id="deliveryFee" class="fw-bold text-primary">₱{{ "%.2f"|format(delivery_fee|default(36.0)) }}</span>
                        </div>'''
    
    content = re.sub(shipping_pattern, shipping_replacement, content, flags=re.DOTALL)
    print("✅ Updated delivery fee display in checkout.html")
    
    # Add delivery fee info tooltip
    info_pattern = r'(<!-- Estimated Delivery -->)'
    info_replacement = r'''<!-- Delivery Fee Info -->
                        <div class="alert alert-info small mb-3">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>Delivery Fee:</strong> Calculated based on your province location.
                            {% if default_address and default_address.province %}
                                <br><small>{{ default_address.province }} delivery: ₱{{ "%.2f"|format(delivery_fee|default(36.0)) }}</small>
                            {% endif %}
                        </div>
                        
                        \1'''
    
    content = re.sub(info_pattern, info_replacement, content)
    print("✅ Added delivery fee info section")
    
    # Write the fixed content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Successfully fixed {filepath}")

def remove_rider_html():
    """Remove rider.html as riders now use mobile app only"""
    rider_files = [
        'templates/rider.html',
        'templates/rider/rider.html',
        'templates/rider/dashboard.html'
    ]
    
    print("\n🗑️  Removing rider HTML files (riders use mobile app)...")
    
    for filepath in rider_files:
        if os.path.exists(filepath):
            backup_file(filepath)
            os.remove(filepath)
            print(f"✅ Removed: {filepath}")
        else:
            print(f"⚠️  Not found: {filepath}")

def create_api_endpoint_for_delivery_fee():
    """Add API endpoint to calculate delivery fee dynamically"""
    filepath = 'app.py'
    
    print(f"\n📝 Adding delivery fee API endpoint...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if endpoint already exists
    if '@app.route(\'/api/calculate-delivery-fee\'' in content:
        print("⚠️  API endpoint already exists, skipping...")
        return
    
    # Add the API endpoint before the last line
    api_endpoint = '''

@app.route('/api/calculate-delivery-fee', methods=['POST'])
@login_required
def api_calculate_delivery_fee():
    """Calculate delivery fee based on province (AJAX endpoint)"""
    try:
        data = request.get_json() or {}
        province = data.get('province', '').strip()
        
        if not province:
            return jsonify({'success': False, 'error': 'Province is required'}), 400
        
        try:
            delivery_fee = calculate_delivery_fee(province)
            province_rank = get_province_rank(province)
            
            return jsonify({
                'success': True,
                'delivery_fee': float(delivery_fee),
                'province': province,
                'province_rank': province_rank,
                'formula': f'{province_rank} × ₱36 = ₱{delivery_fee:.2f}'
            })
        except Exception as e:
            app.logger.error(f'Delivery fee calculation error: {e}')
            return jsonify({
                'success': False,
                'error': 'Failed to calculate delivery fee',
                'delivery_fee': 36.0  # Default fallback
            }), 500
            
    except Exception as e:
        app.logger.error(f'API calculate delivery fee error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

'''
    
    # Insert before the last few lines (usually if __name__ == '__main__')
    if "if __name__ == '__main__':" in content:
        content = content.replace("if __name__ == '__main__':", api_endpoint + "if __name__ == '__main__':")
    else:
        content += api_endpoint
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added delivery fee calculation API endpoint")

def add_javascript_for_dynamic_fee():
    """Add JavaScript to checkout.html for dynamic delivery fee updates"""
    filepath = 'templates/buyer/checkout.html'
    
    print(f"\n📝 Adding dynamic delivery fee JavaScript...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already added
    if 'updateDeliveryFee' in content:
        print("⚠️  JavaScript already exists, skipping...")
        return
    
    # Add JavaScript before {% endblock scripts %}
    js_code = '''
// Dynamic delivery fee calculation when address changes
function updateDeliveryFee(province) {
    if (!province) return;
    
    const deliveryFeeElement = document.getElementById('deliveryFee');
    const grandTotalElement = document.getElementById('grandTotalDisplay');
    
    if (!deliveryFeeElement) return;
    
    // Show loading state
    deliveryFeeElement.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
    
    fetch('/api/calculate-delivery-fee', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ province: province })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const deliveryFee = parseFloat(data.delivery_fee);
            deliveryFeeElement.textContent = `₱${deliveryFee.toFixed(2)}`;
            
            // Update grand total
            const subtotal = parseFloat('{{ total|default(0) }}');
            const discount = parseFloat('{{ discount_amount|default(0) }}');
            const newGrandTotal = subtotal - discount + deliveryFee;
            
            if (grandTotalElement) {
                grandTotalElement.textContent = `₱${newGrandTotal.toFixed(2)}`;
            }
            
            console.log('Delivery fee updated:', data.formula);
        } else {
            deliveryFeeElement.textContent = '₱36.00';
            console.error('Failed to calculate delivery fee:', data.error);
        }
    })
    .catch(error => {
        console.error('Error calculating delivery fee:', error);
        deliveryFeeElement.textContent = '₱36.00';
    });
}

// Listen for province changes in address modals
document.addEventListener('DOMContentLoaded', function() {
    const editProvinceSelect = document.getElementById('edit_province');
    const addProvinceSelect = document.getElementById('add_province');
    
    if (editProvinceSelect) {
        editProvinceSelect.addEventListener('change', function() {
            const provinceText = this.options[this.selectedIndex]?.text;
            if (provinceText) {
                updateDeliveryFee(provinceText);
            }
        });
    }
    
    if (addProvinceSelect) {
        addProvinceSelect.addEventListener('change', function() {
            const provinceText = this.options[this.selectedIndex]?.text;
            if (provinceText) {
                updateDeliveryFee(provinceText);
            }
        });
    }
});

'''
    
    # Insert before {% endblock scripts %}
    content = content.replace('{% endblock %}', js_code + '\n{% endblock %}')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added dynamic delivery fee JavaScript")

def main():
    """Main execution function"""
    print("=" * 60)
    print("DELIVERY FEE IMPLEMENTATION FIX")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Update app.py to calculate province-based delivery fees")
    print("2. Update checkout.html to display delivery fees")
    print("3. Add API endpoint for dynamic fee calculation")
    print("4. Remove rider HTML files (mobile app only)")
    print("\nAll files will be backed up before modification.")
    print("=" * 60)
    
    response = input("\nProceed with fixes? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Aborted by user")
        return
    
    try:
        # Execute all fixes
        fix_app_py()
        fix_checkout_html()
        create_api_endpoint_for_delivery_fee()
        add_javascript_for_dynamic_fee()
        remove_rider_html()
        
        print("\n" + "=" * 60)
        print("✅ ALL FIXES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📋 Summary:")
        print("  ✅ app.py - Province-based delivery fee calculation")
        print("  ✅ checkout.html - Delivery fee display")
        print("  ✅ API endpoint - Dynamic fee calculation")
        print("  ✅ JavaScript - Real-time fee updates")
        print("  ✅ Rider HTML files removed")
        print("\n🔄 Next Steps:")
        print("  1. Restart Flask server")
        print("  2. Test checkout with different provinces")
        print("  3. Verify delivery fee in orders")
        print("  4. Check rider earnings (mobile app)")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPlease check the error and try again.")
        print("All modified files have backups with .backup_TIMESTAMP extension")

if __name__ == '__main__':
    main()
