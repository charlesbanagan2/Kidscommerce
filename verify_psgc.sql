-- PSGC Database Verification Script

-- 1. Check if tables exist
SHOW TABLES LIKE 'psgc_%';

-- 2. Check data counts
SELECT 'regions' as table_name, COUNT(*) as count FROM psgc_regions
UNION ALL
SELECT 'provinces', COUNT(*) FROM psgc_provinces
UNION ALL
SELECT 'cities', COUNT(*) FROM psgc_cities
UNION ALL
SELECT 'barangays', COUNT(*) FROM psgc_barangays;

-- 3. Sample data check
SELECT * FROM psgc_regions LIMIT 5;
SELECT * FROM psgc_provinces LIMIT 5;
SELECT * FROM psgc_cities LIMIT 5;
SELECT * FROM psgc_barangays LIMIT 5;

-- 4. Check profile_picture column
DESCRIBE users;
SELECT id, email, profile_picture FROM users WHERE role = 'buyer' LIMIT 10;

-- 5. Check buyer_addresses table
DESCRIBE buyer_addresses;
SELECT * FROM buyer_addresses LIMIT 10;

-- If PSGC tables are empty, you need to import data from:
-- https://github.com/faeldon/philippines-json-maps
-- or use the PSGC official data
