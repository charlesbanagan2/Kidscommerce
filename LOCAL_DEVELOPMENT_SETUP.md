# Local Development Setup Guide

## Current Configuration

### Backend Server
- **URL**: `http://172.20.10.12:5000`
- **Location**: `backend/app.py`
- **Status**: Running locally on your machine

### Mobile App
- **Config File**: `mobile_app/lib/config/url_config.dart`
- **Base URL**: `http://172.20.10.12:5000`
- **Updated**: ✅ Now pointing to local server

## Steps to Test

### 1. Start Backend Server
```bash
cd backend
python app.py
```

Expected output:
```
* Running on http://172.20.10.12:5000
```

### 2. Verify Backend is Running
Open browser and test:
- http://172.20.10.12:5000/
- http://172.20.10.12:5000/api/v1/chat/unread-count (should return 401 without auth)

### 3. Run Mobile App
```bash
cd mobile_app
flutter run
```

The app should now connect to your local backend at `http://172.20.10.12:5000`

## Troubleshooting

### Issue: Still getting 404 errors
**Solution**: 
1. Stop the Flutter app completely
2. Run `flutter clean`
3. Run `flutter pub get`
4. Run `flutter run` again

### Issue: "Auth requested but no access token available"
**Solution**: 
1. Log out from the app
2. Log in again to get a fresh JWT token
3. The token will be stored and used for API requests

### Issue: Backend not accessible from mobile
**Solution**:
1. Make sure your phone and computer are on the same network
2. Check if firewall is blocking port 5000
3. Run the batch file: `ALLOW_MOBILE_CONNECTION.bat`

### Issue: Connection timeout
**Solution**:
1. Verify the IP address is correct: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Update `url_config.dart` with the correct IP
3. Restart both backend and mobile app

## Network Requirements

### Same Network
- Your computer (running backend) and phone must be on the same WiFi network
- OR use USB tethering/hotspot

### Firewall Rules
The backend needs to accept connections on port 5000:
```bash
# Windows (run as Administrator)
netsh advfirewall firewall add rule name="Flask Backend" dir=in action=allow protocol=TCP localport=5000
```

## Switching Between Local and Production

### For Local Development (Current)
In `url_config.dart`:
```dart
static const String _localUrl = 'http://172.20.10.12:5000';
static String get baseUrl => _localUrl;
```

### For Production (Render.com)
In `url_config.dart`:
```dart
static const String _renderUrl = 'https://kidscommerce-backend.onrender.com';
static String get baseUrl => _renderUrl;
```

## API Endpoints to Test

### Chat Endpoints
- `GET /api/v1/chat/conversations` - Get all conversations
- `GET /api/v1/chat/messages/<user_id>` - Get messages with a user
- `POST /api/v1/chat/send` - Send a message
- `GET /api/v1/chat/unread-count` - Get unread message count

### Product Endpoints
- `GET /api/v1/products` - Get all products
- `GET /api/v1/products/<id>` - Get product details

### Order Endpoints
- `GET /api/v1/orders` - Get user orders
- `POST /api/v1/orders` - Create new order

### Cart Endpoints
- `GET /api/v1/cart` - Get cart items
- `POST /api/v1/cart` - Add to cart

### Wishlist Endpoints
- `GET /api/v1/wishlist` - Get wishlist items
- `POST /api/v1/wishlist` - Add to wishlist

## Common Errors and Solutions

### Error: `[404] Invalid response from server`
**Cause**: The endpoint doesn't exist or the URL is wrong
**Solution**: 
1. Check if backend is running
2. Verify the endpoint exists in `app.py`
3. Check the URL in `url_config.dart`

### Error: `[401] Unauthorized`
**Cause**: JWT token is missing or invalid
**Solution**: Log out and log in again

### Error: `[500] Internal Server Error`
**Cause**: Backend error (check backend console for details)
**Solution**: Look at the backend terminal for error messages

## Files Modified

1. ✅ `mobile_app/lib/config/url_config.dart` - Updated to use local IP
2. ✅ `backend/app.py` - Fixed chat system to use unified ChatMessage
3. ✅ `backend/unified_chat_api.py` - Fixed JWT authentication

## Next Steps

1. **Restart Backend**: Stop and start `python app.py`
2. **Restart Mobile App**: Stop and run `flutter run`
3. **Test Login**: Log in with a test account
4. **Test Features**: Try chat, products, cart, orders
5. **Check Logs**: Monitor backend terminal for any errors

## Important Notes

- The IP address `172.20.10.12` is your computer's local network IP
- This IP may change if you reconnect to WiFi
- For production, switch back to Render.com URL
- Always test on the same network (WiFi/hotspot)
