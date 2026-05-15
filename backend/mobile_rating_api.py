# Mobile Rating API Endpoint
# Add this to app.py or import it

from flask import request, jsonify
from werkzeug.utils import secure_filename
from sqlalchemy import text as sa_text
import os
from datetime import datetime

def register_mobile_rating_endpoints(app, db, Order, Review, token_required):
    """Register mobile rating endpoints with media upload support"""
    
    @app.route('/api/v1/buyer/orders/<int:order_id>/rating', methods=['POST'])
    @token_required
    def submit_order_rating_mobile(order_id):
        """Submit order rating with optional media files (images/videos)"""
        try:
            # Get order
            order = db.session.get(Order, order_id)
            if not order:
                return jsonify({'success': False, 'error': 'Order not found'}), 404
            
            # Verify order belongs to current user
            if order.buyer_id != request.current_user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            # Check if order is completed/delivered
            if order.status not in ['completed', 'delivered']:
                return jsonify({'success': False, 'error': 'Can only rate completed orders'}), 400
            
            # Get rating data
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Multipart form data (with files)
                rating = int(request.form.get('rating', 0))
                comment = request.form.get('comment', '').strip()
            else:
                # JSON data (no files)
                data = request.get_json() or {}
                rating = int(data.get('rating', 0))
                comment = data.get('comment', '').strip()
            
            # Validate rating
            if not (1 <= rating <= 5):
                return jsonify({'success': False, 'error': 'Rating must be between 1 and 5'}), 400
            
            # Process media files if present
            media_list = []
            if request.files:
                upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'reviews')
                os.makedirs(upload_dir, exist_ok=True)
                
                app.logger.info(f'Processing {len(request.files)} files for review')
                
                for key in request.files:
                    # Accept both 'media_X' and 'media[X]' formats
                    if key.startswith('media'):
                        file = request.files[key]
                        if file and file.filename:
                            # Secure filename
                            filename = secure_filename(file.filename)
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                            filename = timestamp + filename
                            
                            # Determine media type
                            ext = filename.rsplit('.', 1)[-1].lower()
                            media_type = 'video' if ext in ['mp4', 'mov', 'avi', 'mkv'] else 'image'
                            
                            # Save file
                            filepath = os.path.join(upload_dir, filename)
                            file.save(filepath)
                            
                            app.logger.info(f'Saved {media_type} file: {filename}')
                            
                            # Add to media list
                            media_list.append({
                                'type': media_type,
                                'path': f'/static/uploads/reviews/{filename}'
                            })
                
                app.logger.info(f'Total media files saved: {len(media_list)}')
            
            # Create reviews for each product in the order
            reviews_created = []
            for item in order.items:
                # Check if review already exists
                existing = Review.query.filter_by(
                    user_id=request.current_user_id,
                    product_id=item.product_id,
                    order_id=order_id
                ).first()
                
                if existing:
                    # Update existing review
                    existing.rating = rating
                    existing.content = comment
                    if media_list:
                        existing.media = media_list
                    reviews_created.append(existing)
                else:
                    # Create new review
                    review = Review(
                        product_id=item.product_id,
                        user_id=request.current_user_id,
                        order_id=order_id,
                        rating=rating,
                        content=comment,
                        verified_purchase=True,
                        media=media_list if media_list else None,
                        status='published'
                    )
                    db.session.add(review)
                    reviews_created.append(review)
            
            # Ensure the review ID sequence is aligned to avoid duplicate PKs.
            db.session.execute(
                sa_text(
                    "SELECT setval(pg_get_serial_sequence('review', 'id'), "
                    "COALESCE((SELECT MAX(id) FROM review), 1))"
                )
            )
            db.session.commit()
            
            # Update product ratings and review counts
            from sqlalchemy import func
            for item in order.items:
                # Calculate average rating for this product
                avg_rating = db.session.query(func.avg(Review.rating)).filter(
                    Review.product_id == item.product_id,
                    Review.status == 'published'
                ).scalar() or 0.0
                
                # Count reviews for this product
                review_count = db.session.query(func.count(Review.id)).filter(
                    Review.product_id == item.product_id,
                    Review.status == 'published'
                ).scalar() or 0
                
                # Update product using raw SQL to avoid model issues
                db.session.execute(
                    sa_text("UPDATE product SET rating = :rating, review_count = :count WHERE id = :id"),
                    {'rating': float(avg_rating), 'count': review_count, 'id': item.product_id}
                )
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Rating submitted successfully',
                'reviews_count': len(reviews_created)
            }), 200
            
        except ValueError as e:
            return jsonify({'success': False, 'error': 'Invalid rating value'}), 400
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f'Error submitting rating: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500
