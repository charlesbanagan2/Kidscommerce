"""
Comprehensive test suite for all 4 phases of the e-commerce workflow.

PHASE 1: Landing Page & Buyer Window Shopping
PHASE 2: Seller to Admin Product Approval Flow
PHASE 3: Rider First-Come, First-Serve Logistics with Socket.IO
PHASE 4: Return and Refund Flow
"""

import pytest
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Product, Order, OrderItem, Cart, Category, DeliveryPersonnel
from flask import session


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def setup_users(client):
    """Create test users for buyer, seller, admin, and rider."""
    with app.app_context():
        # Create admin
        admin = User(
            email='admin@test.com',
            password='password123',
            first_name='Admin',
            last_name='User',
            phone='1234567890',
            address='Admin Address',
            role='admin',
            status='active'
        )
        db.session.add(admin)
        
        # Create seller
        seller = User(
            email='seller@test.com',
            password='password123',
            first_name='Seller',
            last_name='User',
            phone='1234567891',
            address='Seller Address',
            role='seller',
            status='active'
        )
        db.session.add(seller)
        
        # Create buyer
        buyer = User(
            email='buyer@test.com',
            password='password123',
            first_name='Buyer',
            last_name='User',
            phone='1234567892',
            address='Buyer Address',
            role='buyer',
            status='active'
        )
        db.session.add(buyer)
        
        # Create rider
        rider = User(
            email='rider@test.com',
            password='password123',
            first_name='Rider',
            last_name='User',
            phone='1234567893',
            address='Rider Address',
            role='rider',
            status='active'
        )
        db.session.add(rider)
        
        # Create category
        category = Category(name='Test Category', status='active')
        db.session.add(category)
        
        # Commit users and category first to get IDs
        db.session.commit()
        
        # Create rider profile after rider has an ID
        rider_profile = DeliveryPersonnel(
            user_id=rider.id,
            employee_id='EMP0001',
            name='Rider User',
            phone='1234567890',
            status='active'
        )
        db.session.add(rider_profile)
        db.session.commit()
        
        return {
            'admin_id': admin.id,
            'seller_id': seller.id,
            'buyer_id': buyer.id,
            'rider_id': rider.id,
            'category_id': category.id
        }


def login_user(client, user_id):
    """Helper to login a user by ID."""
    with app.app_context():
        user = db.session.get(User, user_id)
        user_name = f"{user.first_name} {user.last_name}"
        user_role = user.role
    
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['user_name'] = user_name
        sess['active_role'] = user_role


# ==================== PHASE 1 TESTS ====================

def test_phase1_home_shows_only_approved_products(client, setup_users):
    """Test that home page shows only approved products."""
    users = setup_users
    login_user(client, users['seller_id'])
    
    with app.app_context():
        # Create pending product
        pending_product = Product(
            name='Pending Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='pending'
        )
        db.session.add(pending_product)
        
        # Create approved product
        approved_product = Product(
            name='Approved Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='approved'
        )
        db.session.add(approved_product)
        
        # Create rejected product
        rejected_product = Product(
            name='Rejected Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='rejected'
        )
        db.session.add(rejected_product)
        
        db.session.commit()
    
    # Logout and test home page (no login required)
    with client.session_transaction() as sess:
        sess.clear()
    
    response = client.get('/')
    assert response.status_code == 200
    # Should contain approved product
    assert b'Approved Product' in response.data
    # Should NOT contain pending or rejected
    assert b'Pending Product' not in response.data
    assert b'Rejected Product' not in response.data


def test_phase1_shop_shows_only_approved_products(client, setup_users):
    """Test that shop page shows only approved products."""
    users = setup_users
    login_user(client, users['seller_id'])
    
    with app.app_context():
        # Create approved product
        approved_product = Product(
            name='Shop Approved Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='approved'
        )
        db.session.add(approved_product)
        
        # Create pending product
        pending_product = Product(
            name='Shop Pending Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='pending'
        )
        db.session.add(pending_product)
        
        db.session.commit()
    
    # Logout and test shop page (no login required)
    with client.session_transaction() as sess:
        sess.clear()
    
    response = client.get('/shop')
    assert response.status_code == 200
    assert b'Shop Approved Product' in response.data
    assert b'Shop Pending Product' not in response.data


