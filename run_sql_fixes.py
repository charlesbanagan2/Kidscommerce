#!/usr/bin/env python3
"""
Run SQL fixes for Profile Images and PSGC API
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Database connection
DB_URL = "postgresql://postgres.qkdacoawexaxejljfihh:Kidscommerce%401234@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"

print("=" * 50)
print("RUNNING SQL FIXES FOR PROFILE & PSGC")
print("=" * 50)

try:
    # Connect to database
    print("\n1. Connecting to Supabase PostgreSQL...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    print("Connected successfully!")
    
    # 1. Add profile_picture column
    print("\n2. Adding profile_picture column to users table...")
    try:
        cur.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(255);
        """)
        conn.commit()
        print("profile_picture column added/verified")
    except Exception as e:
        print(f"Column may already exist: {e}")
        conn.rollback()
    
    # 2. Create PSGC tables
    print("\n3. Creating PSGC tables...")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS psgc_regions (
            psgc_code VARCHAR(20) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            code VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS psgc_provinces (
            psgc_code VARCHAR(20) PRIMARY KEY,
            region_code VARCHAR(20) NOT NULL,
            name VARCHAR(255) NOT NULL,
            code VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS psgc_cities (
            psgc_code VARCHAR(20) PRIMARY KEY,
            province_code VARCHAR(20) NOT NULL,
            name VARCHAR(255) NOT NULL,
            code VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS psgc_barangays (
            psgc_code VARCHAR(20) PRIMARY KEY,
            city_code VARCHAR(20) NOT NULL,
            name VARCHAR(255) NOT NULL,
            code VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    print("PSGC tables created")
    
    # 3. Insert Philippine regions
    print("\n4. Inserting Philippine regions...")
    regions = [
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
        ('170000000', 'Region IV-B (MIMAROPA)', '17'),
    ]
    
    for region in regions:
        cur.execute("""
            INSERT INTO psgc_regions (psgc_code, name, code)
            VALUES (%s, %s, %s)
            ON CONFLICT (psgc_code) DO NOTHING
        """, region)
    conn.commit()
    print(f"Inserted {len(regions)} regions")
    
    # 4. Insert Metro Manila province
    print("\n5. Inserting Metro Manila province...")
    cur.execute("""
        INSERT INTO psgc_provinces (psgc_code, region_code, name, code)
        VALUES ('133900000', '130000000', 'Metro Manila', '1339')
        ON CONFLICT (psgc_code) DO NOTHING
    """)
    conn.commit()
    print("Metro Manila province inserted")
    
    # 5. Insert Metro Manila cities
    print("\n6. Inserting Metro Manila cities...")
    cities = [
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
        ('133917000', '133900000', 'Valenzuela City', '133917'),
    ]
    
    for city in cities:
        cur.execute("""
            INSERT INTO psgc_cities (psgc_code, province_code, name, code)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (psgc_code) DO NOTHING
        """, city)
    conn.commit()
    print(f"Inserted {len(cities)} cities")
    
    # 6. Insert sample barangays for Manila
    print("\n7. Inserting sample barangays for Manila...")
    barangays = [
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
        ('133901016', '133901000', 'Quiapo', '13390116'),
    ]
    
    for barangay in barangays:
        cur.execute("""
            INSERT INTO psgc_barangays (psgc_code, city_code, name, code)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (psgc_code) DO NOTHING
        """, barangay)
    conn.commit()
    print(f"Inserted {len(barangays)} barangays")
    
    # 7. Verify data
    print("\n8. Verifying data...")
    cur.execute("SELECT COUNT(*) FROM psgc_regions")
    regions_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM psgc_provinces")
    provinces_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM psgc_cities")
    cities_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM psgc_barangays")
    barangays_count = cur.fetchone()[0]
    
    print(f"\nData Summary:")
    print(f"   Regions: {regions_count}")
    print(f"   Provinces: {provinces_count}")
    print(f"   Cities: {cities_count}")
    print(f"   Barangays: {barangays_count}")
    
    # Close connection
    cur.close()
    conn.close()
    
    print("\n" + "=" * 50)
    print("ALL FIXES APPLIED SUCCESSFULLY!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Test PSGC API: http://localhost:5000/api/regions")
    print("2. Check profile_picture in users table")
    print("3. Update backend routes to expose PSGC endpoints")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
