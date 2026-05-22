-- ============================================
-- SQL QUERIES TO CHECK RATINGS AND REVIEWS
-- ============================================

-- 1. CHECK ALL REVIEWS IN DATABASE
SELECT 
    r.id as review_id,
    r.product_id,
    p.name as product_name,
    r.user_id,
    u.email as user_email,
    r.rating,
    r.title,
    r.content,
    r.created_at,
    r.updated_at
FROM reviews r
LEFT JOIN products p ON r.product_id = p.id
LEFT JOIN users u ON r.user_id = u.id
ORDER BY r.created_at DESC;

-- 2. CHECK PRODUCT RATINGS (aggregated)
SELECT 
    p.id as product_id,
    p.name as product_name,
    p.rating as current_rating,
    p.review_count as current_review_count,
    COUNT(r.id) as actual_review_count,
    AVG(r.rating) as calculated_avg_rating,
    MIN(r.rating) as min_rating,
    MAX(r.rating) as max_rating
FROM products p
LEFT JOIN reviews r ON p.id = r.product_id
GROUP BY p.id, p.name, p.rating, p.review_count
HAVING COUNT(r.id) > 0
ORDER BY p.id;

-- 3. CHECK ORDER RATINGS
SELECT 
    o.id as order_id,
    o.buyer_id,
    u.email as buyer_email,
    o.rating as order_rating,
    o.review as order_review,
    o.status,
    o.created_at as order_date,
    o.updated_at
FROM orders o
LEFT JOIN users u ON o.buyer_id = u.id
WHERE o.rating IS NOT NULL
ORDER BY o.updated_at DESC;

-- 4. CHECK SPECIFIC ORDER (replace 22 with your order ID)
SELECT 
    o.id as order_id,
    o.buyer_id,
    o.rating as order_rating,
    o.review as order_review,
    o.status,
    oi.product_id,
    p.name as product_name,
    p.rating as product_rating,
    p.review_count
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.id
WHERE o.id = 22;

-- 5. CHECK IF REVIEWS EXIST FOR ORDER 22's PRODUCTS
SELECT 
    oi.order_id,
    oi.product_id,
    p.name as product_name,
    r.id as review_id,
    r.rating,
    r.content,
    r.created_at as review_date
FROM order_items oi
LEFT JOIN products p ON oi.product_id = p.id
LEFT JOIN reviews r ON r.product_id = oi.product_id AND r.user_id = (SELECT buyer_id FROM orders WHERE id = 22)
WHERE oi.order_id = 22;

-- 6. CHECK REVIEW MEDIA (images/videos)
SELECT 
    rm.id as media_id,
    rm.review_id,
    r.product_id,
    p.name as product_name,
    rm.media_type,
    rm.media_path,
    rm.created_at
FROM review_media rm
LEFT JOIN reviews r ON rm.review_id = r.id
LEFT JOIN products p ON r.product_id = p.id
ORDER BY rm.created_at DESC;

-- 7. FIND PRODUCTS WITH MISMATCHED RATINGS
-- (where calculated rating doesn't match stored rating)
SELECT 
    p.id,
    p.name,
    p.rating as stored_rating,
    p.review_count as stored_count,
    COUNT(r.id) as actual_count,
    ROUND(AVG(r.rating), 2) as calculated_rating,
    CASE 
        WHEN p.rating != ROUND(AVG(r.rating), 2) THEN 'MISMATCH'
        WHEN p.review_count != COUNT(r.id) THEN 'COUNT MISMATCH'
        ELSE 'OK'
    END as status
FROM products p
LEFT JOIN reviews r ON p.id = r.product_id
GROUP BY p.id, p.name, p.rating, p.review_count
HAVING COUNT(r.id) > 0;

-- 8. CHECK LATEST 10 REVIEWS WITH ALL DETAILS
SELECT 
    r.id,
    r.product_id,
    p.name as product_name,
    r.user_id,
    u.email as reviewer_email,
    CONCAT(u.first_name, ' ', u.last_name) as reviewer_name,
    r.rating,
    r.title,
    r.content,
    r.created_at,
    (SELECT COUNT(*) FROM review_media WHERE review_id = r.id) as media_count
FROM reviews r
LEFT JOIN products p ON r.product_id = p.id
LEFT JOIN users u ON r.user_id = u.id
ORDER BY r.created_at DESC
LIMIT 10;

-- 9. CHECK IF USER 25 (from your logs) HAS SUBMITTED REVIEWS
SELECT 
    r.id as review_id,
    r.product_id,
    p.name as product_name,
    r.rating,
    r.title,
    r.content,
    r.created_at,
    o.id as related_order_id
FROM reviews r
LEFT JOIN products p ON r.product_id = p.id
LEFT JOIN order_items oi ON oi.product_id = r.product_id
LEFT JOIN orders o ON o.id = oi.order_id AND o.buyer_id = r.user_id
WHERE r.user_id = 25
ORDER BY r.created_at DESC;

-- 10. QUICK CHECK - COUNT EVERYTHING
SELECT 
    'Total Reviews' as metric,
    COUNT(*) as count
FROM reviews
UNION ALL
SELECT 
    'Reviews with Media',
    COUNT(DISTINCT review_id)
FROM review_media
UNION ALL
SELECT 
    'Products with Reviews',
    COUNT(DISTINCT product_id)
FROM reviews
UNION ALL
SELECT 
    'Orders with Ratings',
    COUNT(*)
FROM orders
WHERE rating IS NOT NULL;
