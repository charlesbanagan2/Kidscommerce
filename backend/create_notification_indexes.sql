-- =====================================================
-- NOTIFICATION TABLE PERFORMANCE INDEXES
-- Run this SQL in your Supabase SQL Editor
-- =====================================================

-- Index for user_id lookups (most common query)
CREATE INDEX IF NOT EXISTS idx_notification_user_id 
ON notification(user_id);

-- Index for unread notifications (frequently queried)
CREATE INDEX IF NOT EXISTS idx_notification_is_read 
ON notification(is_read);

-- Index for created_at ordering (used in ORDER BY)
CREATE INDEX IF NOT EXISTS idx_notification_created_at 
ON notification(created_at DESC);

-- Composite index for user + unread queries (most common combination)
CREATE INDEX IF NOT EXISTS idx_notification_user_unread 
ON notification(user_id, is_read);

-- Composite index for user + created_at (pagination queries)
CREATE INDEX IF NOT EXISTS idx_notification_user_created 
ON notification(user_id, created_at DESC);

-- Composite index for user + type filtering
CREATE INDEX IF NOT EXISTS idx_notification_user_type 
ON notification(user_id, type);

-- Composite index for optimal unread count queries
CREATE INDEX IF NOT EXISTS idx_notification_user_unread_created 
ON notification(user_id, is_read, created_at DESC);

-- Index for order_id lookups (when fetching order-related notifications)
CREATE INDEX IF NOT EXISTS idx_notification_order_id 
ON notification(order_id) WHERE order_id IS NOT NULL;

-- Index for actor_user_id (when showing who triggered the notification)
CREATE INDEX IF NOT EXISTS idx_notification_actor_user_id 
ON notification(actor_user_id) WHERE actor_user_id IS NOT NULL;

-- =====================================================
-- ADDITIONAL PERFORMANCE INDEXES FOR OTHER TABLES
-- =====================================================

-- Cart table indexes
CREATE INDEX IF NOT EXISTS idx_cart_user_id ON cart(user_id);
CREATE INDEX IF NOT EXISTS idx_cart_product_id ON cart(product_id);
CREATE INDEX IF NOT EXISTS idx_cart_user_product ON cart(user_id, product_id);

-- Order table indexes
CREATE INDEX IF NOT EXISTS idx_order_buyer_id ON "order"(buyer_id);
CREATE INDEX IF NOT EXISTS idx_order_status ON "order"(status);
CREATE INDEX IF NOT EXISTS idx_order_buyer_status ON "order"(buyer_id, status);
CREATE INDEX IF NOT EXISTS idx_order_created_at ON "order"(created_at DESC);

-- Chat message indexes
CREATE INDEX IF NOT EXISTS idx_chat_buyer_seller ON store_chat_message(buyer_id, seller_id);
CREATE INDEX IF NOT EXISTS idx_chat_seller_unread ON store_chat_message(seller_id, is_read);
CREATE INDEX IF NOT EXISTS idx_chat_created_at ON store_chat_message(created_at DESC);

-- =====================================================
-- VERIFY INDEXES
-- =====================================================

-- Run this to see all indexes on notification table:
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'notification';

-- Run this to see index usage statistics:
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
-- FROM pg_stat_user_indexes
-- WHERE tablename = 'notification'
-- ORDER BY idx_scan DESC;
