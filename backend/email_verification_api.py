"""
Email verification API endpoints for Flask app
Add these endpoints to your main app.py to enable email verification
"""

from flask import jsonify, request
from email_verification import get_email_verifier
import logging

logger = logging.getLogger(__name__)


def register_email_verification_endpoints(app):
    """
    Register email verification endpoints
    
    Endpoints:
    - POST /api/verify-email - Verify single email
    - POST /api/verify-emails - Batch verify multiple emails
    """
    
    @app.route('/api/verify-email', methods=['POST'])
    def verify_single_email():
        """
        Verify a single email address
        
        Request:
            {
                "email": "test@example.com"
            }
            
        Response:
            {
                "valid": true,
                "reason": "Valid email",
                "score": 100,
                "api_used": true
            }
        """
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        try:
            verifier = get_email_verifier()
            result = verifier.verify_email(email)
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Email verification error: {e}")
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/api/verify-emails', methods=['POST'])
    def verify_multiple_emails():
        """
        Verify multiple email addresses (batch)
        
        Request:
            {
                "emails": ["test1@example.com", "test2@example.com"]
            }
            
        Response:
            {
                "test1@example.com": {
                    "valid": true,
                    "reason": "Valid email",
                    "score": 100,
                    "api_used": true
                },
                "test2@example.com": {
                    "valid": false,
                    "reason": "Invalid email",
                    "score": 0,
                    "api_used": false
                }
            }
        """
        data = request.get_json(silent=True) or {}
        emails = data.get('emails', [])
        
        if not emails or not isinstance(emails, list):
            return jsonify({'error': 'emails array is required'}), 400
        
        try:
            verifier = get_email_verifier()
            results = verifier.batch_verify(emails)
            return jsonify(results), 200
        except Exception as e:
            logger.error(f"Batch email verification error: {e}")
            return jsonify({'error': str(e)}), 500
    
    
    @app.route('/api/verify-email-status', methods=['GET'])
    def email_verification_status():
        """
        Check if email verification is enabled and API key status
        
        Response:
            {
                "enabled": true,
                "api": "emaillistverify",
                "fallback_validation": "enabled"
            }
        """
        verifier = get_email_verifier()
        return jsonify({
            'enabled': verifier.enabled,
            'api': 'emaillistverify' if verifier.enabled else 'local_only',
            'fallback_validation': 'enabled'
        }), 200
