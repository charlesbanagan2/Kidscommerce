"""
Vercel entry point - index.py
This is the main entry point that Vercel will use
"""
from app import app

# Vercel looks for 'app' or 'application' variable
application = app

# For local testing
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
