# Rider Earnings System - Complete Fix (Province-Based Delivery Fee)

## Problem
Rider earnings were showing ₱0.00 because:
1. The system was not crediting earnings to the rider's wallet when orders were delivered
2. Earnings were incorrectly calculated as 15% of order total instead of actual delivery fee

## Solution Implemented

### 1. Automatic Delivery Fee Calculation (Checkout Screen)
**File:** `mobile_app/lib/screens/buyer_app/checkout_screen.dart`

**Changes:**
- Integrated `DeliveryFeeService` for automatic province-based delivery fee calculation
- Formula: `Delivery Fee = Province Rank × ₱36 per item`
- Examples:
  - Laguna (Rank 1): ₱36/item → 3 items = ₱108
  - Rizal (Rank 2): ₱72/item → 3 items = ₱216
  - Cebu (Rank 45): ₱1,620/item → 3 items = ₱4,860
  - Tawi-Tawi (Rank 82): ₱2,952/item → 3 items = ₱8,856

**Features:**
- Auto-detects province from buyer's shipping address
- Calculates per-item delivery fee
- Updates automatically when address changes
- Displays province name and rank in order summary
- Delivery fee is saved to order record

### 2. Rider Earnings = Delivery Fee (Backend)
**File:** `backend/app.py`

**Changes:**
- Added automatic earnings credit in `api_rider_mark_delivered()` endpoint
- **Rider earnings = Full delivery fee amount** (NOT percentage)
- Uses existing `credit_wallet()` function
- Logs all transactions for audit trail

**Code Added:**
```python
# Credit rider earnings (delivery fee based on province ranking)
try:
    # Get delivery fee from order (calculated during checkout based on province)
    delivery_fee = float(order.get('delivery_fee', 0)) or float(order.get('shipping_fee', 0))
    if delivery_fee > 0:
        credit_wallet(
            user_id=request.current_user_id,
            amount=delivery_fee,
            source='order_delivery',
            order_id=order_id
        )
        app.logger.info(f"Credited ₱{delivery_fee:.2f} delivery fee to rider {request.current_user_id} for order {order_id}")
    else:
        app.logger.warning(f"No delivery fee found for order {order_id}")
except Exception as e:
    app.logger.error(f"Failed to credit rider earnings: {e}")
```

### 3. Database Schema Updates
**File:** `backend/app.py`

**Changes:**
- Added `delivery_fee` column to Order table
- Added `shipping_fee` column to Order table
- Migration runs automatically on server start

```python
if 'delivery_fee' not in cols:
    stmts.append("ALTER TABLE \"order\" ADD COLUMN delivery_fee FLOAT DEFAULT 0.0")
if 'shipping_fee' not in cols:
    stmts.append("ALTER TABLE \"order\" ADD COLUMN shipping_fee FLOAT DEFAULT 0.0")
```

### 4. Checkout API Updates
**Files:** 
- `backend/app.py` - API endpoint
- `mobile_app/lib/services/buyer_service.dart` - Service layer
- `mobile_app/lib/providers/buyer_provider.dart` - Provider layer

**Changes:**
- Added `delivery_fee` parameter to checkout request
- Saves delivery_fee to order record
- Includes delivery_fee in grand total calculation

## How It Works

### Order Flow with Earnings:

1. **Buyer Checkout**
   - System detects province from shipping address (e.g., "Laguna")
   - Calculates delivery fee: `Province Rank × ₱36 × Item Count`
   - Example: Laguna (Rank 1) × ₱36 × 3 items = ₱108
   - Displays in order summary
   - Total = Subtotal - Discount + Shipping Fee (₱10) + Delivery Fee (₱108)
   - **Delivery fee saved to order.delivery_fee column**

2. **Rider Accepts Order**
   - Order assigned to rider
   - Status: `to_ship` → `picked_up` → `out_for_delivery`

3. **Rider Marks as Delivered**
   - Status changes to `delivered`
   - **Automatic earnings credit:** Full delivery fee amount (₱108)
   - Transaction recorded in `wallet_transaction` table
   - Source: `order_delivery`

4. **Rider Dashboard**
   - Earnings immediately visible
   - Shows: Total, Today, Week, Month
   - Pulls from `wallet_transaction` table

## Earnings Calculation Examples

### Example 1: Order to Laguna
- Items: 3 products
- Subtotal: ₱1,500
- Province: Laguna (Rank 1)
- Delivery Fee: 3 × ₱36 = ₱108
- Shipping Fee: ₱10
- **Total Order:** ₱1,618
- **Rider Earnings:** ₱108 (full delivery fee)

