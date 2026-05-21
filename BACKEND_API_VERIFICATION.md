# 🔧 Backend API Routes Verification

## ❌ 404 Error: POST /api/v1/buyer/cart

### Issue
The mobile app is getting 404 errors when trying to add items to cart.

### Required Backend Routes

Add these routes to your Flask backend:

```python
# ============================================
# CART API ROUTES - Add to your backend
# ============================================

@app.route('/api/v1/buyer/cart', methods=['GET'])
@jwt_required()
def get_cart():
    """Get buyer's cart items"""
    try:
        user_id = get_jwt_identity()
        # Your cart fetch logic here
        cart_items = fetch_cart_items(user_id)
        return jsonify({
            'success': True,
            'cart': cart_items
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1/buyer/cart', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add item to cart"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        if not product_id:
            return jsonify({
                'success': False,
                'error': 'Product ID is required'
            }), 400
        
        # Check product stock
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
            
        if product['stock'] < quantity:
            return jsonify({
                'success': False,
                'error': f'Only {product["stock"]} items available'
            }), 400
        
        # Add to cart logic
        cart_item = add_item_to_cart(user_id, product_id, quantity)
        
        return jsonify({
            'success': True,
            'message': 'Item added to cart',
            'cart_item': cart_item
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1/buyer/cart/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    """Update cart item quantity"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        quantity = data.get('quantity')
        
        if quantity is None or quantity < 1:
            return jsonify({
                'success': False,
                'error': 'Invalid quantity'
            }), 400
        
        # Update cart item
        updated_item = update_cart_quantity(user_id, item_id, quantity)
        
        return jsonify({
            'success': True,
            'cart_item': updated_item
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v1/buyer/cart/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    """Remove item from cart"""
    try:
        user_id = get_jwt_identity()
        
        # Remove from cart
        delete_cart_item(user_id, item_id)
        
        return jsonify({
            'success': True,
            'message': 'Item removed from cart'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

## ✅ Verification Checklist

Test these endpoints using Postman or curl:

### 1. GET Cart
```bash
curl -X GET http://192.168.1.26:5000/api/v1/buyer/cart \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected: 200 OK with cart items

### 2. POST Add to Cart
```bash
curl -X POST http://192.168.1.26:5000/api/v1/buyer/cart \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

Expected: 201 Created with cart item

### 3. PUT Update Cart Item
```bash
curl -X PUT http://192.168.1.26:5000/api/v1/buyer/cart/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 3}'
```

Expected: 200 OK with updated item

### 4. DELETE Remove from Cart
```bash
curl -X DELETE http://192.168.1.26:5000/api/v1/buyer/cart/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected: 200 OK with success message

---

## 🔍 Common Backend Issues

### Issue 1: Route Not Registered
**Symptom:** 404 errors
**Fix:** Ensure routes are registered before `app.run()`

### Issue 2: Missing JWT Decorator
**Symptom:** 401 Unauthorized
**Fix:** Add `@jwt_required()` to protected routes

### Issue 3: CORS Issues
**Symptom:** Blocked by CORS policy
**Fix:** Add CORS headers:
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### Issue 4: Wrong HTTP Method
**Symptom:** 405 Method Not Allowed
**Fix:** Ensure route accepts correct methods: `methods=['GET', 'POST']`

---

## 📋 Backend Testing Steps

1. ✅ Start Flask server: `python app.py`
2. ✅ Check server logs for route registration
3. ✅ Test each endpoint with Postman
4. ✅ Verify database updates
5. ✅ Test from mobile app
6. ✅ Check for 404/500 errors in logs

---

## 🚨 Critical Routes to Verify

- [ ] `GET /api/v1/buyer/cart`
- [ ] `POST /api/v1/buyer/cart`
- [ ] `PUT /api/v1/buyer/cart/<id>`
- [ ] `DELETE /api/v1/buyer/cart/<id>`
- [ ] `POST /api/v1/buyer/checkout`
- [ ] `GET /api/v1/buyer/orders`
- [ ] `GET /api/v1/products`

---

## 📝 Server Logs to Check

Look for these in your Flask console:

```
✅ GOOD:
 * Running on http://192.168.1.26:5000
 * Registered routes:
   - GET /api/v1/buyer/cart
   - POST /api/v1/buyer/cart

❌ BAD:
[404] POST /api/v1/buyer/cart - Route not found
```

---

## 🔧 Quick Fix Template

If routes are missing, add this to your Flask app:

```python
# Import at top
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# Add routes
@app.route('/api/v1/buyer/cart', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def handle_cart():
    if request.method == 'GET':
        return get_cart()
    elif request.method == 'POST':
        return add_to_cart()
    # ... etc
```

---

**Priority:** 🔴 CRITICAL
**Estimated Fix Time:** 20 minutes
**Testing Time:** 10 minutes
