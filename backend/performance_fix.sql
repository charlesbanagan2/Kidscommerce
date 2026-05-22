-- Performance optimization indexes for slow queries
-- Run this SQL to speed up common queries

-- Chat messages indexes
CREATE INDEX IF NOT EXISTS idx_chat_sender_receiver ON chat_message(sender_id, receiver_id);
CREATE INDEX IF NOT EXISTS idx_chat_receiver_unread ON chat_message(receiver_id, is_read);
CREATE INDEX IF NOT EXISTS idx_chat_created_at ON chat_message(created_at DESC);

-- Notification indexes
CREATE INDEX IF NOT EXISTS idx_notification_user_read ON notification(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_notification_user_type ON notification(user_id, type);
CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notification(created_at DESC);

-- Order indexes
CREATE INDEX IF NOT EXISTS idx_order_buyer_status ON "order"(buyer_id, status);
CREATE INDEX IF NOT EXISTS idx_order_seller_status ON "order"(seller_id, status);
CREATE INDEX IF NOT EXISTS idx_order_created_at ON "order"(created_at DESC);

-- Cart indexes
CREATE INDEX IF NOT EXISTS idx_cart_user ON cart(user_id);

-- Wishlist indexes
CREATE INDEX IF NOT EXISTS idx_wishlist_user ON wishlist(user_id);

-- Review indexes
CREATE INDEX IF NOT EXISTS idx_review_product ON review(product_id);
CREATE INDEX IF NOT EXISTS idx_review_created_at ON review(created_at DESC);

-- Product indexes
CREATE INDEX IF NOT EXISTS idx_product_seller ON product(seller_id);
CREATE INDEX IF NOT EXISTS idx_product_category ON product(category_id);