### Example 2: Order to Rizal
- Items: 5 products
- Subtotal: ₱3,000
- Province: Rizal (Rank 2)
- Delivery Fee: 5 × ₱72 = ₱360
- Shipping Fee: ₱10
- **Total Order:** ₱3,370
- **Rider Earnings:** ₱360 (full delivery fee)

### Example 3: Order to Cebu
- Items: 2 products
- Subtotal: ₱2,500
- Province: Cebu (Rank 45)
- Delivery Fee: 2 × ₱1,620 = ₱3,240
- Shipping Fee: ₱10
- **Total Order:** ₱5,750
- **Rider Earnings:** ₱3,240 (full delivery fee)

## Database Schema

### Order Table (Updated)
```sql
ALTER TABLE "order" ADD COLUMN delivery_fee FLOAT DEFAULT 0.0;
ALTER TABLE "order" ADD COLUMN shipping_fee FLOAT DEFAULT 0.0;
```

### WalletTransaction Table
```sql
CREATE TABLE wallet_transaction (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    order_id INT,
    amount FLOAT NOT NULL,  -- Full delivery fee amount
    type VARCHAR(20) DEFAULT 'credit',
    source VARCHAR(50),  -- 'order_delivery'
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### Checkout (Updated)
```
POST /api/v1/buyer/checkout
Authorization: Bearer {token}

Request:
{
  "recipient_name": "Juan Dela Cruz",
  "recipient_phone": "09123456789",
  "shipping_address": "123 Main St, Biñan, Laguna",
  "payment_method": "cod",
  "shipping_fee": 10.0,
  "delivery_fee": 108.0,  // NEW: Province-based delivery fee
  "selected_items": [1, 2, 3]
}
```

### Get Rider Earnings
```
GET /api/v1/rider/earnings
Authorization: Bearer {token}

Response:
{
  "success": true,
  "total": 1500.50,
  "today": 108.00,
  "week": 850.00,
  "month": 1500.50
}
```

### Mark Order as Delivered (Updated)
```
POST /api/v1/rider/orders/{order_id}/mark-delivered
Authorization: Bearer {token}

Response:
{
  "success": true,
  "message": "Order marked as delivered successfully",
  "order": {
    "id": 123,
    "status": "delivered"
  }
}

// Backend automatically credits delivery_fee to rider wallet
```

## Testing Checklist

- [x] Delivery fee calculates correctly based on province
- [x] Delivery fee updates when address changes
- [x] Rider earnings credited when order marked as delivered
- [x] Earnings visible in rider dashboard immediately
- [x] Wallet transactions logged correctly
- [x] Multiple deliveries accumulate earnings
- [x] Today/Week/Month filters work correctly

## Files Modified

1. `mobile_app/lib/screens/buyer_app/checkout_screen.dart`
   - Added DeliveryFeeService import
   - Added `_deliveryFee` and `_detectedProvince` variables
   - Added `_calculateDeliveryFee()` method
   - Updated order summary to show delivery fee with province info

2. `backend/app.py`
   - Added rider earnings credit in `api_rider_mark_delivered()`
   - Uses existing `credit_wallet()` function
   - Logs all earnings transactions

## Province Ranking System (All 82 Provinces)

| Rank | Province | Fee/Item |
|------|----------|----------|
| 1 | Laguna | ₱36 |
| 2 | Rizal | ₱72 |
| 3 | Quezon | ₱108 |
| 4 | Batangas | ₱144 |
| 5 | Cavite | ₱180 |
| ... | ... | ... |
| 45 | Cebu | ₱1,620 |
| ... | ... | ... |
| 82 | Tawi-Tawi | ₱2,952 |

See `mobile_app/lib/services/delivery_fee_service.dart` for complete list.

## Notes

- Earnings are credited immediately upon delivery confirmation
- No manual intervention required
- All transactions are logged for audit
- Earnings are cumulative and never expire
- System uses existing wallet infrastructure
- Compatible with future payout features

## Future Enhancements

1. **Payout System**
   - Allow riders to request payouts
   - Admin approval workflow
   - Payment method selection (GCash, Bank Transfer)

2. **Earnings Breakdown**
   - Show per-order earnings history
   - Filter by date range
   - Export to CSV

3. **Performance Bonuses**
   - Bonus for completing X deliveries per day
   - Rating-based bonuses
   - Peak hour multipliers

4. **Real-time Updates**
   - WebSocket notifications for new earnings
   - Push notifications on delivery completion
   - Live earnings counter

---

**Status:** ✅ COMPLETE AND TESTED
**Date:** 2025-01-XX
**Developer:** Amazon Q
