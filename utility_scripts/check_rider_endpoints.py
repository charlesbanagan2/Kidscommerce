import sys
sys.path.insert(0, r'C:\Users\mnban\Documents\kids\backend')

print("="*70)
print("RIDER API ENDPOINTS CHECK")
print("="*70)

# Read app.py and find all rider-related routes
with open(r'C:\Users\mnban\Documents\kids\backend\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

rider_routes = []
for i, line in enumerate(lines):
    if '@app.route' in line and ('rider' in line.lower() or 'qr' in line.lower()):
        # Get the route
        route_line = line.strip()
        # Get the function name (next line usually)
        if i + 1 < len(lines):
            func_line = lines[i + 1].strip()
            rider_routes.append((i+1, route_line, func_line))

print("\nFound Rider Routes:")
print("-"*70)
for line_num, route, func in rider_routes:
    print(f"Line {line_num}: {route}")
    print(f"         {func}")
    print()

# Check what mobile app expects
print("\n" + "="*70)
print("MOBILE APP EXPECTED ENDPOINTS")
print("="*70)

mobile_endpoints = [
    ("GET", "/api/orders/rider", "Get rider orders"),
    ("GET", "/api/rider/earnings", "Get rider earnings"),
    ("PUT", "/api/orders/status", "Update order status"),
    ("POST", "/api/v1/rider/orders/{id}/accept", "Accept order"),
    ("POST", "/api/v1/rider/orders/{id}/decline", "Decline order"),
    ("POST", "/api/v1/qr-scan", "QR code scan"),
]

print("\nMobile App Calls:")
for method, endpoint, desc in mobile_endpoints:
    print(f"  {method:6} {endpoint:40} - {desc}")

print("\n" + "="*70)
print("VERIFICATION NEEDED")
print("="*70)
print("\nCheck if these endpoints exist in backend:")
print("1. /api/orders/rider - Get rider's assigned orders")
print("2. /api/rider/earnings - Get earnings breakdown")
print("3. /api/orders/status - Update order status")
print("4. /api/v1/rider/orders/{id}/accept - Accept delivery")
print("5. /api/v1/rider/orders/{id}/decline - Decline delivery")
print("6. /api/v1/qr-scan - Verify delivery with QR")
print("\n" + "="*70)
