import re

# Read the app.py file
with open('c:/Users/mnban/Documents/kids/backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The new endpoint code
new_endpoint = '''

@app.route('/api/v1/buyer/orders/<int:order_id>/rating', methods=['POST'])
@token_required
def buyer_submit_rating(order_id):
    """Submit order rating with optional media files - for mobile app."""
    try:
        # Verify order belongs to user
        orders = get_data('order', filters={'id': order_id, 'buyer_id': request.current_user_id})
        if not orders or len(orders) == 0:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        order = orders[0]
        
        # Get rating and comment from form data (multipart)
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({'success': False, 'error': 'Invalid rating (must be 1-5)'}), 400
        
        # Handle media files
        media_urls = []
        if request.files:
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'reviews')
            os.makedirs(upload_dir, exist_ok=True)
            
            for key in request.files:
                file = request.files[key]
                if file and file.filename:
                    # Save file
                    filename = secure_filename(f"{order_id}_{int(time.time())}_{file.filename}")
                    filepath = os.path.join(upload_dir, filename)
                    file.save(filepath)
                    
                    # Determine media type
                    ext = filename.lower().split('.')[-1]
                    media_type = 'video' if ext in ['mp4', 'mov', 'avi', 'webm'] else 'image'
                    media_urls.append({
                        'type': media_type,
                        'path': f'/static/uploads/reviews/{filename}'
                    })
        
        # Update order rating
        update_data_by_id('order', order_id, {
            'rating': rating,
            'review': comment,
            'review_media': json.dumps(media_urls) if media_urls else None
        })
        
        # Get buyer info
        buyer = get_data_by_id('user', request.current_user_id)
        buyer_name = f"{buyer.get('first_name', '')} {buyer.get('last_name', '')}".strip() or 'Anonymous'
        buyer_avatar = buyer.get('profile_image')
        
        # Extract category ratings from comment
        category_ratings = ''
        if comment and ('Product Quality:' in comment or 'Delivery Speed:' in comment):
            lines = comment.split('\\n')
            rating_lines = [line for line in lines if any(cat in line for cat in ['Product Quality:', 'Delivery Speed:', 'Packaging:', 'Rider Service:'])]
            if rating_lines:
                category_ratings = ', '.join(rating_lines)
        
        # Create product reviews for each item in the order
        order_items = get_data('order_item', filters={'order_id': order_id})
        if order_items:
            for item in order_items:
                product_id = item.get('product_id')
                if not product_id:
                    continue
                
                # Create review
                review_data = {
                    'product_id': product_id,
                    'user_id': request.current_user_id,
                    'buyer_id': request.current_user_id,
                    'buyer_name': buyer_name,
                    'buyer_avatar': buyer_avatar,
                    'rating': rating,
                    'title': '',
                    'content': comment,
                    'media': json.dumps(media_urls) if media_urls else None,
                    'category_ratings': category_ratings,
                    'verified_purchase': True,
                    'order_id': order_id,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                insert_data('review', review_data)
                
                # Update product rating
                reviews = get_data('review', filters={'product_id': product_id})
                if reviews:
                    avg_rating = sum(r.get('rating', 0) for r in reviews) / len(reviews)
                    review_count = len(reviews)
                    
                    update_data_by_id('product', product_id, {
                        'rating': round(avg_rating, 1),
                        'review_count': review_count
                    })
        
        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully'
        })
        
    except Exception as e:
        app.logger.error(f'buyer_submit_rating error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500

'''

# Find the location to insert (after buyer_confirm_delivery function)
# Look for the pattern: the end of buyer_confirm_delivery and before buyer_get_addresses
pattern = r"(@app\.route\('/api/v1/buyer/addresses', methods=\['GET'\]\))"

# Insert the new endpoint before buyer_get_addresses
new_content = re.sub(pattern, new_endpoint + r"\1", content, count=1)

# Write back
with open('c:/Users/mnban/Documents/kids/backend/app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Rating endpoint added successfully!")
print("Location: After buyer_confirm_delivery, before buyer_get_addresses")
