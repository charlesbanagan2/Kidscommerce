-- ============================================
-- CHAT MESSAGE TABLE VERIFICATION AND SETUP
-- ============================================

-- Check if chat_message table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'chat_message'
);

-- If table doesn't exist, create it
CREATE TABLE IF NOT EXISTS chat_message (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    receiver_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    product_id INTEGER REFERENCES product(id) ON DELETE SET NULL,
    order_id INTEGER REFERENCES "order"(id) ON DELETE SET NULL,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_chat_message_sender ON chat_message(sender_id);
CREATE INDEX IF NOT EXISTS idx_chat_message_receiver ON chat_message(receiver_id);
CREATE INDEX IF NOT EXISTS idx_chat_message_product ON chat_message(product_id);
CREATE INDEX IF NOT EXISTS idx_chat_message_order ON chat_message(order_id);
CREATE INDEX IF NOT EXISTS idx_chat_message_created ON chat_message(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_message_unread ON chat_message(receiver_id, is_read) WHERE is_read = FALSE;

-- Create composite index for conversation queries
CREATE INDEX IF NOT EXISTS idx_chat_message_conversation 
ON chat_message(sender_id, receiver_id, created_at DESC);

-- Verify table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'chat_message'
ORDER BY ordinal_position;

-- Check existing messages
SELECT COUNT(*) as total_messages FROM chat_message;

-- Check messages by sender/receiver
SELECT 
    u1.first_name || ' ' || u1.last_name as sender,
    u2.first_name || ' ' || u2.last_name as receiver,
    COUNT(*) as message_count
FROM chat_message cm
JOIN "user" u1 ON cm.sender_id = u1.id
JOIN "user" u2 ON cm.receiver_id = u2.id
GROUP BY u1.id, u1.first_name, u1.last_name, u2.id, u2.first_name, u2.last_name
ORDER BY message_count DESC;

-- Check unread messages
SELECT 
    u.first_name || ' ' || u.last_name as receiver,
    COUNT(*) as unread_count
FROM chat_message cm
JOIN "user" u ON cm.receiver_id = u.id
WHERE cm.is_read = FALSE
GROUP BY u.id, u.first_name, u.last_name
ORDER BY unread_count DESC;

-- Sample query: Get conversation between two users
-- Replace [buyer_id] and [seller_id] with actual IDs
/*
SELECT 
    cm.id,
    cm.sender_id,
    cm.receiver_id,
    cm.message,
    cm.product_id,
    cm.is_read,
    cm.created_at,
    u.first_name || ' ' || u.last_name as sender_name,
    p.name as product_name
FROM chat_message cm
JOIN "user" u ON cm.sender_id = u.id
LEFT JOIN product p ON cm.product_id = p.id
WHERE (cm.sender_id = [buyer_id] AND cm.receiver_id = [seller_id])
   OR (cm.sender_id = [seller_id] AND cm.receiver_id = [buyer_id])
ORDER BY cm.created_at ASC;
*/

-- Sample query: Get all conversations for a seller
-- Replace [seller_id] with actual ID
/*
SELECT DISTINCT 
    u.id as buyer_id,
    u.first_name || ' ' || u.last_name as buyer_name,
    (SELECT COUNT(*) 
     FROM chat_message 
     WHERE sender_id = u.id 
     AND receiver_id = [seller_id] 
     AND is_read = FALSE) as unread_count,
    (SELECT message 
     FROM chat_message 
     WHERE (sender_id = u.id AND receiver_id = [seller_id])
        OR (sender_id = [seller_id] AND receiver_id = u.id)
     ORDER BY created_at DESC 
     LIMIT 1) as last_message,
    (SELECT created_at 
     FROM chat_message 
     WHERE (sender_id = u.id AND receiver_id = [seller_id])
        OR (sender_id = [seller_id] AND receiver_id = u.id)
     ORDER BY created_at DESC 
     LIMIT 1) as last_message_time
FROM "user" u
WHERE EXISTS (
    SELECT 1 FROM chat_message cm
    WHERE (cm.sender_id = u.id AND cm.receiver_id = [seller_id])
       OR (cm.sender_id = [seller_id] AND cm.receiver_id = u.id)
)
ORDER BY last_message_time DESC;
*/

-- ============================================
-- MIGRATION FROM OLD StoreChatMessage TABLE
-- ============================================

-- If you have old messages in StoreChatMessage, migrate them:
/*
INSERT INTO chat_message (sender_id, receiver_id, message, product_id, is_read, created_at)
SELECT 
    CASE 
        WHEN sender_role = 'buyer' THEN buyer_id
        WHEN sender_role = 'seller' THEN seller_id
    END as sender_id,
    CASE 
        WHEN sender_role = 'buyer' THEN seller_id
        WHEN sender_role = 'seller' THEN buyer_id
    END as receiver_id,
    message,
    product_id,
    is_read,
    created_at
FROM store_chat_message
WHERE NOT EXISTS (
    SELECT 1 FROM chat_message cm
    WHERE cm.message = store_chat_message.message
    AND cm.created_at = store_chat_message.created_at
);
*/

-- ============================================
-- CLEANUP (OPTIONAL)
-- ============================================

-- After verifying migration, you can drop old table:
-- DROP TABLE IF EXISTS store_chat_message CASCADE;

-- ============================================
-- TESTING QUERIES
-- ============================================

-- Test 1: Insert a test message
/*
INSERT INTO chat_message (sender_id, receiver_id, message, is_read, created_at)
VALUES (1, 2, 'Test message from buyer to seller', FALSE, CURRENT_TIMESTAMP)
RETURNING *;
*/

-- Test 2: Mark message as read
/*
UPDATE chat_message
SET is_read = TRUE
WHERE sender_id = 1 AND receiver_id = 2 AND is_read = FALSE
RETURNING *;
*/

-- Test 3: Get unread count for a user
/*
SELECT COUNT(*) as unread_count
FROM chat_message
WHERE receiver_id = 2 AND is_read = FALSE;
*/

-- ============================================
-- PERFORMANCE MONITORING
-- ============================================

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE tablename = 'chat_message'
ORDER BY idx_scan DESC;

-- Check table size
SELECT 
    pg_size_pretty(pg_total_relation_size('chat_message')) as total_size,
    pg_size_pretty(pg_relation_size('chat_message')) as table_size,
    pg_size_pretty(pg_indexes_size('chat_message')) as indexes_size;

-- ============================================
-- MAINTENANCE
-- ============================================

-- Vacuum and analyze for optimal performance
VACUUM ANALYZE chat_message;

-- Reindex if needed
REINDEX TABLE chat_message;

-- ============================================
-- DONE!
-- ============================================
