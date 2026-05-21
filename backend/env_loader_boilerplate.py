"""
Environment Variable Loader Boilerplate
========================================
Place this code at the TOP of your app.py file (after imports)

This securely loads environment variables from .env file using python-dotenv
and makes them available throughout your application via os.getenv()
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================

# Get the directory where app.py is located
BASE_DIR = Path(__file__).resolve().parent

# Load .env file from the same directory as app.py
# override=True ensures .env values take precedence over system environment variables
load_dotenv(dotenv_path=BASE_DIR / '.env', override=True)

# ============================================
# GOOGLE OAUTH CONFIGURATION
# ============================================

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# Validate Google OAuth credentials are loaded
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise ValueError(
        "❌ Google OAuth credentials not found in .env file. "
        "Please ensure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set."
    )

print(f"✅ Google OAuth loaded: {GOOGLE_CLIENT_ID[:20]}...")

# ============================================
# SUPABASE CONFIGURATION
# ============================================

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Validate Supabase configuration
if not SUPABASE_URL:
    raise ValueError(
        "❌ Supabase URL not found in .env file. "
        "Please ensure SUPABASE_URL is set."
    )

print(f"✅ Supabase configured: {SUPABASE_URL}")

# ============================================
# FLASK APPLICATION SETTINGS
# ============================================

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# ============================================
# SERVER CONFIGURATION
# ============================================

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# ============================================
# DATABASE CONFIGURATION
# ============================================

DATABASE_URL = os.getenv('DATABASE_URL')

# ============================================
# USAGE IN YOUR APPLICATION
# ============================================

"""
How to use these variables in your Flask app:

1. Flask App Configuration:
   app.config['SECRET_KEY'] = SECRET_KEY
   app.config['DEBUG'] = DEBUG

2. Google OAuth Setup:
   google_bp = make_google_blueprint(
       client_id=GOOGLE_CLIENT_ID,
       client_secret=GOOGLE_CLIENT_SECRET,
       scope=["openid", "email", "profile"],
       redirect_to="google_login_callback"
   )

3. Supabase Client:
   from supabase import create_client
   supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

4. Running the Server:
   if __name__ == "__main__":
       app.run(host=HOST, port=PORT, debug=DEBUG)
"""

# ============================================
# SECURITY BEST PRACTICES
# ============================================

"""
✅ DO:
- Keep .env file in .gitignore
- Use different .env files for dev/staging/production
- Rotate credentials regularly
- Use environment-specific values
- Validate all required variables on startup

❌ DON'T:
- Commit .env to version control
- Share .env files via email/chat
- Use production credentials in development
- Hardcode sensitive values in code
- Log sensitive environment variables
"""
