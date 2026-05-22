-- =============================================
-- COMPLETE RLS POLICIES FOR ALL TABLES
-- Reference guide - Shows what policies exist
-- =============================================

-- =============================================
-- 1. USER TABLE
-- =============================================
-- Policies:
-- - Allow public registration (anyone can insert)
-- - Users can view their own profile
-- - Users can update their own profile

CREATE POLICY "Allow public registration" ON "user"
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view own profile" ON "user"
  FOR SELECT USING (
    auth.uid()::text = supabase_uid::text
  );

CREATE POLICY "Users can update own profile" ON "user"
  FOR UPDATE USING (
    auth.uid()::text = supabase_uid::text
  );

-- =============================================
-- 2. ADDRESS TABLE
-- =============================================
-- Policies:
-- - Users can view their own addresses
-- - Users can insert their own addresses
-- - Users can update their own addresses
-- - Users can delete their own addresses

CREATE POLICY "Users can view own addresses" ON "address"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = address.user_id
    )
  );

CREATE POLICY "Users can insert own addresses" ON "address"
  FOR INSERT WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = address.user_id
    )
  );

CREATE POLICY "Users can update own addresses" ON "address"
  FOR UPDATE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = address.user_id
    )
  );

CREATE POLICY "Users can delete own addresses" ON "address"
  FOR DELETE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = address.user_id
    )
  );

-- =============================================
-- 3. CART TABLE
-- =============================================
-- Policies:
-- - Users can view their own cart
-- - Users can add to their cart
-- - Users can update their cart
-- - Users can delete from their cart

CREATE POLICY "Users can view own cart" ON "cart"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = cart.user_id
    )
  );

CREATE POLICY "Users can add to cart" ON "cart"
  FOR INSERT WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = cart.user_id
    )
  );

CREATE POLICY "Users can update own cart" ON "cart"
  FOR UPDATE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = cart.user_id
    )
  );

CREATE POLICY "Users can delete from cart" ON "cart"
  FOR DELETE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = cart.user_id
    )
  );

-- =============================================
-- 4. ORDER TABLE (NEW SHOPEE-STYLE POLICIES)
-- =============================================
-- See SHOPEE_STYLE_ORDER_FIX.sql for complete policies
-- Summary:
-- - Service role: Full access
-- - Buyers: View own orders (complete history)
-- - Riders: View assigned + available orders
-- - Sellers: View orders with their products
-- - Buyers: Create orders
-- - Buyers: Update own orders
-- - Riders: Update assigned orders
-- - Sellers: Update orders with their products

-- =============================================
-- 5. ORDER_ITEM TABLE (NEW SHOPEE-STYLE POLICIES)
-- =============================================
-- See SHOPEE_STYLE_ORDER_FIX.sql for complete policies
-- Summary:
-- - Service role: Full access
-- - Buyers: View items in their orders
-- - Riders: View items in assigned/available orders
-- - Sellers: View items for their products
-- - Buyers: Create items during checkout

-- =============================================
-- 6. PRODUCT TABLE
-- =============================================
-- Policies:
-- - Anyone can view active/approved products (public marketplace)
-- - Sellers can view all their own products
-- - Sellers can create products
-- - Sellers can update their own products
-- - Sellers can delete their own products

CREATE POLICY "Anyone can view active products" ON "product"
  FOR SELECT USING (
    status IN ('active', 'approved')
  );

CREATE POLICY "Sellers can view own products" ON "product"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = product.seller_id
    )
  );

CREATE POLICY "Sellers can create products" ON "product"
  FOR INSERT WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = product.seller_id
    )
  );

CREATE POLICY "Sellers can update own products" ON "product"
  FOR UPDATE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = product.seller_id
    )
  );

CREATE POLICY "Sellers can delete own products" ON "product"
  FOR DELETE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = product.seller_id
    )
  );

-- =============================================
-- 7. CATEGORY TABLE
-- =============================================
-- Policies:
-- - Anyone can view categories (public)

CREATE POLICY "Anyone can view categories" ON "category"
  FOR SELECT USING (true);

-- =============================================
-- 8. SUBCATEGORY TABLE
-- =============================================
-- Policies:
-- - Anyone can view subcategories (public)

CREATE POLICY "Anyone can view subcategories" ON "subcategory"
  FOR SELECT USING (true);

