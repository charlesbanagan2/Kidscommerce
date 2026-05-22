-- ============================================
-- UPDATE ALL IMAGE URLS TO SUPABASE STORAGE
-- ============================================
-- Run this in Supabase SQL Editor to fix image URLs
-- This assumes images are already uploaded to Supabase Storage bucket 'product-images'

-- STEP 1: Check current image URLs
SELECT 'BEFORE UPDATE - Product Images' as status;
SELECT id, name, image_filename 
FROM product 
WHERE image_filename IS NOT NULL 
  AND image_filename != ''
LIMIT 5;

SELECT 'BEFORE UPDATE - Store Logos' as status;
SELECT id, store_name, store_logo 
FROM seller_application 
WHERE store_logo IS NOT NULL 
  AND store_logo != ''
  AND status = 'approved'
LIMIT 5;

-- STEP 2: Update product images to Supabase Storage URLs
-- Only update if not already a full URL
UPDATE product
SET image_filename = 'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/' || 
                     REPLACE(REPLACE(image_filename, '/static/uploads/', ''), 'static/uploads/', '')
WHERE image_filename IS NOT NULL
  AND image_filename != ''
  AND image_filename NOT LIKE 'http%';

-- STEP 3: Update product gallery images (JSON array)
-- This is more complex - you may need to do this manually or via backend script

-- STEP 4: Update store logos to Supabase Storage URLs
UPDATE seller_application
SET store_logo = 'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/' || 
                 REPLACE(REPLACE(REPLACE(store_logo, '/static/uploads/documents/', ''), '/static/uploads/', ''), 'static/uploads/', '')
WHERE store_logo IS NOT NULL
  AND store_logo != ''
  AND store_logo NOT LIKE 'http%';

-- STEP 5: Update store background images
UPDATE seller_application
SET store_background = 'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/' || 
                       REPLACE(REPLACE(REPLACE(store_background, '/static/uploads/documents/', ''), '/static/uploads/', ''), 'static/uploads/', '')
WHERE store_background IS NOT NULL
  AND store_background != ''
  AND store_background NOT LIKE 'http%';

-- STEP 6: Verify changes
SELECT 'AFTER UPDATE - Product Images' as status;
SELECT id, name, image_filename 
FROM product 
WHERE image_filename IS NOT NULL 
  AND image_filename != ''
LIMIT 5;

SELECT 'AFTER UPDATE - Store Logos' as status;
SELECT id, store_name, store_logo 
FROM seller_application 
WHERE store_logo IS NOT NULL 
  AND store_logo != ''
  AND status = 'approved'
LIMIT 5;

-- STEP 7: Count updated records
SELECT 
    'Product Images Updated' as type,
    COUNT(*) as count
FROM product
WHERE image_filename LIKE 'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/%'

UNION ALL

SELECT 
    'Store Logos Updated' as type,
    COUNT(*) as count
FROM seller_application
WHERE store_logo LIKE 'https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/%';
