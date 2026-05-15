# Manual Chat System Test Guide

## Prerequisites
1. Backend server running on `http://localhost:5000`
2. Three test accounts created:
   - Buyer account
   - Seller account (with approved seller application)
   - Rider account (with approved rider application)
3. At least one product created by the seller

## Setup Test Accounts

### Option 1: Use Existing Accounts
Update these credentials in `test_chat_system.py`:
```python
TEST_USERS = {
    'buyer': {'email': 'your_buyer@gmail.com', 'password': 'YourPassword123!'},
    'seller': {'email': 'your_seller@gmail.com', 'password': 'YourPassword123!'},
    'rider': {'email': 'your_rider@gmail.com', 'password': 'YourPassword123!'}
}
TEST_PRODUCT_ID = 1  # Update with actual product ID
```

### Option 2: Create Test Accounts via API
```bash
# Create Buyer
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testbuyer@gmail.com",
    "password": "Buyer123!",
    "first_name": "Test",
    "last_name": "Buyer",
    "phone": "09123456789",
    "role": "buyer"
  }'

# Create Seller (then approve via admin panel)
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testseller@gmail.com",
    "password": "Seller123!",
    "first_name": "Test",
    "last_name": "Seller",
    "phone": "09123456790",
    "role": "seller"
  }'

# Create Rider (then approve via admin panel)
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testrider@gmail.com",
    "password": "Rider123!",
    "first_name": "Test",
    "last_name": "Rider",
    "phone": "09123456791",
    "role": "rider",
    "vehicle_type": "Motorcycle",
    "vehicle_number": "ABC123"
  }'
```

## Running Tests

### Full Test Suite (Recommended)
```bash
cd backend
python test_chat_system.py
```

This will test:
- ✓ Authentication for all roles
- ✓ Buyer → Seller product chat
- ✓ Seller → Buyer responses
- ✓ Buyer ↔ Seller direct messaging
- ✓ Buyer ↔ Rider messaging
- ✓ Seller ↔ Rider messaging
- ✓ Conversations list
- ✓ Unread message counts

### Quick Test (Faster)
```bash
python test_chat_system.py quick
```

### Buyer-Seller Only Test
```bash
python test_chat_system.py buyer-seller
```

## Manual Testing with cURL

### 1. Login and Get Tokens

**Buyer Login:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "testbuyer@gmail.com", "password": "Buyer123!"}' \
  | jq -r '.access_token'
```

**Seller Login:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "testseller@gmail.com", "password": "Seller123!"}' \
  | jq -r '.access_token'
```

**Rider Login:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "testrider@gmail.com", "password": "Rider123!"}' \
  | jq -r '.access_token'
```

Save the tokens as environment variables:
```bash
export BUYER_TOKEN="<buyer_token_here>"
export SELLER_TOKEN="<seller_token_here>"
export RIDER_TOKEN="<rider_token_here>"
```

### 2. Test Product Chat (Buyer → Seller)

**Start Product Chat:**
```bash
curl -X POST http://localhost:5000/api/v1/chat/product/start \
  -H "Authorization: Bearer $BUYER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "message": "Hi! Is this product still available?"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "conversation": {
    "peer_id": 5,
    "product_id": 1
  }
}
```

**Send Product Message:**
```bash
curl -X POST http://localhost:5000/api/v1/chat/product/send \
  -H "Authorization: Bearer $BUYER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "message": "What is the shipping cost?"
  }'
```

**Get Product Messages (Seller View):**
```bash
curl -X GET http://localhost:5000/api/v1/chat/product/1/messages \
  -H "Authorization: Bearer $SELLER_TOKEN"
```

**Seller Responds:**
```bash
curl -X POST http://localhost:5000/api/v1/chat/product/send \
  -H "Authorization: Bearer $SELLER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "message": "Shipping is ₱50 to Metro Manila!"
  }'
```

### 3. Test Direct Messaging (Buyer ↔ Rider)

**Buyer Sends Message to Rider:**
```bash
curl -X POST http://localhost:5000/api/v1/chat/send \
  -H "Authorization: Bearer $BUYER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_id": 7,
    "message": "Can you deliver to Quezon City?"
  }'
```

**Rider Responds:**
```bash
curl -X POST http://localhost:5000/api/v1/chat/send \
  -H "Authorization: Bearer $RIDER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_id": 2,
    "message": "Yes! I can deliver there in 30 minutes."
  }'
```

**Get Messages Between Buyer and Rider:**
```bash
curl -X GET http://localhost:5000/api/v1/chat/messages/7 \
  -H "Authorization: Bearer $BUYER_TOKEN"
```

### 4. Test Conversations

**Get All Conversations (Buyer):**
```bash
curl -X GET http://localhost:5000/api/v1/chat/conversations \
  -H "Authorization: Bearer $BUYER_TOKEN"
```

**Get Product Conversations (Seller):**
```bash
curl -X GET http://localhost:5000/api/v1/chat/conversations/product \
  -H "Authorization: Bearer $SELLER_TOKEN"
```

### 5. Test Unread Count

**Get Unread Count:**
```bash
curl -X GET http://localhost:5000/api/v1/chat/unread-count \
  -H "Authorization: Bearer $BUYER_TOKEN"
```

## Expected Test Results

### ✅ Success Indicators
- All API calls return 200/201 status codes
- Messages are sent and received correctly
- Conversations list shows all chats
- Unread counts update properly
- Product chat auto-fetches seller_id
- Direct messages work between all role combinations

### ❌ Failure Indicators
- 404 errors → Routes not registered properly
- 400 errors → Missing required fields or validation issues
- 401 errors → Authentication problems
- 500 errors → Server-side errors (check logs)

## Troubleshooting

### Issue: 404 Not Found
**Solution:** Make sure backend server is running and routes are registered
```bash
# Check if server is running
curl http://localhost:5000/api/v1/chat/conversations
```

### Issue: 401 Unauthorized
**Solution:** Token expired or invalid
```bash
# Re-login to get fresh token
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "testbuyer@gmail.com", "password": "Buyer123!"}'
```

### Issue: 400 Bad Request
**Solution:** Check request payload
```bash
# Make sure all required fields are present
# For product chat: product_id and message
# For direct chat: receiver_id and message
```

### Issue: Messages not appearing
**Solution:** Check database
```bash
# Connect to database and check chat_message table
sqlite3 instance/kids_ecommerce.db
SELECT * FROM chat_message ORDER BY created_at DESC LIMIT 10;
```

## Test Checklist

- [ ] Buyer can start product chat with seller
- [ ] Seller receives product chat messages
- [ ] Seller can respond to product inquiries
- [ ] Buyer can send direct messages to seller
- [ ] Buyer can send direct messages to rider
- [ ] Seller can send direct messages to rider
- [ ] All users can view their conversations
- [ ] Unread message counts are accurate
- [ ] Messages are marked as read when viewed
- [ ] Real-time notifications work (Socket.IO)

## Performance Benchmarks

Expected response times:
- Login: < 500ms
- Send message: < 200ms
- Get conversations: < 300ms
- Get messages: < 400ms
- Unread count: < 100ms

## Next Steps After Testing

1. ✅ If all tests pass → Deploy to production
2. ⚠️ If some tests fail → Check error logs and fix issues
3. 📱 Test with mobile app to ensure compatibility
4. 🔔 Verify real-time notifications work
5. 📊 Monitor performance in production
