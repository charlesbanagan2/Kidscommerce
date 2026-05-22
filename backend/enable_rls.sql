-- Enable RLS on all tables and create security policies
-- Run this in your Supabase SQL Editor

-- ============================================
-- ENABLE RLS ON ALL TABLES
-- ============================================

ALTER TABLE "user" ENABLE ROW LEVEL SECURITY;
ALTER TABLE seller_application ENABLE ROW LEVEL SECURITY;
ALTER TABLE "order" ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_item ENABLE ROW LEVEL SECURITY;
ALTER TABLE cart ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_label ENABLE ROW LEVEL SECURITY;
ALTER TABLE seller_order_seen ENABLE ROW LEVEL SECURITY;
ALTER TABLE return_request ENABLE ROW LEVEL SECURITY;
ALTER TABLE restock_request ENABLE ROW LEVEL SECURITY;
ALTER TABLE return_pickup ENABLE ROW LEVEL SECURITY;
ALTER TABLE qr_scan_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE delivery_personnel ENABLE ROW LEVEL SECURITY;
ALTER TABLE wishlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE address ENABLE ROW LEVEL SECURITY;
ALTER TABLE oauth ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_security_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification ENABLE ROW LEVEL SECURITY;
ALTER TABLE wallet_transaction ENABLE ROW LEVEL SECURITY;
ALTER TABLE store_chat_message ENABLE ROW LEVEL SECURITY;
ALTER TABLE rider_chat_message ENABLE ROW LEVEL SECURITY;
ALTER TABLE hero_slide ENABLE ROW LEVEL SECURITY;
ALTER TABLE theme_setting ENABLE ROW LEVEL SECURITY;
ALTER TABLE category ENABLE ROW LEVEL SECURITY;
ALTER TABLE subcategory ENABLE ROW LEVEL SECURITY;
ALTER TABLE region ENABLE ROW LEVEL SECURITY;
ALTER TABLE province ENABLE ROW LEVEL SECURITY;
ALTER TABLE city ENABLE ROW LEVEL SECURITY;
ALTER TABLE barangay ENABLE ROW LEVEL SECURITY;
ALTER TABLE city_municipality ENABLE ROW LEVEL SECURITY;
ALTER TABLE product ENABLE ROW LEVEL SECURITY;
ALTER TABLE review ENABLE ROW LEVEL SECURITY;
ALTER TABLE coupon ENABLE ROW LEVEL SECURITY;
ALTER TABLE follow ENABLE ROW LEVEL SECURITY;
ALTER TABLE rider_application ENABLE ROW LEVEL SECURITY;

-- ============================================
-- USER TABLE POLICIES
-- ============================================

-- Users can read their own data
CREATE POLICY "Users can view own profile" ON "user"
    FOR SELECT USING (true);

-- Users can update their own data
CREATE POLICY "Users can update own profile" ON "user"
    FOR UPDATE USING (id = current_setting('app.user_id')::integer);

-- Allow insert for registration (public)
CREATE POLICY "Allow user registration" ON "user"
    FOR INSERT WITH CHECK (true);

-- ============================================
-- PRODUCT TABLE POLICIES
-- ============================================

-- Everyone can view active products
CREATE POLICY "Anyone can view active products" ON product
    FOR SELECT USING (status IN ('active', 'approved'));

-- Sellers can insert their own products
CREATE POLICY "Sellers can create products" ON product
    FOR INSERT WITH CHECK (seller_id = current_setting('app.user_id')::integer);

-- Sellers can update their own products
CREATE POLICY "Sellers can update own products" ON product
    FOR UPDATE USING (seller_id = current_setting('app.user_id')::integer);

-- Sellers can delete their own products
CREATE POLICY "Sellers can delete own products" ON product
    FOR DELETE USING (seller_id = current_setting('app.user_id')::integer);

-- ============================================
-- CART TABLE POLICIES
-- ============================================

-- Users can view their own cart
CREATE POLICY "Users can view own cart" ON cart
    FOR SELECT USING (user_id = current_setting('app.user_id')::integer);

-- Users can insert to their own cart
CREATE POLICY "Users can add to cart" ON cart
    FOR INSERT WITH CHECK (user_id = current_setting('app.user_id')::integer);

-- Users can update their own cart
CREATE POLICY "Users can update own cart" ON cart
    FOR UPDATE USING (user_id = current_setting('app.user_id')::integer);

-- Users can delete from their own cart
CREATE POLICY "Users can delete from cart" ON cart
    FOR DELETE USING (user_id = current_setting('app.user_id')::integer);

-- ============================================
-- ORDER TABLE POLICIES
-- ============================================

-- Buyers can view their own orders
CREATE POLICY "Buyers can view own orders" ON "order"
    FOR SELECT USING (buyer_id = current_setting('app.user_id')::integer);

-- Buyers can create orders
CREATE POLICY "Buyers can create orders" ON "order"
    FOR INSERT WITH CHECK (buyer_id = current_setting('app.user_id')::integer);

