-- =============================================
-- FIX ORDER RLS POLICIES
-- Ensures orders show up for buyers and riders
-- =============================================

-- Drop existing order policies
DROP POLICY IF EXISTS "Buyers can view own orders" ON "order";
DROP POLICY IF EXISTS "Sellers can view orders with their products" ON "order";
DROP POLICY IF EXISTS "Riders can view assigned orders" ON "order";
DROP POLICY IF EXISTS "Buyers can create orders" ON "order";
DROP POLICY IF EXISTS "Buyers can update own orders" ON "order";
DROP POLICY IF EXISTS "Sellers can update orders with their products" ON "order";
DROP POLICY IF EXISTS "Riders can update assigned orders" ON "order";

-- Drop existing order_item policies
DROP POLICY IF EXISTS "Buyers can view own order items" ON "order_item";
DROP POLICY IF EXISTS "Sellers can view order items for their products" ON "order_item";
DROP POLICY IF EXISTS "Riders can view items in assigned orders" ON "order_item";
DROP POLICY IF EXISTS "Allow order item creation" ON "order_item";

-- =============================================
-- CREATE NEW ORDER POLICIES
-- =============================================

-- 1. Buyers can view their own orders
CREATE POLICY "Buyers can view own orders" ON "order"
  FOR SELECT USING (
    buyer_id::text = current_setting('app.user_id', true)
    OR buyer_id = CAST(current_setting('app.user_id', true) AS bigint)
  );

-- 2. Sellers can view orders containing their products
CREATE POLICY "Sellers can view orders with their products" ON "order"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM order_item oi
      JOIN product p ON oi.product_id = p.id
      WHERE oi.order_id = "order".id
      AND (
        p.seller_id::text = current_setting('app.user_id', true)
        OR p.seller_id = CAST(current_setting('app.user_id', true) AS bigint)
      )
    )
  );

-- 3. Riders can view assigned orders OR orders ready for pickup
CREATE POLICY "Riders can view assigned orders" ON "order"
  FOR SELECT USING (
    rider_id::text = current_setting('app.user_id', true)
    OR rider_id = CAST(current_setting('app.user_id', true) AS bigint)
    OR picked_up_by::text = current_setting('app.user_id', true)
    OR picked_up_by = CAST(current_setting('app.user_id', true) AS bigint)
    OR delivered_by::text = current_setting('app.user_id', true)
    OR delivered_by = CAST(current_setting('app.user_id', true) AS bigint)
    OR (status = 'ready_for_pickup' AND rider_id IS NULL)
  );

-- 4. Buyers can create orders
CREATE POLICY "Buyers can create orders" ON "order"
  FOR INSERT WITH CHECK (
    buyer_id::text = current_setting('app.user_id', true)
    OR buyer_id = CAST(current_setting('app.user_id', true) AS bigint)
  );

-- 5. Buyers can update their own orders
CREATE POLICY "Buyers can update own orders" ON "order"
  FOR UPDATE USING (
    buyer_id::text = current_setting('app.user_id', true)
    OR buyer_id = CAST(current_setting('app.user_id', true) AS bigint)
  );

-- 6. Sellers can update orders with their products
CREATE POLICY "Sellers can update orders with their products" ON "order"
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM order_item oi
      JOIN product p ON oi.product_id = p.id
      WHERE oi.order_id = "order".id
      AND (
        p.seller_id::text = current_setting('app.user_id', true)
        OR p.seller_id = CAST(current_setting('app.user_id', true) AS bigint)
      )
    )
  );

-- 7. Riders can update assigned orders
CREATE POLICY "Riders can update assigned orders" ON "order"
  FOR UPDATE USING (
    rider_id::text = current_setting('app.user_id', true)
    OR rider_id = CAST(current_setting('app.user_id', true) AS bigint)
    OR picked_up_by::text = current_setting('app.user_id', true)
    OR picked_up_by = CAST(current_setting('app.user_id', true) AS bigint)
    OR delivered_by::text = current_setting('app.user_id', true)
    OR delivered_by = CAST(current_setting('app.user_id', true) AS bigint)
  );

-- =============================================
-- CREATE NEW ORDER_ITEM POLICIES
-- =============================================

-- 1. Buyers can view items in their orders
CREATE POLICY "Buyers can view own order items" ON "order_item"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_item.order_id
      AND (
        "order".buyer_id::text = current_setting('app.user_id', true)
        OR "order".buyer_id = CAST(current_setting('app.user_id', true) AS bigint)
      )
    )
  );

-- 2. Sellers can view items for their products
CREATE POLICY "Sellers can view order items for their products" ON "order_item"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM product
      WHERE product.id = order_item.product_id
      AND (
        product.seller_id::text = current_setting('app.user_id', true)
        OR product.seller_id = CAST(current_setting('app.user_id', true) AS bigint)
      )
    )
  );

-- 3. Riders can view items in assigned orders OR ready for pickup
CREATE POLICY "Riders can view items in assigned orders" ON "order_item"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_item.order_id
      AND (
        "order".rider_id::text = current_setting('app.user_id', true)
        OR "order".rider_id = CAST(current_setting('app.user_id', true) AS bigint)
        OR "order".picked_up_by::text = current_setting('app.user_id', true)
        OR "order".picked_up_by = CAST(current_setting('app.user_id', true) AS bigint)
        OR ("order".status = 'ready_for_pickup' AND "order".rider_id IS NULL)
      )
    )
  );

-- 4. Allow order item creation during checkout
CREATE POLICY "Allow order item creation" ON "order_item"
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_item.order_id
      AND (
        "order".buyer_id::text = current_setting('app.user_id', true)
        OR "order".buyer_id = CAST(current_setting('app.user_id', true) AS bigint)
      )
    )
  );

-- =============================================
-- VERIFICATION QUERY
-- =============================================

-- Check order policies
SELECT 
    'order' as table_name,
    policyname,
    cmd as operation,
    qual as using_expression
FROM pg_policies 
WHERE tablename = 'order'
ORDER BY policyname;

-- Check order_item policies
SELECT 
    'order_item' as table_name,
    policyname,
    cmd as operation,
    qual as using_expression
FROM pg_policies 
WHERE tablename = 'order_item'
ORDER BY policyname;

-- =============================================
-- TEST QUERIES (Run these to verify)
-- =============================================

-- Test 1: Check if RLS is enabled
SELECT 
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('order', 'order_item');

-- Test 2: Count policies
SELECT 
    tablename,
    COUNT(*) as policy_count
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('order', 'order_item')
GROUP BY tablename;

-- =============================================
-- COMPLETION MESSAGE
-- =============================================

DO $$ 
BEGIN
    RAISE NOTICE '✅ ORDER RLS POLICIES FIXED!';
    RAISE NOTICE '📊 Orders should now be visible to:';
    RAISE NOTICE '   - Buyers: their own orders';
    RAISE NOTICE '   - Riders: assigned orders + ready_for_pickup orders';
    RAISE NOTICE '   - Sellers: orders with their products';
    RAISE NOTICE '🔐 Policies handle both string and bigint user IDs';
END $$;
