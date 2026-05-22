#!/usr/bin/env python3
"""
Test Email Configuration
Tests if the email credentials in .env are working correctly.
"""

import os
import smtplib
import socket
from email.mime.text import MIMEText
from email.utils import formataddr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MAIL_SENDER = os.getenv('MAIL_SENDER', 'charlesgabrielle.banagan@lspu.edu.ph')
MAIL_APP_PASSWORD = os.getenv('MAIL_APP_PASSWORD', 'uadirdemyawgaemu')
MAIL_SENDER_NAME = os.getenv('MAIL_SENDER_NAME', 'Kids Kingdom')

print("=" * 60)
print("Kids Kingdom - Email Configuration Test")
print("=" * 60)
print(f"\n📧 Testing email configuration...")
print(f"   Sender: {MAIL_SENDER}")
print(f"   Name: {MAIL_SENDER_NAME}")
print(f"   Password: {'*' * len(MAIL_APP_PASSWORD)}")
print()

# Test recipient (send to yourself)
test_recipient = input(f"Enter test recipient email (press Enter to use {MAIL_SENDER}): ").strip()
if not test_recipient:
    test_recipient = MAIL_SENDER

print(f"\n🔄 Attempting to send test email to: {test_recipient}")
print()

try:
    # Set timeout
    socket.setdefaulttimeout(15)
    
    # Create message
    subject = "✅ Kids Kingdom Email Test - Success!"
    body = f"""Hello!

This is a test email from Kids Kingdom.

If you're reading this, your email configuration is working correctly! 🎉

Configuration Details:
- Sender: {MAIL_SENDER}
- Sender Name: {MAIL_SENDER_NAME}
- SMTP Server: smtp.gmail.com:465 (SSL)
- Timeout: 15 seconds

Best regards,
Kids Kingdom Team

---
This is an automated test message.
"""
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = formataddr((MAIL_SENDER_NAME, MAIL_SENDER))
    msg['To'] = test_recipient
    
    print("⏳ Connecting to Gmail SMTP server...")
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15) as smtp:
        print("✅ Connected!")
        
        print("⏳ Authenticating...")
        smtp.login(MAIL_SENDER, MAIL_APP_PASSWORD)
        print("✅ Authenticated!")
        
        print("⏳ Sending email...")
        smtp.send_message(msg)
        print("✅ Email sent successfully!")
    
    print()
    print("=" * 60)
    print("✅ SUCCESS! Email configuration is working correctly.")
    print("=" * 60)
    print(f"\n📬 Check your inbox at: {test_recipient}")
    print()

except smtplib.SMTPAuthenticationError as e:
    print()
    print("=" * 60)
    print("❌ AUTHENTICATION FAILED!")
    print("=" * 60)
    print(f"\nError: {str(e)}")
    print("\n🔧 How to fix:")
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Enable 2-Step Verification")
    print("3. Go to: https://myaccount.google.com/apppasswords")
    print("4. Generate a new App Password:")
    print("   → Select 'Mail' and 'Windows Computer'")
    print("   → Copy the 16-character password")
    print("\n5. Update backend/.env file:")
    print(f"   MAIL_APP_PASSWORD=your_new_password_here")
    print("\n6. Restart Flask application")
    print("=" * 60)
    print()

except socket.timeout:
    print()
    print("=" * 60)
    print("❌ CONNECTION TIMEOUT!")
    print("=" * 60)
    print("\n🔧 Possible causes:")
    print("1. Firewall blocking port 465")
    print("2. No internet connection")
    print("3. Gmail SMTP server is down (rare)")
    print("\n🔧 How to fix:")
    print("1. Check your internet connection")
    print("2. Check firewall settings (allow port 465)")
    print("3. Try again in a few minutes")
    print("=" * 60)
    print()

except smtplib.SMTPException as e:
    print()
    print("=" * 60)
    print("❌ SMTP ERROR!")
    print("=" * 60)
    print(f"\nError: {str(e)}")
    print("\n🔧 This might be a temporary issue. Try again in a few minutes.")
    print("=" * 60)
    print()

except Exception as e:
    print()
    print("=" * 60)
    print("❌ UNEXPECTED ERROR!")
    print("=" * 60)
    print(f"\nError: {str(e)}")
    print("\n🔧 Please check:")
    print("1. .env file exists in backend/ folder")
    print("2. MAIL_SENDER and MAIL_APP_PASSWORD are set correctly")
    print("3. No typos in email address or password")
    print("=" * 60)
    print()
