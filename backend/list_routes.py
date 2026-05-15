#!/usr/bin/env python3
"""
List all registered Flask routes
Run this to verify rider routes are loaded
"""

import sys
sys.path.insert(0, 'c:\\Users\\mnban\\Documents\\kids\\backend')

try:
    from app import app
    
    print("\n" + "="*80)
    print("REGISTERED FLASK ROUTES")
    print("="*80)
    
    # Get all routes
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
            'path': str(rule)
        })
    
    # Sort by path
    routes.sort(key=lambda x: x['path'])
    
    # Filter and display rider routes
    rider_routes = [r for r in routes if '/rider' in r['path']]
    
    if rider_routes:
        print(f"\n✅ RIDER ROUTES FOUND ({len(rider_routes)} routes):")
        print("-"*80)
        for route in rider_routes:
            print(f"{route['methods']:15} {route['path']}")
    else:
        print("\n❌ NO RIDER ROUTES FOUND!")
        print("   The rider_mobile_only_api.py module was not loaded.")
        print("   Make sure the backend server was restarted.")
    
    # Show all API routes
    api_routes = [r for r in routes if '/api/' in r['path']]
    print(f"\n📋 ALL API ROUTES ({len(api_routes)} routes):")
    print("-"*80)
    for route in api_routes:
        print(f"{route['methods']:15} {route['path']}")
    
    print("\n" + "="*80)
    print(f"Total routes registered: {len(routes)}")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"\n❌ Error loading Flask app: {e}")
    print("\nMake sure:")
    print("  1. You're in the backend directory")
    print("  2. All dependencies are installed")
    print("  3. The Flask app can start without errors")
