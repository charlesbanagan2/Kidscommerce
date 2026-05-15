# Rider System - Complete Fixes

## Problems Identified & Solutions

---

## ❌ PROBLEM 1: Multiple Conflicting API Files

**Issue**: You have 3 different rider API files with overlapping endpoints:
- `rider_complete_api.py` - Uses `/api/rider/*` endpoints
- `rider_mobile_only_api.py` - Uses `/api/v1/rider/*` endpoints  
- `rider_api.py` - Unknown endpoints (need to check)

**Impact**: 
- Endpoint conflicts causing 404 errors
- Mobile app calling wrong endpoints
- Inconsistent behavior

**Solution**: Use ONLY ONE API file

### ✅ Fix: Consolidate to Single API File

**Decision**: Use `rider_mobile_only_api.py` as the single source of truth

**Action Steps**:

1. **Delete or rename old files**:
   ```bash
   cd backend
   mv rider_complete_api.py rider_complete_api.py.OLD
   mv rider_api.py rider_api.py.OLD
   ```

2. **Update app.py to import only mobile API**:
   ```python
   # Remove these if they exist:
   # from rider_complete_api import *
   # from rider_api import *
   
   # Add only this:
   from rider_mobile_only_api import *
   ```

3. **Update mobile app to use correct endpoints**:
   - Change ALL `/api/rider/*` to `/api/v1/rider/*`

---

## ❌ PROBLEM 2: Endpoint Mismatch in Mobile App

**Issue**: Mobile app services use wrong endpoint paths

**Files Affected**:
- `rider_service.dart` - Uses `/api/rider/*` (WRONG)
- `rider_mobile_service.dart` - Uses `/api/v1/rider/*` (CORRECT)

**Solution**: Use ONLY `rider_mobile_service.dart`

### ✅ Fix: Update Mobile App Imports

**File**: `rider_available_orders_screen.dart`

**Change**:
```dart
// OLD (WRONG):
import '../../services/rider_service.dart';

// NEW (CORRECT):
import '../../services/rider_mobile_service.dart';
```

**Update all method calls**:
```dart
// OLD:
RiderService.initializeSocket(...)
RiderService.getAvailableOrders(...)
RiderService.acceptOrder(...)

// NEW:
RiderMobileService.initializeSocket(...)
RiderMobileService.getAvailableOrders(...)
RiderMobileService.acceptOrder(...)
```

---

## ❌ PROBLEM 3: Missing Decorators in API

**Issue**: Some endpoints missing required decorators

**Example from `rider_mobile_only_api.py`**:
```python
@app.route('/api/v1/rider/available-orders', methods=['GET'])
@token_required
@role_required('rider')
@active_user_required  # ❌ This decorator doesn't exist!
```

**Solution**: Remove `@active_user_required` or implement it

### ✅ Fix: Remove Non-Existent Decorator

**File**: `rider_mobile_only_api.py`

**Change ALL endpoints**:
```python
# BEFORE:
@app.route('/api/v1/rider/available-orders', methods=['GET'])
@token_required
@role_required('rider')
@active_user_required  # ❌ Remove this

# AFTER:
@app.route('/api/v1/rider/available-orders', methods=['GET'])
@token_required
@role_required('rider')
def api_rider_available_orders():
    # Add manual status check inside function
    user = db.session.get(User, request.current_user_id)
    if user.status != 'approved':
        return jsonify({
            'success': False,
            'error': 'Your account is not approved yet'
        }), 403
```

---

## ❌ PROBLEM 4: Missing Database Models

**Issue**: Code references models that may not exist:
- `RiderDetails` model
- `ChatMessage` model

**Solution**: Verify models exist or create them

### ✅ Fix: Add Missing Models to app.py

**Add to app.py** (if not already present):

```python
# Rider Details Model
class RiderDetails(db.Model):
    __tablename__ = 'rider_details'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_type = db.Column(db.String(50))  # motorcycle, bicycle, car
    vehicle_model = db.Column(db.String(100))
    plate_number = db.Column(db.String(20))
    valid_id_front = db.Column(db.String(255))
    valid_id_back = db.Column(db.String(255))
    drivers_license = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='rider_details')

# Chat Message Model
class ChatMessage(db.Model):
    __tablename__ = 'chat_message'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sender': {
                'id': self.sender.id,
                'name': f"{self.sender.first_name} {self.sender.last_name}",
                'role': self.sender.role,
                'profile_picture': self.sender.profile_picture
            },
            'receiver': {
                'id': self.receiver.id,
                'name': f"{self.receiver.first_name} {self.receiver.last_name}",
                'role': self.receiver.role,
                'profile_picture': self.receiver.profile_picture
            }
        }
```

**Add to Order model** (if missing):
```python
# Add these columns to Order model
rider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
picked_up_at = db.Column(db.DateTime, nullable=True)
picked_up_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
delivered_at = db.Column(db.DateTime, nullable=True)
delivered_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
rider_earnings = db.Column(db.Float, default=0.0)

# Add relationship
rider = db.relationship('User', foreign_keys=[rider_id], backref='rider_orders')
```

