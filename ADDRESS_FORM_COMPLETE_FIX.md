# Address Form Fixes - Complete Summary

## Issues Fixed

### 1. ✅ Backend API - Regions Not Loading
**Problem:** Frontend showed "No regions found"
**Root Cause:** Backend was returning raw PSGC API response, but frontend expected `{result: [...]}`

**Fixed Files:**
- `backend/app.py` - All 4 PSGC proxy endpoints

**Changes:**
```python
# Before: Returned raw response
return Response(r.content, status=r.status_code, ...)

# After: Wrap in result format
data = r.json()
if isinstance(data, list):
    return jsonify({'result': data})
elif isinstance(data, dict) and 'result' in data:
    return jsonify(data)
else:
    return jsonify({'result': data if isinstance(data, list) else [data]})
```

**Endpoints Fixed:**
- `/api/regions` - Returns regions list
- `/api/provinces?region_code=XXX` - Returns provinces for region
- `/api/cities?province_code=XXX` - Returns cities for province
- `/api/barangays?city_code=XXX` - Returns barangays for city

### 2. ✅ Bottom Sheet Size - Reduced
**Problem:** Address form too large (55% of screen)
**Solution:** Reduced to 42% for better UX

**File:** `mobile_app/lib/screens/buyer_app/profile_screen.dart`
**Line:** 1126

```dart
// Before
maxHeight: MediaQuery.of(ctx).size.height * 0.55,

// After
maxHeight: MediaQuery.of(ctx).size.height * 0.42,
```

### 3. ✅ Database Save - Already Working
**Status:** Already implemented correctly

**Save Flow:**
1. User completes 5-step address form:
   - Step 1: Select Region
   - Step 2: Select Province
   - Step 3: Select City
   - Step 4: Select Barangay
   - Step 5: Enter street address + label

2. On "Save Address" button:
   ```dart
   await _addAddress(
     label: finalLabel,
     street: streetController.text.trim(),
     city: selectedCity ?? '',
     province: selectedProvince ?? '',
     region: selectedRegion ?? '',
     barangay: selectedBarangay,
     zip: '',
     isDefault: isDefault,
   );
   ```

3. API Call to Backend:
   ```dart
   POST /api/v1/buyer/addresses
   Body: {
     'label': 'Home',
     'full_address': 'Unit 4B, Brgy San Jose, Manila, Metro Manila, NCR',
     'street_address': 'Unit 4B',
     'city': 'Manila',
     'province': 'Metro Manila',
     'region': 'NCR',
     'barangay': 'San Jose',
     'zip_code': '',
     'is_default': true
   }
   ```

4. Database Table: `address`
   - Columns: id, user_id, label, full_address, street, city, province, region, barangay, is_default, created_at

5. If `is_default = true`:
   - Updates buyer profile
   - Refreshes AuthProvider
   - Refreshes BuyerProvider

### 4. ✅ Checkout Integration - Already Working
**Status:** Address automatically used at checkout

**How it works:**
1. When buyer goes to checkout, system fetches default address:
   ```dart
   GET /api/v1/buyer/addresses
   ```

2. Default address is pre-filled in shipping_address field

3. Order is created with full address:
   ```dart
   POST /api/v1/orders
   Body: {
     'shipping_address': 'Unit 4B, Brgy San Jose, Manila, Metro Manila, NCR',
     ...
   }
   ```

4. Order table stores complete address in `shipping_address` column

## Testing Checklist

- [x] Backend returns regions in correct format
- [x] Backend returns provinces when region selected
- [x] Backend returns cities when province selected
- [x] Backend returns barangays when city selected
- [x] Bottom sheet is good size (42% of screen)
- [x] Form is scrollable for all content
- [x] Address saves to database
- [x] Default address updates buyer profile
- [x] Address appears in profile screen
- [x] Address used automatically at checkout
- [x] Order stores complete shipping address

## Database Schema

### address table
```sql
CREATE TABLE address (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user(id),
    label VARCHAR(50) NOT NULL,
    full_address TEXT NOT NULL,
    street VARCHAR(255),
    city VARCHAR(120),
    province VARCHAR(120),
    region VARCHAR(120),
    barangay VARCHAR(120),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### order table (shipping_address column)
```sql
CREATE TABLE "order" (
    id SERIAL PRIMARY KEY,
    buyer_id INTEGER REFERENCES user(id),
    shipping_address TEXT NOT NULL,
    recipient_name VARCHAR(255),
    recipient_phone VARCHAR(20),
    ...
);
```

## API Endpoints

### Address Management
- `GET /api/v1/buyer/addresses` - Get all addresses for buyer
- `POST /api/v1/buyer/addresses` - Add new address
- `DELETE /api/v1/buyer/addresses/:id` - Delete address

### PSGC Location Data
- `GET /api/regions` - Get all regions
- `GET /api/provinces?region_code=XXX` - Get provinces
- `GET /api/cities?province_code=XXX` - Get cities
- `GET /api/barangays?city_code=XXX` - Get barangays

## Complete Flow

1. **Add Address:**
   - Buyer opens profile → Add Address
   - Selects: Region → Province → City → Barangay
   - Enters: Street address + Label (Home/Work/Office/Other)
   - Checks: "Set as default" (optional)
   - Saves to database

2. **View Addresses:**
   - Profile screen shows all saved addresses
   - Default address has badge
   - Can delete addresses

3. **Checkout:**
   - Default address auto-filled
   - Buyer can change if needed
   - Order created with shipping_address

4. **Order Tracking:**
   - Rider sees full delivery address
   - Buyer sees shipping address in order details

## Result

✅ All address functionality working:
- Regions load correctly
- Form is good size
- Saves to database
- Updates at checkout
- Complete address flow functional
