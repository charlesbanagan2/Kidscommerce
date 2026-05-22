-- ============================================
-- CLEAR ALL DATA FROM SUPABASE DATABASE
-- WARNING: This will delete ALL data!
-- ============================================

-- Disable foreign key checks temporarily to allow deletion in any order
SET session_replication_role = 'replica';

-- Clear all tables (order matters for foreign keys)
TRUNCATE TABLE 
    "notification",
    "admin_security_log",
    "admin_profile",
    "address",
    "cart",
    "chat_message",
    "chat_participant",
    "conversation",
    "delivery_personnel",
    "hero_slide",
    "notification_preferences",
    "order_item",
    "order",
    "password_reset_token",
    "product_review",
    "product",
    "return_request",
    "rider_application",
    "seller_application",
    "subcategory",
    "category",
    "user"
    RESTART IDENTITY CASCADE;

-- Re-enable foreign key checks
SET session_replication_role = 'origin';

-- Reset sequences
ALTER SEQUENCE IF EXISTS "user_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "category_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "subcategory_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "product_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "order_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "order_item_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "cart_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "notification_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "address_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "admin_profile_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "admin_security_log_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "hero_slide_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "return_request_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "rider_application_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "seller_application_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "delivery_personnel_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "product_review_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "chat_message_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "chat_participant_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "conversation_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "notification_preferences_id_seq" RESTART WITH 1;
ALTER SEQUENCE IF EXISTS "password_reset_token_id_seq" RESTART WITH 1;

-- Insert fresh admin user
INSERT INTO "user" ("id", "role", "first_name", "last_name", "email", "password", "phone", "address", "role_actual", "status", "email_verified", "verification_code", "valid_id", "created_at", "two_factor_enabled", "email_notifications")
VALUES (1, 'user', 'Admin', 'Account', 'admin@kidscommerce.com', 'admin123', '0000000000', 'Admin Office', 'admin', 'active', TRUE, NULL, NULL, NOW(), FALSE, TRUE);

INSERT INTO "admin_profile" ("id", "user_id", "full_name", "contact_number", "system_role", "last_login", "account_status", "two_factor_enabled", "password_reset_required", "created_at", "updated_at")
VALUES (1, 1, 'Admin Account', '0000000000', 'Administrator', NOW(), 'Active', FALSE, FALSE, NOW(), NOW());

-- Insert default categories
INSERT INTO "category" ("name", "status", "created_at") VALUES
('Baby Clothes & Accessories', 'active', NOW()),
('Toys & Games', 'active', NOW()),
('Strollers & Gear', 'active', NOW()),
('Nursery Furniture', 'active', NOW()),
('Safety and Health', 'active', NOW()),
('Educational Materials', 'active', NOW()),
('Test Category', 'active', NOW());

-- ============================================
-- DATA CLEARED SUCCESSFULLY
-- Admin login: admin@kidscommerce.com / admin123
-- ============================================
