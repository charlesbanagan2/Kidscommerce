# Notification Flow Documentation

## Overview
This document describes the complete notification flow for the Kids Commerce platform across buyer, seller, and rider roles.

## Backend Notification System

### Components
1. **notification_service.py** - Contains NotificationService class with methods for creating notifications
2. **notification_routes.py** - API endpoints for web notifications
3. **notification_api_endpoints.py** - Mobile API endpoints for notifications (registered in app.py)
4. **push_notification()** function in app.py - Core function that creates and emits notifications

### Notification Storage
- Notifications are stored in the `notification` table in the database
- Each notification includes: user_id, message, type, order_id, created_at, is_read, etc.
- Real-time notifications are emitted via Socket.IO to room `user_{user_id}`

## Mobile App Integration

### API Endpoints (notification_api_endpoints.py)
- `GET /api/v1/notifications` - Get all notifications for current user
- `GET /api/v1/notifications/unread-count` - Get unread notification count
- `PUT /api/v1/notifications/<id>/read` - Mark notification as read
- `PUT /api/v1/notifications/mark-all-read` - Mark all notifications as read
- `DELETE /api/v1/notifications/<id>` - Delete notification

### Mobile Screens
- **Buyer Notification Screen** (`mobile_app/lib/screens/buyer_app/notification_screen.dart`)
  - Fetches notifications from `/api/v1/notifications`
  - Displays notifications with filtering (all, unread, orders, promos, products)
  - Supports marking as read and dismissing notifications
  
- **Rider Notification Screen** (`mobile_app/lib/screens/rider/rider_notifications_screen.dart`)
  - Fetches notifications from `/api/v1/notifications`
  - Displays notifications with type badges (new order, in transit, delivered, payment, bonus)
  - Supports marking as read and dismissing notifications

- **Seller App** - No dedicated notification screen (uses web interface)

## Notification Flow

### 1. Buyer Places Order
**Endpoint:** `POST /api/v1/orders`

**Flow:**
1. Buyer creates order via mobile app
2. Order is created in database
3. **Notification sent to all sellers** of products in the order
4. Message: "New order #{order_id} received!"
5. Type: `order`

**Code Location:** app.py line 16444-16454

---

### 2. Seller Processes Order
**Endpoint:** `PUT /api/v1/orders/status` (status = 'processing')

**Flow:**
1. Seller marks order as processing
2. **Notification sent to buyer**
3. Message: "Your order #{order_id} is now being processed."
4. Type: `order_processing`

**Code Location:** app.py line 17608-17615

---

### 3. Seller Marks Ready for Pickup
**Endpoint:** `PUT /api/v1/orders/status` (status = 'ready_for_pickup')

**Flow:**
1. Seller marks order as ready for pickup
2. **Notification sent to buyer** (shown as "out for delivery")
3. Message: "Your order #{order_id} is out for delivery."
4. Type: `out_for_delivery`
5. **Socket.IO broadcast to all active riders** with order details
6. Riders see order in their available orders list

**Code Location:** app.py line 17616-17631

---

### 4. Rider Accepts Order
**Endpoint:** `POST /api/v1/rider/orders/<order_id>/accept`

**Flow:**
1. Rider accepts available order (FCFS - first-come-first-served)
2. Order status changes to `in_transit`
3. **Notification sent to buyer**
4. Message: "Rider {rider_name} has been assigned to deliver your order #{order_id}."
5. Type: `rider_assigned`
6. **Notification sent to seller**
7. Message: "Rider {rider_name} has accepted order #{order_id}."
8. Type: `rider_assigned`

**Code Location:** app.py line 17508-17530

---

### 5. Rider Picks Up Order
**Endpoint:** `PUT /api/v1/orders/status` (status = 'picked_up')

**Flow:**
1. Rider marks order as picked up
2. **Notification sent to seller**
3. Message: "✓ Order #{order_id} picked up by rider {rider_name}"
4. Type: `order_picked_up`

**Code Location:** app.py line 17632-17651

---

### 6. Rider Delivers Order
**Endpoint:** `PUT /api/v1/orders/status` (status = 'delivered')

**Flow:**
1. Rider marks order as delivered
2. **Notification sent to buyer**
3. Message: "Your order #{order_id} has been delivered! Please confirm receipt."
4. Type: `order_delivered`
5. **Notification sent to seller**
6. Message: "Order #{order_id} has been delivered to buyer."
7. Type: `order_delivered`

**Code Location:** app.py line 17652-17671

