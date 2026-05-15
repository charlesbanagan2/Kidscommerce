"""
Test Email Configuration Script
Run this to verify your Gmail SMTP setup is working correctly
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import os
from dotenv import load_dotenv

# Load environment variables
SUPABASE_ENV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'mobile_app',
    'lib',
    'kids_commercedb',
    'supabase.env',
)
load_dotenv(SUPABASE_ENV_PATH, override=True)

def test_email_connection():
    """Test Gmail SMTP connection and send a test email"""
    
    # Get credentials from environment
    sender_email = os.getenv('MAIL_SENDER', 'gbanagan33@gmail.com')
    app_password = os.getenv('MAIL_APP_PASSWORD', 'hprhqjfxpdfahxsf')
    
    print("=" * 60)
    print("📧 GMAIL SMTP TEST")
    print("=" * 60)
    print(f"Sender Email: {sender_email}")
    print(f"App Password: {'*' * (len(app_password) - 4)}{app_password[-4:]}")
    print("=" * 60)
    
    # Ask for test recipient
    test_recipient = input("\n✉️  Enter test email address (or press Enter to use sender): ").strip()
    if not test_recipient:
        test_recipient = sender_email
    
    print(f"\n📤 Sending test email to: {test_recipient}")
    print("⏳ Please wait...\n")
    
    try:
        # Create test email
        subject = "🧪 Test Email - Kids Kingdom SMTP Configuration"
        
        html_body = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }
                .content { padding: 40px 30px; }
                .success-box { background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; border-radius: 5px; }
                .footer { background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧪 Test Email</h1>
                    <p>SMTP Configuration Test</p>
                </div>
                <div class="content">
                    <div class="success-box">
                        <strong>✅ Success!</strong> Your Gmail SMTP configuration is working correctly.
                    </div>
                    <p>This is a test email from your Kids Kingdom application.</p>
                    <p>If you received this email, it means:</p>
                    <ul>
                        <li>✅ Gmail App Password is configured correctly</li>
                        <li>✅ SMTP connection is working</li>
                        <li>✅ Email sending functionality is operational</li>
                    </ul>
                    <p><strong>You can now send:</strong></p>
                    <ul>
                        <li>🔐 Password reset codes</li>
                        <li>✅ Account approval notifications</li>
                        <li>❌ Account rejection notifications</li>
                        <li>🎁 Coupon codes</li>
                        <li>📦 Order confirmations</li>
                    </ul>
                </div>
                <div class="footer">
                    <p><strong>Kids Kingdom Team</strong></p>
                    <p style="font-size: 12px; color: #666;">This is an automated test message</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = """
        Test Email - Kids Kingdom SMTP Configuration
        
        ✅ Success! Your Gmail SMTP configuration is working correctly.
        
        This is a test email from your Kids Kingdom application.
        
        If you received this email, it means:
        - Gmail App Password is configured correctly
        - SMTP connection is working
        - Email sending functionality is operational
        
        You can now send:
        - Password reset codes
        - Account approval notifications
        - Account rejection notifications
        - Coupon codes
        - Order confirmations
        
        Kids Kingdom Team
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = formataddr(('Kids Kingdom', sender_email))
        msg['To'] = test_recipient
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Connect and send
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        
        print("✅ SUCCESS! Test email sent successfully!")
        print(f"📬 Check your inbox at: {test_recipient}")
        print("\n" + "=" * 60)
        print("🎉 Your Gmail SMTP configuration is working!")
        print("=" * 60)
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print("❌ AUTHENTICATION ERROR!")
        print("\n" + "=" * 60)
        print("🔧 HOW TO FIX:")
        print("=" * 60)
        print("1. Enable 2-Factor Authentication on your Gmail account")
        print("   → https://myaccount.google.com/security")
        print("\n2. Generate an App Password")
        print("   → https://myaccount.google.com/apppasswords")
        print("   → Select 'Mail' and 'Other (Custom name)'")
        print("   → Name it 'Kids Kingdom App'")
        print("   → Copy the 16-character password")
        print("\n3. Update your supabase.env file:")
        print(f"   MAIL_APP_PASSWORD=your_16_char_password_here")
        print("\n4. Restart your Flask application")
        print("=" * 60)
        print(f"\nError details: {e}")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nPlease check your internet connection and try again.")
        return False

if __name__ == "__main__":
    test_email_connection()
