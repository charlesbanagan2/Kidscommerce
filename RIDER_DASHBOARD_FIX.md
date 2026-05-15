# Rider Dashboard Fix - Real-Time Order Pickup System

## Problem
Riders were not seeing incoming orders when sellers marked items as "ready for pickup". The incoming orders section remained empty.

## Root Causes

1. **Wrong API Endpoint**: Mobile app was calling `/api/orders/rider` which only returns orders already assigned to the rider, not available orders.

2. **Missing Endpoints**: The accept/decline endpoints (`/api/v1/rider/orders/<id>/accept` and `/api/v1/rider/orders/<id>/decline`) were not implemented in the backend.

3. **No Auto-Refresh**: The rider dashboard wasn't automatically refreshing to show new orders.

## Changes Made

### Backend (app.py)

1. **Added Accept Order Endpoint** (`/api/v1/rider/orders/<int:order_id>/accept`):
   - Implements FCFS (First Come First Served) with row-level locking
   - Prevents race conditions when multiple riders try to accept same order
   - Updates order status from `ready_for_pickup` to `in_transit`
   - Assigns rider_id and calculates rider earnings (15% of order total)
   - Sends Socket.IO notifications to buyer and other riders

2. **Added Decline Order Endpoint** (`/api/v1/rider/orders/<int:order_id>/decline`):
   - Allows riders to decline orders they don't want
   - Order remains available for other riders

### Mobile App

1. **ApiService** (`lib/services/api_service.dart`):
   - Added `getRiderAvailableOrders()` - fetches orders with status `ready_for_pickup`
   - Added `acceptRiderOrder(orderId)` - accepts an order
   - Added `declineRiderOrder(orderId)` - declines an order

2. **Rider Dashboard** (`lib/screens/rider/rider_dashboard_screen.dart`):
   - Now fetches BOTH available orders AND assigned orders
   - Added auto-refresh every 10 seconds to check for new orders
   - Improved error handling for FCFS conflicts (when another rider takes the order first)
   - Added Timer cleanup on dispose

## How It Works Now

### Order Flow

```
Seller marks order as "ready_for_pickup"
    ↓
Order appears in /api/v1/rider/available-orders
    ↓
Rider dashboard auto-refreshes (every 10 seconds)
    ↓
Order shows in "Incoming Orders" section
    ↓
Rider clicks "Accept"
    ↓
Backend locks the order row (FCFS)
    ↓
If still available:
  - Order status → "in_transit"
  - rider_id assigned
  - rider_earnings calculated (15%)
  - Notifications sent
    ↓
Order moves to "My Active Orders"
```

### FCFS Protection

The accept endpoint uses database row-level locking:
```python
order = db.session.query(Order).filter(
    Order.id == order_id
).with_for_update().first()
```

This ensures only ONE rider can accept each order, even if multiple riders click "Accept" simultaneously.

### Real-Time Updates

1. **Auto-Refresh**: Dashboard refreshes every 10 seconds
2. **Socket.IO** (future): Can be enhanced with real-time push notifications
3. **Conflict Handling**: If order is taken by another rider, shows error and refreshes

## API Endpoints

### Get Available Orders
```
GET /api/v1/rider/available-orders
Authorization: Bearer <token>
Role: rider

Response:
{
  "orders": [
    {
      "id": 123,
      "total_amount": 500.0,
      "shipping_address": "...",
      "recipient_name": "...",
      "recipient_phone": "...",
      "buyer": {...},
      "items": [...]
    }
  ],
  "pagination": {...}
}
```

### Accept Order
```
POST /api/v1/rider/orders/<order_id>/accept
Authorization: Bearer <token>
Role: rider

Response (Success):
{
  "success": true,
  "message": "Order accepted successfully",
  "order": {
    "id": 123,
    "status": "in_transit",
    "rider_earnings": 75.0,
    "picked_up_at": "2025-01-15T10:30:00"
  }
}

Response (Conflict):
{
  "success": false,
  "error": "Order already taken by another rider",
  "conflict": true
}
```

### Decline Order
```
POST /api/v1/rider/orders/<order_id>/decline
Authorization: Bearer <token>
Role: rider

Response:
{
  "success": true,
  "message": "Order declined"
}
```

## Testing

1. **Login as Seller** → Mark order as "ready for pickup"
2. **Login as Rider** → Wait up to 10 seconds
3. **Verify** order appears in "Incoming Orders"
4. **Click Accept** → Order moves to "My Active Orders"
5. **Test FCFS** → Have 2 riders try to accept same order (only 1 succeeds)

## Future Enhancements

1. **Socket.IO Integration**: Real-time push notifications instead of polling
2. **Sound Alerts**: Play sound when new order arrives
3. **Push Notifications**: FCM for background notifications
4. **Order Filtering**: Filter by distance, earnings, etc.
5. **Map View**: Show pickup/delivery locations on map

## Files Modified

### Backend
- `backend/app.py` - Added accept/decline endpoints

### Mobile App
- `mobile_app/lib/services/api_service.dart` - Added API methods
- `mobile_app/lib/screens/rider/rider_dashboard_screen.dart` - Added auto-refresh and improved order fetching

## Result

✅ Riders now see incoming orders in real-time
✅ FCFS system prevents conflicts
✅ Auto-refresh keeps dashboard updated
✅ Accept/decline functionality works correctly
✅ Orders properly transition from available → assigned → delivered
