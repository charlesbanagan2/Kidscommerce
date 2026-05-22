-- ============================================================================
-- 🔧 FIX PRODUCT IMAGES - Add Full URL to Product Images
-- ============================================================================
-- This script adds the full domain to product images that only have filenames
-- ============================================================================

BEGIN;

-- ============================================================================
-- 📦 UPDATE PRODUCT IMAGE_FILENAME
-- Add https://kids-kingdom.onrender.com/ to images that don't have it
-- ============================================================================

-- Update image_filename: Add domain if it doesn't start with http
UPDATE product 
SET image_filename = 'https://kids-kingdom.onrender.com/' || image_filename
WHERE image_filename IS NOT NULL 
  AND image_filename != ''
  AND image_filename NOT LIKE 'http%';

-- ============================================================================
-- 🎥 UPDATE PRODUCT VIDEO_FILENAME
-- Add https://kids-kingdom.onrender.com/ to videos that don't have it
-- ============================================================================

UPDATE product 
SET video_filename = 'https://kids-kingdom.onrender.com/' || video_filename
WHERE video_filename IS NOT NULL 
  AND video_filename != ''
  AND video_filename NOT LIKE 'http%';

-- ============================================================================
-- 🖼️ UPDATE PRODUCT GALLERY (JSON array of images)
-- This is more complex - need to update each item in the JSON array
-- ============================================================================

-- For products with gallery images that don't have full URLs
UPDATE product
SET gallery = (
    SELECT jsonb_agg(
        CASE 
            WHEN value::text LIKE '"%http%"' THEN value
            ELSE to_jsonb('https://kids-kingdom.onrender.com/' || trim(both '"' from value::text))
        END
    )
    FROM jsonb_array_elements(gallery)
)
WHERE gallery IS NOT NULL 
  AND gallery::text NOT LIKE '%http%';

COMMIT;

-- ============================================================================
-- ✅ VERIFICATION - Check the results
-- ============================================================================

SELECT 
    id,
    name,
    image_filename,
    video_filename,
    gallery
FROM product
ORDER BY id
LIMIT 10;

-- ============================================================================
-- 📊 COUNT - How many products were updated
-- ============================================================================

SELECT 
    COUNT(*) as total_products,
    COUNT(CASE WHEN image_filename LIKE 'https://kids-kingdom.onrender.com/%' THEN 1 END) as images_with_url,
    COUNT(CASE WHEN video_filename LIKE 'https://kids-kingdom.onrender.com/%' THEN 1 END) as videos_with_url
FROM product;

-- ============================================================================
-- 🎉 DONE!
-- ============================================================================
