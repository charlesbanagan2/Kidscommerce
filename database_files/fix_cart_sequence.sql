-- Fix Cart Table Sequence Issue
-- Run this in Supabase SQL Editor

-- Step 1: Find the highest ID in cart table
SELECT MAX(id) FROM cart;

-- Step 2: Reset the sequence to the correct value
-- Replace the number with MAX(id) + 1 from Step 1
-- If MAX(id) is NULL (empty table), use 1

SELECT setval('cart_id_seq', COALESCE((SELECT MAX(id) FROM cart), 0) + 1, false);

-- Step 3: Verify the fix
SELECT nextval('cart_id_seq');

-- This should show the next available ID that won't conflict
