-- Fix all table sequences in the database
-- Run this in Supabase SQL Editor to fix all sequence issues at once

-- Fix address sequence
SELECT setval('address_id_seq', (SELECT COALESCE(MAX(id), 1) FROM address), true);

-- Fix user sequence (if needed)
SELECT setval('user_id_seq', (SELECT COALESCE(MAX(id), 1) FROM "user"), true);

-- Fix product sequence (if needed)
SELECT setval('product_id_seq', (SELECT COALESCE(MAX(id), 1) FROM product), true);

-- Fix order sequence (if needed)
SELECT setval('order_id_seq', (SELECT COALESCE(MAX(id), 1) FROM "order"), true);

-- Fix order_item sequence (if needed)
SELECT setval('order_item_id_seq', (SELECT COALESCE(MAX(id), 1) FROM order_item), true);

-- Fix cart sequence (if needed)
SELECT setval('cart_id_seq', (SELECT COALESCE(MAX(id), 1) FROM cart), true);

-- Fix review sequence (if needed)
SELECT setval('review_id_seq', (SELECT COALESCE(MAX(id), 1) FROM review), true);

-- Fix notification sequence (if needed)
SELECT setval('notification_id_seq', (SELECT COALESCE(MAX(id), 1) FROM notification), true);

-- Fix category sequence (if needed)
SELECT setval('category_id_seq', (SELECT COALESCE(MAX(id), 1) FROM category), true);

-- Fix subcategory sequence (if needed)
SELECT setval('subcategory_id_seq', (SELECT COALESCE(MAX(id), 1) FROM subcategory), true);

-- Verify all sequences
SELECT 
    'address' as table_name,
    (SELECT MAX(id) FROM address) as max_id,
    currval('address_id_seq') as sequence_value
UNION ALL
SELECT 
    'user' as table_name,
    (SELECT MAX(id) FROM "user") as max_id,
    currval('user_id_seq') as sequence_value
UNION ALL
SELECT 
    'product' as table_name,
    (SELECT MAX(id) FROM product) as max_id,
    currval('product_id_seq') as sequence_value
UNION ALL
SELECT 
    'order' as table_name,
    (SELECT MAX(id) FROM "order") as max_id,
    currval('order_id_seq') as sequence_value
UNION ALL
SELECT 
    'cart' as table_name,
    (SELECT MAX(id) FROM cart) as max_id,
    currval('cart_id_seq') as sequence_value;

-- All sequence_value should be >= max_id
