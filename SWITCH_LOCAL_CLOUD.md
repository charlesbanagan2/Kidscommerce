# How to Switch Between Local and Cloud

## 🔄 Quick Switch Guide

### Para sa LOCAL Development (Hotspot)
1. Open: `mobile_app/lib/config/url_config.dart`
2. Change line 9:
```dart
static const bool USE_LOCAL = true;  // 👈 Set to TRUE
```
3. Save file
4. Restart Flutter app:
```bash
# Stop app (Ctrl+C or Stop button)
flutter run
```

### Para sa CLOUD/Production (Render.com)
1. Open: `mobile_app/lib/config/url_config.dart`
2. Change line 9:
```dart
static const bool USE_LOCAL = false;  // 👈 Set to FALSE
```
3. Save file
4. Restart Flutter app:
```bash
# Stop app (Ctrl+C or Stop button)
flutter run
```

## 📋 Current Configuration

### Local Development
- **URL**: `http://172.20.10.12:5000`
- **When to use**: Testing on your computer via hotspot
- **Requirements**: 
  - Mobile hotspot ON
  - Computer connected to hotspot
  - Backend running locally
  - Firewall port 5000 open

### Cloud/Production
- **URL**: `https://kids-kingdom.onrender.com`
- **When to use**: 
  - Testing with live server
  - No local backend needed
  - Works from anywhere with internet
  - Production deployment

## 🎯 Which One to Use?

### Use LOCAL when:
- ✅ Developing new features
- ✅ Testing backend changes
- ✅ Debugging issues
- ✅ No internet connection
- ✅ Faster response times

### Use CLOUD when:
- ✅ Testing production environment
- ✅ Sharing with others
- ✅ No local backend setup
- ✅ Testing from different locations
- ✅ Final testing before release

## 🔍 How to Verify Current Setting

### Check Config File
Open `mobile_app/lib/config/url_config.dart` and look at line 9:
```dart
static const bool USE_LOCAL = true;   // Using LOCAL
static const bool USE_LOCAL = false;  // Using CLOUD
```

### Check App Logs
When app starts, you'll see in logs:
```
// Local
🔤 API GET http://172.20.10.12:5000/api/v1/...

// Cloud
🔤 API GET https://kids-kingdom.onrender.com/api/v1/...
```

## ⚠️ Common Issues

### Issue: Changed config but still using old URL
**Solution**: 
```bash
# Stop app completely
# Clear cache
flutter clean
flutter pub get
# Run again
flutter run
```

### Issue: Local not working after switching
**Solution**:
1. Check if backend is running: `python backend/app.py`
2. Check if on hotspot
3. Check IP address: `ipconfig`
4. Update IP in config if changed

### Issue: Cloud not working after switching
**Solution**:
1. Check if Render.com backend is live
2. Check internet connection
3. Check URL is correct: `https://kids-kingdom.onrender.com`

## 📱 Quick Commands

### Switch to Local
```bash
# 1. Edit config file
# Set USE_LOCAL = true

# 2. Restart app
flutter run
```

### Switch to Cloud
```bash
# 1. Edit config file
# Set USE_LOCAL = false

# 2. Restart app
flutter run
```

### Test Current URL
```bash
# In Dart DevTools console or app logs
print(UrlConfig.baseUrl);
```

## 🚀 Pro Tips

### Tip 1: Use Environment Variables (Advanced)
Para hindi na manual ang pag-switch, pwede gumamit ng environment variables:
```bash
# Local
flutter run --dart-define=USE_LOCAL=true

# Cloud
flutter run --dart-define=USE_LOCAL=false
```

### Tip 2: Create Build Flavors (Advanced)
Create separate builds for dev and prod:
```bash
# Development build (local)
flutter run --flavor dev

# Production build (cloud)
flutter run --flavor prod
```

### Tip 3: Quick Switch Script
Create `switch_to_local.bat`:
```batch
@echo off
echo Switching to LOCAL development...
# Add sed or powershell command to change config
flutter run
```

## 📊 Configuration Summary

| Setting | Local | Cloud |
|---------|-------|-------|
| USE_LOCAL | `true` | `false` |
| URL | http://172.20.10.12:5000 | https://kids-kingdom.onrender.com |
| Protocol | HTTP | HTTPS |
| Port | 5000 | 443 |
| Network | Hotspot | Internet |
| Backend | Your computer | Render.com |

## ✅ Checklist Before Switching

### Before Switching to LOCAL:
- [ ] Mobile hotspot is ON
- [ ] Computer connected to hotspot
- [ ] Backend is running (`python backend/app.py`)
- [ ] Firewall port 5000 is open
- [ ] IP address is correct (172.20.10.12)

### Before Switching to CLOUD:
- [ ] Internet connection is working
- [ ] Render.com backend is live
- [ ] URL is correct (https://kids-kingdom.onrender.com)
- [ ] No local backend needed

## 🎉 You're All Set!

Now you can easily switch between local and cloud development!

**Current Setting**: Check line 9 in `url_config.dart`
- `USE_LOCAL = true` → Local development
- `USE_LOCAL = false` → Cloud/Production

Happy coding! 🚀