-- =============================================
-- 9. NOTIFICATION TABLE
-- =============================================
-- Policies:
-- - Users can view their own notifications
-- - Users can update their own notifications (mark as read)
-- - System can create notifications

CREATE POLICY "Users can view own notifications" ON "notification"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = notification.user_id
    )
  );

CREATE POLICY "Users can update own notifications" ON "notification"
  FOR UPDATE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = notification.user_id
    )
  );

CREATE POLICY "Allow notification creation" ON "notification"
  FOR INSERT WITH CHECK (true);

-- =============================================
-- 10. WALLET_TRANSACTION TABLE
-- =============================================
-- Policies:
-- - Users can view their own wallet transactions
-- - System can create wallet transactions

CREATE POLICY "Users can view own wallet transactions" ON "wallet_transaction"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = wallet_transaction.user_id
    )
  );

CREATE POLICY "Allow wallet transaction creation" ON "wallet_transaction"
  FOR INSERT WITH CHECK (true);

-- =============================================
-- 11. REVIEW TABLE
-- =============================================
-- Policies:
-- - Anyone can view published reviews
-- - Users can view their own reviews (including pending)
-- - Users can create reviews
-- - Users can update their own reviews
-- - Users can delete their own reviews

CREATE POLICY "Anyone can view published reviews" ON "review"
  FOR SELECT USING (
    status = 'published'
  );

CREATE POLICY "Users can view own reviews" ON "review"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = review.user_id
    )
  );

CREATE POLICY "Users can create reviews" ON "review"
  FOR INSERT WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = review.user_id
    )
  );

CREATE POLICY "Users can update own reviews" ON "review"
  FOR UPDATE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = review.user_id
    )
  );

CREATE POLICY "Users can delete own reviews" ON "review"
  FOR DELETE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = review.user_id
    )
  );

-- =============================================
-- 12. WISHLIST TABLE
-- =============================================
-- Policies:
-- - Users can view their own wishlist
-- - Users can add to wishlist
-- - Users can remove from wishlist

CREATE POLICY "Users can view own wishlist" ON "wishlist"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = wishlist.user_id
    )
  );

CREATE POLICY "Users can add to wishlist" ON "wishlist"
  FOR INSERT WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = wishlist.user_id
    )
  );

CREATE POLICY "Users can remove from wishlist" ON "wishlist"
  FOR DELETE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = wishlist.user_id
    )
  );

-- =============================================
-- 13. SELLER_APPLICATION TABLE
-- =============================================
-- Policies:
-- - Users can view their own seller application
-- - Users can create seller application
-- - Users can update their own pending application

CREATE POLICY "Users can view own seller application" ON "seller_application"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = seller_application.user_id
    )
  );

CREATE POLICY "Users can create seller application" ON "seller_application"
  FOR INSERT WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = seller_application.user_id
    )
  );

CREATE POLICY "Users can update own pending application" ON "seller_application"
  FOR UPDATE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = seller_application.user_id
    )
    AND status = 'pending'
  );

-- =============================================
-- 14. RIDER_APPLICATION TABLE
-- =============================================
-- Policies:
-- - Users can view their own rider application
-- - Users can create rider application

CREATE POLICY "Users can view own rider application" ON "rider_application"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = rider_application.user_id
    )
  );

CREATE POLICY "Users can create rider application" ON "rider_application"
  FOR INSERT WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = rider_application.user_id
    )
  );

-- =============================================
-- 15. RETURN_REQUEST TABLE
-- =============================================
-- Policies:
-- - Buyers can view their own return requests
-- - Sellers can view return requests for their products
-- - Buyers can create return requests
-- - Buyers can update their own return requests
-- - Sellers can update return requests for their products

CREATE POLICY "Buyers can view own return requests" ON "return_request"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = return_request.buyer_id
    )
  );

CREATE POLICY "Sellers can view return requests for their products" ON "return_request"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = return_request.seller_id
    )
  );

CREATE POLICY "Buyers can create return requests" ON "return_request"
  FOR INSERT WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = return_request.buyer_id
    )
  );

CREATE POLICY "Buyers can update own return requests" ON "return_request"
  FOR UPDATE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = return_request.buyer_id
    )
  );

CREATE POLICY "Sellers can update return requests for their products" ON "return_request"
  FOR UPDATE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = return_request.seller_id
    )
  );

