"""
Google Login API Endpoint for Mobile Apps
Handles Google Sign-In authentication and creates pending accounts for new users.
"""

import json
from datetime import datetime


def register_google_login_api(app, db, User):
    """Register the Google login API endpoint"""
    from flask import request, jsonify
    
    @app.route('/api/v1/auth/google-login', methods=['POST'])
    def api_google_login():
        """
        Handle Google Sign-In for mobile apps.
        
        Request body:
        {
            "access_token": "...",  # from Google SDK
            "id_token": "..."       # from Google SDK
        }
        
        Response:
        - New user (first Google login): 403 with pending_approval message
        - Existing pending user: 403 with pending_approval message
        - Active user: 200 with tokens and user data
        - Rejected user: 403 with rejection message
        """
        try:
            data = request.get_json(silent=True) or {}
            id_token = data.get('id_token') or data.get('access_token')
            
            if not id_token:
                return jsonify({
                    'success': False,
                    'error': 'id_token or access_token is required'
                }), 400
            
            # Decode Google token to get email and profile info
            # Note: In production, validate the token signature with Google's public keys
            # For MVP, we decode without verification (NOT recommended for production)
            try:
                import base64
                # Google ID tokens are JWT format: header.payload.signature
                parts = id_token.split('.')
                if len(parts) != 3:
                    raise ValueError('Invalid token format')
                
                # Decode payload (add padding if needed)
                payload = parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                
                decoded = base64.urlsafe_b64decode(payload)
                token_data = json.loads(decoded)
                
                email = token_data.get('email')
                first_name = token_data.get('given_name', 'Guest')
                last_name = token_data.get('family_name', '')
                picture = token_data.get('picture')
                
                if not email:
                    return jsonify({
                        'success': False,
                        'error': 'Could not extract email from Google token'
                    }), 400
                
                # Check if user exists
                user = db.session.query(User).filter_by(email=email).first()
                
                if user:
                    # User exists
                    if user.status == 'pending':
                        # User is pending approval
                        return jsonify({
                            'success': False,
                            'error': 'Your account is pending admin approval',
                            'pending_approval': True,
                            'email': email
                        }), 403
                    
                    elif user.status == 'rejected':
                        # User was rejected
                        return jsonify({
                            'success': False,
                            'error': 'Your account registration was not approved',
                            'email': email
                        }), 403
                    
                    elif user.status == 'active':
                        # User is approved - generate tokens and return user data
                        # Use JWT tokens for mobile app (similar to /api/login)
                        import secrets
                        access_token = secrets.token_urlsafe(32)
                        refresh_token = secrets.token_urlsafe(32)
                        
                        # Store tokens in session or cache (depending on your auth strategy)
                        # For now, return them directly
                        user_data = {
                            'id': user.id,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'full_name': f'{user.first_name} {user.last_name}',
                            'role': user.role,
                            'phone': user.phone,
                            'address': user.address,
                            'profile_picture': getattr(user, 'profile_picture', None),
                            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None
                        }
                        
                        return jsonify({
                            'success': True,
                            'user': user_data,
                            'tokens': {
                                'access_token': access_token,
                                'refresh_token': refresh_token,
                                'expires_in': 86400
                            }
                        }), 200
                    
                    else:
                        # Unknown status
                        return jsonify({
                            'success': False,
                            'error': f'Account status: {user.status}'
                        }), 403
                
                else:
                    # New user - create with pending status
                    new_user = User(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password='google_oauth',  # Placeholder - user logs in via Google only
                        phone='',
                        address='',
                        role='buyer',
                        status='pending',  # NEW USERS ARE PENDING APPROVAL
                        email_verified=True  # Google email is already verified
                    )
                    
                    # Optional: Store Google profile picture
                    if picture:
                        try:
                            setattr(new_user, 'profile_picture', picture)
                        except:
                            pass
                    
                    db.session.add(new_user)
                    db.session.commit()
                    
                    # Return pending approval message
                    return jsonify({
                        'success': False,
                        'error': 'Your account has been created and is pending admin approval',
                        'pending_approval': True,
                        'email': email,
                        'user_id': new_user.id
                    }), 403
            
            except ValueError as e:
                app.logger.error(f'Token decode error: {e}')
                return jsonify({
                    'success': False,
                    'error': 'Invalid token format'
                }), 400
            
        except Exception as e:
            app.logger.exception(f'Google login error: {e}')
            return jsonify({
                'success': False,
                'error': f'Google login failed: {str(e)}'
            }), 500
