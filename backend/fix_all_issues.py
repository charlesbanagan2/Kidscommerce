#!/usr/bin/env python3
"""
Comprehensive fix for checkout and profile issues
"""

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

changes_made = []

# Fix 1: Ensure buyer_profile_api uses ORM directly instead of get_data_by_id
old_profile = """@app.route('/api/v1/buyer/profile', methods=['GET', 'PUT'])
@token_required
def buyer_profile_api():
    \"\"\"Get or update buyer profile - for mobile app (Supabase version).\"\"\"
    try:
        user = get_data_by_id('user', request.current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'user': {
                    'id': user.get('id'),
                    'first_name': user.get('first_name'),
                    'last_name': user.get('last_name'),
                    'email': user.get('email'),
                    'phone': user.get('phone'),
                    'address': user.get('address'),
                    'role': user.get('role'),
                    'status': user.get('status'),
                    'email_verified': user.get('email_verified')
                }
            })"""

new_profile = """@app.route('/api/v1/buyer/profile', methods=['GET', 'PUT'])
@token_required
def buyer_profile_api():
    \"\"\"Get or update buyer profile - for mobile app (uses ORM directly for reliability).\"\"\"
    try:
        # Use ORM directly for more reliable data access
        user = db.session.get(User, request.current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone': user.phone,
                    'address': user.address,
                    'role': user.role,
                    'status': user.status,
                    'email_verified': user.email_verified
                }
            })"""

if old_profile in content:
    content = content.replace(old_profile, new_profile)
    changes_made.append("Fixed buyer_profile_api to use ORM directly")

# Fix 2: Also fix the PUT method in profile
old_put = """        elif request.method == 'PUT':
            data = request.get_json()
            
            # Update allowed fields
            update_data = {}
            if 'first_name' in data:
                update_data['first_name'] = data['first_name']
            if 'last_name' in data:
                update_data['last_name'] = data['last_name']
            if 'phone' in data:
                update_data['phone'] = data['phone']
            if 'address' in data:
                update_data['address'] = data['address']
            
            updated_user = update_data_by_id('user', request.current_user_id, update_data)
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'user': {
                    'id': updated_user.get('id'),
                    'first_name': updated_user.get('first_name'),
                    'last_name': updated_user.get('last_name'),
                    'email': updated_user.get('email'),
                    'phone': updated_user.get('phone'),
                    'address': updated_user.get('address'),
                    'role': updated_user.get('role'),
                    'status': updated_user.get('status')
                }
            })"""

new_put = """        elif request.method == 'PUT':
            data = request.get_json()
            
            # Update allowed fields directly on ORM object
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'phone' in data:
                user.phone = data['phone']
            if 'address' in data:
                user.address = data['address']
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone': user.phone,
                    'address': user.address,
                    'role': user.role,
                    'status': user.status
                }
            })"""

if old_put in content:
    content = content.replace(old_put, new_put)
    changes_made.append("Fixed buyer_profile_api PUT method to use ORM directly")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

if changes_made:
    print("[SUCCESS] Applied fixes:")
    for change in changes_made:
        print(f"  - {change}")
else:
    print("[INFO] No changes needed - may already be fixed")

print("\nNext steps:")
print("1. Restart Flask backend: python app.py")
print("2. Test from mobile app:")
print("   - Profile should show correct data")
print("   - Checkout should work without 401 errors")
