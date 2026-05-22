-- ============================================
-- FIX PROFILE PICTURE COLUMN FOR BUYER AND RIDER
-- Run this in Supabase SQL Editor
-- ============================================

-- 1. Remove profile_image column from user table
ALTER TABLE "user" 
DROP COLUMN IF EXISTS profile_image;

-- 2. Ensure profile_picture column exists
ALTER TABLE "user" 
ADD COLUMN IF NOT EXISTS profile_picture TEXT;

-- 3. Verify the user table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'user' 
AND column_name LIKE '%profile%'
ORDER BY column_name;

-- 4. Check sample data
SELECT id, email, role, profile_picture 
FROM "user" 
WHERE role IN ('buyer', 'rider')
LIMIT 10;

-- ============================================
-- DONE! Now update your mobile app code to use:
-- - profile_picture (not profile_image)
-- ============================================