-- =============================================
-- 16. RETURN_PICKUP TABLE
-- =============================================
-- Policies:
-- - Buyers can view their own return pickups
-- - Riders can view available and assigned return pickups
-- - Riders can update assigned return pickups

CREATE POLICY "Buyers can view own return pickups" ON "return_pickup"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM return_request
      WHERE return_request.id = return_pickup.return_request_id
      AND auth.uid()::text IN (
        SELECT supabase_uid::text FROM "user" WHERE id = return_request.buyer_id
      )
    )
  );

CREATE POLICY "Riders can view return pickups" ON "return_pickup"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = return_pickup.rider_id
    )
    OR return_pickup.rider_id IS NULL
  );

CREATE POLICY "Riders can update assigned return pickups" ON "return_pickup"
  FOR UPDATE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = return_pickup.rider_id
    )
  );

-- =============================================
-- 17. STORE_CHAT_MESSAGE TABLE
-- =============================================
-- Policies:
-- - Users can view their own store chats (buyer-seller)
-- - Users can send store chat messages
-- - Users can update their own store chats

CREATE POLICY "Users can view own store chats" ON "store_chat_message"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" 
      WHERE id = store_chat_message.buyer_id 
         OR id = store_chat_message.seller_id
    )
  );

CREATE POLICY "Users can send store chat messages" ON "store_chat_message"
  FOR INSERT WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" 
      WHERE id = store_chat_message.buyer_id 
         OR id = store_chat_message.seller_id
    )
  );

CREATE POLICY "Users can update own store chats" ON "store_chat_message"
  FOR UPDATE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" 
      WHERE id = store_chat_message.buyer_id 
         OR id = store_chat_message.seller_id
    )
  );

-- =============================================
-- 18. RIDER_CHAT_MESSAGE TABLE
-- =============================================
-- Policies:
-- - Users can view their own rider chats (buyer-rider)
-- - Users can send rider chat messages
-- - Users can update their own rider chats

CREATE POLICY "Users can view own rider chats" ON "rider_chat_message"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" 
      WHERE id = rider_chat_message.buyer_id 
         OR id = rider_chat_message.rider_id
    )
  );

CREATE POLICY "Users can send rider chat messages" ON "rider_chat_message"
  FOR INSERT WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" 
      WHERE id = rider_chat_message.buyer_id 
         OR id = rider_chat_message.rider_id
    )
  );

CREATE POLICY "Users can update own rider chats" ON "rider_chat_message"
  FOR UPDATE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" 
      WHERE id = rider_chat_message.buyer_id 
         OR id = rider_chat_message.rider_id
    )
  );

-- =============================================
-- 19. FOLLOW TABLE
-- =============================================
-- Policies:
-- - Users can view follows (their own and sellers they follow)
-- - Users can follow sellers
-- - Users can unfollow sellers

CREATE POLICY "Users can view follows" ON "follow"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" 
      WHERE id = follow.follower_id 
         OR id = follow.seller_id
    )
  );

CREATE POLICY "Users can follow sellers" ON "follow"
  FOR INSERT WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = follow.follower_id
    )
  );

CREATE POLICY "Users can unfollow sellers" ON "follow"
  FOR DELETE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = follow.follower_id
    )
  );

-- =============================================
-- 20. COUPON TABLE
-- =============================================
-- Policies:
-- - Anyone can view active coupons

CREATE POLICY "Anyone can view active coupons" ON "coupon"
  FOR SELECT USING (
    is_active = true
  );

-- =============================================
-- 21. HERO_SLIDE TABLE
-- =============================================
-- Policies:
-- - Anyone can view active hero slides

CREATE POLICY "Anyone can view active hero slides" ON "hero_slide"
  FOR SELECT USING (
    is_active = true
  );

-- =============================================
-- 22. THEME_SETTING TABLE
-- =============================================
-- Policies:
-- - Anyone can view theme settings

CREATE POLICY "Anyone can view theme settings" ON "theme_setting"
  FOR SELECT USING (true);

-- =============================================
-- 23. REGION/PROVINCE/CITY/BARANGAY TABLES
-- =============================================
-- Policies:
-- - Anyone can view (public address data)

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

-- =============================================
-- 24. ORDER_LABEL TABLE
-- =============================================
-- Policies:
-- - Buyers can view their own order labels
-- - Sellers can view order labels for their products
-- - Riders can view assigned order labels

