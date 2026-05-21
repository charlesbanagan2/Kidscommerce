# Profile Screen Fixes

## Issues Found:
1. Profile image not displaying
2. PSGC API not showing addresses

## Backend API Endpoints to Verify:

### 1. Profile Image Endpoint
```
GET /api/v1/buyer/profile
```
Should return:
```json
{
  "success": true,
  "profile": {
    "first_name": "...",
    "last_name": "...",
    "email": "...",
    "phone": "...",
    "address": "...",
    "profile_picture": "uploads/profiles/xxx.jpg"  // ← CHECK THIS
  }
}
```

### 2. PSGC API Endpoints (NO AUTH)
```
GET /api/regions
GET /api/provinces?region_code=XXXXXX
GET /api/cities?province_code=XXXXXX
GET /api/barangays?city_code=XXXXXX
```

Each should return:
```json
{
  "success": true,
  "result": [
    {
      "psgc_code": "...",
      "name": "...",
      "code": "..."
    }
  ]
}
```

### 3. Address Management
```
GET /api/v1/buyer/addresses
POST /api/v1/buyer/addresses
```

## Database Tables to Check:

### users table
- profile_picture column (VARCHAR)

### psgc_regions table
- psgc_code (VARCHAR PRIMARY KEY)
- name (VARCHAR)

### psgc_provinces table
- psgc_code (VARCHAR PRIMARY KEY)
- region_code (VARCHAR)
- name (VARCHAR)

### psgc_cities table
- psgc_code (VARCHAR PRIMARY KEY)
- province_code (VARCHAR)
- name (VARCHAR)

### psgc_barangays table
- psgc_code (VARCHAR PRIMARY KEY)
- city_code (VARCHAR)
- name (VARCHAR)

### buyer_addresses table
- id
- buyer_id
- label
- full_address
- is_default

## Quick Backend Checks:

1. Check if PSGC tables have data:
```sql
SELECT COUNT(*) FROM psgc_regions;
SELECT COUNT(*) FROM psgc_provinces;
SELECT COUNT(*) FROM psgc_cities;
SELECT COUNT(*) FROM psgc_barangays;
```

2. Check profile_picture column:
```sql
SELECT id, email, profile_picture FROM users WHERE role = 'buyer' LIMIT 5;
```

3. Test PSGC endpoints in Postman/browser:
```
http://localhost:8000/api/regions
http://localhost:8000/api/provinces?region_code=010000000
```
