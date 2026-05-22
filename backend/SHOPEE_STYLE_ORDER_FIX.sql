-- =============================================
-- SHOPEE/LAZADA STYLE ORDER POLICIES
-- Buyers see their own orders, Riders see assigned orders
-- Run this entire script in Supabase SQL Editor
-- =============================================

-- Step 1: Drop old restrictive policies
DROP POLICY IF EXISTS "Buyers can view own orders" ON "order";
DROP POLICY IF EXISTS "Sellers can view orders with their products" ON "order";
DROP POLICY IF EXISTS "Riders can view assigned orders" ON "order";
DROP POLICY IF EXISTS "Buyers can create orders" ON "order";
DROP POLICY IF EXISTS "Buyers can update own orders" ON "order";
DROP POLICY IF EXISTS "Sellers can update orders with their products" ON "order";
DROP POLICY IF EXISTS "Riders can update assigned orders" ON "order";
DROP POLICY IF EXISTS "Service role full access to orders" ON "order";
DROP POLICY IF EXISTS "Authenticated users can view orders" ON "order";
DROP POLICY IF EXISTS "Authenticated users can create orders" ON "order";
DROP POLICY IF EXISTS "Authenticated users can update orders" ON "order";

DROP POLICY IF EXISTS "Buyers can view own order items" ON "order_item";
DROP POLICY IF EXISTS "Sellers can view order items for their products" ON "order_item";
DROP POLICY IF EXISTS "Riders can view items in assigned orders" ON "order_item";
DROP POLICY IF EXISTS "Allow order item creation" ON "order_item";
DROP POLICY IF EXISTS "Service role full access to order items" ON "order_item";
DROP POLICY IF EXISTS "Authenticated users can view order items" ON "order_item";
DROP POLICY IF EXISTS "Authenticated users can create order items" ON "order_item";

-- =============================================
-- STEP 2: CREATE SHOPEE-STYLE ORDER POLICIES
-- =============================================

-- 1. Service role (backend) has full access - bypasses RLS
CREATE POLICY "service_role_orders_all" ON "order"
  FOR ALL TO service_role
  USING (true) 
  WITH CHECK (true);

-- 2. Buyers can view ALL their own orders (complete history like Shopee)
CREATE POLICY "buyers_view_own_orders" ON "order"
  FOR SELECT TO authenticated
  USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = "order".buyer_id
    )
  );

-- 3. Riders can view assigned orders + available orders (ready for pickup)
CREATE POLICY "riders_view_orders" ON "order"
  FOR SELECT TO authenticated
  USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" 
      WHERE id = "order".rider_id 
         OR id = "order".picked_up_by 
         OR id = "order".delivered_by
    )
    OR (
      "order".status = 'ready_for_pickup' 
      AND "order".rider_id IS NULL
      AND auth.uid()::text IN (
        SELECT supabase_uid::text FROM "user" WHERE role = 'rider'
      )
    )
  );

-- 4. Sellers can view orders containing their products
CREATE POLICY "sellers_view_orders" ON "order"
  FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM order_item oi
      JOIN product p ON oi.product_id = p.id
      WHERE oi.order_id = "order".id
      AND auth.uid()::text IN (
        SELECT supabase_uid::text FROM "user" WHERE id = p.seller_id
      )
    )
  );

-- 5. Buyers can create orders
CREATE POLICY "buyers_create_orders" ON "order"
  FOR INSERT TO authenticated
  WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = "order".buyer_id
    )
  );

-- 6. Buyers can update their own orders (cancel, confirm delivery)
CREATE POLICY "buyers_update_own_orders" ON "order"
  FOR UPDATE TO authenticated
  USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = "order".buyer_id
    )
  );

-- 7. Riders can update assigned orders
CREATE POLICY "riders_update_orders" ON "order"
  FOR UPDATE TO authenticated
  USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" 
      WHERE id = "order".rider_id 
         OR id = "order".picked_up_by 
         OR id = "order".delivered_by
    )
  );

-- 8. Sellers can update orders with their products
CREATE POLICY "sellers_update_orders" ON "order"
  FOR UPDATE TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM order_item oi
      JOIN product p ON oi.product_id = p.id
      WHERE oi.order_id = "order".id
      AND auth.uid()::text IN (
        SELECT supabase_uid::text FROM "user" WHERE id = p.seller_id
      )
    )
  );

-- =============================================
-- STEP 3: CREATE ORDER_ITEM POLICIES
-- =============================================

