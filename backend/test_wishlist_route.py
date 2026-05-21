"""Test if wishlist route is registered"""
import sys
sys.path.insert(0, 'c:\\Users\\mnban\\OneDrive\\Desktop\\kids\\backend')

from app import app

print("=" * 60)
print("CHECKING WISHLIST ROUTE REGISTRATION")
print("=" * 60)

# List all routes
wishlist_routes = []
all_routes = []

for rule in app.url_map.iter_rules():
    all_routes.append(str(rule))
    if 'wishlist' in str(rule).lower():
        wishlist_routes.append({
            'endpoint': rule.endpoint,
            'methods': ','.join(rule.methods),
            'rule': str(rule)
        })

print(f"\nTotal routes registered: {len(all_routes)}")
print(f"\nWishlist routes found: {len(wishlist_routes)}")

if wishlist_routes:
    print("\nWISHLIST ROUTES REGISTERED:")
    for route in wishlist_routes:
        print(f"  - {route['rule']}")
        print(f"    Methods: {route['methods']}")
        print(f"    Endpoint: {route['endpoint']}")
else:
    print("\nNO WISHLIST ROUTES FOUND!")
    print("\nSearching for similar routes:")
    for route in all_routes:
        if '/api/v1/' in route:
            print(f"  - {route}")

print("\n" + "=" * 60)
