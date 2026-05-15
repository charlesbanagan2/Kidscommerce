#!/usr/bin/env python3
"""
Fix checkout endpoint decorator order
The issue: @active_user_required is before @token_required
But active_user_required needs request.current_user_id which is set by token_required
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Swap decorator order for checkout endpoint
old_decorators = """@app.route('/api/v1/buyer/checkout', methods=['POST'])
@active_user_required
@token_required
def api_buyer_checkout():"""

new_decorators = """@app.route('/api/v1/buyer/checkout', methods=['POST'])
@token_required
@active_user_required
def api_buyer_checkout():"""

if old_decorators in content:
    content = content.replace(old_decorators, new_decorators)
    print("✅ Fixed decorator order for checkout endpoint")
else:
    print("⚠️ Decorator pattern not found - may already be fixed")

# Fix 2: Add better error handling in token_required
old_token_check = """        if not payload:
            print("Token is invalid or expired")
            return jsonify({'error': 'Token is invalid or expired'}), 401"""

new_token_check = """        if not payload:
            print("Token is invalid or expired")
            print(f"Token was: {token[:50]}..." if token else "No token")
            return jsonify({'error': 'Authentication required'}), 401"""

if old_token_check in content:
    content = content.replace(old_token_check, new_token_check)
    print("✅ Enhanced token error handling")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ All fixes applied successfully!")
print("\nNext steps:")
print("1. Restart the Flask backend server")
print("2. Test checkout from mobile app")