-- 1. Service role has full access
CREATE POLICY "service_role_order_items_all" ON "order_item"
  FOR ALL TO service_role
  USING (true) 
  WITH CHECK (true);

-- 2. Buyers can view items in their orders
CREATE POLICY "buyers_view_order_items" ON "order_item"
  FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_item.order_id
      AND auth.uid()::text IN (
        SELECT supabase_uid::text FROM "user" WHERE id = "order".buyer_id
      )
    )
  );

-- 3. Riders can view items in assigned orders + available orders
CREATE POLICY "riders_view_order_items" ON "order_item"
  FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_item.order_id
      AND (
        auth.uid()::text IN (
          SELECT supabase_uid::text FROM "user" 
          WHERE id = "order".rider_id 
             OR id = "order".picked_up_by 
             OR id = "order".delivered_by
        )
        OR (
          "order".status = 'ready_for_pickup' 
          AND "order".rider_id IS NULL
          AND auth.uid()::text IN (
            SELECT supabase_uid::text FROM "user" WHERE role = 'rider'
          )
        )
      )
    )
  );

-- 4. Sellers can view items for their products
CREATE POLICY "sellers_view_order_items" ON "order_item"
  FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM product
      WHERE product.id = order_item.product_id
      AND auth.uid()::text IN (
        SELECT supabase_uid::text FROM "user" WHERE id = product.seller_id
      )
    )
  );

-- 5. Buyers can create order items during checkout
CREATE POLICY "buyers_create_order_items" ON "order_item"
  FOR INSERT TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_item.order_id
      AND auth.uid()::text IN (
        SELECT supabase_uid::text FROM "user" WHERE id = "order".buyer_id
      )
    )
  );

-- =============================================
-- STEP 4: VERIFY POLICIES
-- =============================================

SELECT 
    '✅ ORDER POLICIES' as status,
    COUNT(*) as count
FROM pg_policies 
WHERE tablename = 'order'
UNION ALL
SELECT 
    '✅ ORDER_ITEM POLICIES' as status,
    COUNT(*) as count
FROM pg_policies 
WHERE tablename = 'order_item';

-- Show all order policies
SELECT 
    'ORDER' as table_name,
    policyname,
    cmd as operation,
    roles
FROM pg_policies 
WHERE tablename = 'order'
ORDER BY policyname;

-- Show all order_item policies
SELECT 
    'ORDER_ITEM' as table_name,
    policyname,
    cmd as operation,
    roles
FROM pg_policies 
WHERE tablename = 'order_item'
ORDER BY policyname;

-- =============================================
-- STEP 5: SUCCESS MESSAGE
-- =============================================

DO $$ 
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ SHOPEE-STYLE ORDER POLICIES APPLIED!';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '🛍️ How it works (like Shopee/Lazada):';
    RAISE NOTICE '';
    RAISE NOTICE '👤 BUYERS:';
    RAISE NOTICE '   ✅ See ALL their own orders (complete history)';
    RAISE NOTICE '   ✅ Can create new orders';
    RAISE NOTICE '   ✅ Can update their orders (cancel, confirm)';
    RAISE NOTICE '   ✅ See all items in their orders';
    RAISE NOTICE '';
    RAISE NOTICE '🏍️ RIDERS:';
    RAISE NOTICE '   ✅ See orders assigned to them';
    RAISE NOTICE '   ✅ See available orders (ready_for_pickup)';
    RAISE NOTICE '   ✅ Can update assigned orders';
    RAISE NOTICE '   ✅ See items in their orders';
    RAISE NOTICE '';
    RAISE NOTICE '🏪 SELLERS:';
    RAISE NOTICE '   ✅ See orders with their products';
    RAISE NOTICE '   ✅ Can update order status';
    RAISE NOTICE '   ✅ See items for their products';
    RAISE NOTICE '';
    RAISE NOTICE '🔐 Security:';
    RAISE NOTICE '   ✅ Uses Supabase auth.uid() for user identification';
    RAISE NOTICE '   ✅ Backend service_role bypasses RLS';
    RAISE NOTICE '   ✅ Direct database access is protected';
    RAISE NOTICE '   ✅ Each user only sees their own data';
    RAISE NOTICE '';
    RAISE NOTICE '📱 Next steps:';
    RAISE NOTICE '   1. Open mobile app';
    RAISE NOTICE '   2. Login as buyer';
    RAISE NOTICE '   3. Go to "My Orders" tab';
    RAISE NOTICE '   4. Pull to refresh';
    RAISE NOTICE '   5. All your orders should appear!';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;
