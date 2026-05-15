"""
Kids & Baby E-commerce Platform - Application Launcher
Run this file to start the application
"""
from app import app, socketio

if __name__ == '__main__':
    print("=" * 60)
    print("Kids & Baby E-commerce Platform")
    print("=" * 60)
    
    print("\nStarting application...")
    print("Access the application at: http://localhost:5000")
    print("Supabase configuration is loaded from mobile_app/lib/kids_commercedb/supabase.env")
    print("Press CTRL+C to stop the server\n")
    print("=" * 60)
    
    # Run with SocketIO to enable real-time features
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
