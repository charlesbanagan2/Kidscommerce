# FIXED FORGOT PASSWORD ENDPOINT
# Replace the existing /api/v1/auth/forgot-password route in app.py with this version

@app.route('/api/v1/auth/forgot-password', methods=['POST'])
def api_v1_forgot_password():
    """Send password reset code to user's email (Mobile API) - FIXED VERSION."""
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False, 
                'error': 'Invalid JSON data',
                'error_type': 'invalid_request'
            }), 400
        
        email = (data.get('email') or '').strip()
        if not email:
            return jsonify({
                'success': False, 
                'error': 'Email is required',
                'error_type': 'missing_email'
            }), 400
        
        # Check if user exists using ORM (more reliable)
        try:
            user = User.query.filter_by(email=email).first()
        except Exception as e:
            app.logger.error(f"Database query error: {str(e)}")
            return jsonify({
                'success': False, 
                'error': 'Database error. Please try again.',
                'error_type': 'database_error'
            }), 500
        
        if not user:
            return jsonify({
                'success': False, 
                'error': 'No account found with this email address',
                'error_type': 'user_not_found'
            }), 404
        
        # Generate 6-digit reset code
        reset_code = str(random.randint(100000, 999999))
        
        # Store code in user's verification_code field using ORM
        try:
            user.verification_code = reset_code
            db.session.commit()
            
            app.logger.info(f"✅ Reset code generated for {email}: {reset_code}")
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"❌ Failed to save reset code: {str(e)}")
            return jsonify({
                'success': False, 
                'error': 'Failed to generate reset code. Please try again.',
                'error_type': 'code_generation_failed'
            }), 500
        
        # Send email with reset code
        try:
            if send_verification_email(email, reset_code):
                app.logger.info(f"📧 Password reset code sent to {email}")
                return jsonify({
                    'success': True, 
                    'message': 'Reset code sent to your email. Please check your inbox.'
                }), 200
            else:
                # Email failed but code is saved - user can try again
                app.logger.error(f"❌ Failed to send reset email to {email}")
                return jsonify({
                    'success': False, 
                    'error': 'Failed to send email. Please check your email address and try again.',
                    'error_type': 'email_failed'
                }), 500
                
        except Exception as e:
            app.logger.error(f"❌ Email sending error: {str(e)}")
            return jsonify({
                'success': False, 
                'error': 'Failed to send email. Please try again later.',
                'error_type': 'email_error'
            }), 500
        
    except Exception as e:
        app.logger.error(f"❌ Unexpected error in forgot password: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False, 
            'error': 'An unexpected error occurred. Please try again.',
            'error_type': 'server_error'
        }), 500