---

## ❌ PROBLEM 5: Missing Helper Functions

**Issue**: Code calls functions that don't exist:
- `push_notification()`
- `join_room()` and `emit()` from Socket.IO

**Solution**: Import or implement these functions

### ✅ Fix: Add Missing Imports

**Add to top of rider_mobile_only_api.py**:

```python
from flask_socketio import emit, join_room, leave_room

# If push_notification doesn't exist, create stub or remove calls
def push_notification(user_id, message, type=None, order_id=None, actor_user_id=None):
    """Push notification stub - implement with FCM later"""
    try:
        # TODO: Implement Firebase Cloud Messaging
        app.logger.info(f"Push notification to user {user_id}: {message}")
    except Exception as e:
        app.logger.error(f"Push notification error: {str(e)}")
```

---

## ❌ PROBLEM 6: Socket.IO Not Properly Initialized

**Issue**: Socket.IO events won't work if not properly set up

**Solution**: Ensure Socket.IO is initialized in app.py

### ✅ Fix: Verify Socket.IO Setup

**Check app.py has**:

```python
from flask_socketio import SocketIO, emit, join_room, leave_room

# Initialize Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# At the end of file:
if __name__ == '__main__':
    # MUST use socketio.run(), NOT app.run()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

---

## ❌ PROBLEM 7: Database Not PostgreSQL

**Issue**: FCFS row-level locking requires PostgreSQL, not SQLite

**Solution**: Verify database is PostgreSQL

### ✅ Fix: Check Database Configuration

**In app.py**:

```python
# Check current database
print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Should be:
# postgresql://user:password@localhost/dbname

# NOT:
# sqlite:///kids_ecommerce.db
```

**If using SQLite, switch to PostgreSQL**:

```python
# Install PostgreSQL and psycopg2
# pip install psycopg2-binary

