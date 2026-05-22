-- =============================================
-- DIAGNOSTIC: Check juanbuyer@gmail.com Orders
-- =============================================

-- Step 1: Find the user
SELECT 
    id,
    first_name,
    last_name,
    email,
    role,
    status
FROM "user"
WHERE email = 'juanbuyer@gmail.com';

-- Step 2: Check all orders for this user (replace USER_ID with actual ID from step 1)
-- If user id is 25, use that
SELECT 
    o.id as order_id,
    o.buyer_id,
    o.rider_id,
    o.status,
    o.total_amount,
    o.created_at,
    o.updated_at
FROM "order" o
WHERE o.buyer_id = (SELECT id FROM "user" WHERE email = 'juanbuyer@gmail.com')
ORDER BY o.created_at DESC;

-- Step 3: Check Order #49 specifically
SELECT 
    o.id as order_id,
    o.buyer_id,
    o.rider_id,
    o.status,
    o.total_amount,
    o.created_at,
    u.email as buyer_email,
    u.first_name as buyer_name
FROM "order" o
LEFT JOIN "user" u ON o.buyer_id = u.id
WHERE o.id = 49;

-- Step 4: Check order items for Order #49
SELECT 
    oi.id,
    oi.order_id,
    oi.product_id,
    oi.quantity,
    oi.price_at_time,
    p.name as product_name
FROM order_item oi
LEFT JOIN product p ON oi.product_id = p.id
WHERE oi.order_id = 49;

-- Step 5: Check RLS policies on order table
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE tablename = 'order';

-- Step 6: Check if RLS is enabled
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables
WHERE tablename IN ('order', 'order_item')
AND schemaname = 'public';

-- Step 7: Count total orders in database
SELECT 
    COUNT(*) as total_orders
FROM "order";

-- Step 8: Count orders by status
SELECT 
    status,
    COUNT(*) as count
FROM "order"
GROUP BY status
ORDER BY count DESC;

-- Step 9: Check if there are any orders at all for juanbuyer
SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN '❌ NO ORDERS FOUND for juanbuyer@gmail.com'
        ELSE '✅ Found ' || COUNT(*) || ' orders for juanbuyer@gmail.com'
    END as result
FROM "order" o
WHERE o.buyer_id = (SELECT id FROM "user" WHERE email = 'juanbuyer@gmail.com');

-- Step 10: Check if Order #49 exists and who owns it
SELECT 
    CASE 
        WHEN o.id IS NULL THEN '❌ Order #49 does NOT exist in database'
        WHEN u.email = 'juanbuyer@gmail.com' THEN '✅ Order #49 belongs to juanbuyer@gmail.com'
        ELSE '⚠️ Order #49 belongs to ' || u.email || ' (NOT juanbuyer@gmail.com)'
    END as result
FROM "order" o
LEFT JOIN "user" u ON o.buyer_id = u.id
WHERE o.id = 49;