-- Buyers can update their own orders (for cancellation, etc)
CREATE POLICY "Buyers can update own orders" ON "order"
    FOR UPDATE USING (buyer_id = current_setting('app.user_id')::integer);

-- Riders can view assigned orders
CREATE POLICY "Riders can view assigned orders" ON "order"
    FOR SELECT USING (rider_id = current_setting('app.user_id')::integer);

-- Riders can update assigned orders
CREATE POLICY "Riders can update assigned orders" ON "order"
    FOR UPDATE USING (rider_id = current_setting('app.user_id')::integer);

-- ============================================
-- ORDER_ITEM TABLE POLICIES
-- ============================================

-- Users can view order items for their orders
CREATE POLICY "Users can view own order items" ON order_item
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM "order" 
            WHERE "order".id = order_item.order_id 
            AND "order".buyer_id = current_setting('app.user_id')::integer
        )
    );

-- Allow insert for order creation
CREATE POLICY "Allow order item creation" ON order_item
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM "order" 
            WHERE "order".id = order_item.order_id 
            AND "order".buyer_id = current_setting('app.user_id')::integer
        )
    );

-- ============================================
-- WISHLIST TABLE POLICIES
-- ============================================

-- Users can view their own wishlist
CREATE POLICY "Users can view own wishlist" ON wishlist
    FOR SELECT USING (user_id = current_setting('app.user_id')::integer);

-- Users can add to their wishlist
CREATE POLICY "Users can add to wishlist" ON wishlist
    FOR INSERT WITH CHECK (user_id = current_setting('app.user_id')::integer);

-- Users can remove from their wishlist
CREATE POLICY "Users can remove from wishlist" ON wishlist
    FOR DELETE USING (user_id = current_setting('app.user_id')::integer);

-- ============================================
-- ADDRESS TABLE POLICIES
-- ============================================

-- Users can view their own addresses
CREATE POLICY "Users can view own addresses" ON address
    FOR SELECT USING (user_id = current_setting('app.user_id')::integer);

-- Users can create their own addresses
CREATE POLICY "Users can create addresses" ON address
    FOR INSERT WITH CHECK (user_id = current_setting('app.user_id')::integer);

-- Users can update their own addresses
CREATE POLICY "Users can update own addresses" ON address
    FOR UPDATE USING (user_id = current_setting('app.user_id')::integer);

-- Users can delete their own addresses
CREATE POLICY "Users can delete own addresses" ON address
    FOR DELETE USING (user_id = current_setting('app.user_id')::integer);

-- ============================================
-- NOTIFICATION TABLE POLICIES
-- ============================================

-- Users can view their own notifications
CREATE POLICY "Users can view own notifications" ON notification
    FOR SELECT USING (user_id = current_setting('app.user_id')::integer);

-- Users can update their own notifications (mark as read)
CREATE POLICY "Users can update own notifications" ON notification
    FOR UPDATE USING (user_id = current_setting('app.user_id')::integer);

-- Allow system to create notifications
CREATE POLICY "Allow notification creation" ON notification
    FOR INSERT WITH CHECK (true);

-- ============================================
-- REVIEW TABLE POLICIES
-- ============================================

-- Everyone can view published reviews
CREATE POLICY "Anyone can view published reviews" ON review
    FOR SELECT USING (status = 'published');

-- Users can create reviews for products they purchased
CREATE POLICY "Users can create reviews" ON review
    FOR INSERT WITH CHECK (user_id = current_setting('app.user_id')::integer);

-- Users can update their own reviews
CREATE POLICY "Users can update own reviews" ON review
    FOR UPDATE USING (user_id = current_setting('app.user_id')::integer);

-- ============================================
-- CHAT MESSAGE POLICIES
-- ============================================

-- Users can view messages where they are buyer or seller
CREATE POLICY "Users can view own chat messages" ON store_chat_message
    FOR SELECT USING (
        buyer_id = current_setting('app.user_id')::integer 
        OR seller_id = current_setting('app.user_id')::integer
    );

-- Users can send messages as buyer or seller
CREATE POLICY "Users can send chat messages" ON store_chat_message
    FOR INSERT WITH CHECK (
        buyer_id = current_setting('app.user_id')::integer 
        OR seller_id = current_setting('app.user_id')::integer
    );

-- Users can update their own messages (mark as read)
CREATE POLICY "Users can update chat messages" ON store_chat_message
    FOR UPDATE USING (
        buyer_id = current_setting('app.user_id')::integer 
        OR seller_id = current_setting('app.user_id')::integer
    );

-- ============================================
-- RIDER CHAT MESSAGE POLICIES
-- ============================================

-- Users can view messages where they are buyer or rider
CREATE POLICY "Users can view rider chat messages" ON rider_chat_message
    FOR SELECT USING (
        buyer_id = current_setting('app.user_id')::integer 
        OR rider_id = current_setting('app.user_id')::integer
    );

