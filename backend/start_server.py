#!/usr/bin/env python3
"""
Kids E-commerce Server Startup Script
Run this script to start the Flask server with mobile API support
"""

import socket
import subprocess
import sys
import os

def get_local_ip():
    """Get the local IP address for network access"""
    try:
        # Create a socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def main():
    print("=" * 60)
    print("KIDS E-COMMERCE MOBILE API SERVER")
    print("=" * 60)
    
    # Get local IP
    local_ip = get_local_ip()
    
    print(f"Local Network IP: {local_ip}")
    print(f"Web Interface: http://127.0.0.1:5000")
    print(f"Mobile API Base: http://{local_ip}:5000/api/v1")
    print(f"Socket.IO: ws://{local_ip}:5000/socket.io/")
    print()
    print("API ENDPOINTS READY FOR TESTING:")
    print("  POST /api/v1/auth/login")
    print("  POST /api/v1/auth/register") 
    print("  GET  /api/v1/products")
    print("  GET  /api/v1/categories")
    print("  GET  /api/v1/orders (requires auth)")
    print("  GET  /api/v1/user/profile (requires auth)")
    print()
    print("POSTMAN TESTING:")
    print(f"  1. Set base_url: http://{local_ip}:5000/api/v1")
    print("  2. Test login endpoint")
    print("  3. Copy access_token to environment variable")
    print("  4. Test protected endpoints")
    print()
    print("FLUTTER INTEGRATION:")
    print(f"  1. Update API base URL to: http://{local_ip}:5000/api/v1")
    print(f"  2. Socket.IO URL: ws://{local_ip}:5000/socket.io/")
    print("  3. Use JWT tokens for authentication")
    print("  4. Implement real-time features with Socket.IO events")
    print()
    print("=" * 60)
    print("Starting Flask server...")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Start the Flask app
    try:
        from app import app, socketio
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
