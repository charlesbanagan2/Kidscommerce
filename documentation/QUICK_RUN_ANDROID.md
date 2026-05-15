# 🚀 QUICK RUN - Android Testing

## Simplest Way to Test App

### Prerequisites Checklist:
- ✓ Backend running: `python backend/app.py`
- ✓ Android phone connected via **USB cable**
- ✓ **USB Debugging enabled** on phone
- ✓ Flutter installed
- ✓ Phone and PC on **same WiFi**

---

## 3-Step Process

### Step 1: Start Backend
```powershell
cd c:\Users\mnban\Documents\kids
python backend/app.py
```
**Leave this running** - you'll see: `Running on http://0.0.0.0:5000`

---

### Step 2: Connect Phone

1. **Connect Android phone via USB cable**
2. **Go to Settings > Developer Options**
3. **Enable USB Debugging** (if not already enabled)
4. **Click "Allow USB Debugging" popup on phone**
5. Wait a few seconds...

---

### Step 3: Launch App

```powershell
cd c:\Users\mnban\Documents\kids\mobile_app
flutter run
```

**What happens:**
- Flutter finds your phone automatically
- App installs on phone
- App launches
- You'll see login screen

---

## 📝 Login on Phone

When app opens:

1. **Step 1:** Select "Buyer"
2. **Step 2:** Enter info with test password
3. **Step 3:** Enter address  
4. **Login:** Use test credentials:
   - Email: `testbuyer@test.com`
   - Password: `test123`

---

## ✅ Expected Results

| Action | Result |
|--------|--------|
| Select Buyer | Auto-advance to Step 2 ✓ |
| Enter password | Strength bar shows red/green ✓ |
| Click eye icon | Password visible/hidden ✓ |
| Enter wrong email | Shows error in red ✓ |
| Skip required field | Can't proceed ✓ |
| Enter credentials | Login successful → Dashboard ✓ |

---

## 🐛 Troubleshooting

### "No devices found"
```
1. Check USB cable connection
2. Check USB Debugging is ON
3. Accept USB Debugging popup on phone
4. Restart: unplug USB, plug back in
```

### "Connection Error" after login
```
1. Make sure phone is on SAME WiFi as PC
2. Test: Open phone browser to http://192.168.1.20:5000/
3. Should load Kids Kingdom login page
4. If not: Backend not accessible from phone network
```

### "App won't install"
```
# Uninstall old version
adb uninstall com.example.kids_commerce

# Try again
flutter run
```

### "Flutter command not found"
```
# Add Flutter to PATH in Windows:
# Settings > Environment Variables > PATH > Add: C:\flutter\bin
# Restart PowerShell
```

---

## 🔥 Hot Reload (After Code Changes)

While `flutter run` is active in terminal:

```
Press 'r' - Hot reload (quick)
Press 'R' - Hot restart (full rebuild)
Press 'q' - Quit
```

---

## 📊 Test Checklist

In the app, test these:

**Step 1 - Role Selection:**
- [ ] Tap Buyer - advances to Step 2
- [ ] Tap Rider - shows different role

**Step 2 - Personal Info:**
- [ ] First name shows error if empty
- [ ] Phone auto-starts with "09"
- [ ] Password strength bar shows color
- [ ] Eye icon shows/hides password
- [ ] Both password fields have eye icon
- [ ] Confirm password error if mismatch

**Step 3 - Address:**
- [ ] Street address field appears
- [ ] City/Province fields appear
- [ ] Buyer: Valid ID section (blue)
- [ ] Rider: Vehicle section (green)

**Login:**
- [ ] testbuyer@test.com / test123 works
- [ ] Success screen appears
- [ ] Wrong password shows error

---

## 📱 Tips

- Hot reload is fast for UI changes: Press `r`
- Keep phone charged
- Keep backend terminal open
- Check WiFi connection if API errors
- Logs show in same terminal as `flutter run`

---

## ✨ That's It!

You're ready to test the Kids Kingdom Android app! 🎉

