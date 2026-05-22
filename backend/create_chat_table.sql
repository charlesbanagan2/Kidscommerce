-- Create chat_message table for unified chat system
-- Run this in Supabase SQL Editor

-- Drop table if exists (for clean reinstall)
DROP TABLE IF EXISTS chat_message CASCADE;

-- Create chat_message table
CREATE TABLE chat_message (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    receiver_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    product_id INTEGER REFERENCES product(id) ON DELETE SET NULL,
    order_id INTEGER REFERENCES "order"(id) ON DELETE SET NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_chat_message_sender ON chat_message(sender_id);
CREATE INDEX idx_chat_message_receiver ON chat_message(receiver_id);
CREATE INDEX idx_chat_message_product ON chat_message(product_id);
CREATE INDEX idx_chat_message_order ON chat_message(order_id);
CREATE INDEX idx_chat_message_created_at ON chat_message(created_at DESC);
CREATE INDEX idx_chat_message_unread ON chat_message(receiver_id, is_read) WHERE is_read = FALSE;

-- Create composite indexes for common queries
CREATE INDEX idx_chat_message_conversation ON chat_message(sender_id, receiver_id, created_at DESC);
CREATE INDEX idx_chat_message_product_conversation ON chat_message(product_id, sender_id, receiver_id, created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE chat_message ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can see messages they sent or received
CREATE POLICY "Users can view their own messages"
ON chat_message
FOR SELECT
USING (
    auth.uid()::text::integer = sender_id 
    OR auth.uid()::text::integer = receiver_id
);

-- RLS Policy: Users can insert messages they send
CREATE POLICY "Users can send messages"
ON chat_message
FOR INSERT
WITH CHECK (auth.uid()::text::integer = sender_id);

-- RLS Policy: Users can update messages they received (mark as read)
CREATE POLICY "Users can mark received messages as read"
ON chat_message
FOR UPDATE
USING (auth.uid()::text::integer = receiver_id)
WITH CHECK (auth.uid()::text::integer = receiver_id);

-- Grant permissions
GRANT ALL ON chat_message TO authenticated;
GRANT ALL ON chat_message TO anon;
GRANT USAGE, SELECT ON SEQUENCE chat_message_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE chat_message_id_seq TO anon;

-- Verify table creation
SELECT 
    'chat_message table created successfully' as status,
    COUNT(*) as message_count 
FROM chat_message;
