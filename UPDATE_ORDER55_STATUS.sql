-- Update Order #55 status from 'processing' to 'to_ship'
-- This ensures the order appears in the correct tab when rider is assigned

UPDATE "order" 
SET status = 'to_ship', updated_at = NOW()
WHERE id = 55;

-- Verify the update
SELECT id, status, rider_id, created_at, updated_at 
FROM "order" 
WHERE id = 55;
