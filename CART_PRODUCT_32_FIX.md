# Fix: Product ID 32 Hindi Ma-add to Cart (404 Error)

## Problema
- Product ID 32 (Play-Doh Classic 4 Pack) ayaw ma-add to cart
- Nakikita sa log: `POST /api/v1/buyer/cart HTTP/1.1" 404`
- Product existing naman sa database at may stock pa (50 units)

## Root Cause
**Status Mismatch:**
- Ang product status sa database: `approved`
- Ang code nag-check ng: `active`
- Kaya kahit existing ang product, nag-return ng 404 "Product not found"

### Code na May Bug (Before):
```python
product = get_data_by_id('product', product_id)
if not product or product.get('status') != 'active':  # ❌ Mali!
    return jsonify({'error': 'Product not found'}), 404
```

### Fixed Code (After):
```python
product = get_data_by_id('product', product_id)
if not product or product.get('status') != 'approved':  # ✅ Tama!
    return jsonify({'error': 'Product not found'}), 404
```

## Solusyon
Pinalitan ang lahat ng status checks mula `'active'` to `'approved'` sa:
1. `/api/v1/buyer/cart` POST endpoint (add to cart)
2. `/api/v1/buyer/cart` GET endpoint (view cart)
3. `/api/v1/buyer/cart/<item_id>` PUT endpoint (update quantity)
4. `/api/v1/cart` endpoints
5. Checkout endpoints

**Total: 7 occurrences fixed**

## Files Modified
- `backend/app.py` - Fixed all product status checks

## Testing

### Manual Test:
```bash
cd backend
python test_cart_fix.py
```

### Expected Result:
```json
{
  "success": true,
  "message": "Item added to cart",
  "cart_item": {
    "id": <cart_item_id>,
    "product_id": 32,
    "product_name": "Play-Doh Classic 4 Pack Assorted Color",
    "price": 150.0,
    "quantity": 1,
    "stock": 50,
    "subtotal": 150.0
  }
}
```

## Important: Restart Server
**Kailangan i-restart ang Flask server para mag-take effect ang changes!**

```bash
# Stop current server (Ctrl+C)
# Then restart:
python app.py
```

## Verification
After restart, try adding product 32 to cart from mobile app:
1. Open product ID 32 (Play-Doh)
2. Click "Add to Cart"
3. Should now work without 404 error

## Product 32 Details
```
ID: 32
Name: Play-Doh Classic 4 Pack Assorted Color
Price: ₱150.00
Stock: 50 units
Status: approved ✓
Seller ID: 14
```

## Related Endpoints Fixed
- `POST /api/v1/buyer/cart` - Add to cart
- `GET /api/v1/buyer/cart` - View cart items
- `PUT /api/v1/buyer/cart/<item_id>` - Update cart quantity
- `POST /api/v1/buyer/cart/clear` - Clear cart
- Checkout endpoints that validate product status

---
**Status:** ✅ FIXED
**Date:** May 20, 2026
**Fix Applied By:** FIX_CART_STATUS_CHECK.py
