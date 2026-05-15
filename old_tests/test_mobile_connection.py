import sys
sys.path.insert(0, r'C:\Users\mnban\Documents\kids\backend')

from app import app
import requests

print("="*70)
print("MOBILE APP CONNECTION TEST")
print("="*70)

# Test backend endpoints that mobile app uses
backend_url = "http://192.168.100.46:5000"

endpoints = [
    ("/api/health", "GET", "Health check"),
    ("/api/products", "GET", "Get products"),
    ("/api/login", "POST", "Login endpoint"),
]

print(f"\nBackend URL: {backend_url}")
print("\nTesting API endpoints...\n")

for path, method, description in endpoints:
    url = f"{backend_url}{path}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json={}, timeout=5)
        
        status = "OK" if response.status_code < 400 else "FAIL"
        print(f"[{status}] {method} {path}")
        print(f"     {description}")
        print(f"     Status: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] {method} {path}")
        print(f"     {description}")
        print(f"     ERROR: Cannot connect to backend")
    except Exception as e:
        print(f"[FAIL] {method} {path}")
        print(f"     {description}")
        print(f"     ERROR: {e}")
    print()

print("="*70)
print("MOBILE APP CONFIGURATION")
print("="*70)
print("\nIn mobile_app/lib/config/url_config.dart:")
print(f"  backendHost = '192.168.100.46'")
print(f"  backendPort = 5000")
print(f"  baseUrl = '{backend_url}'")
print("\nMake sure:")
print("  1. Flask server is running on 192.168.100.46:5000")
print("  2. Mobile device is on same network")
print("  3. Firewall allows port 5000")
print("\n" + "="*70)
