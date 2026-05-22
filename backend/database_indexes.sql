-- ============================================================================
-- PostgreSQL Database Indexes for Kids E-Commerce Platform (Supabase)
-- Generated for Performance Optimization
-- Compatible with PostgreSQL 15+
-- ============================================================================

-- ============================================================================
-- USER TABLE INDEXES
-- ============================================================================

-- Email lookup (login, registration checks)
CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);

-- Role-based queries (admin dashboard, seller/buyer filtering)
CREATE INDEX IF NOT EXISTS idx_user_role ON "user"(role);

-- Status filtering (active users, pending approvals)
CREATE INDEX IF NOT EXISTS idx_user_status ON "user"(status);

-- Composite index for role + status queries (common in admin dashboards)
CREATE INDEX IF NOT EXISTS idx_user_role_status ON "user"(role, status);

-- Email verification lookups
CREATE INDEX IF NOT EXISTS idx_user_email_verified ON "user"(email_verified);

-- Created date for sorting/filtering new users
CREATE INDEX IF NOT EXISTS idx_user_created_at ON "user"(created_at DESC);


-- ============================================================================
-- SELLER APPLICATION TABLE INDEXES
-- ============================================================================

-- Foreign key to user
CREATE INDEX IF NOT EXISTS idx_seller_application_user_id ON seller_application(user_id);

-- Status filtering (pending, approved, rejected applications)
CREATE INDEX IF NOT EXISTS idx_seller_application_status ON seller_application(status);

-- Reviewer tracking
CREATE INDEX IF NOT EXISTS idx_seller_application_reviewed_by ON seller_application(reviewed_by);

-- Application date sorting
CREATE INDEX IF NOT EXISTS idx_seller_application_applied_at ON seller_application(applied_at DESC);

-- Composite for user + status (check if user has approved application)
CREATE INDEX IF NOT EXISTS idx_seller_application_user_status ON seller_application(user_id, status);


-- ============================================================================
-- PRODUCT TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_product_category_id ON product(category_id);
CREATE INDEX IF NOT EXISTS idx_product_subcategory_id ON product(subcategory_id);
CREATE INDEX IF NOT EXISTS idx_product_seller_id ON product(seller_id);

-- Status filtering (active, pending, approved products)
CREATE INDEX IF NOT EXISTS idx_product_status ON product(status);

-- Featured products flag
CREATE INDEX IF NOT EXISTS idx_product_featured ON product(featured);

-- New arrivals flag
CREATE INDEX IF NOT EXISTS idx_product_show_in_new_arrival ON product(show_in_new_arrival);

-- Created date for sorting (newest products)
CREATE INDEX IF NOT EXISTS idx_product_created_at ON product(created_at DESC);

-- Price sorting/filtering
CREATE INDEX IF NOT EXISTS idx_product_price ON product(price);

-- Stock availability checks
CREATE INDEX IF NOT EXISTS idx_product_stock ON product(stock);

-- Composite for category + status (shop page filtering)
CREATE INDEX IF NOT EXISTS idx_product_category_status ON product(category_id, status);

-- Composite for seller + status (seller dashboard)
CREATE INDEX IF NOT EXISTS idx_product_seller_status ON product(seller_id, status);

-- Composite for featured + status (homepage featured products)
CREATE INDEX IF NOT EXISTS idx_product_featured_status ON product(featured, status) WHERE featured = true;


-- ============================================================================
-- CATEGORY TABLE INDEXES
-- ============================================================================

-- Status filtering (active categories)
CREATE INDEX IF NOT EXISTS idx_category_status ON category(status);

-- Name for sorting/searching
CREATE INDEX IF NOT EXISTS idx_category_name ON category(name);

-- Created date
CREATE INDEX IF NOT EXISTS idx_category_created_at ON category(created_at DESC);


-- ============================================================================
-- SUBCATEGORY TABLE INDEXES
-- ============================================================================

-- Foreign key to category
CREATE INDEX IF NOT EXISTS idx_subcategory_category_id ON subcategory(category_id);

-- Status filtering
CREATE INDEX IF NOT EXISTS idx_subcategory_status ON subcategory(status);

