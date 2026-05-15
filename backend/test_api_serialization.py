from app import app, db, Product
import json

app.app_context().push()

print('=== TESTING API SERIALIZATION ===\n')

# Get Product #22 using ORM
product_orm = db.session.get(Product, 22)
if product_orm:
    print('1. ORM Product Object:')
    print(f'   - ID: {product_orm.id}')
    print(f'   - Name: {product_orm.name}')
    print(f'   - Rating: {product_orm.rating}')
    print(f'   - Review Count: {product_orm.review_count}')
    
    # Convert to dict (simulating what get_data returns)
    product_dict = {
        'id': product_orm.id,
        'name': product_orm.name,
        'description': product_orm.description,
        'price': product_orm.price,
        'stock': product_orm.stock,
        'reserved_stock': product_orm.reserved_stock or 0,
        'image_filename': product_orm.image_filename,
        'video_filename': product_orm.video_filename,
        'gallery': product_orm.gallery,
        'category_id': product_orm.category_id,
        'subcategory_id': product_orm.subcategory_id,
        'seller_id': product_orm.seller_id,
        'status': product_orm.status,
        'featured': product_orm.featured,
        'show_in_new_arrival': product_orm.show_in_new_arrival,
        'rating': product_orm.rating,
        'review_count': product_orm.review_count,
        'created_at': product_orm.created_at.isoformat() if hasattr(product_orm, 'created_at') else None,
    }
    
    print('\n2. Product Dict (what get_data should return):')
    print(f'   - rating: {product_dict.get("rating")}')
    print(f'   - review_count: {product_dict.get("review_count")}')
    
    # Test _serialize_product_api_dict
    from app import _serialize_product_api_dict
    serialized = _serialize_product_api_dict(product_dict)
    
    print('\n3. Serialized API Response:')
    print(f'   - rating: {serialized.get("rating")}')
    print(f'   - review_count: {serialized.get("review_count")}')
    print(f'\n4. Full Serialized Product (JSON):')
    print(json.dumps(serialized, indent=2, default=str))
else:
    print('ERROR: Product #22 not found!')

print('\n=== TEST COMPLETE ===')
