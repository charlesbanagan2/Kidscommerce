-- ============================================================================
-- 🔄 URL UPDATE SCRIPT - RUN IN SUPABASE SQL EDITOR
-- ============================================================================
-- Instructions:
-- 1. Go to Supabase Dashboard → SQL Editor
-- 2. Copy and paste this ENTIRE script
-- 3. Click "Run" button
-- 4. Wait for completion message
-- ============================================================================

-- Start transaction
BEGIN;

-- ============================================================================
-- 📦 PRODUCTS TABLE
-- ============================================================================
UPDATE product 
SET image_filename = REPLACE(image_filename, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE image_filename LIKE '%http://127.0.0.1:5000%';

UPDATE product 
SET image_filename = REPLACE(image_filename, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE image_filename LIKE '%http://localhost:5000%';

UPDATE product 
SET video_filename = REPLACE(video_filename, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE video_filename LIKE '%http://127.0.0.1:5000%';

UPDATE product 
SET video_filename = REPLACE(video_filename, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE video_filename LIKE '%http://localhost:5000%';

UPDATE product 
SET gallery = REPLACE(gallery::text, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')::jsonb 
WHERE gallery::text LIKE '%http://127.0.0.1:5000%';

UPDATE product 
SET gallery = REPLACE(gallery::text, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')::jsonb 
WHERE gallery::text LIKE '%http://localhost:5000%';

-- ============================================================================
-- 👤 USER TABLE
-- ============================================================================
UPDATE "user" 
SET profile_picture = REPLACE(profile_picture, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE profile_picture LIKE '%http://127.0.0.1:5000%';

UPDATE "user" 
SET profile_picture = REPLACE(profile_picture, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE profile_picture LIKE '%http://localhost:5000%';

UPDATE "user" 
SET valid_id = REPLACE(valid_id, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE valid_id LIKE '%http://127.0.0.1:5000%';

UPDATE "user" 
SET valid_id = REPLACE(valid_id, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE valid_id LIKE '%http://localhost:5000%';

-- ============================================================================
-- 📋 ORDER TABLE
-- ============================================================================
UPDATE "order" 
SET proof_photo_url = REPLACE(proof_photo_url, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE proof_photo_url LIKE '%http://127.0.0.1:5000%';

UPDATE "order" 
SET proof_photo_url = REPLACE(proof_photo_url, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE proof_photo_url LIKE '%http://localhost:5000%';

UPDATE "order" 
SET qr_code = REPLACE(qr_code, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE qr_code LIKE '%http://127.0.0.1:5000%';

UPDATE "order" 
SET qr_code = REPLACE(qr_code, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE qr_code LIKE '%http://localhost:5000%';

-- ============================================================================
-- ⭐ REVIEW TABLE (Buyer uploads)
-- ============================================================================
UPDATE review 
SET image_filename = REPLACE(image_filename, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE image_filename LIKE '%http://127.0.0.1:5000%';

UPDATE review 
SET image_filename = REPLACE(image_filename, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE image_filename LIKE '%http://localhost:5000%';

UPDATE review 
SET media = REPLACE(media::text, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')::jsonb 
WHERE media::text LIKE '%http://127.0.0.1:5000%';

UPDATE review 
SET media = REPLACE(media::text, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')::jsonb 
WHERE media::text LIKE '%http://localhost:5000%';

-- ============================================================================
-- 🔄 RETURN_REQUEST TABLE (Buyer uploads)
-- ============================================================================
UPDATE return_request 
SET images = REPLACE(images::text, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')::jsonb 
WHERE images::text LIKE '%http://127.0.0.1:5000%';

UPDATE return_request 
SET images = REPLACE(images::text, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')::jsonb 
WHERE images::text LIKE '%http://localhost:5000%';

UPDATE return_request 
SET video_filename = REPLACE(video_filename, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE video_filename LIKE '%http://127.0.0.1:5000%';

UPDATE return_request 
SET video_filename = REPLACE(video_filename, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE video_filename LIKE '%http://localhost:5000%';

-- ============================================================================
-- 🏪 SELLER_APPLICATION TABLE
-- ============================================================================
UPDATE seller_application 
SET school_id_document = REPLACE(school_id_document, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE school_id_document LIKE '%http://127.0.0.1:5000%';

UPDATE seller_application 
SET school_id_document = REPLACE(school_id_document, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE school_id_document LIKE '%http://localhost:5000%';

UPDATE seller_application 
SET store_logo = REPLACE(store_logo, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE store_logo LIKE '%http://127.0.0.1:5000%';

UPDATE seller_application 
SET store_logo = REPLACE(store_logo, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE store_logo LIKE '%http://localhost:5000%';

UPDATE seller_application 
SET business_registration = REPLACE(business_registration, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE business_registration LIKE '%http://127.0.0.1:5000%';

UPDATE seller_application 
SET business_registration = REPLACE(business_registration, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE business_registration LIKE '%http://localhost:5000%';

UPDATE seller_application 
SET valid_id = REPLACE(valid_id, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE valid_id LIKE '%http://127.0.0.1:5000%';

UPDATE seller_application 
SET valid_id = REPLACE(valid_id, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE valid_id LIKE '%http://localhost:5000%';

UPDATE seller_application 
SET store_banner = REPLACE(store_banner, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE store_banner LIKE '%http://127.0.0.1:5000%';

UPDATE seller_application 
SET store_banner = REPLACE(store_banner, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE store_banner LIKE '%http://localhost:5000%';

UPDATE seller_application 
SET store_background = REPLACE(store_background, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE store_background LIKE '%http://127.0.0.1:5000%';

UPDATE seller_application 
SET store_background = REPLACE(store_background, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE store_background LIKE '%http://localhost:5000%';

-- ============================================================================
-- 🚚 DELIVERY_PERSONNEL TABLE
-- ============================================================================
UPDATE delivery_personnel 
SET id_document = REPLACE(id_document, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE id_document LIKE '%http://127.0.0.1:5000%';

UPDATE delivery_personnel 
SET id_document = REPLACE(id_document, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE id_document LIKE '%http://localhost:5000%';

UPDATE delivery_personnel 
SET photo_path = REPLACE(photo_path, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE photo_path LIKE '%http://127.0.0.1:5000%';

UPDATE delivery_personnel 
SET photo_path = REPLACE(photo_path, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE photo_path LIKE '%http://localhost:5000%';

-- ============================================================================
-- 🎨 HERO_SLIDE TABLE
-- ============================================================================
UPDATE hero_slide 
SET image_filename = REPLACE(image_filename, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE image_filename LIKE '%http://127.0.0.1:5000%';

UPDATE hero_slide 
SET image_filename = REPLACE(image_filename, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE image_filename LIKE '%http://localhost:5000%';

UPDATE hero_slide 
SET link = REPLACE(link, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE link LIKE '%http://127.0.0.1:5000%';

UPDATE hero_slide 
SET link = REPLACE(link, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE link LIKE '%http://localhost:5000%';

-- ============================================================================
-- 🔔 NOTIFICATION TABLE
-- ============================================================================
UPDATE notification 
SET image_url = REPLACE(image_url, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE image_url LIKE '%http://127.0.0.1:5000%';

UPDATE notification 
SET image_url = REPLACE(image_url, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE image_url LIKE '%http://localhost:5000%';

UPDATE notification 
SET link = REPLACE(link, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE link LIKE '%http://127.0.0.1:5000%';

UPDATE notification 
SET link = REPLACE(link, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE link LIKE '%http://localhost:5000%';

UPDATE notification 
SET action_url = REPLACE(action_url, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE action_url LIKE '%http://127.0.0.1:5000%';

UPDATE notification 
SET action_url = REPLACE(action_url, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE action_url LIKE '%http://localhost:5000%';

UPDATE notification 
SET images = REPLACE(images::text, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')::jsonb 
WHERE images::text LIKE '%http://127.0.0.1:5000%';

UPDATE notification 
SET images = REPLACE(images::text, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')::jsonb 
WHERE images::text LIKE '%http://localhost:5000%';

UPDATE notification 
SET metadata = REPLACE(metadata::text, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')::json 
WHERE metadata::text LIKE '%http://127.0.0.1:5000%';

UPDATE notification 
SET metadata = REPLACE(metadata::text, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')::json 
WHERE metadata::text LIKE '%http://localhost:5000%';

-- ============================================================================
-- 📁 CATEGORY TABLE
-- ============================================================================
UPDATE category 
SET cover_image_filename = REPLACE(cover_image_filename, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE cover_image_filename LIKE '%http://127.0.0.1:5000%';

UPDATE category 
SET cover_image_filename = REPLACE(cover_image_filename, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE cover_image_filename LIKE '%http://localhost:5000%';

-- ============================================================================
-- 🎨 THEME_SETTING TABLE
-- ============================================================================
UPDATE theme_setting 
SET logo_filename = REPLACE(logo_filename, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE logo_filename LIKE '%http://127.0.0.1:5000%';

UPDATE theme_setting 
SET logo_filename = REPLACE(logo_filename, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE logo_filename LIKE '%http://localhost:5000%';

-- ============================================================================
-- 📝 REGISTRATION_REQUEST TABLE
-- ============================================================================
UPDATE registration_request 
SET valid_id = REPLACE(valid_id, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com') 
WHERE valid_id LIKE '%http://127.0.0.1:5000%';

UPDATE registration_request 
SET valid_id = REPLACE(valid_id, 'http://localhost:5000', 'https://kids-kingdom.onrender.com') 
WHERE valid_id LIKE '%http://localhost:5000%';

-- Commit all changes
COMMIT;

-- ============================================================================
-- ✅ VERIFICATION - Check results
-- ============================================================================
SELECT 
    'Products' as table_name,
    COUNT(*) FILTER (WHERE 
        image_filename LIKE '%kids-kingdom.onrender.com%' OR 
        gallery::text LIKE '%kids-kingdom.onrender.com%' OR 
        video_filename LIKE '%kids-kingdom.onrender.com%'
    ) as records_with_new_url
FROM product
UNION ALL
SELECT 'Users', COUNT(*) FILTER (WHERE profile_picture LIKE '%kids-kingdom.onrender.com%' OR valid_id LIKE '%kids-kingdom.onrender.com%') FROM "user"
UNION ALL
SELECT 'Orders', COUNT(*) FILTER (WHERE proof_photo_url LIKE '%kids-kingdom.onrender.com%' OR qr_code LIKE '%kids-kingdom.onrender.com%') FROM "order"
UNION ALL
SELECT 'Reviews', COUNT(*) FILTER (WHERE image_filename LIKE '%kids-kingdom.onrender.com%' OR media::text LIKE '%kids-kingdom.onrender.com%') FROM review
UNION ALL
SELECT 'Return Requests', COUNT(*) FILTER (WHERE images::text LIKE '%kids-kingdom.onrender.com%' OR video_filename LIKE '%kids-kingdom.onrender.com%') FROM return_request
UNION ALL
SELECT 'Seller Applications', COUNT(*) FILTER (WHERE school_id_document LIKE '%kids-kingdom.onrender.com%' OR store_logo LIKE '%kids-kingdom.onrender.com%' OR business_registration LIKE '%kids-kingdom.onrender.com%' OR valid_id LIKE '%kids-kingdom.onrender.com%' OR store_banner LIKE '%kids-kingdom.onrender.com%' OR store_background LIKE '%kids-kingdom.onrender.com%') FROM seller_application
UNION ALL
SELECT 'Delivery Personnel', COUNT(*) FILTER (WHERE id_document LIKE '%kids-kingdom.onrender.com%' OR photo_path LIKE '%kids-kingdom.onrender.com%') FROM delivery_personnel
UNION ALL
SELECT 'Hero Slides', COUNT(*) FILTER (WHERE image_filename LIKE '%kids-kingdom.onrender.com%' OR link LIKE '%kids-kingdom.onrender.com%') FROM hero_slide
UNION ALL
SELECT 'Notifications', COUNT(*) FILTER (WHERE image_url LIKE '%kids-kingdom.onrender.com%' OR link LIKE '%kids-kingdom.onrender.com%' OR action_url LIKE '%kids-kingdom.onrender.com%' OR images::text LIKE '%kids-kingdom.onrender.com%' OR metadata::text LIKE '%kids-kingdom.onrender.com%') FROM notification
UNION ALL
SELECT 'Categories', COUNT(*) FILTER (WHERE cover_image_filename LIKE '%kids-kingdom.onrender.com%') FROM category
UNION ALL
SELECT 'Theme Settings', COUNT(*) FILTER (WHERE logo_filename LIKE '%kids-kingdom.onrender.com%') FROM theme_setting
UNION ALL
SELECT 'Registration Requests', COUNT(*) FILTER (WHERE valid_id LIKE '%kids-kingdom.onrender.com%') FROM registration_request;

-- ============================================================================
-- 🎉 DONE!
-- ============================================================================
-- All URLs have been updated to: https://kids-kingdom.onrender.com
-- Check the results table above to see how many records were updated
-- ============================================================================
