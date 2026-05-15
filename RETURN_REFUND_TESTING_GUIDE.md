# 🧪 RETURN & REFUND TESTING GUIDE

## 📋 OVERVIEW

Complete testing guide para sa Return & Refund flow including image and video uploads.

---

## 🎯 TEST SCENARIOS

### ✅ TEST 1: BUYER SUBMITS RETURN REQUEST (Without Media)

**Steps:**
1. Login as Buyer
2. Go to "My Orders" tab
3. Find a DELIVERED order
4. Tap "Return & Refund" button
5. **Step 1:** Select items to return
   - ✅ Tap checkbox to select item
   - ✅ Adjust quantity if needed
   - ✅ Tap "Continue"
6. **Step 2:** Provide reason
   - ✅ Select reason: "Item damaged or defective"
   - ✅ Add details: "The item has a defect"
   - ✅ Skip photo upload
   - ✅ Select refund method: "Original Payment Method"
   - ✅ Tap "Continue"
7. **Step 3:** Review and submit
   - ✅ Review all details
   - ✅ Tap "Submit Request"

**Expected Results:**
```
✅ Success screen appears
✅ Shows "Request Submitted!"
✅ Shows Request ID
✅ Shows "Status: Under Review"
✅ Can tap "Back to Order"
```

**Database Check:**
```sql
SELECT * FROM return_request 
WHERE order_id = [ORDER_ID]
ORDER BY created_at DESC LIMIT 1;

Expected:
- status = 'submitted'
- reason = 'Item damaged or defective'
- description = 'The item has a defect'
- images = NULL or []
```

**Notification Check:**
```
SELLER SHOULD RECEIVE:
🔔 New Return Request
   Order #[ID] - [Product Name]
   Reason: Item damaged or defective
```

---

### ✅ TEST 2: BUYER SUBMITS RETURN WITH IMAGES

**Steps:**
1. Login as Buyer
2. Go to "My Orders" tab
3. Find a DELIVERED order
4. Tap "Return & Refund" button
5. **Step 1:** Select items
   - ✅ Select item
   - ✅ Tap "Continue"
6. **Step 2:** Provide reason AND upload images
   - ✅ Select reason: "Item damaged or defective"
   - ✅ Add details: "The shoes have a tear on the left side"
   - ✅ **TAP "Tap to upload photo"**
   - ✅ **Select image from gallery**
   - ✅ **Image preview appears**
   - ✅ **Upload 2-3 more images (max 5)**
   - ✅ **Verify all images show in preview**
   - ✅ **Test delete button (X) on one image**
   - ✅ Select refund method
   - ✅ Tap "Continue"
7. **Step 3:** Review
   - ✅ **Verify "Evidence Photos" section shows**
   - ✅ **Shows first 3 image thumbnails**
   - ✅ **Shows "+2" if more than 3 images**
   - ✅ Tap "Submit Request"

**Expected Results:**
```
✅ Success screen appears
✅ Images uploaded successfully
✅ Request created with media
```

**Database Check:**
```sql
SELECT * FROM return_request 
WHERE order_id = [ORDER_ID]
ORDER BY created_at DESC LIMIT 1;

Expected:
- status = 'submitted'
- images = JSON array with image paths
  Example: ["uploads/returns/123_image1.jpg", "uploads/returns/123_image2.jpg"]
```

**CRITICAL CHECK:**
```
⚠️ CURRENT ISSUE: Images are NOT being uploaded to backend!
   The _submitRequest() method does NOT include images in the API call.
   
   NEED TO FIX:
   1. Update _submitRequest() to upload images
   2. Backend API must accept multipart/form-data
   3. Store image paths in database
```

---

### ✅ TEST 3: SELLER VIEWS RETURN REQUEST (With Images)

**Steps:**
1. Login as Seller
2. Go to "Returns" tab
3. Find the return request
4. **Verify card shows:**
   - ✅ Product name
   - ✅ Order number
   - ✅ Buyer name
   - ✅ Reason
   - ✅ Refund amount
   - ✅ Details/Description
   - ✅ **[CRITICAL] Evidence photos section**
5. **Tap on return request card**
6. **View full details:**
   - ✅ **All uploaded images should be visible**
   - ✅ **Can tap image to view full size**
   - ✅ **Can swipe between images**
   - ✅ **Videos should have play button**

**Expected Results:**
```
✅ Seller can see all buyer's evidence
✅ Images load properly
✅ Can view full-size images
✅ Can make informed decision
```

**CRITICAL CHECK:**
```
⚠️ CURRENT ISSUE: Seller screen does NOT show images!
   The seller_returns_screen.dart does NOT display media.
   
   NEED TO FIX:
   1. Add media display section to seller card
   2. Show image thumbnails
   3. Add tap to view full size
   4. Add video player for videos
```

---

### ✅ TEST 4: SELLER APPROVES RETURN

