#!/usr/bin/env python3
"""Debug script to check Order #55 data"""

import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment
env_path = os.path.join(os.path.dirname(__file__), 'backend', 'supabase_env')
load_dotenv(env_path, override=True)

from app import app, get_data, get_data_by_id

# Use Flask app context
with app.app_context():
    # Fetch Order #55
    print("🔍 Fetching Order #55...")
    orders = get_data('order', filters={'id': 55})

    if not orders:
        print("❌ Order #55 not found")
        sys.exit(1)

    order = orders[0]
    print(f"✅ Order #55 found")
    print(f"\nOrder Data:")
    print(f"  id: {order.get('id')}")
    print(f"  status: {order.get('status')}")
    print(f"  buyer_id: {order.get('buyer_id')}")
    print(f"  rider_id: {order.get('rider_id')}")
    print(f"  picked_up_by: {order.get('picked_up_by')}")
    print(f"  delivered_by: {order.get('delivered_by')}")

    # Check rider
    rider_id = order.get('rider_id') or order.get('picked_up_by') or order.get('delivered_by')
    print(f"\nResolved rider_id: {rider_id}")

    if rider_id:
        print(f"🔍 Fetching Rider #{rider_id}...")
        rider = get_data_by_id('user', rider_id)
        if rider:
            print(f"✅ Rider found")
            print(f"  id: {rider.get('id')}")
            print(f"  first_name: {rider.get('first_name')}")
            print(f"  last_name: {rider.get('last_name')}")
            print(f"  name: {rider.get('name')}")
            print(f"  phone: {rider.get('phone')}")
            print(f"  profile_picture: {rider.get('profile_picture')}")
            
            # Simulate serialization
            rider_name = f"{rider.get('first_name', '')} {rider.get('last_name', '')}".strip()
            rider_phone = rider.get('phone')
            rider_profile_picture = rider.get('profile_picture')
            
            print(f"\nSerialized Rider Data:")
            print(f"  rider_name: {rider_name}")
            print(f"  rider_phone: {rider_phone}")
            print(f"  rider_profile_picture: {rider_profile_picture}")
        else:
            print(f"❌ Rider #{rider_id} not found")
    else:
        print(f"❌ No rider assigned to Order #55")
