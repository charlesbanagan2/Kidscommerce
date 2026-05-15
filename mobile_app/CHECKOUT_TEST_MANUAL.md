# Checkout Functionality - Manual Test Checklist

## Test Environment Setup
- [ ] Backend server running on `http://192.168.100.46:5000`
- [ ] Mobile app running on device/emulator
- [ ] Test user logged in (buyer@test.com / buyer123)
- [ ] At least 2 products in cart

---

## Test Case 1: Checkout WITHOUT Coupon ✅

### Steps:
1. **Add Products to Cart**
   - [ ] Open app and browse products
   - [ ] Add 2-3 products to cart
   - [ ] Verify cart badge shows correct count
   - [ ] Navigate to Cart screen

2. **Review Cart**
   - [ ] Verify all items are displayed
   - [ ] Check quantities are correct
   - [ ] Verify prices are accurate
   - [ ] Check subtotal calculation
   - [ ] Click "Slide for Checkout"

3. **Checkout Screen - No Coupon**
   - [ ] Verify cart items are listed
   - [ ] Check shipping address is pre-filled
   - [ ] Verify phone number is pre-filled
   - [ ] Select payment method: COD
   - [ ] **DO NOT enter any coupon code**
   - [ ] Leave coupon field EMPTY

4. **Order Summary - No Coupon**
   - [ ] Verify Subtotal is correct
   - [ ] **Verify Discount row is NOT shown** (important!)
   - [ ] Verify Shipping Fee is shown (₱10.00)
   - [ ] Verify Total = Subtotal + Shipping Fee
   - [ ] Example: ₱500 + ₱10 = ₱510

5. **Place Order**
   - [ ] Click "Checkout" button
   - [ ] Wait for processing
   - [ ] Verify success message appears
   - [ ] Verify redirected to Order Confirmation screen
   - [ ] Note the Order ID

6. **Verify Order Created**
   - [ ] Navigate to Orders screen
   - [ ] Find the order by Order ID
   - [ ] Verify order status is "Pending" or "To Pay"
   - [ ] Verify order total matches
   - [ ] Verify no discount applied

### Expected Results:
✅ Order created successfully WITHOUT coupon
✅ Discount row NOT displayed in summary
✅ Total = Subtotal + Shipping Fee (no discount)
✅ Order appears in Orders list

---

## Test Case 2: Checkout WITH Coupon ✅

### Steps:
1. **Add Products to Cart**
   - [ ] Add 2-3 products to cart (different from Test 1)
   - [ ] Navigate to Cart screen
   - [ ] Click "Slide for Checkout"

2. **Checkout Screen - With Coupon**
   - [ ] Verify cart items are listed
   - [ ] Check shipping address is pre-filled
   - [ ] Select payment method: GCash
   - [ ] **Enter coupon code in field**
   - [ ] Click "Apply" button

3. **Coupon Application**
   - [ ] Verify success message: "Coupon applied successfully"
   - [ ] Check if discount appears in Order Summary
   - [ ] Verify discount amount is correct

4. **Order Summary - With Coupon**
   - [ ] Verify Subtotal is correct
   - [ ] **Verify Discount row IS shown** (important!)
   - [ ] Verify discount amount in green
   - [ ] Verify Shipping Fee is shown
   - [ ] Verify Total = Subtotal - Discount + Shipping Fee
   - [ ] Example: ₱500 - ₱50 + ₱10 = ₱460

5. **Place Order**
   - [ ] Click "Checkout" button
   - [ ] Wait for processing
   - [ ] Verify success message appears
   - [ ] Verify redirected to Order Confirmation screen
   - [ ] Note the Order ID

6. **Verify Order Created**
   - [ ] Navigate to Orders screen
   - [ ] Find the order by Order ID
   - [ ] Verify order status is "Pending" or "To Pay"
   - [ ] Verify order total includes discount
   - [ ] Verify discount was applied

### Expected Results:
✅ Coupon applied successfully
✅ Discount row DISPLAYED in summary
✅ Total = Subtotal - Discount + Shipping Fee
✅ Order created with discount applied

