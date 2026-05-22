"""
Vercel Serverless Function Entry Point
"""
import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_path)

# Import the Flask app
from app import app

# Export for Vercel
def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, lambda *args: None)

# For direct access
application = app
