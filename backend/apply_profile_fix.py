import re

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Updated buyer profile with database sync
buyer_profile_new = '''@app.route('/api/v1/buyer/profile', methods=['GET', 'PUT'])
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
        return jsonify({'success': False, 'error': str(e)}), 400'''

# Pattern to find and replace buyer profile
pattern = r"@app\.route\('/api/v1/buyer/profile'.*?\n@token_required\ndef buyer_profile_api\(\):.*?(?=\n\n@app\.route)"
content = re.sub(pattern, buyer_profile_new + '\n', content, flags=re.DOTALL)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Buyer profile updated with database sync")

# Now update rider profile in rider_mobile_only_api.py
with open('rider_mobile_only_api.py', 'r', encoding='utf-8') as f:
    rider_content = f.read()

# Find and replace GET endpoint
rider_get_pattern = r"@app\.route\('/api/v1/rider/profile', methods=\['GET'\]\).*?@token_required.*?@role_required\('rider'\)\ndef api_rider_get_profile\(\):.*?(?=@app\.route\('/api/v1/rider/profile', methods=\['PUT'\]\))"

# Find and replace PUT endpoint
rider_put_old = r"@app\.route\('/api/v1/rider/profile', methods=\['PUT'\]\).*?@token_required.*?@role_required\('rider'\)\ndef api_rider_update_profile\(\):.*?(?=\n  # )"

rider_put_new = '''@app.route('/api/v1/rider/profile', methods=['PUT'])
  @token_required
  @role_required('rider')
  def api_rider_update_profile():
      """Update rider profile - syncs to database"""
      try:
          rider_id = request.current_user_id
          data = request.get_json()
          
          user = db.session.get(User, rider_id)
          if not user:
              return jsonify({'success': False, 'error': 'User not found'}), 404
          
          if 'first_name' in data:
              user.first_name = data['first_name']
          if 'last_name' in data:
              user.last_name = data['last_name']
          if 'phone' in data:
              user.phone = data['phone']
          if 'address' in data:
              user.address = data['address']
          
          user.updated_at = datetime.utcnow()
          
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
          app.logger.error(f"Error updating profile: {str(e)}")
          return jsonify({'success': False, 'error': 'Failed to update profile'}), 500
  
  # '''

rider_content = re.sub(rider_put_old, rider_put_new, rider_content, flags=re.DOTALL)

with open('rider_mobile_only_api.py', 'w', encoding='utf-8') as f:
    f.write(rider_content)

print("[OK] Rider profile updated with database sync")
print("\n[SUCCESS] TAPOS NA! Profile updates will now sync to database and entire system")
