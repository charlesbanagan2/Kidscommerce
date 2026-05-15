"""
AUTOMATIC NOTIFICATION INTEGRATION SCRIPT
==========================================

This script will automatically add notification calls to your existing app.py
Run this once to integrate the Shopee-style notification system.

Usage:
    python integrate_notifications.py
"""

import re
import os
from datetime import datetime

def backup_file(filepath):
    """Create a backup of the file"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Backup created: {backup_path}")
    return backup_path


def add_imports(content):
    """Add notification system imports"""
    import_block = """
# Shopee-Style Notification System
from shopee_notification_system import (
    ensure_notification_table,
    notify_order_placed,
    notify_order_confirmed,
    notify_order_processing,
    notify_order_ready_for_pickup,
    notify_order_accepted_by_rider,
    notify_order_in_transit,
    notify_order_delivered,
    notify_order_completed,
    notify_order_cancelled,
    notify_payment_confirmed,
    notify_return_requested,
    notify_return_approved,
    notify_return_rejected,
    notify_refund_processed,
    notify_product_approved,
    notify_product_rejected,
    notify_low_stock,
    notify_out_of_stock
)
from notification_api_endpoints import register_notification_api
"""
    
    # Find the last import statement
    import_pattern = r'(from .+ import .+\n|import .+\n)'
    matches = list(re.finditer(import_pattern, content))
    
    if matches:
        last_import = matches[-1]
        insert_pos = last_import.end()
        content = content[:insert_pos] + import_block + content[insert_pos:]
        print("✓ Added notification imports")
    
    return content


def add_initialization(content):
    """Add notification system initialization"""
    init_code = """
# Initialize Notification System
register_notification_api(app)

# Ensure notification table
@app.before_request
def _ensure_notification_table():
    if not app.config.get('_notification_table_ready', False):
        try:
            ensure_notification_table()
            app.config['_notification_table_ready'] = True
        except Exception as e:
            print(f"Notification table setup error: {e}")
            app.config['_notification_table_ready'] = True
"""
    
    # Find app initialization (after app = Flask(__name__))
    pattern = r"(app = Flask\(__name__\).*?\n)"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        insert_pos = match.end()
        # Find the next blank line
        next_blank = content.find('\n\n', insert_pos)
        if next_blank != -1:
            content = content[:next_blank] + '\n' + init_code + content[next_blank:]
            print("✓ Added notification initialization")
    
    return content


def add_notification_to_checkout(content):
    """Add notification to checkout endpoint"""
    # Find checkout endpoint
    pattern = r"(@app\.route\('/api/checkout'.*?def api_checkout\(\):.*?db\.session\.commit\(\))"
    
    def replacement(match):
        original = match.group(0)
        if 'notify_order_placed' not in original:
            return original + "\n        \n        # Send notifications\n        notify_order_placed(order)"
        return original
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    if new_content != content:
        print("✓ Added notification to checkout")
    return new_content


def add_notification_to_order_status_changes(content):
    """Add notifications to order status change endpoints"""
    
    # Pattern: order.status = 'some_status'
    status_patterns = {
        "'processing'": "notify_order_processing(order)",
        "'ready_for_pickup'": "notify_order_ready_for_pickup(order)",
        "'accepted_by_rider'": "notify_order_accepted_by_rider(order)",
        "'in_transit'": "notify_order_in_transit(order)",
        "'delivered'": "notify_order_delivered(order)",
        "'completed'": "notify_order_completed(order)",
        "'cancelled'": "notify_order_cancelled(order)",
    }
    
    for status, notify_call in status_patterns.items():
        # Find: order.status = 'status'
        # Add after: db.session.commit()
        pattern = rf"(order\.status = {status}.*?db\.session\.commit\(\))"
        
        def replacement(match):
            original = match.group(0)
            if notify_call not in original:
                return original + f"\n        \n        # Send notification\n        {notify_call}"
            return original
        
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    print("✓ Added notifications to order status changes")
    return content


def add_notification_to_product_approval(content):
    """Add notifications to product approval"""
    
    # Find product approval
    pattern = r"(product\.status = 'approved'.*?db\.session\.commit\(\))"
    
    def replacement(match):
        original = match.group(0)
        if 'notify_product_approved' not in original:
            return original + "\n        \n        # Send notification\n        notify_product_approved(product)"
        return original
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Find product rejection
    pattern = r"(product\.status = 'rejected'.*?db\.session\.commit\(\))"
    
    def replacement(match):
        original = match.group(0)
        if 'notify_product_rejected' not in original:
            return original + "\n        \n        # Send notification\n        notify_product_rejected(product)"
        return original
    
    new_content = re.sub(pattern, replacement, new_content, flags=re.DOTALL)
    
    if new_content != content:
        print("✓ Added notifications to product approval/rejection")
    return new_content


def integrate_notifications():
    """Main integration function"""
    print("=" * 60)
    print("SHOPEE-STYLE NOTIFICATION SYSTEM - AUTO INTEGRATION")
    print("=" * 60)
    print()
    
    app_py_path = 'app.py'
    
    if not os.path.exists(app_py_path):
        print("✗ Error: app.py not found in current directory")
        print("  Please run this script from the backend directory")
        return False
    
    print(f"Reading {app_py_path}...")
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_path = backup_file(app_py_path)
    
    print("\nIntegrating notification system...")
    print("-" * 60)
    
    # Apply transformations
    content = add_imports(content)
    content = add_initialization(content)
    content = add_notification_to_checkout(content)
    content = add_notification_to_order_status_changes(content)
    content = add_notification_to_product_approval(content)
    
    # Write back
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("-" * 60)
    print("\n✓ Integration complete!")
    print(f"\nBackup saved to: {backup_path}")
    print("\nNext steps:")
    print("1. Review the changes in app.py")
    print("2. Test the notification system")
    print("3. Check SHOPEE_NOTIFICATION_INTEGRATION_GUIDE.py for details")
    print("\nTo test:")
    print("  python app.py")
    print("  # Then place an order and check notifications")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = integrate_notifications()
        if success:
            print("=" * 60)
            print("SUCCESS! Notification system integrated.")
            print("=" * 60)
        else:
            print("\nIntegration failed. Please check the errors above.")
    except Exception as e:
        print(f"\n✗ Error during integration: {e}")
        print("\nPlease integrate manually using the guide:")
        print("  SHOPEE_NOTIFICATION_INTEGRATION_GUIDE.py")
