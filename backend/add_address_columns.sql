-- Add missing columns to address table
-- Run this in your Supabase SQL Editor

-- Add street_address column if it doesn't exist
ALTER TABLE address 
ADD COLUMN IF NOT EXISTS street_address TEXT;

-- Add other potentially missing columns
ALTER TABLE address 
ADD COLUMN IF NOT EXISTS city TEXT,
ADD COLUMN IF NOT EXISTS province TEXT,
ADD COLUMN IF NOT EXISTS region TEXT,
ADD COLUMN IF NOT EXISTS barangay TEXT,
ADD COLUMN IF NOT EXISTS zip_code TEXT;

-- Verify the columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'address'
ORDER BY ordinal_position;
