-- Check all product prices and stock in database
SELECT 
    id,
    name,
    price,
    stock,
    status,
    seller_id,
    created_at
FROM product
WHERE status = 'active'
ORDER BY id;

-- Check for any invalid prices or stock
SELECT 
    id,
    name,
    price,
    stock,
    CASE 
        WHEN price <= 0 THEN 'Invalid Price'
        WHEN stock < 0 THEN 'Negative Stock'
        ELSE 'OK'
    END as issue
FROM product
WHERE status = 'active' AND (price <= 0 OR stock < 0);
