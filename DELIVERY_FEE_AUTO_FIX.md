# DELIVERY FEE FIX - AUTOMATIC PROVINCE DETECTION

## Problema
- Lahat ng orders ay may ₱36 delivery fee kahit iba-iba ang province
- Order #52 sa Cavite ay dapat ₱180 (rank 5 × ₱36) pero ₱36 pa rin

## Solusyon
1. **Updated `province_delivery_fees.py`**
   - Added `extract_province_from_address()` - extracts province from address string
   - Added `calculate_delivery_fee_from_address()` - calculates fee directly from address
   - Added city-to-province mapping for better detection

2. **Updated `app.py`**
   - Changed `/api/v1/rider/available-orders` endpoint
   - Now calculates delivery fee dynamically from shipping address
   - Added logging to show: Address → Province → Fee

3. **Updated `rider_available_orders_screen.dart`**
   - Removed total price display (privacy)
   - Shows only "Delivery Fee" badge
   - Uses backend-calculated fee

## How It Works
```
Address: "123 Main St, Imus, Cavite"
  ↓
Extract Province: "Cavite"
  ↓
Get Rank: 5
  ↓
Calculate: 5 × ₱36 = ₱180
```

## Province Detection
1. Checks for exact province name (e.g., "Cavite", "Laguna")
2. Checks for city/municipality name (e.g., "Imus" → Cavite)
3. Checks for abbreviations (e.g., "NCR" → Laguna)
4. Defaults to ₱36 (Laguna) if not found

## Testing
1. Restart backend: `python app.py`
2. Refresh mobile app
3. Check logs for: `Order #XX: Address='...' -> Province='...' -> Fee=₱XXX`

## Expected Results
- Order #52 (Cavite): ₱180
- Order sa Laguna: ₱36
- Order sa Rizal: ₱72
- Order sa Quezon: ₱108
- etc.
