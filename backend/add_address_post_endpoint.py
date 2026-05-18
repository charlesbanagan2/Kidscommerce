"""
Add POST /api/v1/buyer/addresses endpoint to app.py
This allows mobile app to save new addresses for buyers
"""

import re

# Read the app.py file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the GET addresses endpoint
get_addresses_pattern = r"(@app\.route\('/api/v1/buyer/addresses', methods=\['GET'\]\).*?\ndef buyer_get_addresses\(\):.*?(?=\n@app\.route|\nclass |\Z))"

# The new POST endpoint to add
post_endpoint = '''@app.route('/api/v1/buyer/addresses', methods=['POST'])
@token_required
@active_user_required
def buyer_add_address():
    """Add a new address for the current buyer"""
    try:
        user_id = request.current_user_id
        data = request.get_json() or {}
        
        # Validate required fields
        label = (data.get('label') or '').strip()
        full_address = (data.get('full_address') or '').strip()
        
        if not label:
            return jsonify({'success': False, 'message': 'Address label is required'}), 400
        if not full_address:
            return jsonify({'success': False, 'message': 'Full address is required'}), 400
        
        # Create new address
        new_address = Address(
            user_id=user_id,
            label=label,
            full_address=full_address,
            street=data.get('street_address'),
            city=data.get('city'),
            province=data.get('province'),
            barangay=data.get('barangay'),
            region=data.get('region'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            is_default=data.get('is_default', False)
        )
        
        # Also add zip_code if provided
        if 'zip_code' in data:
            new_address.zip_code = data.get('zip_code')
        
        # If no zip_code field exists on the model yet, don't set it
        # The migration will handle adding it if needed
        
        db.session.add(new_address)
        
        # If this is set as default, unset other defaults for this user
        if new_address.is_default:
            Address.query.filter(
                Address.user_id == user_id,
                Address.id != new_address.id
            ).update({Address.is_default: False})
        
        db.session.commit()
        
        # Return the created address
        response = {
            'success': True,
            'message': 'Address added successfully',
            'address': {
                'id': new_address.id,
                'label': new_address.label,
                'full_address': new_address.full_address,
                'street_address': new_address.street,
                'city': new_address.city,
                'province': new_address.province,
                'barangay': new_address.barangay,
                'region': new_address.region,
                'zip_code': getattr(new_address, 'zip_code', ''),
                'is_default': new_address.is_default,
                'latitude': new_address.latitude,
                'longitude': new_address.longitude,
                'created_at': new_address.created_at.isoformat() if new_address.created_at else None
            }
        }
        return jsonify(response), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.exception('Error adding address')
        return jsonify({'success': False, 'message': f'Error adding address: {str(e)}'}), 500

'''

# Check if the endpoint already exists
if "@app.route('/api/v1/buyer/addresses', methods=['POST'])" in content:
    print("POST endpoint already exists")
    exit(0)

# Find where to insert the new endpoint
# Look for the closing of the GET addresses function (marked by the next @app.route)
# We'll insert before the next @app.route that comes after buyer_get_addresses

# Find the GET addresses endpoint
get_match = re.search(r"@app\.route\('/api/v1/buyer/addresses', methods=\['GET'\]\)\n@token_required\n", content)

if not get_match:
    print("Could not find GET addresses endpoint")
    exit(1)

# Find the next @app.route after the GET endpoint
start_pos = get_match.end()
next_route = re.search(r"\n@app\.route\(", content[start_pos:])

if next_route:
    insert_pos = start_pos + next_route.start()
else:
    print("Could not find next route after addresses GET")
    exit(1)

# Insert the new endpoint
new_content = content[:insert_pos] + '\n' + post_endpoint + content[insert_pos:]

# Write back to file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✓ POST /api/v1/buyer/addresses endpoint added successfully")
