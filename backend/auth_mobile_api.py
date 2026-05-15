# Mobile Authentication API Endpoints
# Add these routes to your app.py file

from flask import request, jsonify
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText

# Store reset codes temporarily (in production, use Redis or database)
reset_codes = {}

@app.route('/api/v1/auth/forgot-password', methods=['POST'])
def mobile_forgot_password():
    """Send password reset code to user's email"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'success': False, 'error': 'No account found with this email address'}), 404
        
        # Generate 6-digit code
        code = str(random.randint(100000, 999999))
        
        # Store code with expiration (5 minutes)
        reset_codes[email] = {
            'code': code,
            'expires': datetime.utcnow() + timedelta(minutes=5),
            'attempts': 0
        }
        
        # Send email
        try:
            subject = 'Kids Kingdom - Password Reset Code'
            body = f'''Hello {user.first_name},

You requested to reset your password for Kids Kingdom.

Your password reset code is: {code}

This code will expire in 5 minutes.

If you didn't request this, please ignore this email.

Best regards,
Kids Kingdom Team'''
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = app.config['MAIL_SENDER']
            msg['To'] = email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
                smtp.send_message(msg)
            
            return jsonify({
                'success': True,
                'message': 'Reset code sent to your email'
            }), 200
            
        except Exception as e:
            app.logger.error(f'Failed to send reset email: {str(e)}')
            return jsonify({
                'success': False,
                'error': 'Failed to send email. Please try again later.'
            }), 500
            
    except Exception as e:
        app.logger.error(f'Forgot password error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'An error occurred. Please try again.'
        }), 500


@app.route('/api/v1/auth/reset-password', methods=['POST'])
def mobile_reset_password():
    """Reset password using code"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        code = data.get('code', '').strip()
        new_password = data.get('new_password', '')
        
        if not email or not code or not new_password:
            return jsonify({
                'success': False,
                'error': 'Email, code, and new password are required'
            }), 400
        
        # Check if code exists
        if email not in reset_codes:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired code. Please request a new one.',
                'error_type': 'invalid_code'
            }), 400
        
        stored_data = reset_codes[email]
        
        # Check if code expired
        if datetime.utcnow() > stored_data['expires']:
            del reset_codes[email]
            return jsonify({
                'success': False,
                'error': 'Code has expired. Please request a new one.',
                'error_type': 'expired_code'
            }), 400
        
        # Check attempts
        if stored_data['attempts'] >= 3:
            del reset_codes[email]
            return jsonify({
                'success': False,
                'error': 'Too many failed attempts. Please request a new code.',
                'error_type': 'too_many_attempts'
            }), 400
        
        # Verify code
        if stored_data['code'] != code:
            stored_data['attempts'] += 1
            remaining_attempts = 3 - stored_data['attempts']
            return jsonify({
                'success': False,
                'error': f'Invalid code. {remaining_attempts} attempt(s) remaining.',
                'error_type': 'invalid_code',
                'attempts': stored_data['attempts'],
                'remaining_attempts': remaining_attempts
            }), 400
        
        # Find user and update password
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found',
                'error_type': 'user_not_found'
            }), 404
        
        # Update password (in production, hash this!)
        user.password = new_password
        db.session.commit()
        
        # Clear reset code
        del reset_codes[email]
        
        # Send confirmation email
        try:
            subject = 'Kids Kingdom - Password Changed Successfully'
            body = f'''Hello {user.first_name},

Your password has been successfully changed.

If you didn't make this change, please contact us immediately.

Best regards,
Kids Kingdom Team'''
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = app.config['MAIL_SENDER']
            msg['To'] = email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
                smtp.send_message(msg)
        except:
            pass  # Don't fail if confirmation email fails
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully'
        }), 200
        
    except Exception as e:
        app.logger.error(f'Reset password error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'An error occurred. Please try again.',
            'error_type': 'server_error'
        }), 500