---

## Test Case 3: Invalid Coupon Code ❌

### Steps:
1. **Add Products to Cart**
   - [ ] Add products to cart
   - [ ] Navigate to Checkout screen

2. **Try Invalid Coupon**
   - [ ] Enter invalid coupon code: "INVALID123"
   - [ ] Click "Apply" button

3. **Verify Error Handling**
   - [ ] Verify error message appears
   - [ ] Verify discount is NOT applied
   - [ ] Verify order summary shows no discount
   - [ ] Verify can still checkout without coupon

4. **Complete Checkout**
   - [ ] Click "Checkout" button (without valid coupon)
   - [ ] Verify order is created successfully
   - [ ] Verify no discount applied

### Expected Results:
✅ Error message for invalid coupon
✅ Checkout still works without valid coupon
✅ Order created successfully

---

## Test Case 4: Empty Coupon Field ✅

### Steps:
1. **Add Products to Cart**
   - [ ] Add products to cart
   - [ ] Navigate to Checkout screen

2. **Leave Coupon Field Empty**
   - [ ] **DO NOT enter anything in coupon field**
   - [ ] **DO NOT click Apply button**
   - [ ] Proceed directly to checkout

3. **Order Summary**
   - [ ] Verify Discount row is NOT shown
   - [ ] Verify Total = Subtotal + Shipping Fee

4. **Place Order**
   - [ ] Click "Checkout" button
   - [ ] Verify order is created successfully

### Expected Results:
✅ Checkout works with empty coupon field
✅ No discount applied
✅ Order created successfully

---

## Test Case 5: Different Payment Methods 💳

### Test with COD:
- [ ] Add products to cart
- [ ] Select payment method: Cash on Delivery
- [ ] Complete checkout (no coupon)
- [ ] Verify order created with COD payment method

### Test with GCash:
- [ ] Add products to cart
- [ ] Select payment method: GCash
- [ ] Complete checkout (no coupon)
- [ ] Verify order created with GCash payment method

### Test with Card:
- [ ] Add products to cart
- [ ] Select payment method: Card
- [ ] Complete checkout (no coupon)
- [ ] Verify order created with Card payment method

### Expected Results:
✅ All payment methods work
✅ Checkout succeeds regardless of payment method
✅ Payment method saved correctly in order

---

## Test Case 6: Required Fields Validation ⚠️

### Test Missing Name:
- [ ] Clear recipient name field
- [ ] Try to checkout
- [ ] Verify error: "Please fill in all required fields"

### Test Missing Phone:
- [ ] Clear phone number field
- [ ] Try to checkout
- [ ] Verify error: "Please fill in all required fields"

### Test Missing Address:
- [ ] Clear shipping address field
- [ ] Try to checkout
- [ ] Verify error: "Please fill in all required fields"

### Expected Results:
✅ Validation prevents checkout with missing fields
✅ Error messages are clear
✅ User can correct and retry

---

## Test Case 7: Cart Clearing After Checkout 🛒

### Steps:
1. **Before Checkout**
   - [ ] Note number of items in cart
   - [ ] Note cart total

2. **Complete Checkout**
   - [ ] Complete checkout successfully
   - [ ] Wait for confirmation screen

3. **Check Cart After Checkout**
   - [ ] Navigate back to Cart screen
   - [ ] Verify cart is EMPTY
   - [ ] Verify cart badge shows 0
   - [ ] Verify "Your cart is empty" message

### Expected Results:
✅ Cart is cleared after successful checkout
✅ Cart count resets to 0
✅ Empty cart message displayed

---

## Test Case 8: Multiple Orders 📦

### Steps:
1. **Create First Order**
   - [ ] Add products to cart
   - [ ] Checkout WITHOUT coupon
   - [ ] Note Order ID #1

2. **Create Second Order**
   - [ ] Add different products to cart
   - [ ] Checkout WITH coupon
   - [ ] Note Order ID #2