def test_phase1_add_to_cart_requires_login(client, setup_users):
    """Test that add to cart redirects to login when not authenticated."""
    users = setup_users
    login_user(client, users['seller_id'])
    
    with app.app_context():
        # Create approved product
        product = Product(
            name='Test Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='approved'
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    
    # Logout
    with client.session_transaction() as sess:
        sess.clear()
    
    # Try to add to cart without login
    response = client.get(f'/add-to-cart/{product_id}')
    assert response.status_code == 302  # Redirect
    assert '/login' in response.location


def test_phase1_add_to_cart_approved_only(client, setup_users):
    """Test that only approved products can be added to cart."""
    users = setup_users
    login_user(client, users['buyer_id'])
    
    with app.app_context():
        # Create pending product
        pending_product = Product(
            name='Pending Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='pending'
        )
        db.session.add(pending_product)
        
        # Create approved product
        approved_product = Product(
            name='Approved Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='approved'
        )
        db.session.add(approved_product)
        
        db.session.commit()
    
    # Try to add pending product to cart
    response = client.get(f'/add-to-cart/{pending_product.id}')
    assert response.status_code == 302
    # Should redirect with error message
    
    # Try to add approved product to cart
    response = client.get(f'/add-to-cart/{approved_product.id}')
    assert response.status_code == 302


# ==================== PHASE 2 TESTS ====================

def test_phase2_seller_creates_pending_product(client, setup_users):
    """Test that seller creates product with pending status."""
    users = setup_users
    login_user(client, users['seller_id'])
    
    data = {
        'name': 'New Product',
        'description': 'Test description',
        'price': '100.0',
        'stock': '10',
        'category_id': str(users['category_id'])
    }
    
    response = client.post('/seller/add-product', data=data)
    assert response.status_code == 302
    
    with app.app_context():
        product = Product.query.filter_by(name='New Product').first()
        assert product is not None
        assert product.status == 'pending'
        assert product.seller_id == users['seller_id']


def test_phase2_admin_approves_product(client, setup_users):
    """Test that admin can approve pending product."""
    users = setup_users
    login_user(client, users['seller_id'])
    
    with app.app_context():
        # Create pending product
        product = Product(
            name='Pending for Approval',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='pending'
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    
    # Login as admin
    login_user(client, users['admin_id'])
    
    response = client.get(f'/admin/approve-product/{product_id}')
    assert response.status_code == 302
    
    with app.app_context():
        product = Product.query.get(product_id)
        assert product.status == 'approved'


def test_phase2_admin_rejects_product(client, setup_users):
    """Test that admin can reject pending product."""
    users = setup_users
    login_user(client, users['seller_id'])
    
    with app.app_context():
        # Create pending product
        product = Product(
            name='Pending for Rejection',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='pending'
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    
    # Login as admin
    login_user(client, users['admin_id'])
    
    response = client.get(f'/admin/reject-product/{product_id}?reason=Test%20reason')
    assert response.status_code == 302
    
    with app.app_context():
        product = Product.query.get(product_id)
        assert product.status == 'rejected'


# ==================== PHASE 3 TESTS ====================

def test_phase3_seller_marks_ready_for_pickup(client, setup_users):
    """Test that seller can mark order as ready for pickup."""
    users = setup_users
    login_user(client, users['buyer_id'])
    
    with app.app_context():
        # Create approved product
        product = Product(
            name='Test Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='approved'
        )
        db.session.add(product)
        
        # Create order
        order = Order(
            buyer_id=users['buyer_id'],
            total_amount=100.0,
            status='processing',
            payment_method='cod',
            payment_status='paid',
            shipping_address='Test Address'
        )
        db.session.add(order)
        db.session.commit()
        
        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            price_at_time=100.0
        )
        db.session.add(order_item)
        db.session.commit()
        order_id = order.id
    
    # Login as seller
    login_user(client, users['seller_id'])
    
    response = client.post(f'/seller/order/{order_id}/ready-for-pickup')
    assert response.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'ready_for_pickup'
        assert order.packed_by == users['seller_id']


def test_phase3_rider_accepts_order_race_condition(client, setup_users):
    """Test that rider acceptance has race condition prevention."""
    users = setup_users
    login_user(client, users['buyer_id'])
    
    with app.app_context():
        # Create approved product
        product = Product(
            name='Test Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='approved'
        )
        db.session.add(product)
        
        # Create order ready for pickup
        order = Order(
            buyer_id=users['buyer_id'],
            total_amount=100.0,
            status='ready_for_pickup',
            payment_method='cod',
            payment_status='paid',
            shipping_address='Test Address',
            rider_id=None
        )
        db.session.add(order)
        db.session.commit()
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            price_at_time=100.0
        )
        db.session.add(order_item)
        db.session.commit()
        order_id = order.id
    
    # First rider accepts
    login_user(client, users['rider_id'])
    response1 = client.post(f'/rider/order/{order_id}/accept')
    assert response1.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'accepted_by_rider'
        assert order.rider_id == users['rider_id']
    
    # Second rider tries to accept (should fail)
    rider2 = User(
        email='rider2@test.com',
        password='password123',
        first_name='Rider2',
        last_name='User',
        phone='1234567894',
        address='Rider2 Address',
        role='rider',
        status='active'
    )
    with app.app_context():
        db.session.add(rider2)
        db.session.commit()  # Commit to get ID
        rider2_profile = DeliveryPersonnel(
            user_id=rider2.id,
            employee_id='EMP0002',
            name='Rider2 User',
            phone='1234567894',
            status='active'
        )
        db.session.add(rider2_profile)
        db.session.commit()
    
    login_user(client, rider2.id)
    response2 = client.post(f'/rider/order/{order_id}/accept')
    assert response2.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        # Rider should still be the first rider
        assert order.rider_id == users['rider_id']


# ==================== PHASE 4 TESTS ====================

def test_phase4_buyer_requests_return(client, setup_users):
    """Test that buyer can request return for completed order."""
    users = setup_users
    login_user(client, users['buyer_id'])
    
    with app.app_context():
        # Create approved product
        product = Product(
            name='Test Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='approved'
        )
        db.session.add(product)
        
        # Create completed order
        order = Order(
            buyer_id=users['buyer_id'],
            total_amount=100.0,
            status='completed',
            payment_method='cod',
            payment_status='paid',
            shipping_address='Test Address'
        )
        db.session.add(order)
        db.session.commit()
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            price_at_time=100.0
        )
        db.session.add(order_item)
        db.session.commit()
        order_id = order.id
    
    data = {'return_reason': 'Product damaged'}
    response = client.post(f'/buyer/order/{order_id}/request-return', data=data)
    assert response.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'return_requested'
        assert order.return_reason == 'Product damaged'


