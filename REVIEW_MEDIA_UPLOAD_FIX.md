# Test Review Media Upload

## Problem
Nag-upload ng images at videos sa review pero NULL lang sa database ang `image_filename` at walang laman ang `media` field.

## Root Cause
Ang backend ay nag-expect ng field name na `media_X` (e.g., `media_0`, `media_1`) pero ang mobile app ay nag-send ng `media[X]` format.

## Solution Applied
Updated `mobile_rating_api.py` to accept BOTH formats:
- `media_0`, `media_1`, `media_2` (original format)
- `media[0]`, `media[1]`, `media[2]` (mobile app format)

Changed from:
```python
if key.startswith('media_'):
```

To:
```python
if key.startswith('media'):  # Accepts both media_ and media[
```

## How to Test

### 1. Check Backend Logs
After submitting a review with media, check the logs for:
```
Processing X files for review
Saved image file: 20240118_120000_photo.jpg
Saved video file: 20240118_120001_video.mp4
Total media files saved: 2
```

### 2. Check Database
```sql
SELECT id, product_id, user_id, rating, content, media, image_filename, created_at 
FROM review 
ORDER BY created_at DESC 
LIMIT 5;
```

Expected result:
- `media` field should contain JSON array:
```json
[
  {"type": "image", "path": "/static/uploads/reviews/20240118_120000_photo.jpg"},
  {"type": "video", "path": "/static/uploads/reviews/20240118_120001_video.mp4"}
]
```

### 3. Check File System
Files should be saved in:
```
backend/static/uploads/reviews/
├── 20240118_120000_photo.jpg
├── 20240118_120001_video.mp4
└── ...
```

### 4. Check API Response
```bash
curl http://localhost:5000/api/products/123/reviews
```

Should return:
```json
{
  "success": true,
  "reviews": [
    {
      "id": 1,
      "user_name": "Juan Dela Cruz",
      "user_avatar": "/static/uploads/user_avatars/user_avatar_456.png",
      "rating": 5,
      "content": "Great product!",
      "media": [
        {"type": "image", "path": "/static/uploads/reviews/20240118_120000_photo.jpg"},
        {"type": "video", "path": "/static/uploads/reviews/20240118_120001_video.mp4"}
      ]
    }
  ]
}
```

## Mobile App Side

The mobile app sends files as:
```dart
files: mediaFiles.asMap().map((index, file) => MapEntry(
  'media[$index]',  // This format: media[0], media[1], etc.
  file,
)),
```

Backend now accepts this format! ✅

## Additional Improvements

Added logging to track:
1. Number of files being processed
2. Each file being saved (with type and filename)
3. Total files successfully saved

This helps debug upload issues.

## Next Steps

1. **Test the upload** - Submit a new review with images/videos
2. **Check the logs** - Verify files are being saved
3. **Check database** - Verify `media` field has data
4. **View in app** - Verify images/videos display correctly

## If Still Not Working

Check these:
1. **File permissions** - Make sure `static/uploads/reviews/` is writable
2. **File size limits** - Check if files are too large
3. **Network issues** - Verify files are actually being sent from mobile app
4. **Content-Type** - Must be `multipart/form-data`

## Expected Behavior

✅ Images and videos upload successfully
✅ Files saved to `static/uploads/reviews/`
✅ `media` field in database contains JSON array
✅ Reviews display with images and videos
✅ All users can see the media (public access)
