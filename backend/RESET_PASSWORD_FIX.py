# FIXED RESET PASSWORD ENDPOINT
# Replace the existing /api/v1/auth/reset-password route in app.py with this version

@app.route('/api/v1/auth/reset-password', methods=['POST'])
def api_v1_reset_password():
    """Reset user password with verification code (Mobile API) - FIXED VERSION."""
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False, 
                'error': 'Invalid JSON data',
                'error_type': 'invalid_request'
            }), 400
        
        email = (data.get('email') or '').strip()
        code = (data.get('code') or '').strip()
        new_password = data.get('new_password')
        
        # Validate required fields
        if not email:
            return jsonify({
                'success': False, 
                'error': 'Email is required',
                'error_type': 'missing_email'
            }), 400
        
        if not code:
            return jsonify({
                'success': False, 
                'error': 'Reset code is required',
                'error_type': 'missing_code'
            }), 400
        
        if not new_password:
            return jsonify({
                'success': False, 
                'error': 'New password is required',
                'error_type': 'missing_password'
            }), 400
        
        # Validate password strength
        is_valid, password_message = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False, 
                'error': password_message,
                'error_type': 'weak_password'
            }), 400
        
        # Find user by email using ORM (more reliable than Supabase REST)
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
                'error': 'User not found',
                'error_type': 'user_not_found'
            }), 404
        
        # Verify reset code
        if not user.verification_code:
            return jsonify({
                'success': False, 
                'error': 'No reset code found. Please request a new code.',
                'error_type': 'no_code'
            }), 400
        
        if user.verification_code != code:
            return jsonify({
                'success': False, 
                'error': 'Invalid verification code. Please check your email and try again.',
                'error_type': 'invalid_code'
            }), 400
        
        # Update password and clear verification code using ORM
        try:
            user.password = new_password
            user.verification_code = None
            db.session.commit()
            
            app.logger.info(f"✅ Password reset successful for {email}")
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"❌ Database update error: {str(e)}")
            return jsonify({
                'success': False, 
                'error': 'Failed to update password. Please try again.',
                'error_type': 'update_failed'
            }), 500
        
        # Send confirmation email (don't fail if this fails)
        try:
            from email.utils import formataddr
            
            subject = '✅ Kids Kingdom - Password Changed Successfully'
            body = f'''Hello {user.first_name},

Your password has been successfully changed.

If you didn't make this change, please contact us immediately at support@kidskingdom.com

Best regards,
Kids Kingdom Team'''
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = formataddr(('Kids Kingdom', app.config['MAIL_SENDER']))
            msg['To'] = email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
                smtp.send_message(msg)
                
            app.logger.info(f"📧 Confirmation email sent to {email}")
        except Exception as e:
            # Don't fail the request if email fails
            app.logger.warning(f"⚠️ Failed to send confirmation email: {str(e)}")
        
        return jsonify({
            'success': True, 
            'message': 'Password reset successfully. You can now login with your new password.'
        }), 200
        
    except Exception as e:
        app.logger.error(f"❌ Unexpected error in reset password: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False, 
            'error': 'An unexpected error occurred. Please try again.',
            'error_type': 'server_error'
        }), 500
