-- =============================================
-- COMPLETE RLS SECURITY SETUP
-- E-COMMERCE PLATFORM (Shopee/Lazada Style)
-- =============================================
-- This script ensures ALL tables have proper RLS policies
-- Run this in Supabase SQL Editor

-- =============================================
-- STEP 1: ENABLE RLS ON ALL TABLES
-- =============================================

DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
    LOOP
        EXECUTE 'ALTER TABLE ' || quote_ident(r.tablename) || ' ENABLE ROW LEVEL SECURITY';
    END LOOP;
END $$;

-- =============================================
-- STEP 2: DROP ALL EXISTING POLICIES (CLEAN SLATE)
-- =============================================

DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (
        SELECT schemaname, tablename, policyname 
        FROM pg_policies 
        WHERE schemaname = 'public'
    ) 
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(r.policyname) || 
                ' ON ' || quote_ident(r.tablename);
    END LOOP;
END $$;

-- =============================================
-- STEP 3: CREATE COMPREHENSIVE POLICIES
-- =============================================

-- ---------------------------------------------
-- USER TABLE POLICIES
-- ---------------------------------------------

-- Allow public registration (anyone can insert)
CREATE POLICY "Allow public registration" ON "user"
  FOR INSERT WITH CHECK (true);

-- Users can view their own profile
CREATE POLICY "Users can view own profile" ON "user"
  FOR SELECT USING (
    id = current_setting('app.user_id', true)::bigint
  );

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON "user"
  FOR UPDATE USING (
    id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- ADDRESS TABLE POLICIES
-- ---------------------------------------------

CREATE POLICY "Users can view own addresses" ON "address"
  FOR SELECT USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can insert own addresses" ON "address"
  FOR INSERT WITH CHECK (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can update own addresses" ON "address"
  FOR UPDATE USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can delete own addresses" ON "address"
  FOR DELETE USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- CART TABLE POLICIES (Like Shopee/Lazada)
-- ---------------------------------------------

CREATE POLICY "Users can view own cart" ON "cart"
  FOR SELECT USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can add to cart" ON "cart"
  FOR INSERT WITH CHECK (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can update own cart" ON "cart"
  FOR UPDATE USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can delete from cart" ON "cart"
  FOR DELETE USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- ORDER TABLE POLICIES (Multi-role access)
-- ---------------------------------------------

-- Buyers can view their own orders
CREATE POLICY "Buyers can view own orders" ON "order"
  FOR SELECT USING (
    buyer_id = current_setting('app.user_id', true)::bigint
  );

-- Sellers can view orders containing their products
CREATE POLICY "Sellers can view orders with their products" ON "order"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM order_item oi
      JOIN product p ON oi.product_id = p.id
      WHERE oi.order_id = "order".id
      AND p.seller_id = current_setting('app.user_id', true)::bigint
    )
  );

-- Riders can view assigned orders
CREATE POLICY "Riders can view assigned orders" ON "order"
  FOR SELECT USING (
    rider_id = current_setting('app.user_id', true)::bigint
    OR picked_up_by = current_setting('app.user_id', true)::bigint
    OR delivered_by = current_setting('app.user_id', true)::bigint
  );

-- Buyers can create orders
CREATE POLICY "Buyers can create orders" ON "order"
  FOR INSERT WITH CHECK (
    buyer_id = current_setting('app.user_id', true)::bigint
  );

-- Buyers can update their own orders (cancel, confirm delivery)
CREATE POLICY "Buyers can update own orders" ON "order"
  FOR UPDATE USING (
    buyer_id = current_setting('app.user_id', true)::bigint
  );

-- Sellers can update orders with their products (process, ship)
CREATE POLICY "Sellers can update orders with their products" ON "order"
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM order_item oi
      JOIN product p ON oi.product_id = p.id
      WHERE oi.order_id = "order".id
      AND p.seller_id = current_setting('app.user_id', true)::bigint
    )
  );

