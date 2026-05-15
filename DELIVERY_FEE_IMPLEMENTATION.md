# Delivery Fee Calculator Implementation Guide

## Overview
Automatic delivery fee calculator based on province ranking from Laguna using "Incremental Ranking Fee" logic.

## Formula
**Delivery Fee = Province Rank × ₱36**

Examples:
- Laguna (Rank 1) = ₱36 per item
- Rizal (Rank 2) = ₱72 per item  
- Quezon (Rank 3) = ₱108 per item
- Tawi-Tawi (Rank 82) = ₱2,952 per item

## Files Created

### 1. DeliveryFeeService (`lib/services/delivery_fee_service.dart`)
Core service containing:
- All 82 provinces with rankings
- `calculateDeliveryFee(province)` - Calculate fee per item
- `calculateTotalDeliveryFee(province, itemCount)` - Calculate total for multiple items
- `getProvinceRank(province)` - Get province rank
- `getAllProvinces()` - Get sorted province list
- `isValidProvince(province)` - Validate province

### 2. Updated CartProvider (`lib/providers/cart_provider.dart`)
Added:
- `getDeliveryFee(province)` method - Calculate delivery fee from province
- `getGrandTotal(province)` method - Calculate grand total with delivery fee
- No need to store province - passed as parameter from buyer's address

### 3. ProvinceSelector Widget (`lib/widgets/province_selector.dart`)
**Optional widget** - Only use if you want manual province selection
- For this implementation, province is auto-extracted from address
- Widget can be used for address management screens

## How It Works

### For Buyers:
1. **Register with Address**: Buyer registers with complete address including province
   - Example: "123 Main St, Biñan, Laguna"
   - Example: "456 Ortigas Ave, Pasig, Rizal"
2. **Auto-Extract Province**: System automatically detects province from address
3. **Auto-Calculate**: Delivery fee calculated based on:
   - Detected province rank
   - Number of items in cart
4. **Per-Item Fee**: Each item has its own delivery fee
   - Example: 3 items, address contains "Rizal" = 3 × ₱72 = ₱216

### For Riders:
1. **Delivery Completion**: When rider marks order as "delivered"
2. **Earnings**: The delivery fee automatically goes to rider's earnings
3. **Backend Handles**: Server-side logic credits the rider

## Integration Steps

### Step 1: Get Buyer's Address from Profile

```dart
// In checkout screen or cart screen:
final buyerProvider = context.read<BuyerProvider>();
final buyerAddress = buyerProvider.buyer?.address;

// Extract province automatically
final province = DeliveryFeeService.extractProvinceFromAddress(buyerAddress);
```

### Step 2: Calculate Delivery Fee

```dart
// Option 1: Direct from address
final deliveryFee = DeliveryFeeService.calculateTotalDeliveryFeeFromAddress(
  buyerAddress,
  cartProvider.items.length,
);

// Option 2: From extracted province
final deliveryFee = cartProvider.getDeliveryFee(province);
```

### Step 3: Display Delivery Fee in Order Summary

```dart
// Get buyer's address
final buyerAddress = context.read<BuyerProvider>().buyer?.address;
final province = DeliveryFeeService.extractProvinceFromAddress(buyerAddress);
final deliveryFee = cartProvider.getDeliveryFee(province);

// Display in UI
Row(
  mainAxisAlignment: MainAxisAlignment.spaceBetween,
  children: [
    Text('Delivery Fee (${cartProvider.items.length} items to $province)'),
    Text('₱${deliveryFee.toStringAsFixed(2)}'),
  ],
)
```

### Step 4: Calculate Grand Total

```dart
final grandTotal = cartProvider.getGrandTotal(province);

Text(
  '₱${grandTotal.toStringAsFixed(2)}',
  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
)
```

### Step 5: Backend Integration

The backend should:
1. Store buyer's complete address (including province)
2. Extract province from address when creating order
3. Calculate delivery fee server-side
4. Credit delivery fee to rider when order is completed

Example API payload:
```json
{
  "order_id": 123,
  "buyer_address": "123 Main St, Biñan, Laguna",
  "buyer_province": "Laguna",
  "item_count": 3,
  "delivery_fee": 108.00,
  "rider_id": 456
}
```

## Address Format Examples

For proper province detection, addresses should include province name:

✅ **Good Examples:**
- "123 Main Street, Biñan City, Laguna"
- "456 Ortigas Avenue, Pasig City, Rizal"
- "789 Colon Street, Cebu City, Cebu"
- "Unit 5B, Makati Avenue, Makati, Metro Manila" (will default to Laguna)

❌ **Bad Examples:**
- "123 Main Street" (no province)
- "Biñan City" (no province)

**Note:** If no province is detected, system defaults to Laguna rate (₱36/item)

## Province Rankings (All 82 Provinces)

| Rank | Province | Fee/Item |
|------|----------|----------|
| 1 | Laguna | ₱36 |
| 2 | Rizal | ₱72 |
| 3 | Quezon | ₱108 |
| 4 | Batangas | ₱144 |
| 5 | Cavite | ₱180 |
| ... | ... | ... |
| 82 | Tawi-Tawi | ₱2,952 |

(See `delivery_fee_service.dart` for complete list)

## Example Calculations

### Example 1: Single Item to Laguna
- Province: Laguna (Rank 1)
- Items: 1
- Delivery Fee: 1 × ₱36 = **₱36**

### Example 2: Multiple Items to Rizal
- Province: Rizal (Rank 2)
- Items: 5
- Delivery Fee: 5 × ₱72 = **₱360**

### Example 3: Order to Cebu
- Province: Cebu (Rank 45)
- Items: 2
- Delivery Fee: 2 × ₱1,620 = **₱3,240**

## Rider Earnings Flow

1. **Order Placed**: Buyer pays total including delivery fee
2. **Order Accepted**: Rider accepts the delivery
3. **Delivery Complete**: Rider marks as delivered
4. **Earnings Updated**: Delivery fee added to rider's earnings

Backend should track:
```sql
-- Example rider_earnings table
CREATE TABLE rider_earnings (
  id SERIAL PRIMARY KEY,
  rider_id INT,
  order_id INT,
  delivery_fee DECIMAL(10,2),
  province VARCHAR(100),
  item_count INT,
  earned_at TIMESTAMP
);
```

## Testing Checklist

- [ ] Address with "Laguna" calculates ₱36/item
- [ ] Address with "Rizal" calculates ₱72/item
- [ ] Address with "Cebu" calculates ₱1,620/item
- [ ] Multiple items calculate correctly (fee × item count)
- [ ] Address without province defaults to ₱36/item
- [ ] Cart total includes delivery fee
- [ ] Checkout shows correct delivery fee
- [ ] Order confirmation displays delivery fee
- [ ] Rider earnings include delivery fee after completion
- [ ] Province extraction is case-insensitive

## Notes

- Base fee per rank: ₱36
- Total provinces: 82
- Fee range: ₱36 - ₱2,952 per item
- Calculation is automatic and real-time
- Rider gets 100% of delivery fee