CREATE POLICY "Buyers can view own order labels" ON "order_label"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_label.order_id
      AND auth.uid()::text IN (
        SELECT supabase_uid::text FROM "user" WHERE id = "order".buyer_id
      )
    )
  );

CREATE POLICY "Sellers can view order labels for their products" ON "order_label"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM order_item oi
      JOIN product p ON oi.product_id = p.id
      WHERE oi.order_id = order_label.order_id
      AND auth.uid()::text IN (
        SELECT supabase_uid::text FROM "user" WHERE id = p.seller_id
      )
    )
  );

CREATE POLICY "Riders can view assigned order labels" ON "order_label"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_label.order_id
      AND auth.uid()::text IN (
        SELECT supabase_uid::text FROM "user" 
        WHERE id = "order".rider_id 
           OR id = "order".picked_up_by
      )
    )
  );

-- =============================================
-- 25. SELLER_ORDER_SEEN TABLE
-- =============================================
-- Policies:
-- - Sellers can view their own order seen records
-- - Sellers can manage their own order seen records

CREATE POLICY "Sellers can view own order seen records" ON "seller_order_seen"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = seller_order_seen.seller_id
    )
  );

CREATE POLICY "Sellers can manage own order seen records" ON "seller_order_seen"
  FOR ALL USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = seller_order_seen.seller_id
    )
  );

-- =============================================
-- 26. RESTOCK_REQUEST TABLE
-- =============================================
-- Policies:
-- - Sellers can view their own restock requests
-- - Sellers can create restock requests

CREATE POLICY "Sellers can view own restock requests" ON "restock_request"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = restock_request.seller_id
    )
  );

CREATE POLICY "Sellers can create restock requests" ON "restock_request"
  FOR INSERT WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = restock_request.seller_id
    )
  );

-- =============================================
-- 27. QR_SCAN_LOG TABLE
-- =============================================
-- Policies:
-- - Users can view their own order scan logs
-- - Riders can create scan logs

CREATE POLICY "Users can view own order scan logs" ON "qr_scan_log"
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = qr_scan_log.order_id
      AND auth.uid()::text IN (
        SELECT supabase_uid::text FROM "user" 
        WHERE id = "order".buyer_id 
           OR id = "order".rider_id
      )
    )
  );

CREATE POLICY "Riders can create scan logs" ON "qr_scan_log"
  FOR INSERT WITH CHECK (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = qr_scan_log.scanned_by
    )
  );

-- =============================================
-- 28. DELIVERY_PERSONNEL TABLE
-- =============================================
-- Policies:
-- - Riders can view their own delivery personnel record
-- - Riders can update their own delivery personnel record

CREATE POLICY "Riders can view own delivery personnel record" ON "delivery_personnel"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = delivery_personnel.user_id
    )
  );

CREATE POLICY "Riders can update own delivery personnel record" ON "delivery_personnel"
  FOR UPDATE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = delivery_personnel.user_id
    )
  );

-- =============================================
-- 29. OAUTH TABLE
-- =============================================
-- Policies:
-- - Users can view their own oauth records

CREATE POLICY "Users can view own oauth records" ON "oauth"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = oauth.user_id
    )
  );

-- =============================================
-- 30. ADMIN_PROFILE TABLE
-- =============================================
-- Policies:
-- - Admins can view their own profile
-- - Admins can update their own profile

CREATE POLICY "Admins can view own profile" ON "admin_profile"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = admin_profile.user_id
    )
  );

CREATE POLICY "Admins can update own profile" ON "admin_profile"
  FOR UPDATE USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = admin_profile.user_id
    )
  );

-- =============================================
-- 31. ADMIN_SECURITY_LOG TABLE
-- =============================================
-- Policies:
-- - Admins can view their own security logs

CREATE POLICY "Admins can view own security logs" ON "admin_security_log"
  FOR SELECT USING (
    auth.uid()::text IN (
      SELECT supabase_uid::text FROM "user" WHERE id = admin_security_log.user_id
    )
  );

-- =============================================
-- SUMMARY
-- =============================================
-- Total tables with RLS policies: 31+
-- All policies use auth.uid() for user identification
-- Service role (backend) bypasses all RLS policies
-- Each user can only access their own data
-- Public data (categories, products, etc.) is accessible to all
