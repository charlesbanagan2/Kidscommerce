-- ============================================================================
-- COMPREHENSIVE URL UPDATE SCRIPT
-- Replace all local development URLs with live production domain
-- ============================================================================
-- Old URLs: http://127.0.0.1:5000, http://localhost:5000
-- New URL: https://kids-kingdom.onrender.com
-- ============================================================================

BEGIN;

-- Show current state before updates
SELECT 'BEFORE UPDATE - Checking for old URLs...' as status;

-- ============================================================================
-- 1. PRODUCTS TABLE
-- ============================================================================
SELECT 'Updating products table...' as status;

-- Update main product image_filename
UPDATE product 
SET image_filename = REPLACE(image_filename, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')
WHERE image_filename LIKE '%http://127.0.0.1:5000%';

UPDATE product 
SET image_filename = REPLACE(image_filename, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')
WHERE image_filename LIKE '%http://localhost:5000%';

-- Update product gallery (JSON array)
UPDATE product 
SET gallery = REPLACE(gallery::text, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')::jsonb
WHERE gallery::text LIKE '%http://127.0.0.1:5000%';

UPDATE product 
SET gallery = REPLACE(gallery::text, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')::jsonb
WHERE gallery::text LIKE '%http://localhost:5000%';

-- Update product video_filename
UPDATE product 
SET video_filename = REPLACE(video_filename, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')
WHERE video_filename LIKE '%http://127.0.0.1:5000%';

UPDATE product 
SET video_filename = REPLACE(video_filename, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')
WHERE video_filename LIKE '%http://localhost:5000%';

SELECT COUNT(*) as products_updated FROM product 
WHERE image_filename LIKE '%kids-kingdom.onrender.com%' 
   OR gallery::text LIKE '%kids-kingdom.onrender.com%'
   OR video_filename LIKE '%kids-kingdom.onrender.com%';

-- ============================================================================
-- 2. USER TABLE
-- ============================================================================
SELECT 'Updating user table...' as status;

-- Update profile pictures
UPDATE "user" 
SET profile_picture = REPLACE(profile_picture, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')
WHERE profile_picture LIKE '%http://127.0.0.1:5000%';

UPDATE "user" 
SET profile_picture = REPLACE(profile_picture, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')
WHERE profile_picture LIKE '%http://localhost:5000%';

-- Update store logos
UPDATE "user" 
SET store_logo = REPLACE(store_logo, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')
WHERE store_logo LIKE '%http://127.0.0.1:5000%';

UPDATE "user" 
SET store_logo = REPLACE(store_logo, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')
WHERE store_logo LIKE '%http://localhost:5000%';

-- Update store backgrounds
UPDATE "user" 
SET store_background = REPLACE(store_background, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')
WHERE store_background LIKE '%http://127.0.0.1:5000%';

UPDATE "user" 
SET store_background = REPLACE(store_background, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')
WHERE store_background LIKE '%http://localhost:5000%';

SELECT COUNT(*) as users_updated FROM "user" 
WHERE profile_picture LIKE '%kids-kingdom.onrender.com%' 
   OR store_logo LIKE '%kids-kingdom.onrender.com%'
   OR store_background LIKE '%kids-kingdom.onrender.com%';

-- ============================================================================
-- 3. ORDERS TABLE
-- ============================================================================
SELECT 'Updating orders table...' as status;

-- Update proof photos
UPDATE "order" 
SET proof_photo_url = REPLACE(proof_photo_url, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')
WHERE proof_photo_url LIKE '%http://127.0.0.1:5000%';

UPDATE "order" 
SET proof_photo_url = REPLACE(proof_photo_url, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')
WHERE proof_photo_url LIKE '%http://localhost:5000%';

SELECT COUNT(*) as orders_updated FROM "order" 
WHERE proof_photo_url LIKE '%kids-kingdom.onrender.com%';

-- ============================================================================
-- 4. REVIEWS TABLE
-- ============================================================================
SELECT 'Updating reviews table...' as status;

-- Update review media (JSON array)
UPDATE review 
SET media = REPLACE(media::text, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')::jsonb
WHERE media::text LIKE '%http://127.0.0.1:5000%';

UPDATE review 
SET media = REPLACE(media::text, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')::jsonb
WHERE media::text LIKE '%http://localhost:5000%';

SELECT COUNT(*) as reviews_updated FROM review 
WHERE media::text LIKE '%kids-kingdom.onrender.com%';

-- ============================================================================
-- 5. SITE_SETTINGS TABLE (if exists)
-- ============================================================================
SELECT 'Updating site_settings table...' as status;

DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'site_settings') THEN
        -- Update logo
        UPDATE site_settings 
        SET logo = REPLACE(logo, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')
        WHERE logo LIKE '%http://127.0.0.1:5000%';

        UPDATE site_settings 
        SET logo = REPLACE(logo, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')
        WHERE logo LIKE '%http://localhost:5000%';

        -- Update favicon
        UPDATE site_settings 
        SET favicon = REPLACE(favicon, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')
        WHERE favicon LIKE '%http://127.0.0.1:5000%';

        UPDATE site_settings 
        SET favicon = REPLACE(favicon, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')
        WHERE favicon LIKE '%http://localhost:5000%';

        RAISE NOTICE 'Site settings updated';
    END IF;
END $$;

-- ============================================================================
-- 6. BANNERS TABLE (if exists)
-- ============================================================================
SELECT 'Updating banners table...' as status;

DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'banner') THEN
        UPDATE banner 
        SET image_url = REPLACE(image_url, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')
        WHERE image_url LIKE '%http://127.0.0.1:5000%';

        UPDATE banner 
        SET image_url = REPLACE(image_url, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')
        WHERE image_url LIKE '%http://localhost:5000%';

        RAISE NOTICE 'Banners updated';
    END IF;
END $$;

-- ============================================================================
-- 7. CATEGORIES TABLE (if exists)
-- ============================================================================
SELECT 'Updating categories table...' as status;

DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'category') THEN
        UPDATE category 
        SET image = REPLACE(image, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')
        WHERE image LIKE '%http://127.0.0.1:5000%';

        UPDATE category 
        SET image = REPLACE(image, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')
        WHERE image LIKE '%http://localhost:5000%';

        RAISE NOTICE 'Categories updated';
    END IF;
END $$;

-- ============================================================================
-- 8. NOTIFICATIONS TABLE (if exists)
-- ============================================================================
SELECT 'Updating notifications table...' as status;

DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'notification') THEN
        UPDATE notification 
        SET data = REPLACE(data::text, 'http://127.0.0.1:5000', 'https://kids-kingdom.onrender.com')::jsonb
        WHERE data::text LIKE '%http://127.0.0.1:5000%';

        UPDATE notification 
        SET data = REPLACE(data::text, 'http://localhost:5000', 'https://kids-kingdom.onrender.com')::jsonb
        WHERE data::text LIKE '%http://localhost:5000%';

        RAISE NOTICE 'Notifications updated';
    END IF;
END $$;

-- ============================================================================
-- FINAL VERIFICATION
-- ============================================================================
SELECT 'AFTER UPDATE - Verification...' as status;

-- Check for any remaining old URLs
SELECT 'Checking for remaining old URLs...' as status;

-- Products
SELECT 'Products with old URLs:' as check_type, COUNT(*) as count
FROM product 
WHERE image_filename LIKE '%http://127.0.0.1:5000%' 
   OR image_filename LIKE '%http://localhost:5000%'
   OR gallery::text LIKE '%http://127.0.0.1:5000%'
   OR gallery::text LIKE '%http://localhost:5000%'
   OR video_filename LIKE '%http://127.0.0.1:5000%'
   OR video_filename LIKE '%http://localhost:5000%';

-- Users
SELECT 'Users with old URLs:' as check_type, COUNT(*) as count
FROM "user" 
WHERE profile_picture LIKE '%http://127.0.0.1:5000%' 
   OR profile_picture LIKE '%http://localhost:5000%'
   OR store_logo LIKE '%http://127.0.0.1:5000%'
   OR store_logo LIKE '%http://localhost:5000%'
   OR store_background LIKE '%http://127.0.0.1:5000%'
   OR store_background LIKE '%http://localhost:5000%';

-- Orders
SELECT 'Orders with old URLs:' as check_type, COUNT(*) as count
FROM "order" 
WHERE proof_photo_url LIKE '%http://127.0.0.1:5000%' 
   OR proof_photo_url LIKE '%http://localhost:5000%';

-- Reviews
SELECT 'Reviews with old URLs:' as check_type, COUNT(*) as count
FROM review 
WHERE media::text LIKE '%http://127.0.0.1:5000%'
   OR media::text LIKE '%http://localhost:5000%';

-- Summary of updates
SELECT 'UPDATE SUMMARY' as status;
SELECT 
    'Products' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE image_filename LIKE '%kids-kingdom.onrender.com%' 
                      OR gallery::text LIKE '%kids-kingdom.onrender.com%'
                      OR video_filename LIKE '%kids-kingdom.onrender.com%') as records_with_new_url
FROM product
UNION ALL
SELECT 
    'Users' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE profile_picture LIKE '%kids-kingdom.onrender.com%' 
                      OR store_logo LIKE '%kids-kingdom.onrender.com%'
                      OR store_background LIKE '%kids-kingdom.onrender.com%') as records_with_new_url
FROM "user"
UNION ALL
SELECT 
    'Orders' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE proof_photo_url LIKE '%kids-kingdom.onrender.com%') as records_with_new_url
FROM "order"
UNION ALL
SELECT 
    'Reviews' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE media::text LIKE '%kids-kingdom.onrender.com%') as records_with_new_url
FROM review;

-- If everything looks good, commit the transaction
COMMIT;

SELECT '✅ URL UPDATE COMPLETE!' as status;
SELECT 'All local URLs have been replaced with: https://kids-kingdom.onrender.com' as message;
