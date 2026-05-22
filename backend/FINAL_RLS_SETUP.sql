-- =============================================
-- FINAL RLS SETUP WITH SERVICE_ROLE KEY
-- Shopee-style security with proper backend access
-- Run this in Supabase SQL Editor
-- =============================================

-- Step 1: Drop all existing policies
DROP POLICY IF EXISTS "backend_full_access_orders" ON "order";
DROP POLICY IF EXISTS "backend_full_access_order_items" ON "order_item";
DROP POLICY IF EXISTS "block_direct_access_orders" ON "order";
DROP POLICY IF EXISTS "block_direct_access_order_items" ON "order_item";
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
-- STEP 2: ENABLE RLS
-- =============================================

ALTER TABLE "order" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "order_item" ENABLE ROW LEVEL SECURITY;

-- =============================================
-- STEP 3: SERVICE_ROLE FULL ACCESS
-- =============================================

-- Backend with service_role key bypasses RLS automatically
-- But we create explicit policies for clarity
CREATE POLICY "service_role_all_orders" ON "order"
  FOR ALL 
  TO service_role
  USING (true) 
  WITH CHECK (true);

CREATE POLICY "service_role_all_order_items" ON "order_item"
  FOR ALL 
  TO service_role
  USING (true) 
  WITH CHECK (true);

-- =============================================
-- STEP 4: BLOCK DIRECT ACCESS
-- =============================================

-- Block authenticated and anonymous users
-- Force them to use backend API
CREATE POLICY "block_direct_orders" ON "order"
  FOR ALL 
  TO authenticated, anon
  USING (false) 
  WITH CHECK (false);

CREATE POLICY "block_direct_order_items" ON "order_item"
  FOR ALL 
  TO authenticated, anon
  USING (false) 
  WITH CHECK (false);

-- =============================================
-- STEP 5: VERIFY SETUP
-- =============================================

SELECT 
    '✅ ORDER TABLE' as table_name,
    CASE WHEN rowsecurity THEN '🔒 RLS ENABLED' ELSE '⚠️ RLS DISABLED' END as status
FROM pg_tables 
WHERE schemaname = 'public' AND tablename = 'order'
UNION ALL
SELECT 
    '✅ ORDER_ITEM TABLE' as table_name,
    CASE WHEN rowsecurity THEN '🔒 RLS ENABLED' ELSE '⚠️ RLS DISABLED' END as status
FROM pg_tables 
WHERE schemaname = 'public' AND tablename = 'order_item';

-- Show policies
SELECT 
    '📋 ' || tablename as table_name,
    policyname as policy,
    cmd as operation,
    ARRAY_TO_STRING(roles, ', ') as roles
FROM pg_policies 
WHERE tablename IN ('order', 'order_item')
ORDER BY tablename, policyname;

-- =============================================
-- STEP 6: SUCCESS MESSAGE
-- =============================================

DO $$ 
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ SHOPEE-STYLE RLS SECURITY ENABLED!';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '🔐 Security Configuration:';
    RAISE NOTICE '   ✅ RLS is ENABLED on order tables';
    RAISE NOTICE '   ✅ Backend uses service_role key';
    RAISE NOTICE '   ✅ service_role bypasses RLS';
    RAISE NOTICE '   ✅ Direct database access BLOCKED';
    RAISE NOTICE '';
    RAISE NOTICE '🛡️ How it works:';
    RAISE NOTICE '';
    RAISE NOTICE '   Backend (service_role):';
    RAISE NOTICE '   ✅ Full access to all data';
    RAISE NOTICE '   ✅ Validates JWT tokens';
    RAISE NOTICE '   ✅ Filters: WHERE buyer_id = user_id';
    RAISE NOTICE '';
    RAISE NOTICE '   Direct Access (authenticated/anon):';
    RAISE NOTICE '   ❌ BLOCKED by RLS policies';
    RAISE NOTICE '   ❌ Cannot read orders';
    RAISE NOTICE '   ❌ Cannot write orders';
    RAISE NOTICE '';
    RAISE NOTICE '👤 User Experience:';
    RAISE NOTICE '   1. Juan Buyer logs in';
    RAISE NOTICE '   2. Gets JWT token';
    RAISE NOTICE '   3. Calls /api/v1/buyer/orders';
    RAISE NOTICE '   4. Backend validates JWT';
    RAISE NOTICE '   5. Backend filters by buyer_id';
    RAISE NOTICE '   6. Juan sees ONLY his orders!';
    RAISE NOTICE '';
    RAISE NOTICE '📱 Next Steps:';
    RAISE NOTICE '   1. ✅ service_role key updated in .env';
    RAISE NOTICE '   2. 🔄 RESTART backend server';
    RAISE NOTICE '   3. 📱 Test mobile app';
    RAISE NOTICE '   4. 🎉 Orders should appear!';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️ IMPORTANT:';
    RAISE NOTICE '   - Keep service_role key SECRET';
    RAISE NOTICE '   - Never expose in mobile app';
    RAISE NOTICE '   - Only use in backend server';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;
