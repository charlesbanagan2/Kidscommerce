# Delivery Proof Upload Fix

## Issue
- 404 error when uploading proof or images and clicking delivered
- Rider dashboard showing "Delivered" button for orders with status `to_ship`
- Backend only accepts `in_transit` orders for marking as delivered

## Root Cause
The rider dashboard was showing a "Delivered" button for both `to_ship` and `in_transit` orders, but the backend `/api/v1/rider/orders/<order_id>/mark-delivered` endpoint only accepts orders with status `in_transit`.

## Solution

### Frontend Fix (rider_dashboard_screen.dart)
1. **Separated action buttons by order status:**
   - `to_ship` orders → Show "Picked Up" button (transitions to `in_transit`)
   - `in_transit` orders → Show "Delivered" button (opens photo proof sheet)

2. **Added `_markPickedUp()` method:**
   - Calls `ApiService.updateOrderStatus()` to transition from `to_ship` → `in_transit`
   - Shows success message
   - Refreshes dashboard

3. **Photo proof flow remains intact:**
   - Only triggered for `in_transit` orders
   - Opens bottom sheet to capture/select photo
   - Uploads photo via `uploadDeliveryProof()`
   - Marks order as delivered via `markOrderAsDelivered()`

### Backend Endpoints (Already Working)
1. **Upload Proof:** `POST /api/v1/rider/orders/<order_id>/upload-proof`
   - Accepts multipart form data with `proof_photo` field
   - Saves to `static/uploads/delivery_proofs/`
   - Updates order with `proof_photo_url`

2. **Mark Delivered:** `POST /api/v1/rider/orders/<order_id>/mark-delivered`
   - Requires order status to be `in_transit`
   - Updates status to `delivered`
   - Sets `delivered_at` and `delivered_by`
   - Notifies buyer and sellers

### Buyer Side (Already Working)
- `order_detail.dart` already displays delivery proof photos
- Shows photo in a card with tap-to-expand functionality
- Uses `UrlConfig.toAbsoluteImageUrl()` to construct full URL

## Order Flow
```
1. Order created → status: 'to_ship'
2. Rider accepts order → status: 'to_ship' (assigned to rider)
3. Rider picks up from seller → status: 'in_transit' (via "Picked Up" button)
4. Rider delivers to customer:
   a. Tap "Delivered" button
   b. Take/select photo proof
   c. Upload photo → saved to server
   d. Mark as delivered → status: 'delivered'
5. Buyer views order → sees delivery proof photo
```

## Files Modified
- `mobile_app/lib/screens/rider/rider_dashboard_screen.dart`
  - Fixed action button logic
  - Added `_markPickedUp()` method
  - Separated buttons by order status

## Testing Checklist
- [x] Rider can mark `to_ship` order as picked up
- [x] Rider can upload photo proof for `in_transit` order
- [x] Rider can mark `in_transit` order as delivered
- [x] Buyer can view delivery proof photo
- [x] Backend endpoints working correctly
- [x] No 404 errors

## API Endpoints Used
```
POST /api/orders/status
  - Update order status (to_ship → in_transit)

POST /api/v1/rider/orders/<order_id>/upload-proof
  - Upload delivery proof photo

POST /api/v1/rider/orders/<order_id>/mark-delivered
  - Mark order as delivered (requires in_transit status)
```
