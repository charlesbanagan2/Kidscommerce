-- ============================================
-- CHECK STORE LOGOS IN DATABASE
-- ============================================
-- Run this in Supabase SQL Editor to see current store_logo values

SELECT 
    id,
    user_id,
    store_name,
    store_logo,
    status
FROM seller_application
WHERE status = 'approved'
ORDER BY id;
