# Quick Start: Chat System Testing

## 🚀 Fast Setup (5 minutes)

### Step 1: Check Database
```bash
cd backend
python check_chat_database.py
```

This will:
- ✓ Verify chat_message table exists
- ✓ Show available test users
- ✓ Show available products
- ✓ Optionally create test data

**When prompted, type `y` to create test accounts automatically.**

### Step 2: Update Test Configuration

The script will show you the test credentials. Update `test_chat_system.py`:

```python
TEST_USERS = {
    'buyer': {
        'email': 'testbuyer@gmail.com',
        'password': 'Buyer123!',
    },
    'seller': {
        'email': 'testseller@gmail.com',
        'password': 'Seller123!',
    },
    'rider': {
        'email': 'testrider@gmail.com',
        'password': 'Rider123!',
    }
}

TEST_PRODUCT_ID = 1  # Use the product ID shown by check script
```

### Step 3: Run Tests
```bash
python test_chat_system.py
```

## 📊 Expected Output

```
╔════════════════════════════════════════════════════════════╗
║          CHAT SYSTEM COMPREHENSIVE TEST SUITE             ║
╚════════════════════════════════════════════════════════════╝

============================================================
  STEP 1: Authentication
============================================================

ℹ Logging in as buyer...
✓ Buyer logged in successfully
ℹ User ID: 2

ℹ Logging in as seller...
✓ Seller logged in successfully
ℹ User ID: 5

ℹ Logging in as rider...
✓ Rider logged in successfully
ℹ User ID: 7

============================================================
  STEP 2: Buyer → Seller Product Chat
============================================================

ℹ Testing start product chat...
✓ Product chat started with seller ID: 5

ℹ Testing send product message from buyer...
✓ Product message sent (ID: 1)
  Message: What's the shipping cost to Manila?

...

============================================================
  TEST RESULTS SUMMARY
============================================================

Total Tests: 25
✓ Passed: 25
✗ Failed: 0

Success Rate: 100.0%

✓ 🎉 CHAT SYSTEM IS FULLY FUNCTIONAL! 🎉
```

## 🔍 Quick Tests

### Test Only Buyer-Seller Chat
```bash
python test_chat_system.py buyer-seller
```

### Test All Roles (Fast)
```bash
python test_chat_system.py quick
```

## 🐛 Troubleshooting

### Issue: "Cannot proceed without buyer login"
**Solution:** Make sure test accounts exist and credentials are correct
```bash
python check_chat_database.py
# Type 'y' when asked to create test data
```

### Issue: "Product not found"
**Solution:** Update TEST_PRODUCT_ID in test_chat_system.py
```bash
# Check available products
python check_chat_database.py
# Look for "Available Test Products" section
```

### Issue: "Connection refused"
**Solution:** Make sure backend server is running
```bash
# In another terminal
cd backend
python app.py
# or
flask run
```

### Issue: Tests fail with 401 errors
**Solution:** Check if accounts are active
```sql
-- Connect to database
sqlite3 instance/kids_ecommerce.db

-- Check user status
SELECT id, email, role, status FROM user 
WHERE email IN ('testbuyer@gmail.com', 'testseller@gmail.com', 'testrider@gmail.com');

-- Activate users if needed
UPDATE user SET status='active' 
WHERE email IN ('testbuyer@gmail.com', 'testseller@gmail.com', 'testrider@gmail.com');
```

## 📱 Testing with Mobile App

After backend tests pass, test with mobile app:

1. **Login as Buyer**
   - Open product detail page
   - Tap "Chat with Seller" button
   - Send message
   - Check if message appears

2. **Login as Seller**
   - Open Messages/Inbox
   - Check if buyer's message appears
   - Reply to message
   - Check if reply is sent

3. **Login as Rider**
   - Open Messages
   - Send message to buyer
   - Check if message is delivered

## ✅ Success Checklist

- [ ] Database check passes
- [ ] Test accounts created
- [ ] All authentication tests pass
- [ ] Product chat works (buyer → seller)
- [ ] Direct messaging works (all combinations)
- [ ] Conversations list shows all chats
- [ ] Unread counts are accurate
- [ ] Messages marked as read when viewed
- [ ] Mobile app can send/receive messages

## 📝 Test Results

Record your test results:

| Test | Status | Notes |
|------|--------|-------|
| Database Check | ⬜ Pass / ⬜ Fail | |
| Buyer Login | ⬜ Pass / ⬜ Fail | |
| Seller Login | ⬜ Pass / ⬜ Fail | |
| Rider Login | ⬜ Pass / ⬜ Fail | |
| Product Chat Start | ⬜ Pass / ⬜ Fail | |
| Send Product Message | ⬜ Pass / ⬜ Fail | |
| Direct Messaging | ⬜ Pass / ⬜ Fail | |
| Get Conversations | ⬜ Pass / ⬜ Fail | |
| Unread Count | ⬜ Pass / ⬜ Fail | |
| Mobile App Chat | ⬜ Pass / ⬜ Fail | |

## 🎯 Next Steps

After all tests pass:

1. ✅ **Deploy to Production**
   - Update production database
   - Test with real users
   - Monitor error logs

2. 📊 **Monitor Performance**
   - Check response times
   - Monitor database queries
   - Watch for errors

3. 🔔 **Test Real-time Features**
   - Socket.IO notifications
   - Typing indicators
   - Message delivery

4. 📱 **Mobile App Integration**
   - Test on iOS
   - Test on Android
   - Check push notifications

## 📞 Support

If tests fail:
1. Check `CHAT_MESSAGING_FIX.md` for detailed API documentation
2. Check `CHAT_TEST_GUIDE.md` for manual testing steps
3. Review error logs in terminal
4. Check database with `check_chat_database.py`

---

**Ready to test?** Run: `python check_chat_database.py`
