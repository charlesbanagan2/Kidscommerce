-- ============================================
-- REVERT PRODUCT IMAGES TO LOCAL FILENAMES
-- ============================================
-- This will remove Supabase Storage URLs and use local filenames only
-- Run this in Supabase SQL Editor

-- STEP 1: Check current URLs
SELECT 'BEFORE REVERT - Product Images' as status;
SELECT id, name, image_filename 
FROM product 
WHERE image_filename LIKE 'https://qkdacoawexaxejljfihh.supabase.co%'
LIMIT 5;

-- STEP 2: Revert product images to local filenames
UPDATE product
SET image_filename = REPLACE(image_filename, 'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/', '')
WHERE image_filename LIKE 'https://qkdacoawexaxejljfihh.supabase.co%';

-- STEP 3: Revert store logos to local paths
UPDATE seller_application
SET store_logo = '/static/uploads/documents/' || REPLACE(store_logo, 'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/', '')
WHERE store_logo LIKE 'https://qkdacoawexaxejljfihh.supabase.co%';

-- STEP 3.5: Revert user profile pictures to local paths
UPDATE "user"
SET profile_picture = REPLACE(profile_picture, 'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/', '')
WHERE profile_picture LIKE 'https://qkdacoawexaxejljfihh.supabase.co%';

-- STEP 4: Verify changes
SELECT 'AFTER REVERT - Product Images' as status;
SELECT id, name, image_filename 
FROM product 
WHERE image_filename IS NOT NULL 
  AND image_filename != ''
LIMIT 5;

SELECT 'AFTER REVERT - Store Logos' as status;
SELECT id, store_name, store_logo 
FROM seller_application 
WHERE store_logo IS NOT NULL 
  AND store_logo != ''
  AND status = 'approved'
LIMIT 5;

SELECT 'AFTER REVERT - User Profile Pictures' as status;
SELECT id, email, profile_picture 
FROM "user" 
WHERE profile_picture IS NOT NULL 
  AND profile_picture != ''
LIMIT 5;

-- STEP 5: Count reverted records
SELECT 
    'Product Images Reverted' as type,
    COUNT(*) as count
FROM product
WHERE image_filename NOT LIKE 'http%'
  AND image_filename IS NOT NULL
  AND image_filename != ''

UNION ALL

SELECT 
    'Store Logos Reverted' as type,
    COUNT(*) as count
FROM seller_application
WHERE store_logo LIKE '/static/uploads/%';
