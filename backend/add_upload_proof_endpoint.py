import os

# Read the app.py file
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with mark-delivered endpoint (line 16319 in 1-indexed)
insert_line = 16318  # 0-indexed

# New endpoint code
new_endpoint = '''
@app.route('/api/v1/rider/orders/<int:order_id>/upload-proof', methods=['POST'])
@token_required
@role_required('rider')
def api_rider_upload_proof(order_id):
    """Upload delivery proof photo"""
    try:
        order = get_data_by_id('order', order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.get('rider_id') != request.current_user_id:
            return jsonify({'error': 'Not authorized'}), 403
        
        if 'proof_photo' not in request.files:
            return jsonify({'error': 'No photo provided'}), 400
        
        file = request.files['proof_photo']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file
        filename = f"proof_{order_id}_{int(datetime.utcnow().timestamp())}.jpg"
        upload_folder = os.path.join('static', 'uploads', 'delivery_proofs')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Update order with proof photo URL
        photo_url = f"/static/uploads/delivery_proofs/{filename}"
        update_data_by_id('order', order_id, {
            'proof_photo_url': photo_url,
            'updated_at': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            'success': True,
            'photo_url': photo_url
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error uploading proof: {e}")
        return jsonify({'error': str(e)}), 500

'''

# Insert the new endpoint
lines.insert(insert_line, new_endpoint)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Upload proof endpoint added successfully")
