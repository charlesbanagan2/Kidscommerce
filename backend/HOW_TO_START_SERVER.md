# How to Start Backend Server and Run Tests

## Step 1: Start the Backend Server

### Option A: Using the Batch File (Easiest)
```bash
# Double-click this file or run in terminal:
START_SERVER.bat
```

### Option B: Using Command Line
```bash
cd backend
python app.py
```

### Option C: Using Flask CLI
```bash
cd backend
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
```

## Step 2: Verify Server is Running

Open a browser and go to:
```
http://localhost:5000
```

You should see the Kids Commerce homepage.

## Step 3: Open a New Terminal for Tests

**IMPORTANT:** Keep the server running in the first terminal!

Open a **NEW** terminal window:

```bash
cd backend
python check_chat_database.py
```

Type `y` when asked to create test data.

## Step 4: Run the Tests

In the same terminal (with server still running in the other):

```bash
python test_chat_system.py
```

## Common Issues

### Issue: "Connection refused" or "Port 5000 already in use"

**Solution 1: Check if server is already running**
```bash
# Windows
netstat -ano | findstr :5000

# If something is using port 5000, kill it:
taskkill /PID <PID_NUMBER> /F
```

**Solution 2: Use a different port**
Edit `app.py` at the bottom:
```python
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)  # Changed to 5001
```

Then update `test_chat_system.py`:
```python
BASE_URL = "http://localhost:5001"  # Changed to 5001
```

### Issue: "Module not found" errors

**Solution: Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: Database errors

**Solution: Initialize database**
```bash
cd backend
python check_chat_database.py
# Type 'y' to create test data
```

## Quick Start Checklist

- [ ] Backend server is running (http://localhost:5000 works)
- [ ] Test accounts created (run check_chat_database.py)
- [ ] New terminal opened for tests
- [ ] Tests running (python test_chat_system.py)

## Terminal Setup

You need **TWO** terminal windows:

**Terminal 1 (Server):**
```
C:\Users\mnban\Documents\kids\backend> python app.py
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.100:5000
```

**Terminal 2 (Tests):**
```
C:\Users\mnban\Documents\kids\backend> python test_chat_system.py
✓ Buyer logged in successfully
✓ Seller logged in successfully
...
```

## Visual Guide

```
┌─────────────────────────────────────┐
│  Terminal 1: Backend Server         │
│  --------------------------------   │
│  > cd backend                       │
│  > python app.py                    │
│                                     │
│  Server running on port 5000...    │
│  (Keep this running!)               │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Terminal 2: Run Tests              │
│  --------------------------------   │
│  > cd backend                       │
│  > python check_chat_database.py    │
│  > python test_chat_system.py       │
│                                     │
│  Tests running...                   │
└─────────────────────────────────────┘
```

## Next Steps After Server Starts

1. ✅ Server running → Go to Step 3
2. ❌ Server errors → Check error messages
3. ❌ Port in use → Use different port or kill process

## Troubleshooting Server Startup

### Error: "Address already in use"
```bash
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <PID> /F

# Or use a different port in app.py
```

### Error: "Module 'flask' not found"
```bash
# Install dependencies
pip install flask flask-socketio flask-sqlalchemy
```

### Error: "Database locked"
```bash
# Close any database browsers
# Restart the server
```

## Success Indicators

✅ **Server Started Successfully:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.100:5000
Press CTRL+C to quit
```

✅ **Tests Running:**
```
============================================================
  STEP 1: Authentication
============================================================

ℹ Logging in as buyer...
✓ Buyer logged in successfully
```

## Ready to Start?

1. Open Terminal 1 → Run `START_SERVER.bat` or `python app.py`
2. Wait for "Running on http://127.0.0.1:5000"
3. Open Terminal 2 → Run `python test_chat_system.py`
4. Watch the tests run!

---

**Need help?** Make sure:
- ✓ You're in the `backend` folder
- ✓ Virtual environment is activated (if using one)
- ✓ Dependencies are installed
- ✓ Server is running in Terminal 1
- ✓ Tests are running in Terminal 2
