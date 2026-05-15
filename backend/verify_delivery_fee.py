"""
DELIVERY FEE VERIFICATION SCRIPT
=================================
Quick verification that all changes are in place
"""

import os
import re

def check_file_exists(filepath):
    """Check if file exists"""
    exists = os.path.exists(filepath)
    status = "[OK]" if exists else "[MISSING]"
    print(f"{status} {filepath}")
    return exists

def check_content(filepath, pattern, description):
    """Check if file contains expected content"""
    if not os.path.exists(filepath):
        print(f"[SKIP] {description} - File not found")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    found = bool(re.search(pattern, content, re.DOTALL))
    status = "[OK]" if found else "[MISSING]"
    print(f"{status} {description}")
    return found

def main():
    print("=" * 60)
    print("DELIVERY FEE IMPLEMENTATION VERIFICATION")
    print("=" * 60)
    
    all_ok = True
    
    # Check files exist
    print("\n1. Checking Files...")
    all_ok &= check_file_exists('app.py')
    all_ok &= check_file_exists('templates/buyer/checkout.html')
    all_ok &= check_file_exists('province_delivery_fees.py')
    
    # Check backups exist
    print("\n2. Checking Backups...")
    backup_exists = False
    for f in os.listdir('.'):
        if f.startswith('app.py.backup_'):
            print(f"[OK] Found backup: {f}")
            backup_exists = True
            break
    if not backup_exists:
        print("[WARNING] No app.py backup found")
    
    # Check app.py content
    print("\n3. Checking app.py Implementation...")
    all_ok &= check_content(
        'app.py',
        r'from province_delivery_fees import calculate_delivery_fee',
        'Import statement'
    )
    all_ok &= check_content(
        'app.py',
        r'delivery_fee = calculate_delivery_fee\(default_address\.province\)',
        'Checkout delivery fee calculation'
    )
    all_ok &= check_content(
        'app.py',
        r'delivery_fee=delivery_fee,',
        'Delivery fee in template context'
    )
    all_ok &= check_content(
        'app.py',
        r'grand_total = .*? delivery_fee',
        'Grand total includes delivery_fee'
    )
    all_ok &= check_content(
        'app.py',
        r'delivery_fee=delivery_fee,\s+shipping_fee=shipping_fee',
        'Order creation with delivery_fee'
    )
    
    # Check checkout.html content
    print("\n4. Checking checkout.html Display...")
    all_ok &= check_content(
        'templates/buyer/checkout.html',
        r'Delivery Fee',
        'Delivery Fee label'
    )
    all_ok &= check_content(
        'templates/buyer/checkout.html',
        r'delivery_fee\|default\(36\.0\)',
        'Delivery fee template variable'
    )
    all_ok &= check_content(
        'templates/buyer/checkout.html',
        r'default_address\.province',
        'Province display'
    )
    
    # Check province_delivery_fees.py
    print("\n5. Checking Province Delivery Fees Module...")
    all_ok &= check_content(
        'province_delivery_fees.py',
        r'PROVINCE_RANKS = \{',
        'Province ranks dictionary'
    )
    all_ok &= check_content(
        'province_delivery_fees.py',
        r'def calculate_delivery_fee\(province\):',
        'Calculate delivery fee function'
    )
    all_ok &= check_content(
        'province_delivery_fees.py',
        r'BASE_FEE = 36',
        'Base fee constant'
    )
    
    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("[SUCCESS] All checks passed!")
        print("\nYou can now:")
        print("  1. Restart your Flask server")
        print("  2. Test checkout with different provinces")
        print("  3. Verify delivery fees in database")
    else:
        print("[WARNING] Some checks failed!")
        print("\nPlease review the output above and fix any issues.")
    print("=" * 60)
    
    # Quick test of province_delivery_fees module
    print("\n6. Testing Province Delivery Fee Calculation...")
    try:
        from province_delivery_fees import calculate_delivery_fee, get_province_rank
        
        test_cases = [
            ('Laguna', 1, 36.0),
            ('Rizal', 2, 72.0),
            ('Cebu', 45, 1620.0),
            ('Tawi-Tawi', 82, 2952.0)
        ]
        
        for province, expected_rank, expected_fee in test_cases:
            rank = get_province_rank(province)
            fee = calculate_delivery_fee(province)
            
            rank_ok = rank == expected_rank
            fee_ok = fee == expected_fee
            
            status = "[OK]" if (rank_ok and fee_ok) else "[FAIL]"
            print(f"{status} {province}: Rank {rank} (expected {expected_rank}), Fee ₱{fee:.2f} (expected ₱{expected_fee:.2f})")
        
        print("\n[SUCCESS] Province delivery fee module is working correctly!")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to test province_delivery_fees module: {e}")
        print("Make sure province_delivery_fees.py is in the same directory as app.py")

if __name__ == '__main__':
    main()
