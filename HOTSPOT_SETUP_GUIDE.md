# Mobile Hotspot Development Setup Guide

## Your Current Configuration

### Network Setup
- **Connection Type**: Mobile Hotspot
- **Computer IP**: `172.20.10.12`
- **Backend URL**: `http://172.20.10.12:5000`
- **Mobile App**: Configured to connect to `http://172.20.10.12:5000`

### Files Already Configured ✅
1. `mobile_app/lib/config/url_config.dart` - Points to `http://172.20.10.12:5000`
2. `backend/app.py` - Listens on `0.0.0.0:5000` (all network interfaces)

## Step-by-Step Setup

### Step 1: Enable Mobile Hotspot
1. On your phone, go to **Settings** → **Mobile Hotspot**
2. Turn ON the hotspot
3. Note the hotspot name and password

### Step 2: Connect Computer to Hotspot
1. On your computer, open WiFi settings
2. Connect to your phone's hotspot
3. Enter the password

### Step 3: Verify IP Address (Optional)
If you want to verify the IP address:
```bash
ipconfig
```
Look for "Wireless LAN adapter Wi-Fi" and find the IPv4 Address.
It should be `172.20.10.12` or similar.

### Step 4: Open Firewall Port (ONE TIME ONLY)
**IMPORTANT**: Run as Administrator!

1. Right-click `ALLOW_MOBILE_CONNECTION.bat`
2. Select "Run as administrator"
3. Press any key to continue
4. Wait for confirmation

This opens port 5000 so your phone can connect to the backend.

### Step 5: Start Backend Server
Double-click: `START_BACKEND_LOCAL.bat`

You should see:
```
* Running on http://172.20.10.12:5000
* Running on http://127.0.0.1:5000
```

**Keep this window open!** The backend needs to stay running.

### Step 6: Start Mobile App
In a new terminal:
```bash
cd mobile_app
flutter run
```

Or use your IDE to run the app.

## Testing the Connection

### Test 1: Check Backend from Computer
Open browser on your computer:
- http://172.20.10.12:5000/

You should see the website homepage.

### Test 2: Check Backend from Phone
Open browser on your phone:
- http://172.20.10.12:5000/

You should see the same homepage.

### Test 3: Test API Endpoint
In phone browser:
- http://172.20.10.12:5000/api/v1/products

