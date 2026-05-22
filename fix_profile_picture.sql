-- ============================================
-- REMOVE profile_image COLUMN AND FIX PROFILE PICTURE SETUP
-- Run this in Supabase SQL Editor
-- ============================================

-- Remove the profile_image column from user table
ALTER TABLE "user" 
DROP COLUMN IF EXISTS profile_image;

-- Ensure profile_picture column exists with correct type
ALTER TABLE "user" 
ADD COLUMN IF NOT EXISTS profile_picture TEXT;

-- Verify the changes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'user' 
AND column_name IN ('profile_image', 'profile_picture');

-- ============================================
-- DONE! profile_image removed, profile_picture ready
-- ============================================
