-- ============================================
-- SQL QUERIES TO CHECK RATINGS AND REVIEWS
-- First, let's find the correct table names
-- ============================================

-- 0. FIND ALL TABLES IN DATABASE
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- After running above, use the correct table names below
-- Common variations: orders/order, reviews/review, products/product

-- ============================================
-- QUICK CHECKS (try these variations)
-- ============================================

-- Check tables that might contain orders
SELECT * FROM "order" WHERE id = 22 LIMIT 1;
-- OR
SELECT * FROM "Order" WHERE id = 22 LIMIT 1;
-- OR
SELECT * FROM orders WHERE id = 22 LIMIT 1;

-- Check tables that might contain reviews
SELECT * FROM review ORDER BY created_at DESC LIMIT 5;
-- OR
SELECT * FROM "Review" ORDER BY created_at DESC LIMIT 5;
-- OR
SELECT * FROM reviews ORDER BY created_at DESC LIMIT 5;

-- Check tables that might contain products
SELECT id, name, rating, review_count FROM product LIMIT 5;
-- OR
SELECT id, name, rating, review_count FROM "Product" LIMIT 5;
-- OR
SELECT id, name, rating, review_count FROM products LIMIT 5;

-- ============================================
-- ONCE YOU KNOW THE TABLE NAMES, USE THESE:
-- ============================================

-- 1. CHECK ALL REVIEWS (replace 'review' with correct table name)
SELECT 
    r.id,
    r.product_id,
    r.user_id,
    r.rating,
    r.title,
    r.content,
    r.created_at
FROM review r
ORDER BY r.created_at DESC
LIMIT 20;

-- 2. CHECK ORDER 22 (replace 'order' with correct table name)
SELECT 
    o.id,
    o.buyer_id,
    o.rating,
    o.review,
    o.status,
    o.created_at
FROM "order" o
WHERE o.id = 22;

-- 3. CHECK IF USER 25 HAS REVIEWS
SELECT * FROM review WHERE user_id = 25;

-- 4. CHECK PRODUCT RATINGS
SELECT 
    p.id,
    p.name,
    p.rating,
    p.review_count
FROM product p
WHERE p.review_count > 0
ORDER BY p.id;

-- 5. COUNT REVIEWS
SELECT COUNT(*) as total_reviews FROM review;

-- 6. CHECK REVIEW MEDIA
SELECT * FROM review_media ORDER BY created_at DESC LIMIT 10;
-- OR
SELECT * FROM "ReviewMedia" ORDER BY created_at DESC LIMIT 10;

-- 7. FIND PRODUCTS FROM ORDER 22
SELECT 
    oi.order_id,
    oi.product_id,
    p.name as product_name,
    p.rating,
    p.review_count
FROM order_item oi
JOIN product p ON oi.product_id = p.id
WHERE oi.order_id = 22;

-- 8. CHECK IF PRODUCTS FROM ORDER 22 HAVE REVIEWS
SELECT 
    oi.product_id,
    p.name,
    r.id as review_id,
    r.rating,
    r.content,
    r.created_at
FROM order_item oi
JOIN product p ON oi.product_id = p.id
LEFT JOIN review r ON r.product_id = oi.product_id AND r.user_id = (SELECT buyer_id FROM "order" WHERE id = 22)
WHERE oi.order_id = 22;
