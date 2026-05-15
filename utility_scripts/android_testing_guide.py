#!/usr/bin/env python
"""Android Phone Testing Guide"""
import requests
import json
import socket
import os

# Get machine IP
def get_local_ip():
    """Get local machine IP on the network"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.20"

API_URL = "http://192.168.1.20:5000"

print("=" * 70)
print("ANDROID PHONE TESTING GUIDE - Kids Kingdom")
print("=" * 70)

# 1. Verify backend is running
print("\n1. Verifying Backend API...")
try:
    response = requests.get(f"{API_URL}/", timeout=5)
    print(f"   ✓ Backend is RUNNING (Status: {response.status_code})")
except Exception as e:
    print(f"   ✗ Backend is NOT running: {e}")
    print("\n   Action: Make sure the backend server is running!")
    print("   Run: python app.py in c:\\Users\\mnban\\Documents\\kids\\backend")
    exit(1)

# 2. Test login endpoint
print("\n2. Testing Login API Endpoint...")
try:
    response = requests.post(
        f"{API_URL}/api/v1/auth/login",
        json={"email": "testbuyer@test.com", "password": "test123"},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"   ✓ Login API is working")
            user = data.get('user', {})
            print(f"     Email: {user.get('email')}")
            print(f"     Role: {user.get('role')}")
        else:
            print(f"   ⚠ Login returned: {data.get('error')}")
    else:
        print(f"   ✗ API Error: {response.status_code}")
except Exception as e:
    print(f"   ✗ Connection failed: {e}")

# 3. Network configuration
print("\n3. Network Configuration:")
print(f"   Backend IP: 192.168.1.20")
print(f"   Backend Port: 5000")
print(f"   Backend URL: {API_URL}")

# 4. Android Phone Instructions
print("\n4. ANDROID PHONE SETUP:")
print("   ✓ Make sure your Android phone is on the SAME WiFi network")
print("   ✓ The phone should see: 192.168.1.20:5000")
print("\n   Step 1: Open Flutter app on your Android phone")
print("   Step 2: App will automatically detect it's Android")
print("   Step 3: App will connect to: 192.168.1.20:5000")
print("   Step 4: Login with these credentials:")
print("           Email: testbuyer@test.com")
print("           Password: test123")

# 5. Troubleshooting
print("\n5. IF LOGIN FAILS:")
print("   ⚠ Check Network:")
print("      - Is Android phone connected to WiFi?")
print("      - Can you ping 192.168.1.20 from your phone?")
print("   ⚠ Check Backend:")
print("      - Is backend running on 192.168.1.20:5000?")
print("      - Check backend terminal for errors")
print("   ⚠ Check Firewall:")
print("      - Allow port 5000 through Windows Firewall")

# 6. Test account info
print("\n6. TEST ACCOUNT DETAILS:")
print("   Email: testbuyer@test.com")
print("   Password: test123")
print("   Role: buyer")
print("   Status: active")

print("\n" + "=" * 70)
print("READY FOR ANDROID TESTING")
print("=" * 70)
