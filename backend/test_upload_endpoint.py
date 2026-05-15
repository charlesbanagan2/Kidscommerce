"""Test script to verify the upload proof endpoint is registered"""
import requests

# Test if the endpoint exists (should return 401 without auth, not 404)
url = "http://192.168.1.20:5000/api/v1/rider/orders/22/upload-proof"

try:
    response = requests.post(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 404:
        print("\n❌ ENDPOINT NOT FOUND - Server needs to be restarted")
    elif response.status_code == 401:
        print("\n✅ ENDPOINT EXISTS - Returns 401 (authentication required)")
    else:
        print(f"\n⚠️ Unexpected status code: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")
