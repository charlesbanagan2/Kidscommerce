# Google OAuth Setup - Updated Client IDs

## ✅ Configuration Complete

All Google OAuth Client IDs have been updated across the system.

---

## 🔑 Client IDs

### Android
```
19725108081-d03cnmvghsfr3tpevj05pnn2upr55vds.apps.googleusercontent.com
```

### Web
```
19725108081-hna4pcv8mopmrbj5jnb95g4m5v9431q1.apps.googleusercontent.com
```

---

## 📁 Files Updated

### 1. Backend Configuration
**File:** `backend/.env`
```env
GOOGLE_OAUTH_CLIENT_ID_ANDROID=19725108081-d03cnmvghsfr3tpevj05pnn2upr55vds.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_ID_WEB=19725108081-hna4pcv8mopmrbj5jnb95g4m5v9431q1.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_ID=19725108081-hna4pcv8mopmrbj5jnb95g4m5v9431q1.apps.googleusercontent.com
```

### 2. Android Configuration
**File:** `mobile_app/android/app/src/main/res/values/strings.xml`
```xml
<string name="default_web_client_id">19725108081-hna4pcv8mopmrbj5jnb95g4m5v9431q1.apps.googleusercontent.com</string>
```

### 3. Web Configuration
**File:** `mobile_app/web/index.html`
```html
<meta name="google-signin-client_id" content="19725108081-hna4pcv8mopmrbj5jnb95g4m5v9431q1.apps.googleusercontent.com">
```

### 4. Flutter Configuration
**File:** `mobile_app/lib/config/google_oauth_config.dart`
- Android Client ID constant
- Web Client ID constant
- Platform-aware getter

---

## 🚀 How to Use

### In Flutter Code
```dart
import 'package:kids_commerce/config/google_oauth_config.dart';

// Use in Google Sign-In initialization
final GoogleSignIn googleSignIn = GoogleSignIn(
  clientId: GoogleOAuthConfig.webClientId,
  scopes: ['email', 'profile'],
);
```

### In Backend Code
```python
# Access from environment variables
android_client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID_ANDROID')
web_client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID_WEB')
```

---

## ✅ Verification Steps

### 1. Clean and Rebuild
```bash
cd mobile_app
flutter clean
flutter pub get
flutter build apk  # For Android
flutter build web  # For Web
```

### 2. Test Android
```bash
flutter run -d android
# Try Google Sign-In
```

### 3. Test Web
```bash
flutter run -d chrome
# Try Google Sign-In
```

### 4. Backend Restart
```bash
cd backend
# Restart Flask server to load new .env
python app.py
```

---

## 🔧 Google Cloud Console Setup

Make sure these are configured in Google Cloud Console:

### Android OAuth Client
- **Type:** Android
- **Package Name:** `com.example.kids_commerce`
- **SHA-1:** Your app's signing certificate SHA-1
- **Client ID:** `19725108081-d03cnmvghsfr3tpevj05pnn2upr55vds.apps.googleusercontent.com`

### Web OAuth Client
- **Type:** Web application
- **Authorized JavaScript origins:**
  - `http://localhost:5000`
  - `http://172.20.10.12:5000`
  - Your production domain
- **Authorized redirect URIs:**
  - `http://localhost:5000/login/google/authorized`
  - `http://172.20.10.12:5000/login/google/authorized`
  - Your production callback URL
- **Client ID:** `19725108081-hna4pcv8mopmrbj5jnb95g4m5v9431q1.apps.googleusercontent.com`

---

## 📱 Platform-Specific Notes

### Android
- Uses Android Client ID automatically via `strings.xml`
- Google Sign-In plugin reads from resources
- No code changes needed

### Web
- Uses Web Client ID from meta tag
- Also configured in Flutter code
- Works in browser and PWA

### iOS (Future)
- Will use Web Client ID
- Requires additional setup in Xcode
- Add to Info.plist when needed

---

## 🐛 Troubleshooting

### "Sign-In Failed" Error
1. Check Client IDs match Google Cloud Console
2. Verify package name: `com.example.kids_commerce`
3. Check SHA-1 certificate is registered
4. Clear app data and try again

### Web Sign-In Not Working
1. Check authorized JavaScript origins
2. Verify redirect URIs are correct
3. Check browser console for errors
4. Try incognito mode

### Backend OAuth Errors
1. Restart Flask server after .env changes
2. Check environment variables loaded: `echo $GOOGLE_OAUTH_CLIENT_ID`
3. Verify client secret is correct

---

## 🔐 Security Notes

- ✅ Client IDs are public (safe to commit)
- ❌ Client Secret is private (keep in .env, never commit)
- ✅ Use different Client IDs for dev/prod
- ✅ Restrict authorized domains in production

---

## 📊 Summary

✅ **Backend** - Updated with both Android and Web Client IDs
✅ **Android** - strings.xml created with Web Client ID
✅ **Web** - index.html updated with meta tag
✅ **Flutter** - Config file created for easy access
✅ **Documentation** - Complete setup guide

**All systems updated and ready to use! 🎉**

---

## 🔄 Next Steps

1. **Clean build:**
   ```bash
   cd mobile_app
   flutter clean
   flutter pub get
   ```

2. **Test on Android:**
   ```bash
   flutter run -d android
   ```

3. **Test on Web:**
   ```bash
   flutter run -d chrome
   ```

4. **Restart backend:**
   ```bash
   cd backend
   python app.py
   ```

5. **Test Google Sign-In** on all platforms

---

**Setup Complete! Ready for Google Authentication! 🚀**