def test_phase4_seller_approves_return(client, setup_users):
    """Test that seller can approve return request."""
    users = setup_users
    login_user(client, users['buyer_id'])
    
    with app.app_context():
        # Create approved product
        product = Product(
            name='Test Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='approved'
        )
        db.session.add(product)
        
        # Create order in return_requested status
        order = Order(
            buyer_id=users['buyer_id'],
            total_amount=100.0,
            status='return_requested',
            return_reason='Product damaged',
            payment_method='cod',
            payment_status='paid',
            shipping_address='Test Address',
            rider_id=users['rider_id']
        )
        db.session.add(order)
        db.session.commit()
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            price_at_time=100.0
        )
        db.session.add(order_item)
        db.session.commit()
        order_id = order.id
    
    # Login as seller
    login_user(client, users['seller_id'])
    
    response = client.post(f'/seller/order/{order_id}/approve-return')
    assert response.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'return_ready_for_pickup'
        assert order.rider_id is None  # Rider reset for first-come-first-serve


def test_phase4_rider_accepts_return(client, setup_users):
    """Test that rider can accept return pickup."""
    users = setup_users
    login_user(client, users['buyer_id'])
    
    with app.app_context():
        # Create approved product
        product = Product(
            name='Test Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='approved'
        )
        db.session.add(product)
        
        # Create order ready for return pickup
        order = Order(
            buyer_id=users['buyer_id'],
            total_amount=100.0,
            status='return_ready_for_pickup',
            return_reason='Product damaged',
            payment_method='cod',
            payment_status='paid',
            shipping_address='Test Address',
            rider_id=None
        )
        db.session.add(order)
        db.session.commit()
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            price_at_time=100.0
        )
        db.session.add(order_item)
        db.session.commit()
        order_id = order.id
    
    # Login as rider
    login_user(client, users['rider_id'])
    
    response = client.post(f'/rider/order/{order_id}/accept-return')
    assert response.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'return_accepted_by_rider'
        assert order.rider_id == users['rider_id']


def test_phase4_rider_completes_return(client, setup_users):
    """Test that rider can complete return delivery."""
    users = setup_users
    login_user(client, users['buyer_id'])
    
    with app.app_context():
        # Create approved product
        product = Product(
            name='Test Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='approved'
        )
        db.session.add(product)
        
        # Create order accepted by rider
        order = Order(
            buyer_id=users['buyer_id'],
            total_amount=100.0,
            status='return_accepted_by_rider',
            return_reason='Product damaged',
            payment_method='cod',
            payment_status='paid',
            shipping_address='Test Address',
            rider_id=users['rider_id']
        )
        db.session.add(order)
        db.session.commit()
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            price_at_time=100.0
        )
        db.session.add(order_item)
        db.session.commit()
        order_id = order.id
    
    # Login as rider
    login_user(client, users['rider_id'])
    
    response = client.post(f'/rider/order/{order_id}/complete-return')
    assert response.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'return_delivered'


