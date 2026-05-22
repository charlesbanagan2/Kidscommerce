-- ============================================================================
-- STEP 2: UPDATE ALL URLs TO SUPABASE STORAGE
-- ============================================================================
-- Run this AFTER running STEP1_EXTEND_COLUMNS.sql
-- This script updates all image URLs to point to Supabase Storage
-- Old: https://kids-kingdom.onrender.com/[filename]
-- New: https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/[filename]
-- ============================================================================

BEGIN;

-- ============================================================================
-- 📦 PRODUCT TABLE
-- ============================================================================

-- Update image_filename
UPDATE product 
SET image_filename = REPLACE(
    image_filename, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE image_filename LIKE 'https://kids-kingdom.onrender.com/%';

-- Update video_filename
UPDATE product 
SET video_filename = REPLACE(
    video_filename, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE video_filename LIKE 'https://kids-kingdom.onrender.com/%';

-- Update gallery (JSON array)
UPDATE product
SET gallery = (
    SELECT jsonb_agg(
        to_jsonb(
            REPLACE(
                trim(both '"' from value::text),
                'https://kids-kingdom.onrender.com/',
                'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
            )
        )
    )
    FROM jsonb_array_elements(gallery)
)
WHERE gallery IS NOT NULL 
  AND gallery::text LIKE '%kids-kingdom.onrender.com%';

-- ============================================================================
-- 👤 USER TABLE
-- ============================================================================

UPDATE "user" 
SET profile_picture = REPLACE(
    profile_picture, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE profile_picture LIKE 'https://kids-kingdom.onrender.com/%';

UPDATE "user" 
SET valid_id = REPLACE(
    valid_id, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE valid_id LIKE 'https://kids-kingdom.onrender.com/%';

-- ============================================================================
-- 📋 ORDER TABLE
-- ============================================================================

UPDATE "order" 
SET proof_photo_url = REPLACE(
    proof_photo_url, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE proof_photo_url LIKE 'https://kids-kingdom.onrender.com/%';

UPDATE "order" 
SET qr_code = REPLACE(
    qr_code, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE qr_code LIKE 'https://kids-kingdom.onrender.com/%';

-- ============================================================================
-- ⭐ REVIEW TABLE
-- ============================================================================

UPDATE review 
SET image_filename = REPLACE(
    image_filename, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE image_filename LIKE 'https://kids-kingdom.onrender.com/%';

UPDATE review 
SET media = (
    SELECT jsonb_agg(
        to_jsonb(
            REPLACE(
                trim(both '"' from value::text),
                'https://kids-kingdom.onrender.com/',
                'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
            )
        )
    )
    FROM jsonb_array_elements(media)
)
WHERE media IS NOT NULL 
  AND media::text LIKE '%kids-kingdom.onrender.com%';

-- ============================================================================
-- 🔄 RETURN_REQUEST TABLE
-- ============================================================================

UPDATE return_request 
SET images = (
    SELECT jsonb_agg(
        to_jsonb(
            REPLACE(
                trim(both '"' from value::text),
                'https://kids-kingdom.onrender.com/',
                'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
            )
        )
    )
    FROM jsonb_array_elements(images)
)
WHERE images IS NOT NULL 
  AND images::text LIKE '%kids-kingdom.onrender.com%';

UPDATE return_request 
SET video_filename = REPLACE(
    video_filename, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE video_filename LIKE 'https://kids-kingdom.onrender.com/%';

-- ============================================================================
-- 🏪 SELLER_APPLICATION TABLE
-- ============================================================================

UPDATE seller_application 
SET school_id_document = REPLACE(
    school_id_document, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE school_id_document LIKE 'https://kids-kingdom.onrender.com/%';

UPDATE seller_application 
SET store_logo = REPLACE(
    store_logo, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE store_logo LIKE 'https://kids-kingdom.onrender.com/%';

UPDATE seller_application 
SET business_registration = REPLACE(
    business_registration, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE business_registration LIKE 'https://kids-kingdom.onrender.com/%';

UPDATE seller_application 
SET valid_id = REPLACE(
    valid_id, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE valid_id LIKE 'https://kids-kingdom.onrender.com/%';

UPDATE seller_application 
SET store_banner = REPLACE(
    store_banner, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE store_banner LIKE 'https://kids-kingdom.onrender.com/%';

UPDATE seller_application 
SET store_background = REPLACE(
    store_background, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE store_background LIKE 'https://kids-kingdom.onrender.com/%';

-- ============================================================================
-- 🚚 DELIVERY_PERSONNEL TABLE
-- ============================================================================

UPDATE delivery_personnel 
SET id_document = REPLACE(
    id_document, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE id_document LIKE 'https://kids-kingdom.onrender.com/%';

UPDATE delivery_personnel 
SET photo_path = REPLACE(
    photo_path, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE photo_path LIKE 'https://kids-kingdom.onrender.com/%';

-- ============================================================================
-- 🎨 HERO_SLIDE TABLE
-- ============================================================================

UPDATE hero_slide 
SET image_filename = REPLACE(
    image_filename, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE image_filename LIKE 'https://kids-kingdom.onrender.com/%';

-- ============================================================================
-- 🔔 NOTIFICATION TABLE
-- ============================================================================

UPDATE notification 
SET image_url = REPLACE(
    image_url, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE image_url LIKE 'https://kids-kingdom.onrender.com/%';

UPDATE notification 
SET images = (
    SELECT jsonb_agg(
        to_jsonb(
            REPLACE(
                trim(both '"' from value::text),
                'https://kids-kingdom.onrender.com/',
                'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
            )
        )
    )
    FROM jsonb_array_elements(images)
)
WHERE images IS NOT NULL 
  AND images::text LIKE '%kids-kingdom.onrender.com%';

-- ============================================================================
-- 📁 CATEGORY TABLE
-- ============================================================================

UPDATE category 
SET cover_image_filename = REPLACE(
    cover_image_filename, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE cover_image_filename LIKE 'https://kids-kingdom.onrender.com/%';

-- ============================================================================
-- 🎨 THEME_SETTING TABLE
-- ============================================================================

UPDATE theme_setting 
SET logo_filename = REPLACE(
    logo_filename, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE logo_filename LIKE 'https://kids-kingdom.onrender.com/%';

-- ============================================================================
-- 📝 REGISTRATION_REQUEST TABLE
-- ============================================================================

UPDATE registration_request 
SET valid_id = REPLACE(
    valid_id, 
    'https://kids-kingdom.onrender.com/', 
    'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/'
)
WHERE valid_id LIKE 'https://kids-kingdom.onrender.com/%';

COMMIT;

-- ============================================================================
-- ✅ VERIFICATION
-- ============================================================================

SELECT 
    'Products' as table_name,
    COUNT(*) FILTER (WHERE image_filename LIKE '%supabase.co/storage%') as with_supabase_url
FROM product
UNION ALL
SELECT 'Hero Slides', COUNT(*) FILTER (WHERE image_filename LIKE '%supabase.co/storage%') FROM hero_slide
UNION ALL
SELECT 'Theme Settings', COUNT(*) FILTER (WHERE logo_filename LIKE '%supabase.co/storage%') FROM theme_setting
UNION ALL
SELECT 'Users', COUNT(*) FILTER (WHERE profile_picture LIKE '%supabase.co/storage%') FROM "user"
UNION ALL
SELECT 'Reviews', COUNT(*) FILTER (WHERE image_filename LIKE '%supabase.co/storage%') FROM review;

-- ============================================================================
-- 🎉 DONE! All URLs now point to Supabase Storage
-- ============================================================================
