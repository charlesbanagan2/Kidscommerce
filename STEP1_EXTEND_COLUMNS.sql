-- ============================================================================
-- STEP 1: EXTEND COLUMN SIZES FOR SUPABASE STORAGE URLs
-- ============================================================================
-- Supabase Storage URLs are longer than the current VARCHAR(120) limit
-- This script extends all image/video columns to VARCHAR(500)
-- ============================================================================

BEGIN;

-- ============================================================================
-- 📦 PRODUCT TABLE
-- ============================================================================
ALTER TABLE product 
ALTER COLUMN image_filename TYPE VARCHAR(500);

ALTER TABLE product 
ALTER COLUMN video_filename TYPE VARCHAR(500);

-- ============================================================================
-- 👤 USER TABLE
-- ============================================================================
ALTER TABLE "user" 
ALTER COLUMN profile_picture TYPE VARCHAR(500);

ALTER TABLE "user" 
ALTER COLUMN valid_id TYPE VARCHAR(500);

-- ============================================================================
-- 📋 ORDER TABLE
-- ============================================================================
ALTER TABLE "order" 
ALTER COLUMN proof_photo_url TYPE VARCHAR(500);

ALTER TABLE "order" 
ALTER COLUMN qr_code TYPE VARCHAR(500);

-- ============================================================================
-- ⭐ REVIEW TABLE
-- ============================================================================
ALTER TABLE review 
ALTER COLUMN image_filename TYPE VARCHAR(500);

-- ============================================================================
-- 🔄 RETURN_REQUEST TABLE
-- ============================================================================
ALTER TABLE return_request 
ALTER COLUMN video_filename TYPE VARCHAR(500);

-- ============================================================================
-- 🏪 SELLER_APPLICATION TABLE
-- ============================================================================
ALTER TABLE seller_application 
ALTER COLUMN school_id_document TYPE VARCHAR(500);

ALTER TABLE seller_application 
ALTER COLUMN store_logo TYPE VARCHAR(500);

ALTER TABLE seller_application 
ALTER COLUMN business_registration TYPE VARCHAR(500);

ALTER TABLE seller_application 
ALTER COLUMN valid_id TYPE VARCHAR(500);

ALTER TABLE seller_application 
ALTER COLUMN store_banner TYPE VARCHAR(500);

ALTER TABLE seller_application 
ALTER COLUMN store_background TYPE VARCHAR(500);

-- ============================================================================
-- 🚚 DELIVERY_PERSONNEL TABLE
-- ============================================================================
ALTER TABLE delivery_personnel 
ALTER COLUMN id_document TYPE VARCHAR(500);

ALTER TABLE delivery_personnel 
ALTER COLUMN photo_path TYPE VARCHAR(500);

-- ============================================================================
-- 🎨 HERO_SLIDE TABLE
-- ============================================================================
ALTER TABLE hero_slide 
ALTER COLUMN image_filename TYPE VARCHAR(500);

-- ============================================================================
-- 🔔 NOTIFICATION TABLE
-- ============================================================================
ALTER TABLE notification 
ALTER COLUMN image_url TYPE VARCHAR(500);

-- ============================================================================
-- 📁 CATEGORY TABLE
-- ============================================================================
ALTER TABLE category 
ALTER COLUMN cover_image_filename TYPE VARCHAR(500);

-- ============================================================================
-- 🎨 THEME_SETTING TABLE
-- ============================================================================
ALTER TABLE theme_setting 
ALTER COLUMN logo_filename TYPE VARCHAR(500);

-- ============================================================================
-- 📝 REGISTRATION_REQUEST TABLE
-- ============================================================================
ALTER TABLE registration_request 
ALTER COLUMN valid_id TYPE VARCHAR(500);

COMMIT;

-- ============================================================================
-- ✅ VERIFICATION
-- ============================================================================
SELECT 
    table_name,
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN ('product', 'user', 'order', 'review', 'hero_slide', 'theme_setting')
  AND (column_name LIKE '%image%' OR column_name LIKE '%photo%' OR column_name LIKE '%video%' OR column_name LIKE '%logo%')
ORDER BY table_name, column_name;

-- ============================================================================
-- 🎉 DONE! Now run STEP2_UPDATE_URLS_TO_SUPABASE_STORAGE.sql
-- ============================================================================
