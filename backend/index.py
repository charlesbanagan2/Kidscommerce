"""
Vercel entry point - index.py
This is the main entry point that Vercel will use
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app

# Vercel looks for 'app' variable
app = app

# For local testing
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
