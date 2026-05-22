-- Quick test: Add delivery proof to the most recent order
-- Run this in your database

-- First, check recent orders
SELECT id, status, proof_photo_url, buyer_id 
FROM "order" 
ORDER BY created_at DESC 
LIMIT 5;

-- Add a test delivery proof to order #1 (change the ID as needed)
-- Using a placeholder image path
UPDATE "order" 
SET proof_photo_url = 'delivery_proofs/test_proof.jpg',
    status = 'completed'
WHERE id = 1;

-- Verify the update
SELECT id, status, proof_photo_url 
FROM "order" 
WHERE id = 1;