-- Name for sorting
CREATE INDEX IF NOT EXISTS idx_subcategory_name ON subcategory(name);

-- Composite for category + status
CREATE INDEX IF NOT EXISTS idx_subcategory_category_status ON subcategory(category_id, status);


-- ============================================================================
-- ORDER TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_order_buyer_id ON "order"(buyer_id);
CREATE INDEX IF NOT EXISTS idx_order_rider_id ON "order"(rider_id);
CREATE INDEX IF NOT EXISTS idx_order_coupon_id ON "order"(coupon_id);

-- Status filtering (critical for order management)
CREATE INDEX IF NOT EXISTS idx_order_status ON "order"(status);

-- Payment status filtering
CREATE INDEX IF NOT EXISTS idx_order_payment_status ON "order"(payment_status);

-- Payment method filtering
CREATE INDEX IF NOT EXISTS idx_order_payment_method ON "order"(payment_method);

-- Created date for sorting orders
CREATE INDEX IF NOT EXISTS idx_order_created_at ON "order"(created_at DESC);

-- Updated date for recent changes
CREATE INDEX IF NOT EXISTS idx_order_updated_at ON "order"(updated_at DESC);

-- QR code lookup (order tracking)
CREATE INDEX IF NOT EXISTS idx_order_qr_code ON "order"(qr_code);

-- Tracking number lookup
CREATE INDEX IF NOT EXISTS idx_order_tracking_number ON "order"(tracking_number);

-- Batch code for logistics
CREATE INDEX IF NOT EXISTS idx_order_batch_code ON "order"(batch_code);

-- Composite for buyer + status (buyer order history)
CREATE INDEX IF NOT EXISTS idx_order_buyer_status ON "order"(buyer_id, status);

-- Composite for rider + status (rider dashboard)
CREATE INDEX IF NOT EXISTS idx_order_rider_status ON "order"(rider_id, status);

-- Composite for payment status + order status
CREATE INDEX IF NOT EXISTS idx_order_payment_order_status ON "order"(payment_status, status);


-- ============================================================================
-- ORDER ITEM TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_order_item_order_id ON order_item(order_id);
CREATE INDEX IF NOT EXISTS idx_order_item_product_id ON order_item(product_id);

-- Composite for order + product (order details page)
CREATE INDEX IF NOT EXISTS idx_order_item_order_product ON order_item(order_id, product_id);


-- ============================================================================
-- CART TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_cart_user_id ON cart(user_id);
CREATE INDEX IF NOT EXISTS idx_cart_product_id ON cart(product_id);

-- Created date for cart expiration
CREATE INDEX IF NOT EXISTS idx_cart_created_at ON cart(created_at DESC);

-- Composite for user + product (check if item already in cart)
CREATE INDEX IF NOT EXISTS idx_cart_user_product ON cart(user_id, product_id);


-- ============================================================================
-- WISHLIST TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_wishlist_user_id ON wishlist(user_id);
CREATE INDEX IF NOT EXISTS idx_wishlist_product_id ON wishlist(product_id);

-- Created date
CREATE INDEX IF NOT EXISTS idx_wishlist_created_at ON wishlist(created_at DESC);

-- Composite for user + product (check if already in wishlist)
CREATE INDEX IF NOT EXISTS idx_wishlist_user_product ON wishlist(user_id, product_id);


-- ============================================================================
-- REVIEW TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_review_product_id ON review(product_id);
CREATE INDEX IF NOT EXISTS idx_review_user_id ON review(user_id);
CREATE INDEX IF NOT EXISTS idx_review_order_id ON review(order_id);

-- Status filtering (published, pending, hidden)
CREATE INDEX IF NOT EXISTS idx_review_status ON review(status);

-- Rating for filtering/sorting
CREATE INDEX IF NOT EXISTS idx_review_rating ON review(rating);

-- Created date for sorting
CREATE INDEX IF NOT EXISTS idx_review_created_at ON review(created_at DESC);

-- Verified purchase flag
CREATE INDEX IF NOT EXISTS idx_review_verified_purchase ON review(verified_purchase);

-- Composite for product + status (product detail page reviews)
CREATE INDEX IF NOT EXISTS idx_review_product_status ON review(product_id, status);


