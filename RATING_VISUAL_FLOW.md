# 🎨 Rating System Visual Flow

## 📱 User Journey

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCT LISTING SCREEN                    │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ Product  │  │ Product  │  │ Product  │                 │
│  │  Image   │  │  Image   │  │  Image   │                 │
│  │          │  │          │  │          │                 │
│  │ ⭐ 4.5   │  │ ⭐ 3.8   │  │ ⭐ 5.0   │  ← Ratings      │
│  │ (12)     │  │ (5)      │  │ (8)      │  ← Review Count │
│  │ ₱299.00  │  │ ₱450.00  │  │ ₱199.00  │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Tap Product
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  PRODUCT DETAIL SCREEN                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Product Image Gallery                     │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Hot Wheels Basic Car                                       │
│  ⭐⭐⭐⭐⭐ 4.5 (12 reviews)                                │
│  ₱299.00                                                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Ratings & Reviews              [Write] [See All]   │    │
│  │                                                     │    │
│  │ ┌─────────────────────────────────────────────┐   │    │
│  │ │ Juan D. ⭐⭐⭐⭐⭐ Jan 15, 2025            │   │    │
│  │ │ "Excellent product!"                        │   │    │
│  │ │ Very satisfied with this purchase...        │   │    │
│  │ └─────────────────────────────────────────────┘   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Tap "Write"
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  SUBMIT REVIEW SCREEN                        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ [Product Image] Hot Wheels Basic Car               │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Your Rating                                                │
│  ⭐ ⭐ ⭐ ⭐ ⭐  ← Tap to select                            │
│  Excellent                                                  │
│                                                              │
│  Review Title (Optional)                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Summarize your experience                          │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Your Review (Optional)                                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Share your experience with this product...         │    │
│  │                                                     │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Add Photos/Videos (Optional)                               │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐                                  │
│  │ 📷│ │ 📷│ │ 🎥│ │ + │  ← Up to 6 files                 │
│  └───┘ └───┘ └───┘ └───┘                                  │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           [Submit Review]                          │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Submit
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   SUCCESS OVERLAY                            │
│                                                              │
│              ┌─────────────────────────┐                    │
│              │                         │                    │
│              │      ╔═══════╗          │                    │
│              │      ║   ✓   ║  ← Animated                  │
│              │      ╚═══════╝    Check Icon                │
│              │                                              │
│              │  Review Submitted!                           │
│              │                                              │
│              │  Salamat sa iyong                            │
│              │  5-star review!                              │
│              │                                              │
│              │  ⭐ ⭐ ⭐ ⭐ ⭐  ← Animated                   │
│              │                                              │
│              │  ┌─────────────────────┐                    │
│              │  │ ℹ️ Makikita na ng   │                    │
│              │  │ lahat ang iyong     │                    │
│              │  │ review              │                    │
│              │  └─────────────────────┘                    │
│              │                         │                    │
│              └─────────────────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Auto-close (2s)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              PRODUCT DETAIL (REFRESHED)                      │
│                                                              │
│  Hot Wheels Basic Car                                       │
│  ⭐⭐⭐⭐⭐ 4.6 (13 reviews)  ← Updated!                    │
│  ₱299.00                                                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Ratings & Reviews              [Write] [See All]   │    │
│  │                                                     │    │
│  │ ┌─────────────────────────────────────────────┐   │    │
│  │ │ You ⭐⭐⭐⭐⭐ Just now                      │   │    │
│  │ │ "Excellent product!"                        │   │ ← New!
│  │ │ [📷] [📷] [🎥]                              │   │    │
│  │ └─────────────────────────────────────────────┘   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Technical Flow