**Steps:**
1. Seller views return request with images
2. Reviews evidence photos
3. Taps "Approve" button
4. Confirmation dialog appears
5. Taps "Approve" to confirm

**Expected Results:**
```
✅ Return status → 'approved'
✅ Order status → 'refunded'
✅ Success message shown
✅ Buyer receives notification
✅ Order moves to Returns tab
```

**Database Check:**
```sql
-- Return Request
SELECT * FROM return_request WHERE id = [RETURN_ID];
Expected:
- status = 'approved'
- processed_at = NOW()
- processed_by = [SELLER_ID]

-- Order
SELECT * FROM "order" WHERE id = [ORDER_ID];
Expected:
- status = 'refunded'
- updated_at = NOW()
```

**Notification Check:**
```
BUYER SHOULD RECEIVE:
🔔 Return Approved
   Your return request for Order #[ID] 
   has been approved. The item is now 
   refunded.
```

---

### ✅ TEST 5: SELLER REJECTS RETURN

**Steps:**
1. Seller views return request
2. Taps "Reject" button
3. Dialog appears asking for reason
4. Enters: "Item shows signs of use beyond normal wear"
5. Taps "Reject" to confirm

**Expected Results:**
```
✅ Return status → 'rejected'
✅ Rejection reason saved
✅ Success message shown
✅ Buyer receives notification
```

**Database Check:**
```sql
SELECT * FROM return_request WHERE id = [RETURN_ID];
Expected:
- status = 'rejected'
- seller_response_reason = 'Item shows signs of use...'
- processed_at = NOW()
- processed_by = [SELLER_ID]
```

**Notification Check:**
```
BUYER SHOULD RECEIVE:
🔔 Return Rejected
   Your return request for Order #[ID] 
   was rejected.
   Reason: Item shows signs of use...
```

---

## 🐛 KNOWN ISSUES & FIXES NEEDED

### Issue #1: Images NOT Uploaded to Backend

**Problem:**
```dart
// Current code in return_refund_screen.dart
Future<void> _submitRequest() async {
  final requestData = {
    'items': [...],
    'reason': _selectedReason,
    'additional_details': _additionalDetails,
    'refund_method': _refundMethod,
    // ❌ MISSING: No images included!
  };
  
  final response = await ApiService.createReturnRequest(
    widget.order.id,
    requestData,
  );
}
```

**Fix Needed:**
```dart
Future<void> _submitRequest() async {
  // Upload images first
  List<String> uploadedImageUrls = [];
  for (var photo in _evidencePhotos) {
    final url = await ApiService.uploadReturnEvidence(photo);
    if (url != null) uploadedImageUrls.add(url);
  }
  
  final requestData = {
    'items': [...],
    'reason': _selectedReason,
    'additional_details': _additionalDetails,
    'refund_method': _refundMethod,
    'images': uploadedImageUrls, // ✅ Include images
  };
  
  final response = await ApiService.createReturnRequest(
    widget.order.id,
    requestData,
  );
}
```

---

### Issue #2: Seller Cannot View Images

**Problem:**
```dart
// Current seller_returns_screen.dart
Widget _buildReturnCard(dynamic returnRequest) {
  return Card(
    child: Column(
      children: [
        // Product info
        // Buyer name
        // Reason
        // Refund amount
        // ❌ MISSING: No image display!
      ],
    ),
  );
}
```

**Fix Needed:**
```dart
Widget _buildReturnCard(dynamic returnRequest) {
  final images = returnRequest['images'] ?? [];
  
  return Card(
    child: Column(
      children: [
        // ... existing fields ...
        
        // ✅ ADD: Evidence photos section
        if (images.isNotEmpty) ...[
          const SizedBox(height: 12),
          const Text('Evidence Photos:'),
          const SizedBox(height: 8),
          SizedBox(
            height: 80,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: images.length,
              itemBuilder: (ctx, i) {
                return GestureDetector(
                  onTap: () => _viewFullImage(images[i]),
                  child: Container(
                    margin: const EdgeInsets.only(right: 8),
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(8),
                      image: DecorationImage(
                        image: NetworkImage(images[i]),
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ],
    ),
  );
}
```

---

### Issue #3: Backend API Needs Image Upload Endpoint

**Problem:**
```python
# Current return_refund_api.py
@app.route('/api/buyer/orders/<int:order_id>/return-request', methods=['POST'])
@token_required
def api_create_return_request(order_id):
    data = request.get_json()  # ❌ Only accepts JSON, not files!
    # ...
```

**Fix Needed:**
```python
# Add image upload endpoint
@app.route('/api/return-evidence/upload', methods=['POST'])
@token_required
def api_upload_return_evidence():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    filename = timestamp + filename
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'returns')
    os.makedirs(upload_path, exist_ok=True)
    file.save(os.path.join(upload_path, filename))
    
    return jsonify({
        'success': True,
        'url': f'/static/uploads/returns/{filename}'
    })

# Update create return request to accept images
@app.route('/api/buyer/orders/<int:order_id>/return-request', methods=['POST'])
@token_required
def api_create_return_request(order_id):
    data = request.get_json()
    images = data.get('images', [])  # ✅ Accept images array
    
    return_request = ReturnRequest(
        # ... other fields ...
        images=json.dumps(images) if images else None  # ✅ Store images
    )
    # ...
```

