"""
WSGI entry point for Vercel deployment
"""
from app import app

# Vercel expects the Flask app to be named 'app'
# This file ensures compatibility with Vercel's Python runtime

# Export app for Vercel
application = app

if __name__ == "__main__":
    app.run()
