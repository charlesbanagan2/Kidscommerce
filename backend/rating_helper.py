"""Helper functions for calculating product ratings"""
from sqlalchemy import func
from datetime import datetime


def calculate_product_rating(db, Review, product_id):
    """Calculate average rating and count for a product"""
    result = db.session.query(
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).filter(
        Review.product_id == product_id,
        Review.status == 'published'
    ).first()
    
    avg_rating = float(result.avg_rating or 0.0)
    review_count = int(result.review_count or 0)
    
    return avg_rating, review_count


def add_ratings_to_products(db, Review, products):
    """Add rating and review_count to a list of product dicts"""
    if not products:
        return products
    
    # Get all product IDs
    product_ids = [p.get('id') if isinstance(p, dict) else p.id for p in products]
    
    # Batch query all ratings
    ratings = db.session.query(
        Review.product_id,
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).filter(
        Review.product_id.in_(product_ids),
        Review.status == 'published'
    ).group_by(Review.product_id).all()
    
    # Create lookup dict
    rating_map = {
        r.product_id: {
            'rating': float(r.avg_rating or 0.0),
            'review_count': int(r.review_count or 0)
        }
        for r in ratings
    }
    
    # Add ratings to products
    result = []
    for p in products:
        if isinstance(p, dict):
            product_id = p.get('id')
            p['rating'] = rating_map.get(product_id, {}).get('rating', 0.0)
            p['review_count'] = rating_map.get(product_id, {}).get('review_count', 0)
            result.append(p)
        else:
            # ORM object
            product_id = p.id
            p.rating = rating_map.get(product_id, {}).get('rating', 0.0)
            p.review_count = rating_map.get(product_id, {}).get('review_count', 0)
            result.append(p)
    
    return result
