"""
FIX: Buyer and Rider Profile Updates
Ensures profile updates sync to database and entire system
"""

BUYER_PROFILE_UPDATE = '''
@app.route('/api/v1/buyer/profile', methods=['GET', 'PUT'])
@token_required
def buyer_profile_api():
    """Get or update buyer profile - syncs to database"""
    try:
        user = db.session.get(User, request.current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        if request.method == 'GET':
            profile_image = get_user_avatar_url(user.id, user.role)
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
                    'email_verified': user.email_verified,
                    'profile_image': profile_image,
                    'profile_picture': profile_image,
                }
            })
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            # Update fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'phone' in data:
                user.phone = data['phone']
            if 'address' in data:
                user.address = data['address']
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Sync to Supabase
            try:
                supabase.table('users').update({
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'address': user.address,
                    'updated_at': user.updated_at.isoformat()
                }).eq('id', user.id).execute()
            except Exception as e:
                app.logger.warning(f'Supabase sync failed: {e}')
            
            profile_image = get_user_avatar_url(user.id, user.role)
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
                    'status': user.status,
                    'profile_image': profile_image,
                    'profile_picture': profile_image,
                }
            })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'buyer_profile error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400
'''

RIDER_PROFILE_UPDATE = '''
@app.route('/api/v1/rider/profile', methods=['GET', 'PUT'])
@token_required
@role_required('rider')
def api_rider_profile():
    """Get or update rider profile - syncs to database"""
    try:
        rider_id = request.current_user_id
        user = db.session.get(User, rider_id)
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        if request.method == 'GET':
            rider_application = RiderApplication.query.filter_by(user_id=rider_id).first()
            profile_image = get_user_avatar_url(user.id, user.role)
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'address': user.address,
                    'profile_picture': profile_image,
                    'status': user.status,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                },
                'rider_details': {
                    'vehicle_type': rider_application.vehicle_type if rider_application else None,
                    'vehicle_number': rider_application.vehicle_number if rider_application else None,
                    'status': rider_application.status if rider_application else None
                } if rider_application else None
            }), 200
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            # Update user fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'phone' in data:
                user.phone = data['phone']
            if 'address' in data:
                user.address = data['address']
            
            user.updated_at = datetime.utcnow()
            
            # Update rider application if exists
            rider_application = RiderApplication.query.filter_by(user_id=rider_id).first()
            if rider_application:
                if 'vehicle_type' in data:
                    rider_application.vehicle_type = data['vehicle_type']
                if 'vehicle_number' in data:
                    rider_application.vehicle_number = data['vehicle_number']
            
            db.session.commit()
            
            # Sync to Supabase
            try:
                supabase.table('users').update({
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'address': user.address,
                    'updated_at': user.updated_at.isoformat()
                }).eq('id', user.id).execute()
                
                if rider_application:
                    supabase.table('rider_applications').update({
                        'vehicle_type': rider_application.vehicle_type,
                        'vehicle_number': rider_application.vehicle_number
                    }).eq('user_id', rider_id).execute()
            except Exception as e:
                app.logger.warning(f'Supabase sync failed: {e}')
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully'
            }), 200
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error with rider profile: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to process profile'}), 500
'''

print("INSTRUCTIONS:")
print("=" * 60)
print("1. I-replace ang buyer profile endpoint sa app.py (line ~20189)")
print("2. I-replace ang rider profile endpoint sa rider_mobile_only_api.py")
print("3. Siguruhing may import ng datetime at supabase")
print("=" * 60)