-- Riders can update assigned orders (pickup, deliver)
CREATE POLICY "Riders can update assigned orders" ON "order"
  FOR UPDATE USING (
    rider_id = current_setting('app.user_id', true)::bigint
    OR picked_up_by = current_setting('app.user_id', true)::bigint
    OR delivered_by = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- ORDER ITEM TABLE POLICIES
-- ---------------------------------------------

-- Buyers can view items in their orders
CREATE POLICY "Buyers can view own order items" ON "order_item"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_item.order_id
      AND "order".buyer_id = current_setting('app.user_id', true)::bigint
    )
  );

-- Sellers can view items for their products
CREATE POLICY "Sellers can view order items for their products" ON "order_item"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM product
      WHERE product.id = order_item.product_id
      AND product.seller_id = current_setting('app.user_id', true)::bigint
    )
  );

-- Riders can view items in assigned orders
CREATE POLICY "Riders can view items in assigned orders" ON "order_item"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_item.order_id
      AND (
        "order".rider_id = current_setting('app.user_id', true)::bigint
        OR "order".picked_up_by = current_setting('app.user_id', true)::bigint
      )
    )
  );

-- Allow order item creation during checkout
CREATE POLICY "Allow order item creation" ON "order_item"
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_item.order_id
      AND "order".buyer_id = current_setting('app.user_id', true)::bigint
    )
  );

-- ---------------------------------------------
-- PRODUCT TABLE POLICIES (Public + Seller)
-- ---------------------------------------------

-- Anyone can view active/approved products (public marketplace)
CREATE POLICY "Anyone can view active products" ON "product"
  FOR SELECT USING (
    status IN ('active', 'approved')
  );

-- Sellers can view all their own products (including pending)
CREATE POLICY "Sellers can view own products" ON "product"
  FOR SELECT USING (
    seller_id = current_setting('app.user_id', true)::bigint
  );

-- Sellers can create products
CREATE POLICY "Sellers can create products" ON "product"
  FOR INSERT WITH CHECK (
    seller_id = current_setting('app.user_id', true)::bigint
  );

-- Sellers can update their own products
CREATE POLICY "Sellers can update own products" ON "product"
  FOR UPDATE USING (
    seller_id = current_setting('app.user_id', true)::bigint
  );

