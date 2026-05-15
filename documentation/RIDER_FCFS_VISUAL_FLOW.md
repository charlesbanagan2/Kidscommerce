# Rider FCFS System - Visual Flow Diagram

## 🎯 Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SELLER DASHBOARD                             │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Order #123: Processing                                     │    │
│  │  [Mark as Ready for Pickup] ← Seller clicks this           │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FLASK BACKEND                                │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  1. Update order.status = 'ready_for_pickup'               │    │
│  │  2. db.session.commit()                                     │    │
│  │  3. broadcast_new_order_available(order_id)                │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         SOCKET.IO SERVER                             │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  emit('new_order_available', {                             │    │
│  │    order_id: 123,                                           │    │
│  │    buyer_name: "John Doe",                                  │    │
│  │    delivery_address: "123 Main St",                         │    │
│  │    total_amount: 1500.00                                    │    │
│  │  }) → room='riders'                                         │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                    │                │                │
                    ▼                ▼                ▼
        ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
        │   RIDER A     │  │   RIDER B     │  │   RIDER C     │
        │   (Mobile)    │  │   (Mobile)    │  │   (Mobile)    │
        └───────────────┘  └───────────────┘  └───────────────┘
                │                │                │
                ▼                ▼                ▼
        Order #123       Order #123       Order #123
        appears ✅       appears ✅       appears ✅
```

---

## 🏁 FCFS Race Condition Scenario

### Timeline: Multiple Riders Click "Accept" Simultaneously

```
Time    Rider A                     Rider B                     Backend
────────────────────────────────────────────────────────────────────────
T0      Sees Order #123             Sees Order #123             status: ready_for_pickup
        [Accept] button             [Accept] button             rider_id: NULL

T1      Clicks "Accept" ──────────────────────────────────────→ POST /api/rider/accept-order
                                                                 🔒 Lock row (with_for_update)
                                                                 Read: status = ready_for_pickup ✅

T2                                  Clicks "Accept" ──────────→ POST /api/rider/accept-order
                                                                 ⏳ WAITING for lock...

T3                                                               Update: status = in_transit
                                                               Update: rider_id = A
                                                               Commit ✅
                                                               🔓 Release lock

T4      ✅ Success!                                             emit('order_taken', {order_id: 123})
        Order moved to                                          → room='riders'
        "My Deliveries"

T5                                  Order disappears ❌         🔒 Lock row (with_for_update)
                                    (via Socket.IO)             Read: status = in_transit ❌

T6                                  If still clicks:            Check: status != ready_for_pickup
                                    ❌ "Already taken"          Rollback
                                                               Return: HTTP 409 Conflict
                                                               🔓 Release lock

T7                                  ❌ Error toast
                                    Order removed
```

---

## 🔐 Database Transaction Flow

### Successful Accept (Rider A)

```
┌─────────────────────────────────────────────────────────────┐
│  BEGIN TRANSACTION                                           │
│                                                              │
│  1. SELECT * FROM order                                      │
│     WHERE id = 123                                           │
│     FOR UPDATE;  ← 🔒 EXCLUSIVE LOCK                        │
│                                                              │
│  2. IF order.status == 'ready_for_pickup':                  │
│       ✅ Condition met                                       │
│                                                              │
│  3. UPDATE order                                             │
│     SET status = 'in_transit',                              │
│         rider_id = A,                                        │
│         picked_up_at = NOW()                                 │
│     WHERE id = 123;                                          │
│                                                              │
│  4. COMMIT;  ← 🔓 RELEASE LOCK                              │
│                                                              │
│  Result: HTTP 200 OK                                         │
└─────────────────────────────────────────────────────────────┘
```

### Failed Accept (Rider B)

```
┌─────────────────────────────────────────────────────────────┐
│  BEGIN TRANSACTION                                           │
│                                                              │
│  1. SELECT * FROM order                                      │
│     WHERE id = 123                                           │
│     FOR UPDATE;  ← ⏳ WAIT for Rider A's lock...           │
│                  ← 🔒 LOCK ACQUIRED (after A commits)       │
│                                                              │
│  2. IF order.status == 'ready_for_pickup':                  │
│       ❌ Condition NOT met (status = 'in_transit')          │
│                                                              │
│  3. ROLLBACK;  ← 🔓 RELEASE LOCK                            │
│                                                              │
│  Result: HTTP 409 CONFLICT                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📱 Mobile App State Management

### Available Orders Screen State Flow

