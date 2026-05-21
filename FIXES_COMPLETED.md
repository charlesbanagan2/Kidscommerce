# ✅ PROFILE & PSGC FIX - COMPLETED

## What Was Done Successfully:

### ✅ Database Fixed (COMPLETED)
- Created `psgc_regions` table with 17 Philippine regions
- Created `psgc_provinces` table with Metro Manila
- Created `psgc_cities` table with 17 Metro Manila cities
- Created `psgc_barangays` table with 16 Manila barangays
- All PSGC data is now in the database!

### ⚠️ What Still Needs to Be Done:

## 1. Add Profile Picture Column to Users Table

The `users` table doesn't exist yet. You need to add the column manually in Supabase:

**Go to Supabase Dashboard:**
1. Open https://supabase.com/dashboard
2. Select your project: `qkdacoawexaxejljfihh`
3. Go to **Table Editor** → **users** table
4. Click **Add Column**
5. Add column:
   - Name: `profile_picture`
   - Type: `text` or `varchar`
   - Nullable: Yes (check the box)
6. Click **Save**

## 2. Add PSGC API Routes to Backend

**File: `backend/app.py` or `backend/routes.py`**

Add these routes:

```python
from flask import jsonify, request
from supabase import create_client
import os

# Initialize Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# PSGC Routes (NO AUTH REQUIRED)
@app.route('/api/regions', methods=['GET'])
def get_regions():
    try:
        response = supabase.table('psgc_regions').select('*').order('name').execute()
        return jsonify({
            'success': True,
            'result': response.data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/provinces', methods=['GET'])
def get_provinces():
    try:
        region_code = request.args.get('region_code')
        query = supabase.table('psgc_provinces').select('*')
        if region_code:
            query = query.eq('region_code', region_code)
        response = query.order('name').execute()
        return jsonify({
            'success': True,
            'result': response.data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cities', methods=['GET'])
def get_cities():
    try:
        province_code = request.args.get('province_code')
        query = supabase.table('psgc_cities').select('*')
        if province_code:
            query = query.eq('province_code', province_code)
        response = query.order('name').execute()
        return jsonify({
            'success': True,
            'result': response.data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/barangays', methods=['GET'])
def get_barangays():
    try:
        city_code = request.args.get('city_code')
        query = supabase.table('psgc_barangays').select('*')
        if city_code:
            query = query.eq('city_code', city_code)
        response = query.order('name').execute()
        return jsonify({
            'success': True,
            'result': response.data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

## 3. Update Profile API to Return profile_picture

**File: `backend/routes/profile.py` or wherever profile endpoint is**

```python
@app.route('/api/v1/buyer/profile', methods=['GET'])
@require_auth  # Your auth decorator
def get_buyer_profile(user_id):
    try:
        response = supabase.table('users').select('*').eq('id', user_id).single().execute()
        user = response.data
        
        return jsonify({
            'success': True,
            'profile': {
                'id': user['id'],
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'email': user['email'],
                'phone': user.get('phone'),
                'address': user.get('address'),
                'profile_picture': user.get('profile_picture'),  # ← ADD THIS
                'role': user['role']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

## 4. Test Everything

### Test PSGC APIs:
```bash
# Test regions
curl http://localhost:5000/api/regions

# Test provinces for NCR
curl http://localhost:5000/api/provinces?region_code=130000000

# Test cities for Metro Manila
curl http://localhost:5000/api/cities?province_code=133900000

# Test barangays for Manila
curl http://localhost:5000/api/barangays?city_code=133901000
```

### Test Profile API:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/v1/buyer/profile
```

Should return:
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
    "profile_picture": "profiles/abc123.jpg",  ← THIS FIELD
    "role": "buyer"
  }
}
```

## Summary:

✅ PSGC database tables created and populated  
✅ 17 regions, 1 province, 17 cities, 16 barangays loaded  
⏳ Need to add PSGC routes to Flask backend  
⏳ Need to add profile_picture column to users table in Supabase  
⏳ Need to update profile API to return profile_picture  

The Flutter app is already correct and will work once backend is updated!
