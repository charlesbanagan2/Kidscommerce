from app import app, db, Product, Review

app.app_context().push()

print('=== COMPLETE VERIFICATION ===\n')

# 1. Check Product Model
print('1. Product Model Fields:')
print(f'   - Has rating field: {hasattr(Product, "rating")}')
print(f'   - Has review_count field: {hasattr(Product, "review_count")}')

# 2. Check Database Columns
print('\n2. Database Columns:')
import sqlalchemy
inspector = sqlalchemy.inspect(db.engine)
cols = [c['name'] for c in inspector.get_columns('product')]
print(f'   - rating column exists: {"rating" in cols}')
print(f'   - review_count column exists: {"review_count" in cols}')

# 3. Check Product #22 Data
print('\n3. Current Data for Product #22:')
result = db.session.execute(db.text('SELECT id, name, rating, review_count FROM product WHERE id = 22')).fetchone()
if result:
    print(f'   - Product: {result[1]}')
    print(f'   - Rating: {result[2]}')
    print(f'   - Review Count: {result[3]}')
else:
    print('   - Product #22 NOT FOUND!')

# 4. Check Reviews for Product #22
print('\n4. Reviews for Product #22:')
reviews = db.session.execute(db.text('SELECT id, rating, content, order_id FROM review WHERE product_id = 22')).fetchall()
print(f'   - Total reviews: {len(reviews)}')
for r in reviews:
    print(f'     * Review #{r[0]}: {r[1]} stars, Order #{r[3]}')

# 5. Check Order #22 (or Order #37 based on error log)
print('\n5. Check Orders with Reviews:')
orders_with_reviews = db.session.execute(db.text('SELECT DISTINCT order_id FROM review WHERE product_id = 22')).fetchall()
for o in orders_with_reviews:
    print(f'   - Order #{o[0]} has a review for Product #22')

# 6. Check if Product model serialization includes rating
print('\n6. Product Serialization Test:')
product = db.session.get(Product, 22)
if product:
    print(f'   - product.rating = {product.rating}')
    print(f'   - product.review_count = {product.review_count}')
    print(f'   - Product object has rating attr: {hasattr(product, "rating")}')
    print(f'   - Product object has review_count attr: {hasattr(product, "review_count")}')
else:
    print('   - Product #22 NOT FOUND in ORM!')

print('\n=== VERIFICATION COMPLETE ===')
