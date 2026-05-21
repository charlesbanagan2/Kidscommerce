# CHAT SYSTEM - TROUBLESHOOTING GUIDE 🔧

## Problem: "Hindi nakikita lahat ng messages"

### Database Check ✅ PASSED
- Total messages: 30
- User 25 ↔ User 14: 7 messages
- SQL query working correctly
- All messages exist in database

### What We Found:
The database and SQL queries are working perfectly. The problem is likely in:
1. JWT token extraction
2. API routing
3. Frontend API calls

## Debug Steps Added

### 1. Enhanced Logging in Backend
Added debug logs to `unified_chat_api.py`:
```python
print(f"[DEBUG] get_messages called: user_id={user_id}, other_user_id={other_user_id}")
print(f"[DEBUG] Found {len(messages)} messages between user {user_id} and {other_user_id}")
```

### 2. How to Check Backend Logs

**IMPORTANTE: I-restart ang backend para makita ang logs!**

```bash
cd backend
python app.py
```

Then sa Flutter app, i-open ang conversation. Check ang backend console for:
```
[DEBUG] get_messages called: user_id=25, other_user_id=14
[DEBUG] Found 7 messages between user 25 and 14
```

## Possible Issues & Solutions

### Issue 1: JWT Token Invalid
**Symptoms**: Backend logs show `[ERROR] No user_id extracted from token`

**Solution**:
1. Check if user is logged in
2. Check if access token is valid
3. Try logging out and logging in again

### Issue 2: Wrong User ID
**Symptoms**: Backend logs show different user_id than expected

**Solution**:
1. Check `AuthProvider.user?.id` in Flutter
2. Verify JWT token contains correct user_id
3. Check if token is expired

### Issue 3: API Endpoint Not Found
**Symptoms**: 404 error in Flutter console

**Solution**:
1. Verify backend is running on correct port (5000)
2. Check `UrlConfig.baseUrl` in Flutter
3. Verify route is registered in backend

### Issue 4: CORS or Network Error
**Symptoms**: Network error in Flutter console

**Solution**:
1. Check if backend is accessible from device
2. Verify IP address in `UrlConfig`
3. Check firewall settings

## Testing Checklist

### Backend Test
```bash
cd backend
python test_specific_users.py
```
Expected output: 7 messages between User 25 and User 14

### API Test (Manual)
1. Get JWT token from Flutter app (print it in console)
2. Use Postman or curl:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     http://192.168.1.26:5000/api/chat/messages/14
```

Expected response:
```json
{
  "success": true,
  "messages": [
    {
      "id": 25,
      "sender_id": 25,
      "receiver_id": 14,
      "message": "Hi! I'm interested in...",
      ...
    },
    ...
  ]
}
```

### Flutter Test
Add debug print in `chat_screen.dart`:
```dart
Future<void> _loadMessages() async {
  print('[DEBUG] Loading messages for user ${widget.otherUserId}');
  print('[DEBUG] Access token: ${accessToken?.substring(0, 20)}...');
  
  final result = await ChatService.getMessages(accessToken, widget.otherUserId);
  
  print('[DEBUG] API response: ${result['success']}');
  print('[DEBUG] Messages count: ${result['messages']?.length ?? 0}');
  
  if (result['success'] == true) {
    _messages = result['messages'] ?? [];
    print('[DEBUG] Loaded ${_messages.length} messages');
  } else {
    print('[ERROR] Failed to load messages: ${result['error']}');
  }
}
```

## Quick Fix Steps

### Step 1: Restart Backend with Logging
```bash
cd backend
# Stop current server (Ctrl+C)
python app.py
```

### Step 2: Test in Flutter App
1. Open app
2. Go to chat conversations
3. Tap on seller conversation
4. Check backend console for debug logs

### Step 3: Check Logs
Look for these patterns:

**✅ GOOD:**
```
[DEBUG] get_messages called: user_id=25, other_user_id=14
[DEBUG] Found 7 messages between user 25 and 14
```

**❌ BAD:**
```
[ERROR] No user_id extracted from token
```
→ JWT token problem

**❌ BAD:**
```
[DEBUG] get_messages called: user_id=None, other_user_id=14
```
→ Token extraction failed

**❌ BAD:**
```
[DEBUG] Found 0 messages between user 25 and 14
```
→ Wrong user IDs or database issue

## Common Fixes

### Fix 1: Token Extraction Issue
If `user_id=None`, check JWT_SECRET_KEY:

```python
# In .env file
JWT_SECRET_KEY=your-mobile-jwt-secret-key-change-in-production
```

Make sure it matches the key used when creating tokens.

### Fix 2: Wrong Endpoint
Flutter should call:
```dart
Uri.parse('${UrlConfig.baseUrl}/api/chat/messages/$otherUserId')
```

NOT:
```dart
Uri.parse('${UrlConfig.baseUrl}/api/v1/chat/messages/$otherUserId')
```

Both work, but check which one is being used.

### Fix 3: Cache Issue
Clear app data and reinstall:
```bash
flutter clean
flutter pub get
flutter run
```

## Database Verification

Run this to verify messages exist:
```bash
cd backend
python test_specific_users.py
```

Should show:
```
Query returned 7 messages:
1. Message ID: 25 (SENT, READ)
   Message: Hi! I'm interested in Hobby Tree Kiddie BZ Bus with Slide
2. Message ID: 26 (SENT, READ)
   ...
```

## Final Checklist

- [ ] Backend restarted with debug logging
- [ ] Flutter app shows correct user_id in logs
- [ ] Backend logs show correct user_id extraction
- [ ] Backend logs show correct message count
- [ ] Database has messages (verified with test script)
- [ ] JWT token is valid and not expired
- [ ] Network connection is working
- [ ] Correct API endpoint is being called

## Next Steps

1. **Restart backend** with debug logging
2. **Open Flutter app** and go to chat
3. **Check backend console** for debug logs
4. **Report back** with the exact logs you see

The logs will tell us exactly where the problem is!

---

**Status**: Debug logging added, ready to test
**Action Required**: Restart backend and check logs
