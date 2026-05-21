# CHAT SYSTEM - Troubleshooting Guide (Tagalog) 🔧

## Problema: "Hindi nakikita lahat ng messages"

### Database Check ✅ OKAY NA
- Total messages: 30
- User 25 ↔ User 14: 7 messages
- SQL query gumagana ng maayos
- Lahat ng messages nandoon sa database

### Ano ang Nakita Natin:
Ang database at SQL queries ay gumagana ng perpekto. Ang problema ay malamang sa:
1. JWT token extraction
2. API routing
3. Frontend API calls

## Debug Logs Na-add

### 1. Enhanced Logging sa Backend
Nag-add ako ng debug logs sa `unified_chat_api.py`:
```python
print(f"[DEBUG] get_messages called: user_id={user_id}, other_user_id={other_user_id}")
print(f"[DEBUG] Found {len(messages)} messages between user {user_id} and {other_user_id}")
```

### 2. Paano Tingnan ang Backend Logs

**IMPORTANTE: I-restart ang backend para makita ang logs!**

```bash
cd backend
python app.py
```

Tapos sa Flutter app, i-open ang conversation. Tingnan ang backend console para sa:
```
[DEBUG] get_messages called: user_id=25, other_user_id=14
[DEBUG] Found 7 messages between user 25 and 14
```

## Mga Possible Issues at Solutions

### Issue 1: JWT Token Invalid
**Symptoms**: Backend logs ay nagpapakita ng `[ERROR] No user_id extracted from token`

**Solution**:
1. Check kung naka-login ang user
2. Check kung valid ang access token
3. Try mag-logout at mag-login ulit

### Issue 2: Mali ang User ID
**Symptoms**: Backend logs ay nagpapakita ng ibang user_id

**Solution**:
1. Check `AuthProvider.user?.id` sa Flutter
2. Verify kung tama ang user_id sa JWT token
3. Check kung expired na ang token

### Issue 3: API Endpoint Not Found
**Symptoms**: 404 error sa Flutter console

**Solution**:
1. Verify kung tumatakbo ang backend sa port 5000
2. Check `UrlConfig.baseUrl` sa Flutter
3. Verify kung naka-register ang route sa backend

### Issue 4: CORS o Network Error
**Symptoms**: Network error sa Flutter console

**Solution**:
1. Check kung accessible ang backend from device
2. Verify ang IP address sa `UrlConfig`
3. Check firewall settings

## Testing Checklist

### Backend Test
```bash
cd backend
python test_specific_users.py
```
Expected output: 7 messages between User 25 and User 14

### API Test (Manual)
1. Kunin ang JWT token from Flutter app (i-print sa console)
2. Gamitin ang Postman o curl:
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
I-add ang debug print sa `chat_screen.dart`:
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

### Step 1: I-restart ang Backend with Logging
```bash
cd backend
# I-stop ang current server (Ctrl+C)
python app.py
```

### Step 2: I-test sa Flutter App
1. Buksan ang app
2. Pumunta sa chat conversations
3. I-tap ang seller conversation
4. Tingnan ang backend console para sa debug logs

### Step 3: Check ang Logs
Hanapin ang mga patterns na ito:

**✅ OKAY:**
```
[DEBUG] get_messages called: user_id=25, other_user_id=14
[DEBUG] Found 7 messages between user 25 and 14
```

**❌ MAY PROBLEMA:**
```
[ERROR] No user_id extracted from token
```
→ JWT token problem

**❌ MAY PROBLEMA:**
```
[DEBUG] get_messages called: user_id=None, other_user_id=14
```
→ Token extraction failed

**❌ MAY PROBLEMA:**
```
[DEBUG] Found 0 messages between user 25 and 14
```
→ Mali ang user IDs o may database issue

## Common Fixes

### Fix 1: Token Extraction Issue
Kung `user_id=None`, check ang JWT_SECRET_KEY:

```python
# Sa .env file
JWT_SECRET_KEY=your-mobile-jwt-secret-key-change-in-production
```

Siguraduhing pareho ang key na ginamit sa pag-create ng tokens.

### Fix 2: Mali ang Endpoint
Ang Flutter dapat ay tumatawag ng:
```dart
Uri.parse('${UrlConfig.baseUrl}/api/chat/messages/$otherUserId')
```

HINDI:
```dart
Uri.parse('${UrlConfig.baseUrl}/api/v1/chat/messages/$otherUserId')
```

Pareho naman gumagana, pero check kung alin ang ginagamit.

### Fix 3: Cache Issue
I-clear ang app data at i-reinstall:
```bash
flutter clean
flutter pub get
flutter run
```

## Database Verification

I-run ito para i-verify na may messages:
```bash
cd backend
python test_specific_users.py
```

Dapat ay magpakita ng:
```
Query returned 7 messages:
1. Message ID: 25 (SENT, READ)
   Message: Hi! I'm interested in Hobby Tree Kiddie BZ Bus with Slide
2. Message ID: 26 (SENT, READ)
   ...
```

## Final Checklist

- [ ] Backend naka-restart with debug logging
- [ ] Flutter app ay nagpapakita ng tamang user_id sa logs
- [ ] Backend logs ay nagpapakita ng tamang user_id extraction
- [ ] Backend logs ay nagpapakita ng tamang message count
- [ ] Database ay may messages (verified with test script)
- [ ] JWT token ay valid at hindi expired
- [ ] Network connection ay gumagana
- [ ] Tamang API endpoint ang tinatawagan

## Susunod na Hakbang

1. **I-restart ang backend** with debug logging
2. **Buksan ang Flutter app** at pumunta sa chat
3. **Tingnan ang backend console** para sa debug logs
4. **I-report** ang exact logs na nakita mo

Ang logs ay magsasabi sa atin kung nasaan exactly ang problema!

---

**Status**: Debug logging na-add, ready to test
**Action Required**: I-restart ang backend at tingnan ang logs

## Mga Test Scripts Na Available

1. `check_chat_messages.py` - Check total messages sa database
2. `test_specific_users.py` - Test messages between User 25 and 14
3. `debug_chat_comprehensive.py` - Comprehensive database check
4. `test_chat_api.py` - Test API endpoints directly

I-run ang kahit alin para ma-verify ang database at API!
