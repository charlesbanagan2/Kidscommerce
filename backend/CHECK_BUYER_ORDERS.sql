-- =============================================
-- CHECK BUYER ORDERS IN DATABASE
-- Verify if juanbuyer@gmail.com has orders
-- Run this in Supabase SQL Editor
-- =============================================

-- Step 1: Find the buyer user
SELECT 
    '👤 BUYER INFO' as section,
    id as user_id,
    email,
    first_name,
    last_name,
    role,
    created_at
FROM "user"
WHERE email = 'juanbuyer@gmail.com';

-- Step 2: Check orders for this buyer
SELECT 
    '📦 ORDERS' as section,
    o.id as order_id,
    o.buyer_id,
    o.status,
    o.total_amount,
    o.created_at,
    o.payment_method,
    (SELECT COUNT(*) FROM order_item WHERE order_id = o.id) as item_count
FROM "order" o
WHERE o.buyer_id = (
    SELECT id FROM "user" WHERE email = 'juanbuyer@gmail.com'
)
ORDER BY o.created_at DESC;

-- Step 3: Check order items
SELECT 
    '🛒 ORDER ITEMS' as section,
    oi.id as item_id,
    oi.order_id,
    oi.product_id,
    p.name as product_name,
    oi.quantity,
    p.price as product_price,
    (oi.quantity * p.price) as subtotal
FROM order_item oi
JOIN product p ON p.id = oi.product_id
WHERE oi.order_id IN (
    SELECT o.id FROM "order" o
    WHERE o.buyer_id = (
        SELECT id FROM "user" WHERE email = 'juanbuyer@gmail.com'
    )
)
ORDER BY oi.order_id DESC, oi.id;

-- Step 4: Summary
DO $$ 
DECLARE
    buyer_id_var INT;
    order_count INT;
    total_spent NUMERIC;
BEGIN
    -- Get buyer ID
    SELECT id INTO buyer_id_var 
    FROM "user" 
    WHERE email = 'juanbuyer@gmail.com';
    
    IF buyer_id_var IS NULL THEN
        RAISE NOTICE '========================================';
        RAISE NOTICE '❌ BUYER NOT FOUND!';
        RAISE NOTICE '========================================';
        RAISE NOTICE 'Email: juanbuyer@gmail.com does not exist';
        RAISE NOTICE 'Please create this buyer account first.';
        RETURN;
    END IF;
    
    -- Count orders
    SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
    INTO order_count, total_spent
    FROM "order"
    WHERE buyer_id = buyer_id_var;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE '📊 BUYER ORDER SUMMARY';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '👤 Buyer: juanbuyer@gmail.com';
    RAISE NOTICE '🆔 User ID: %', buyer_id_var;
    RAISE NOTICE '📦 Total Orders: %', order_count;
    RAISE NOTICE '💰 Total Spent: ₱%', total_spent;
    RAISE NOTICE '';
    
    IF order_count = 0 THEN
        RAISE NOTICE '⚠️ NO ORDERS FOUND!';
        RAISE NOTICE '';
        RAISE NOTICE '🔍 Possible reasons:';
        RAISE NOTICE '   1. Buyer has not placed any orders yet';
        RAISE NOTICE '   2. Orders were deleted';
        RAISE NOTICE '   3. Wrong buyer_id in orders table';
        RAISE NOTICE '';
        RAISE NOTICE '💡 Solution:';
        RAISE NOTICE '   1. Place a test order in the mobile app';
        RAISE NOTICE '   2. Or create test order in database:';
        RAISE NOTICE '';
        RAISE NOTICE '   INSERT INTO "order" (';
        RAISE NOTICE '       buyer_id, status, total_amount,';
        RAISE NOTICE '       shipping_address, payment_method';
        RAISE NOTICE '   ) VALUES (';
        RAISE NOTICE '       %, ''pending'', 100.00,', buyer_id_var;
        RAISE NOTICE '       ''Test Address'', ''cod''';
        RAISE NOTICE '   );';
    ELSE
        RAISE NOTICE '✅ ORDERS EXIST!';
        RAISE NOTICE '';
        RAISE NOTICE '🔍 If mobile app shows 0 orders:';
        RAISE NOTICE '   1. Check backend logs for errors';
        RAISE NOTICE '   2. Verify JWT token has correct user_id';
        RAISE NOTICE '   3. Check RLS policies are not blocking';
        RAISE NOTICE '   4. Restart backend server';
    END IF;
    
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;