```
┌─────────────────────────────────────────────────────────────┐
│  INITIAL STATE                                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │  _availableOrders = []                             │    │
│  │  _isLoading = true                                  │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  LOADING STATE                                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │  GET /api/rider/available-orders                   │    │
│  │  Show: CircularProgressIndicator                    │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  LOADED STATE                                                │
│  ┌────────────────────────────────────────────────────┐    │
│  │  _availableOrders = [Order #123, Order #124]      │    │
│  │  _isLoading = false                                 │    │
│  │  Show: ListView with order cards                    │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  REAL-TIME UPDATE (Socket.IO)                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │  onNewOrderAvailable: (data) {                     │    │
│  │    setState(() {                                    │    │
│  │      _availableOrders.insert(0, data);             │    │
│  │    });                                              │    │
│  │  }                                                  │    │
│  │                                                     │    │
│  │  onOrderTaken: (orderId) {                         │    │
│  │    setState(() {                                    │    │
│  │      _availableOrders.removeWhere(                 │    │
│  │        (order) => order['id'] == orderId           │    │
│  │      );                                             │    │
│  │    });                                              │    │
│  │  }                                                  │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  ACCEPT ORDER FLOW                                           │
│  ┌────────────────────────────────────────────────────┐    │
│  │  1. User clicks "Accept Order"                     │    │
│  │  2. Show loading dialog                             │    │
│  │  3. POST /api/rider/accept-order                   │    │
│  │  4. Close loading dialog                            │    │
│  │                                                     │    │
│  │  IF success:                                        │    │
│  │    ✅ Remove from _availableOrders                 │    │
│  │    ✅ Show success toast                           │    │
│  │    ✅ Navigate to "My Deliveries"                  │    │
│  │                                                     │    │
│  │  IF conflict (409):                                 │    │
│  │    ❌ Remove from _availableOrders                 │    │
│  │    ❌ Show "Already taken" toast                   │    │
│  │                                                     │    │
│  │  IF error:                                          │    │
│  │    ❌ Show error toast                             │    │
│  │    ❌ Keep in list (retry possible)                │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Order Lifecycle

```
┌──────────────┐
│   PENDING    │  ← Buyer places order
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PROCESSING  │  ← Seller confirms order
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ READY_FOR_PICKUP     │  ← Seller marks ready
│ (Visible to riders)  │     🔔 Broadcast to all riders
└──────┬───────────────┘
       │
       ▼
┌──────────────┐
│  IN_TRANSIT  │  ← Rider accepts order
│              │     🔒 FCFS lock prevents duplicates
└──────┬───────┘     🔔 Notify buyer
       │
       ▼
┌──────────────┐
│  DELIVERED   │  ← Rider marks delivered
└──────┬───────┘     🔔 Notify buyer to confirm
       │
       ▼
┌──────────────┐
│  COMPLETED   │  ← Buyer confirms receipt
└──────────────┘     💰 Release commissions
```

---

## 🎭 User Experience Flow

### Rider's Perspective

```
┌─────────────────────────────────────────────────────────────┐
│  1. Open "Available Orders" screen                           │
│     ┌──────────────────────────────────────────────┐        │
│     │  🔄 Loading...                                │        │
│     └──────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. See available orders                                     │
│     ┌──────────────────────────────────────────────┐        │
│     │  📦 Order #123                                │        │
│     │  👤 John Doe                                  │        │
│     │  📍 123 Main St                               │        │
│     │  💰 ₱1,500.00                                 │        │
│     │  [Accept Order]                               │        │
│     └──────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Click "Accept Order"                                     │
│     ┌──────────────────────────────────────────────┐        │
│     │  ⏳ Accepting order...                        │        │
│     └──────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  4a. SUCCESS                                                 │
│     ┌──────────────────────────────────────────────┐        │
│     │  ✅ Order accepted!                           │        │
│     │  Check "My Deliveries" tab                    │        │
│     └──────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  4b. CONFLICT (Another rider was faster)                     │
│     ┌──────────────────────────────────────────────┐        │
│     │  ❌ Order already taken by another rider      │        │
│     │  (Order disappears from list)                 │        │
│     └──────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

1. **FCFS = First Come First Served**
   - Database row-level locking ensures fairness
   - Only ONE rider can accept each order
   - No race conditions possible

2. **Real-Time = Instant Updates**
   - Socket.IO broadcasts to all riders
   - Orders appear/disappear automatically
   - No manual refresh needed

3. **User-Friendly = Clear Feedback**
   - Loading states during operations
   - Success/error messages
   - Automatic list updates

4. **Production-Ready = Battle-Tested**
   - Transaction safety
   - Error handling
   - Scalable architecture

---

**This is the complete visual guide to understanding the Rider FCFS system!** 🎉
