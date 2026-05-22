-- =============================================
-- CLEAN UP CONFLICTING RLS POLICIES
-- Remove all policies and set up clean security
-- Run this in Supabase SQL Editor
-- =============================================

-- =============================================
-- STEP 1: DROP ALL EXISTING POLICIES
-- =============================================

-- Drop order table policies
DROP POLICY IF EXISTS "authenticated_can_access" ON "order";
DROP POLICY IF EXISTS "block_direct_orders" ON "order";
DROP POLICY IF EXISTS "service_role_all_orders" ON "order";
DROP POLICY IF EXISTS "service_role_full_access" ON "order";
DROP POLICY IF EXISTS "backend_full_access_orders" ON "order";
DROP POLICY IF EXISTS "service_role_orders_all" ON "order";
DROP POLICY IF EXISTS "buyers_view_own_orders" ON "order";
DROP POLICY IF EXISTS "riders_view_orders" ON "order";
DROP POLICY IF EXISTS "sellers_view_orders" ON "order";
DROP POLICY IF EXISTS "buyers_create_orders" ON "order";
DROP POLICY IF EXISTS "buyers_update_own_orders" ON "order";
DROP POLICY IF EXISTS "riders_update_orders" ON "order";
DROP POLICY IF EXISTS "sellers_update_orders" ON "order";

-- Drop order_item table policies
DROP POLICY IF EXISTS "authenticated_can_access" ON "order_item";
DROP POLICY IF EXISTS "block_direct_order_items" ON "order_item";
DROP POLICY IF EXISTS "service_role_all_order_items" ON "order_item";
DROP POLICY IF EXISTS "service_role_full_access" ON "order_item";
DROP POLICY IF EXISTS "backend_full_access_order_items" ON "order_item";
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
-- STEP 3: CREATE CLEAN POLICIES
-- =============================================

-- Service role has full access (backend with service_role key)
CREATE POLICY "service_role_access" ON "order"
  FOR ALL 
  TO service_role
  USING (true) 
  WITH CHECK (true);

CREATE POLICY "service_role_access" ON "order_item"
  FOR ALL 
  TO service_role
  USING (true) 
  WITH CHECK (true);

-- Block all other access (authenticated and anonymous users)
CREATE POLICY "block_direct_access" ON "order"
  FOR ALL 
  TO authenticated, anon
  USING (false) 
  WITH CHECK (false);

CREATE POLICY "block_direct_access" ON "order_item"
  FOR ALL 
  TO authenticated, anon
  USING (false) 
  WITH CHECK (false);

-- =============================================
-- STEP 4: VERIFY CLEAN SETUP
-- =============================================

-- Check RLS status
SELECT 
    '🔒 ' || tablename as table_name,
    CASE 
        WHEN rowsecurity THEN '✅ RLS ENABLED' 
        ELSE '❌ RLS DISABLED' 
    END as status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('order', 'order_item')
ORDER BY tablename;

-- Check policies (should only have 2 per table)
SELECT 
    '📋 ' || tablename as table_name,
    policyname as policy_name,
    cmd as operation,
    ARRAY_TO_STRING(roles, ', ') as allowed_roles
FROM pg_policies 
WHERE tablename IN ('order', 'order_item')
ORDER BY tablename, policyname;

-- =============================================
-- STEP 5: SUCCESS MESSAGE
-- =============================================

DO $$ 
DECLARE
    order_policy_count INT;
    order_item_policy_count INT;
BEGIN
    -- Count policies
    SELECT COUNT(*) INTO order_policy_count 
    FROM pg_policies WHERE tablename = 'order';
    
    SELECT COUNT(*) INTO order_item_policy_count 
    FROM pg_policies WHERE tablename = 'order_item';
    
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ RLS POLICIES CLEANED UP!';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Policy Count:';
    RAISE NOTICE '   order table: % policies', order_policy_count;
    RAISE NOTICE '   order_item table: % policies', order_item_policy_count;
    RAISE NOTICE '   Expected: 2 policies per table';
    RAISE NOTICE '';
    
    IF order_policy_count = 2 AND order_item_policy_count = 2 THEN
        RAISE NOTICE '✅ PERFECT! Clean setup complete.';
    ELSE
        RAISE NOTICE '⚠️ WARNING: Unexpected policy count!';
    END IF;
    
    RAISE NOTICE '';
    RAISE NOTICE '🔐 Security Model:';
    RAISE NOTICE '   ✅ service_role: Full access (backend)';
    RAISE NOTICE '   ❌ authenticated: Blocked';
    RAISE NOTICE '   ❌ anon: Blocked';
    RAISE NOTICE '';
    RAISE NOTICE '🛡️ How it works:';
    RAISE NOTICE '   1. Backend uses service_role key';
    RAISE NOTICE '   2. Backend bypasses RLS automatically';
    RAISE NOTICE '   3. Backend validates JWT tokens';
    RAISE NOTICE '   4. Backend filters: WHERE buyer_id = user_id';
    RAISE NOTICE '   5. Users see only THEIR data';
    RAISE NOTICE '';
    RAISE NOTICE '📱 Next Steps:';
    RAISE NOTICE '   1. ✅ Policies cleaned up';
    RAISE NOTICE '   2. ✅ service_role key in .env';
    RAISE NOTICE '   3. 🔄 RESTART backend server NOW';
    RAISE NOTICE '   4. 📱 Test mobile app';
    RAISE NOTICE '   5. 🎉 Orders should appear!';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️ If orders still empty:';
    RAISE NOTICE '   - Check backend logs for errors';
    RAISE NOTICE '   - Verify JWT token is valid';
    RAISE NOTICE '   - Check buyer_id in database';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;
