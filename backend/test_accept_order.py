import requests
import json

# Test the accept-order endpoint
url = "http://192.168.1.20:5000/api/v1/rider/accept-order"

# You need to replace this with a valid rider token
token = "YOUR_RIDER_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
    "order_id": 50
}

print("Testing accept-order endpoint...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")
print()

try:
    response = requests.post(url, headers=headers, json=data, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {str(e)}")
