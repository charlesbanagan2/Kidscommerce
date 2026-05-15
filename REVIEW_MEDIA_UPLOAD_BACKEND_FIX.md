# Review Media Upload Backend Fix

## Problem
Images uploaded by buyers in reviews are not being saved to the database.

## Backend Fix Required

Add this endpoint to `backend/app.py`:

```python
@app.route('/api/v1/buyer/orders/<int:order_id>/rating', methods=['POST'])
@jwt_required()
def submit_order_rating_with_media(order_id):
    """Submit order rating with optional media files"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get form data
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({'success': False, 'error': 'Invalid rating'}), 400
        
        # Verify order belongs to user
        order = supabase.table('orders').select('*').eq('id', order_id).eq('buyer_id', current_user_id).execute()
        if not order.data:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        # Handle media files
        media_urls = []
        if request.files:
            for key in request.files:
                file = request.files[key]
                if file and file.filename:
                    # Save file
                    filename = secure_filename(f"{order_id}_{int(time.time())}_{file.filename}")
                    filepath = os.path.join('static/uploads/reviews', filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    file.save(filepath)
                    
                    # Determine media type
                    media_type = 'video' if filename.lower().endswith(('.mp4', '.mov', '.avi')) else 'image'
                    media_urls.append({
                        'type': media_type,
                        'path': f'/uploads/reviews/{filename}'
                    })
        
        # Update order rating
        supabase.table('orders').update({
            'rating': rating,
            'review': comment,
            'review_media': media_urls  # Store as JSON
        }).eq('id', order_id).execute()
        
        # Also create product reviews for each item
        order_items = supabase.table('order_items').select('product_id').eq('order_id', order_id).execute()
        
        # Get buyer info
        buyer = supabase.table('users').select('first_name, last_name, profile_image').eq('id', current_user_id).single().execute()
        buyer_name = f"{buyer.data.get('first_name', '')} {buyer.data.get('last_name', '')}".strip() or 'Anonymous'
        buyer_avatar = buyer.data.get('profile_image')
        
        # Extract category ratings from comment
        category_ratings = ''
        if 'Product Quality:' in comment or 'Delivery Speed:' in comment:
            lines = comment.split('\n')
            for line in lines:
                if any(cat in line for cat in ['Product Quality:', 'Delivery Speed:', 'Packaging:', 'Rider Service:']):
                    category_ratings = line if not category_ratings else f"{category_ratings}, {line}"
        
        for item in order_items.data:
            product_id = item['product_id']
            
            # Create review
            review_data = {
                'product_id': product_id,
                'buyer_id': current_user_id,
                'buyer_name': buyer_name,
                'buyer_avatar': buyer_avatar,
                'rating': rating,
                'title': '',
                'content': comment,
                'media': media_urls,
                'category_ratings': category_ratings,
                'created_at': datetime.utcnow().isoformat()
            }
            
            supabase.table('reviews').insert(review_data).execute()
            
            # Update product rating
            reviews = supabase.table('reviews').select('rating').eq('product_id', product_id).execute()
            if reviews.data:
                avg_rating = sum(r['rating'] for r in reviews.data) / len(reviews.data)
                review_count = len(reviews.data)
                
                supabase.table('products').update({
                    'rating': round(avg_rating, 1),
                    'review_count': review_count
                }).eq('id', product_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully'
        })
        
    except Exception as e:
        print(f"Error submitting rating: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

## Database Schema Update

Ensure the `reviews` table has these columns:

```sql
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS buyer_name VARCHAR(255);
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS buyer_avatar TEXT;
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS media JSONB;
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS category_ratings TEXT;
```

Also update `orders` table:

```sql
ALTER TABLE orders ADD COLUMN IF NOT EXISTS review_media JSONB;
```

## Frontend Already Fixed

The Flutter app has been updated to:
1. Show only 1 review preview (not 2)
2. Always show "See All" button
3. Display category ratings
4. Add star rating filter (All, 5★, 4★, 3★, 2★, 1★)
5. Use correct buyer name and avatar from `buyer_name` and `buyer_avatar` fields

## Testing

1. Restart backend: `python backend/app.py`
2. Complete an order
3. Rate the order with photos/videos
4. Check that media appears in product reviews
5. Verify buyer name and avatar are correct
6. Test the star filter on reviews screen
