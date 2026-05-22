-- ============================================================================
-- 🔄 REVERT URLs TO FILENAMES ONLY
-- ============================================================================
-- This removes the full Supabase Storage URL and keeps only the filename
-- The backend will handle serving images from Supabase Storage
-- ============================================================================

BEGIN;

-- ============================================================================
-- 📦 PRODUCT TABLE
-- ============================================================================

-- Extract filename from Supabase Storage URL
UPDATE product 
SET image_filename = SUBSTRING(image_filename FROM '[^/]+$')
WHERE image_filename LIKE '%supabase.co/storage%';

UPDATE product 
SET video_filename = SUBSTRING(video_filename FROM '[^/]+$')
WHERE video_filename LIKE '%supabase.co/storage%';

-- Update gallery JSON array
UPDATE product
SET gallery = (
    SELECT jsonb_agg(
        to_jsonb(
            SUBSTRING(trim(both '"' from value::text) FROM '[^/]+$')
        )
    )
    FROM jsonb_array_elements(gallery)
)
WHERE gallery IS NOT NULL 
  AND gallery::text LIKE '%supabase.co/storage%';

-- ============================================================================
-- 👤 USER TABLE
-- ============================================================================

UPDATE "user" 
SET profile_picture = SUBSTRING(profile_picture FROM '[^/]+$')
WHERE profile_picture LIKE '%supabase.co/storage%';

UPDATE "user" 
SET valid_id = SUBSTRING(valid_id FROM '[^/]+$')
WHERE valid_id LIKE '%supabase.co/storage%';

-- ============================================================================
-- 📋 ORDER TABLE
-- ============================================================================

UPDATE "order" 
SET proof_photo_url = SUBSTRING(proof_photo_url FROM '[^/]+$')
WHERE proof_photo_url LIKE '%supabase.co/storage%';

UPDATE "order" 
SET qr_code = SUBSTRING(qr_code FROM '[^/]+$')
WHERE qr_code LIKE '%supabase.co/storage%';

-- ============================================================================
-- ⭐ REVIEW TABLE
-- ============================================================================

UPDATE review 
SET image_filename = SUBSTRING(image_filename FROM '[^/]+$')
WHERE image_filename LIKE '%supabase.co/storage%';

UPDATE review 
SET media = (
    SELECT jsonb_agg(
        to_jsonb(
            SUBSTRING(trim(both '"' from value::text) FROM '[^/]+$')
        )
    )
    FROM jsonb_array_elements(media)
)
WHERE media IS NOT NULL 
  AND media::text LIKE '%supabase.co/storage%';

-- ============================================================================
-- 🔄 RETURN_REQUEST TABLE
-- ============================================================================

UPDATE return_request 
SET images = (
    SELECT jsonb_agg(
        to_jsonb(
            SUBSTRING(trim(both '"' from value::text) FROM '[^/]+$')
        )
    )
    FROM jsonb_array_elements(images)
)
WHERE images IS NOT NULL 
  AND images::text LIKE '%supabase.co/storage%';

UPDATE return_request 
SET video_filename = SUBSTRING(video_filename FROM '[^/]+$')
WHERE video_filename LIKE '%supabase.co/storage%';

-- ============================================================================
-- 🏪 SELLER_APPLICATION TABLE
-- ============================================================================

UPDATE seller_application 
SET school_id_document = SUBSTRING(school_id_document FROM '[^/]+$')
WHERE school_id_document LIKE '%supabase.co/storage%';

UPDATE seller_application 
SET store_logo = SUBSTRING(store_logo FROM '[^/]+$')
WHERE store_logo LIKE '%supabase.co/storage%';

UPDATE seller_application 
SET business_registration = SUBSTRING(business_registration FROM '[^/]+$')
WHERE business_registration LIKE '%supabase.co/storage%';

UPDATE seller_application 
SET valid_id = SUBSTRING(valid_id FROM '[^/]+$')
WHERE valid_id LIKE '%supabase.co/storage%';

UPDATE seller_application 
SET store_banner = SUBSTRING(store_banner FROM '[^/]+$')
WHERE store_banner LIKE '%supabase.co/storage%';

UPDATE seller_application 
SET store_background = SUBSTRING(store_background FROM '[^/]+$')
WHERE store_background LIKE '%supabase.co/storage%';

-- ============================================================================
-- 🚚 DELIVERY_PERSONNEL TABLE
-- ============================================================================

UPDATE delivery_personnel 
SET id_document = SUBSTRING(id_document FROM '[^/]+$')
WHERE id_document LIKE '%supabase.co/storage%';

UPDATE delivery_personnel 
SET photo_path = SUBSTRING(photo_path FROM '[^/]+$')
WHERE photo_path LIKE '%supabase.co/storage%';

-- ============================================================================
-- 🎨 HERO_SLIDE TABLE
-- ============================================================================

UPDATE hero_slide 
SET image_filename = SUBSTRING(image_filename FROM '[^/]+$')
WHERE image_filename LIKE '%supabase.co/storage%';

-- ============================================================================
-- 🔔 NOTIFICATION TABLE
-- ============================================================================

UPDATE notification 
SET image_url = SUBSTRING(image_url FROM '[^/]+$')
WHERE image_url LIKE '%supabase.co/storage%';

UPDATE notification 
SET images = (
    SELECT jsonb_agg(
        to_jsonb(
            SUBSTRING(trim(both '"' from value::text) FROM '[^/]+$')
        )
    )
    FROM jsonb_array_elements(images)
)
WHERE images IS NOT NULL 
  AND images::text LIKE '%supabase.co/storage%';

-- ============================================================================
-- 📁 CATEGORY TABLE
-- ============================================================================

UPDATE category 
SET cover_image_filename = SUBSTRING(cover_image_filename FROM '[^/]+$')
WHERE cover_image_filename LIKE '%supabase.co/storage%';

-- ============================================================================
-- 🎨 THEME_SETTING TABLE
-- ============================================================================

UPDATE theme_setting 
SET logo_filename = SUBSTRING(logo_filename FROM '[^/]+$')
WHERE logo_filename LIKE '%supabase.co/storage%';

-- ============================================================================
-- 📝 REGISTRATION_REQUEST TABLE
-- ============================================================================

UPDATE registration_request 
SET valid_id = SUBSTRING(valid_id FROM '[^/]+$')
WHERE valid_id LIKE '%supabase.co/storage%';

COMMIT;

-- ============================================================================
-- ✅ VERIFICATION
-- ============================================================================

SELECT 
    'Products' as table_name,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE image_filename NOT LIKE '%http%') as filename_only
FROM product
UNION ALL
SELECT 'Hero Slides', COUNT(*), COUNT(*) FILTER (WHERE image_filename NOT LIKE '%http%') FROM hero_slide
UNION ALL
SELECT 'Theme Settings', COUNT(*), COUNT(*) FILTER (WHERE logo_filename NOT LIKE '%http%') FROM theme_setting;

-- ============================================================================
-- 🎉 DONE! Now update app.py to serve from Supabase Storage
-- ============================================================================