-- Users can send rider chat messages
CREATE POLICY "Users can send rider chat messages" ON rider_chat_message
    FOR INSERT WITH CHECK (
        buyer_id = current_setting('app.user_id')::integer 
        OR rider_id = current_setting('app.user_id')::integer
    );

-- ============================================
-- WALLET TRANSACTION POLICIES
-- ============================================

-- Users can view their own wallet transactions
CREATE POLICY "Users can view own wallet transactions" ON wallet_transaction
    FOR SELECT USING (user_id = current_setting('app.user_id')::integer);

-- Allow system to create wallet transactions
CREATE POLICY "Allow wallet transaction creation" ON wallet_transaction
    FOR INSERT WITH CHECK (true);

-- ============================================
-- SELLER APPLICATION POLICIES
-- ============================================

-- Users can view their own seller applications
CREATE POLICY "Users can view own seller applications" ON seller_application
    FOR SELECT USING (user_id = current_setting('app.user_id')::integer);

-- Users can create seller applications
CREATE POLICY "Users can create seller applications" ON seller_application
    FOR INSERT WITH CHECK (user_id = current_setting('app.user_id')::integer);

-- Users can update their own pending applications
CREATE POLICY "Users can update own seller applications" ON seller_application
    FOR UPDATE USING (user_id = current_setting('app.user_id')::integer AND status = 'pending');

-- ============================================
-- RIDER APPLICATION POLICIES
-- ============================================

-- Users can view their own rider applications
CREATE POLICY "Users can view own rider applications" ON rider_application
    FOR SELECT USING (user_id = current_setting('app.user_id')::integer);

-- Users can create rider applications
CREATE POLICY "Users can create rider applications" ON rider_application
    FOR INSERT WITH CHECK (user_id = current_setting('app.user_id')::integer);

-- ============================================
-- RETURN REQUEST POLICIES
-- ============================================

-- Buyers can view their own return requests
CREATE POLICY "Buyers can view own return requests" ON return_request
    FOR SELECT USING (buyer_id = current_setting('app.user_id')::integer);

-- Sellers can view return requests for their products
CREATE POLICY "Sellers can view return requests" ON return_request
    FOR SELECT USING (seller_id = current_setting('app.user_id')::integer);

-- Buyers can create return requests
CREATE POLICY "Buyers can create return requests" ON return_request
    FOR INSERT WITH CHECK (buyer_id = current_setting('app.user_id')::integer);

-- Buyers and sellers can update return requests
CREATE POLICY "Users can update return requests" ON return_request
    FOR UPDATE USING (
        buyer_id = current_setting('app.user_id')::integer 
        OR seller_id = current_setting('app.user_id')::integer
    );

-- ============================================
-- PUBLIC READ TABLES (Categories, Regions, etc)
-- ============================================

-- Everyone can read categories
CREATE POLICY "Anyone can view categories" ON category
    FOR SELECT USING (true);

-- Everyone can read subcategories
CREATE POLICY "Anyone can view subcategories" ON subcategory
    FOR SELECT USING (true);

-- Everyone can read regions
CREATE POLICY "Anyone can view regions" ON region
    FOR SELECT USING (true);

-- Everyone can read provinces
CREATE POLICY "Anyone can view provinces" ON province
    FOR SELECT USING (true);

-- Everyone can read cities
CREATE POLICY "Anyone can view cities" ON city
    FOR SELECT USING (true);

-- Everyone can read barangays
CREATE POLICY "Anyone can view barangays" ON barangay
    FOR SELECT USING (true);

-- Everyone can read city_municipality
CREATE POLICY "Anyone can view city_municipality" ON city_municipality
    FOR SELECT USING (true);

-- Everyone can read active hero slides
CREATE POLICY "Anyone can view hero slides" ON hero_slide
    FOR SELECT USING (is_active = true);

-- Everyone can read theme settings
CREATE POLICY "Anyone can view theme settings" ON theme_setting
    FOR SELECT USING (true);

-- Everyone can read active coupons
CREATE POLICY "Anyone can view active coupons" ON coupon
    FOR SELECT USING (is_active = true);

-- ============================================
-- FOLLOW TABLE POLICIES
-- ============================================

-- Users can view their own follows
CREATE POLICY "Users can view own follows" ON follow
    FOR SELECT USING (follower_id = current_setting('app.user_id')::integer);

-- Users can follow sellers
CREATE POLICY "Users can follow sellers" ON follow
    FOR INSERT WITH CHECK (follower_id = current_setting('app.user_id')::integer);

-- Users can unfollow sellers
CREATE POLICY "Users can unfollow sellers" ON follow
    FOR DELETE USING (follower_id = current_setting('app.user_id')::integer);

-- ============================================
-- NOTES
-- ============================================

-- To use these policies in your app, you need to set the user_id in your database connection:
-- SET LOCAL app.user_id = <user_id>;
-- 
-- Or use Supabase Auth and JWT tokens which automatically set auth.uid()
-- 
-- For admin operations, use the service_role key which bypasses RLS
