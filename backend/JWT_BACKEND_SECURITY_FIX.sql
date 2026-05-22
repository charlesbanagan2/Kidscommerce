-- =============================================
-- SHOPEE-STYLE SECURITY WITH JWT BACKEND
-- Secure orders - users only see their own data
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
-- STEP 2: ENABLE RLS
-- =============================================

ALTER TABLE "order" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "order_item" ENABLE ROW LEVEL SECURITY;

-- =============================================
-- STEP 3: CREATE SERVICE ROLE POLICY (Backend Full Access)
-- =============================================

-- Your backend uses service_role key, so it bypasses RLS automatically
-- This policy ensures backend has full access
CREATE POLICY "backend_full_access_orders" ON "order"
  FOR ALL 
  TO service_role
  USING (true) 
  WITH CHECK (true);

CREATE POLICY "backend_full_access_order_items" ON "order_item"
  FOR ALL 
  TO service_role
  USING (true) 
  WITH CHECK (true);

-- =============================================
-- STEP 4: BLOCK DIRECT DATABASE ACCESS
-- =============================================

-- Block all direct access from authenticated users
-- Force them to go through your backend API
CREATE POLICY "block_direct_access_orders" ON "order"
  FOR ALL 
  TO authenticated, anon
  USING (false) 
  WITH CHECK (false);

CREATE POLICY "block_direct_access_order_items" ON "order_item"
  FOR ALL 
  TO authenticated, anon
  USING (false) 
  WITH CHECK (false);

-- =============================================
-- STEP 5: VERIFY SETUP
-- =============================================

SELECT 
    '✅ ORDER TABLE' as status,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' AND tablename = 'order'
UNION ALL
SELECT 
    '✅ ORDER_ITEM TABLE' as status,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' AND tablename = 'order_item';

-- Show all policies
SELECT 
    tablename,
    policyname,
    cmd as operation,
    roles
FROM pg_policies 
WHERE tablename IN ('order', 'order_item')
ORDER BY tablename, policyname;

-- =============================================
-- STEP 6: SUCCESS MESSAGE
-- =============================================

DO $$ 
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ SHOPEE-STYLE SECURITY ENABLED!';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '🔐 Security Model:';
    RAISE NOTICE '   ✅ Backend (service_role) has full access';
    RAISE NOTICE '   ✅ Direct database access is BLOCKED';
    RAISE NOTICE '   ✅ Users must go through backend API';
    RAISE NOTICE '   ✅ Backend validates JWT and filters by user_id';
    RAISE NOTICE '';
    RAISE NOTICE '🛍️ How it works:';
    RAISE NOTICE '';
    RAISE NOTICE '👤 Juan Buyer:';
    RAISE NOTICE '   1. Logs in → gets JWT token';
    RAISE NOTICE '   2. Calls /api/v1/buyer/orders';
    RAISE NOTICE '   3. Backend validates JWT';
    RAISE NOTICE '   4. Backend filters: WHERE buyer_id = juan_id';
    RAISE NOTICE '   5. Juan only sees HIS orders!';
    RAISE NOTICE '';
    RAISE NOTICE '🏍️ Juan Rider:';
    RAISE NOTICE '   1. Logs in → gets JWT token';
    RAISE NOTICE '   2. Calls /api/orders/rider';
    RAISE NOTICE '   3. Backend validates JWT';
    RAISE NOTICE '   4. Backend filters: WHERE rider_id = juan_id';
    RAISE NOTICE '   5. Juan only sees HIS assigned orders!';
    RAISE NOTICE '';
    RAISE NOTICE '🏪 Juan Seller:';
    RAISE NOTICE '   1. Logs in → gets JWT token';
    RAISE NOTICE '   2. Calls /api/seller/orders';
    RAISE NOTICE '   3. Backend validates JWT';
    RAISE NOTICE '   4. Backend filters by seller products';
    RAISE NOTICE '   5. Juan only sees orders with HIS products!';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️ IMPORTANT: Your backend MUST filter data!';
    RAISE NOTICE '   Example Python/Flask code:';
    RAISE NOTICE '   ';
    RAISE NOTICE '   @app.route("/api/v1/buyer/orders")';
    RAISE NOTICE '   @jwt_required()';
    RAISE NOTICE '   def get_buyer_orders():';
    RAISE NOTICE '       user_id = get_jwt_identity()';
    RAISE NOTICE '       orders = Order.query.filter_by(';
    RAISE NOTICE '           buyer_id=user_id';
    RAISE NOTICE '       ).all()';
    RAISE NOTICE '       return jsonify(orders)';
    RAISE NOTICE '';
    RAISE NOTICE '📱 Next steps:';
    RAISE NOTICE '   1. Verify backend filters by user_id';
    RAISE NOTICE '   2. Restart backend server';
    RAISE NOTICE '   3. Test in mobile app';
    RAISE NOTICE '   4. Juan Buyer should see only HIS orders!';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;