You should see JSON data (or 401 error if auth is required - that's OK).

### Test 4: Run Flutter App
The app should now:
- ✅ Load products
- ✅ Show cart items
- ✅ Display orders
- ✅ Show chat messages
- ✅ Update unread counts

## Troubleshooting

### Problem: "Connection refused" or "Cannot connect"

**Solution 1: Check if backend is running**
```bash
# In backend folder
python app.py
```

**Solution 2: Verify computer is on hotspot**
- Check WiFi settings
- Make sure connected to your phone's hotspot

**Solution 3: Check firewall**
- Run `ALLOW_MOBILE_CONNECTION.bat` as Administrator
- Restart backend after opening firewall

**Solution 4: Verify IP address**
```bash
ipconfig
```
If IP changed, update `url_config.dart` with new IP.

### Problem: "404 Not Found" errors

**Solution 1: Clear Flutter cache**
```bash
cd mobile_app
flutter clean
flutter pub get
flutter run
```

**Solution 2: Restart backend**
- Stop backend (Ctrl+C)
- Start again: `python app.py`

**Solution 3: Check backend logs**
Look at the backend terminal for error messages.

### Problem: "Auth requested but no access token available"

**Solution: Log out and log in again**
1. Open app
2. Go to Profile/Settings
3. Log out
4. Log in with your credentials
5. New JWT token will be generated

### Problem: IP Address Changed

If your IP address changes (e.g., reconnected to hotspot):

**Step 1: Find new IP**
```bash
ipconfig
```

**Step 2: Update Flutter config**
Edit `mobile_app/lib/config/url_config.dart`:
```dart
static const String _localUrl = 'http://NEW_IP_HERE:5000';
```

**Step 3: Restart everything**
- Stop backend
- Stop Flutter app
- Start backend
- Start Flutter app

## Network Architecture

```
┌─────────────────┐
│  Your Phone     │
│  (Hotspot ON)   │
│  Mobile App     │
└────────┬────────┘
         │
         │ WiFi Hotspot
         │
┌────────▼────────┐
│  Your Computer  │
│  IP: 172.20.10.12│
│  Backend Server │
│  Port: 5000     │
└─────────────────┘
```

## Important Notes

### About the IP Address
- `172.20.10.12` is a private IP assigned by your phone's hotspot
- This IP is only accessible within the hotspot network
- The IP may change if you:
  - Restart the hotspot
  - Reconnect to the hotspot
  - Use a different hotspot

### About Port 5000
- Flask default development port
- Must be open in Windows Firewall
- Use `ALLOW_MOBILE_CONNECTION.bat` to open it

### About Mobile Data
- Backend running on your computer uses your phone's mobile data
- API requests from mobile app to backend use mobile data
- Be aware of data usage if you have limited data plan

## Quick Start Commands

### Start Backend
```bash
# Option 1: Use batch file
START_BACKEND_LOCAL.bat

# Option 2: Manual
cd backend
python app.py
```

### Start Mobile App
```bash
cd mobile_app
flutter run
```

### Check Backend Status
Open browser: http://172.20.10.12:5000/

## Files Reference

### Configuration Files
- `mobile_app/lib/config/url_config.dart` - Mobile app API URL
- `backend/app.py` - Backend server configuration
- `backend/.env` - Environment variables (JWT secret, database, etc.)

### Helper Scripts
- `START_BACKEND_LOCAL.bat` - Start backend server
- `ALLOW_MOBILE_CONNECTION.bat` - Open firewall port (run as Admin)

### Documentation
- `HOTSPOT_SETUP_GUIDE.md` - This file
- `LOCAL_DEVELOPMENT_SETUP.md` - General local development guide
- `CHAT_SYSTEM_FIX_COMPLETE.md` - Chat system fixes documentation

## Common Scenarios

### Scenario 1: Daily Development
1. Turn on mobile hotspot
2. Connect computer to hotspot
3. Run `START_BACKEND_LOCAL.bat`
4. Run `flutter run` in mobile_app folder
5. Start coding!

### Scenario 2: IP Address Changed
1. Run `ipconfig` to find new IP
2. Update `url_config.dart` with new IP
3. Restart backend and Flutter app

### Scenario 3: Switching to Production
1. Edit `url_config.dart`
2. Change `baseUrl` to Render.com URL
3. Rebuild Flutter app
4. Deploy backend to Render.com

## Security Notes

⚠️ **Development Mode Only**
- This setup is for development/testing only
- Do NOT use in production
- Backend is running in debug mode
- No HTTPS encryption (using HTTP)

🔒 **For Production**
- Use HTTPS (SSL/TLS)
- Deploy to proper hosting (Render.com, AWS, etc.)
- Use environment variables for secrets
- Enable proper authentication

## Need Help?

### Check Backend Logs
Look at the terminal where backend is running for error messages.

### Check Flutter Logs
Look at the terminal where Flutter is running for API errors.

### Test API Manually
Use browser or Postman to test API endpoints:
- http://172.20.10.12:5000/api/v1/products
- http://172.20.10.12:5000/api/v1/chat/unread-count

### Verify Network
```bash
# Check if backend is accessible
ping 172.20.10.12

# Check if port is open
telnet 172.20.10.12 5000
```

## Success Checklist

- [ ] Mobile hotspot is ON
- [ ] Computer connected to hotspot
- [ ] IP address is `172.20.10.12` (or updated in config)
- [ ] Firewall port 5000 is open
- [ ] Backend is running (http://172.20.10.12:5000 works in browser)
- [ ] Flutter app is running
- [ ] App can load products, cart, orders
- [ ] Chat system works
- [ ] No 404 errors in Flutter logs

## You're All Set! 🎉

Your development environment is now configured for mobile hotspot development.

**Quick Start:**
1. Turn on hotspot
2. Connect computer
3. Run `START_BACKEND_LOCAL.bat`
4. Run `flutter run`
5. Start developing!
