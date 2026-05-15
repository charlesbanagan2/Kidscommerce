"""
Quick Email Test - Verify if existing App Password works
"""

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

# Test credentials
SENDER = 'gbanagan33@gmail.com'
PASSWORD = 'hprhqjfxpdfahxsf'

print("=" * 60)
print("🧪 TESTING EXISTING APP PASSWORD")
print("=" * 60)
print(f"Email: {SENDER}")
print(f"Password: {PASSWORD}")
print("=" * 60)

try:
    print("\n⏳ Connecting to Gmail SMTP...")
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as smtp:
        print("✅ Connected!")
        print("⏳ Authenticating...")
        smtp.login(SENDER, PASSWORD)
        print("✅ Authentication successful!")
        
        # Send test email
        print("⏳ Sending test email...")
        msg = MIMEText("Test email from Kids Kingdom - Your SMTP is working!")
        msg['Subject'] = "✅ SMTP Test Success"
        msg['From'] = formataddr(('Kids Kingdom', SENDER))
        msg['To'] = SENDER
        
        smtp.send_message(msg)
        print("✅ Test email sent!")
        
    print("\n" + "=" * 60)
    print("🎉 SUCCESS! Your existing App Password is working!")
    print("=" * 60)
    print("\n✅ Your email configuration is ready to use!")
    print("✅ No need to generate a new App Password!")
    print("\n📧 Check your inbox at:", SENDER)
    
except smtplib.SMTPAuthenticationError as e:
    print("\n" + "=" * 60)
    print("❌ AUTHENTICATION FAILED!")
    print("=" * 60)
    print("\nThe existing password 'hprhqjfxpdfahxsf' is no longer valid.")
    print("\n🔧 YOU NEED TO GENERATE A NEW APP PASSWORD:")
    print("\n1. Go to: https://myaccount.google.com/security")
    print("   → Enable 2-Factor Authentication (if not enabled)")
    print("\n2. Go to: https://myaccount.google.com/apppasswords")
    print("   → Select 'Mail' and 'Other (Custom name)'")
    print("   → Name it 'Kids Kingdom App'")
    print("   → Copy the 16-character password")
    print("\n3. Update supabase.env file:")
    print("   MAIL_APP_PASSWORD=your_new_password_here")
    print("\n4. Restart Flask application")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nPlease check your internet connection and try again.")

print("\n")
