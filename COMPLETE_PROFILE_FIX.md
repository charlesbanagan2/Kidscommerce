## PROFILE IMAGE FIX - ALL SCREENS

### Issue: Profile images not displaying in Buyer and Rider profile screens

### Root Cause Analysis:
1. **Backend API** - Profile endpoint not returning `profile_picture` field correctly
2. **Database** - `profile_picture` column may be NULL or empty
3. **Image Path** - Incorrect URL construction or missing files

---

## BACKEND FIXES (Laravel/PHP)

### 1. Check Database Schema
```sql
-- Verify profile_picture column exists
DESCRIBE users;

-- Check current data
SELECT id, email, role, profile_picture FROM users WHERE role IN ('buyer', 'rider');

-- If column doesn't exist, add it:
ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255) NULL AFTER email;
```

### 2. Update Profile API Response

**File: `app/Http/Controllers/Api/ProfileController.php`**

```php
public function getProfile(Request $request)
{
    $user = $request->user();
    
    return response()->json([
        'success' => true,
        'profile' => [
            'id' => $user->id,
            'first_name' => $user->first_name,
            'last_name' => $user->last_name,
            'email' => $user->email,
            'phone' => $user->phone,
            'address' => $user->address,
            'profile_picture' => $user->profile_picture, // ← CRITICAL
            'role' => $user->role,
        ]
    ]);
}
```

### 3. Update User Model

**File: `app/Models/User.php`**

```php
protected $fillable = [
    'first_name',
    'last_name',
    'email',
    'password',
    'phone',
    'address',
    'profile_picture', // ← ADD THIS
    'role',
];

protected $appends = ['full_name'];

public function getFullNameAttribute()
{
    return trim("{$this->first_name} {$this->last_name}");
}
```

### 4. Profile Update Endpoint

```php
public function updateProfile(Request $request)
{
    $user = $request->user();
    
    $validated = $request->validate([
        'first_name' => 'sometimes|string|max:255',
        'last_name' => 'sometimes|string|max:255',
        'email' => 'sometimes|email|unique:users,email,' . $user->id,
        'phone' => 'sometimes|string|max:20',
        'address' => 'sometimes|string',
        'profile_picture' => 'sometimes|image|max:2048', // ← ADD THIS
    ]);
    
    // Handle profile picture upload
    if ($request->hasFile('profile_picture')) {
        // Delete old image if exists
        if ($user->profile_picture) {
            Storage::disk('public')->delete($user->profile_picture);
        }
        
        $path = $request->file('profile_picture')->store('profiles', 'public');
        $validated['profile_picture'] = $path;
    }
    
    $user->update($validated);
    
    return response()->json([
        'success' => true,
        'message' => 'Profile updated successfully',
        'user' => $user
    ]);
}
```

---

## PSGC API FIXES

### 1. Create PSGC Controller

**File: `app/Http/Controllers/Api/PSGCController.php`**

```php
<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class PSGCController extends Controller
{
    public function getRegions()
    {
        $regions = DB::table('psgc_regions')
            ->select('psgc_code', 'name', 'code')
            ->orderBy('name')
            ->get();
            
        return response()->json([
            'success' => true,
            'result' => $regions
        ]);
    }
    
    public function getProvinces(Request $request)
    {
        $regionCode = $request->query('region_code');
        
        $provinces = DB::table('psgc_provinces')
            ->select('psgc_code', 'name', 'code', 'region_code')
            ->where('region_code', $regionCode)
            ->orderBy('name')
            ->get();
            
        return response()->json([
            'success' => true,
            'result' => $provinces
        ]);
    }
    
    public function getCities(Request $request)
    {
        $provinceCode = $request->query('province_code');
        
        $cities = DB::table('psgc_cities')
            ->select('psgc_code', 'name', 'code', 'province_code')
            ->where('province_code', $provinceCode)
            ->orderBy('name')
            ->get();
            
        return response()->json([
            'success' => true,
            'result' => $cities
        ]);
    }
    
    public function getBarangays(Request $request)
    {
        $cityCode = $request->query('city_code');
        
        $barangays = DB::table('psgc_barangays')
            ->select('psgc_code', 'name', 'code', 'city_code')
            ->where('city_code', $cityCode)
            ->orderBy('name')
            ->get();
            
        return response()->json([
            'success' => true,
            'result' => $barangays
        ]);
    }
}
```

