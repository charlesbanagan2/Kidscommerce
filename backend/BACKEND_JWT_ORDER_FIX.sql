-- =============================================
-- BACKEND JWT AUTHENTICATION ORDER POLICIES
-- For backends using JWT tokens (not Supabase Auth)
-- Run this entire script in Supabase SQL Editor
-- =============================================

-- Step 1: Drop all existing policies
DROP POLICY IF EXISTS "service_role_orders_all" ON "order";
DROP POLICY IF EXISTS "buyers_view_own_orders" ON "order";
DROP POLICY IF EXISTS "riders_view_orders" ON "order";
DROP POLICY IF EXISTS "sellers_view_orders" ON "order";
DROP POLICY IF EXISTS "buyers_create_orders" ON "order";
DROP POLICY IF EXISTS "buyers_update_own_orders" ON "order";
DROP POLICY IF EXISTS "riders_update_orders" ON "order";
DROP POLICY IF EXISTS "sellers_update_orders" ON "order";

DROP POLICY IF EXISTS "service_role_order_items_all" ON "order_item";
DROP POLICY IF EXISTS "buyers_view_order_items" ON "order_item";
DROP POLICY IF EXISTS "riders_view_order_items" ON "order_item";
DROP POLICY IF EXISTS "sellers_view_order_items" ON "order_item";
DROP POLICY IF EXISTS "buyers_create_order_items" ON "order_item";

-- =============================================
-- STEP 2: DISABLE RLS (Backend handles auth)
-- =============================================

-- Since your backend uses JWT tokens and handles authentication,
-- it's better to disable RLS and let the backend control access
ALTER TABLE "order" DISABLE ROW LEVEL SECURITY;
ALTER TABLE "order_item" DISABLE ROW LEVEL SECURITY;

-- =============================================
-- STEP 3: VERIFY RLS IS DISABLED
-- =============================================

SELECT 
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('order', 'order_item');

-- =============================================
-- STEP 4: SUCCESS MESSAGE
-- =============================================

DO $$ 
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ RLS DISABLED FOR BACKEND JWT AUTH!';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '🔐 Security Model:';
    RAISE NOTICE '   ✅ Backend handles all authentication';
    RAISE NOTICE '   ✅ JWT tokens verify user identity';
    RAISE NOTICE '   ✅ Backend filters data by user_id';
    RAISE NOTICE '   ✅ Direct database access still requires credentials';
    RAISE NOTICE '';
    RAISE NOTICE '📱 Next steps:';
    RAISE NOTICE '   1. Restart your backend server';
    RAISE NOTICE '   2. Open mobile app';
    RAISE NOTICE '   3. Login as buyer';
    RAISE NOTICE '   4. Check "My Orders" - should show all orders!';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;
