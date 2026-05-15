# Rider Flow Simplified - No Pickup Confirmation

## Changes Made

### Old Flow:
1. Rider accepts order → status: `to_ship`
2. Rider confirms pickup → status: `in_transit`
3. Rider marks delivered → status: `delivered`

### New Flow:
1. Rider accepts order → status: `in_transit` (auto-pickup)
2. Rider marks delivered → status: `delivered`

## What Changed

**File:** `app.py` - Both accept-order endpoints

**Before:**
```python
order.status = 'to_ship'
order.rider_id = rider_id
order.rider_earnings = rider_earnings
```

**After:**
```python
order.status = 'in_transit'
order.rider_id = rider_id
order.picked_up_by = rider_id
order.picked_up_at = datetime.utcnow()
order.rider_earnings = rider_earnings
```

## Benefits

1. **Faster workflow** - One less step for riders
2. **Automatic assignment** - Seller sees rider assigned immediately
3. **Clearer status** - Order goes straight to "Out for Delivery"
4. **Better UX** - Rider just needs to accept and deliver

## Mobile App Impact

The mobile app should now:
- Show "Mark as Delivered" button immediately after accepting
- Skip the "Confirm Pickup" screen
- Display order as "In Transit" right after acceptance

## Testing

1. Rider accepts order
2. Check order status = `in_transit`
3. Check `picked_up_by` and `picked_up_at` are set
4. Seller sees rider assigned
5. Next action: Mark as Delivered