```
┌──────────────┐
│ Mobile App   │
│ (Flutter)    │
└──────┬───────┘
       │
       │ 1. User selects rating & uploads media
       │
       ▼
┌──────────────────────────────────────────┐
│ ApiService.uploadMultipart()             │
│                                          │
│ POST /api/reviews                        │
│ Content-Type: multipart/form-data        │
│ Authorization: Bearer {token}            │
│                                          │
│ Fields:                                  │
│   - product_id: 45                       │
│   - rating: 5                            │
│   - title: "Excellent!"                  │
│   - content: "Great product..."          │
│                                          │
│ Files:                                   │
│   - media[0]: photo1.jpg                 │
│   - media[1]: photo2.jpg                 │
│   - media[2]: video1.mp4                 │
└──────┬───────────────────────────────────┘
       │
       │ 2. HTTP Request
       │
       ▼
┌──────────────────────────────────────────┐
│ Flask Backend (app.py)                   │
│                                          │
│ @app.route('/api/reviews', POST)         │
│ @token_required                          │
│ @role_required('buyer')                  │
│                                          │
│ 1. Validate JWT token                   │
│ 2. Check user role (buyer)               │
│ 3. Validate product exists               │
│ 4. Check verified purchase               │
│ 5. Validate rating (1-5)                 │
│ 6. Process media files                   │
│ 7. Save files to disk                    │
│ 8. Create review record                  │
│ 9. Update product rating                 │
└──────┬───────────────────────────────────┘
       │
       │ 3. Save Files
       │
       ▼
┌──────────────────────────────────────────┐
│ File System                              │
│                                          │
│ /static/uploads/reviews/                 │
│   ├── 20250115_143022_photo1.jpg         │
│   ├── 20250115_143023_photo2.jpg         │
│   └── 20250115_143025_video1.mp4         │
└──────┬───────────────────────────────────┘
       │
       │ 4. Save to Database
       │
       ▼
┌──────────────────────────────────────────┐
│ Supabase Database                        │
│                                          │
│ review table:                            │
│ ┌────────────────────────────────────┐  │
│ │ id: 123                            │  │
│ │ product_id: 45                     │  │
│ │ user_id: 67                        │  │
│ │ rating: 5                          │  │
│ │ title: "Excellent!"                │  │
│ │ content: "Great product..."        │  │
│ │ media: [                           │  │
│ │   {type: "image", path: "..."},    │  │
│ │   {type: "image", path: "..."},    │  │
│ │   {type: "video", path: "..."}     │  │
│ │ ]                                  │  │
│ │ verified_purchase: true            │  │
│ │ status: "published"                │  │
│ │ created_at: 2025-01-15T14:30:25Z   │  │
│ └────────────────────────────────────┘  │
└──────┬───────────────────────────────────┘
       │
       │ 5. Return Success
       │
       ▼
┌──────────────────────────────────────────┐
│ JSON Response                            │
│                                          │
│ {                                        │
│   "success": true,                       │
│   "message": "Review submitted!",        │
│   "review_id": 123                       │
│ }                                        │
└──────┬───────────────────────────────────┘
       │
       │ 6. Handle Response
       │
       ▼
┌──────────────────────────────────────────┐
│ Mobile App                               │
│                                          │
│ 1. Show success overlay                  │
│ 2. Animate check icon                    │
│ 3. Display stars                         │
│ 4. Show Tagalog message                  │
│ 5. Auto-dismiss (2s)                     │
│ 6. Refresh products                      │
│ 7. Update UI                             │
│ 8. Navigate back                         │
└──────────────────────────────────────────┘
```

---

## 🎨 Animation Timeline

```
Success Overlay Animation (800ms total):

0ms     ┌─────────────────────────────────────┐
        │ Fade In (0-300ms)                   │
        │ Opacity: 0 → 1                      │
        └─────────────────────────────────────┘

0ms     ┌─────────────────────────────────────┐
        │ Scale In (0-500ms)                  │
        │ Scale: 0.3 → 1.0                    │
        │ Curve: Elastic Out                  │
        └─────────────────────────────────────┘

300ms   ┌─────────────────────────────────────┐
        │ Check Icon (300-800ms)              │
        │ Scale: 0 → 1.0                      │
        │ Curve: Elastic Out                  │
        └─────────────────────────────────────┘

400ms   ┌─────────────────────────────────────┐
        │ Star 1 Animation                    │
        │ Scale: 0 → 1.0                      │
        └─────────────────────────────────────┘

500ms   ┌─────────────────────────────────────┐
        │ Star 2 Animation                    │
        └─────────────────────────────────────┘

600ms   ┌─────────────────────────────────────┐
        │ Star 3 Animation                    │
        └─────────────────────────────────────┘

700ms   ┌─────────────────────────────────────┐
        │ Star 4 Animation                    │
        └─────────────────────────────────────┘

800ms   ┌─────────────────────────────────────┐
        │ Star 5 Animation                    │
        └─────────────────────────────────────┘

2000ms  ┌─────────────────────────────────────┐
        │ Auto Dismiss                        │
        │ Remove overlay                      │
        │ Navigate back                       │
        └─────────────────────────────────────┘
```

---

## 📊 Data Flow

```
User Input → Mobile App → API → Backend → Database
                                    ↓
                              File System
                                    ↓
                              Response
                                    ↓
                            Success UI
                                    ↓
                            Refresh Data
                                    ↓
                            Update Display
```

---

## 🎯 Key Components

### Mobile App:
- ✅ SubmitReviewScreen (UI)
- ✅ ProductDetailScreen (Display)
- ✅ ProductCardWidget (Ratings)
- ✅ ApiService (Upload)
- ✅ BuyerProvider (State)

### Backend:
- ✅ /api/reviews endpoint
- ✅ File upload handler
- ✅ Authentication middleware
- ✅ Validation logic
- ✅ Database operations

### Database:
- ✅ review table
- ✅ product table (rating calculation)
- ✅ user table (authentication)
- ✅ order table (verification)

---

## 🎉 Complete System!

```
┌─────────────────────────────────────────┐
│         RATING SYSTEM COMPLETE          │
│                                         │
│  ⭐ Star Ratings (1-5)                  │
│  📸 Image Uploads                       │
│  🎥 Video Uploads                       │
│  🎨 Beautiful UI                        │
│  🔒 Secure & Validated                  │
│  🌐 Public Visibility                   │
│  📱 Mobile Optimized                    │
│  ✅ Production Ready                    │
│                                         │
│         TAPOS NA! 🎊                    │
└─────────────────────────────────────────┘
```

**Status:** ✅ FULLY WORKING
**Date:** January 2025