def test_phase4_seller_refunds_order(client, setup_users):
    """Test that seller can process refund after return is delivered."""
    users = setup_users
    login_user(client, users['buyer_id'])
    
    with app.app_context():
        # Create approved product
        product = Product(
            name='Test Product',
            description='Test description',
            price=100.0,
            stock=10,
            category_id=users['category_id'],
            seller_id=users['seller_id'],
            status='approved'
        )
        db.session.add(product)
        
        # Create order in return_delivered status
        order = Order(
            buyer_id=users['buyer_id'],
            total_amount=100.0,
            status='return_delivered',
            return_reason='Product damaged',
            payment_method='cod',
            payment_status='paid',
            shipping_address='Test Address',
            rider_id=users['rider_id']
        )
        db.session.add(order)
        db.session.commit()
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            price_at_time=100.0
        )
        db.session.add(order_item)
        db.session.commit()
        order_id = order.id
    
    # Login as seller
    login_user(client, users['seller_id'])
    
    response = client.post(f'/seller/order/{order_id}/refund')
    assert response.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'refunded'
        assert order.payment_status == 'refunded'


# ==================== INTEGRATION TEST ====================

def test_full_workflow_integration(client, setup_users):
    """Test complete workflow from product creation to refund."""
    users = setup_users
    
    # Step 1: Seller creates product (pending)
    login_user(client, users['seller_id'])
    data = {
        'name': 'Integration Test Product',
        'description': 'Test description',
        'price': '100.0',
        'stock': '10',
        'category_id': str(users['category_id'])
    }
    response = client.post('/seller/add-product', data=data)
    assert response.status_code == 302
    
    with app.app_context():
        product = Product.query.filter_by(name='Integration Test Product').first()
        assert product.status == 'pending'
        product_id = product.id
    
    # Step 2: Admin approves product
    login_user(client, users['admin_id'])
    response = client.get(f'/admin/approve-product/{product_id}')
    assert response.status_code == 302
    
    with app.app_context():
        product = Product.query.get(product_id)
        assert product.status == 'approved'
    
    # Step 3: Buyer browses shop (no login)
    with client.session_transaction() as sess:
        sess.clear()
    response = client.get('/shop')
    assert response.status_code == 200
    assert b'Integration Test Product' in response.data
    
    # Step 4: Buyer adds to cart (requires login)
    login_user(client, users['buyer_id'])
    response = client.get(f'/add-to-cart/{product_id}')
    assert response.status_code == 302
    
    # Step 5: Create order
    with app.app_context():
        cart_item = Cart.query.filter_by(user_id=users['buyer_id'], product_id=product_id).first()
        if cart_item:
            db.session.delete(cart_item)
        
        order = Order(
            buyer_id=users['buyer_id'],
            total_amount=100.0,
            status='processing',
            payment_method='cod',
            payment_status='paid',
            shipping_address='Test Address'
        )
        db.session.add(order)
        db.session.commit()
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product_id,
            quantity=1,
            price_at_time=100.0
        )
        db.session.add(order_item)
        db.session.commit()
        order_id = order.id
    
    # Step 6: Seller marks ready for pickup
    login_user(client, users['seller_id'])
    response = client.post(f'/seller/order/{order_id}/ready-for-pickup')
    assert response.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'ready_for_pickup'
    
    # Step 7: Rider accepts order
    login_user(client, users['rider_id'])
    response = client.post(f'/rider/order/{order_id}/accept')
    assert response.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'accepted_by_rider'
        assert order.rider_id == users['rider_id']
    
    # Step 8: Complete order
    with app.app_context():
        order = Order.query.get(order_id)
        order.status = 'completed'
        db.session.commit()
    
    # Step 9: Buyer requests return
    login_user(client, users['buyer_id'])
    data = {'return_reason': 'Product not as described'}
    response = client.post(f'/buyer/order/{order_id}/request-return', data=data)
    assert response.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'return_requested'
    
    # Step 10: Seller approves return
    login_user(client, users['seller_id'])
    response = client.post(f'/seller/order/{order_id}/approve-return')
    assert response.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'return_ready_for_pickup'
        assert order.rider_id is None
    
    # Step 11: Rider accepts return
    login_user(client, users['rider_id'])
    response = client.post(f'/rider/order/{order_id}/accept-return')
    assert response.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'return_accepted_by_rider'
    
    # Step 12: Rider completes return
    response = client.post(f'/rider/order/{order_id}/complete-return')
    assert response.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'return_delivered'
    
    # Step 13: Seller processes refund
    login_user(client, users['seller_id'])
    response = client.post(f'/seller/order/{order_id}/refund')
    assert response.status_code == 302
    
    with app.app_context():
        order = Order.query.get(order_id)
        assert order.status == 'refunded'
        assert order.payment_status == 'refunded'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
