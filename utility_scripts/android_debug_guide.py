#!/usr/bin/env python
"""Android Connection Troubleshooting Guide"""
import socket
import requests
import json

print("=" * 80)
print("ANDROID CONNECTION DEBUGGING GUIDE - Kids Kingdom")
print("=" * 80)

# 1. Check backend server
print("\n1. CHECKING BACKEND SERVER...")
API_URL = "http://192.168.1.20:5000"
try:
    response = requests.get(f"{API_URL}/", timeout=5)
    print(f"   ✓ Backend is running (Status: {response.status_code})")
except Exception as e:
    print(f"   ✗ Backend is NOT running")
    print(f"     Error: {e}")
    print(f"     ACTION: Start backend server:")
    print(f"             cd c:\\Users\\mnban\\Documents\\kids\\backend")
    print(f"             python app.py")
    exit(1)

# 2. Verify API endpoint
print("\n2. CHECKING API ENDPOINTS...")
endpoints = [
    ('/api/v1/auth/login', 'POST'),
    ('/api/v1/auth/register', 'POST'),
]

for endpoint, method in endpoints:
    try:
        if method == 'POST':
            response = requests.post(
                f"{API_URL}{endpoint}",
                json={},
                timeout=5
            )
        print(f"   ✓ {method} {endpoint} - Reachable (Status: {response.status_code})")
    except Exception as e:
        print(f"   ✗ {method} {endpoint} - Failed: {e}")

# 3. Test login with correct IP
print("\n3. TESTING LOGIN WITH 192.168.1.20:5000...")
login_url = f"{API_URL}/api/v1/auth/login"
try:
    response = requests.post(
        login_url,
        json={"email": "testbuyer@test.com", "password": "test123"},
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"   ✓ Login API Working!")
            print(f"     User: {data['user']['email']}")
            print(f"     Role: {data['user']['role']}")
        else:
            print(f"   ⚠ API returned error: {data.get('error')}")
    else:
        print(f"   ✗ API Error: {response.status_code}")
except Exception as e:
    print(f"   ✗ Connection failed: {e}")

# 4. Network configuration info
print("\n4. NETWORK INFORMATION...")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    print(f"   Server IP: {local_ip}")
    print(f"   Backend URL: {API_URL}")
except:
    print(f"   Could not determine local IP")

# 5. Android Configuration
print("\n5. FLUTTER APP CONFIGURATION (Android)...")
print(f"   Backend URL in app: 192.168.1.20:5000")
print(f"   This is hardcoded in: lib/services/api_service.dart")
print(f"   Line: baseUrl = 'http://192.168.1.20:5000';")

# 6. Android Troubleshooting
print("\n6. IF LOGIN FAILS ON ANDROID DEVICE:")
print("   ═" * 40)
print()
print("   STEP 1: Verify Network Connection")
print("   ─────────────────────────────────")
print("   ✓ Check Android is on SAME WiFi network")
print("   ✓ Try: adb logcat | grep -i 'connection\\|error'")
print("   ✓ Check WiFi signal strength on phone")
print()
print("   STEP 2: Check Network Connectivity")
print("   ──────────────────────────────────")
print("   ✓ On Android phone terminal app, try:")
print("     ping 192.168.1.20")
print("     Or use Network Diagnostic app")
print()
print("   STEP 3: Check Firewall Settings")
print("   ───────────────────────────────")
print("   ✓ Windows Defender Firewall:")
print("     1. Open Windows Defender Firewall")
print("     2. Click 'Allow an app through firewall'")
print("     3. Find Python (backend process)")
print("     4. Check both Private and Public")
print("     5. Click OK")
print()
print("   STEP 4: Check Backend Logs")
print("   ──────────────────────────")
print("   ✓ Look at backend terminal for errors")
print("   ✓ Check if request even reaches backend")
print("   ✓ Look for CORS or connection errors")
print()
print("   STEP 5: Enable Debug Logging")
print("   ───────────────────────────")
print("   ✓ Check Flutter console for actual error message")
print("   ✓ The error message now shows actual exception, not just 'Check connection'")
print("   ✓ Look for: 'Login Error: ...' in console")
print()

# 7. Common Issues
print("\n7. COMMON ISSUES & SOLUTIONS:")
print("   ═" * 40)
print()
print("   ISSUE: 'Connection failed' error")
print("   ──────────────────────────────")
print("   CAUSES:")
print("      • Phone not on same WiFi as backend")
print("      • Backend not running")
print("      • Firewall blocking port 5000")
print("      • Wrong IP address in app code")
print("   SOLUTION:")
print("      • Verify WiFi connection")
print("      • Restart backend")
print("      • Check firewall rules")
print("      • Verify IP: 192.168.1.20")
print()
print("   ISSUE: 'Invalid credentials' error")
print("   ────────────────────────────────")
print("   CAUSES:")
print("      • Wrong email/password")
print("      • Test account doesn't exist")
print("      • Account suspended/rejected")
print("   SOLUTION:")
print("      • Verify test account exists")
print("      • Check database for account")
print("      • Verify account status = 'active'")
print()
print("   ISSUE: Backend not responding at all")
print("   ────────────────────────────────────")
print("   CAUSES:")
print("      • Backend crashed")
print("      • Wrong port (should be 5000)")
print("      • Database connection failed")
print("   SOLUTION:")
print("      • Check backend terminal for errors")
print("      • Restart backend")
print("      • Check database connection")
print()

# 8. Test Account Info
print("\n8. TEST ACCOUNT DETAILS:")
print("   ═" * 40)
print("   Email: testbuyer@test.com")
print("   Password: test123")
print("   Role: buyer")
print("   Status: active")
print()

print("=" * 80)
print("READY FOR ANDROID TESTING WITH DEBUGGING")
print("=" * 80)
