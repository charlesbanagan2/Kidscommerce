# Quick Start Guide - Local Development

## 🚀 Quick Start (3 Steps)

### 1. Setup Network (One Time)
```bash
# Turn ON mobile hotspot on your phone
# Connect computer to hotspot
# Run as Administrator:
ALLOW_MOBILE_CONNECTION.bat
```

### 2. Start Backend
```bash
START_BACKEND_LOCAL.bat
```
Wait for: `* Running on http://172.20.10.12:5000`

### 3. Start Mobile App
```bash
cd mobile_app
flutter run
```

## ✅ Verify Everything Works

### Test Backend (Browser)
```
http://172.20.10.12:5000/
```
Should show homepage ✅

### Test Mobile App
- Login ✅
- View products ✅
- Add to cart ✅
- View orders ✅
- Chat ✅

## 🔧 If Something Breaks

### Backend Won't Start
```bash
# Check if port is in use
netstat -ano | findstr :5000
# Kill process if needed
taskkill /PID <process_id> /F
# Start again
python backend/app.py
```

### Mobile App Shows 404
```bash
# Clear cache
cd mobile_app
flutter clean
flutter pub get
flutter run
```

### "My Orders" Not Working
```bash
# Test database
cd backend
python test_my_orders.py

# Restart backend
# Ctrl+C to stop
python app.py
```

### IP Address Changed
```bash
# Find new IP
ipconfig

# Update mobile app config
# Edit: mobile_app/lib/config/url_config.dart
# Change: static const String _localUrl = 'http://NEW_IP:5000';

# Restart everything
```

## 📱 Daily Workflow

```
Morning:
1. Turn on hotspot
2. Connect computer
3. START_BACKEND_LOCAL.bat
4. flutter run
5. Start coding!

Evening:
1. Stop Flutter app
2. Stop backend (Ctrl+C)
3. Turn off hotspot
```

## 🆘 Emergency Fixes

### Everything is Broken
```bash
# Nuclear option - restart everything
1. Stop all (Ctrl+C)
2. Close all terminals
3. Restart computer
4. Turn on hotspot
5. Connect computer
6. START_BACKEND_LOCAL.bat
7. flutter run
```

### Database Issues
```bash
cd backend
python test_my_orders.py
# Check output for errors
```

### Chat Not Working
```bash
# Already fixed! But if issues:
# Check backend terminal for errors
# Look for "ChatMessage" errors
```

## 📞 Quick Reference

| What | Where | Command |
|------|-------|---------|
| Start Backend | Root folder | `START_BACKEND_LOCAL.bat` |
| Start Mobile | mobile_app/ | `flutter run` |
| Test Backend | backend/ | `python test_my_orders.py` |
| Check IP | Anywhere | `ipconfig` |
| Open Firewall | Root folder | `ALLOW_MOBILE_CONNECTION.bat` (Admin) |
| Backend URL | Browser | http://172.20.10.12:5000 |
| Mobile Config | mobile_app/lib/config/ | url_config.dart |

## 📚 Full Documentation

- `COMPLETE_FIX_SUMMARY_TAGALOG.md` - Complete guide (Tagalog)
- `HOTSPOT_SETUP_GUIDE.md` - Detailed hotspot setup
- `CHECK_BACKEND_ERRORS.md` - Error troubleshooting
- `CHAT_SYSTEM_FIX_COMPLETE.md` - Chat system fixes

## ✨ You're All Set!

Backend: http://172.20.10.12:5000 ✅
Mobile: Connected ✅
Ready to code! 🚀