---

### 7. Buyer Confirms Receipt
**Endpoint:** `POST /api/v1/buyer/orders/<order_id>/confirm-delivery` (web endpoint)

**Flow:**
1. Buyer confirms order receipt
2. Order status changes to `completed`
3. Commission is released to seller (85%) and admin (15%)
4. **Notification sent to rider** (if rider exists)
5. Message: "Order #{order_id} completed. Your delivery fee has been credited."
6. Type: `delivery_completed`

**Code Location:** app.py line 12684-12693 (web endpoint)

---

## Issues Fixed

### Issue 1: Mobile Apps Using Mock Data
**Problem:** Buyer and rider notification screens were using hardcoded mock data instead of fetching from the backend API.

**Fix:**
- Updated buyer notification screen to call `ApiService.getNotifications()`
- Updated rider notification screen to call `ApiService.getNotifications()`
- Added proper time formatting and type parsing
- Integrated mark-as-read functionality with API calls

**Files Modified:**
- `mobile_app/lib/screens/buyer_app/notification_screen.dart`
- `mobile_app/lib/screens/rider/rider_notifications_screen.dart`

---

### Issue 2: Missing Notifications in Mobile API Endpoints
**Problem:** The mobile API endpoints for order creation and status updates were not triggering notifications, unlike the web endpoints.

**Fix:**
- Added notification calls to `POST /api/v1/orders` (order creation)
- Added notification calls to `PUT /api/v1/orders/status` (status updates)
- Added notification calls to `POST /api/v1/rider/orders/<id>/accept` (rider accept)
- Notifications now trigger for: processing, ready_for_pickup, picked_up, delivered statuses

**Files Modified:**
- `backend/app.py` (lines 16444-16454, 17603-17673, 17508-17530)

---

## Notification Types

| Type | Description | Triggered By |
|------|-------------|--------------|
| `order` | New order received | Buyer places order |
| `order_processing` | Order being processed | Seller marks processing |
| `out_for_delivery` | Order out for delivery | Seller marks ready for pickup |
| `rider_assigned` | Rider assigned to order | Rider accepts order |
| `order_picked_up` | Order picked up by rider | Rider marks picked up |
| `order_delivered` | Order delivered | Rider marks delivered |
| `delivery_completed` | Delivery completed | Buyer confirms receipt |

---

## Real-Time Updates

### Socket.IO Events
- **notification** - Emitted to `user_{user_id}` room when a new notification is created
- **order_available** - Emitted to all active riders when order is ready for pickup

### Event Payload
```json
{
  "message": "Notification message",
  "type": "notification_type",
  "order_id": 123,
  "actor_user_id": 456,
  "images": ["image_url1", "image_url2"]
}
```

---

## Testing Checklist

### Buyer Notifications
- [ ] Buyer receives notification when order is processing
- [ ] Buyer receives notification when order is out for delivery
- [ ] Buyer receives notification when order is delivered
- [ ] Buyer can mark notifications as read
- [ ] Buyer can dismiss notifications
- [ ] Unread count is accurate

### Seller Notifications
- [ ] Seller receives notification when new order is placed
- [ ] Seller receives notification when rider accepts order
- [ ] Seller receives notification when rider picks up order
- [ ] Seller receives notification when order is delivered

### Rider Notifications
- [ ] Rider receives notification when order is assigned
- [ ] Rider receives notification when delivery is completed
- [ ] Rider can mark notifications as read
- [ ] Rider can dismiss notifications
- [ ] Rider sees available orders via Socket.IO

---

## Notes

1. **Seller App:** Currently uses web interface for notifications. A dedicated seller notification screen can be added to the mobile app in the future.

2. **Notification Persistence:** All notifications are persisted in the database, ensuring users can view them even if they were offline when the notification was sent.

3. **Real-Time vs Polling:** The system supports both real-time Socket.IO updates and API polling. Mobile apps can choose either approach based on their requirements.

4. **Error Handling:** All notification calls are wrapped in try-catch blocks to prevent failures from breaking the main order flow.

5. **Multi-Seller Orders:** For orders with items from multiple sellers, all sellers receive a notification when the order is placed.

---

## Summary

The notification system is now fully functional across all roles:
- **Buyers** receive updates on order status changes
- **Sellers** receive new order alerts and delivery updates
- **Riders** receive order assignments and completion notifications

All mobile API endpoints now trigger appropriate notifications, and the mobile screens fetch and display real notification data from the backend.
