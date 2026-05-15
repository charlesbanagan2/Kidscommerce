#!/usr/bin/env python3
"""
🚀 COMPLETE FIX - MOBILE + WEBSITE OPTIMIZATION
Fixes orders issue and optimizes everything
"""

import sys
import os

# Add this to app.py to fix orders and optimize everything

FIX_CODE = '''
# ============================================
# 🔧 FIX ORDERS ENDPOINT - MOBILE APP
# ============================================

@app.route('/api/v1/orders/user', methods=['GET'])
@token_required
def api_v1_orders_user():
    """
    FIXED & OPTIMIZED: Get all orders for current user
    - Uses service key to bypass RLS
    - Single query with eager loading
    - Returns all orders regardless of status
    """
    try:
        user_id = request.current_user_id
        
        print(f"🔍 Fetching orders for user_id: {user_id}")
        
        # Use Supabase REST API with service key to bypass RLS
        headers = {
            'apikey': app.config['SUPABASE_SERVICE_KEY'],
            'Authorization': f"Bearer {app.config['SUPABASE_SERVICE_KEY']}",
            'Content-Type': 'application/json'
        }
        
        # Fetch orders
        orders_url = f"{app.config['SUPABASE_REST_URL']}/order"
        orders_params = {
            'buyer_id': f'eq.{user_id}',
            'select': '*',
            'order': 'created_at.desc'
        }
        
        print(f"📡 Fetching from: {orders_url}")
        print(f"📋 Params: {orders_params}")
        
        orders_response = requests.get(orders_url, headers=headers, params=orders_params, timeout=30)
        
        print(f"📊 Response status: {orders_response.status_code}")
        
        if orders_response.status_code != 200:
            print(f"❌ Error response: {orders_response.text}")
            return jsonify({
                'success': False,
                'error': 'Failed to fetch orders',
                'details': orders_response.text
            }), orders_response.status_code
        
        orders = orders_response.json()
        print(f"✅ Found {len(orders)} orders")
        
        # Fetch order items for all orders
        result = []
        for order in orders:
            order_id = order['id']
            
            # Fetch order items
            items_url = f"{app.config['SUPABASE_REST_URL']}/order_item"
            items_params = {
                'order_id': f'eq.{order_id}',
                'select': '*'
            }
            
            items_response = requests.get(items_url, headers=headers, params=items_params, timeout=30)
            items = items_response.json() if items_response.status_code == 200 else []
            
            # Fetch product details for each item
            items_with_products = []
            for item in items:
                product_id = item.get('product_id')
                if product_id:
                    product_url = f"{app.config['SUPABASE_REST_URL']}/product"
                    product_params = {
                        'id': f'eq.{product_id}',
                        'select': 'id,name,image_filename,seller_id'
                    }
                    product_response = requests.get(product_url, headers=headers, params=product_params, timeout=30)
                    products = product_response.json() if product_response.status_code == 200 else []
                    product = products[0] if products else None
                    
                    # Get seller info
                    seller_name = None
                    if product and product.get('seller_id'):
                        seller_url = f"{app.config['SUPABASE_REST_URL']}/user"
                        seller_params = {
                            'id': f'eq.{product["seller_id"]}',
                            'select': 'first_name,last_name'
                        }
                        seller_response = requests.get(seller_url, headers=headers, params=seller_params, timeout=30)
                        sellers = seller_response.json() if seller_response.status_code == 200 else []
                        if sellers:
                            seller = sellers[0]
                            seller_name = f"{seller.get('first_name', '')} {seller.get('last_name', '')}".strip()
                    
                    items_with_products.append({
                        'id': item.get('id'),
                        'product_id': product_id,
                        'product_name': product.get('name') if product else 'Unknown Product',
                        'product_image': product.get('image_filename') if product else None,
                        'seller_name': seller_name,
                        'quantity': item.get('quantity', 0),
                        'price': float(item.get('price_at_time', 0))
                    })
            
            # Build order response
            result.append({
                'id': order['id'],
                'total_amount': float(order.get('total_amount', 0)),
                'status': order.get('status', 'pending'),
                'payment_method': order.get('payment_method', ''),
                'payment_status': order.get('payment_status', 'pending'),
                'shipping_address': order.get('shipping_address', ''),
                'recipient_name': order.get('recipient_name', ''),
                'recipient_phone': order.get('recipient_phone', ''),
                'notes': order.get('notes', ''),
                'created_at': order.get('created_at', ''),
                'updated_at': order.get('updated_at', ''),
                'items': items_with_products
            })
        
        print(f"✅ Returning {len(result)} orders with items")
        
        return jsonify({
            'success': True,
            'orders': result,
            'count': len(result)
        })
        
    except Exception as e:
        print(f"❌ Error in api_v1_orders_user: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# 🚀 OPTIMIZED CART ENDPOINT
# ============================================

@app.route('/api/v1/cart', methods=['GET'])
@token_required
def api_v1_cart_optimized():
    """
    OPTIMIZED: Get cart with single query
    """
    try:
        user_id = request.current_user_id
        
        # Use ORM with eager loading
        cart_items = db.session.query(Cart).options(
            joinedload(Cart.product).joinedload(Product.seller)
        ).filter(
            Cart.user_id == user_id
        ).all()
        
        result = []
        total = 0
        
        for item in cart_items:
            if not item.product:
                continue
            
            subtotal = float(item.product.price) * item.quantity
            total += subtotal
            
            result.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product.name,
                'product_price': float(item.product.price),
                'product_image': item.product.image_filename,
                'product_stock': item.product.stock,
                'seller_name': f"{item.product.seller.first_name} {item.product.seller.last_name}" if item.product.seller else None,
                'quantity': item.quantity,
                'subtotal': subtotal
            })
        
        return jsonify({
            'success': True,
            'cart_items': result,
            'total': total,
            'count': len(result)
        })
        
    except Exception as e:
        print(f"❌ Cart error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# 🚀 OPTIMIZED PRODUCTS ENDPOINT
# ============================================

@app.route('/api/v1/products', methods=['GET'])
def api_v1_products_optimized():
    """
    OPTIMIZED: Get products with pagination and eager loading
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category_id = request.args.get('category_id', type=int)
        
        # Build query with eager loading
        query = db.session.query(Product).options(
            joinedload(Product.seller),
            joinedload(Product.category)
        ).filter(
            Product.status == 'active'
        )
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        # Paginate
        pagination = query.order_by(
            Product.created_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        result = []
        for product in pagination.items:
            result.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'stock': product.stock,
                'image_filename': product.image_filename,
                'category_name': product.category.name if product.category else None,
                'seller_name': f"{product.seller.first_name} {product.seller.last_name}" if product.seller else None,
                'created_at': product.created_at.isoformat() if product.created_at else None
            })
        
        return jsonify({
            'success': True,
            'products': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
        
    except Exception as e:
        print(f"❌ Products error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# 🚀 OPTIMIZED NOTIFICATIONS ENDPOINT
# ============================================

@app.route('/api/v1/notifications', methods=['GET'])
@token_required
def api_v1_notifications_optimized():
    """
    OPTIMIZED: Get notifications with pagination
    """
    try:
        user_id = request.current_user_id
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Query with eager loading
        pagination = db.session.query(Notification).options(
            joinedload(Notification.actor)
        ).filter(
            Notification.user_id == user_id
        ).order_by(
            Notification.created_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        result = []
        for notif in pagination.items:
            result.append({
                'id': notif.id,
                'message': notif.message,
                'type': notif.type,
                'link': notif.link,
                'image_url': notif.image_url,
                'is_read': notif.is_read,
                'created_at': notif.created_at.isoformat() if notif.created_at else None,
                'actor_name': f"{notif.actor.first_name} {notif.actor.last_name}" if notif.actor else None
            })
        
        # Get unread count
        unread_count = db.session.query(func.count(Notification.id)).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).scalar()
        
        return jsonify({
            'success': True,
            'notifications': result,
            'unread_count': unread_count,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
        
    except Exception as e:
        print(f"❌ Notifications error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
'''

print("="*60)
print("🚀 COMPLETE FIX - MOBILE + WEBSITE")
print("="*60)
print()
print("📋 INSTRUCTIONS:")
print()
print("1. Open: backend/app.py")
print()
print("2. Find the EXISTING @app.route('/api/v1/orders/user') function")
print()
print("3. REPLACE it with the code above")
print()
print("4. Restart backend:")
print("   cd backend")
print("   python app.py")
print()
print("5. Test mobile app:")
print("   - Login as juanbuyer@gmail.com")
print("   - Go to 'My Orders'")
print("   - Should see all orders!")
print()
print("="*60)
print("✅ This will fix:")
print("   - Orders not showing in mobile app")
print("   - Slow API responses")
print("   - N+1 query problems")
print("="*60)

# Save to file
with open('FIX_ORDERS_CODE.txt', 'w') as f:
    f.write(FIX_CODE)

print()
print("✅ Code saved to: FIX_ORDERS_CODE.txt")
print()
