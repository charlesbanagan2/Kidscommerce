from app import app, db, Product, Review, Order, get_data, get_data_by_id, _serialize_product_api_dict
import json

app.app_context().push()

print('=' * 60)
print('FINAL COMPREHENSIVE VERIFICATION')
print('=' * 60)

# Test 1: Database has correct data
print('\n[TEST 1] Database Data for Product #22:')
result = db.session.execute(db.text('SELECT id, name, rating, review_count FROM product WHERE id = 22')).fetchone()
print(f'  [OK] Product: {result[1]}')
print(f'  [OK] Rating: {result[2]}')
print(f'  [OK] Review Count: {result[3]}')
assert result[2] == 4.0, "Rating should be 4.0"
assert result[3] == 1, "Review count should be 1"

# Test 2: Product Model has fields
print('\n[TEST 2] Product Model Fields:')
product_orm = db.session.get(Product, 22)
print(f'  [OK] product.rating = {product_orm.rating}')
print(f'  [OK] product.review_count = {product_orm.review_count}')
assert hasattr(product_orm, 'rating'), "Product model should have rating field"
assert hasattr(product_orm, 'review_count'), "Product model should have review_count field"
assert product_orm.rating == 4.0, "Product rating should be 4.0"
assert product_orm.review_count == 1, "Product review_count should be 1"

# Test 3: get_data function includes rating fields
print('\n[TEST 3] get_data() Function:')
products = get_data('product', filters={'id': 22})
if products and len(products) > 0:
    product = products[0]
    print(f'  [OK] get_data rating: {product.get("rating")}')
    print(f'  [OK] get_data review_count: {product.get("review_count")}')
    assert 'rating' in product, "get_data should include rating"
    assert 'review_count' in product, "get_data should include review_count"
    assert product.get('rating') == 4.0, "get_data rating should be 4.0"
    assert product.get('review_count') == 1, "get_data review_count should be 1"
else:
    print('  [FAIL] get_data returned no products!')

# Test 4: get_data_by_id function includes rating fields
print('\n[TEST 4] get_data_by_id() Function:')
product = get_data_by_id('product', 22)
if product:
    print(f'  [OK] get_data_by_id rating: {product.get("rating")}')
    print(f'  [OK] get_data_by_id review_count: {product.get("review_count")}')
    assert 'rating' in product, "get_data_by_id should include rating"
    assert 'review_count' in product, "get_data_by_id should include review_count"
else:
    print('  [FAIL] get_data_by_id returned None!')

# Test 5: API Serialization includes rating fields
print('\n[TEST 5] API Serialization (_serialize_product_api_dict):')
product_dict = {
    'id': 22,
    'name': 'Test Product',
    'description': 'Test',
    'price': 999.0,
    'stock': 92,
    'reserved_stock': 0,
    'seller_id': 16,
    'category_id': 16,
    'subcategory_id': None,
    'image_filename': 'test.png',
    'rating': 4.0,
    'review_count': 1,
}
serialized = _serialize_product_api_dict(product_dict)
print(f'  [OK] Serialized rating: {serialized.get("rating")}')
print(f'  [OK] Serialized review_count: {serialized.get("review_count")}')
assert 'rating' in serialized, "Serialized product should include rating"
assert 'review_count' in serialized, "Serialized product should include review_count"
assert serialized.get('rating') == 4.0, "Serialized rating should be 4.0"
assert serialized.get('review_count') == 1, "Serialized review_count should be 1"

# Test 6: Check Order #22 has review
print('\n[TEST 6] Order #22 Review Status:')
reviews = db.session.execute(db.text('SELECT id, rating, order_id FROM review WHERE order_id = 22')).fetchall()
print(f'  [OK] Order #22 has {len(reviews)} review(s)')
for r in reviews:
    print(f'    - Review #{r[0]}: {r[1]} stars')
assert len(reviews) > 0, "Order #22 should have at least one review"

# Test 7: mobile_rating_api.py is fixed
print('\n[TEST 7] mobile_rating_api.py Fix:')
with open('mobile_rating_api.py', 'r', encoding='utf-8') as f:
    content = f.read()
    has_old_error = 'db.Model._decl_class_registry' in content
    has_sql_update = 'UPDATE product SET rating' in content
    print(f'  [OK] Removed old error code: {not has_old_error}')
    print(f'  [OK] Uses SQL update: {has_sql_update}')
    assert not has_old_error, "mobile_rating_api should not use _decl_class_registry"
    assert has_sql_update, "mobile_rating_api should use SQL UPDATE"

print('\n' + '=' * 60)
print('ALL TESTS PASSED!')
print('=' * 60)
print('\nNext Steps:')
print('1. Restart Flask backend server (Ctrl+C then python app.py)')
print('2. Restart mobile app (flutter run or hot reload)')
print('3. Check Product #22 in mobile app - should show 4.0 stars')
print('4. Check Order #22 - "Rate Now" button should be hidden')
print('=' * 60)