-- Sellers can delete their own products
CREATE POLICY "Sellers can delete own products" ON "product"
  FOR DELETE USING (
    seller_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- CATEGORY & SUBCATEGORY POLICIES (Public)
-- ---------------------------------------------

CREATE POLICY "Anyone can view categories" ON "category"
  FOR SELECT USING (true);

CREATE POLICY "Anyone can view subcategories" ON "subcategory"
  FOR SELECT USING (true);

-- ---------------------------------------------
-- NOTIFICATION TABLE POLICIES
-- ---------------------------------------------

CREATE POLICY "Users can view own notifications" ON "notification"
  FOR SELECT USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can update own notifications" ON "notification"
  FOR UPDATE USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- Allow system to create notifications
CREATE POLICY "Allow notification creation" ON "notification"
  FOR INSERT WITH CHECK (true);

-- ---------------------------------------------
-- WALLET TRANSACTION POLICIES
-- ---------------------------------------------

CREATE POLICY "Users can view own wallet transactions" ON "wallet_transaction"
  FOR SELECT USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- Allow system to create wallet transactions
CREATE POLICY "Allow wallet transaction creation" ON "wallet_transaction"
  FOR INSERT WITH CHECK (true);

-- ---------------------------------------------
-- REVIEW TABLE POLICIES (Like Shopee/Lazada)
-- ---------------------------------------------

-- Anyone can view published reviews
CREATE POLICY "Anyone can view published reviews" ON "review"
  FOR SELECT USING (
    status = 'published'
  );

-- Users can view their own reviews (including pending)
CREATE POLICY "Users can view own reviews" ON "review"
  FOR SELECT USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- Users can create reviews
CREATE POLICY "Users can create reviews" ON "review"
  FOR INSERT WITH CHECK (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- Users can update their own reviews
CREATE POLICY "Users can update own reviews" ON "review"
  FOR UPDATE USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- Users can delete their own reviews
CREATE POLICY "Users can delete own reviews" ON "review"
  FOR DELETE USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- WISHLIST TABLE POLICIES
-- ---------------------------------------------

CREATE POLICY "Users can view own wishlist" ON "wishlist"
  FOR SELECT USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can add to wishlist" ON "wishlist"
  FOR INSERT WITH CHECK (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can remove from wishlist" ON "wishlist"
  FOR DELETE USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- SELLER APPLICATION POLICIES
-- ---------------------------------------------

CREATE POLICY "Users can view own seller application" ON "seller_application"
  FOR SELECT USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can create seller application" ON "seller_application"
  FOR INSERT WITH CHECK (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can update own pending application" ON "seller_application"
  FOR UPDATE USING (
    user_id = current_setting('app.user_id', true)::bigint
    AND status = 'pending'
  );

-- ---------------------------------------------
-- RIDER APPLICATION POLICIES
-- ---------------------------------------------

CREATE POLICY "Users can view own rider application" ON "rider_application"
  FOR SELECT USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can create rider application" ON "rider_application"
  FOR INSERT WITH CHECK (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- RETURN REQUEST POLICIES (Like Shopee/Lazada)
-- ---------------------------------------------

-- Buyers can view their own return requests
CREATE POLICY "Buyers can view own return requests" ON "return_request"
  FOR SELECT USING (
    buyer_id = current_setting('app.user_id', true)::bigint
  );

-- Sellers can view return requests for their products
CREATE POLICY "Sellers can view return requests for their products" ON "return_request"
  FOR SELECT USING (
    seller_id = current_setting('app.user_id', true)::bigint
  );

-- Buyers can create return requests
CREATE POLICY "Buyers can create return requests" ON "return_request"
  FOR INSERT WITH CHECK (
    buyer_id = current_setting('app.user_id', true)::bigint
  );

-- Buyers can update their own return requests
CREATE POLICY "Buyers can update own return requests" ON "return_request"
  FOR UPDATE USING (
    buyer_id = current_setting('app.user_id', true)::bigint
  );

-- Sellers can update return requests for their products
CREATE POLICY "Sellers can update return requests for their products" ON "return_request"
  FOR UPDATE USING (
    seller_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- RETURN PICKUP POLICIES
-- ---------------------------------------------

-- Buyers can view their own return pickups
CREATE POLICY "Buyers can view own return pickups" ON "return_pickup"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM return_request
      WHERE return_request.id = return_pickup.return_request_id
      AND return_request.buyer_id = current_setting('app.user_id', true)::bigint
    )
  );

-- Riders can view available and assigned return pickups
CREATE POLICY "Riders can view return pickups" ON "return_pickup"
  FOR SELECT USING (
    rider_id = current_setting('app.user_id', true)::bigint
    OR rider_id IS NULL
  );

-- Riders can update assigned return pickups
CREATE POLICY "Riders can update assigned return pickups" ON "return_pickup"
  FOR UPDATE USING (
    rider_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- CHAT MESSAGE POLICIES (Buyer-Seller)
-- ---------------------------------------------

CREATE POLICY "Users can view own store chats" ON "store_chat_message"
  FOR SELECT USING (
    buyer_id = current_setting('app.user_id', true)::bigint
    OR seller_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can send store chat messages" ON "store_chat_message"
  FOR INSERT WITH CHECK (
    buyer_id = current_setting('app.user_id', true)::bigint
    OR seller_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can update own store chats" ON "store_chat_message"
  FOR UPDATE USING (
    buyer_id = current_setting('app.user_id', true)::bigint
    OR seller_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- RIDER CHAT MESSAGE POLICIES (Buyer-Rider)
-- ---------------------------------------------

CREATE POLICY "Users can view own rider chats" ON "rider_chat_message"
  FOR SELECT USING (
    buyer_id = current_setting('app.user_id', true)::bigint
    OR rider_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can send rider chat messages" ON "rider_chat_message"
  FOR INSERT WITH CHECK (
    buyer_id = current_setting('app.user_id', true)::bigint
    OR rider_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can update own rider chats" ON "rider_chat_message"
  FOR UPDATE USING (
    buyer_id = current_setting('app.user_id', true)::bigint
    OR rider_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- FOLLOW POLICIES (Follow sellers)
-- ---------------------------------------------

CREATE POLICY "Users can view follows" ON "follow"
  FOR SELECT USING (
    follower_id = current_setting('app.user_id', true)::bigint
    OR seller_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can follow sellers" ON "follow"
  FOR INSERT WITH CHECK (
    follower_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Users can unfollow sellers" ON "follow"
  FOR DELETE USING (
    follower_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- COUPON POLICIES (Public read)
-- ---------------------------------------------

CREATE POLICY "Anyone can view active coupons" ON "coupon"
  FOR SELECT USING (
    is_active = true
  );

-- ---------------------------------------------
-- HERO SLIDE POLICIES (Public read)
-- ---------------------------------------------

CREATE POLICY "Anyone can view active hero slides" ON "hero_slide"
  FOR SELECT USING (
    is_active = true
  );

-- ---------------------------------------------
-- THEME SETTING POLICIES (Public read)
-- ---------------------------------------------

CREATE POLICY "Anyone can view theme settings" ON "theme_setting"
  FOR SELECT USING (true);

-- ---------------------------------------------
-- REGION/PROVINCE/CITY/BARANGAY (Public read)
-- ---------------------------------------------

CREATE POLICY "Anyone can view regions" ON "region"
  FOR SELECT USING (true);

CREATE POLICY "Anyone can view provinces" ON "province"
  FOR SELECT USING (true);

CREATE POLICY "Anyone can view cities" ON "city"
  FOR SELECT USING (true);

CREATE POLICY "Anyone can view barangays" ON "barangay"
  FOR SELECT USING (true);

CREATE POLICY "Anyone can view city_municipality" ON "city_municipality"
  FOR SELECT USING (true);

-- ---------------------------------------------
-- ORDER LABEL POLICIES
-- ---------------------------------------------

CREATE POLICY "Buyers can view own order labels" ON "order_label"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_label.order_id
      AND "order".buyer_id = current_setting('app.user_id', true)::bigint
    )
  );

CREATE POLICY "Sellers can view order labels for their products" ON "order_label"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM order_item oi
      JOIN product p ON oi.product_id = p.id
      WHERE oi.order_id = order_label.order_id
      AND p.seller_id = current_setting('app.user_id', true)::bigint
    )
  );

CREATE POLICY "Riders can view assigned order labels" ON "order_label"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_label.order_id
      AND (
        "order".rider_id = current_setting('app.user_id', true)::bigint
        OR "order".picked_up_by = current_setting('app.user_id', true)::bigint
      )
    )
  );

-- ---------------------------------------------
-- SELLER ORDER SEEN POLICIES
-- ---------------------------------------------

CREATE POLICY "Sellers can view own order seen records" ON "seller_order_seen"
  FOR SELECT USING (
    seller_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Sellers can manage own order seen records" ON "seller_order_seen"
  FOR ALL USING (
    seller_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- RESTOCK REQUEST POLICIES
-- ---------------------------------------------

CREATE POLICY "Sellers can view own restock requests" ON "restock_request"
  FOR SELECT USING (
    seller_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Sellers can create restock requests" ON "restock_request"
  FOR INSERT WITH CHECK (
    seller_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- QR SCAN LOG POLICIES
-- ---------------------------------------------

CREATE POLICY "Users can view own order scan logs" ON "qr_scan_log"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = qr_scan_log.order_id
      AND (
        "order".buyer_id = current_setting('app.user_id', true)::bigint
        OR "order".rider_id = current_setting('app.user_id', true)::bigint
      )
    )
  );

CREATE POLICY "Riders can create scan logs" ON "qr_scan_log"
  FOR INSERT WITH CHECK (
    scanned_by = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- DELIVERY PERSONNEL POLICIES
-- ---------------------------------------------

CREATE POLICY "Riders can view own delivery personnel record" ON "delivery_personnel"
  FOR SELECT USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Riders can update own delivery personnel record" ON "delivery_personnel"
  FOR UPDATE USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- OAUTH POLICIES
-- ---------------------------------------------

CREATE POLICY "Users can view own oauth records" ON "oauth"
  FOR SELECT USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- ADMIN PROFILE POLICIES
-- ---------------------------------------------

CREATE POLICY "Admins can view own profile" ON "admin_profile"
  FOR SELECT USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

CREATE POLICY "Admins can update own profile" ON "admin_profile"
  FOR UPDATE USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- ---------------------------------------------
-- ADMIN SECURITY LOG POLICIES
-- ---------------------------------------------

CREATE POLICY "Admins can view own security logs" ON "admin_security_log"
  FOR SELECT USING (
    user_id = current_setting('app.user_id', true)::bigint
  );

-- =============================================
-- STEP 4: GRANT PERMISSIONS
-- =============================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO anon, authenticated;

-- Grant select on all tables to authenticated users
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;

-- Grant specific insert/update/delete permissions
GRANT INSERT ON "user" TO anon, authenticated;
GRANT UPDATE ON "user" TO authenticated;

GRANT INSERT, UPDATE, DELETE ON address TO authenticated;
GRANT INSERT, UPDATE, DELETE ON cart TO authenticated;
GRANT INSERT, UPDATE ON "order" TO authenticated;
GRANT INSERT ON order_item TO authenticated;
GRANT INSERT, UPDATE, DELETE ON wishlist TO authenticated;
GRANT INSERT, UPDATE, DELETE ON review TO authenticated;
GRANT INSERT ON seller_application TO authenticated;
GRANT INSERT ON rider_application TO authenticated;
GRANT INSERT, UPDATE ON return_request TO authenticated;
GRANT UPDATE ON return_pickup TO authenticated;
GRANT INSERT, UPDATE ON store_chat_message TO authenticated;
GRANT INSERT, UPDATE ON rider_chat_message TO authenticated;
GRANT INSERT, DELETE ON follow TO authenticated;
GRANT UPDATE ON notification TO authenticated;
GRANT INSERT, UPDATE ON seller_order_seen TO authenticated;
GRANT INSERT ON restock_request TO authenticated;
GRANT INSERT ON qr_scan_log TO authenticated;
GRANT UPDATE ON delivery_personnel TO authenticated;

-- Grant insert on product for sellers
GRANT INSERT, UPDATE, DELETE ON product TO authenticated;

-- =============================================
-- STEP 5: VERIFICATION
-- =============================================

-- Check RLS status and policy count for all tables
SELECT 
    t.tablename,
    t.rowsecurity as rls_enabled,
    COUNT(p.policyname) as policy_count,
    CASE 
        WHEN t.rowsecurity = false THEN '❌ RLS DISABLED'
        WHEN COUNT(p.policyname) = 0 THEN '⚠️ NO POLICIES - INACCESSIBLE!'
        WHEN COUNT(p.policyname) < 2 THEN '⚠️ LIMITED POLICIES'
        ELSE '✅ FULLY SECURED'
    END as status
FROM pg_tables t
LEFT JOIN pg_policies p ON t.tablename = p.tablename AND t.schemaname = p.schemaname
WHERE t.schemaname = 'public'
GROUP BY t.tablename, t.rowsecurity
ORDER BY 
    CASE 
        WHEN t.rowsecurity = false THEN 1
        WHEN COUNT(p.policyname) = 0 THEN 2
        WHEN COUNT(p.policyname) < 2 THEN 3
        ELSE 4
    END,
    t.tablename;

-- =============================================
-- COMPLETION MESSAGE
-- =============================================

DO $$ 
BEGIN
    RAISE NOTICE '✅ RLS SETUP COMPLETE!';
    RAISE NOTICE '📊 Check the verification results above';
    RAISE NOTICE '🔐 All tables should show "FULLY SECURED" status';
    RAISE NOTICE '🚀 Your e-commerce platform is now protected like Shopee/Lazada!';
END $$;
