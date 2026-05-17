# 🚀 QUICK START - Test Return & Refund System

## ⚡ 5-Minute Test Guide

### Step 1: Open Mobile App
```bash
cd mobile_app
flutter run
```

### Step 2: Navigate to Returns
1. Login as buyer
2. Tap "Orders" from bottom navigation
3. Swipe to "Returns" tab
4. You should see any refunded orders here

### Step 3: Create Test Return
1. Go back to "All Orders" or "Completed" tab
2. Tap on a delivered order
3. Look for "Request Return" button
4. Tap it to start return process

### Step 4: Complete Return Form
**Step 1 - Select Items:**
- Tap items you want to return
- Adjust quantity if needed
- Tap "Continue"

**Step 2 - Reason & Evidence:**
- Select a return reason
- Tap "Photo *" to upload at least 1 photo
- Tap "Video *" to upload at least 1 video
- (Optional) Add additional details
- Choose refund method
- Tap "Continue"

**Step 3 - Review:**
- Review all information
- Tap "Submit Request"

### Step 5: Verify Success
- ✅ You should see success screen
- ✅ Return should appear in "Returns" tab
- ✅ Seller should receive notification

---

## 🔍 Troubleshooting

### Issue: "Request Return" button not showing
**Solution:** Order must be in "delivered" or "completed" status

### Issue: Can't upload photos/videos
**Solution:** 
1. Check camera/storage permissions
2. Verify backend endpoint: `/api/return-evidence/upload`
3. Check file size limits

### Issue: Submit fails with error
**Solution:**
1. Check backend endpoint: `/api/buyer/orders/{id}/return-request`
2. Verify authentication token is valid
3. Check backend logs for errors

### Issue: Return doesn't appear in Returns tab
**Solution:**
1. Pull to refresh the orders list
2. Check order status is "refunded" or contains "return"
3. Verify backend returns correct status

---

## 🧪 Backend Verification

### Test File Upload
```bash
curl -X POST http://localhost:5000/api/return-evidence/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.jpg"
```

**Expected Response:**
```json
{
  "success": true,
  "url": "/uploads/evidence_1234567890.jpg"
}
```

### Test Create Return
```bash
curl -X POST http://localhost:5000/api/buyer/orders/1/return-request \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "order_item_id": 1,
        "quantity": 1,
        "reason": "Item damaged or defective"
      }
    ],
    "reason": "Item damaged or defective",
    "additional_details": "The item arrived with a crack",
    "refund_method": "original",
    "images": ["/uploads/evidence_1.jpg"],
    "videos": ["/uploads/evidence_2.mp4"]
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "return_id": 123,
  "message": "Return request submitted successfully"
}
```

---

## 📱 Mobile App Code Locations

### Main Files:
- **Orders Screen**: `mobile_app/lib/screens/buyer_app/orders_screen.dart`
- **Return Screen**: `mobile_app/lib/screens/buyer_app/return_refund_screen.dart`
- **API Service**: `mobile_app/lib/services/api_service.dart`

### Key Methods:
```dart
// Upload evidence
ApiService.uploadReturnEvidence(File file)

// Create return request
ApiService.createReturnRequest(int orderId, Map<String, dynamic> data)

// Get buyer returns
ApiService.getBuyerReturnRequests()
```

---

## 🎯 Success Criteria

✅ **Mobile App:**
- Returns tab shows refunded orders
- Can open return form from order detail
- Can upload photos and videos
- Can submit return request
- Shows success confirmation

✅ **Backend:**
- File upload endpoint works
- Create return endpoint works
- Returns are saved to database
- Seller receives notification
- Status updates correctly

✅ **End-to-End:**
- Buyer submits return → Seller sees it
- Seller approves → Buyer sees status update
- Refund is processed → Order status changes

---

## 🐛 Common Errors & Fixes

### Error: "Network error: Check internet connection"
**Fix:** Backend server not running or wrong URL in `url_config.dart`

### Error: "Request timeout"
**Fix:** Backend taking too long, check server performance

### Error: "Invalid response from server"
**Fix:** Backend returning wrong format, check API response structure

### Error: "Upload failed"
**Fix:** 
- Check file size (max 5MB for images, 50MB for videos)
- Verify backend accepts multipart/form-data
- Check file permissions

---

## 📊 Expected Flow

```
1. Buyer: Order delivered ✅
   ↓
2. Buyer: Request return 📱
   ↓
3. System: Upload evidence 📸
   ↓
4. System: Create return request 💾
   ↓
5. Seller: Receives notification 🔔
   ↓
6. Seller: Reviews & approves ✅
   ↓
7. System: Updates status 🔄
   ↓
8. Buyer: Sees approved status 📱
   ↓
9. System: Processes refund 💰
   ↓
10. Buyer: Receives refund ✅
```

---

## 🎉 You're Ready!

The system is fully implemented. Just:
1. ✅ Verify backend endpoints exist
2. ✅ Test file upload
3. ✅ Test end-to-end flow
4. ✅ Deploy to production

**Need help?** Check the detailed documentation in:
- `SYSTEM_READY.md` - Complete system overview
- `IMPLEMENTATION_STATUS.md` - Implementation details
- `MOBILE_APP_CODE_FIXES.md` - Code reference

---

**Happy Testing! 🚀**