-- ============================================================================
-- ADDRESS TABLE INDEXES
-- ============================================================================

-- Foreign key to user
CREATE INDEX IF NOT EXISTS idx_address_user_id ON address(user_id);

-- Default address lookup
CREATE INDEX IF NOT EXISTS idx_address_is_default ON address(is_default);

-- Created date
CREATE INDEX IF NOT EXISTS idx_address_created_at ON address(created_at DESC);

-- Composite for user + default (get user's default address)
CREATE INDEX IF NOT EXISTS idx_address_user_default ON address(user_id, is_default);


-- ============================================================================
-- NOTIFICATION TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notification(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_actor_user_id ON notification(actor_user_id);
CREATE INDEX IF NOT EXISTS idx_notification_order_id ON notification(order_id);

-- Read status filtering
CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notification(is_read);

-- Type filtering
CREATE INDEX IF NOT EXISTS idx_notification_type ON notification(type);

-- Created date for sorting
CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notification(created_at DESC);

-- Composite for user + read status (unread notifications)
CREATE INDEX IF NOT EXISTS idx_notification_user_read ON notification(user_id, is_read);

-- Composite for user + created (user's recent notifications)
CREATE INDEX IF NOT EXISTS idx_notification_user_created ON notification(user_id, created_at DESC);


-- ============================================================================
-- RETURN REQUEST TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_return_request_order_id ON return_request(order_id);
CREATE INDEX IF NOT EXISTS idx_return_request_order_item_id ON return_request(order_item_id);
CREATE INDEX IF NOT EXISTS idx_return_request_buyer_id ON return_request(buyer_id);
CREATE INDEX IF NOT EXISTS idx_return_request_seller_id ON return_request(seller_id);
CREATE INDEX IF NOT EXISTS idx_return_request_processed_by ON return_request(processed_by);

-- Status filtering (submitted, approved, rejected, etc.)
CREATE INDEX IF NOT EXISTS idx_return_request_status ON return_request(status);

-- Request type (return vs refund)
CREATE INDEX IF NOT EXISTS idx_return_request_request_type ON return_request(request_type);

-- Created date
CREATE INDEX IF NOT EXISTS idx_return_request_created_at ON return_request(created_at DESC);

-- Updated date
CREATE INDEX IF NOT EXISTS idx_return_request_updated_at ON return_request(updated_at DESC);

-- Composite for seller + status (seller return dashboard)
CREATE INDEX IF NOT EXISTS idx_return_request_seller_status ON return_request(seller_id, status);

-- Composite for buyer + status (buyer return history)
CREATE INDEX IF NOT EXISTS idx_return_request_buyer_status ON return_request(buyer_id, status);


-- ============================================================================
-- RESTOCK REQUEST TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_restock_request_product_id ON restock_request(product_id);
CREATE INDEX IF NOT EXISTS idx_restock_request_seller_id ON restock_request(seller_id);
CREATE INDEX IF NOT EXISTS idx_restock_request_processed_by ON restock_request(processed_by);

-- Status filtering
CREATE INDEX IF NOT EXISTS idx_restock_request_status ON restock_request(status);

-- Created date
CREATE INDEX IF NOT EXISTS idx_restock_request_created_at ON restock_request(created_at DESC);

-- Composite for seller + status
CREATE INDEX IF NOT EXISTS idx_restock_request_seller_status ON restock_request(seller_id, status);


-- ============================================================================
-- RETURN PICKUP TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_return_pickup_return_request_id ON return_pickup(return_request_id);
CREATE INDEX IF NOT EXISTS idx_return_pickup_rider_id ON return_pickup(rider_id);

-- Status filtering (available, waiting_rider_pickup, etc.)
CREATE INDEX IF NOT EXISTS idx_return_pickup_status ON return_pickup(status);

-- Created date
CREATE INDEX IF NOT EXISTS idx_return_pickup_created_at ON return_pickup(created_at DESC);

-- Updated date
CREATE INDEX IF NOT EXISTS idx_return_pickup_updated_at ON return_pickup(updated_at DESC);

-- Composite for rider + status
CREATE INDEX IF NOT EXISTS idx_return_pickup_rider_status ON return_pickup(rider_id, status);


-- ============================================================================
-- WALLET TRANSACTION TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_wallet_transaction_user_id ON wallet_transaction(user_id);
CREATE INDEX IF NOT EXISTS idx_wallet_transaction_order_id ON wallet_transaction(order_id);

-- Type filtering (credit vs debit)
CREATE INDEX IF NOT EXISTS idx_wallet_transaction_type ON wallet_transaction(type);

-- Source filtering
CREATE INDEX IF NOT EXISTS idx_wallet_transaction_source ON wallet_transaction(source);

-- Created date for transaction history
CREATE INDEX IF NOT EXISTS idx_wallet_transaction_created_at ON wallet_transaction(created_at DESC);

-- Composite for user + type (user's credits/debits)
CREATE INDEX IF NOT EXISTS idx_wallet_transaction_user_type ON wallet_transaction(user_id, type);

-- Composite for user + created (user's transaction history)
CREATE INDEX IF NOT EXISTS idx_wallet_transaction_user_created ON wallet_transaction(user_id, created_at DESC);


-- ============================================================================
-- STORE CHAT MESSAGE TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_store_chat_buyer_id ON store_chat_message(buyer_id);
CREATE INDEX IF NOT EXISTS idx_store_chat_seller_id ON store_chat_message(seller_id);
CREATE INDEX IF NOT EXISTS idx_store_chat_product_id ON store_chat_message(product_id);

-- Sender role filtering
CREATE INDEX IF NOT EXISTS idx_store_chat_sender_role ON store_chat_message(sender_role);

-- Read status
CREATE INDEX IF NOT EXISTS idx_store_chat_is_read ON store_chat_message(is_read);

-- Created date for message ordering
CREATE INDEX IF NOT EXISTS idx_store_chat_created_at ON store_chat_message(created_at DESC);

-- Composite for buyer + seller (conversation lookup)
CREATE INDEX IF NOT EXISTS idx_store_chat_buyer_seller ON store_chat_message(buyer_id, seller_id);

-- Composite for seller + read status (unread messages for seller)
CREATE INDEX IF NOT EXISTS idx_store_chat_seller_read ON store_chat_message(seller_id, is_read);


-- ============================================================================
-- RIDER CHAT MESSAGE TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_rider_chat_buyer_id ON rider_chat_message(buyer_id);
CREATE INDEX IF NOT EXISTS idx_rider_chat_rider_id ON rider_chat_message(rider_id);
CREATE INDEX IF NOT EXISTS idx_rider_chat_order_id ON rider_chat_message(order_id);

-- Sender role filtering
CREATE INDEX IF NOT EXISTS idx_rider_chat_sender_role ON rider_chat_message(sender_role);

-- Read status
CREATE INDEX IF NOT EXISTS idx_rider_chat_is_read ON rider_chat_message(is_read);

-- Created date
CREATE INDEX IF NOT EXISTS idx_rider_chat_created_at ON rider_chat_message(created_at DESC);

-- Composite for buyer + rider (conversation lookup)
CREATE INDEX IF NOT EXISTS idx_rider_chat_buyer_rider ON rider_chat_message(buyer_id, rider_id);


-- ============================================================================
-- COUPON TABLE INDEXES
-- ============================================================================

-- Code lookup (checkout validation)
CREATE INDEX IF NOT EXISTS idx_coupon_code ON coupon(code);

-- Active status filtering
CREATE INDEX IF NOT EXISTS idx_coupon_is_active ON coupon(is_active);

-- Validity date range filtering
CREATE INDEX IF NOT EXISTS idx_coupon_valid_from ON coupon(valid_from);
CREATE INDEX IF NOT EXISTS idx_coupon_valid_until ON coupon(valid_until);

-- Created date
CREATE INDEX IF NOT EXISTS idx_coupon_created_at ON coupon(created_at DESC);

-- Composite for active + validity (valid coupons)
CREATE INDEX IF NOT EXISTS idx_coupon_active_valid ON coupon(is_active, valid_until) WHERE is_active = true;


-- ============================================================================
-- FOLLOW TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_follow_follower_id ON follow(follower_id);
CREATE INDEX IF NOT EXISTS idx_follow_seller_id ON follow(seller_id);

-- Created date
CREATE INDEX IF NOT EXISTS idx_follow_created_at ON follow(created_at DESC);

-- Composite for follower + seller (check if following)
CREATE INDEX IF NOT EXISTS idx_follow_follower_seller ON follow(follower_id, seller_id);


-- ============================================================================
-- RIDER APPLICATION TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_rider_application_user_id ON rider_application(user_id);
CREATE INDEX IF NOT EXISTS idx_rider_application_reviewed_by ON rider_application(reviewed_by);

-- Status filtering
CREATE INDEX IF NOT EXISTS idx_rider_application_status ON rider_application(status);

-- Applied date
CREATE INDEX IF NOT EXISTS idx_rider_application_applied_at ON rider_application(applied_at DESC);

-- Composite for user + status
CREATE INDEX IF NOT EXISTS idx_rider_application_user_status ON rider_application(user_id, status);


-- ============================================================================
-- DELIVERY PERSONNEL TABLE INDEXES
-- ============================================================================

-- Foreign key to user
CREATE INDEX IF NOT EXISTS idx_delivery_personnel_user_id ON delivery_personnel(user_id);

-- Employee ID lookup
CREATE INDEX IF NOT EXISTS idx_delivery_personnel_employee_id ON delivery_personnel(employee_id);

-- Status filtering
CREATE INDEX IF NOT EXISTS idx_delivery_personnel_status ON delivery_personnel(status);

-- Created date
CREATE INDEX IF NOT EXISTS idx_delivery_personnel_created_at ON delivery_personnel(created_at DESC);


-- ============================================================================
-- ORDER LABEL TABLE INDEXES
-- ============================================================================

-- Foreign key to order
CREATE INDEX IF NOT EXISTS idx_order_label_order_id ON order_label(order_id);

-- QR code lookup
CREATE INDEX IF NOT EXISTS idx_order_label_qr_code ON order_label(qr_code);

-- Tracking number lookup
CREATE INDEX IF NOT EXISTS idx_order_label_tracking_number ON order_label(tracking_number);

-- Batch code
CREATE INDEX IF NOT EXISTS idx_order_label_batch_code ON order_label(batch_code);

-- Status filtering
CREATE INDEX IF NOT EXISTS idx_order_label_status ON order_label(status);

-- Created date
CREATE INDEX IF NOT EXISTS idx_order_label_created_at ON order_label(created_at DESC);


-- ============================================================================
-- QR SCAN LOG TABLE INDEXES
-- ============================================================================

-- Foreign keys
CREATE INDEX IF NOT EXISTS idx_qr_scan_log_order_id ON qr_scan_log(order_id);
CREATE INDEX IF NOT EXISTS idx_qr_scan_log_order_label_id ON qr_scan_log(order_label_id);
CREATE INDEX IF NOT EXISTS idx_qr_scan_log_scanned_by ON qr_scan_log(scanned_by);

-- QR code lookup
CREATE INDEX IF NOT EXISTS idx_qr_scan_log_qr_code ON qr_scan_log(qr_code);

-- Scan type filtering
CREATE INDEX IF NOT EXISTS idx_qr_scan_log_scan_type ON qr_scan_log(scan_type);

-- Created date
CREATE INDEX IF NOT EXISTS idx_qr_scan_log_created_at ON qr_scan_log(created_at DESC);


-- ============================================================================
-- SELLER ORDER SEEN TABLE INDEXES
-- ============================================================================

-- Composite for seller + order (check if seller has seen order)
CREATE INDEX IF NOT EXISTS idx_seller_order_seen_seller_order ON seller_order_seen(seller_id, order_id);

-- Seen date
CREATE INDEX IF NOT EXISTS idx_seller_order_seen_seen_at ON seller_order_seen(seen_at DESC);


-- ============================================================================
-- HERO SLIDE TABLE INDEXES
-- ============================================================================

-- Active status filtering
CREATE INDEX IF NOT EXISTS idx_hero_slide_is_active ON hero_slide(is_active);

-- Created date for ordering
CREATE INDEX IF NOT EXISTS idx_hero_slide_created_at ON hero_slide(created_at ASC);


-- ============================================================================
-- THEME SETTING TABLE INDEXES
-- ============================================================================
-- No indexes needed - typically single row table


-- ============================================================================
-- PSGC (Philippine Standard Geographic Code) TABLE INDEXES
-- ============================================================================

-- Region table
CREATE INDEX IF NOT EXISTS idx_region_code ON region(code);
CREATE INDEX IF NOT EXISTS idx_region_name ON region(name);

-- Province table
CREATE INDEX IF NOT EXISTS idx_province_code ON province(code);
CREATE INDEX IF NOT EXISTS idx_province_region_code ON province(region_code);
CREATE INDEX IF NOT EXISTS idx_province_name ON province(name);

-- City table
CREATE INDEX IF NOT EXISTS idx_city_code ON city(code);
CREATE INDEX IF NOT EXISTS idx_city_province_code ON city(province_code);
CREATE INDEX IF NOT EXISTS idx_city_name ON city(name);

-- Barangay table
CREATE INDEX IF NOT EXISTS idx_barangay_code ON barangay(code);
CREATE INDEX IF NOT EXISTS idx_barangay_city_code ON barangay(city_code);
CREATE INDEX IF NOT EXISTS idx_barangay_name ON barangay(name);

-- City Municipality table
CREATE INDEX IF NOT EXISTS idx_city_municipality_psgc_code ON city_municipality(psgc_code);
CREATE INDEX IF NOT EXISTS idx_city_municipality_province_id ON city_municipality(province_id);
CREATE INDEX IF NOT EXISTS idx_city_municipality_name ON city_municipality(name);


-- ============================================================================
-- OAUTH TABLE INDEXES
-- ============================================================================

-- Provider user ID lookup (OAuth login)
CREATE INDEX IF NOT EXISTS idx_oauth_provider_user_id ON oauth(provider_user_id);

-- User ID lookup
CREATE INDEX IF NOT EXISTS idx_oauth_user_id ON oauth(user_id);


-- ============================================================================
-- ADMIN PROFILE TABLE INDEXES
-- ============================================================================

-- Foreign key to user
CREATE INDEX IF NOT EXISTS idx_admin_profile_user_id ON admin_profile(user_id);

-- Account status filtering
CREATE INDEX IF NOT EXISTS idx_admin_profile_account_status ON admin_profile(account_status);

-- Last login for activity tracking
CREATE INDEX IF NOT EXISTS idx_admin_profile_last_login ON admin_profile(last_login DESC);


-- ============================================================================
-- ADMIN SECURITY LOG TABLE INDEXES
-- ============================================================================

-- Foreign key to user
CREATE INDEX IF NOT EXISTS idx_admin_security_log_user_id ON admin_security_log(user_id);

-- Action filtering
CREATE INDEX IF NOT EXISTS idx_admin_security_log_action ON admin_security_log(action);

-- Created date for log history
CREATE INDEX IF NOT EXISTS idx_admin_security_log_created_at ON admin_security_log(created_at DESC);

-- IP address for security analysis
CREATE INDEX IF NOT EXISTS idx_admin_security_log_ip_address ON admin_security_log(ip_address);


-- ============================================================================
-- PERFORMANCE NOTES
-- ============================================================================
-- 1. All foreign key columns are indexed to speed up JOIN operations
-- 2. Status columns are indexed for filtering (pending, active, completed, etc.)
-- 3. Created/updated timestamps are indexed DESC for recent-first sorting
-- 4. Composite indexes are created for common query patterns
-- 5. Unique lookup columns (email, code, tracking_number) are indexed
-- 6. Boolean flags used in WHERE clauses are indexed
-- 7. Partial indexes are used where appropriate (e.g., featured products)
--
-- MAINTENANCE:
-- - Monitor index usage with: SELECT * FROM pg_stat_user_indexes;
-- - Remove unused indexes to reduce write overhead
-- - Consider REINDEX periodically for heavily updated tables
-- - Use EXPLAIN ANALYZE to verify query plans use these indexes
-- ============================================================================
