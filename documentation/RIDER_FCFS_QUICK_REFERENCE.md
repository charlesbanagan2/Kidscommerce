# Rider FCFS Quick Reference Card

## 🚀 Quick Implementation Steps

### Backend (5 minutes)

1. **Add to app.py** (after your existing routes):
```python
# Copy all code from rider_api.py
```

2. **Update seller order status endpoint**:
```python
if new_status == 'ready_for_pickup':
    order.status = 'ready_for_pickup'
    db.session.commit()
    broadcast_new_order_available(order_id)  # Add this line
```

3. **Verify Order model has rider_id**:
```python
rider_id = db.Column(db.Integer, db.ForeignKey('user.id'))
```

### Mobile App (10 minutes)

1. **Add dependency** to `pubspec.yaml`:
```yaml
socket_io_client: ^2.0.0
```

2. **Copy files**:
   - `rider_service.dart` → `lib/services/`
   - `rider_available_orders_screen.dart` → `lib/screens/rider/`

3. **Add to rider dashboard**:
```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => const RiderAvailableOrdersScreen(),
  ),
);
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rider/available-orders` | Get all orders ready for pickup |
| POST | `/api/rider/accept-order` | Accept order (FCFS logic) |
| GET | `/api/rider/my-deliveries` | Get rider's deliveries |
| POST | `/api/rider/complete-delivery` | Mark delivery as completed |

---

## 🔄 Order Status Flow

```
pending → processing → ready_for_pickup → in_transit → delivered → completed
                              ↑                ↑
                         (Seller)         (Rider)
```

---

## 🎯 FCFS Logic (Race Condition Prevention)

```python
# Backend uses row-level locking
order = db.session.query(Order).filter(
    Order.id == order_id
).with_for_update().first()  # 🔒 Lock acquired

if order.status != 'ready_for_pickup':
    return 409  # Already taken

order.status = 'in_transit'
order.rider_id = rider_id
db.session.commit()  # 🔓 Lock released
```

**Result**: Only ONE rider can accept the order, even if 100 riders click at the same time!

---

## 📱 Socket.IO Events

### Backend Emits:
- `new_order_available` → All riders (when seller marks ready)
- `order_taken` → All riders (when rider accepts)
- `order_accepted_by_rider` → Buyer (when rider accepts)

### Mobile Listens:
```dart
RiderService.initializeSocket(
  accessToken,
  onNewOrderAvailable: (data) => addOrderToList(data),
  onOrderTaken: (orderId) => removeOrderFromList(orderId),
);
```

---

## ✅ Testing Checklist

- [ ] Seller marks order as "Ready for Pickup"
- [ ] Order appears on all riders' screens instantly
- [ ] Rider A accepts order → Success
- [ ] Order disappears from all other riders' screens
- [ ] Rider B tries to accept → Error: "Already taken"
- [ ] Buyer receives notification
- [ ] Rider completes delivery
- [ ] Order status updates to "delivered"

---

## 🐛 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Orders not appearing | Check Socket.IO connection |
| Multiple riders accepting | Verify `with_for_update()` is used |
| Socket.IO not connecting | Check CORS settings |
| 401 Unauthorized | Verify JWT token is valid |

---

## 🔐 Security Features

✅ JWT authentication required
✅ Role-based access control (riders only)
✅ Database transaction locking
✅ Status validation
✅ Approved riders only

---

## 📊 Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (missing data) |
| 401 | Unauthorized (no token) |
| 403 | Forbidden (not a rider) |
| 404 | Order not found |
| 409 | Conflict (order already taken) |
| 500 | Server error |

---

## 🎨 UI Flow

```
Available Orders Screen
  ↓
[Order Card] → Click "Accept"
  ↓
Loading...
  ↓
Success? → Move to "My Deliveries"
  ↓
Conflict? → Show "Already taken" + Remove from list
  ↓
Error? → Show error message
```

---

## 💡 Pro Tips

1. **Always use `with_for_update()`** for FCFS logic
2. **Test with 2+ riders** to verify race condition handling
3. **Monitor Socket.IO logs** for real-time debugging
4. **Use pull-to-refresh** for manual order list updates
5. **Show clear error messages** when order is taken

---

## 📞 Support

If you encounter issues:
1. Check backend logs for errors
2. Verify Socket.IO connection in mobile logs
3. Test API endpoints with Postman
4. Ensure database supports row-level locking

---

## 🎉 Success Criteria

✅ Orders appear in real-time
✅ Only one rider can accept each order
✅ Clear error messages for conflicts
✅ Buyer receives notifications
✅ Smooth user experience

**You're ready to go! 🚀**
