"""
Product Chat Feature Verification Script
Checks if all components are properly configured
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"[OK] {description}")
        return True
    else:
        print(f"[FAIL] {description} - File not found: {filepath}")
        return False

def check_file_contains(filepath, search_text, description):
    """Check if file contains specific text"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"[OK] {description}")
                return True
            else:
                print(f"[FAIL] {description} - Text not found")
                return False
    except Exception as e:
        print(f"[ERROR] {description} - {e}")
        return False

def main():
    print("=" * 70)
    print("PRODUCT CHAT FEATURE VERIFICATION")
    print("=" * 70)
    print()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mobile_dir = os.path.join(os.path.dirname(base_dir), 'mobile_app')
    
    results = []
    
    # Backend checks
    print("=== BACKEND CHECKS ===")
    results.append(check_file_exists(
        os.path.join(base_dir, 'product_chat_api.py'),
        "Product Chat API file exists"
    ))
    
    results.append(check_file_contains(
        os.path.join(base_dir, 'app.py'),
        'from product_chat_api import register_product_chat_api',
        "App.py imports product_chat_api"
    ))
    
    results.append(check_file_contains(
        os.path.join(base_dir, 'app.py'),
        'register_product_chat_api(app, db, socketio, token_required)',
        "App.py registers product_chat_api"
    ))
    
    results.append(check_file_contains(
        os.path.join(base_dir, 'unified_chat_api.py'),
        'product_id',
        "ChatMessage model has product_id column"
    ))
    
    print()
    
    # Mobile app checks
    print("=== MOBILE APP CHECKS ===")
    
    product_detail_path = os.path.join(
        mobile_dir, 
        'lib', 'screens', 'buyer_app', 'product_detail_screen.dart'
    )
    results.append(check_file_exists(
        product_detail_path,
        "Product detail screen exists"
    ))
    
    results.append(check_file_contains(
        product_detail_path,
        '_openProductChat',
        "Product detail has _openProductChat function"
    ))
    
    results.append(check_file_contains(
        product_detail_path,
        "import '../chat/chat_screen.dart'",
        "Product detail imports chat screen"
    ))
    
    api_service_path = os.path.join(
        mobile_dir,
        'lib', 'services', 'api_service.dart'
    )
    results.append(check_file_contains(
        api_service_path,
        'startProductChat',
        "ApiService has startProductChat method"
    ))
    
    results.append(check_file_contains(
        api_service_path,
        '/api/v1/chat/product/start',
        "ApiService has correct endpoint"
    ))
    
    print()
    print("=" * 70)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"RESULTS: {passed}/{total} checks passed")
    
    if passed == total:
        print("[SUCCESS] All checks passed! Feature is ready to test.")
        print()
        print("Next steps:")
        print("1. Restart backend: python app.py")
        print("2. Run mobile app")
        print("3. Navigate to product detail")
        print("4. Click message icon to test")
    else:
        print("[WARNING] Some checks failed. Please review the errors above.")
    
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
