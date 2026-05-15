"""
Email verification module using EmailListVerify API
Provides real-time email validation for registration and password reset
"""
import os
import requests
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class EmailVerifier:
    """
    Real-time email verification using EmailListVerify API
    API Docs: https://emaillistverify.com/api-documentation/
    """
    
    BASE_URL = "https://api.emaillistverify.com"
    
    def __init__(self, api_key: str = None):
        """Initialize with API key from environment or parameter"""
        self.api_key = api_key or os.getenv('EMAILLISTVERIFY_API_KEY', '').strip()
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logger.warning("EmailListVerify API key not configured. Email validation disabled.")
    
    def verify_email(self, email: str) -> Dict:
        """
        Verify email address in real-time
        
        Args:
            email: Email address to verify
            
        Returns:
            Dict with keys:
            - valid: bool (True if email is valid)
            - reason: str (verification reason/status)
            - score: int (0-100, confidence level)
            - result: str ('success', 'invalid', 'unknown')
        """
        
        # If API not configured, use basic validation
        if not self.enabled:
            return self._basic_validation(email)
        
        try:
            # Call EmailListVerify API
            params = {
                'secret': self.api_key,
                'email': email
            }
            
            response = requests.get(
                f"{self.BASE_URL}/verify",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response
            result = data.get('result', 'unknown')  # 'success', 'invalid', 'unknown'
            reason = data.get('reason', 'No reason provided')
            
            return {
                'valid': result == 'success',
                'reason': reason,
                'score': self._calculate_score(result),
                'result': result,
                'api_used': True
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"EmailListVerify API error: {e}")
            # Fallback to basic validation on API error
            return self._basic_validation(email)
    
    def _basic_validation(self, email: str) -> Dict:
        """
        Basic email validation using regex and simple checks
        Used as fallback when API is unavailable
        """
        import re
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(pattern, email))
        
        # Check for disposable email domains (basic list)
        disposable_domains = {
            'tempmail.com', 'guerrillamail.com', '10minutemail.com',
            'mailinator.com', 'temp-mail.org', 'throwaway.email'
        }
        
        domain = email.split('@')[1].lower() if '@' in email else ''
        is_disposable = domain in disposable_domains
        
        return {
            'valid': is_valid and not is_disposable,
            'reason': 'Invalid format' if not is_valid else 'Disposable email' if is_disposable else 'Valid',
            'score': 100 if (is_valid and not is_disposable) else 0,
            'result': 'success' if (is_valid and not is_disposable) else 'invalid',
            'api_used': False
        }
    
    def _calculate_score(self, result: str) -> int:
        """Convert API result to confidence score"""
        scores = {
            'success': 100,
            'invalid': 0,
            'unknown': 50
        }
        return scores.get(result, 50)
    
    def batch_verify(self, emails: list) -> Dict[str, Dict]:
        """
        Verify multiple emails (note: EmailListVerify has rate limits)
        
        Args:
            emails: List of email addresses
            
        Returns:
            Dict mapping email -> verification result
        """
        results = {}
        for email in emails:
            results[email] = self.verify_email(email)
        return results


# Initialize global verifier
_verifier = None

def get_email_verifier() -> EmailVerifier:
    """Get or create email verifier instance"""
    global _verifier
    if _verifier is None:
        _verifier = EmailVerifier()
    return _verifier


def verify_email_address(email: str) -> Tuple[bool, str]:
    """
    Convenience function to verify email
    
    Args:
        email: Email address to verify
        
    Returns:
        Tuple of (is_valid, reason_message)
    """
    verifier = get_email_verifier()
    result = verifier.verify_email(email)
    return result['valid'], result['reason']