# Update config
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/kids_ecommerce'
```

---

## ❌ PROBLEM 8: Missing Seller Integration

**Issue**: When seller marks order "ready_for_pickup", riders aren't notified

**Solution**: Call `notify_riders_order_ready()` in seller endpoint

### ✅ Fix: Update Seller Order Status Endpoint

**Find seller endpoint that updates order status** (in app.py):

```python
@app.route('/api/seller/orders/<int:order_id>/status', methods=['PUT'])
@token_required
@role_required('seller')
def update_order_status(order_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        order.status = new_status
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        # ✅ ADD THIS: Notify riders when ready for pickup
        if new_status == 'ready_for_pickup':
            notify_riders_order_ready(order.id)
        
        return jsonify({'success': True, 'order': order.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
```

---

## ❌ PROBLEM 9: Chat API Missing Socket.IO Context

**Issue**: Socket.IO events in chat_complete_api.py use `request.current_user_id` which doesn't exist in Socket.IO context

**Solution**: Use Socket.IO authentication middleware

### ✅ Fix: Add Socket.IO Authentication

**Add to app.py**:

```python
from flask_socketio import disconnect

@socketio.on('connect')
def handle_connect():
    """Authenticate Socket.IO connection"""
    try:
        # Get token from query params or headers
        token = request.args.get('token')
        if not token:
            disconnect()
            return False
        
        # Verify token and set user context
        # (Implement your token verification logic)
        user_id = verify_token(token)  # Your function
        if user_id:
            request.current_user_id = user_id
            return True
        else:
            disconnect()
            return False
    except:
        disconnect()
        return False
```

---

## ❌ PROBLEM 10: Mobile App Using Wrong Service File

**Issue**: `rider_available_orders_screen.dart` imports `rider_service.dart` instead of `rider_mobile_service.dart`

**Solution**: Update import

### ✅ Fix: Update Screen Import

**File**: `mobile_app/lib/screens/rider/rider_available_orders_screen.dart`

**Line 4 - Change**:
```dart
// BEFORE:
import '../../services/rider_service.dart';

// AFTER:
import '../../services/rider_mobile_service.dart';
```

**Update all RiderService calls to RiderMobileService**:
```dart
// Find and replace in file:
RiderService. → RiderMobileService.
```

---

## 🔧 COMPLETE FIX CHECKLIST

### Backend Fixes

- [ ] **Delete old API files**
  ```bash
  cd backend
  mv rider_complete_api.py rider_complete_api.py.OLD
  mv rider_api.py rider_api.py.OLD
  ```

- [ ] **Update app.py imports**
  ```python
  from rider_mobile_only_api import *
  from chat_complete_api import *
  ```

- [ ] **Remove @active_user_required decorator** from all endpoints in `rider_mobile_only_api.py`

- [ ] **Add missing models** (RiderDetails, ChatMessage) to app.py

- [ ] **Add missing imports** to rider_mobile_only_api.py:
  ```python
  from flask_socketio import emit, join_room, leave_room
  ```

- [ ] **Add push_notification stub** to rider_mobile_only_api.py

- [ ] **Verify Socket.IO initialization** in app.py:
  ```python
  socketio = SocketIO(app, cors_allowed_origins="*")
  ```

- [ ] **Check database is PostgreSQL** (not SQLite)

- [ ] **Update seller endpoint** to call `notify_riders_order_ready()`

- [ ] **Add Socket.IO authentication** middleware

### Mobile App Fixes

- [ ] **Update rider_available_orders_screen.dart**:
  - Change import to `rider_mobile_service.dart`
  - Replace all `RiderService.` with `RiderMobileService.`

- [ ] **Delete or rename old service file**:
  ```bash
  cd mobile_app/lib/services
  mv rider_service.dart rider_service.dart.OLD
  ```

- [ ] **Verify all rider screens use RiderMobileService**:
  - rider_available_orders_screen.dart
  - rider_dashboard_screen.dart
  - rider_my_deliveries_screen.dart

### Database Fixes

- [ ] **Run migration to add missing columns**:
  ```sql
  ALTER TABLE "order" ADD COLUMN IF NOT EXISTS rider_id INTEGER;
  ALTER TABLE "order" ADD COLUMN IF NOT EXISTS picked_up_at TIMESTAMP;
  ALTER TABLE "order" ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP;
  ALTER TABLE "order" ADD COLUMN IF NOT EXISTS rider_earnings FLOAT DEFAULT 0.0;
  ```

- [ ] **Create rider_details table**:
  ```sql
  CREATE TABLE IF NOT EXISTS rider_details (
      id SERIAL PRIMARY KEY,
      user_id INTEGER REFERENCES "user"(id),
      vehicle_type VARCHAR(50),
      vehicle_model VARCHAR(100),
      plate_number VARCHAR(20),
      valid_id_front VARCHAR(255),
      valid_id_back VARCHAR(255),
      drivers_license VARCHAR(255),
      status VARCHAR(20) DEFAULT 'pending',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

- [ ] **Create chat_message table**:
  ```sql
  CREATE TABLE IF NOT EXISTS chat_message (
      id SERIAL PRIMARY KEY,
      sender_id INTEGER REFERENCES "user"(id),
      receiver_id INTEGER REFERENCES "user"(id),
      message TEXT NOT NULL,
      is_read BOOLEAN DEFAULT FALSE,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  
  CREATE INDEX idx_chat_sender ON chat_message(sender_id);
  CREATE INDEX idx_chat_receiver ON chat_message(receiver_id);
  CREATE INDEX idx_chat_is_read ON chat_message(is_read);
  ```

---

## 🚀 TESTING AFTER FIXES

### 1. Test Backend Startup

```bash
cd backend
python app.py
```

**Expected Output**:
```
* Running on http://0.0.0.0:5000
* Socket.IO initialized
* Database: postgresql://...
```

### 2. Test Rider Registration

```bash
curl -X POST http://192.168.1.20:5000/api/v1/rider/register \
  -F "email=testrider@test.com" \
  -F "password=test123" \
  -F "first_name=Test" \
  -F "last_name=Rider" \
  -F "phone=09123456789" \
  -F "vehicle_type=motorcycle" \
  -F "plate_number=ABC123"
```

**Expected**: `{"success": true, "status": "pending"}`

### 3. Test Available Orders (After Approval)

```bash
curl -X GET http://192.168.1.20:5000/api/v1/rider/available-orders \
  -H "Authorization: Bearer <rider_token>"
```

**Expected**: `{"success": true, "orders": [...]}`

### 4. Test FCFS Accept Order

Run the automated test script:
```bash
python test_rider_workflow.py
```

**Expected**: Only 1 rider succeeds, other gets 409 Conflict

---

## 📝 SUMMARY OF CHANGES

### Files to Modify

1. **backend/app.py**
   - Add missing models (RiderDetails, ChatMessage)
   - Import rider_mobile_only_api
   - Add Socket.IO authentication
   - Update seller endpoint

2. **backend/rider_mobile_only_api.py**
   - Remove @active_user_required decorator
   - Add missing imports
   - Add push_notification stub

3. **mobile_app/lib/screens/rider/rider_available_orders_screen.dart**
   - Change import to rider_mobile_service.dart
   - Replace RiderService with RiderMobileService

4. **Database**
   - Add missing columns to Order table
   - Create rider_details table
   - Create chat_message table

### Files to Delete/Rename

1. **backend/rider_complete_api.py** → rider_complete_api.py.OLD
2. **backend/rider_api.py** → rider_api.py.OLD
3. **mobile_app/lib/services/rider_service.dart** → rider_service.dart.OLD

---

## ✅ SUCCESS CRITERIA

After applying all fixes, you should have:

1. ✅ Backend starts without errors
2. ✅ Rider registration works
3. ✅ Approved riders can see available orders
4. ✅ Socket.IO notifications work in real-time
5. ✅ FCFS logic prevents race conditions
6. ✅ Only one rider can accept each order
7. ✅ Mobile app connects successfully
8. ✅ All API endpoints return correct responses

---

**Ready to apply fixes!** Start with backend fixes first, then mobile app, then test.
