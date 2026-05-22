-- ============================================
-- ADD PROFILE_PICTURE COLUMN TO USER TABLE
-- Run this in Supabase SQL Editor
-- ============================================

-- Add profile_picture column to user table
ALTER TABLE "user" 
ADD COLUMN IF NOT EXISTS profile_picture TEXT;

-- Verify the column was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'user' 
AND column_name = 'profile_picture';

-- Check current user data
SELECT id, email, role, profile_picture 
FROM "user" 
LIMIT 10;

-- ============================================
-- DONE! Column added successfully
-- ============================================
