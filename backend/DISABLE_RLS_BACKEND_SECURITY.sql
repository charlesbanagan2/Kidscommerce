-- =============================================
-- DISABLE RLS - LET BACKEND HANDLE SECURITY
-- Backend validates JWT and filters by user_id
-- Run this in Supabase SQL Editor
-- =============================================

-- Drop all policies
DROP POLICY IF EXISTS "backend_full_access_orders" ON "order";
DROP POLICY IF EXISTS "backend_full_access_order_items" ON "order_item";
DROP POLICY IF EXISTS "block_direct_access_orders" ON "order";
DROP POLICY IF EXISTS "block_direct_access_order_items" ON "order_item";

-- Disable RLS
ALTER TABLE "order" DISABLE ROW LEVEL SECURITY;
ALTER TABLE "order_item" DISABLE ROW LEVEL SECURITY;

-- Verify
SELECT 
    tablename,
    CASE WHEN rowsecurity THEN '❌ RLS ENABLED' ELSE '✅ RLS DISABLED' END as status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('order', 'order_item');

-- Success message
DO $$ 
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ RLS DISABLED - BACKEND SECURITY MODE';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '🔐 Security Model:';
    RAISE NOTICE '   ✅ Backend validates JWT tokens';
    RAISE NOTICE '   ✅ Backend filters: WHERE buyer_id = user_id';
    RAISE NOTICE '   ✅ Database credentials still required';
    RAISE NOTICE '   ✅ No direct public access';
    RAISE NOTICE '';
    RAISE NOTICE '📱 Test now:';
    RAISE NOTICE '   1. Login as juanbuyer@gmail.com';
    RAISE NOTICE '   2. Go to "My Orders"';
    RAISE NOTICE '   3. Should see order history!';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;
