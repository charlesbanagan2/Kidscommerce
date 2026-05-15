# Photo Proof Delivery Implementation

## Summary
Added photo proof functionality for delivery confirmation. Riders must upload a photo when marking orders as delivered, and buyers can view the proof in order details.

## Changes Made

### 1. Mobile App (Flutter)

#### API Service (`lib/services/api_service.dart`)
- Added `dart:io` import
- Added `uploadDeliveryProof()` method to upload photo via multipart request

#### Order Model (`lib/models/order.dart`)
- Added `proofPhotoUrl` field to Order class
- Updated `fromJson()` and `toJson()` methods

#### Rider Dashboard (`lib/screens/rider/rider_dashboard_screen.dart`)
- Added photo proof bottom sheet UI (`_PhotoProofSheet`)
- Added camera/gallery picker functionality
- Updated `_submitDelivery()` to upload photo then mark as delivered
- Added helper methods: `_showSourcePicker()`, `_buildPhotoPlaceholder()`, `_buildPhotoPreview()`
- Added `_SourceButton` widget

#### Buyer Order Detail (`lib/screens/buyer_app/order_detail.dart`)
- Added `_buildDeliveryProof()` method to display proof photo
- Photo is tappable to view full-screen
- Only shows when `proofPhotoUrl` is available

### 2. Backend (Flask)

#### API Endpoint (`app.py`)
- Added `/api/v1/rider/orders/<order_id>/upload-proof` endpoint
- Handles multipart file upload
- Saves photo to `static/uploads/delivery_proofs/`
- Updates order with `proof_photo_url`
- Returns photo URL to client

#### Database
- Need to run migration: `python add_proof_column_supabase.py`
- Adds `proof_photo_url TEXT` column to `order` table

## Usage Flow

### Rider Side:
1. Rider taps "Delivered" button on active order
2. Photo proof sheet appears
3. Rider selects Camera or Gallery
4. Takes/selects photo
5. Reviews photo (can retake)
6. Taps "Confirm Delivery"
7. Photo uploads → Order marked as delivered

### Buyer Side:
1. Opens delivered order details
2. Sees "Delivery Proof" section with photo
3. Taps photo to view full-screen
4. Can close full-screen view

## Files Modified
- `mobile_app/lib/services/api_service.dart`
- `mobile_app/lib/models/order.dart`
- `mobile_app/lib/screens/rider/rider_dashboard_screen.dart`
- `mobile_app/lib/screens/buyer_app/order_detail.dart`
- `backend/app.py`

## Files Created
- `backend/add_upload_proof_endpoint.py` (migration script)
- `backend/add_proof_column_supabase.py` (database migration)
- `backend/add_proof_photo_url_column.sql` (SQL migration)

## Next Steps
1. Run database migration: `python add_proof_column_supabase.py`
2. Create `static/uploads/delivery_proofs/` directory
3. Test photo upload flow
4. Verify photo display on buyer side