### 2. Add Routes

**File: `routes/api.php`**

```php
// PSGC Routes (NO AUTH REQUIRED)
Route::get('/regions', [PSGCController::class, 'getRegions']);
Route::get('/provinces', [PSGCController::class, 'getProvinces']);
Route::get('/cities', [PSGCController::class, 'getCities']);
Route::get('/barangays', [PSGCController::class, 'getBarangays']);
```

### 3. Create Database Tables

```sql
-- Create PSGC tables
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_code) REFERENCES psgc_regions(psgc_code)
);

CREATE TABLE IF NOT EXISTS psgc_cities (
    psgc_code VARCHAR(20) PRIMARY KEY,
    province_code VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (province_code) REFERENCES psgc_provinces(psgc_code)
);

CREATE TABLE IF NOT EXISTS psgc_barangays (
    psgc_code VARCHAR(20) PRIMARY KEY,
    city_code VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_code) REFERENCES psgc_cities(psgc_code)
);
```

### 4. Import PSGC Data

Download from: https://github.com/faeldon/philippines-json-maps

Or use this sample data:

```sql
-- Sample Regions
INSERT INTO psgc_regions (psgc_code, name, code) VALUES
('010000000', 'Region I (Ilocos Region)', '01'),
('020000000', 'Region II (Cagayan Valley)', '02'),
('030000000', 'Region III (Central Luzon)', '03'),
('040000000', 'Region IV-A (CALABARZON)', '04'),
('130000000', 'National Capital Region (NCR)', '13');

-- Sample Provinces for NCR
INSERT INTO psgc_provinces (psgc_code, region_code, name, code) VALUES
('133900000', '130000000', 'Metro Manila', '1339');

-- Sample Cities for Metro Manila
INSERT INTO psgc_cities (psgc_code, province_code, name, code) VALUES
('133901000', '133900000', 'Manila', '13390100'),
('133902000', '133900000', 'Quezon City', '13390200'),
('133903000', '133900000', 'Makati', '13390300');
```

---

## TESTING

### 1. Test Profile API
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/buyer/profile
```

Expected response:
```json
{
  "success": true,
  "profile": {
    "id": 1,
    "first_name": "Juan",
    "last_name": "Dela Cruz",
    "email": "juan@example.com",
    "phone": "09123456789",
    "address": "Manila",
    "profile_picture": "profiles/abc123.jpg",
    "role": "buyer"
  }
}
```

### 2. Test PSGC APIs
```bash
# Test regions (NO AUTH)
curl http://localhost:8000/api/regions

# Test provinces
curl http://localhost:8000/api/provinces?region_code=130000000

# Test cities
curl http://localhost:8000/api/cities?province_code=133900000

# Test barangays
curl http://localhost:8000/api/barangays?city_code=133901000
```

---

## QUICK FIX CHECKLIST

- [ ] Run `php artisan migrate`
- [ ] Add `profile_picture` column to users table
- [ ] Create PSGCController.php
- [ ] Add PSGC routes to api.php
- [ ] Create PSGC database tables
- [ ] Import PSGC data
- [ ] Test `/api/regions` endpoint
- [ ] Test `/api/v1/buyer/profile` endpoint
- [ ] Verify images in `public/storage/profiles/` directory
- [ ] Run `php artisan storage:link` if needed

---

## FRONTEND (Already Fixed)

The Flutter code is already correct:
- Buyer profile: Uses `UrlConfig.toAbsoluteImageUrl(profileImage)`
- Rider profile: Uses `UrlConfig.toAbsoluteImageUrl(profileImage)`

The issue is 100% backend - the API is not returning the profile_picture field.
