-- ============================================
-- CHECK BUYER AND RIDER PROFILE PICTURE SETUP
-- Run this in Supabase SQL Editor
-- ============================================

-- Check if buyer table exists and its profile picture columns
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'buyer' 
AND column_name LIKE '%profile%'
ORDER BY column_name;

-- Check if rider table exists and its profile picture columns
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'rider' 
AND column_name LIKE '%profile%'
ORDER BY column_name;

-- Check user table profile columns for reference
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'user' 
AND column_name LIKE '%profile%'
ORDER BY column_name;

-- If buyer table exists, check sample data
SELECT id, profile_picture, profile_image 
FROM buyer 
LIMIT 5;

-- If rider table exists, check sample data
SELECT id, profile_picture, profile_image 
FROM rider 
LIMIT 5;

-- ============================================
-- Review the results to see which columns exist
-- ============================================
