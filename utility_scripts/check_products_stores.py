import sqlite3

conn = sqlite3.connect('kids_ecommerce.db')
cursor = conn.cursor()

# Get products with seller info
print('=== PRODUCTS WITH SELLER INFO ===')
cursor.execute('''
SELECT p.id, p.name, p.seller_id, u.first_name, u.last_name, 
       COUNT(DISTINCT r.id) as review_count
FROM product p
LEFT JOIN user u ON p.seller_id = u.id
LEFT JOIN review r ON p.id = r.product_id
WHERE p.status = 'active'
GROUP BY p.id
ORDER BY p.id
''')

all_products = cursor.fetchall()
for row in all_products:
    print(f'ID: {row[0]}, Name: {row[1]}, Seller: {row[3]} {row[4]}, Reviews: {row[5]}')

# Check for SpongeBob product specifically
print('\n=== SPONGEBOB PRODUCT DETAILS ===')
cursor.execute('''
SELECT p.id, p.name, p.price, p.stock, u.first_name, u.last_name, p.gallery, p.image_filename
FROM product p
LEFT JOIN user u ON p.seller_id = u.id
WHERE p.name LIKE '%SpongeBob%' OR p.name LIKE '%Sticky Catcher%'
''')

spongebob = cursor.fetchall()
for row in spongebob:
    product_id = row[0]
    print(f'Product: {row[1]}')
    print(f'  ID: {product_id}, Price: {row[2]}, Stock: {row[3]}')
    print(f'  Seller: {row[4]} {row[5]}')
    print(f'  Main Image: {row[7]}')
    print(f'  Gallery: {row[6]}')
    
    # Get reviews for this product
    cursor.execute('SELECT id, rating, title, content, user_id FROM review WHERE product_id = ? AND status = ?', (product_id, 'published'))
    reviews = cursor.fetchall()
    print(f'  Reviews ({len(reviews)}):')
    for review in reviews:
        print(f'    - Rating: {review[1]}, Title: {review[2]}')
        print(f'      Content: {review[3][:80] if review[3] else "No content"}...')

# Check seller applications to get store names
print('\n=== SELLER STORE INFORMATION ===')
cursor.execute('''
SELECT sa.user_id, u.first_name, u.last_name, sa.store_name, sa.status
FROM seller_application sa
LEFT JOIN user u ON sa.user_id = u.id
WHERE sa.status = 'approved'
''')

sellers = cursor.fetchall()
for seller in sellers:
    print(f'Seller ID: {seller[0]}, Name: {seller[1]} {seller[2]}, Store: {seller[3]}')

conn.close()
