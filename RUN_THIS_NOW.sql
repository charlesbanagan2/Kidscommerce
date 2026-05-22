-- ============================================
-- RUN THIS SQL SCRIPT NOW TO FIX PROFILE IMAGES
-- ============================================

-- 1. Add profile_picture column if it doesn't exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(255) NULL AFTER email;

-- 2. Check current users
SELECT id, email, role, profile_picture FROM users LIMIT 10;

-- 3. Create PSGC tables
CREATE TABLE IF NOT EXISTS psgc_regions (
    psgc_code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS psgc_provinces (
    psgc_code VARCHAR(20) PRIMARY KEY,
    region_code VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS psgc_cities (
    psgc_code VARCHAR(20) PRIMARY KEY,
    province_code VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS psgc_barangays (
    psgc_code VARCHAR(20) PRIMARY KEY,
    city_code VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Insert sample PSGC data (Philippine regions)
INSERT IGNORE INTO psgc_regions (psgc_code, name, code) VALUES
('010000000', 'Region I (Ilocos Region)', '01'),
('020000000', 'Region II (Cagayan Valley)', '02'),
('030000000', 'Region III (Central Luzon)', '03'),
('040000000', 'Region IV-A (CALABARZON)', '04'),
('050000000', 'Region V (Bicol Region)', '05'),
('060000000', 'Region VI (Western Visayas)', '06'),
('070000000', 'Region VII (Central Visayas)', '07'),
('080000000', 'Region VIII (Eastern Visayas)', '08'),
('090000000', 'Region IX (Zamboanga Peninsula)', '09'),
('100000000', 'Region X (Northern Mindanao)', '10'),
('110000000', 'Region XI (Davao Region)', '11'),
('120000000', 'Region XII (SOCCSKSARGEN)', '12'),
('130000000', 'National Capital Region (NCR)', '13'),
('140000000', 'Cordillera Administrative Region (CAR)', '14'),
('150000000', 'Autonomous Region in Muslim Mindanao (ARMM)', '15'),
('160000000', 'Region XIII (Caraga)', '16'),
('170000000', 'Region IV-B (MIMAROPA)', '17');

-- 5. Insert NCR provinces
INSERT IGNORE INTO psgc_provinces (psgc_code, region_code, name, code) VALUES
('133900000', '130000000', 'Metro Manila', '1339');

-- 6. Insert Metro Manila cities
INSERT IGNORE INTO psgc_cities (psgc_code, province_code, name, code) VALUES
('133901000', '133900000', 'City of Manila', '133901'),
('133902000', '133900000', 'Quezon City', '133902'),
('133903000', '133900000', 'Caloocan City', '133903'),
('133904000', '133900000', 'Las Piñas City', '133904'),
('133905000', '133900000', 'Makati City', '133905'),
('133906000', '133900000', 'Malabon City', '133906'),
('133907000', '133900000', 'Mandaluyong City', '133907'),
('133908000', '133900000', 'Marikina City', '133908'),
('133909000', '133900000', 'Muntinlupa City', '133909'),
('133910000', '133900000', 'Navotas City', '133910'),
('133911000', '133900000', 'Parañaque City', '133911'),
('133912000', '133900000', 'Pasay City', '133912'),
('133913000', '133900000', 'Pasig City', '133913'),
('133914000', '133900000', 'Pateros', '133914'),
('133915000', '133900000', 'San Juan City', '133915'),
('133916000', '133900000', 'Taguig City', '133916'),
('133917000', '133900000', 'Valenzuela City', '133917');

-- 7. Insert sample barangays for Manila
INSERT IGNORE INTO psgc_barangays (psgc_code, city_code, name, code) VALUES
('133901001', '133901000', 'Barangay 1 (Intramuros)', '13390101'),
('133901002', '133901000', 'Barangay 2 (Intramuros)', '13390102'),
('133901003', '133901000', 'Barangay 3 (Intramuros)', '13390103'),
('133901004', '133901000', 'Ermita', '13390104'),
('133901005', '133901000', 'Malate', '13390105'),
('133901006', '133901000', 'Paco', '13390106'),
('133901007', '133901000', 'Pandacan', '13390107'),
('133901008', '133901000', 'Port Area', '13390108'),
('133901009', '133901000', 'Sampaloc', '13390109'),
('133901010', '133901000', 'San Miguel', '13390110'),
('133901011', '133901000', 'Santa Ana', '13390111'),
('133901012', '133901000', 'Santa Cruz', '13390112'),
('133901013', '133901000', 'Santa Mesa', '13390113'),
('133901014', '133901000', 'Tondo', '13390114'),
('133901015', '133901000', 'Binondo', '13390115'),
('133901016', '133901000', 'Quiapo', '13390116');

-- 8. Verify data was inserted
SELECT 'Regions' as table_name, COUNT(*) as count FROM psgc_regions
UNION ALL
SELECT 'Provinces', COUNT(*) FROM psgc_provinces
UNION ALL
SELECT 'Cities', COUNT(*) FROM psgc_cities
UNION ALL
SELECT 'Barangays', COUNT(*) FROM psgc_barangays;

-- 9. Test queries
SELECT * FROM psgc_regions LIMIT 5;
SELECT * FROM psgc_provinces WHERE region_code = '130000000';
SELECT * FROM psgc_cities WHERE province_code = '133900000' LIMIT 5;
SELECT * FROM psgc_barangays WHERE city_code = '133901000' LIMIT 5;

-- ============================================
-- DONE! Now test the API endpoints:
-- http://localhost:8000/api/regions
-- http://localhost:8000/api/provinces?region_code=130000000
-- http://localhost:8000/api/cities?province_code=133900000
-- http://localhost:8000/api/barangays?city_code=133901000
-- ============================================