---

## 📝 COMPLETE TEST CHECKLIST

### Buyer Side:
- [ ] Can access Return & Refund screen from delivered order
- [ ] Can select items to return
- [ ] Can adjust quantity
- [ ] Can select return reason
- [ ] Can add additional details
- [ ] **Can upload images (tap to upload)**
- [ ] **Image preview shows after upload**
- [ ] **Can delete uploaded image**
- [ ] **Can upload multiple images (max 5)**
- [ ] **Can upload videos**
- [ ] Can select refund method
- [ ] Can review all details before submit
- [ ] **Evidence photos show in review step**
- [ ] Can submit request successfully
- [ ] See success screen
- [ ] Receive confirmation notification

### Seller Side:
- [ ] Receive notification for new return
- [ ] Can view return request in Returns tab
- [ ] Can see all return details
- [ ] **Can see uploaded images**
- [ ] **Can tap image to view full size**
- [ ] **Can swipe between images**
- [ ] **Videos have play button**
- [ ] Can approve return
- [ ] See confirmation dialog
- [ ] See success message after approve
- [ ] Can reject return
- [ ] Must enter rejection reason
- [ ] See success message after reject

### Database:
- [ ] Return request created with correct data
- [ ] **Images stored in database**
- [ ] Status updates correctly
- [ ] Order status changes to 'refunded' when approved
- [ ] Timestamps recorded
- [ ] Rejection reason saved

### Notifications:
- [ ] Seller notified when buyer submits
- [ ] Buyer notified when seller approves
- [ ] Buyer notified when seller rejects
- [ ] Real-time updates via SocketIO

---

## 🚀 PRIORITY FIXES

### HIGH PRIORITY:
1. **✅ Add image upload to API call**
   - Update `_submitRequest()` in `return_refund_screen.dart`
   - Upload images before creating return request
   - Include image URLs in request data

2. **✅ Add image upload endpoint to backend**
   - Create `/api/return-evidence/upload` endpoint
   - Handle multipart/form-data
   - Save files to `static/uploads/returns/`
   - Return image URLs

3. **✅ Display images on seller side**
   - Update `seller_returns_screen.dart`
   - Show image thumbnails in return card
   - Add tap to view full size
   - Add image gallery viewer

### MEDIUM PRIORITY:
4. **Add video support**
   - Allow video upload (MP4, max 50MB)
   - Show video thumbnail with play icon
   - Add video player

5. **Add image compression**
   - Compress images before upload
   - Reduce file size
   - Faster uploads

### LOW PRIORITY:
6. **Add image zoom**
   - Pinch to zoom on full-size image
   - Better viewing experience

7. **Add multiple image viewer**
   - Swipe between images
   - Show image counter (1/5)

---

## 📊 TEST DATA

### Sample Return Request:
```json
{
  "order_id": 123,
  "items": [
    {
      "order_item_id": 456,
      "quantity": 1,
      "reason": "Item damaged or defective"
    }
  ],
  "reason": "Item damaged or defective",
  "additional_details": "The baby shoes have a tear on the left side",
  "refund_method": "original",
  "images": [
    "/static/uploads/returns/20250115_103000_shoe_damage1.jpg",
    "/static/uploads/returns/20250115_103001_shoe_damage2.jpg",
    "/static/uploads/returns/20250115_103002_shoe_damage3.jpg"
  ]
}
```

### Sample Database Record:
```sql
INSERT INTO return_request (
  order_id, order_item_id, buyer_id, seller_id,
  reason, description, quantity, status,
  refund_amount, images, created_at
) VALUES (
  123, 456, 25, 10,
  'Item damaged or defective',
  'The baby shoes have a tear on the left side',
  1, 'submitted', 450.00,
  '["uploads/returns/20250115_103000_shoe_damage1.jpg","uploads/returns/20250115_103001_shoe_damage2.jpg"]',
  NOW()
);
```

---

## ✅ SUCCESS CRITERIA

**Test is SUCCESSFUL when:**
1. ✅ Buyer can upload images/videos
2. ✅ Images show in preview
3. ✅ Images uploaded to server
4. ✅ Images stored in database
5. ✅ Seller can view all images
6. ✅ Seller can tap to view full size
7. ✅ Approve/Reject works correctly
8. ✅ Notifications sent properly
9. ✅ Order status updates correctly
10. ✅ No errors in console

---

## 🎯 NEXT STEPS

1. **Implement image upload functionality**
2. **Test with real images**
3. **Add seller image viewer**
4. **Test end-to-end flow**
5. **Fix any bugs found**
6. **Deploy to production**

---

**READY FOR TESTING!** 🚀
