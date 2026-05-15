# 📡 Rating API Reference

## Endpoint: Submit Review

### POST `/api/reviews`

**Authentication:** Required (JWT Bearer Token)  
**Role:** Buyer only  
**Content-Type:** `multipart/form-data`

---

## 📤 Request Format

### Headers:
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
Accept: application/json
```

### Form Fields:
```
product_id: integer (required)
rating: integer (required, 1-5)
title: string (optional, max 120 chars)
content: string (optional, max 800 chars)
```

### Files:
```
media[0]: File (optional)
media[1]: File (optional)
media[2]: File (optional)
media[3]: File (optional)
media[4]: File (optional)
media[5]: File (optional)
```

**Supported Formats:**
- Images: .jpg, .jpeg, .png
- Videos: .mp4, .mov, .avi, .mkv

**Maximum:** 6 files total

---

## 📥 Response Format

### Success Response (201 Created):
```json
{
  "success": true,
  "message": "Review submitted successfully!",
  "review_id": 123
}
```

### Error Responses:

#### 400 Bad Request - Missing Fields:
```json
{
  "success": false,
  "error": "product_id and rating are required"
}
```

#### 400 Bad Request - Invalid Rating:
```json
{
  "success": false,
  "error": "rating must be between 1 and 5"
}
```

#### 403 Forbidden - Cannot Review:
```json
{
  "success": false,
  "error": "You must purchase this product before reviewing"
}
```

#### 404 Not Found - Product Not Found:
```json
{
  "success": false,
  "error": "Product not found"
}
```

#### 500 Internal Server Error:
```json
{
  "success": false,
  "error": "Internal server error"
}
```

---

## 💾 Database Storage

### Review Record:
```json
{
  "id": 123,
  "product_id": 45,
  "user_id": 67,
  "order_id": 89,
  "rating": 5,
  "title": "Excellent product!",
  "content": "Very satisfied with this purchase. Highly recommended!",
  "status": "published",
  "verified_purchase": true,
  "media": [
    {
      "type": "image",
      "path": "/static/uploads/reviews/20250115_143022_photo1.jpg"
    },
    {
      "type": "image",
      "path": "/static/uploads/reviews/20250115_143023_photo2.jpg"
    },
    {
      "type": "video",
      "path": "/static/uploads/reviews/20250115_143025_video1.mp4"
    }
  ],
  "created_at": "2025-01-15T14:30:25.000Z"
}
```

---

## 🔧 Flutter Implementation

### Example Code:
```dart
Future<void> _submitReview() async {
  final fields = {
    'product_id': productId.toString(),
    'rating': rating.toString(),
    'title': titleController.text.trim(),
    'content': contentController.text.trim(),
  };

  final files = <String, File>{};
  for (int i = 0; i < mediaFiles.length; i++) {
    files['media[$i]'] = mediaFiles[i];
  }

  final result = await ApiService.uploadMultipart(
    'POST',
    '/api/reviews',
    fields: fields,
    files: files.isNotEmpty ? files : null,
    auth: true,
  );

  if (result['success'] == true) {
    // Show success message
    _showSuccessOverlay();
    // Refresh products
    await context.read<BuyerProvider>().fetchProducts();
    // Navigate back
    Navigator.pop(context, true);
  } else {
    // Show error
    ModernSnackBar.showError(context, result['error']);
  }
}
```

---

## 🔍 Validation Rules

### Backend Validation:
1. ✅ User must be authenticated
2. ✅ User must have buyer role
3. ✅ Product must exist and be active
4. ✅ User must have purchased the product
5. ✅ Rating must be between 1 and 5
6. ✅ Only one review per user per product
7. ✅ Files must be valid image/video formats
8. ✅ Maximum 6 files allowed

### Mobile Validation:
1. ✅ Rating must be selected (1-5 stars)
2. ✅ Title max 100 characters
3. ✅ Content max 800 characters
4. ✅ Maximum 6 media files
5. ✅ Supported file formats only

---

## 📊 Rating Calculation

### Average Rating Formula:
```python
avg_rating = sum(all_ratings) / count(all_ratings)
```

### Example:
```
Reviews: [5, 4, 5, 3, 5]
Average: (5+4+5+3+5) / 5 = 4.4
Display: ⭐ 4.4 (5 reviews)
```

---

## 🎯 Product Response Format

### Product with Reviews:
```json
{
  "id": 45,
  "name": "Hot Wheels Basic Car",
  "price": 299.00,
  "rating": 4.4,
  "review_count": 5,
  "reviews": [
    {
      "id": 123,
      "user_name": "Juan D.",
      "rating": 5,
      "title": "Excellent!",
      "content": "Great product",
      "media": [...],
      "verified_purchase": true,
      "created_at": "2025-01-15T14:30:25.000Z"
    }
  ]
}
```

---

## 🔐 Security Notes

1. **JWT Authentication:** All requests require valid access token
2. **Role Check:** Only buyers can submit reviews
3. **Purchase Verification:** Backend validates user purchased the product
4. **File Security:** Filenames are sanitized using secure_filename()
5. **Path Traversal Prevention:** Files saved in designated directory only
6. **SQL Injection Prevention:** Using ORM with parameterized queries

---

## 📁 File Storage

### Directory Structure:
```
backend/
  static/
    uploads/
      reviews/
        20250115_143022_photo1.jpg
        20250115_143023_photo2.jpg
        20250115_143025_video1.mp4
```

### File Naming Convention:
```
{YYYYMMDD}_{HHMMSS}_{original_filename}
```

Example:
```
20250115_143022_IMG_1234.jpg
```

---

## 🌐 URL Access

### Media URLs:
```
http://localhost:5000/static/uploads/reviews/20250115_143022_photo1.jpg
```

### In Production:
```
https://yourdomain.com/static/uploads/reviews/20250115_143022_photo1.jpg
```

---

## ✅ Success Criteria

A review is successfully submitted when:
1. ✅ HTTP 201 status code returned
2. ✅ `success: true` in response
3. ✅ `review_id` is returned
4. ✅ Files saved in `/static/uploads/reviews/`
5. ✅ Database record created
6. ✅ Product rating recalculated
7. ✅ Review visible to all users

---

## 🎉 Complete!

This API is **PRODUCTION READY** and supports:
- ⭐ Star ratings (1-5)
- 📸 Image uploads
- 🎥 Video uploads
- 🔒 Secure authentication
- ✅ Verified purchases
- 🌐 Public visibility

**API Status:** ✅ WORKING
**Last Updated:** January 2025