3. **Verify Both Orders**
   - [ ] Navigate to Orders screen
   - [ ] Verify both orders are listed
   - [ ] Verify Order #1 has no discount
   - [ ] Verify Order #2 has discount
   - [ ] Verify totals are different

### Expected Results:
✅ Multiple orders can be created
✅ Each order maintains its own discount status
✅ All orders appear in Orders list

---

## Test Case 9: Notes Field (Optional) 📝

### Test Without Notes:
- [ ] Add products to cart
- [ ] Leave notes field EMPTY
- [ ] Complete checkout
- [ ] Verify order created successfully

### Test With Notes:
- [ ] Add products to cart
- [ ] Enter notes: "Please deliver in the morning"
- [ ] Complete checkout
- [ ] Verify order created successfully
- [ ] Check if notes are saved (if visible in order details)

### Expected Results:
✅ Notes field is optional
✅ Checkout works with or without notes
✅ Notes are saved when provided

---

## Test Case 10: Available Coupons List 🎟️

### Steps:
1. **Navigate to Checkout**
   - [ ] Add products to cart
   - [ ] Go to Checkout screen

2. **View Available Coupons**
   - [ ] Expand "Available Coupons" section
   - [ ] Verify list of coupons is displayed
   - [ ] Note coupon codes and descriptions

3. **Select Coupon from List**
   - [ ] Tap on a coupon from the list
   - [ ] Verify coupon code is auto-filled in field
   - [ ] Click "Apply" button
   - [ ] Verify coupon is applied

4. **Complete Checkout**
   - [ ] Verify discount is shown
   - [ ] Complete checkout
   - [ ] Verify order created with discount

### Expected Results:
✅ Available coupons are listed
✅ Tapping coupon auto-fills code
✅ Coupon can be applied and used

---

## Summary Checklist ✅

### Core Functionality:
- [ ] Checkout works WITHOUT coupon
- [ ] Checkout works WITH coupon
- [ ] Discount row hidden when no coupon
- [ ] Discount row shown when coupon applied
- [ ] Total calculation correct in both cases
- [ ] All payment methods work
- [ ] Required fields validated
- [ ] Cart cleared after checkout
- [ ] Orders created successfully

### Edge Cases:
- [ ] Invalid coupon handled gracefully
- [ ] Empty coupon field works
- [ ] Notes field is optional
- [ ] Multiple orders can be created
- [ ] Available coupons list works

---

## Test Results Summary

**Date:** _______________
**Tester:** _______________
**App Version:** _______________
**Backend Version:** _______________

### Test Results:
- Total Tests: 10
- Passed: _____ / 10
- Failed: _____ / 10
- Blocked: _____ / 10

### Issues Found:
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### Notes:
_______________________________________________
_______________________________________________
_______________________________________________

---

## Quick Test Commands

### Run Unit Tests:
```bash
cd mobile_app
flutter test test/checkout_test.dart
```

### Run All Tests:
```bash
cd mobile_app
flutter test
```

### Check Test Coverage:
```bash
cd mobile_app
flutter test --coverage
```

---

## Expected Test Results:

✅ **ALL TESTS SHOULD PASS**

The checkout functionality is designed to work seamlessly with or without coupons. The key points:

1. **No Coupon**: `couponId` = `null`, discount = 0.0
2. **With Coupon**: `couponId` = actual ID, discount > 0
3. **Empty Field**: Treated same as no coupon
4. **Invalid Coupon**: Error shown, checkout still works
5. **All Payment Methods**: Work regardless of coupon status

---

## Troubleshooting

### If checkout fails:
1. Check backend is running
2. Verify user is logged in
3. Check network connection
4. Review backend logs
5. Check cart has items

### If coupon doesn't apply:
1. Verify coupon code is correct
2. Check coupon is active in backend
3. Verify coupon hasn't expired
4. Check minimum order requirements

### If order not created:
1. Check backend logs for errors
2. Verify database connection
3. Check API response in network tab
4. Verify all required fields filled

---

**READY TO TEST! 🚀**
