from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort, render_template_string, make_response, Response
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pytz import timezone as pytz_timezone
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
import os
from dotenv import load_dotenv
import requests
from requests.exceptions import RequestException
import re
import time
import qrcode
import io
import base64
import json
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import string
import jwt
import bcrypt
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from PIL import Image
from urllib.parse import quote
from optimized_endpoints import register_optimized_endpoints
from province_delivery_fees import calculate_delivery_fee, get_province_rank, calculate_delivery_fee_from_address, extract_province_from_address
from mobile_rating_api import register_mobile_rating_endpoints
from return_refund_api import register_return_refund_api
from notification_api_endpoints import register_notification_api
from notification_service import NotificationService
from google_login_api import register_google_login_api
from shopee_notification_system import (
    ensure_notification_table,
    notify_order_placed,
    notify_order_confirmed,
    notify_order_processing,
    notify_order_ready_for_pickup,
    notify_order_accepted_by_rider,
    notify_order_in_transit,
    notify_order_delivered,
    notify_order_completed,
    notify_order_cancelled,
    notify_payment_confirmed,
    notify_return_requested,
    notify_return_approved,
    notify_return_rejected,
    notify_refund_processed,
    notify_product_approved,
    notify_product_rejected,
    notify_low_stock,
    notify_out_of_stock
)
from unified_chat_api import register_unified_chat_api
from product_chat_api import register_product_chat_api
from email_verification_api import register_email_verification_endpoints

# Load backend .env first (higher priority for database connection)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

# Load mobile app's Supabase env only if not already configured in backend .env
SUPABASE_ENV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'mobile_app',
    'lib',
    'kids_commercedb',
    'supabase.env',
)
load_dotenv(SUPABASE_ENV_PATH, override=False)




PSGC_REMOTE_CANDIDATES = [
    "https://psgc.vercel.app/api",     # preferred dynamic endpoint
    "https://psgc.gitlab.io/api"       # static JSON mirror (user-provided curl examples)
]

# Allow HTTP for OAuth in development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

# Load SECRET_KEY from environment - REQUIRED for production security
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY environment variable is not set! "
        "Please add SECRET_KEY to your .env file. "
        "This is required for Flask session security."
    )
app.config['SECRET_KEY'] = SECRET_KEY

# Ensure templates and static assets refresh during development
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache static files for 1 year (31536000 seconds)

# Initialize Notification System
# MOVED: register_notification_api(app)

# Ensure notification table has all required columns for Shopee-style notifications
# This will be called after app is fully initialized to avoid circular import
def ensure_notification_table_on_startup():
    """Ensure notification table has all required columns (called after app init)"""
    try:
        with app.app_context():
            ensure_notification_table(db, _sa_text)
        print("[OK] Notification table columns verified")
    except Exception as e:
        print(f"[ERROR] Error ensuring notification table columns: {e}")

@app.before_request
def before_request():
    """Track request start time for performance monitoring"""
    request.start_time = time.time()
    # Log all incoming requests
    print(f"[REQUEST] {request.method} {request.path} from {request.remote_addr}")

# CORS Configuration for Mobile API Access
@app.after_request
def after_request(response):
    """Add CORS headers for mobile app access and performance monitoring"""
    # CORS headers
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')

    # Performance monitoring - log ALL requests
    if hasattr(request, 'start_time'):
        elapsed = time.time() - request.start_time
        status_emoji = "?" if response.status_code < 400 else "?"
        print(f"{status_emoji} [{response.status_code}] {request.method} {request.path} - {elapsed:.3f}s")

    return response

# Performance monitoring
import time
@app.before_request
def before_request():
    request.start_time = time.time()
try:
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}
except Exception:
    pass

PH_TZ = ZoneInfo('Asia/Manila')

def to_ph_time(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(PH_TZ)

def ph_time(dt, fmt='%b %d, %Y %I:%M %p'):
    dt_ph = to_ph_time(dt)
    return dt_ph.strftime(fmt) if dt_ph else ''

app.jinja_env.filters['ph_time'] = ph_time


app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Supabase Configuration from supabase.env
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_API_KEY:
    raise RuntimeError(
        f"Missing SUPABASE_URL or SUPABASE_KEY in {SUPABASE_ENV_PATH}."
    )

SUPABASE_REST_URL = f"{SUPABASE_URL}/rest/v1"
app.config['SUPABASE_URL'] = SUPABASE_URL
app.config['SUPABASE_REST_URL'] = SUPABASE_REST_URL
app.config['SUPABASE_API_KEY'] = SUPABASE_API_KEY
app.config['SUPABASE_SERVICE_KEY'] = os.getenv('SUPABASE_SERVICE_KEY', SUPABASE_API_KEY)

# SQLAlchemy configuration - Use Supabase Transaction Pooler from environment
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')
if not SUPABASE_DB_URL:
    print("[WARNING] SUPABASE_DB_URL not found in environment, falling back to SQLite")
    SUPABASE_DB_URL = 'sqlite:///:memory:'
else:
    print(f"[INFO] Using Supabase database: {SUPABASE_DB_URL.split('@')[0]}@...")

app.config['SQLALCHEMY_DATABASE_URI'] = SUPABASE_DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False  # Enable SQL query logging to identify slow queries
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': False,
    'echo': False,
}
db = SQLAlchemy(app)

# Global flag to track database availability
DB_AVAILABLE = True
DB_ERROR_MESSAGE = None

def check_database_connection():
    """Check if database connection is available"""
    global DB_AVAILABLE, DB_ERROR_MESSAGE
    try:
        # Test the database connection within app context
        with app.app_context():
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
        DB_AVAILABLE = True
        DB_ERROR_MESSAGE = None
        print("[OK] Direct PostgreSQL connection successful")
        return True
    except Exception as e:
        DB_AVAILABLE = False
        DB_ERROR_MESSAGE = str(e)
        print(f"[WARNING] Database connection failed: {e}")
        print("[INFO] Falling back to REST API mode")
        return False

# Check database connection on startup (after app and db are initialized)
with app.app_context():
    try:
        check_database_connection()
    except Exception as e:
        print(f"[ERROR] Failed to check database connection: {e}")
        DB_AVAILABLE = False

# Default error handling (use Flask's built-in handlers)

# Dev toggle: when set to '1' use local ORM for buyer/cart/checkout reads/writes
USE_LOCAL_ORM_FALLBACK = os.environ.get('USE_LOCAL_ORM_FALLBACK', '1') == '1'

# In-process local fallbacks when remote DB/ORM are unavailable
LOCAL_CARTS = {}  # {user_id: [{id, product_id, quantity, created_at}]}
LOCAL_ID_COUNTER = {'cart': -1, 'order': -1, 'order_item': -1}

# Supabase REST API Helper Functions
def get_supabase_headers(use_service_key=True):  # Changed default to True
    """Get standard headers for Supabase REST API calls
    
    Args:
        use_service_key: If True, use service key to bypass RLS (admin operations)
    """
    key = app.config.get('SUPABASE_SERVICE_KEY', SUPABASE_API_KEY) if use_service_key else SUPABASE_API_KEY
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    # Set user context for RLS if user is logged in (only when in request context)
    try:
        if 'user_id' in session and not use_service_key:
            headers['X-User-Id'] = str(session['user_id'])
    except RuntimeError:
        # Outside request context, skip session access
        pass
    
    return headers

def get_data(table, filters=None, select='*', order=None, limit=None, offset=None):
    """
    Fetch data from Supabase table
    
    Args:
        table: Table name
        filters: Dict of filters (e.g., {'email': 'test@example.com'})
        select: Columns to select (default: '*')
        order: Order by clause (e.g., 'created_at.desc')
        limit: Number of records to return
        offset: Number of records to skip
    
    Returns:
        List of records or None on error
    """
    # If dev toggle enabled, prefer local ORM
    try:
        if USE_LOCAL_ORM_FALLBACK:
            # simple ORM emulation for common tables
            if table == 'cart':
                query = Cart.query
                if filters:
                    if filters.get('user_id'):
                        query = query.filter_by(user_id=filters.get('user_id'))
                    if filters.get('product_id'):
                        query = query.filter_by(product_id=filters.get('product_id'))
                rows = query.order_by(Cart.created_at.desc() if hasattr(Cart, 'created_at') else None).all()
                return [
                    {
                        'id': r.id,
                        'user_id': r.user_id,
                        'product_id': r.product_id,
                        'quantity': r.quantity,
                        'created_at': r.created_at.isoformat() if hasattr(r, 'created_at') else None
                    } for r in rows
                ]
            if table == 'product':
                query = Product.query
                if filters:
                    for k, v in filters.items():
                        if hasattr(Product, k):
                            if isinstance(v, (list, tuple, set)):
                                query = query.filter(getattr(Product, k).in_(list(v)))
                                continue
                            # Handle Supabase-style filters (gte., lte., etc.)
                            if isinstance(v, str) and '.' in v:
                                parts = v.split('.', 1)
                                if len(parts) == 2:
                                    op, val = parts
                                    col = getattr(Product, k)
                                    if op == 'gte':
                                        try:
                                            dt = datetime.fromisoformat(val)
                                            query = query.filter(col >= dt)
                                        except ValueError:
                                            pass
                                    elif op == 'lte':
                                        try:
                                            dt = datetime.fromisoformat(val)
                                            query = query.filter(col <= dt)
                                        except ValueError:
                                            pass
                                    elif op == 'gt':
                                        try:
                                            dt = datetime.fromisoformat(val)
                                            query = query.filter(col > dt)
                                        except ValueError:
                                            pass
                                    elif op == 'lt':
                                        try:
                                            dt = datetime.fromisoformat(val)
                                            query = query.filter(col < dt)
                                        except ValueError:
                                            pass
                                    else:
                                        # Unknown operator, skip
                                        pass
                            else:
                                # Standard equality filter
                                query = query.filter(getattr(Product, k) == v)
                if order:
                    if 'desc' in order:
                        order_col = order.split('.')[0]
                        if hasattr(Product, order_col):
                            query = query.order_by(getattr(Product, order_col).desc())
                if limit:
                    query = query.limit(limit)
                rows = query.all()
                return [{
                    'id': r.id,
                    'name': r.name,
                    'description': r.description,
                    'price': r.price,
                    'stock': r.stock,
                    'reserved_stock': r.reserved_stock or 0,
                    'image_filename': r.image_filename,
                    'video_filename': r.video_filename,
                    'gallery': r.gallery,
                    'category_id': r.category_id,
                    'subcategory_id': r.subcategory_id,
                    'seller_id': r.seller_id,
                    'status': r.status,
                    'featured': r.featured,
                    'show_in_new_arrival': r.show_in_new_arrival,
                    'rating': r.rating if hasattr(r, 'rating') else 0.0,
                    'review_count': r.review_count if hasattr(r, 'review_count') else 0,
                    'created_at': r.created_at.isoformat() if hasattr(r, 'created_at') else None,
                } for r in rows]
            if table == 'category':
                query = Category.query
                if filters:
                    for k, v in filters.items():
                        if hasattr(Category, k):
                            query = query.filter(getattr(Category, k) == v)
                if order:
                    if 'desc' in order:
                        order_col = order.split('.')[0]
                        if hasattr(Category, order_col):
                            query = query.order_by(getattr(Category, order_col).desc())
                    else:
                        order_col = order.split('.')[0]
                        if hasattr(Category, order_col):
                            query = query.order_by(getattr(Category, order_col).asc())
                rows = query.all()
                return [{
                    'id': r.id,
                    'name': r.name,
                    'description': r.description,
                    'status': r.status,
                    'cover_image_filename': r.cover_image_filename,
                    'created_at': r.created_at.isoformat() if hasattr(r, 'created_at') else None,
                } for r in rows]
            if table == 'subcategory':
                query = Subcategory.query
                if filters:
                    for k, v in filters.items():
                        if hasattr(Subcategory, k):
                            query = query.filter(getattr(Subcategory, k) == v)
                if order:
                    if 'desc' in order:
                        order_col = order.split('.')[0]
                        if hasattr(Subcategory, order_col):
                            query = query.order_by(getattr(Subcategory, order_col).desc())
                    else:
                        order_col = order.split('.')[0]
                        if hasattr(Subcategory, order_col):
                            query = query.order_by(getattr(Subcategory, order_col).asc())
                rows = query.all()
                return [{
                    'id': r.id,
                    'name': r.name,
                    'category_id': r.category_id,
                    'status': r.status,
                } for r in rows]
            if table == 'user':
                query = User.query
                if filters:
                    for k, v in filters.items():
                        if hasattr(User, k):
                            query = query.filter(getattr(User, k) == v)
                if order:
                    if 'desc' in order:
                        order_col = order.split('.')[0]
                        if hasattr(User, order_col):
                            query = query.order_by(getattr(User, order_col).desc())
                if limit:
                    query = query.limit(limit)
                rows = query.all()
                return [{
                    'id': r.id,
                    'email': r.email,
                    'password': r.password,
                    'first_name': r.first_name,
                    'last_name': r.last_name,
                    'phone': r.phone,
                    'role': r.role,
                    'status': r.status,
                    'created_at': r.created_at.isoformat() if hasattr(r, 'created_at') else None,
                } for r in rows]
            # fallback: continue to Supabase below
        url = f"{SUPABASE_REST_URL}/{table}"
        params = {'select': select}
        
        if filters:
            for key, value in filters.items():
                if isinstance(value, (list, tuple, set)):
                    params[key] = f"in.({','.join(str(item) for item in value)})"
                else:
                    params[key] = f'eq.{value}'
        
        if order:
            params['order'] = order
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        
        response = None
        last_exc = None
        for attempt in range(3):
            try:
                response = requests.get(url, headers=get_supabase_headers(), params=params, timeout=30)
                last_exc = None
                break
            except RequestException as exc:
                last_exc = exc
                time.sleep(0.4 * (2 ** attempt))

        if last_exc:
            print(f"Exception fetching {table}: {str(last_exc)}")
            return []

        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            return []

        print(f"Error fetching {table}: {response.status_code} - {response.text}")
        return []
    except Exception as e:
        print(f"Exception fetching {table}: {str(e)}")
        # Final in-memory fallback for cart queries
        try:
            if table == 'cart' and filters and filters.get('user_id'):
                uid = int(filters.get('user_id'))
                return LOCAL_CARTS.get(uid, [])
        except Exception:
            pass
        return []

def get_data_by_id(table, record_id, select='*'):
    """
    Fetch a single record by ID from Supabase table
    
    Args:
        table: Table name
        record_id: Record ID
        select: Columns to select (default: '*')
    
    Returns:
        Record dict or None on error
    """
    try:
        if USE_LOCAL_ORM_FALLBACK:
            # ORM local lookup
            if table == 'product':
                orm_product = db.session.get(Product, int(record_id))
                if orm_product:
                    return {
                        'id': orm_product.id,
                        'name': orm_product.name,
                        'description': orm_product.description,
                        'price': orm_product.price,
                        'stock': orm_product.stock,
                        'seller_id': orm_product.seller_id,
                        'category_id': orm_product.category_id,
                        'subcategory_id': orm_product.subcategory_id,
                        'image_filename': orm_product.image_filename,
                        'gallery': orm_product.gallery,
                        'video_filename': orm_product.video_filename,
                        'status': orm_product.status,
                        'featured': orm_product.featured,
                        'rating': orm_product.rating if hasattr(orm_product, 'rating') else 0.0,
                        'review_count': orm_product.review_count if hasattr(orm_product, 'review_count') else 0,
                        'created_at': orm_product.created_at,
                    }
            if table == 'user':
                orm_user = db.session.get(User, int(record_id))
                if orm_user:
                    return {
                        'id': orm_user.id,
                        'status': orm_user.status,
                        'role': orm_user.role,
                        'first_name': orm_user.first_name if hasattr(orm_user, 'first_name') else None,
                        'last_name': orm_user.last_name if hasattr(orm_user, 'last_name') else None,
                        'name': orm_user.name if hasattr(orm_user, 'name') else None,
                        'phone': orm_user.phone if hasattr(orm_user, 'phone') else None,
                        'email': orm_user.email if hasattr(orm_user, 'email') else None,
                        'profile_picture': orm_user.profile_picture if hasattr(orm_user, 'profile_picture') else None,
                    }
            if table == 'cart':
                orm_cart = db.session.get(Cart, int(record_id))
                if orm_cart:
                    return {'id': orm_cart.id, 'user_id': orm_cart.user_id, 'product_id': orm_cart.product_id, 'quantity': orm_cart.quantity}
            # else fallthrough to Supabase
        url = f"{SUPABASE_REST_URL}/{table}?id=eq.{record_id}&select={select}"
        response = requests.get(url, headers=get_supabase_headers(), timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
        else:
            print(f"Error fetching {table} by ID: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception fetching {table} by ID: {str(e)}")
        return None

def insert_data(table, data):
    """
    Insert data into Supabase table
    
    Args:
        table: Table name
        data: Dict of data to insert
    
    Returns:
        Inserted record dict or None on error
    """
    try:
        if USE_LOCAL_ORM_FALLBACK:
            try:
                if table == 'cart':
                    cart_obj = Cart(user_id=data.get('user_id'), product_id=data.get('product_id'), quantity=data.get('quantity', 1))
                    db.session.add(cart_obj)
                    db.session.commit()
                    return {
                        'id': cart_obj.id,
                        'user_id': cart_obj.user_id,
                        'product_id': cart_obj.product_id,
                        'quantity': cart_obj.quantity,
                        'created_at': cart_obj.created_at.isoformat() if hasattr(cart_obj, 'created_at') else None
                    }
                if table == 'order':
                    order_obj = Order(
                        buyer_id=data.get('buyer_id'),
                        total_amount=data.get('total_amount', 0),
                        status=data.get('status', 'pending'),
                        payment_method=data.get('payment_method'),
                        payment_status=data.get('payment_status', 'pending'),
                        recipient_name=data.get('recipient_name'),
                        recipient_phone=data.get('recipient_phone'),
                        shipping_address=data.get('shipping_address'),
                        notes=data.get('notes')
                    )
                    db.session.add(order_obj)
                    db.session.commit()
                    return {
                        'id': order_obj.id,
                        'buyer_id': order_obj.buyer_id,
                        'total_amount': order_obj.total_amount,
                        'status': order_obj.status,
                        'payment_method': order_obj.payment_method,
                        'payment_status': order_obj.payment_status,
                        'created_at': order_obj.created_at,
                    }
                if table == 'order_item':
                    order_item_obj = OrderItem(
                        order_id=data.get('order_id'),
                        product_id=data.get('product_id'),
                        quantity=data.get('quantity', 1),
                        price_at_time=data.get('price_at_time', 0)
                    )
                    db.session.add(order_item_obj)
                    db.session.commit()
                    return {
                        'id': order_item_obj.id,
                        'order_id': order_item_obj.order_id,
                        'product_id': order_item_obj.product_id,
                        'quantity': order_item_obj.quantity,
                        'price_at_time': order_item_obj.price_at_time,
                    }
                if table == 'review':
                    # Parse media field if it's a JSON string
                    media_data = data.get('media')
                    if isinstance(media_data, str):
                        try:
                            media_data = json.loads(media_data)
                        except:
                            media_data = None
                    
                    # Only use fields that exist in Review model
                    review_obj = Review(
                        product_id=data.get('product_id'),
                        user_id=data.get('user_id'),
                        order_id=data.get('order_id'),
                        rating=data.get('rating'),
                        title=data.get('title', ''),
                        content=data.get('content', ''),
                        media=media_data,
                        status=data.get('status', 'published'),
                        verified_purchase=data.get('verified_purchase', False)
                        # created_at will use model default (datetime.utcnow)
                    )
                    db.session.add(review_obj)
                    db.session.commit()
                    return {
                        'id': review_obj.id,
                        'product_id': review_obj.product_id,
                        'user_id': review_obj.user_id,
                        'rating': review_obj.rating,
                        'title': review_obj.title,
                        'content': review_obj.content,
                        'media': review_obj.media,
                        'verified_purchase': review_obj.verified_purchase,
                        'created_at': review_obj.created_at.isoformat() if review_obj.created_at else None,
                    }
            except Exception as e:
                db.session.rollback()
                print(f'Local ORM insert failed for {table}: {e}')
            # fallthrough to Supabase insertion
        url = f"{SUPABASE_REST_URL}/{table}"
        response = requests.post(url, headers=get_supabase_headers(), json=data, timeout=30)
        
        if response.status_code in [200, 201]:
            return response.json()[0] if response.json() else None
        else:
            # If Supabase insertion failed (RLS or other), try local ORM fallback for common tables
            print(f"Error inserting into {table}: {response.status_code} - {response.text}")
            try:
                if table == 'cart':
                    cart_obj = Cart(user_id=data.get('user_id'), product_id=data.get('product_id'), quantity=data.get('quantity', 1))
                    db.session.add(cart_obj)
                    db.session.commit()
                    return {
                        'id': cart_obj.id,
                        'user_id': cart_obj.user_id,
                        'product_id': cart_obj.product_id,
                        'quantity': cart_obj.quantity,
                        'created_at': cart_obj.created_at.isoformat() if hasattr(cart_obj, 'created_at') else None
                    }
                if table == 'order':
                    order_obj = Order(
                        buyer_id=data.get('buyer_id'),
                        total_amount=data.get('total_amount', 0),
                        status=data.get('status', 'pending'),
                        payment_method=data.get('payment_method'),
                        payment_status=data.get('payment_status', 'pending'),
                        recipient_name=data.get('recipient_name'),
                        recipient_phone=data.get('recipient_phone'),
                        shipping_address=data.get('shipping_address'),
                        notes=data.get('notes')
                    )
                    db.session.add(order_obj)
                    db.session.commit()
                    return {
                        'id': order_obj.id,
                        'buyer_id': order_obj.buyer_id,
                        'total_amount': order_obj.total_amount,
                        'status': order_obj.status,
                        'payment_method': order_obj.payment_method,
                        'payment_status': order_obj.payment_status,
                        'created_at': order_obj.created_at,
                    }
                if table == 'order_item':
                    order_item_obj = OrderItem(
                        order_id=data.get('order_id'),
                        product_id=data.get('product_id'),
                        quantity=data.get('quantity', 1),
                        price_at_time=data.get('price_at_time', 0)
                    )
                    db.session.add(order_item_obj)
                    db.session.commit()
                    return {
                        'id': order_item_obj.id,
                        'order_id': order_item_obj.order_id,
                        'product_id': order_item_obj.product_id,
                        'quantity': order_item_obj.quantity,
                        'price_at_time': order_item_obj.price_at_time,
                    }
            except Exception as e:
                db.session.rollback()
                print(f'ORM fallback insert failed for {table}: {e}')
            # Last-resort: in-memory fallback
            try:
                if table == 'cart':
                    uid = int(data.get('user_id'))
                    LOCAL_ID_COUNTER['cart'] -= 1
                    cid = LOCAL_ID_COUNTER['cart']
                    entry = {'id': cid, 'user_id': uid, 'product_id': int(data.get('product_id')), 'quantity': int(data.get('quantity', 1)), 'created_at': datetime.utcnow().isoformat()}
                    LOCAL_CARTS.setdefault(uid, []).append(entry)
                    return entry
                if table == 'order':
                    LOCAL_ID_COUNTER['order'] -= 1
                    oid = LOCAL_ID_COUNTER['order']
                    entry = {'id': oid, 'buyer_id': int(data.get('buyer_id')), 'total_amount': data.get('total_amount', 0), 'status': data.get('status', 'to_pay'), 'payment_method': data.get('payment_method'), 'payment_status': data.get('payment_status', 'pending'), 'recipient_name': data.get('recipient_name'), 'recipient_phone': data.get('recipient_phone'), 'shipping_address': data.get('shipping_address'), 'notes': data.get('notes'), 'created_at': datetime.utcnow().isoformat()}
                    return entry
                if table == 'order_item':
                    LOCAL_ID_COUNTER['order_item'] -= 1
                    oi = LOCAL_ID_COUNTER['order_item']
                    entry = {'id': oi, 'order_id': int(data.get('order_id')), 'product_id': int(data.get('product_id')), 'quantity': int(data.get('quantity',1)), 'price_at_time': float(data.get('price_at_time',0))}
                    return entry
            except Exception as e:
                print(f'In-memory fallback insert failed for {table}: {e}')
            return None
    except Exception as e:
        print(f"Exception inserting into {table}: {str(e)}")
        return None

def update_data(table, filters, data):
    """
    Update data in Supabase table
    
    Args:
        table: Table name
        filters: Dict of filters to identify records (e.g., {'id': 1})
        data: Dict of data to update
    
    Returns:
        Updated record dict or None on error
    """
    try:
        if USE_LOCAL_ORM_FALLBACK:
            try:
                if table == 'product' and filters and filters.get('id'):
                    orm_product = db.session.get(Product, int(filters.get('id')))
                    if orm_product:
                        for k, v in data.items():
                            if hasattr(orm_product, k):
                                setattr(orm_product, k, v)
                        db.session.commit()
                        return {k: getattr(orm_product, k) for k in data.keys()}
                # generic ORM fallback for cart updates
                if table == 'cart' and filters and filters.get('id'):
                    orm_cart = db.session.get(Cart, int(filters.get('id')))
                    if orm_cart:
                        for k, v in data.items():
                            if hasattr(orm_cart, k):
                                setattr(orm_cart, k, v)
                        db.session.commit()
                        return {k: getattr(orm_cart, k) for k in data.keys()}
            except Exception as e:
                db.session.rollback()
                print(f'Local ORM update failed for {table}: {e}')
            # fallthrough to Supabase
        url = f"{SUPABASE_REST_URL}/{table}"
        params = {}
        
        for key, value in filters.items():
            params[key] = f'eq.{value}'
        
        headers = get_supabase_headers()
        headers['Prefer'] = 'return=representation'
        
        response = requests.patch(url, headers=headers, params=params, json=data, timeout=30)
        
        if response.status_code in [200, 204]:
            if response.status_code == 200:
                return response.json()[0] if response.json() else None
            return data
        else:
            print(f"Error updating {table}: {response.status_code} - {response.text}")
            # Fallback to ORM for product stock updates and simple updates
            try:
                if table == 'product' and 'stock' in data:
                    orm_product = db.session.get(Product, filters.get('id')) if filters and filters.get('id') else None
                    if not orm_product:
                        # try direct id if provided in filters
                        pid = filters.get('id') if filters and filters.get('id') else None
                        if pid:
                            orm_product = db.session.get(Product, int(pid))
                    if orm_product:
                        for k, v in data.items():
                            if hasattr(orm_product, k):
                                setattr(orm_product, k, v)
                        db.session.commit()
                        return {k: getattr(orm_product, k) for k in data.keys()}
                # generic ORM fallback not implemented for other tables
            except Exception as e:
                db.session.rollback()
                print(f'ORM fallback update failed for {table}: {e}')
            return None
    except Exception as e:
        print(f"Exception updating {table}: {str(e)}")
        # in-memory fallback for product stock updates
        try:
            if table == 'product' and filters and filters.get('id') and 'stock' in data:
                pid = int(filters.get('id'))
                try:
                    orm_product = db.session.get(Product, pid)
                except Exception:
                    orm_product = None
                if orm_product:
                    try:
                        orm_product.stock = data.get('stock')
                        db.session.commit()
                        return {'stock': orm_product.stock}
                    except Exception:
                        db.session.rollback()
                # cannot persist stock change; return None
        except Exception:
            pass
        return None

def update_data_by_id(table, record_id, data):
    """
    Update a record by ID in Supabase table
    
    Args:
        table: Table name
        record_id: Record ID
        data: Dict of data to update
    
    Returns:
        Updated record dict or None on error
    """
    return update_data(table, {'id': record_id}, data)

def delete_data(table, filters):
    """
    Delete data from Supabase table
    
    Args:
        table: Table name
        filters: Dict of filters to identify records (e.g., {'id': 1})
    
    Returns:
        True on success, False on error
    """
    try:
        if USE_LOCAL_ORM_FALLBACK:
            try:
                if table == 'cart':
                    cid = filters.get('id') if filters and filters.get('id') else None
                    if cid:
                        obj = db.session.get(Cart, int(cid))
                        if obj:
                            db.session.delete(obj)
                            db.session.commit()
                            return True
                    if filters and filters.get('user_id') and filters.get('product_id'):
                        rows = Cart.query.filter_by(user_id=filters.get('user_id'), product_id=filters.get('product_id')).all()
                        for r in rows:
                            db.session.delete(r)
                        db.session.commit()
                        return True
            except Exception as e:
                db.session.rollback()
                print(f'Local ORM delete failed for {table}: {e}')
            # fallthrough to Supabase delete
        url = f"{SUPABASE_REST_URL}/{table}"
        params = {}
        
        for key, value in filters.items():
            params[key] = f'eq.{value}'
        
        response = requests.delete(url, headers=get_supabase_headers(), params=params, timeout=30)
        
        if response.status_code in [200, 204]:
            return True
        else:
            print(f"Error deleting from {table}: {response.status_code} - {response.text}")
            # Fallback to ORM deletion for cart
            try:
                if table == 'cart':
                    # filters may contain id or user_id
                    cid = filters.get('id') if filters and filters.get('id') else None
                    if cid:
                        obj = db.session.get(Cart, int(cid))
                        if obj:
                            db.session.delete(obj)
                            db.session.commit()
                            return True
                    # if user_id and product_id provided, delete matching rows
                    if filters and filters.get('user_id') and filters.get('product_id'):
                        rows = Cart.query.filter_by(user_id=filters.get('user_id'), product_id=filters.get('product_id')).all()
                        for r in rows:
                            db.session.delete(r)
                        db.session.commit()
                        return True
            except Exception as e:
                db.session.rollback()
                print(f'ORM fallback delete failed for {table}: {e}')
            return False
    except Exception as e:
        print(f"Exception deleting from {table}: {str(e)}")
        # final in-memory fallback for cart
        try:
            if table == 'cart' and filters and filters.get('id'):
                cid = int(filters.get('id'))
                for uid, items in list(LOCAL_CARTS.items()):
                    new_items = [it for it in items if it.get('id') != cid]
                    LOCAL_CARTS[uid] = new_items
                return True
        except Exception:
            pass
        return False

def delete_data_by_id(table, record_id):
    """
    Delete a record by ID from Supabase table
    
    Args:
        table: Table name
        record_id: Record ID
    
    Returns:
        True on success, False on error
    """
    return delete_data(table, {'id': record_id})

def count_data(table, filters=None):
    """
    Count records in Supabase table
    
    Args:
        table: Table name
        filters: Dict of filters (optional)
    
    Returns:
        Count as int or 0 on error
    """
    try:
        if USE_LOCAL_ORM_FALLBACK:
            # Use local ORM for counting
            if table == 'product':
                query = Product.query
                if filters:
                    for k, v in filters.items():
                        if hasattr(Product, k):
                            if isinstance(v, (list, tuple, set)):
                                query = query.filter(getattr(Product, k).in_(list(v)))
                            else:
                                query = query.filter(getattr(Product, k) == v)
                return query.count()
            if table == 'category':
                query = Category.query
                if filters:
                    for k, v in filters.items():
                        if hasattr(Category, k):
                            query = query.filter(getattr(Category, k) == v)
                return query.count()
            if table == 'subcategory':
                query = Subcategory.query
                if filters:
                    for k, v in filters.items():
                        if hasattr(Subcategory, k):
                            query = query.filter(getattr(Subcategory, k) == v)
                return query.count()
            if table == 'cart':
                query = Cart.query
                if filters:
                    for k, v in filters.items():
                        if hasattr(Cart, k):
                            query = query.filter(getattr(Cart, k) == v)
                return query.count()
        
        url = f"{SUPABASE_REST_URL}/{table}"
        params = {'select': 'count'}
        headers = get_supabase_headers()
        headers['Prefer'] = 'count=exact'
        
        if filters:
            for key, value in filters.items():
                if isinstance(value, (list, tuple, set)):
                    params[key] = f"in.({','.join(str(item) for item in value)})"
                else:
                    params[key] = f'eq.{value}'
        
        response = requests.head(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return int(response.headers.get('content-range', '0-0/0').split('/')[-1])
        else:
            print(f"Error counting {table}: {response.status_code} - {response.text}")
            return 0
    except Exception as e:
        print(f"Exception counting {table}: {str(e)}")
        return 0

# Google OAuth Configuration
app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.getenv(
    'GOOGLE_OAUTH_CLIENT_ID',
    '668360708226-q79n83ttq956po4cj3pd5qig0thiqp6c.apps.googleusercontent.com',
)
app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.getenv(
    'GOOGLE_OAUTH_CLIENT_SECRET',
    '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',
)

app.config['MAIL_SENDER'] = os.getenv('MAIL_SENDER', 'gbanagan33@gmail.com')
app.config['MAIL_APP_PASSWORD'] = os.getenv('MAIL_APP_PASSWORD', 'hprhqjfxpdfahxsf')
app.config['MAIL_SENDER_NAME'] = 'Kids Kingdom' 

PSGC_REMOTE_BASE = 'https://psgc.vercel.app/api'

# JWT Configuration for Mobile API - Load from environment (REQUIRED)
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
if not JWT_SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY environment variable is not set! "
        "Please add JWT_SECRET_KEY to your .env file. "
        "This is required for mobile API authentication security."
    )

JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# JWT Authentication Utilities
def generate_tokens(user_id, user_role):
    """Generate access and refresh tokens for mobile authentication"""
    access_payload = {
        'user_id': user_id,
        'role': user_role,
        'exp': datetime.utcnow() + JWT_ACCESS_TOKEN_EXPIRES,
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    
    refresh_payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + JWT_REFRESH_TOKEN_EXPIRES,
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    
    access_token = jwt.encode(access_payload, JWT_SECRET_KEY, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET_KEY, algorithm='HS256')
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': int(JWT_ACCESS_TOKEN_EXPIRES.total_seconds())
    }

def verify_token(token, token_type='access'):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        
        # Check token type
        if payload.get('type') != token_type:
            return None
            
        # Check expiration
        if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
            return None
            
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against bcrypt hash"""
    if not hashed or not password:
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except (ValueError, AttributeError):
        # Handle invalid hash format (e.g., plain text passwords)
        return password == hashed

def token_required(f):
    """Decorator to require JWT token for API endpoints"""
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        print(f"=== Token Required Debug ===")
        print(f"Auth header: {auth_header}")
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
                print(f"Token extracted: {token[:20]}...")
            except IndexError:
                print("Invalid token format")
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            print("Token is missing")
            return jsonify({'error': 'Token is missing'}), 401
            
        payload = verify_token(token, 'access')
        print(f"Payload: {payload}")
        
        if not payload:
            print("Token is invalid or expired")
            return jsonify({'error': 'Token is invalid or expired'}), 401
            
        # Add user info to request context
        request.current_user_id = payload['user_id']
        request.current_user_role = payload.get('role', 'customer')
        print(f"User ID: {request.current_user_id}, Role: {request.current_user_role}")
        
        return f(*args, **kwargs)
    
    return decorated

def role_required(*allowed_roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        from functools import wraps
        
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user_role'):
                return jsonify({'error': 'Authentication required'}), 401
                
            if request.current_user_role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
                
            return f(*args, **kwargs)
        
        return decorated
    return decorator

def active_user_required(f):
    """Decorator to require user status to be 'active' (Supabase version)"""
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'current_user_id'):
            return jsonify({'error': 'Authentication required'}), 401
        # Prefer Supabase user status, but fallback to local ORM when Supabase is unavailable
        user = get_data_by_id('user', request.current_user_id)
        if not user:
            try:
                orm_user = db.session.get(User, request.current_user_id)
                if orm_user and getattr(orm_user, 'status', None) == 'active':
                    return f(*args, **kwargs)
            except Exception:
                pass
            return jsonify({'error': 'Your account is not active. Please wait for admin approval.'}), 403
        # If Supabase shows user but not active, allow if ORM says active (local override)
        if user.get('status') != 'active':
            try:
                orm_user = db.session.get(User, request.current_user_id)
                if orm_user and getattr(orm_user, 'status', None) == 'active':
                    return f(*args, **kwargs)
            except Exception:
                pass
            return jsonify({'error': 'Your account is not active. Please wait for admin approval.'}), 403
            
        return f(*args, **kwargs)
    
    return decorated

# DB helpers

def _is_sqlite():
    try:
        return db.engine.name == 'sqlite'
    except Exception:
        return False

# MySQL check removed - now using Supabase PostgreSQL
def try_remote_json(path, params=None, timeout=12):
    """Try candidate PSGC remotes and return requests.Response on first success."""
    params = params or {}
    last_exc = None
    for base in PSGC_REMOTE_CANDIDATES:
        url = base.rstrip('/') + '/' + path.lstrip('/')
        try:
            r = requests.get(url, params=params, timeout=timeout)
            # Accept 200 and JSON-like responses
            if r.status_code == 200 and r.headers.get('Content-Type', '').lower().startswith(('application/json','text/json','text/html')):
                return r
        except Exception as e:
            last_exc = e
            # try next candidate
    # if all failed, raise last exception (or return None)
    if last_exc:
        raise last_exc
    return None

@app.route('/api/regions')
def proxy_regions():
    try:
        for base_url in PSGC_REMOTE_CANDIDATES:
            for endpoint in ['regions', 'region']:
                try:
                    url = f"{base_url.rstrip('/')}/{endpoint}"
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        data = r.json()
                        if isinstance(data, list) and data:
                            return jsonify({'result': data})
                        elif isinstance(data, dict):
                            if 'result' in data and data['result']:
                                return jsonify(data)
                            elif 'data' in data and data['data']:
                                return jsonify({'result': data['data']})
                except Exception:
                    continue
        return jsonify({'result': []}), 200
    except Exception as e:
        app.logger.exception("PSGC regions proxy failed: %s", e)
        return jsonify({'result': []}), 200

@app.route('/api/provinces')
def proxy_provinces():
    region_code = request.args.get('region') or request.args.get('region_code') or ''
    if not region_code:
        return jsonify({'result': []}), 200
    
    app.logger.info(f"Fetching provinces for region_code: {region_code}")
    
    try:
        # Try to get all provinces first, then filter by region code
        for base_url in PSGC_REMOTE_CANDIDATES:
            for endpoint in ['provinces', 'province']:
                try:
                    url = f"{base_url.rstrip('/')}/{endpoint}"
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        data = r.json()
                        provinces = []
                        
                        # Extract list from response
                        if isinstance(data, list):
                            provinces = data
                        elif isinstance(data, dict):
                            if 'result' in data:
                                provinces = data['result'] if isinstance(data['result'], list) else []
                            elif 'data' in data:
                                provinces = data['data'] if isinstance(data['data'], list) else []
                        
                        app.logger.info(f"Total provinces fetched: {len(provinces)}")
                        
                        # Filter by region code
                        if provinces:
                            # Log first province to see structure
                            if provinces:
                                app.logger.info(f"Sample province data: {provinces[0]}")
                            
                            filtered = []
                            for p in provinces:
                                # Check multiple possible field names for region code
                                p_region = (p.get('regionCode') or p.get('region_code') or 
                                          p.get('region') or p.get('psgc_region_code') or '')
                                if str(p_region) == str(region_code):
                                    filtered.append(p)
                            
                            app.logger.info(f"Filtered provinces: {len(filtered)} for region_code: {region_code}")
                            
                            if filtered:
                                return jsonify({'result': filtered})
                except Exception as e:
                    app.logger.error(f"Province fetch attempt failed: {e}")
                    continue
        
        app.logger.warning(f"No provinces found for region_code: {region_code}")
        return jsonify({'result': []}), 200
    except Exception as e:
        app.logger.exception("PSGC provinces proxy failed: %s", e)
        return jsonify({'result': []}), 200

@app.route('/api/cities')
def proxy_cities():
    province_code = request.args.get('province') or request.args.get('province_code') or ''
    if not province_code:
        return jsonify({'result': []}), 200
    
    app.logger.info(f"Fetching cities for province_code: {province_code}")
    
    try:
        # Try to get all cities first, then filter by province code
        for base_url in PSGC_REMOTE_CANDIDATES:
            for endpoint in ['cities-municipalities', 'cities', 'city']:
                try:
                    url = f"{base_url.rstrip('/')}/{endpoint}"
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        data = r.json()
                        cities = []
                        
                        # Extract list from response
                        if isinstance(data, list):
                            cities = data
                        elif isinstance(data, dict):
                            if 'result' in data:
                                cities = data['result'] if isinstance(data['result'], list) else []
                            elif 'data' in data:
                                cities = data['data'] if isinstance(data['data'], list) else []
                        
                        app.logger.info(f"Total cities fetched: {len(cities)}")
                        
                        # Filter by province code
                        if cities:
                            # Log first city to see structure
                            if cities:
                                app.logger.info(f"Sample city data: {cities[0]}")
                            
                            filtered = []
                            for c in cities:
                                # Check multiple possible field names for province code
                                c_province = (c.get('provinceCode') or c.get('province_code') or 
                                            c.get('province') or c.get('psgc_province_code') or '')
                                if str(c_province) == str(province_code):
                                    filtered.append(c)
                            
                            app.logger.info(f"Filtered cities: {len(filtered)} for province_code: {province_code}")
                            
                            if filtered:
                                return jsonify({'result': filtered})
                except Exception as e:
                    app.logger.error(f"City fetch attempt failed: {e}")
                    continue
        
        app.logger.warning(f"No cities found for province_code: {province_code}")
        return jsonify({'result': []}), 200
    except Exception as e:
        app.logger.exception("PSGC cities proxy failed: %s", e)
        return jsonify({'result': []}), 200

@app.route('/api/barangays')
def proxy_barangays():
    city_code = request.args.get('city') or request.args.get('city_code') or ''
    if not city_code:
        return jsonify({'result': []}), 200
    
    app.logger.info(f"Fetching barangays for city_code: {city_code}")
    
    try:
        # Try to get all barangays first, then filter by city code
        for base_url in PSGC_REMOTE_CANDIDATES:
            for endpoint in ['barangays', 'barangay']:
                try:
                    url = f"{base_url.rstrip('/')}/{endpoint}"
                    app.logger.info(f"Trying URL: {url}")
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        data = r.json()
                        barangays = []
                        
                        # Extract list from response
                        if isinstance(data, list):
                            barangays = data
                        elif isinstance(data, dict):
                            if 'result' in data:
                                barangays = data['result'] if isinstance(data['result'], list) else []
                            elif 'data' in data:
                                barangays = data['data'] if isinstance(data['data'], list) else []
                        
                        app.logger.info(f"Total barangays fetched: {len(barangays)}")
                        
                        # Filter by city code
                        if barangays:
                            filtered = []
                            # Log first barangay to see structure
                            if barangays:
                                app.logger.info(f"Sample barangay data: {barangays[0]}")
                            
                            for b in barangays:
                                # Check multiple possible field names for city code
                                b_city = (b.get('cityCode') or b.get('city_code') or 
                                        b.get('city') or b.get('psgc_city_code') or 
                                        b.get('cityMunCode') or b.get('cityMunicipalityCode') or 
                                        b.get('citymunCode') or b.get('municipalityCode') or '')
                                
                                # Try matching with different formats
                                if (str(b_city) == str(city_code) or 
                                    str(b_city).startswith(str(city_code)) or
                                    str(city_code).startswith(str(b_city))):
                                    filtered.append(b)
                            
                            app.logger.info(f"Filtered barangays: {len(filtered)} for city_code: {city_code}")
                            
                            if filtered:
                                return jsonify({'result': filtered})
                except Exception as e:
                    app.logger.error(f"Barangay fetch attempt failed: {e}")
                    continue
        
        app.logger.warning(f"No barangays found for city_code: {city_code}")
        return jsonify({'result': []}), 200
    except Exception as e:
        app.logger.exception("PSGC barangays proxy failed: %s", e)
        return jsonify({'result': []}), 200


# Template context processor to make cart_count, user info, and theme settings available in all templates
@app.context_processor
def inject_cart_count():
    context = {
        'cart_count': get_cart_count(),
        # default for seller inbox badge so templates don't error even if not logged in
        'unread_chat_count': 0,
    }

    # Default navbar avatar (generic)
    try:
        context['navbar_avatar_url'] = url_for('static', filename='user_avatar.png')
    except Exception:
        context['navbar_avatar_url'] = '/static/user_avatar.png'
    
    # Add search parameter from query string for search bar persistence
    context['search'] = request.args.get('search', '')
    
    # --- THEME SETTINGS BLOCK START ---
    # --- THEME SETTINGS BLOCK START ---
    # Example: fetch from DB; fallback to defaults if not set
    try:
        theme = ThemeSetting.query.first()
        context['theme_logo'] = theme.logo_filename if theme and theme.logo_filename else None
        context['theme_site_name'] = theme.site_name if theme and theme.site_name else "Kids & Baby Store"
        context['theme_primary_color'] = theme.primary_color if theme and theme.primary_color else "#0066ff"
        context['theme_secondary_color'] = theme.secondary_color if theme and theme.secondary_color else "#59b5fc"
        context['theme_footer_color'] = theme.footer_color if theme and theme.footer_color else "#232323"
    except Exception:
        # fallback defaults if ThemeSetting not ready
        context['theme_logo'] = None
        context['theme_site_name'] = "Kids & Baby Store"
        context['theme_primary_color'] = "#0066ff"
        context['theme_secondary_color'] = "#59b5fc"
        context['theme_footer_color'] = "#232323"

    # --- THEME SETTINGS BLOCK END ---

    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        if user:
            active_role = session.get('active_role', user.role)
            context['current_user'] = user
            context['active_role'] = active_role

            # Try admin avatar first when admin
            # Use session avatar URL if available (immediately updated after profile changes)
            if 'navbar_avatar_url' in session:
                context['navbar_avatar_url'] = session['navbar_avatar_url']
                if 'avatar_timestamp' not in session:
                    session['avatar_timestamp'] = int(time.time())
            else:
                # Use helper function to get current avatar URL
                context['navbar_avatar_url'] = get_user_avatar_url(user.id, user.role)
                # Store in session for future requests
                session['navbar_avatar_url'] = context['navbar_avatar_url']
                session['avatar_timestamp'] = int(time.time())
            
            # Check if user can be a seller
            seller_app = SellerApplication.query.filter_by(user_id=user.id, status='approved').first()
            context['can_be_seller'] = user.role == 'seller' or (seller_app is not None)
            # Generic notifications in header for any role
            context['unread_notifications_count'] = Notification.query.filter_by(user_id=user.id, is_read=False).count()
            context['recent_notifications'] = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(5).all()

            # Seller chat inbox badge: count unread messages sent by buyers to this seller
            # Legacy StoreChatMessage removed - unified chat system handles this via API
            try:
                # Access ChatMessage through db.Model registry after unified_chat_api registration
                ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
                if ChatMessage:
                    from sqlalchemy import and_
                    # Count messages where current user is receiver and message is unread
                    context['unread_chat_count'] = db.session.query(ChatMessage).filter(
                        and_(
                            ChatMessage.receiver_id == user.id,
                            ChatMessage.is_read == False,
                        )
                    ).count()
                else:
                    context['unread_chat_count'] = 0
            except Exception:
                # If table not ready or query fails, leave default 0
                context['unread_chat_count'] = 0

            # Backward/role-specific keys for templates
            if user.role == 'admin':
                context['admin_unread_notifications'] = context['unread_notifications_count']
                context['admin_recent_notifications'] = context['recent_notifications']
            if active_role == 'seller' or user.role == 'seller':
                context['seller_unread_notifications'] = context['unread_notifications_count']
                context['seller_recent_notifications'] = context['recent_notifications']
            if active_role == 'buyer' or user.role == 'buyer':
                context['buyer_unread_notifications'] = context['unread_notifications_count']
                context['buyer_recent_notifications'] = context['recent_notifications']
    
    # Add utility functions to templates
    context['get_available_stock'] = get_available_stock
    
    return context


# --- Helper function to get user avatar URL ---
def _avatar_static_filename(profile_picture: str) -> str:
    """Normalize stored profile_picture values to a static filename."""
    pic = str(profile_picture or '').strip().replace('\\', '/')
    if pic.startswith('/static/'):
        pic = pic[len('/static/'):]
    elif pic.startswith('static/'):
        pic = pic[len('static/'):]
    if pic.startswith('uploads/'):
        return pic
    if 'user_avatars/' in pic or 'admin_avatars/' in pic:
        return f"uploads/{pic.split('uploads/')[-1].lstrip('/')}"
    return f"uploads/user_avatars/{os.path.basename(pic)}"


def get_user_avatar_url(user_id, user_role=None):
    """Get avatar URL with database check for profile_picture."""
    try:
        from flask import has_request_context
        base_url = request.url_root.rstrip('/') if has_request_context() else ''

        user = db.session.get(User, user_id)
        if user and user.profile_picture:
            pic = str(user.profile_picture).strip()
            if pic.startswith('http://') or pic.startswith('https://'):
                return pic
            static_name = _avatar_static_filename(pic)
            rel_url = url_for('static', filename=static_name)
            return f"{base_url}{rel_url}" if base_url else rel_url

        static_name = (
            f"uploads/admin_avatars/admin_avatar_{user_id}.png"
            if user_role == 'admin'
            else f"uploads/user_avatars/user_avatar_{user_id}.png"
        )
        avatar_path = os.path.join(app.root_path, 'static', static_name.replace('/', os.sep))
        if not os.path.exists(avatar_path):
            static_name = 'user_avatar.png'
        rel_url = url_for('static', filename=static_name)
        return f"{base_url}{rel_url}" if base_url else rel_url
    except Exception:
        try:
            from flask import has_request_context
            base_url = request.url_root.rstrip('/') if has_request_context() else ''
            rel_url = url_for('static', filename='user_avatar.png')
            return f"{base_url}{rel_url}" if base_url else rel_url
        except Exception:
            return '/static/user_avatar.png'


def _save_user_profile_avatar(user: 'User', file_storage) -> str:
    """Save a square PNG avatar for any user role and return its public URL."""
    if not file_storage or not getattr(file_storage, 'filename', None):
        raise ValueError('No image file provided')
    ext = (file_storage.filename.rsplit('.', 1)[-1].lower() if '.' in file_storage.filename else '')
    if ext not in ALLOWED_IMAGE_EXT:
        raise ValueError('Unsupported image type. Please upload JPG or PNG.')

    avatar_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'user_avatars')
    os.makedirs(avatar_dir, exist_ok=True)

    img = Image.open(file_storage.stream).convert('RGBA')
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side)).resize((256, 256), Image.LANCZOS)

    final_name = f'user_avatar_{user.id}.png'
    img.save(os.path.join(avatar_dir, final_name), format='PNG', optimize=True)

    user.profile_picture = f'uploads/user_avatars/{final_name}'
    db.session.commit()
    return get_user_avatar_url(user.id, user.role)

@app.context_processor
def avatar_helper():
    """Make avatar helper function available in all templates"""
    return dict(get_user_avatar_url=get_user_avatar_url)


def fetch_psgc(endpoint, params=None, timeout=15, max_pages=0, per_page=None, retry=2, backoff=1.0):
    """
    Fetch JSON list from PSGC and support pagination.
    - endpoint: e.g. "regions", "provinces", "cities-municipalities", "barangays"
    - params: dict of query params to send (will be copied per page)
    - timeout: per-request timeout
    - max_pages: 0 => iterate until no more pages; >0 => stop after that many pages
    - per_page: if supported by PSGC, pass as 'perPage' or 'limit' (function will try 'perPage' then 'limit')
    - retry: number of retries on transient errors
    - backoff: seconds to wait between retries (increases by factor 2)
    Returns: list of rows (possibly empty). On error returns the rows collected so far.
    """
    base_url = PSGC_BASE.rstrip('/') + '/' + endpoint.lstrip('/')
    collected = []
    page = 1
    done = False

    # Prepare params copy so we don't mutate caller's dict
    base_params = dict(params or {})

    # Decide on per-page key - try common conventions
    if per_page:
        # prefer 'perPage' then 'limit'
        base_params.setdefault('perPage', per_page)
        base_params.setdefault('limit', per_page)

    while not done:
        req_params = dict(base_params)
        # common pagination param names: page, pageNumber, page_no
        req_params.setdefault('page', page)
        req_params.setdefault('pageNumber', page)

        attempt = 0
        while attempt <= retry:
            try:
                resp = requests.get(base_url, params=req_params, timeout=timeout)
                resp.raise_for_status()
                data = resp.json()
                # Try to extract list payload robustly:
                rows = None
                if isinstance(data, list):
                    rows = data
                elif isinstance(data, dict):
                    # common container keys
                    for key in ('data','results','items','rows','results.items'):
                        if key in data and isinstance(data[key], list):
                            rows = data[key]
                            break
                    if rows is None:
                        # If response contains 'meta' with pagination info and 'data' list
                        if 'data' in data and isinstance(data['data'], list):
                            rows = data['data']
                        else:
                            # Attempt to find first list value
                            for v in data.values():
                                if isinstance(v, list):
                                    rows = v
                                    break
                    # Some PSGC endpoints return {"results": {"items": [...], "meta": {...}}}
                    if rows is None:
                        # Deep check
                        maybe = data.get('results') or data.get('data') or data.get('items')
                        if isinstance(maybe, dict):
                            for k in ('items','rows','data','results'):
                                if k in maybe and isinstance(maybe[k], list):
                                    rows = maybe[k]
                                    break
                # If still None, treat as empty list
                if rows is None:
                    rows = []

                # Append found rows
                if isinstance(rows, list) and rows:
                    collected.extend(rows)

                # Pagination termination logic:
                # - if no rows returned -> done
                if not rows:
                    done = True
                    break

                # - if max_pages is set and we've reached it
                if max_pages and page >= max_pages:
                    done = True
                    break

                # Try to detect if response includes meta/total_pages or links:
                total_pages = None
                if isinstance(data, dict):
                    meta = data.get('meta') or data.get('pagination') or data.get('paging')
                    if isinstance(meta, dict):
                        total_pages = meta.get('totalPages') or meta.get('total_pages') or meta.get('last_page') or meta.get('total_pages_count')
                    # links
                    links = data.get('links') or data.get('_links')
                    if isinstance(links, dict) and links.get('next') in (None, '', False):
                        done = True
                        break
                # If we don't have meta, increment page and continue
                page += 1
                # Safety: stop if page gets absurdly large (guard)
                if page > 10000:
                    app.logger.warning("PSGC fetch reached page cap for %s", endpoint)
                    done = True
                    break

                # Small polite pause to avoid hammering
                time.sleep(0.05)
                break  # success -> break retry loop

            except RequestException as exc:
                attempt += 1
                app.logger.warning("PSGC request error (attempt %s/%s) for %s page %s: %s", attempt, retry, endpoint, page, exc)
                if attempt > retry:
                    app.logger.exception("PSGC fetch failed permanently for %s page %s: %s", endpoint, page, exc)
                    # stop pagination and return what we have
                    done = True
                    break
                else:
                    time.sleep(backoff * (2 ** (attempt - 1)))
            except ValueError as exc:
                # JSON parse error
                app.logger.exception("PSGC returned non-JSON for %s page %s: %s", endpoint, page, exc)
                done = True
                break

    return collected

# Initialize SocketIO first
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    allow_upgrades=False,
)

# Register product chat system (buyer-seller product inquiries)
register_product_chat_api(app, db, socketio, token_required)

# Set up Google OAuth
google_bp = make_google_blueprint(
    client_id=app.config.get('GOOGLE_OAUTH_CLIENT_ID'),
    client_secret=app.config.get('GOOGLE_OAUTH_CLIENT_SECRET'),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    redirect_to="index"
)
app.register_blueprint(google_bp, url_prefix="/login")

# Add account selection prompt to Google OAuth
google_bp.authorization_url_params = {"prompt": "select_account"}



# QR Code Generation Functions
def generate_qr_code(order_id):
    """Generate unique QR code for order"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    order_part = str(order_id).zfill(6)
    qr_code = f"KIDS{order_part}{timestamp}"
    return qr_code

def generate_tracking_number():
    """Generate unique tracking number"""
    random_part = ''.join(random.choices(string.digits, k=9))
    return f"TRK{random_part}"

def generate_batch_code():
    """Generate batch code for logistics"""
    date_part = datetime.now().strftime('%Y%m%d')
    time_part = datetime.now().strftime('%H%M')
    return f"BATCH{date_part}{time_part}"

def create_qr_image(qr_code, size=200):
    """Create QR code image as base64 string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_code)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return img_base64

def create_order_label_data(order):
    """Create comprehensive label data for QR code"""
    label_data = {
        'order_id': order.id,
        'buyer_name': f"{order.buyer.first_name} {order.buyer.last_name}",
        'buyer_phone': order.buyer.phone,
        'buyer_email': order.buyer.email,
        'total_amount': float(order.total_amount),
        'payment_method': order.payment_method,
        'shipping_address': order.shipping_address,
        'created_at': order.created_at.isoformat(),
        'items': []
    }
    
    # Add product information
    for item in order.items:
        item_data = {
            'product_id': item.product_id,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'price': float(item.price_at_time),
            'seller_name': f"{item.product.seller.first_name} {item.product.seller.last_name}",
            'seller_id': item.product.seller_id
        }
        label_data['items'].append(item_data)
    
    return label_data

ALLOWED_IMAGE_EXT = {'png', 'jpg', 'jpeg'}
ALLOWED_VIDEO_EXT = {'mp4', 'webm', 'ogg', 'm4v', 'mov'}
MAX_VIDEO_BYTES = 50 * 1024 * 1024  # 50MB server-side safety limit

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXT

# Lightweight migration helper for SQLite to add product.video_filename if missing
from sqlalchemy import text as _sa_text

def ensure_product_video_column():
    try:
        inspector = sa_inspect(db.engine)
        try:
            cols = {c['name'] for c in inspector.get_columns('product')}
        except Exception:
            return
        stmts = []
        if 'video_filename' not in cols:
            stmts.append("ALTER TABLE product ADD COLUMN video_filename VARCHAR(255)")
        for s in stmts:
            db.session.execute(_sa_text(s))
        if stmts:
            db.session.commit()
    except Exception:
        db.session.rollback()
        pass

def ensure_order_api_columns():
    try:
        inspector = sa_inspect(db.engine)
        try:
            cols = {c['name'] for c in inspector.get_columns('order')}
        except Exception:
            return
        stmts = []
        if 'rider_id' not in cols:
            stmts.append("ALTER TABLE \"order\" ADD COLUMN rider_id INTEGER NULL")
        if 'rider_earnings' not in cols:
            stmts.append("ALTER TABLE \"order\" ADD COLUMN rider_earnings FLOAT DEFAULT 0.0")
        if 'shipping_notes' not in cols:
            stmts.append("ALTER TABLE \"order\" ADD COLUMN shipping_notes TEXT")
        if 'delivery_notes' not in cols:
            stmts.append("ALTER TABLE \"order\" ADD COLUMN delivery_notes TEXT")
        if 'delivery_fee' not in cols:
            stmts.append("ALTER TABLE \"order\" ADD COLUMN delivery_fee FLOAT DEFAULT 0.0")
        if 'shipping_fee' not in cols:
            stmts.append("ALTER TABLE \"order\" ADD COLUMN shipping_fee FLOAT DEFAULT 0.0")
        for stmt in stmts:
            db.session.execute(_sa_text(stmt))
        if stmts:
            db.session.commit()
    except Exception:
        db.session.rollback()
        pass

def ensure_product_gallery_column():
    try:
        inspector = sa_inspect(db.engine)
        try:
            cols = {c['name'] for c in inspector.get_columns('product')}
        except Exception:
            return
        if 'gallery' not in cols:
            # JSON type works for MySQL 5.7+/MariaDB 10.4+ (alias) and SQLite (as TEXT)
            db.session.execute(_sa_text("ALTER TABLE product ADD COLUMN gallery JSON"))
            db.session.commit()
    except Exception:
        db.session.rollback()
        pass

def ensure_return_request_request_type_column():
    """Ensure ReturnRequest has request_type column ("return" or "refund")."""
    try:
        inspector = sa_inspect(db.engine)
        try:
            cols = {c['name'] for c in inspector.get_columns('return_request')}
        except Exception:
            return
        if 'request_type' not in cols:
            db.session.execute(_sa_text("ALTER TABLE return_request ADD COLUMN request_type VARCHAR(20)"))
            db.session.commit()
    except Exception:
        db.session.rollback()
        pass

# Ensure Review has a JSON 'media' column to store uploaded images/videos
# and keep backward-compatible image_filename usage.
def ensure_review_media_column():
    try:
        inspector = sa_inspect(db.engine)
        try:
            cols = {c['name'] for c in inspector.get_columns('review')}
        except Exception:
            return
        if 'media' not in cols:
            db.session.execute(_sa_text("ALTER TABLE review ADD COLUMN media JSON"))
            db.session.commit()
    except Exception:
        db.session.rollback()
        pass

# Ensure Review has verified_purchase (BOOL) and order_id (INT) columns
# to match the ORM model and avoid 1054 unknown column errors
def ensure_review_extra_columns():
    try:
        inspector = sa_inspect(db.engine)
        try:
            cols = {c['name'] for c in inspector.get_columns('review')}
        except Exception:
            return
        stmts = []
        if 'verified_purchase' not in cols:
            # MySQL/MariaDB: BOOLEAN is alias of TINYINT(1)
            stmts.append("ALTER TABLE review ADD COLUMN verified_purchase BOOLEAN NOT NULL DEFAULT 0")
        if 'order_id' not in cols:
            stmts.append("ALTER TABLE review ADD COLUMN order_id INTEGER NULL")
        for s in stmts:
            db.session.execute(_sa_text(s))
        if stmts:
            db.session.commit()
    except Exception:
        db.session.rollback()
        pass

# Ensure DeliveryPersonnel has extended profile fields (address/id)
def ensure_delivery_personnel_extra_columns():
    try:
        inspector = sa_inspect(db.engine)
        try:
            cols = {c['name'] for c in inspector.get_columns('delivery_personnel')}
        except Exception:
            return
        to_add = []
        if 'address' not in cols:
            to_add.append("ALTER TABLE delivery_personnel ADD COLUMN address TEXT")
        if 'id_type' not in cols:
            to_add.append("ALTER TABLE delivery_personnel ADD COLUMN id_type VARCHAR(40)")
        if 'id_number' not in cols:
            to_add.append("ALTER TABLE delivery_personnel ADD COLUMN id_number VARCHAR(60)")
        if 'id_document' not in cols:
            to_add.append("ALTER TABLE delivery_personnel ADD COLUMN id_document VARCHAR(255)")
        if 'photo_path' not in cols:
            to_add.append("ALTER TABLE delivery_personnel ADD COLUMN photo_path VARCHAR(255)")
        for stmt in to_add:
            db.session.execute(_sa_text(stmt))
        if to_add:
            db.session.commit()
    except Exception:
        db.session.rollback()
        pass

# Ensure migration runs once per process before handling requests (Flask 3.x safe)
@app.before_request
def _run_light_migrations_once():
    if not app.config.get('_video_migration_ran', False):
        try:
            ensure_product_video_column()
            app.config['_video_migration_ran'] = True
        except Exception:
            # Avoid blocking requests if migration check fails
            app.config['_video_migration_ran'] = True  # prevent repeated attempts
            pass
    # Ensure tables exist for new features (e.g., ReturnRequest, ReturnPickup)
    if not app.config.get('_schema_ready', False):
        try:
            db.create_all()
            app.config['_schema_ready'] = True
        except Exception:
            app.config['_schema_ready'] = True
            pass

    # Auto-approve stale return requests past review_deadline (every ~5 minutes)
    try:
        last = app.config.get('_returns_escalation_last')
        now = datetime.utcnow()
        if not last or (now - last).total_seconds() > 300:
            _auto_approve_overdue_returns()
            app.config['_returns_escalation_last'] = now
    except Exception:
        pass

# Ensure migration runs before any endpoint uses Product
@app.before_request
def _ensure_schema_migrations():
    try:
        ensure_product_video_column()
        ensure_return_request_request_type_column()
        ensure_review_media_column()
        ensure_review_extra_columns()
        ensure_product_gallery_column()
        ensure_delivery_personnel_extra_columns()
        ensure_order_api_columns()
        ensure_notification_extra_columns()
        ensure_seller_application_background_column()
        # Fix sequence issues for chat tables
        fix_sequence_for_table('rider_chat_message')
        fix_sequence_for_table('store_chat_message')
        fix_sequence_for_table('return_request')
    except Exception:
        # Avoid blocking requests if migration check fails
        pass


# PSGC sync helper (paste this into app.py AFTER your existing api_streets_db route)
# NOTE: requests is already imported in your app.py; this snippet uses app.logger (no additional imports).

PSGC_BASE = "https://psgc.cloud/api"

# helper: try multiple possible key names from PSGC payloads
def _get_field(obj, candidates, default=None):
    for k in candidates:
        if isinstance(obj, dict) and k in obj and obj[k] not in (None, ''):
            return obj[k]
    return default


def upsert_region(code, name):
    if not code:
        return
    r = Region.query.filter_by(code=code).first()
    if r:
        r.name = name or r.name
    else:
        r = Region(code=code, name=name or code)
        db.session.add(r)

def upsert_province(code, name, region_code):
    if not code:
        return
    p = Province.query.filter_by(code=code).first()
    if p:
        p.name = name or p.name
        p.region_code = region_code or p.region_code
    else:
        p = Province(code=code, name=name or code, region_code=region_code or '')
        db.session.add(p)

def upsert_city(code, name, province_code):
    if not code:
        return
    c = City.query.filter_by(code=code).first()
    if c:
        c.name = name or c.name
        c.province_code = province_code or c.province_code
    else:
        c = City(code=code, name=name or code, province_code=province_code or '')
        db.session.add(c)

def upsert_barangay(code, name, city_code):
    if not code:
        return
    b = Barangay.query.filter_by(code=code).first()
    if b:
        b.name = name or b.name
        b.city_code = city_code or b.city_code
    else:
        b = Barangay(code=code, name=name or code, city_code=city_code or '')
        db.session.add(b)

def sync_regions():
    rows = fetch_psgc("regions")
    count = 0
    for item in rows:
        code = _get_field(item, ['code', 'psgcCode', 'regionCode', 'region_code'])
        name = _get_field(item, ['name', 'regionName', 'region_name'])
        if not code and 'region' in item:
            code = _get_field(item['region'], ['code','psgcCode'])
            name = _get_field(item['region'], ['name'])
        if not code:
            continue
        upsert_region(code, name)
        count += 1
    db.session.commit()
    return count

def sync_provinces():
    rows = fetch_psgc("provinces")
    count = 0
    for item in rows:
        code = _get_field(item, ['code','psgcCode','provinceCode','province_code'])
        name = _get_field(item, ['name','provinceName','province_name'])
        parent = _get_field(item, ['regionCode','region_code','region','region_code'])
        if not parent and isinstance(item, dict) and 'region' in item and isinstance(item['region'], dict):
            parent = _get_field(item['region'], ['code','psgcCode'])
        if not code:
            continue
        upsert_province(code, name, parent or '')
        count += 1
    db.session.commit()
    return count


def upsert_city_municipality(psgc_code, name, prov_id=None, type=None, zip_code=None, district=None):
    if not psgc_code:
        return
    cm = CityMunicipality.query.filter_by(psgc_code=psgc_code).first()
    if cm:
        cm.name = name or cm.name
        cm.province_id = prov_id or cm.province_id
        cm.type = type or cm.type
        cm.zip_code = zip_code or cm.zip_code
        cm.district = district or cm.district
    else:
        cm = CityMunicipality(
            psgc_code=psgc_code,
            name=name or psgc_code,
            province_id=prov_id or None,
            type=type,
            zip_code=zip_code,
            district=district
        )
        db.session.add(cm)
        
        
def sync_cities():
    rows = fetch_psgc("cities-municipalities")
    count = 0
    for item in rows:
        code = _get_field(item, ['code','psgcCode','cityMunCode','cityMunicipalityCode','psgc_code'])
        name = _get_field(item, ['name','cityMunName','city_municipality_name','cityName'])
        parent_code = _get_field(item, ['provinceCode','province_code','provCode'])
        # resolve province_id if we have a parent_code (which may be province code)
        prov_id = None
        if parent_code:
            prov = Province.query.filter_by(code=parent_code).first()
            if prov:
                prov_id = prov.id
        # fallback: if item has 'province' dict with 'id' or 'psgcCode' etc.
        upsert_city_municipality(code, name, prov_id=prov_id, type=_get_field(item, ['type']), zip_code=_get_field(item, ['zip_code','zipCode']))
        count += 1
    db.session.commit()
    return count
def sync_barangays():
    rows = fetch_psgc("barangays")
    count = 0
    for item in rows:
        code = _get_field(item, ['code','psgcCode','barangayCode','brgyCode','barangay_code'])
        name = _get_field(item, ['name','barangay','barangayName','brgy_name'])
        parent = _get_field(item, ['cityMunCode','cityCode','city_code','city_municipality_code','cityMunicipalityCode'])
        if not parent and isinstance(item, dict) and 'city' in item and isinstance(item['city'], dict):
            parent = _get_field(item['city'], ['code','psgcCode'])
        if not code:
            continue
        upsert_barangay(code, name, parent or '')
        count += 1
    db.session.commit()
    return count

@app.route('/admin/sync-psgc', methods=['GET','POST'])
def admin_sync_psgc():
    """
    Admin-only route to fetch the PSGC dataset and populate local tables.
    This version performs an inline admin check so it can be placed before
    the admin_required decorator is declared elsewhere in the file.
    """
    # inline admin check (avoids using @admin_required which may be defined later)
    if not is_admin():
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))

    try:
        r_count = sync_regions()
        p_count = sync_provinces()
        c_count = sync_cities()
        b_count = sync_barangays()
        flash(f"PSGC sync completed: regions={r_count}, provinces={p_count}, cities={c_count}, barangays={b_count}", 'success')
    except Exception as e:
        app.logger.exception("PSGC sync failed: %s", e)
        flash("PSGC sync failed. Check logs.", 'danger')
    return redirect(request.referrer or url_for('admin_dashboard'))

# Optional programmatic helper if you prefer running from Python shell:
def sync_all_psgc():
    """Programmatic sync helper. Run inside app.app_context()"""
    r = sync_regions()
    p = sync_provinces()
    c = sync_cities()
    b = sync_barangays()
    return {"regions": r, "provinces": p, "cities": c, "barangays": b}


# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Not hashed as requested
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), default='buyer')  # buyer, seller, admin
    status = db.Column(db.String(20), default='active')  # active, pending, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Security settings
    two_factor_enabled = db.Column(db.Boolean, default=False)  # Two-factor authentication
    email_notifications = db.Column(db.Boolean, default=True)  # Email notifications
    email_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(10))
    
     # NEW: path to uploaded valid ID (relative/public path)
    valid_id = db.Column(db.String(255), nullable=True)
    
    # Profile picture path
    profile_picture = db.Column(db.String(255), nullable=True)

class SellerApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    store_name = db.Column(db.String(120), nullable=False)
    store_description = db.Column(db.Text)
    store_category = db.Column(db.String(100), nullable=False)
    business_address = db.Column(db.Text, nullable=False)
    school_id_document = db.Column(db.String(255))  # File path for uploaded document
    gcash_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # New fields for enhanced seller profile
    store_logo = db.Column(db.String(255))  # Store logo file path
    store_background = db.Column(db.String(255))  # Store background/banner image file path
    store_mission = db.Column(db.Text)  # Store mission statement
    return_policy = db.Column(db.Text)  # Return policy description
    return_days = db.Column(db.Integer, default=7)  # Return period in days
    refund_method = db.Column(db.String(50), default='Original Payment Method')  # Refund method
    business_registration = db.Column(db.String(255))  # Business registration document
    valid_id = db.Column(db.String(255))  # Valid ID document
    
    user = db.relationship('User', backref='seller_applications', foreign_keys=[user_id])


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, to_pay, processing, ready_for_pickup, accepted_by_rider, in_transit, delivered, completed, cancelled, return_requested, return_ready_for_pickup, return_accepted_by_rider, return_in_transit, return_delivered, refunded
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    shipping_address = db.Column(db.Text, nullable=False)
    recipient_name = db.Column(db.String(255))
    recipient_phone = db.Column(db.String(20))
    notes = db.Column(db.Text)
    stock_deducted = db.Column(db.Boolean, default=False)  # TRUE kapag na-process na ng seller
    return_reason = db.Column(db.Text)  # Reason for return request
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Coupon relationship
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupon.id'), nullable=True)
    discount_amount = db.Column(db.Float, default=0.0)
    coupon = db.relationship('Coupon')

    # QR Code and Tracking fields
    qr_code = db.Column(db.String(255), unique=True)
    tracking_number = db.Column(db.String(50), unique=True)
    batch_code = db.Column(db.String(50))
    label_generated_at = db.Column(db.DateTime)
    packed_at = db.Column(db.DateTime)
    picked_up_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    packed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    picked_up_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    delivered_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    rider_earnings = db.Column(db.Float, default=0.0)
    delivery_fee = db.Column(db.Float, default=36.0)  # Province-based delivery fee
    shipping_notes = db.Column(db.Text)
    delivery_notes = db.Column(db.Text)
    proof_photo_url = db.Column(db.String(500))
    
    buyer = db.relationship('User', backref='orders', foreign_keys=[buyer_id])
    rider = db.relationship('User', foreign_keys=[rider_id], backref='assigned_orders')
    packed_by_user = db.relationship('User', foreign_keys=[packed_by], backref='packed_orders')
    picked_up_by_user = db.relationship('User', foreign_keys=[picked_up_by], backref='picked_up_orders')
    delivered_by_user = db.relationship('User', foreign_keys=[delivered_by], backref='delivered_orders')

    @property
    def delivery_address(self):
        return self.shipping_address

    @delivery_address.setter
    def delivery_address(self, value):
        self.shipping_address = value

    @property
    def total_price(self):
        return self.total_amount

    @total_price.setter
    def total_price(self, value):
        self.total_amount = value

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False)  # Price when ordered
    order = db.relationship('Order', backref='items')
    product = db.relationship('Product')

    @property
    def price(self):
        return self.price_at_time

    @price.setter
    def price(self, value):
        self.price_at_time = value

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product')

class OrderLabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    qr_code = db.Column(db.String(255), unique=True, nullable=False)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)
    batch_code = db.Column(db.String(50), nullable=False)
    label_data = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(20), default='generated')  # generated, printed, packed, picked_up, in_transit, delivered, returned
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    packed_at = db.Column(db.DateTime)
    picked_up_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    returned_at = db.Column(db.DateTime)
    packed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    picked_up_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    delivered_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    returned_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    shipping_notes = db.Column(db.Text)
    delivery_notes = db.Column(db.Text)
    return_notes = db.Column(db.Text)
    
    order = db.relationship('Order', backref='labels')


class SellerOrderSeen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, index=True, nullable=False)
    order_id = db.Column(db.Integer, index=True, nullable=False)
    seen_at = db.Column(db.DateTime, default=datetime.utcnow)

# Return & Refund Request model
class ReturnRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_item.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    reason_other = db.Column(db.Text)  # Additional reason details when "Others" is selected
    description = db.Column(db.Text)  # Buyer's detailed description of the issue
    quantity = db.Column(db.Integer, default=1)  # Quantity requested for return
    images = db.Column(db.JSON)  # List of image paths
    video_filename = db.Column(db.String(255))  # Video filename
    request_type = db.Column(db.String(20), nullable=False)  # 'return' or 'refund'
    status = db.Column(db.String(30), default='submitted')  # Updated status values
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    processed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    refund_amount = db.Column(db.Float)
    admin_notes = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    seller_response_reason = db.Column(db.Text)  # Reason provided by seller when rejecting

    order = db.relationship('Order', backref='return_requests')
    order_item = db.relationship('OrderItem')
    buyer = db.relationship('User', foreign_keys=[buyer_id])
    seller = db.relationship('User', foreign_keys=[seller_id])

# Restock Request model
class RestockRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requested_quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    processed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    admin_notes = db.Column(db.Text)
    approved_quantity = db.Column(db.Integer)  # Quantity approved by admin
    
    # Relationships
    product = db.relationship('Product', backref='restock_requests')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='restock_requests')
    processor = db.relationship('User', foreign_keys=[processed_by])

# Rider pickup task for returns
class ReturnPickup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    return_request_id = db.Column(db.Integer, db.ForeignKey('return_request.id'), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(30), default='available')  # available, waiting_rider_pickup, rider_picked_up, rider_delivered_to_seller
    buyer_address = db.Column(db.Text)
    seller_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    picked_up_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)

    return_request = db.relationship('ReturnRequest', backref='pickup_task')
    rider = db.relationship('User', foreign_keys=[rider_id])

def _auto_approve_overdue_returns():
    overdue = ReturnRequest.query.filter(
        ReturnRequest.status.in_(['submitted','seller_reviewing']),
        ReturnRequest.review_deadline != None,
        ReturnRequest.review_deadline <= datetime.utcnow()
    ).all()
    for rr in overdue:
        # Move to waiting_rider_pickup and create a pickup task
        rr.status = 'waiting_rider_pickup'
        buyer_addr = rr.order.shipping_address if rr.order else ''
        seller_addr = ''
        try:
            appq = SellerApplication.query.filter_by(user_id=rr.seller_id, status='approved').first()
            seller_addr = appq.business_address if appq and appq.business_address else ''
        except Exception:
            seller_addr = ''
        task = ReturnPickup(return_request_id=rr.id, buyer_address=buyer_addr, seller_address=seller_addr, status='available')
        db.session.add(task)
        try:
            push_notification(rr.buyer_id, 'Your return/refund request was auto-approved. A rider will pick up your parcel.')
            socketio.emit('return_pickup_available', {'return_id': rr.id}, room='riders')
        except Exception:
            pass
    if overdue:
        db.session.commit()

class QRScanLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    order_label_id = db.Column(db.Integer, db.ForeignKey('order_label.id'), nullable=False)
    qr_code = db.Column(db.String(255), nullable=False)
    scanned_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scan_type = db.Column(db.String(20), nullable=False)  # packing, pickup, delivery, return, inquiry
    scan_location = db.Column(db.String(255))
    scan_notes = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('Order', backref='scan_logs')
    order_label = db.relationship('OrderLabel', backref='scan_logs')
    scanned_by_user = db.relationship('User', backref='qr_scans')

class DeliveryPersonnel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.String(50))
    vehicle_number = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')  # active, inactive, on_duty, off_duty
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='delivery_personnel')

# Temporarily commented out to allow server startup
# class ProductQR(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
#     qr_code = db.Column(db.String(255), unique=True, nullable=False)
#     batch_number = db.Column(db.String(50))
#     manufacturing_date = db.Column(db.Date)
#     expiry_date = db.Column(db.Date)
#     status = db.Column(db.String(20), default='active')  # active, sold, returned, damaged, expired
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     
#     product = db.relationship('Product', backref='qr_codes')

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='wishlist_items')
    product = db.relationship('Product')

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    label = db.Column(db.String(50), nullable=False)  # Home, Work, etc.
    full_address = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    region = db.Column(db.String(120), nullable=True)
    province = db.Column(db.String(120), nullable=True)
    city = db.Column(db.String(120), nullable=True)
    barangay = db.Column(db.String(120), nullable=True)
    street = db.Column(db.String(255), nullable=True)
    user = db.relationship('User', backref='addresses')
    latitude = db.Column(db.Float, default=None)
    longitude = db.Column(db.Float, default=None)

class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship("User")
    
    def __init__(self, **kwargs):
        super(OAuth, self).__init__(**kwargs)
        if 'token' not in kwargs:
            self.token = {}

class AdminProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(160), nullable=False)
    contact_number = db.Column(db.String(20))
    system_role = db.Column(db.String(50), default='Administrator')
    last_login = db.Column(db.DateTime)
    account_status = db.Column(db.String(20), default='Active')
    two_factor_enabled = db.Column(db.Boolean, default=False)
    password_reset_required = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref='admin_profile')

class AdminSecurityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)
    user = db.relationship('User', backref='security_logs')


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    # Optional rich fields
    title = db.Column(db.String(255))          # Notification title
    image_url = db.Column(db.String(255))        # avatar/thumbnail for the notification (single)
    link = db.Column(db.String(255))             # where to go when clicked
    type = db.Column(db.String(40))              # e.g., 'chat', 'order', 'system'
    actor_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # who triggered it (e.g., rider)
    order_id = db.Column(db.Integer)             # associated order (for thumbnails)
    images = db.Column(db.JSON)                  # list of image URLs (e.g., ['/static/uploads/...','...'])
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Disambiguate the two FKs to User with foreign_keys on each relationship
    user = db.relationship('User', foreign_keys=[user_id], backref='notifications')
    actor = db.relationship('User', foreign_keys=[actor_user_id])


# Initialize Notification and Chat APIs (after models are defined)
try:
    register_notification_api(app, db, Notification, User)
    print("[OK] Notification API initialized")
except Exception as e:
    print(f"[ERROR] Notification API: {e}")

# Register Google Sign-In API endpoint for mobile apps (after User model is defined)
try:
    register_google_login_api(app, db, User)
    print("[OK] Google Login API initialized")
except Exception as e:
    print(f"[ERROR] Google Login API: {e}")

# Initialize Email Verification API
try:
    register_email_verification_endpoints(app)
    print("[OK] Email Verification API initialized")
except Exception as e:
    print(f"[ERROR] Email Verification API: {e}")

# Unified chat already registered above at line 1500
# No need to register again here

# Generic wallet ledger for riders and sellers
class WalletTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    amount = db.Column(db.Float, nullable=False)  # positive for credit, negative for debit
    type = db.Column(db.String(20), default='credit')  # credit or debit
    source = db.Column(db.String(50))  # order_delivery, payout, adjustment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='wallet_transactions')
    order = db.relationship('Order', backref='wallet_transactions')

# Earnings split configuration (commission released on buyer confirmation -> completed)
# RIDER EARNINGS = DELIVERY FEE (province-based, calculated during checkout)
# Delivery fee formula: Province Rank × 36 pesos
SELLER_EARNING_RATE = 0.85  # 85% to seller(s) (distributed by item proportion)
ADMIN_EARNING_RATE = 0.15   # 15% to admin(s)


def credit_wallet(user_id: int, amount: float, source: str, order_id: int = None):
    """Credit user wallet (Supabase version)."""
    if amount == 0:
        return
    tx_data = {
        'user_id': user_id,
        'order_id': order_id,
        'amount': float(amount),
        'type': 'credit',
        'source': source,
        'created_at': datetime.utcnow()  # Always set timestamp to prevent NULL values
    }
    insert_data('wallet_transaction', tx_data)


RIDER_WALLET_SOURCES = ('order_commission', 'order_delivery')


def get_user_earnings(user_id: int, period: str = 'today', sources=None) -> float:
    """Return sum of credits for a user within the period using optimized SQL query.
    Uses Philippine Time (UTC+8) for period calculations."""
    from sqlalchemy import func

    # Get current time in Philippine timezone (UTC+8)
    ph_tz = timezone(timedelta(hours=8))
    now = datetime.now(ph_tz)

    # Build base query with WHERE clause instead of fetching all data
    query = db.session.query(
        func.sum(WalletTransaction.amount).label('total')
    ).filter(
        WalletTransaction.user_id == user_id,
        WalletTransaction.type == 'credit'
    )
    if sources:
        query = query.filter(WalletTransaction.source.in_(sources))

    # Add date filter in SQL instead of Python
    if period == 'today':
        # Start of today in PH time
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(WalletTransaction.created_at >= start)
    elif period == 'week':
        # 7 days ago from now in PH time
        start = now - timedelta(days=7)
        query = query.filter(WalletTransaction.created_at >= start)
    elif period == 'month':
        # Start of current month in PH time
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(WalletTransaction.created_at >= start)
    # For 'all', no date filter needed

    result = query.scalar()
    return float(result) if result else 0.0

    result = query.scalar()
    return float(result) if result else 0.0


def push_notification(user_id: int, message: str, title: str = None, image_url: str = None, link: str = None, actor_user_id: int = None, type: str = None, order_id: int = None, images: list = None):
    """Create a notification and emit it via websockets (Supabase version). If order_id or an "Order #123" appears in message, attach product thumbnails."""
    try:
        # Infer order_id from message if not provided
        if order_id is None:
            try:
                import re as _re
                m = _re.search(r"order\s*#(\d+)", message, _re.IGNORECASE)
                if m:
                    order_id = int(m.group(1))
            except Exception:
                pass
        # Build images list from order if available and not explicitly provided
        if images is None and order_id:
            try:
                orders = get_data('order', filters={'id': order_id})
                if orders:
                    order = orders[0]
                    order_items = get_data('order_item', filters={'order_id': order_id})
                    if order_items:
                        imgs = []
                        for it in order_items:
                            product = get_data_by_id('product', it.get('product_id'))
                            if product:
                                fn = product.get('image_filename')
                                if fn:
                                    try:
                                        imgs.append(url_for('static', filename=f'uploads/{fn}'))
                                    except RuntimeError:
                                        # Fallback when outside request context
                                        imgs.append(f'/static/uploads/{fn}')
                            if len(imgs) >= 4:
                                break
                        images = imgs or None
            except Exception:
                images = None

        notification_data = {
            'user_id': user_id,
            'message': message,
            'image_url': image_url,
            'link': link,
            'actor_user_id': actor_user_id,
            'type': type,
            'order_id': order_id,
            'images': images
        }
        if title:
            notification_data['title'] = title
        insert_data('notification', notification_data)
    except Exception as e:
        app.logger.error(f"Error creating notification: {e}")
    # real-time push
    try:
        payload = {'message': message}
        if title:
            payload['title'] = title
        if image_url:
            payload['image_url'] = image_url
        if link:
            payload['link'] = link
        if type:
            payload['type'] = type
        if actor_user_id:
            payload['actor_user_id'] = actor_user_id
        if order_id:
            payload['order_id'] = order_id
        if images:
            payload['images'] = images
        socketio.emit('notification', payload, room=f'user_{user_id}')
    except Exception:
        pass


def _admins():
    """Get all admin users (Supabase version)."""
    admins = get_data('user', filters={'role': 'admin'})
    return admins if admins else []


def _entity_id(entity) -> int:
    if isinstance(entity, dict):
        return entity.get('id')
    return getattr(entity, 'id', None)


def _order_already_commissioned(order_id: int) -> bool:
    """Check if order has already been commissioned (Supabase version)."""
    transactions = get_data('wallet_transaction', filters={'order_id': order_id, 'source': 'order_commission'})
    return transactions is not None and len(transactions) > 0


def _wallet_credit_exists(user_id: int, order_id: int, source: str) -> bool:
    if not user_id or not order_id or not source:
        return False
    try:
        return db.session.query(WalletTransaction.id).filter_by(
            user_id=int(user_id),
            order_id=int(order_id),
            source=source,
            type='credit',
        ).first() is not None
    except Exception:
        transactions = get_data(
            'wallet_transaction',
            filters={
                'user_id': user_id,
                'order_id': order_id,
                'source': source,
                'type': 'credit',
            },
        )
        return bool(transactions)


def _credit_wallet_once(user_id: int, amount: float, source: str, order_id: int) -> bool:
    if not user_id or not amount or amount <= 0:
        return False
    if _wallet_credit_exists(user_id, order_id, source):
        return False
    credit_wallet(user_id, amount, source, order_id)
    return True


def _order_rider_id(order: 'Order'):
    return (
        getattr(order, 'picked_up_by', None)
        or getattr(order, 'delivered_by', None)
        or getattr(order, 'rider_id', None)
    )


def _release_rider_earning(order: 'Order') -> bool:
    """Release the delivery earning only, used when a delivered order is later refunded."""
    rider_id = _order_rider_id(order)
    if not rider_id:
        return False
    delivery_fee = float(order.delivery_fee) if hasattr(order, 'delivery_fee') and order.delivery_fee else 36.0
    released = _credit_wallet_once(rider_id, delivery_fee, 'order_commission', order.id)
    if released:
        try:
            order.rider_earnings = delivery_fee
        except Exception:
            pass
        db.session.commit()
    return released


def _finalize_rider_earning_after_return(order: 'Order', refund_approved: bool) -> bool:
    """Release rider delivery fee after return/refund is approved or rejected."""
    if not order:
        return False
    if refund_approved:
        return _release_rider_earning(order)
    _release_commissions(order)
    return True


def _release_commissions(order: 'Order'):
    """Release commissions once buyer confirms receipt (status: completed). Safe to call idempotently."""
    total = float(order.total_amount)
    released_any = False

    # Rider
    rider_id = _order_rider_id(order)
    if rider_id:
        delivery_fee = float(order.delivery_fee) if hasattr(order, 'delivery_fee') and order.delivery_fee else 36.0
        if _credit_wallet_once(rider_id, delivery_fee, 'order_commission', order.id):
            released_any = True
            try:
                order.rider_earnings = delivery_fee
            except Exception:
                pass

    # Sellers: proportional by item subtotal
    seller_totals = {}
    for it in order.items:
        if it.product and it.product.seller_id:
            seller_totals.setdefault(it.product.seller_id, 0.0)
            seller_totals[it.product.seller_id] += float(it.price_at_time) * it.quantity
    seller_total_amount = sum(seller_totals.values()) or 0.0
    if seller_total_amount > 0:
        for sid, sub in seller_totals.items():
            amount = (sub / seller_total_amount) * (total * SELLER_EARNING_RATE)
            if _credit_wallet_once(sid, amount, 'order_commission', order.id):
                released_any = True

    # Admins
    admins = _admins()
    if admins:
        admin_amount_each = (total * ADMIN_EARNING_RATE) / len(admins)
        for a in admins:
            admin_id = _entity_id(a)
            if _credit_wallet_once(admin_id, admin_amount_each, 'order_commission', order.id):
                released_any = True

    if released_any:
        db.session.commit()


# Legacy chat models removed - now using unified ChatMessage from unified_chat_api.py
# StoreChatMessage and RiderChatMessage have been migrated to ChatMessage table


class HeroSlide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    link = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ThemeSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logo_filename = db.Column(db.String(255))
    site_name = db.Column(db.String(100), default='Kids & Baby Store')
    primary_color = db.Column(db.String(20), default='#0066ff')
    secondary_color = db.Column(db.String(20), default='#59b5fc')
    footer_color = db.Column(db.String(20), default='#232323')
    slide_duration = db.Column(db.Float, default=6)
    transition_duration = db.Column(db.Float, default=0.8)
    
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    cover_image_filename = db.Column(db.String(255))

    subcategories = db.relationship('Subcategory', backref='category', lazy=True)

class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship('Product', backref='subcategory', lazy=True)
    
# PSGC (Philippine Standard Geographic Code) Models for address selection
class Region(db.Model):
    __tablename__ = 'region'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    provinces = db.relationship('Province', backref='region', lazy=True, cascade='all, delete-orphan')


class Province(db.Model):
    __tablename__ = 'province'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    region_code = db.Column(db.String(10), db.ForeignKey('region.code'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    cities = db.relationship('City', backref='province', lazy=True, cascade='all, delete-orphan')


class City(db.Model):
    __tablename__ = 'city'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    province_code = db.Column(db.String(10), db.ForeignKey('province.code'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    barangays = db.relationship('Barangay', backref='city', lazy=True, cascade='all, delete-orphan')


class Barangay(db.Model):
    __tablename__ = 'barangay'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    city_code = db.Column(db.String(10), db.ForeignKey('city.code'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CityMunicipality(db.Model):
    __tablename__ = 'city_municipality'
    id = db.Column(db.Integer, primary_key=True)
    psgc_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey('region.id'), index=True)
    type = db.Column(db.String(50))  # 'City' or 'Municipality'
    zip_code = db.Column(db.String(10))
    district = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    province = db.relationship('Region', backref='cities_municipalities')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    # reserved_stock tracks quantities reserved by pending orders (not yet deducted)
    reserved_stock = db.Column(db.Integer, nullable=False, default=0)
    image_filename = db.Column(db.String(120))
    # NEW: optional product video filename (stored under static/uploads/videos)
    video_filename = db.Column(db.String(255))
    # NEW: additional gallery images (list of filenames under static/uploads)
    gallery = db.Column(db.JSON)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'))  # <-- NEW
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, active
    featured = db.Column(db.Boolean, default=False)
    show_in_new_arrival = db.Column(db.Boolean, default=False)   # <-- NEW FLAG
    # Rating and review count fields
    rating = db.Column(db.Float, default=0.0)  # Average rating (0.0 to 5.0)
    review_count = db.Column(db.Integer, default=0)  # Total number of reviews
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship('Category', backref='products')
    # Cascade deletes from User -> products at ORM level; DB-level CASCADE may require a migration
    seller = db.relationship('User', backref=db.backref('products', cascade='all, delete-orphan'))
    
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(120))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='published')  # published, pending, hidden
    image_filename = db.Column(db.String(255))  # legacy single image support
    media = db.Column(db.JSON)  # list of {type:'image'|'video', 'path': '/static/uploads/reviews/...'}
    verified_purchase = db.Column(db.Boolean, default=False)  # True if user purchased product
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))  # Link to purchase order

    product = db.relationship('Product', backref='reviews')
    user = db.relationship('User', backref='reviews')
    order = db.relationship('Order', backref='reviews')


class Coupon(db.Model):
    """Simple coupon/discount model for checkout."""
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    # 'percent' = percentage (e.g. 10 => 10% off subtotal), 'fixed' = fixed peso value
    discount_type = db.Column(db.String(20), default='percent')
    discount_value = db.Column(db.Float, nullable=False)
    min_order_amount = db.Column(db.Float, default=0.0)  # minimum subtotal required
    max_uses = db.Column(db.Integer)  # null/None = unlimited
    used_count = db.Column(db.Integer, default=0)
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('follower_id', 'seller_id', name='uq_follower_seller'),
    )

    follower = db.relationship('User', foreign_keys=[follower_id], backref='following')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='followers')

class RiderApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    employee_id = db.Column(db.String(50))  # Optional, can be generated
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Explicit relationships to disambiguate foreign keys:
    user = db.relationship(
        'User',
        foreign_keys=[user_id],
        backref=db.backref('rider_applications', lazy='dynamic')
    )
    reviewer = db.relationship(
        'User',
        foreign_keys=[reviewed_by],
        backref=db.backref('rider_reviews', lazy='dynamic')
    )




# Helper to notify all admins
def notify_admins(message, *, type=None, link=None, image_url=None):
    """Notify all admins and emit real-time (Supabase version). Optional metadata: type/link/image_url."""
    admin_users = get_data('user', filters={'role': 'admin'})
    if not admin_users:
        admin_users = []
    
    ids = []
    for admin in admin_users:
        notification_data = {
            'user_id': admin.get('id'),
            'message': message,
            'type': type,
            'link': link,
            'image_url': image_url
        }
        insert_data('notification', notification_data)
        ids.append(admin.get('id'))
    
    try:
        for aid in ids:
            payload = {'message': message}
            if type: payload['type'] = type
            if link: payload['link'] = link
            if image_url: payload['image_url'] = image_url
            socketio.emit('notification', payload, room=f'user_{aid}')
    except Exception:
        pass


# Configure OAuth storage after models are defined
google_bp.storage = SQLAlchemyStorage(OAuth, db.session, user=lambda: db.session.get(User, session.get('user_id')) if 'user_id' in session else None, user_required=False)

# OAuth signal handler
@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    """
    Google OAuth login handler.
    Modified to enforce ADMIN APPROVAL before a user (Googleâ€‘registered) can log in.
    A Google signâ€‘in will:
      - Create a 'pending' user (status='pending') if new.
      - NOT start a session until the account is approved (status becomes 'active').
      - Block login for existing OAuth or email accounts whose status != 'active'.
    """
    if not token:
        flash('Failed to log in with Google.', 'error')
        return False
    
    resp = blueprint.session.get("/oauth2/v3/userinfo")
    if not resp.ok:
        flash('Failed to fetch user info from Google.', 'error')
        return False
    
    google_info = resp.json()
    google_user_id = str(google_info.get("sub", google_info.get("id", "")))
    
    # Check if OAuth record already exists
    oauth_record = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=google_user_id
    ).first()
    
    if oauth_record:
        user = oauth_record.user
        # ENFORCE ADMIN APPROVAL
        if user.status != 'active':
            flash('Your account is pending admin approval. Please wait for confirmation before logging in.', 'warning')
            return False
        # Proceed with normal login
        session['user_id'] = user.id
        session['user_name'] = f"{user.first_name} {user.last_name}"
        session['user_role'] = user.role
        session['active_role'] = user.role
        flash('Welcome back!', 'success')
        return False  # Do not resave token
    
    # If user exists (matched by email) but no OAuth record yet
    user = User.query.filter_by(email=google_info["email"]).first()
    if user:
        # If user exists but NOT yet approved
        if user.status != 'active':
            flash('Your account is pending admin approval. You will be able to log in once approved.', 'warning')
            # Do NOT create OAuth record yet (to avoid premature login linkage)
            return False
        # User active: create OAuth link and log in
        oauth_record = OAuth(
            provider=blueprint.name,
            provider_user_id=google_user_id,
            user=user,
            token=token
        )
        db.session.add(oauth_record)
        db.session.commit()
        session['user_id'] = user.id
        session['user_name'] = f"{user.first_name} {user.last_name}"
        session['user_role'] = user.role
        session['active_role'] = user.role
        flash('Google account linked successfully!', 'success')
        return False
    
    # New Google user: create as PENDING (requires admin approval)
    new_user = User(
        first_name=google_info.get("given_name", "Google"),
        last_name=google_info.get("family_name", "User"),
        email=google_info["email"],
        password="google_oauth",  # still a placeholder (should be replaced / hashed in production)
        phone="",
        address="",
        role="buyer",
        status="pending",          # CRITICAL: must be approved before login
        email_verified=True        # Mark email verified (Google guarantees it); approval still required
    )
    db.session.add(new_user)
    db.session.commit()
    
    # Notify admins there is a new pending Google registration
    try:
        notify_admins(f'New Google registration pending approval: {new_user.first_name} {new_user.last_name} ({new_user.email})')
    except Exception:
        pass
    
    flash('Account created and pending admin approval. You will be able to log in once an administrator approves your account.', 'info')
    # IMPORTANT: Do NOT create OAuth record or start a session yet.
    return False



# Helper functions

# Philippine timezone helpers
PH_TZ = pytz_timezone('Asia/Manila')

def to_ph_time(utc_dt):
    """Convert UTC datetime to Philippine time"""
    if utc_dt is None:
        return None
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=pytz_timezone('UTC'))
    return utc_dt.astimezone(PH_TZ)

def format_ph_datetime(utc_dt):
    """Format datetime in PH time"""
    if utc_dt is None:
        return 'N/A'
    ph_time = to_ph_time(utc_dt)
    return ph_time.strftime('%B %d, %Y %I:%M %p')

def validate_password(password):
    """Validate password against professional requirements"""
    if len(password) < 8 or len(password) > 12:
        return False, "Password must be 8-12 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    if not re.search(r"[!@#$%^&*\-_]", password):
        return False, "Password must contain at least one special character (!@#$%^&*-_)"
    
    # Check for common weak passwords
    weak_passwords = ['password', 'password123', '12345678', 'qwerty123', 'admin123']
    if password.lower() in weak_passwords:
        return False, "This is a common weak password, please choose a stronger one"
    
    return True, "Password is strong"

def calculate_password_strength(password):
    """Calculate password strength score (0-100)"""
    score = 0
    
    # Length score (0-25)
    if len(password) >= 8:
        score += min(25, len(password) * 2)
    
    # Character type scores
    if re.search(r"[A-Z]", password):
        score += 20
    if re.search(r"[a-z]", password):
        score += 20
    if re.search(r"\d", password):
        score += 15
    if re.search(r"[!@#$%^&*\-_]", password):
        score += 20
    
    # Deduct for common patterns
    if password.lower() in ['password', 'password123', '12345678']:
        score = max(0, score - 30)
    
    return min(100, score)

def _send_refund_email(user, amount, order_id):
    try:
        from email.utils import formataddr
        
        subject = f"Refund processed for Order #{order_id}"
        body = (
            f"Hi {getattr(user,'first_name','Customer')},\n\n"
            f"Your return/refund has been completed. We credited ₱{float(amount):,.2f} to your wallet.\n"
            f"Order ID: {order_id}\n\n"
            "Thank you for shopping with us.\n"
            "Kids Kingdom Team"
        )
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = formataddr(('Kids Kingdom', app.config['MAIL_SENDER']))
        msg['To'] = user.email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
            smtp.send_message(msg)
    except Exception as e:
        app.logger.exception('Failed to send refund email to %s: %s', getattr(user,'email','unknown'), e)


def get_cart_count():
    """Get cart count with caching (Supabase version)."""
    if 'user_id' not in session:
        return 0
    # Use scalar query for fast count
    from sqlalchemy import func, select
    try:
        count = db.session.scalar(
            select(func.count(Cart.id)).where(Cart.user_id == session['user_id'])
        )
        return count or 0
    except:
        return 0

def can_user_review_product(user_id, product_id):
    """
    Check if a user can review a product based on purchase history (Supabase version).
    Returns: (can_review: bool, order_id: int or None, message: str)
    """
    # Check if user already reviewed this product
    existing_reviews = get_data('review', filters={'user_id': user_id, 'product_id': product_id})
    if existing_reviews and len(existing_reviews) > 0:
        return False, None, "You have already reviewed this product."
    
    # Find completed or delivered orders containing this product
    completed_orders = get_data('order', filters={'buyer_id': user_id})
    if not completed_orders:
        completed_orders = []
    
    # Filter for completed/delivered orders
    completed_orders = [o for o in completed_orders if o.get('status') in ['completed', 'delivered']]
    
    for order in completed_orders:
        order_items = get_data('order_item', filters={'order_id': order.get('id')})
        if not order_items:
            order_items = []
        
        for item in order_items:
            if item.get('product_id') == product_id:
                # Check if review is within 30 days of delivery (optional)
                delivered_at = order.get('delivered_at')
                if delivered_at:
                    if isinstance(delivered_at, str):
                        delivered_at = datetime.fromisoformat(delivered_at.replace('Z', '+00:00'))
                    # Ensure both datetimes are timezone-aware for comparison
                    if delivered_at.tzinfo is None:
                        delivered_at = delivered_at.replace(tzinfo=timezone.utc)
                    now_aware = datetime.now(timezone.utc)
                    days_since_delivery = (now_aware - delivered_at).days
                    if days_since_delivery > 30:
                        return False, None, "Review period (30 days after delivery) has expired."
                
                return True, order.get('id'), "You can review this product."
    
    return False, None, "You need to purchase this product to leave a review."

def get_user_purchased_products(user_id):
    """
    Get list of products that user has purchased and can review (Supabase version).
    Returns list of dicts with product info and review eligibility.
    """
    purchased_products = []
    completed_orders = get_data('order', filters={'buyer_id': user_id})
    if not completed_orders:
        completed_orders = []
    
    # Filter for completed/delivered orders and sort by delivered_at
    completed_orders = [o for o in completed_orders if o.get('status') in ['completed', 'delivered']]
    completed_orders.sort(key=lambda x: x.get('delivered_at') or '', reverse=True)
    
    seen_products = set()
    for order in completed_orders:
        order_items = get_data('order_item', filters={'order_id': order.get('id')})
        if not order_items:
            order_items = []
        
        for item in order_items:
            product_id = item.get('product_id')
            if product_id not in seen_products:
                seen_products.add(product_id)
                can_review, order_id, message = can_user_review_product(user_id, product_id)
                product = get_data_by_id('product', product_id)
                purchased_products.append({
                    'product': product,
                    'order': order,
                    'can_review': can_review,
                    'review_message': message,
                    'order_id': order_id
                })
    
    return purchased_products

def get_available_stock(product_id):
    """Get available stock using product.stock minus reserved_stock.

    This uses the new reservation model: `reserved_stock` stores quantities reserved
    by pending orders so available = stock - reserved_stock.
    """
    try:
        # Prefer ORM access to get current values (works even if product model has new column)
        product = db.session.get(Product, product_id)
        if not product:
            return 0

        reserved = int(product.reserved_stock or 0)
        available = int(product.stock or 0) - reserved
        result = max(0, available)

        app.logger.debug(f"get_available_stock: product={product_id} stock={product.stock} reserved={reserved} available={result}")
        return result
    except Exception as e:
        app.logger.error(f"Error calculating available stock for product {product_id}: {e}")
        return 0


def reserve_stock(order_id, product_id, quantity):
    """Reserve stock for an order without committing the session (caller commits).

    Shopee/Lazada-style flow: the product's available stock is reduced immediately
    by increasing product.reserved_stock. No separate reservation row is created.

    Returns True if reserved, False if insufficient stock or error.
    """
    try:
        product = db.session.get(Product, product_id)
        if not product:
            return False

        available = int(product.stock or 0) - int(product.reserved_stock or 0)
        if available < quantity:
            return False

        # Increase reserved_stock only; this is what lowers available stock for buyers.
        product.reserved_stock = (product.reserved_stock or 0) + quantity

        # Do not commit here; caller should commit to group operations together
        return True
    except Exception as e:
        app.logger.error(f"reserve_stock failed: {e}")
        return False


def release_stock(order_id):
    """Release reserved stock for an order. Commits the session.

    Returns list of product ids updated.
    """
    try:
        order = db.session.get(Order, order_id)
        if not order:
            return []

        updated = []
        for item in order.items:
            product = db.session.get(Product, item.product_id)
            if product:
                quantity = int(item.quantity or 0)
                if quantity <= 0:
                    continue

                # Preferred path: release the pending-order lock.
                if (product.reserved_stock or 0) >= quantity:
                    product.reserved_stock = max(0, (product.reserved_stock or 0) - quantity)
                # Legacy fallback: some older orders may have already deducted stock.
                elif getattr(order, 'stock_deducted', False):
                    product.stock = int(product.stock or 0) + quantity

                updated.append(product.id)

        order.stock_deducted = False

        db.session.commit()
        for pid in updated:
            broadcast_stock_update(pid)
        return updated
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"release_stock failed: {e}")
        return []


def complete_stock_reservation(order_id):
    """Finalize reserved stock for an order and deduct from actual stock.

    This is called when the seller/rider completes fulfillment. It consumes the
    pending-order lock by reducing reserved_stock and decrementing actual stock.

    Returns list of product ids updated.
    """
    try:
        order = db.session.get(Order, order_id)
        if not order:
            return []

        updated = []
        for item in order.items:
            product = db.session.get(Product, item.product_id)
            if product:
                quantity = int(item.quantity or 0)
                if quantity <= 0:
                    continue

                product.stock = max(0, int(product.stock or 0) - quantity)
                product.reserved_stock = max(0, int(product.reserved_stock or 0) - quantity)
                updated.append(product.id)

        order.stock_deducted = True

        db.session.commit()
        for pid in updated:
            broadcast_stock_update(pid)
        return updated
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"complete_stock_reservation failed: {e}")
        return []


def broadcast_stock_update(product_id):
    """Broadcast stock update to connected clients if SocketIO is configured."""
    try:
        product = db.session.get(Product, product_id)
        if not product:
            return
        reserved = int(product.reserved_stock or 0)
        available = max(0, int(product.stock or 0) - reserved)
        try:
            socketio.emit('product_stock_update', {
                'product_id': product_id,
                'stock': product.stock,
                'reserved_stock': reserved,
                'available_stock': available,
                'timestamp': datetime.utcnow().isoformat()
            }, broadcast=True)
        except Exception:
            # SocketIO may not be configured in some environments
            pass
        app.logger.info(f"Stock update broadcast: Product {product_id}, Available: {available}")
    except Exception as e:
        app.logger.error(f"broadcast_stock_update failed: {e}")

@app.route('/debug-products')
def debug_products():
    """Debug route to list all products and their stock status"""
    if not session.get('user_id') or session.get('active_role') != 'admin':
        return "Admin access required", 403
    
    products = Product.query.all()
    product_info = []
    
    for product in products:
        available_stock = get_available_stock(product.id)
        
        # Get detailed reservation information
        from sqlalchemy import func
        reserved_stock = db.session.query(
            func.sum(OrderItem.quantity)
        ).join(Order).filter(
            OrderItem.product_id == product.id,
            Order.status.in_(['pending', 'to_pay', 'processing'])
        ).scalar() or 0
        
        payment_reserved = db.session.query(
            func.sum(OrderItem.quantity)
        ).join(Order).filter(
            OrderItem.product_id == product.id,
            Order.payment_status.in_(['pending', 'awaiting_payment', 'failed']),
            Order.status != 'cancelled'
        ).scalar() or 0
        
        total_reserved = max(reserved_stock, payment_reserved)
        
        product_info.append({
            'id': product.id,
            'name': product.name,
            'stock': product.stock,
            'reserved_stock': reserved_stock,
            'payment_reserved': payment_reserved,
            'total_reserved': total_reserved,
            'available_stock': available_stock,
            'status': 'Out of Stock' if available_stock <= 0 else f'In Stock ({available_stock})'
        })
    
    # Sort by name for easier finding
    product_info.sort(key=lambda x: x['name'].lower())
    
    html = "<h2>Product Stock Status Debug</h2>"
    html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
    html += "<tr><th>ID</th><th>Name</th><th>Total Stock</th><th>Reserved</th><th>Payment Reserved</th><th>Total Reserved</th><th>Available</th><th>Status</th></tr>"
    for p in product_info:
        row_color = 'red' if p['available_stock'] <= 0 else 'green'
        html += f"<tr style='color: {row_color};'>"
        html += f"<td>{p['id']}</td>"
        html += f"<td>{p['name']}</td>"
        html += f"<td>{p['stock']}</td>"
        html += f"<td>{p['reserved_stock']}</td>"
        html += f"<td>{p['payment_reserved']}</td>"
        html += f"<td>{p['total_reserved']}</td>"
        html += f"<td>{p['available_stock']}</td>"
        html += f"<td>{p['status']}</td>"
        html += "</tr>"
    html += "</table>"
    
    # Add force restock buttons for out of stock items
    html += "<h3>Force Restock Out of Stock Items</h3>"
    for p in product_info:
        if p['available_stock'] <= 0:
            html += f"<div style='margin: 10px 0; padding: 10px; border: 1px solid #ccc;'>"
            html += f"<strong>{p['name']}</strong> (ID: {p['id']}) - "
            html += f"Stock: {p['stock']}, Reserved: {p['total_reserved']}, Available: {p['available_stock']}"
            html += f" <a href='/force-restock/{p['id']}' style='margin-left: 10px;' class='btn btn-primary btn-sm'>Force Restock +10</a>"
            html += f" <a href='/clear-reservations/{p['id']}' style='margin-left: 5px;' class='btn btn-warning btn-sm'>Clear All Reservations</a>"
            html += f"</div>"
    
    return html

@app.route('/force-restock/<int:product_id>')
def force_restock(product_id):
    """Force restock a product for testing"""
    if not session.get('user_id') or session.get('active_role') != 'admin':
        return "Admin access required", 403
    
    product = db.session.get(Product, product_id)
    if not product:
        return f"Product {product_id} not found", 404
    
    # Force add 10 to stock
    product.stock += 10
    db.session.commit()
    
    # Emit real-time update
    available_stock = get_available_stock(product_id)
    try:
        socketio.emit('product_stock_update', {
            'product_id': product_id,
            'stock': available_stock,
            'available_stock': available_stock
        }, broadcast=True)
    except Exception as e:
        pass
    
    return f"Product '{product.name}' (ID: {product_id}) force restocked by 10. New stock: {product.stock}, Available: {available_stock}. <a href='/debug-products'>Back to debug</a>"

@app.route('/clear-reservations/<int:product_id>')
def clear_reservations(product_id):
    """Clear all reservations for a product (for testing)"""
    if not session.get('user_id') or session.get('active_role') != 'admin':
        return "Admin access required", 403
    
    product = db.session.get(Product, product_id)
    if not product:
        return f"Product {product_id} not found", 404
    
    # Cancel all pending orders for this product
    orders_to_cancel = db.session.query(Order).join(OrderItem).filter(
        OrderItem.product_id == product_id,
        Order.status.in_(['pending', 'to_pay', 'processing'])
    ).all()
    
    cancelled_count = 0
    for order in orders_to_cancel:
        order.status = 'cancelled'
        order.updated_at = datetime.utcnow()
        cancelled_count += 1
    
    db.session.commit()
    
    # Emit real-time update
    available_stock = get_available_stock(product_id)
    try:
        socketio.emit('product_stock_update', {
            'product_id': product_id,
            'stock': available_stock,
            'available_stock': available_stock
        }, broadcast=True)
    except Exception as e:
        pass
    
    return f"Cleared {cancelled_count} orders for product '{product.name}' (ID: {product_id}). Available stock: {available_stock}. <a href='/debug-products'>Back to debug</a>"


@app.route('/set-out-of-stock/<int:product_id>')
def set_out_of_stock(product_id):
    """Temporarily set a product as out of stock for testing"""
    if not session.get('user_id') or session.get('active_role') != 'admin':
        return "Admin access required", 403
    
    product = db.session.get(Product, product_id)
    if not product:
        return f"Product {product_id} not found", 404
    
    # Temporarily set stock to 0 for testing
    original_stock = product.stock
    product.stock = 0
    db.session.commit()
    
    # Emit real-time update
    if 'socketio' in globals():
        socketio.emit('product_stock_update', {
            'product_id': product_id,
            'stock': 0,
            'available_stock': 0
        })
    
    return f"Product '{product.name}' (ID: {product_id}) set to out of stock. Original stock: {original_stock}. <a href='/debug-products'>View all products</a>"


def calculate_coupon_discount(code, subtotal):
    """Validate a coupon code and compute its discount for the given subtotal (Supabase version).

    Returns (coupon_dict_or_None, discount_amount: float, error_message: str or None).
    """
    if not code:
        return None, 0.0, None

    normalized = code.strip().upper()
    if not normalized:
        return None, 0.0, None

    # Case-insensitive lookup - fetch all active coupons and filter client-side
    coupons = get_data('coupon', filters={'is_active': True})
    if not coupons:
        coupons = []
    
    coupon = None
    for c in coupons:
        if c.get('code', '').upper() == normalized:
            coupon = c
            break
    
    if not coupon:
        return None, 0.0, "Invalid or inactive coupon code."

    now = datetime.now(timezone.utc)
    valid_from = coupon.get('valid_from')
    valid_until = coupon.get('valid_until')

    if valid_from:
        if isinstance(valid_from, str):
            valid_from = datetime.fromisoformat(valid_from.replace('Z', '+00:00'))
        if valid_from.tzinfo is None:
            valid_from = valid_from.replace(tzinfo=timezone.utc)
        if now < valid_from:
            return None, 0.0, "This coupon is not yet valid."

    if valid_until:
        if isinstance(valid_until, str):
            valid_until = datetime.fromisoformat(valid_until.replace('Z', '+00:00'))
        if valid_until.tzinfo is None:
            valid_until = valid_until.replace(tzinfo=timezone.utc)
        if now > valid_until:
            return None, 0.0, "This coupon has already expired."

    min_amount = coupon.get('min_order_amount') or 0.0
    if subtotal < min_amount:
        return None, 0.0, f"Minimum order amount for this coupon is ₱{min_amount:,.2f}."

    max_uses = coupon.get('max_uses')
    used_count = coupon.get('used_count') or 0
    if max_uses is not None and used_count >= max_uses:
        return None, 0.0, "This coupon has reached its maximum number of uses."

    discount_type = coupon.get('discount_type')
    discount_value = coupon.get('discount_value') or 0
    
    if discount_type == 'percent':
        discount_amount = subtotal * (discount_value / 100.0)
    elif discount_type == 'fixed':
        discount_amount = discount_value
    elif discount_type == 'free_shipping':
        # Shipping will be set to 0 at the route level; no direct subtotal discount needed here
        discount_amount = 0.0
    else:
        # Unknown type: treat as no discount
        return None, 0.0, "Invalid or unsupported coupon type."

    # Do not allow discount to exceed subtotal
    discount_amount = max(0.0, min(discount_amount, subtotal))
    return coupon, float(discount_amount), None


def is_admin():
    if 'user_id' not in session:
        return False
    user = db.session.get(User, session['user_id'])
    return user and user.role == 'admin'

def is_seller():
    if 'user_id' not in session:
        return False
    user = db.session.get(User, session['user_id'])
    if not user:
        return False
    # Admins may access seller pages for management purposes
    if user.role == 'admin':
        return True
    # Require Seller mode AND an approved seller application (prevents early access)
    active_role = session.get('active_role', user.role)
    if active_role != 'seller':
        return False
    approved = SellerApplication.query.filter_by(user_id=user.id, status='approved').first()
    return approved is not None

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def seller_required(f):
    def decorated_function(*args, **kwargs):
        if not is_seller():
            flash('Seller access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Rider role helpers

def is_rider():
    if 'user_id' not in session:
        return False
    user = db.session.get(User, session['user_id'])
    if not user:
        return False
    active_role = session.get('active_role', user.role)
    return (user.role == 'rider' or active_role == 'rider') and user.status == 'active'


def rider_required(f):
    def decorated_function(*args, **kwargs):
        if not is_rider():
            flash('Rider access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# PayMongo Configuration
PAYMONGO_PUBLIC_KEY = 'pk_test_your_public_key_here'
PAYMONGO_SECRET_KEY = 'sk_test_your_secret_key_here'

# send account status update email (approve/reject)
def send_account_status_email(to_email, approved=True, reason=None):
    """
    Sends an email to the user notifying them whether their account was approved or rejected.
    approved: bool
    reason: optional rejection reason string
    """
    try:
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.utils import formataddr
        
        if approved:
            subject = "🎉 Welcome to Kids Kingdom - Account Approved!"
            
            html_body = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }
                    .container { max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
                    .header { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 40px 30px; text-align: center; }
                    .header h1 { margin: 0; font-size: 32px; font-weight: 600; }
                    .header p { margin: 10px 0 0 0; font-size: 18px; opacity: 0.95; }
                    .content { padding: 40px 30px; background: #ffffff; }
                    .button { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 20px 0; font-weight: bold; box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3); transition: transform 0.2s; }
                    .button:hover { transform: translateY(-2px); }
                    .features { background: #f8f9fa; padding: 25px; border-radius: 10px; margin: 25px 0; }
                    .features h3 { margin-top: 0; color: #11998e; font-size: 20px; }
                    .feature-item { padding: 12px 0; border-bottom: 1px solid #e9ecef; display: flex; align-items: center; }
                    .feature-item:last-child { border-bottom: none; }
                    .feature-icon { font-size: 24px; margin-right: 15px; }
                    .footer { background: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef; }
                    .footer p { margin: 5px 0; color: #666; font-size: 13px; }
                    .icon { font-size: 64px; margin-bottom: 15px; }
                    .welcome-text { font-size: 16px; color: #555; line-height: 1.8; }
                    .divider { height: 1px; background: linear-gradient(to right, transparent, #ddd, transparent); margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="icon">🎉</div>
                        <h1>Congratulations!</h1>
                        <p>Your account has been approved</p>
                    </div>
                    <div class="content">
                        <p style="font-size: 16px; color: #333;">Hello,</p>
                        
                        <p class="welcome-text"><strong>Great news!</strong> Your Kids Kingdom account has been successfully approved by our administrator. You can now enjoy all the features and benefits of our platform.</p>
                        
                        <div class="features">
                            <h3>✨ What you can do now:</h3>
                            <div class="feature-item">
                                <span class="feature-icon">🛍️</span>
                                <span>Browse and purchase quality kids products</span>
                            </div>
                            <div class="feature-item">
                                <span class="feature-icon">💳</span>
                                <span>Secure checkout with multiple payment options</span>
                            </div>
                            <div class="feature-item">
                                <span class="feature-icon">📦</span>
                                <span>Track your orders in real-time</span>
                            </div>
                            <div class="feature-item">
                                <span class="feature-icon">⭐</span>
                                <span>Leave reviews and ratings</span>
                            </div>
                            <div class="feature-item">
                                <span class="feature-icon">🎁</span>
                                <span>Access exclusive deals and promotions</span>
                            </div>
                        </div>
                        
                        <center>
                            <a href="http://localhost:5000/login" class="button">Login to Your Account →</a>
                        </center>
                        
                        <div class="divider"></div>
                        
                        <p class="welcome-text">If you have any questions or need assistance getting started, our support team is here to help!</p>
                    </div>
                    <div class="footer">
                        <p style="font-size: 16px; margin-bottom: 10px;">Welcome to the Kids Kingdom family! 👶🛍️💙</p>
                        <p style="font-size: 15px; color: #11998e; font-weight: 600;">Kids Kingdom Team</p>
                        <div class="divider" style="margin: 20px 40px;"></div>
                        <p>📧 <a href="mailto:support@kidskingdom.com" style="color: #11998e; text-decoration: none;">support@kidskingdom.com</a> | 📱 +63 XXX XXX XXXX</p>
                        <p style="color: #999; font-size: 11px; margin-top: 15px;">© 2026 Kids Kingdom. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_body = """
            🎉 Congratulations! Your Account Has Been Approved
            
            Hello,
            
            Great news! Your Kids Kingdom account has been approved by our administrator.
            
            ✨ You can now:
            🛍️ Browse and purchase quality kids products
            💳 Secure checkout with multiple payment options
            📦 Track your orders in real-time
            ⭐ Leave reviews and ratings
            🎁 Access exclusive deals and promotions
            
            Login now at: http://localhost:5000/login
            
            Welcome to the Kids Kingdom family! 👶🛍️💙
            
            Best regards,
            Kids Kingdom Team
            
            ---
            📧 Email: support@kidskingdom.com
            📱 Phone: +63 XXX XXX XXXX
            © 2026 Kids Kingdom. All rights reserved.
            """
        
        else:
            # Account Rejected
            subject = "📋 Account Registration Update - Kids Kingdom"
            
            reason_html = f"<div style='background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;'><strong style='color: #856404;'>Reason:</strong> {reason}</div>" if reason else ""
            reason_text = f"\n\nReason: {reason}\n" if reason else "\n"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
                    .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 40px 30px; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 28px; font-weight: 600; }}
                    .content {{ padding: 40px 30px; background: #ffffff; }}
                    .info-box {{ background: #e7f3ff; border-left: 4px solid #2196F3; padding: 20px; margin: 25px 0; border-radius: 5px; }}
                    .info-box strong {{ color: #1976D2; display: block; margin-bottom: 10px; font-size: 16px; }}
                    .info-box ul {{ margin: 10px 0; padding-left: 20px; }}
                    .info-box li {{ margin: 8px 0; color: #555; }}
                    .button {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: 600; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); }}
                    .footer {{ background: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef; }}
                    .footer p {{ margin: 5px 0; color: #666; font-size: 13px; }}
                    .icon {{ font-size: 48px; margin-bottom: 10px; }}
                    .divider {{ height: 1px; background: linear-gradient(to right, transparent, #ddd, transparent); margin: 20px 0; }}
                    .info-text {{ color: #555; font-size: 15px; line-height: 1.8; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="icon">📋</div>
                        <h1>Account Registration Update</h1>
                    </div>
                    <div class="content">
                        <p style="font-size: 16px; color: #333;">Hello,</p>
                        
                        <p class="info-text">Thank you for your interest in Kids Kingdom.</p>
                        
                        <p class="info-text">We regret to inform you that your account registration was not approved at this time.</p>
                        
                        {reason_html}
                        
                        <div class="info-box">
                            <strong>💡 What you can do next:</strong>
                            <ul>
                                <li>Review the reason provided above carefully</li>
                                <li>Update your information and reapply for an account</li>
                                <li>Contact our support team for clarification or assistance</li>
                                <li>Ensure all required documents are valid and clearly visible</li>
                            </ul>
                        </div>
                        
                        <p class="info-text">If you believe this was a mistake or need assistance with your application, please don't hesitate to reach out to our support team. We're here to help!</p>
                        
                        <center>
                            <a href="mailto:support@kidskingdom.com" class="button">📧 Contact Support</a>
                        </center>
                        
                        <div class="divider"></div>
                        
                        <p class="info-text" style="font-size: 14px; color: #666;">We appreciate your understanding and look forward to potentially serving you in the future.</p>
                    </div>
                    <div class="footer">
                        <p style="font-size: 15px; margin-bottom: 10px;"><strong>Best regards,</strong></p>
                        <p style="font-size: 15px; color: #667eea; font-weight: 600;">Kids Kingdom Team</p>
                        <div class="divider" style="margin: 20px 40px;"></div>
                        <p>📧 <a href="mailto:support@kidskingdom.com" style="color: #667eea; text-decoration: none;">support@kidskingdom.com</a> | 📱 +63 XXX XXX XXXX</p>
                        <p style="color: #999; font-size: 11px; margin-top: 15px;">© 2026 Kids Kingdom. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            📋 Account Registration Update - Kids Kingdom
            
            Hello,
            
            Thank you for your interest in Kids Kingdom.
            
            We regret to inform you that your account registration was not approved at this time.
            {reason_text}
            💡 What you can do next:
            • Review the reason provided above carefully
            • Update your information and reapply for an account
            • Contact our support team for clarification or assistance
            • Ensure all required documents are valid and clearly visible
            
            If you need assistance, please contact us at support@kidskingdom.com
            
            We appreciate your understanding.
            
            Best regards,
            Kids Kingdom Team
            
            ---
            📧 Email: support@kidskingdom.com
            📱 Phone: +63 XXX XXX XXXX
            © 2026 Kids Kingdom. All rights reserved.
            """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = formataddr(('Kids Kingdom', app.config['MAIL_SENDER']))
        msg['To'] = to_email
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
            smtp.send_message(msg)
    except Exception as e:
        # log and continue (don't raise)
        app.logger.exception("Failed to send account status email to %s: %s", to_email, e)


def send_rider_status_email(to_email, approved=True, user_name="Rider", reason=None):
    """
    Sends an email to the rider notifying them whether their application was approved or rejected.
    approved: bool
    user_name: rider's full name
    reason: optional rejection reason string
    """
    try:
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.utils import formataddr
        
        if approved:
            subject = "🎉 Congratulations! Your Rider Application is Approved"
            
            html_body = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }
                    .container { max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }
                    .header h1 { margin: 0; font-size: 32px; font-weight: 600; }
                    .header p { margin: 10px 0 0 0; font-size: 18px; opacity: 0.95; }
                    .content { padding: 40px 30px; background: #ffffff; }
                    .button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 20px 0; font-weight: bold; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); transition: transform 0.2s; }
                    .button:hover { transform: translateY(-2px); }
                    .features { background: #f8f9fa; padding: 25px; border-radius: 10px; margin: 25px 0; }
                    .features h3 { margin-top: 0; color: #667eea; font-size: 20px; }
                    .feature-item { padding: 12px 0; border-bottom: 1px solid #e9ecef; display: flex; align-items: center; }
                    .feature-item:last-child { border-bottom: none; }
                    .feature-icon { font-size: 24px; margin-right: 15px; }
                    .footer { background: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef; }
                    .footer p { margin: 5px 0; color: #666; font-size: 13px; }
                    .icon { font-size: 64px; margin-bottom: 15px; }
                    .welcome-text { font-size: 16px; color: #555; line-height: 1.8; }
                    .divider { height: 1px; background: linear-gradient(to right, transparent, #ddd, transparent); margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="icon">🏍️</div>
                        <h1>Welcome Aboard!</h1>
                        <p>You're now a Kids Kingdom Rider</p>
                    </div>
                    <div class="content">
                        <p style="font-size: 16px; color: #333;">Hello """ + user_name + """,</p>
                        
                        <p class="welcome-text"><strong>Congratulations!</strong> Your rider application has been approved by our administrator. You can now start accepting delivery orders and earning money with Kids Kingdom.</p>
                        
                        <div class="features">
                            <h3>🚀 What you can do now:</h3>
                            <div class="feature-item">
                                <span class="feature-icon">📦</span>
                                <span>Accept and deliver orders in your area</span>
                            </div>
                            <div class="feature-item">
                                <span class="feature-icon">💰</span>
                                <span>Earn delivery fees for each completed order</span>
                            </div>
                            <div class="feature-item">
                                <span class="feature-icon">📱</span>
                                <span>Track your earnings and delivery history</span>
                            </div>
                            <div class="feature-item">
                                <span class="feature-icon">⭐</span>
                                <span>Build your reputation with customer ratings</span>
                            </div>
                            <div class="feature-item">
                                <span class="feature-icon">🎯</span>
                                <span>Flexible schedule - work when you want</span>
                            </div>
                        </div>
                        
                        <center>
                            <a href="http://localhost:5000/login" class="button">Login to Start Delivering →</a>
                        </center>
                        
                        <div class="divider"></div>
                        
                        <p class="welcome-text"><strong>Important:</strong> Make sure your vehicle is in good condition and you have all necessary documents ready. Always prioritize safety and customer satisfaction!</p>
                        
                        <p class="welcome-text">If you have any questions or need assistance, our support team is here to help!</p>
                    </div>
                    <div class="footer">
                        <p style="font-size: 16px; margin-bottom: 10px;">Welcome to the Kids Kingdom Rider Team! 🏍️📦💙</p>
                        <p style="font-size: 15px; color: #667eea; font-weight: 600;">Kids Kingdom Team</p>
                        <div class="divider" style="margin: 20px 40px;"></div>
                        <p>📧 <a href="mailto:support@kidskingdom.com" style="color: #667eea; text-decoration: none;">support@kidskingdom.com</a> | 📱 +63 XXX XXX XXXX</p>
                        <p style="color: #999; font-size: 11px; margin-top: 15px;">© 2026 Kids Kingdom. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            🎉 Congratulations! Your Rider Application is Approved
            
            Hello {user_name},
            
            Great news! Your rider application has been approved by our administrator.
            
            🚀 You can now:
            📦 Accept and deliver orders in your area
            💰 Earn delivery fees for each completed order
            📱 Track your earnings and delivery history
            ⭐ Build your reputation with customer ratings
            🎯 Flexible schedule - work when you want
            
            Login now at: http://localhost:5000/login
            
            Important: Make sure your vehicle is in good condition and you have all necessary documents ready. Always prioritize safety and customer satisfaction!
            
            Welcome to the Kids Kingdom Rider Team! 🏍️📦💙
            
            Best regards,
            Kids Kingdom Team
            
            ---
            📧 Email: support@kidskingdom.com
            📱 Phone: +63 XXX XXX XXXX
            © 2026 Kids Kingdom. All rights reserved.
            """
        
        else:
            # Application Rejected
            subject = "📋 Rider Application Update - Kids Kingdom"
            
            reason_html = f"<div style='background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;'><strong style='color: #856404;'>Reason:</strong> {reason}</div>" if reason else ""
            reason_text = f"\n\nReason: {reason}\n" if reason else "\n"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
                    .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 40px 30px; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 28px; font-weight: 600; }}
                    .content {{ padding: 40px 30px; background: #ffffff; }}
                    .info-box {{ background: #e7f3ff; border-left: 4px solid #2196F3; padding: 20px; margin: 25px 0; border-radius: 5px; }}
                    .info-box strong {{ color: #1976D2; display: block; margin-bottom: 10px; font-size: 16px; }}
                    .info-box ul {{ margin: 10px 0; padding-left: 20px; }}
                    .info-box li {{ margin: 8px 0; color: #555; }}
                    .button {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: 600; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); }}
                    .footer {{ background: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef; }}
                    .footer p {{ margin: 5px 0; color: #666; font-size: 13px; }}
                    .icon {{ font-size: 48px; margin-bottom: 10px; }}
                    .divider {{ height: 1px; background: linear-gradient(to right, transparent, #ddd, transparent); margin: 20px 0; }}
                    .info-text {{ color: #555; font-size: 15px; line-height: 1.8; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="icon">📋</div>
                        <h1>Rider Application Update</h1>
                    </div>
                    <div class="content">
                        <p style="font-size: 16px; color: #333;">Hello {user_name},</p>
                        
                        <p class="info-text">Thank you for your interest in becoming a Kids Kingdom rider.</p>
                        
                        <p class="info-text">We regret to inform you that your rider application was not approved at this time.</p>
                        
                        {reason_html}
                        
                        <div class="info-box">
                            <strong>💡 What you can do next:</strong>
                            <ul>
                                <li>Review the reason provided above carefully</li>
                                <li>Update your information and vehicle documents</li>
                                <li>Reapply for a rider account when ready</li>
                                <li>Contact our support team for clarification or assistance</li>
                                <li>Ensure all required documents are valid and clearly visible</li>
                            </ul>
                        </div>
                        
                        <center>
                            <a href="mailto:support@kidskingdom.com" class="button">Contact Support</a>
                        </center>
                        
                        <div class="divider"></div>
                        
                        <p class="info-text">We appreciate your understanding and interest in joining our delivery team.</p>
                    </div>
                    <div class="footer">
                        <p style="font-size: 15px; color: #667eea; font-weight: 600;">Kids Kingdom Team</p>
                        <div class="divider" style="margin: 20px 40px;"></div>
                        <p>📧 <a href="mailto:support@kidskingdom.com" style="color: #667eea; text-decoration: none;">support@kidskingdom.com</a> | 📱 +63 XXX XXX XXXX</p>
                        <p style="color: #999; font-size: 11px; margin-top: 15px;">© 2026 Kids Kingdom. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            📋 Rider Application Update
            
            Hello {user_name},
            
            Thank you for your interest in becoming a Kids Kingdom rider.
            
            We regret to inform you that your rider application was not approved at this time.
            {reason_text}
            💡 What you can do next:
            • Review the reason provided above carefully
            • Update your information and vehicle documents
            • Reapply for a rider account when ready
            • Contact our support team for clarification or assistance
            • Ensure all required documents are valid and clearly visible
            
            If you need assistance, please contact us at support@kidskingdom.com
            
            We appreciate your understanding and interest in joining our delivery team.
            
            Best regards,
            Kids Kingdom Team
            
            ---
            📧 Email: support@kidskingdom.com
            📱 Phone: +63 XXX XXX XXXX
            © 2026 Kids Kingdom. All rights reserved.
            """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = formataddr(('Kids Kingdom', app.config['MAIL_SENDER']))
        msg['To'] = to_email
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
            smtp.send_message(msg)
        
        app.logger.info(f"Rider status email sent successfully to {to_email}")
        return True
    except Exception as e:
        # log and continue (don't raise)
        app.logger.exception("Failed to send rider status email to %s: %s", to_email, e)
        return False


def send_coupon_email(user, coupon, discount_text=None):
    """Send a professional coupon email to a buyer.

    discount_text is an optional human-friendly summary, e.g. "10% off your next order".
    """
    try:
        from email.utils import formataddr
        
        subject = "You received a new coupon from Kids Kingdom"
        discount_label = discount_text
        if not discount_label:
            if coupon.discount_type == 'percent':
                discount_label = f"{coupon.discount_value:.0f}% off your order"
            else:
                discount_label = f"₱{coupon.discount_value:,.2f} off your order"

        min_order_part = ""
        if coupon.min_order_amount:
            min_order_part = f" (min. order ₱{coupon.min_order_amount:,.2f})"

        validity_part = ""
        if coupon.valid_until:
            validity_part = f" until {coupon.valid_until.strftime('%Y-%m-%d')}"

        body = (
            f"Hi {user.first_name},\n\n"
            f"You have received a new coupon for our Kids Kingdom.\n\n"
            f"Code: {coupon.code}\n"
            f"Offer: {discount_label}{min_order_part}{validity_part}.\n\n"
            "To use this coupon, enter the code on the checkout page before placing your order.\n\n"
            "Thank you for shopping with us!\n"
            "Kids Kingdom Team"
        )

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = formataddr(('Kids Kingdom', app.config['MAIL_SENDER']))
        msg['To'] = user.email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
            smtp.send_message(msg)
    except Exception as e:
        app.logger.exception("Failed to send coupon email to %s: %s", getattr(user, 'email', 'unknown'), e)

# Replace the existing index() and admin_hero_slides() with these versions.

# ---- Return/Refund real-time helper ----

def _emit_return_update(rr, extra=None):
    try:
        payload = {
            'return_id': rr.id,
            'order_id': rr.order_id,
            'status': rr.status,
            'buyer_id': rr.buyer_id,
            'seller_id': rr.seller_id
        }
        if extra and isinstance(extra, dict):
            payload.update(extra)
        # Notify buyer and seller rooms
        socketio.emit('return_update', payload, room=f'user_{rr.buyer_id}')
        socketio.emit('return_update', payload, room=f'user_{rr.seller_id}')
        # Riders may show available/active counts
        socketio.emit('return_update', payload, room='riders')
    except Exception:
        pass

# Ensure Notification has rich fields (image_url, link, type, actor_user_id)

def ensure_notification_extra_columns():
    try:
        inspector = sa_inspect(db.engine)
        try:
            cols = {c['name'] for c in inspector.get_columns('notification')}
        except Exception:
            return
        stmts = []
        if 'image_url' not in cols:
            stmts.append("ALTER TABLE notification ADD COLUMN image_url VARCHAR(255)")
        if 'link' not in cols:
            stmts.append("ALTER TABLE notification ADD COLUMN link VARCHAR(255)")
        if 'type' not in cols:
            stmts.append("ALTER TABLE notification ADD COLUMN type VARCHAR(40)")
        if 'actor_user_id' not in cols:
            stmts.append("ALTER TABLE notification ADD COLUMN actor_user_id INTEGER")
        if 'order_id' not in cols:
            stmts.append("ALTER TABLE notification ADD COLUMN order_id INTEGER")
        if 'images' not in cols:
            # Prefer JSON; MariaDB accepts JSON alias to LONGTEXT
            stmts.append("ALTER TABLE notification ADD COLUMN images JSON")
        for s in stmts:
            db.session.execute(_sa_text(s))
        if stmts:
            db.session.commit()
    except Exception:
        db.session.rollback()
        pass

def ensure_seller_application_background_column():
    """Ensure SellerApplication has store_background column for store banner images."""
    try:
        inspector = sa_inspect(db.engine)
        try:
            cols = {c['name'] for c in inspector.get_columns('seller_application')}
        except Exception:
            return
        if 'store_background' not in cols:
            db.session.execute(_sa_text("ALTER TABLE seller_application ADD COLUMN store_background VARCHAR(255)"))
            db.session.commit()
    except Exception:
        db.session.rollback()
        pass

def fix_sequence_for_table(table_name):
    """Fix PostgreSQL sequence for a table when it gets out of sync."""
    try:
        last_key = f'_sequence_fixed_{table_name}'
        last_fixed = app.config.get(last_key)
        now = time.time()
        if last_fixed and (now - last_fixed) < 300:
            return

        # Only run for PostgreSQL
        if 'postgresql' not in str(db.engine.url).lower():
            return

        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', table_name):
            raise ValueError(f'Invalid table name: {table_name}')

        sql = (
            "SELECT setval(pg_get_serial_sequence(:table_name, 'id'), "
            f"(SELECT COALESCE(MAX(id), 0) FROM {table_name}) + 1, false)"
        )
        db.session.execute(_sa_text(sql), {'table_name': table_name})
        db.session.commit()
        app.config[last_key] = now
        print(f"[OK] Fixed sequence for {table_name}")
    except Exception as e:
        db.session.rollback()
        print(f"[WARN] Could not fix sequence for {table_name}: {e}")
        pass

def force_fix_sequence_for_table(table_name):
    """Immediately fix a PostgreSQL serial sequence for request-time recovery."""
    try:
        if 'postgresql' not in str(db.engine.url).lower():
            return False

        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', table_name):
            raise ValueError(f'Invalid table name: {table_name}')

        sql = (
            "SELECT setval(pg_get_serial_sequence(:table_name, 'id'), "
            f"(SELECT COALESCE(MAX(id), 0) FROM {table_name}) + 1, false)"
        )
        db.session.execute(_sa_text(sql), {'table_name': table_name})
        db.session.commit()
        app.config[f'_sequence_fixed_{table_name}'] = time.time()
        print(f"[OK] Fixed sequence for {table_name}")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"[WARN] Could not fix sequence for {table_name}: {e}")
        return False

@app.route('/')
def index():
    """
    Homepage showing all approved products with hero slides.
    Optimized with eager loading to prevent N+1 queries.
    """
    try:
        from sqlalchemy.orm import joinedload

        # Get all active products with eager loading - ONE query instead of many
        products = Product.query.options(
            joinedload(Product.seller),
            joinedload(Product.category)
        ).filter(Product.status.in_(['approved', 'active'])).order_by(Product.created_at.desc()).limit(24).all()

        # Get hero slides for homepage banner
        hero_slides = HeroSlide.query.filter_by(is_active=True).order_by(HeroSlide.created_at.asc()).limit(6).all()

        # Get unique categories
        all_categories = Category.query.filter_by(status='active').order_by(Category.name).all()
        seen_names = set()
        categories = []
        for cat in all_categories:
            if cat.name not in seen_names:
                seen_names.add(cat.name)
                categories.append(cat)
    except Exception as e:
        print(f"[ERROR] Database query failed in index route: {e}")
        # Fallback to REST API
        products = get_data('product', filters={'status': ['approved', 'active']}, order='created_at.desc', limit=24) or []
        hero_slides = []
        categories = get_data('category', filters={'status': 'active'}) or []

    return render_template('buyer_home.html',
        products=products,
        hero_slides=hero_slides,
        categories=categories
    )


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page with all required data"""
    # Load product
    product = Product.query.filter(
        Product.id == product_id,
        Product.status.in_(['approved', 'active'])
    ).first()
    
    if not product:
        flash('Product not found or unavailable', 'error')
        return redirect(url_for('index'))
    
    # Calculate available stock using reservation-aware inventory only.
    try:
        available_stock = get_available_stock(product.id)
    except:
        available_stock = 0
    
    # Get product images (main + gallery)
    product_images = []
    
    # Add main image
    if product.image_filename:
        product_images.append(product.image_filename)
    
    # Add gallery images
    if product.gallery:
        try:
            import json
            gallery = json.loads(product.gallery) if isinstance(product.gallery, str) else product.gallery
            if isinstance(gallery, list):
                product_images.extend(gallery)
        except:
            pass
    
    # Build media items with proper URLs
    media_items = []
    for img in product_images:
        if img:  # Make sure image filename is not empty
            # Clean the filename - remove any 'uploads/' prefix if present
            clean_img = img.replace('uploads/', '').replace('uploads\\', '')
            media_items.append({
                'type': 'image',
                'url': url_for('static', filename=f'uploads/{clean_img}'),
                'path': url_for('static', filename=f'uploads/{clean_img}')
            })
    
    # If no images, add a placeholder
    if not media_items:
        placeholder_url = url_for('static', filename='placeholder.png')
        media_items.append({
            'type': 'image',
            'url': placeholder_url,
            'path': placeholder_url
        })
    
    # Calculate average rating
    from rating_helper import calculate_product_rating
    avg_rating, review_count = calculate_product_rating(db, Review, product_id)
    reviews = Review.query.filter_by(product_id=product_id).all()
    
    # Get related products
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product_id,
        Product.status.in_(['approved', 'active'])
    ).limit(4).all()
    
    # Check wishlist
    in_wishlist = False
    can_review = False
    
    if 'user_id' in session:
        in_wishlist = Wishlist.query.filter_by(
            user_id=session['user_id'],
            product_id=product_id
        ).first() is not None
        
        # Check if user purchased and can review
        purchased = OrderItem.query.join(Order).filter(
            Order.buyer_id == session['user_id'],
            OrderItem.product_id == product_id,
            Order.status.in_(['delivered', 'completed'])
        ).first()
        
        existing_review = Review.query.filter_by(
            user_id=session['user_id'],
            product_id=product_id
        ).first()
        
        can_review = purchased is not None and existing_review is None
    
    return render_template('product_detail.html',
                         product=product,
                         available_stock=available_stock,
                         media_items=media_items,
                         avg_rating=avg_rating,
                         review_count=review_count,
                         reviews=reviews,
                         related_products=related_products,
                         in_wishlist=in_wishlist,
                         can_review=can_review)



@app.route('/admin/hero-slides', methods=['GET', 'POST'])
@admin_required
def admin_hero_slides():
    if request.method == 'POST':
        # Handle upload
        file = request.files.get('image')
        link = request.form.get('link', '')
        if not file or not file.filename:
            flash('Please select an image to upload.', 'danger')
            return redirect(url_for('admin_hero_slides'))

        filename = secure_filename(file.filename)
        # Use upload folder
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file.save(upload_path)

        slide = HeroSlide(
            image_filename=filename,
            link=link,
            is_active=True
        )
        db.session.add(slide)
        db.session.commit()
        flash('Slide added!', 'success')
        return redirect(url_for('admin_hero_slides'))

    # Return slides in upload order (oldest first). Pass variable hero_slides to template (template expects hero_slides).
    hero_slides = HeroSlide.query.filter_by(is_active=True).order_by(HeroSlide.created_at.asc()).all()
    badge_counts = get_admin_badge_counts()
    return render_template('admin/hero_slides.html', hero_slides=hero_slides, **badge_counts)
    
    
@app.route('/dashboard')
@login_required
def dashboard():
    user = db.session.get(User, session['user_id'])
    active_role = session.get('active_role', user.role)
    
    if user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif active_role == 'seller':
        return redirect(url_for('seller_dashboard'))
    elif user.role == 'rider' or active_role == 'rider':
        return redirect(url_for('rider_dashboard'))
    else:
        # Buyer dashboard - show recent orders and recommendations
        # Notify buyer if seller application was approved (one-time per session)
        approved_app = SellerApplication.query.filter_by(user_id=session['user_id'], status='approved').first()
        if approved_app and not session.get('seller_approved_notified'):
            flash('Your account has been approved to become a seller. You can switch to Seller mode from the header.', 'success')
            session['seller_approved_notified'] = True
        recent_orders = Order.query.filter_by(buyer_id=session['user_id']).order_by(Order.created_at.desc()).limit(5).all()
        wishlist_items = Wishlist.query.filter_by(user_id=session['user_id']).limit(6).all()
        return render_template('buyer_dashboard.html', 
                             recent_orders=recent_orders, 
                             wishlist_items=wishlist_items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        remember = 'remember' in request.form

        # ----------------------------------------------------
        # Direct admin login ("admin" or "admin@kidscommerce.com")
        # ----------------------------------------------------
        admin_identifiers = ('admin', 'admin@kidscommerce.com')
        if email.lower() in admin_identifiers:
            admin_email = 'admin@kidscommerce.com'
            allowed_admin_passwords = ('admin123', 'Admin123!')  # support both defaults

            admin = User.query.filter_by(email=admin_email, role='admin').first()

            # If admin doesn't exist yet, create it only when a known default password is used
            if admin is None:
                if password not in allowed_admin_passwords:
                    flash('Invalid email or password.', 'error')
                    return render_template('login.html')

                admin = User(
                    first_name='Admin',
                    last_name='User',
                    email=admin_email,
                    password=password,
                    phone='1234567890',
                    address='Admin Office',
                    role='admin',
                    status='active',
                    email_verified=True
                )
                db.session.add(admin)
                db.session.commit()
            else:
                # Make sure admin is active and email-verified
                if admin.status != 'active':
                    admin.status = 'active'
                admin.email_verified = True

                # If user typed one of the known default passwords, sync it
                if password in allowed_admin_passwords and admin.password != password:
                    admin.password = password

                db.session.commit()

                # Final password check for admin
                if admin.password != password:
                    flash('Invalid email or password.', 'error')
                    return render_template('login.html')

            # Log admin in and go straight to dashboard
            session['user_id'] = admin.id
            session['user_name'] = f"{admin.first_name} {admin.last_name}"
            session['user_role'] = admin.role
            session['active_role'] = admin.role

            admin_profile = AdminProfile.query.filter_by(user_id=admin.id).first()
            if admin_profile:
                admin_profile.last_login = datetime.utcnow()
                db.session.commit()

            log_admin_action('Login', f'Admin login from IP: {request.remote_addr}')
            return redirect(url_for('admin_dashboard'))

        # ----------------------------------------------------
        # Normal login (buyers / sellers and non-direct admins)
        # ----------------------------------------------------
        # Check user by email only
        user = User.query.filter_by(email=email).first()

        # If credentials are correct but the account is not yet active,
        # show a clear status message instead of a generic login error.
        if user and user.password == password and user.status != 'active':
            # Rider accounts that are still pending admin review
            if user.role == 'rider' and user.status == 'pending':
                return render_template('rider/account_under_review.html', user=user)

            # Other pending accounts (e.g., buyers/sellers)
            if user.status == 'pending':
                return render_template('registration_status.html', role=(user.role or 'buyer'))

            # Rejected or otherwise inactive accounts
            if user.status == 'rejected':
                flash('Your account registration was not approved. You may update your information and reapply.', 'error')
            else:
                flash('Your account is not active. Please contact support for assistance.', 'error')
            return render_template('login.html')

        # --- START: Email verification check ---
        if user and user.password == password and user.status == 'active':
            # Only check email verification for non-admin users
            if user.role != 'admin' and hasattr(user, 'email_verified') and not getattr(user, 'email_verified', False):
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('verify_email', email=email))
        # --- END: Email verification check ---

        if user and user.password == password and user.status == 'active':
            session['user_id'] = user.id
            session['user_name'] = f"{user.first_name} {user.last_name}"
            session['user_role'] = user.role
            session['active_role'] = user.role  # Set initial active role

            # Update admin profile last login if admin user
            if user.role == 'admin':
                admin_profile = AdminProfile.query.filter_by(user_id=user.id).first()
                if admin_profile:
                    admin_profile.last_login = datetime.utcnow()
                    db.session.commit()
                log_admin_action('Login', f'Admin login from IP: {request.remote_addr}')

            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'seller':
                return redirect(url_for('seller_dashboard'))
            elif user.role == 'rider':
                return redirect(url_for('rider_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


# Helper: send 6-digit verification email (shared by registration/forgot-password)

def send_verification_email(email, code):
    try:
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.utils import formataddr
        
        subject = '🔐 Password Reset Code - Kids Kingdom'
        
        # HTML Email Body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; font-weight: 600; }}
                .header p {{ margin: 10px 0 0 0; font-size: 16px; opacity: 0.9; }}
                .content {{ padding: 40px 30px; background: #ffffff; }}
                .code-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: 3px solid #667eea; padding: 25px; text-align: center; font-size: 36px; font-weight: bold; letter-spacing: 8px; margin: 30px 0; border-radius: 10px; color: white; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); }}
                .warning-box {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .warning-box strong {{ color: #856404; }}
                .info-text {{ color: #666; font-size: 14px; line-height: 1.8; }}
                .footer {{ background: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e9ecef; }}
                .footer p {{ margin: 5px 0; color: #666; font-size: 13px; }}
                .footer strong {{ color: #333; }}
                .icon {{ font-size: 48px; margin-bottom: 10px; }}
                .divider {{ height: 1px; background: linear-gradient(to right, transparent, #ddd, transparent); margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="icon">🔐</div>
                    <h1>Password Reset Request</h1>
                    <p>Verification Code for Your Account</p>
                </div>
                <div class="content">
                    <p style="font-size: 16px; color: #333;">Hi there,</p>
                    <p class="info-text">We received a request to reset your password for your <strong>Kids Kingdom</strong> account. To proceed with the password reset, please use the verification code below:</p>
                    
                    <div class="code-box">{code}</div>
                    
                    <div class="warning-box">
                        <strong>⏰ Important:</strong> This code will expire in <strong>5 minutes</strong> for security reasons.
                    </div>
                    
                    <div class="divider"></div>
                    
                    <p class="info-text">If you didn't request this password reset, please ignore this email or contact our support team immediately if you have security concerns.</p>
                    
                    <p class="info-text" style="margin-top: 20px;"><strong>🔒 Security Tip:</strong> Never share this code with anyone, including Kids Kingdom staff. We will never ask for your verification code.</p>
                </div>
                <div class="footer">
                    <p style="font-size: 15px; margin-bottom: 10px;"><strong>Best regards,</strong></p>
                    <p style="font-size: 15px; color: #667eea; font-weight: 600;">Kids Kingdom Team</p>
                    <div class="divider" style="margin: 20px 40px;"></div>
                    <p> Need help? Contact us at <a href="mailto:support@kidskingdom.com" style="color: #667eea; text-decoration: none;">support@kidskingdom.com</a></p>
                    <p style="color: #999; font-size: 11px; margin-top: 15px;">This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        text_body = f"""
        Password Reset Request - Kids Kingdom
        
        Hi there,
        
        We received a request to reset your password for your Kids Kingdom account.
        
        Your verification code is: {code}
        
        ⏰ This code will expire in 5 minutes.
        
        If you didn't request this password reset, please ignore this email.
        
        For security reasons, never share this code with anyone.
        
        Best regards,
        Kids Kingdom Team
        
        ---
        Need help? Contact us at support@kidskingdom.com
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = formataddr(('Kids Kingdom', app.config['MAIL_SENDER']))
        msg['To'] = email
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
            smtp.send_message(msg)
        return True
    except Exception as e:
        app.logger.exception('send_verification_email failed for %s: %s', email, e)
        return False

# Basic disposable/inaccessible email checks
DISPOSABLE_DOMAINS = set([
    'mailinator.com','yopmail.com','guerrillamail.com','10minutemail.com','getnada.com','tempmail.com','tempmailo.com','sharklasers.com','trashmail.com','burnermail.io','throwawaymail.com'
])

def is_disposable_or_invalid_email(address:str)->bool:
    """Cheap local filter for obvious trash / unreachable domains.

    This does NOT talk to external APIs; it only checks known disposable domains
    and basic DNS. Used as a first line of defense before hitting EmailListVerify.
    """
    try:
        if not address or '@' not in address:
            return True
        local, domain = address.rsplit('@', 1)
        domain = domain.lower().strip()
        if domain in DISPOSABLE_DOMAINS:
            return True
        # Enhanced validation for Gmail addresses
        if domain == 'gmail.com':
            # Check for obviously fake Gmail usernames
            # Real Gmail usernames don't have consecutive dots, start/end with dots
            # and have reasonable length (6-30 characters)
            if len(local) < 6 or len(local) > 30:
                return True
            if '..' in local or local.startswith('.') or local.endswith('.'):
                return True
            # Check for obviously random patterns (too many consecutive consonants)
            consonant_pattern = re.compile(r'[bcdfghjklmnpqrstvwxyz]{4,}')
            if consonant_pattern.search(local.lower()):
                return True
        # Optional MX lookup if dnspython exists
        try:
            import dns.resolver  # type: ignore
            try:
                answers = dns.resolver.resolve(domain, 'MX')
                if not answers:
                    return True
            except Exception:
                return True
        except Exception:
            # Fallback: basic A record check
            try:
                import socket
                socket.gethostbyname(domain)
            except Exception:
                return True
    except Exception:
        return True
    return False


# External email verification via EmailListVerify
EMAILLISTVERIFY_API_URL = "https://apps.emaillistverify.com/api/verifyEmail"


def verify_gmail_smtp(address: str) -> tuple[bool, str]:
    """Simple SMTP verification for Gmail addresses without external API.
    
    Returns (is_valid, message)
    """
    try:
        if not address.endswith('@gmail.com'):
            return (False, 'Only Gmail addresses are supported')
        
        # Basic SMTP check - try to connect to Gmail's SMTP server
        import smtplib
        import socket
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        # Try to verify the address exists (this is a basic check)
        # Note: Gmail often doesn't reveal if addresses exist for privacy reasons
        # but we can at least verify the server is reachable
        server.mail('test@gmail.com')
        code, message = server.rcpt(address)
        server.quit()
        
        # If we get a 250 response, the address might exist
        # If we get 550, it definitely doesn't exist
        if code == 250:
            return (True, 'Gmail address appears to be valid')
        elif code == 550:
            return (False, 'This Gmail address does not exist')
        else:
            # For other codes, be conservative and allow it
            return (True, 'Gmail address format verified')
            
    except smtplib.SMTPServerDisconnected:
        return (True, 'Gmail address format verified (SMTP unavailable)')
    except smtplib.SMTPConnectError:
        return (True, 'Gmail address format verified (SMTP connection failed)')
    except socket.timeout:
        return (True, 'Gmail address format verified (SMTP timeout)')
    except Exception as e:
        return (True, f'Gmail address format verified (SMTP error: {str(e)[:50]})')


def verify_email_with_emaillistverify(address: str, return_status: bool = False):
    """Validate an email using the EmailListVerify HTTP API.

    Returns True if the email is considered deliverable/valid, False if it is
    definitely bad (invalid mailbox, syntax, etc).

    If return_status=True, returns a tuple (is_valid: bool, provider_status: str|None)
    where provider_status is the raw status string from ELV, e.g., 'ok', 'failed', 'unknown'.

    If no API key is configured or the API call fails, this returns True so we
    don't block all registrations just because the third‑party service is down.
    Configure the API key via .env as EMAILLISTVERIFY_API_KEY.
    """
    address = (address or "").strip()
    if not address or '@' not in address:
        return (False, None) if return_status else False

    api_key = os.getenv('EMAILLISTVERIFY_API_KEY') or os.getenv('EMAILLISTVERIFY_SECRET')
    if not api_key:
        # No API key configured; fail open for development, log warning
        app.logger.warning('EmailListVerify API key not configured - skipping external validation')
        return (True, 'skipped_no_key') if return_status else True

    try:
        resp = requests.get(
            EMAILLISTVERIFY_API_URL,
            params={"secret": api_key, "email": address},
            timeout=8,
        )
        if resp.status_code != 200:
            app.logger.warning(
                "EmailListVerify non-200 (%s) for %s: %s",
                resp.status_code,
                address,
                (resp.text or "")[:200],
            )
            return (False, 'unavailable_http') if return_status else False
        status = (resp.text or "").strip().lower()
        domain = address.split('@', 1)[-1].lower()
        
        # According to EmailListVerify docs, 'ok' means deliverable.
        if status == 'ok':
            return (True, status) if return_status else True
        
        # Block clearly invalid statuses
        invalid_statuses = {
            'fail', 'failed', 'invalid', 'error', 'bad', 
            'unknown_email', 'unknown_user', 'no_mailbox', 'does_not_exist',
            'invalid_mx',  # Invalid MX records (domain can't receive email)
            'disposable',  # Disposable/temporary email services
            'spamtrap'     # Known spam trap addresses
        }
        if status in invalid_statuses:
            return (False, status) if return_status else False
        
        # Be strict for gmail.com: any non-'ok' means invalid/non-existent
        if domain == 'gmail.com' and status != 'ok':
            return (False, status) if return_status else False
        
        # For other responses (e.g. 'unknown', temporary), fail open for non-gmail
        return (True, status) if return_status else True
    except Exception as e:
        app.logger.exception('EmailListVerify error for %s: %s', address, e)
        return (False, 'unavailable_error') if return_status else False

@app.route('/register-hub')
def register_hub():
    """Deprecated registration hub. Redirect users directly to buyer registration."""
    return redirect(url_for('register_buyer'))


@app.route('/register-multistep')
def register_multistep():
    """
    Modern multi-step registration form with role selection, progress tracking, and dynamic fields.
    Single-page form with smooth transitions between steps.
    """
    return render_template('register_multiStep.html')


@app.route('/register-buyer')
def register_buyer():
    """
    Buyer-specific registration route that renders the buyer registration form.
    This is the primary registration page for customers.
    """
    return render_template('register.html')


# Step 1: start registration, validate input, create OTP, do not save to DB yet
@app.route('/api/check-email', methods=['POST'])
def api_check_email():
    """AJAX endpoint to validate an email before registration step 2.

    Checks:
    - Gmail-only policy
    - Duplicate (already registered) accounts
    - Local disposable/invalid domains
    - External EmailListVerify result
    """
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip()
    if not email:
        return jsonify(ok=False, message='Email is required.')

    # Gmail-only policy
    if not email.endswith('@gmail.com'):
        return jsonify(ok=False, message='Please register using a Gmail address.')

    # Duplicate (non-rejected) account
    existing_users = get_data('user', filters={'email': email})
    if existing_users and len(existing_users) > 0:
        existing_user = existing_users[0]
        user_status = existing_user.get('status', '').lower()
        
        # Check for pending approval
        if user_status == 'pending':
            return jsonify(ok=False, message='This email is already registered and waiting for admin approval. Please wait for approval or contact support.', status='pending')
        
        # Check for other non-rejected statuses
        if user_status != 'rejected':
            return jsonify(ok=False, message='This email address is already registered. Please use a different email or try logging in.', status=user_status)

    # Local disposable / invalid
    if is_disposable_or_invalid_email(email):
        return jsonify(ok=False, message='Disposable or invalid email addresses are not allowed.')

    # External verification (EmailListVerify or fallback SMTP)
    api_key = os.getenv('EMAILLISTVERIFY_API_KEY') or os.getenv('EMAILLISTVERIFY_SECRET')
    if not api_key:
        # Use enhanced local validation + SMTP check for Gmail
        if is_disposable_or_invalid_email(email):
            return jsonify(ok=False, message='Disposable or invalid email addresses are not allowed.')
        
        # Additional SMTP verification for Gmail
        if email.endswith('@gmail.com'):
            smtp_valid, smtp_message = verify_gmail_smtp(email)
            if not smtp_valid:
                return jsonify(ok=False, message=smtp_message)
            return jsonify(ok=True, message=smtp_message, provider_status='smtp_verified')
        else:
            return jsonify(ok=True, message='Email format validated', provider_status='local_only')
    
    # Use EmailListVerify API if key is available
    valid, raw_status = verify_email_with_emaillistverify(email, return_status=True)
    if not valid:
        # Friendlier messages
        status_msg_map = {
            'invalid': 'That email address is invalid.',
            'fail': 'We can’t find that Gmail account. Use an existing Gmail address.',
            'failed': 'We can’t find that Gmail account. Use an existing Gmail address.',
            'unknown_email': 'We can’t find that Gmail account. Use an existing Gmail address.',
            'unknown_user': 'We can’t find that Gmail account. Use an existing Gmail address.',
            'no_mailbox': 'We can’t find that Gmail account. Use an existing Gmail address.',
            'does_not_exist': 'We can’t find that Gmail account. Use an existing Gmail address.',
            'error': 'We could not verify this email right now. Please try again.',
        }
        # Unavailable cases -> block with a clear message
        if (raw_status or '').lower().startswith('unavailable'):
            return jsonify(ok=False, message='Email verification is temporarily unavailable. Please try again later.', provider_status=(raw_status or 'unavailable'))
        msg = status_msg_map.get((raw_status or '').lower(), 'We couldn’t verify this email. Please use an existing Gmail address.')
        return jsonify(ok=False, message=msg, provider_status=(raw_status or 'failed'))

    # ok=True — pass through provider_status as-is so UI can decide whether to show green badge
    # For development without API key, show a friendly message
    if raw_status == 'skipped_no_key':
        return jsonify(ok=True, message='Email format validated (external verification skipped in development)', provider_status='skipped')
    return jsonify(ok=True, message='OK', provider_status=(raw_status or 'ok'))


# --- Fallback OTP pre-verification when external ELV is unavailable ---
@app.route('/api/send-email-otp', methods=['POST'])
def api_send_email_otp():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip()
    if not email or not email.endswith('@gmail.com'):
        return jsonify(ok=False, message='Enter a valid Gmail address first.')
    # Generate 6-digit code, 5-minute expiry
    code = str(random.randint(100000, 999999))
    session['email_preverify'] = {
        'email': email,
        'code': code,
        'exp': (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    }
    # Send the code
    if not send_verification_email(email, code):
        return jsonify(ok=False, message='Failed to send verification code. Try again later.')
    return jsonify(ok=True, message='Verification code sent.')


@app.route('/api/verify-email-otp', methods=['POST'])
def api_verify_email_otp():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip()
    code = (data.get('code') or '').strip()
    stash = session.get('email_preverify') or {}
    if not email or not code:
        return jsonify(ok=False, message='Email and code are required.')
    if not stash or stash.get('email') != email:
        return jsonify(ok=False, message='Please send a new code first.')
    # Check expiry
    try:
        exp = datetime.fromisoformat(stash.get('exp'))
        if datetime.utcnow() > exp:
            return jsonify(ok=False, message='Code expired. Please request a new one.')
    except Exception:
        pass
    if stash.get('code') != code:
        return jsonify(ok=False, message='Invalid code. Please try again.')
    # Mark pre-verified
    session['email_preverified'] = email
    return jsonify(ok=True, message='Email verified by code.')


@app.route('/register/start', methods=['POST'])
def register_start():
    role = (request.form.get('role') or 'buyer').strip().lower()
    if role not in ('buyer','rider'):
        role = 'buyer'

    # Extract fields per role
    if role == 'rider':
        email = (request.form.get('rider_email') or '').strip()
        password = request.form.get('rider_password') or ''
        first_name = (request.form.get('rider_first_name') or '').strip()
        last_name = (request.form.get('rider_last_name') or '').strip()
        raw_phone = (request.form.get('rider_phone') or '').strip()
        street = request.form.get('rider_street_address') or ''
        barangay = request.form.get('rider_barangay') or ''
        city = request.form.get('rider_city') or ''
        province = request.form.get('rider_province') or ''
        region = request.form.get('rider_region') or ''
        address_full = request.form.get('rider_address') or ''
        vehicle_type = (request.form.get('rider_vehicle_type') or '').strip()
        vehicle_number = (request.form.get('rider_vehicle_number') or '').strip()
        file = request.files.get('rider_valid_id')
        terms_accepted = request.form.get('rider_terms')
    else:
        email = (request.form.get('email') or '').strip()
        password = request.form.get('password') or ''
        first_name = (request.form.get('first_name') or '').strip()
        last_name = (request.form.get('last_name') or '').strip()
        raw_phone = (request.form.get('phone') or '').strip()
        street = request.form.get('street_address') or ''
        barangay = request.form.get('barangay') or ''
        city = request.form.get('city') or ''
        province = request.form.get('province') or ''
        region = request.form.get('region') or ''
        address_full = request.form.get('address') or ''
        vehicle_type = ''
        vehicle_number = ''
        file = request.files.get('valid_id')
        terms_accepted = request.form.get('terms')

    # Preserve all current validations
    if not email:
        flash('Email is required.', 'danger'); return render_template('register.html')
    if not password:
        flash('Password is required.', 'danger'); return render_template('register.html')
    if not first_name:
        flash('First name is required.', 'danger'); return render_template('register.html')
    if not last_name:
        flash('Last name is required.', 'danger'); return render_template('register.html')

    phone_digits = ''.join(ch for ch in raw_phone if ch.isdigit())
    if len(phone_digits) != 11:
        flash('Phone number must be exactly 11 digits.', 'danger'); return render_template('register.html')

    # Maintain your Gmail-only policy
    if not email.endswith('@gmail.com'):
        flash('Please register using a Gmail address.', 'danger'); return render_template('register.html')

    if not terms_accepted:
        flash('You must accept the terms and conditions to register.', 'danger'); return render_template('register.html')

    # Check duplicate email that is not rejected
    existing_user = User.query.filter_by(email=email).first()
    if existing_user and existing_user.status != 'rejected':
        flash('This email address is already registered. Please use a different email or try logging in.', 'danger')
        return render_template('register.html')

    # Local disposable / invalid email checks
    if is_disposable_or_invalid_email(email):
        flash('Disposable or invalid email addresses are not allowed.', 'danger')
        return render_template('register.html')

    # External real-time validation via EmailListVerify
    # Only runs when EMAILLISTVERIFY_API_KEY is configured in your .env.
    api_key = os.getenv('EMAILLISTVERIFY_API_KEY') or os.getenv('EMAILLISTVERIFY_SECRET')
    if api_key and not verify_email_with_emaillistverify(email):
        flash('Please enter a valid email address. We could not verify this email.', 'danger')
        return render_template('register.html')

    # Require ID for rider; leave buyer as-is if your current flow requires valid_id too
    if role == 'rider' and (not file or not file.filename):
        flash('Please upload a clear copy of your government-issued ID (JPG, PNG, PDF).', 'danger')
        return render_template('register.html')

    # Save the uploaded ID temporarily (not tied to a DB row yet)
    tmp_id_path = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
        filename = ts + filename
        tmp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        file_path = os.path.join(tmp_dir, filename)
        file.save(file_path)
        tmp_id_path = '/static/uploads/tmp/' + filename

    # Create OTP (5-minute expiry)
    code = str(random.randint(100000, 999999))
    session['reg_data'] = {
        'role': role,
        'email': email,
        'password': password,
        'first_name': first_name,
        'last_name': last_name,
        'phone': phone_digits,
        'street': street,
        'barangay': barangay,
        'city': city,
        'province': province,
        'region': region,
        'address_full': address_full,
        'vehicle_type': vehicle_type,
        'vehicle_number': vehicle_number,
        'tmp_valid_id': tmp_id_path,
    }
    session['reg_code'] = code
    session['reg_code_expires'] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()

    # Send verification email
    if not send_verification_email(email, code):
        flash('Failed to send verification code. Please try again later.', 'danger')
        return render_template('register.html')

    # Go to verify page
    return redirect(url_for('verify_email', email=email))

# Backward compatible endpoint name (HTML action changed to /register/start). Finalization happens after OTP.
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')
    if request.method == 'POST':
        # Get role first to determine which field names to use
        role = request.form.get('role', 'buyer').strip().lower() or 'buyer'
        if role not in ('buyer', 'rider'):
            role = 'buyer'
        
        # Get field values based on role
        if role == 'rider':
            email = request.form.get('rider_email', '').strip()
            password = request.form.get('rider_password', '')
            first_name = request.form.get('rider_first_name', '').strip()
            last_name = request.form.get('rider_last_name', '').strip()
            raw_phone = request.form.get('rider_phone', '').strip()
            address_full = request.form.get('rider_address', '')
            street = request.form.get('rider_street_address', '')
            barangay = request.form.get('rider_barangay', '')
            city = request.form.get('rider_city', '')
            province = request.form.get('rider_province', '')
            region = request.form.get('rider_region', '')
            vehicle_type = request.form.get('rider_vehicle_type', '').strip()
            vehicle_number = request.form.get('rider_vehicle_number', '').strip()
            valid_id_file = request.files.get('rider_valid_id')
            terms_accepted = request.form.get('rider_terms')
        else:
            # Buyer fields (original)
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            raw_phone = request.form.get('phone', '').strip()
            address_full = request.form.get('address', '')
            street = request.form.get('street_address', '') or request.form.get('street', '')
            barangay = request.form.get('barangay', '')
            city = request.form.get('city', '')
            province = request.form.get('province', '')
            region = request.form.get('region', '')
            vehicle_type = request.form.get('vehicle_type', '').strip()
            vehicle_number = request.form.get('vehicle_number', '').strip()
            valid_id_file = None
            terms_accepted = request.form.get('terms')
        
        # Validate required fields
        if not email:
            flash('Email is required.', 'danger')
            return render_template('register.html')
        if not password:
            flash('Password is required.', 'danger')
            return render_template('register.html')
        if not first_name:
            flash('First name is required.', 'danger')
            return render_template('register.html')
        if not last_name:
            flash('Last name is required.', 'danger')
            return render_template('register.html')
        
        # Phone validation
        phone_digits = ''.join(ch for ch in raw_phone if ch.isdigit())
        if len(phone_digits) != 11:
            flash('Phone number must be exactly 11 digits.', 'danger')
            return render_template('register.html')
        phone = phone_digits

        # Enforce Gmail policy if you want (your original code required gmail)
        if not email.endswith('@gmail.com'):
            flash('Please register using a Gmail address.', 'danger')
            # Always show the unified registration page
            return render_template('register.html')
        
        # Validate terms acceptance
        if not terms_accepted:
            flash('You must accept the terms and conditions to register.', 'danger')
            return render_template('register.html')

        # --- START: duplicate email handling (allow reuse if previous account was rejected) ---
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.status != 'rejected':
            # Single clear error message
            flash('This email address is already registered. Please use a different email or try logging in.', 'danger')
            return render_template('register.html')
        # If status == 'rejected', we will *reuse* that user row instead of inserting a new one
        rejected_user = existing_user if existing_user and existing_user.status == 'rejected' else None
        # --- END: duplicate email handling ---

        # Handle uploaded ID document
        valid_id_filename = None
        file = valid_id_file  # Use the role-specific file variable we already set

        # For rider applications, validate required fields
        if role == 'rider':
            if not vehicle_type:
                flash('Vehicle type is required to register as a rider.', 'danger')
                return render_template('register.html')
            if not vehicle_number:
                flash('Vehicle plate number is required to register as a rider.', 'danger')
                return render_template('register.html')
            if (not file or not file.filename):
                flash('Please upload a clear copy of your government-issued ID (JPG, PNG, PDF).', 'danger')
                return render_template('register.html')

        if file and file.filename:
            filename = secure_filename(file.filename)
            _, ext = os.path.splitext(filename)
            ext = (ext or '').lower()
            allowed_ext = {'.png', '.jpg', '.jpeg', '.pdf'}
            if ext not in allowed_ext:
                flash('Invalid ID file type. Allowed formats: JPG, PNG, PDF.', 'danger')
                return render_template('register.html')

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'documents')
            os.makedirs(upload_path, exist_ok=True)
            file.save(os.path.join(upload_path, filename))
            # store relative path (or absolute as you prefer)
            valid_id_filename = f"/static/uploads/documents/{filename}"

        # Create or update user with pending status (cannot login until admin approves)
        code = str(random.randint(100000, 999999))

        if rejected_user:
            # Reuse the existing rejected account: update its details and reset to pending
            new_user = rejected_user
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.password = password  # In production, hash this!
            new_user.phone = phone
            new_user.address = address_full or (', '.join(filter(None, [street, barangay, city, province, region])))
            new_user.role = role
            new_user.status = 'pending'
            new_user.email_verified = False
            new_user.verification_code = code
        else:
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,   # In production, hash this!
                phone=phone,
                address=address_full or (', '.join(filter(None, [street, barangay, city, province, region]))),
                email_verified=False,
                verification_code=code,
                status='pending',   # IMPORTANT: pending until admin approves
                role=role
            )

        # attach valid_id if uploaded (assumes User model now includes valid_id column)
        if valid_id_filename:
            new_user.valid_id = valid_id_filename

        # Only add to session if this is a brand new user, not a reused rejected one
        if not rejected_user:
            db.session.add(new_user)

        db.session.flush()

        # If rider signup, also create a RiderApplication record so admins can review
        if role == 'rider':
            try:
                rider_app = RiderApplication(
                    user_id=new_user.id,
                    vehicle_type=vehicle_type,
                    vehicle_number=vehicle_number,
                    status='pending'
                )
                db.session.add(rider_app)
            except Exception:
                app.logger.exception("Failed to create RiderApplication for new rider signup")

        try:
            if any([street, barangay, city, province, region, address_full]):
                addr = Address(
                    user_id=new_user.id,
                    label='Home',
                    full_address=address_full or (', '.join(filter(None, [street, barangay, city, province, region]))),
                    is_default=True,
                    region=region or None,
                    province=province or None,
                    city=str(city) or None,
                    barangay=barangay or None,
                    street=street or None,
                    latitude=request.form.get('latitude') or None,
                    longitude=request.form.get('longitude') or None
                )
                db.session.add(addr)
        except Exception:
            app.logger.exception("Failed to create address record for new user")

        db.session.commit()

        # Notify admins in-app
        try:
            account_type = 'Rider' if role == 'rider' else 'Buyer'
            notify_admins(f'New {account_type} account registration pending approval: {first_name} {last_name} ({email})')
        except Exception:
            app.logger.exception("Failed to notify admins of new registration")

        # Optionally send email to user that registration is pending
        try:
            msg = MIMEText("Thank you for registering. Your application is now under review. We will notify you via email once an administrator has reviewed your account.")
            msg['Subject'] = 'Registration Submitted - Pending Approval'
            msg['From'] = app.config['MAIL_SENDER']
            msg['To'] = email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
                smtp.send_message(msg)
        except Exception:
            app.logger.exception("Failed to send pending email to user")

        # After successful registration:
        # - Buyers go to the generic registration_status page
        # - Riders go straight to the dedicated rider account-under-review page
        if role == 'rider':
            return render_template('rider/account_under_review.html', user=new_user)
        return redirect(url_for('registration_status', role=role))

    return render_template('register.html')


@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    email = request.args.get('email') or request.form.get('email')
    # Registration-OTP path (session-based)
    if 'reg_data' in session and email == session.get('reg_data', {}).get('email'):
        if request.method == 'POST':
            code = (request.form.get('code') or '').strip()
            stored = session.get('reg_code')
            exp_iso = session.get('reg_code_expires')
            expired = False
            try:
                if exp_iso:
                    expired = datetime.utcnow() > datetime.fromisoformat(exp_iso)
            except Exception:
                expired = True
            if expired or not stored or code != stored:
                flash('Disposable email addresses are not allowed.' if is_disposable_or_invalid_email(email) else 'Invalid or expired verification code.', 'danger')
                # Do not finalize
                return render_template('verify_email.html', email=email)

            # Code matches -> finalize original registration (save to DB now)
            data = session.pop('reg_data')
            session.pop('reg_code', None)
            session.pop('reg_code_expires', None)

            role = data.get('role','buyer')
            email = data['email']
            first_name = data['first_name']; last_name = data['last_name']
            phone = data['phone']; password = data['password']
            street = data.get('street',''); barangay = data.get('barangay',''); city = data.get('city','')
            province = data.get('province',''); region = data.get('region',''); address_full = data.get('address_full','')
            vehicle_type = data.get('vehicle_type'); vehicle_number = data.get('vehicle_number')
            tmp_valid_id = data.get('tmp_valid_id')

            # Re-check duplicate (race condition)
            existing_user = User.query.filter_by(email=email).first()
            rejected_user = existing_user if existing_user and existing_user.status == 'rejected' else None

            # move tmp file to documents
            valid_id_filename = None
            if tmp_valid_id:
                try:
                    # tmp_valid_id like /static/uploads/tmp/filename
                    fn = os.path.basename(tmp_valid_id)
                    src = os.path.join(app.config['UPLOAD_FOLDER'], 'tmp', fn)
                    dst_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'documents')
                    os.makedirs(dst_dir, exist_ok=True)
                    dst = os.path.join(dst_dir, fn)
                    if os.path.exists(src):
                        os.replace(src, dst)
                        valid_id_filename = f"/static/uploads/documents/{fn}"
                except Exception:
                    app.logger.exception('Failed to move temporary ID file for %s', email)

            code2 = str(random.randint(100000, 999999))

            if rejected_user:
                new_user = rejected_user
                new_user.first_name = first_name
                new_user.last_name = last_name
                new_user.password = password
                new_user.phone = phone
                new_user.address = address_full or (', '.join(filter(None, [street, barangay, city, province, region])))
                new_user.role = role
                new_user.status = 'pending'
                new_user.email_verified = False
                new_user.verification_code = code2
            else:
                new_user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                    phone=phone,
                    address=address_full or (', '.join(filter(None, [street, barangay, city, province, region]))),
                    email_verified=False,
                    verification_code=code2,
                    status='pending',
                    role=role
                )
                db.session.add(new_user)
            if valid_id_filename:
                new_user.valid_id = valid_id_filename

            db.session.flush()

            # Optional: create rider application and address now
            if role == 'rider':
                try:
                    rider_app = RiderApplication(
                        user_id=new_user.id,
                        vehicle_type=vehicle_type,
                        vehicle_number=vehicle_number,
                        status='pending'
                    )
                    db.session.add(rider_app)
                except Exception:
                    app.logger.exception('Failed to create RiderApplication (finalize)')

            try:
                if any([street, barangay, city, province, region, address_full]):
                    addr = Address(
                        user_id=new_user.id,
                        label='Home',
                        full_address=address_full or (', '.join(filter(None, [street, barangay, city, province, region]))),
                        is_default=True,
                        region=region or None,
                        province=province or None,
                        city=str(city) or None,
                        barangay=barangay or None,
                        street=street or None,
                        latitude=request.form.get('latitude') or None,
                        longitude=request.form.get('longitude') or None
                    )
                    db.session.add(addr)
            except Exception:
                app.logger.exception('Failed to create address for finalized registration')

            db.session.commit()

            # Notify admins
            try:
                account_type = 'Rider' if role == 'rider' else 'Buyer'
                notify_admins(f'New {account_type} account registration pending approval: {first_name} {last_name} ({email})')
            except Exception:
                pass

            if role == 'rider':
                return render_template('rider/account_under_review.html', user=new_user)
            return redirect(url_for('registration_status', role=role))

        # GET: render verify page with email displayed
        return render_template('verify_email.html', email=email)

    # Legacy path: verifying an already-saved user (forgot password / older flow)
    if request.method == 'POST':
        code = request.form.get('code')
        user = User.query.filter_by(email=email).first()
        if user and user.verification_code == code:
            user.email_verified = True
            user.verification_code = None
            db.session.commit()
            flash('Email verified! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid verification code.', 'danger')
    return render_template('verify_email.html', email=email)


@app.route('/seller-register', methods=['GET', 'POST'])
def seller_register():
    # Get current user if logged in
    current_user = None
    if 'user_id' in session:
        current_user = db.session.get(User, session['user_id'])
    
    if request.method == 'POST':
        # Handle file upload
        school_id_file = None
        if 'school_id' in request.files:
            file = request.files['school_id']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'documents')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)
                file.save(os.path.join(upload_path, filename))
                school_id_file = filename

        # Validate phone and GCash numbers as exactly 11 digits (numbers only)
        raw_phone = request.form.get('phone', '').strip()
        phone_digits = ''.join(ch for ch in raw_phone if ch.isdigit())
        if len(phone_digits) != 11:
            flash('Phone number must be exactly 11 digits.', 'error')
            return render_template('seller_register.html', user=current_user)

        raw_gcash = request.form.get('gcash_number', '').strip()
        gcash_digits = ''.join(ch for ch in raw_gcash if ch.isdigit())
        if len(gcash_digits) != 11:
            flash('GCash number must be exactly 11 digits.', 'error')
            return render_template('seller_register.html', user=current_user)

        if current_user:
            # Existing user applying to be seller
            user = current_user
            # Update user info if provided
            user.first_name = request.form['first_name']
            user.last_name = request.form['last_name']
            user.phone = phone_digits
            user.address = request.form['address']
        else:
            # New user registration (fallback for non-logged users)
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            phone = phone_digits
            address = request.form['address']

            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'error')
                return render_template('seller_register.html', user=current_user)

            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password="seller_app_" + datetime.now().strftime('%Y%m%d%H%M%S'),
                phone=phone,
                address=address,
                # Register as a seller account (awaiting approval)
                role='seller',
                status='pending'
            )
            db.session.add(user)
            db.session.flush()

        # Create seller application (business address is the same as the seller's personal address)
        seller_app = SellerApplication(
            user_id=user.id,
            store_name=request.form['store_name'],
            store_description=request.form.get('store_description', ''),
            store_category=request.form['store_category'],
            business_address=user.address,
            school_id_document=school_id_file,
            gcash_number=gcash_digits
        )

        db.session.add(seller_app)
        db.session.commit()

        flash('Seller application submitted successfully! You will be notified within 1-3 business days.', 'success')
        # Notify all admins of new seller application
        try:
            notify_admins(
                f'New seller application from {user.first_name} {user.last_name} ({user.email}) - Store: {seller_app.store_name}',
                type='seller_application',
                link=url_for('admin_seller_applications')
            )
        except Exception:
            pass

        if current_user:
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('login'))
    
    return render_template('seller_register.html', user=current_user)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate reset code
            reset_code = str(random.randint(100000, 999999))
            user.verification_code = reset_code
            db.session.commit()
            try:
                send_verification_email(email, reset_code)
            except Exception as e:
                # EMAIL ERROR: Log error without printing
                flash('Failed to send reset code. Please try again.', 'danger')
                return render_template('forgot_password.html')
            flash('A reset code has been sent to your email.', 'info')
            return redirect(url_for('reset_password', email=email))
        else:
            flash('Email not found.', 'danger')
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email') or request.form.get('email')
    if request.method == 'POST':
        code = request.form['code']
        new_password = request.form['new_password']
        
        # Validate password
        is_valid, password_message = validate_password(new_password)
        if not is_valid:
            flash(password_message, 'danger')
            return render_template('reset_password.html', email=email)
        
        user = User.query.filter_by(email=email).first()
        if user and user.verification_code == code:
            user.password = new_password
            user.verification_code = None
            user.email_verified = True
            db.session.commit()
            flash('Password reset successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid code or email.', 'danger')
    return render_template('reset_password.html', email=email)


@app.route('/resend-verification-code', methods=['POST'])
def resend_verification_code():
    email = request.form['email']
    # Registration (session) path
    if 'reg_data' in session and email == session.get('reg_data',{}).get('email'):
        code = str(random.randint(100000, 999999))
        session['reg_code'] = code
        session['reg_code_expires'] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        if send_verification_email(email, code):
            flash('A new verification code has been sent to your email.', 'info')
        else:
            flash('Failed to resend verification code. Please try again.', 'danger')
        return redirect(url_for('verify_email', email=email))
    # Legacy: user exists in DB
    user = User.query.filter_by(email=email).first()
    if user:
        code = str(random.randint(100000, 999999))
        user.verification_code = code
        db.session.commit()
        if send_verification_email(email, code):
            flash('A new verification code has been sent to your email.', 'info')
        else:
            flash('Failed to resend verification code. Please try again.', 'danger')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('verify_email', email=email))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    response = make_response(redirect(url_for('index')))
    # Prevent caching of the logout redirect
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/admin')
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    from sqlalchemy import distinct
    # Explicit select() for SQLAlchemy 2.x compatibility when using IN()
    approved_app_users = db.select(SellerApplication.user_id).where(
        SellerApplication.status == 'approved'
    )
    total_sellers = db.session.query(db.func.count(distinct(User.id))).filter(
        db.or_(User.role == 'seller', User.id.in_(approved_app_users))
    ).scalar() or 0
    total_buyers = db.session.query(db.func.count(distinct(User.id))).filter(
        User.role == 'buyer',
        ~User.id.in_(approved_app_users)
    ).scalar() or 0
    total_riders = User.query.filter_by(role='rider').count()
    pending_rider_applications = RiderApplication.query.filter_by(status='pending').count()

    pending_applications = SellerApplication.query.filter_by(status='pending').count()
    pending_products = Product.query.filter(Product.status == 'pending').count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    # Admin commission based on released commissions (wallet), not raw order totals
    admins = User.query.filter_by(role='admin').all()
    admin_ids = [a.id for a in admins] or [0]
    admin_commission_total = float(
        db.session.query(db.func.coalesce(db.func.sum(WalletTransaction.amount), 0.0))
        .filter(
            WalletTransaction.user_id.in_(admin_ids),
            WalletTransaction.type == 'credit',
            WalletTransaction.source == 'order_commission'
        ).scalar() or 0.0
    )
    total_sales = admin_commission_total / 0.05 if admin_commission_total else 0.0
    commission = admin_commission_total
    total_commission = commission  # Add alias for template compatibility
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    pending_seller_apps = SellerApplication.query.filter_by(status='pending').all()
    admin_unread_notifications = Notification.query.filter_by(user_id=session['user_id'], is_read=False).count()
    recent_notifications = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.created_at.desc()).limit(10).all()
    pending_registrations_count = User.query.filter_by(status='pending', role='buyer').count()
    
    # Get badge counts for sidebar
    badge_counts = get_admin_badge_counts()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_buyers=total_buyers,
        total_sellers=total_sellers,
        total_riders=total_riders,
        total_products=total_products,
        total_orders=total_orders,
        total_sales=total_sales,
        commission=commission,
        total_commission=total_commission,
        recent_orders=recent_orders,
        pending_seller_apps=pending_seller_apps,
        moment=datetime.utcnow,
        admin_unread_notifications=admin_unread_notifications,
        recent_notifications=recent_notifications,
        **badge_counts
    )


@app.route('/api/admin/badge-counts')
@admin_required
def api_admin_badge_counts():
    """API endpoint to get current admin badge counts for real-time updates"""
    badge_counts = get_admin_badge_counts()
    return jsonify(badge_counts)


def get_admin_badge_counts():
    """
    Optimized badge counts using separate queries to avoid Cartesian product.
    Each query uses the appropriate status index for fast filtering.
    """
    from sqlalchemy import func
    
    # Separate scalar queries - each uses idx_*_status index
    pending_sellers = db.session.query(func.count(SellerApplication.id))\
        .filter(SellerApplication.status == 'pending')\
        .scalar() or 0
    
    pending_products = db.session.query(func.count(Product.id))\
        .filter(Product.status == 'pending')\
        .scalar() or 0
    
    pending_orders = db.session.query(func.count(Order.id))\
        .filter(Order.status == 'pending')\
        .scalar() or 0
    
    try:
        pending_riders = db.session.query(func.count(RiderApplication.id))\
            .filter(RiderApplication.status == 'pending')\
            .scalar() or 0
    except:
        pending_riders = 0
    
    try:
        pending_returns = db.session.query(func.count(ReturnRequest.id))\
            .filter(ReturnRequest.status.in_(['submitted', 'seller_reviewing']))\
            .scalar() or 0
    except:
        pending_returns = 0
    
    try:
        pending_restocks = db.session.query(func.count(RestockRequest.id))\
            .filter(RestockRequest.status == 'pending')\
            .scalar() or 0
    except:
        pending_restocks = 0
    
    # Pending buyer registrations (new accounts waiting for approval)
    try:
        pending_registrations = db.session.query(func.count(User.id))\
            .filter(User.status == 'pending', User.role == 'buyer')\
            .scalar() or 0
    except:
        pending_registrations = 0
    
    return {
        'pending_sellers': pending_sellers,
        'pending_products': pending_products,
        'pending_orders': pending_orders,
        'pending_riders': pending_riders,
        'pending_returns': pending_returns,
        'pending_restocks': pending_restocks,
        'pending_registrations': pending_registrations
    }


@app.route('/admin/rider-applications')
@admin_required
def admin_rider_applications():
    applications = RiderApplication.query.order_by(RiderApplication.applied_at.desc()).all()
    badge_counts = get_admin_badge_counts()
    return render_template('admin/rider_applications.html', 
                         applications=applications,
                         **badge_counts)


@app.route('/admin/seller-applications')
@admin_required
def admin_seller_applications():
    applications = SellerApplication.query.order_by(SellerApplication.applied_at.desc()).all()
    badge_counts = get_admin_badge_counts()
    return render_template('admin/seller_applications.html', 
                         applications=applications,
                         **badge_counts)


@app.route('/admin/pending-registrations')
@admin_required
def admin_pending_registrations():
    # Show only buyers with status == 'pending' (exclude riders and sellers)
    # FIXED: Changed .asc() to .desc() for latest first
    pending_users = User.query.filter_by(status='pending', role='buyer').order_by(User.created_at.desc()).all()
    badge_counts = get_admin_badge_counts()
    return render_template('admin/pending_registrations.html', 
                         pending_users=pending_users,
                         **badge_counts)

@app.route('/admin/approve-registration/<int:user_id>', methods=['POST','GET'])
@admin_required
def admin_approve_registration(user_id):
    user = User.query.get_or_404(user_id)
    if user.status != 'pending':
        flash('User is not pending.', 'info')
        return redirect(url_for('admin_pending_registrations'))

    user.status = 'active'
    user.email_verified = True  # optional: treat admin approval as verification
    db.session.commit()

    # In-app notification
    try:
        db.session.add(Notification(user_id=user.id, message='Your account registration has been approved. You can now log in.'))
        db.session.commit()
    except Exception:
        db.session.rollback()

    # Send approval email
    try:
        send_account_status_email(user.email, approved=True)
    except Exception:
        app.logger.exception("Failed to send approval email to %s", user.email)

    flash(f'User {user.first_name} {user.last_name} approved.', 'success')
    return redirect(url_for('admin_pending_registrations'))

@app.route('/admin/reject-registration/<int:user_id>', methods=['POST','GET'])
@admin_required
def admin_reject_registration(user_id):
    user = User.query.get_or_404(user_id)
    if user.status != 'pending':
        flash('User is not pending.', 'info')
        return redirect(url_for('admin_pending_registrations'))

    # Option 1: mark rejected, keep record
    user.status = 'rejected'
    db.session.commit()

    # In-app notification
    try:
        db.session.add(Notification(user_id=user.id, message='Your account registration was not approved.'))
        db.session.commit()
    except Exception:
        db.session.rollback()

    # Send rejection email (optional reason)
    reason = request.args.get('reason') or request.form.get('reason') or None
    try:
        send_account_status_email(user.email, approved=False, reason=reason)
    except Exception:
        app.logger.exception("Failed to send rejection email to %s", user.email)

    flash(f'User {user.first_name} {user.last_name} rejected.', 'info')
    return redirect(url_for('admin_pending_registrations'))



@app.route('/admin/approve-seller/<int:app_id>')
@admin_required
def approve_seller(app_id):
    application = SellerApplication.query.get_or_404(app_id)
    application.status = 'approved'
    application.reviewed_at = datetime.utcnow()
    application.reviewed_by = session['user_id']

    # Ensure the seller has a store logo, provide default if missing
    if not application.store_logo:
        application.store_logo = '/static/uploads/default-store-logo.png'

    # Promote the user to seller and activate the account if needed
    user = db.session.get(User, application.user_id)
    if user:
        user.role = 'seller'
        if user.status != 'active':
            user.status = 'active'
        try:
            db.session.add(Notification(user_id=user.id, message='Your seller application was approved. You now have seller access.'))
        except Exception:
            pass

    db.session.commit()
    
    # Notify all admins about the new brand addition
    try:
        notify_admins(
            f"New brand added: {application.store_name} is now available in the brand section",
            type='brand_added',
            link=f'/store/{application.user_id}',
            image_url=application.store_logo
        )
    except Exception:
        pass
    
    flash('Seller application approved successfully! Store added to brand section.', 'success')
    return redirect(url_for('admin_seller_applications'))


@app.route('/admin/reject-seller/<int:app_id>')
@admin_required
def reject_seller(app_id):
    application = SellerApplication.query.get_or_404(app_id)
    application.status = 'rejected'
    application.reviewed_at = datetime.utcnow()
    application.reviewed_by = session['user_id']

    # Send notification to the user
    user = db.session.get(User, application.user_id)
    if user:
        try:
            db.session.add(Notification(user_id=user.id, message='Your seller application was rejected.'))
        except Exception:
            pass

    db.session.commit()
    flash('Seller application rejected.', 'info')
    return redirect(url_for('admin_seller_applications'))


@app.route('/admin/coupons', methods=['GET', 'POST'])
@admin_required
def admin_coupons():
    """Professional coupon management and automatic generation for admins."""
    # List existing coupons
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()

    if request.method == 'POST':
        mode = request.form.get('mode', 'manual')

        # --- Manual create / update coupon ---
        if mode == 'manual':
            code = (request.form.get('code') or '').strip().upper()
            description = (request.form.get('description') or '').strip()
            discount_type = request.form.get('discount_type') or 'percent'
            try:
                discount_value = float(request.form.get('discount_value') or 0)
            except ValueError:
                flash('Discount value must be a number.', 'danger')
                return redirect(url_for('admin_coupons'))

            try:
                min_order_amount = float(request.form.get('min_order_amount') or 0)
            except ValueError:
                flash('Minimum order amount must be a number.', 'danger')
                return redirect(url_for('admin_coupons'))

            max_uses_raw = request.form.get('max_uses') or ''
            max_uses = None
            if max_uses_raw.strip():
                try:
                    max_uses = int(max_uses_raw)
                except ValueError:
                    flash('Maximum uses must be an integer.', 'danger')
                    return redirect(url_for('admin_coupons'))

            # Parse validity dates (optional)
            def _parse_date(field_name):
                val = (request.form.get(field_name) or '').strip()
                if not val:
                    return None
                try:
                    return datetime.strptime(val, '%Y-%m-%d')
                except ValueError:
                    flash(f'Invalid date for {field_name.replace("_", " ")}. Use YYYY-MM-DD.', 'danger')
                    raise

            try:
                valid_from = _parse_date('valid_from')
                valid_until = _parse_date('valid_until')
            except Exception:
                return redirect(url_for('admin_coupons'))

            if not code:
                flash('Coupon code is required.', 'danger')
                return redirect(url_for('admin_coupons'))

            # Create coupon
            existing = Coupon.query.filter(db.func.upper(Coupon.code) == code).first()
            if existing:
                flash('Coupon code already exists. Please choose another.', 'danger')
                return redirect(url_for('admin_coupons'))

            coupon = Coupon(
                code=code,
                description=description,
                discount_type=discount_type,
                discount_value=discount_value,
                min_order_amount=min_order_amount,
                max_uses=max_uses,
                valid_from=valid_from,
                valid_until=valid_until,
                is_active=True
            )
            db.session.add(coupon)
            try:
                db.session.commit()
            except IntegrityError as e:
                # Rollback first
                db.session.rollback()
                msg = ''
                try:
                    msg = str(e.orig)
                except Exception:
                    msg = str(e)
                # If sequence is out-of-sync and produced a duplicate PK, fix it and retry
                if 'coupon_pkey' in msg or 'duplicate key value violates unique constraint' in msg:
                    try:
                        seq_sql = "SELECT setval(pg_get_serial_sequence('coupon','id'), (SELECT COALESCE(MAX(id, 0),0) FROM coupon) + 1);"
                        # Use a safe SQL to set sequence to max(id)+1
                        db.session.execute("SELECT setval(pg_get_serial_sequence('coupon','id'), (SELECT COALESCE(MAX(id),0) FROM coupon) + 1);")
                        db.session.commit()
                        # retry insert
                        db.session.add(coupon)
                        db.session.commit()
                        flash(f'Coupon {coupon.code} created successfully (sequence fixed).', 'success')
                        return redirect(url_for('admin_coupons'))
                    except Exception as e2:
                        db.session.rollback()
                        flash('Error creating coupon after fixing sequence: ' + str(e2), 'danger')
                        return redirect(url_for('admin_coupons'))
                else:
                    flash('Database error creating coupon: ' + str(e), 'danger')
                    return redirect(url_for('admin_coupons'))

            flash(f'Coupon {coupon.code} created successfully.', 'success')
            return redirect(url_for('admin_coupons'))

        # --- Automatic generation based on customer segment ---
        if mode == 'auto':
            segment = request.form.get('segment') or 'all'
            discount_type = request.form.get('auto_discount_type') or 'percent'
            try:
                discount_value = float(request.form.get('auto_discount_value') or 0)
            except ValueError:
                flash('Discount value must be a number.', 'danger')
                return redirect(url_for('admin_coupons'))

            try:
                min_order_amount = float(request.form.get('auto_min_order_amount') or 0)
            except ValueError:
                flash('Minimum order amount must be a number.', 'danger')
                return redirect(url_for('admin_coupons'))

            # How long the coupon is valid from today (in days)
            try:
                valid_days = int(request.form.get('auto_valid_days') or 30)
            except ValueError:
                flash('Valid days must be an integer.', 'danger')
                return redirect(url_for('admin_coupons'))

            # Segment-specific thresholds for loyal buyers
            try:
                min_orders = int(request.form.get('min_orders') or 3)
            except ValueError:
                min_orders = 3
            try:
                min_spent = float(request.form.get('min_spent') or 1000)
            except ValueError:
                min_spent = 1000.0

            # Optional explicit code; otherwise auto-generate professional code
            manual_code = (request.form.get('auto_code') or '').strip().upper()
            if manual_code:
                code = manual_code
            else:
                prefix = {
                    'new': 'NEW',
                    'loyal': 'LOYAL',
                    'all': 'SALE'
                }.get(segment, 'SALE')
                random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                code = f"{prefix}-{random_part}"

            now = datetime.utcnow()
            valid_from = now
            valid_until = now + timedelta(days=valid_days)

            description = (request.form.get('auto_description') or '').strip()
            if not description:
                if discount_type == 'percent':
                    description = f"{discount_value:.0f}% off for selected buyers"
                else:
                    description = f"₱{discount_value:,.2f} off for selected buyers"

            # Ensure code unique
            existing = Coupon.query.filter(db.func.upper(Coupon.code) == code.upper()).first()
            if existing:
                flash('Generated coupon code already exists. Please try again.', 'danger')
                return redirect(url_for('admin_coupons'))

            coupon = Coupon(
                code=code,
                description=description,
                discount_type=discount_type,
                discount_value=discount_value,
                min_order_amount=min_order_amount,
                max_uses=None,  # unlimited by default for campaigns
                valid_from=valid_from,
                valid_until=valid_until,
                is_active=True
            )
            db.session.add(coupon)
            
            try:
                db.session.flush()  # get coupon.id
            except IntegrityError as e:
                db.session.rollback()
                flash('Error creating coupon. Please try again.', 'danger')
                return redirect(url_for('admin_coupons'))

            # Determine target buyers based on segment
            target_buyers = []
            
            try:
                if segment == 'new':
                    # Buyers with no completed orders yet
                    subquery = db.session.query(Order.buyer_id).filter(
                        Order.status.in_(['completed', 'delivered'])
                    ).distinct().subquery()
                    
                    target_buyers = User.query.filter(
                        User.role == 'buyer',
                        ~User.id.in_(subquery)
                    ).all()
                    
                elif segment == 'loyal':
                    # Buyers with either enough orders OR total spend
                    # Get buyers with enough orders
                    order_count_subquery = db.session.query(
                        Order.buyer_id,
                        db.func.count(Order.id).label('order_count'),
                        db.func.sum(Order.total_amount).label('total_spent')
                    ).filter(
                        Order.status.in_(['completed', 'delivered'])
                    ).group_by(Order.buyer_id).subquery()
                    
                    target_buyers = User.query.join(
                        order_count_subquery,
                        User.id == order_count_subquery.c.buyer_id
                    ).filter(
                        User.role == 'buyer',
                        db.or_(
                            order_count_subquery.c.order_count >= min_orders,
                            order_count_subquery.c.total_spent >= min_spent
                        )
                    ).all()
                    
                else:
                    # 'all' buyers – get all active buyers
                    target_buyers = User.query.filter_by(role='buyer').all()
                    
            except Exception as e:
                app.logger.error(f"Error querying target buyers: {e}")
                db.session.rollback()
                flash('Error determining target buyers. Coupon created but not sent.', 'warning')
                db.session.commit()
                return redirect(url_for('admin_coupons'))

            if not target_buyers:
                db.session.commit()
                flash(
                    f"Coupon {coupon.code} created successfully, but no buyers match the '{segment}' segment criteria.",
                    'warning'
                )
                return redirect(url_for('admin_coupons'))

            discount_label = None
            if discount_type == 'percent':
                discount_label = f"{discount_value:.0f}% off your next order"
            else:
                discount_label = f"₱{discount_value:,.2f} off your next order"

            # Create in-site notifications and send emails
            notified_count = 0
            email_sent_count = 0
            
            for buyer in target_buyers:
                try:
                    # Notification text kept concise but clear
                    min_order_text = ""
                    if min_order_amount > 0:
                        min_order_text = f" (min. order ₱{min_order_amount:,.2f})"
                    
                    message = (
                        f"🎉 You received a new coupon: {coupon.code}\n"
                        f"{discount_label}{min_order_text}\n"
                        f"Valid until {coupon.valid_until.strftime('%B %d, %Y')}"
                    )
                    db.session.add(Notification(user_id=buyer.id, message=message))
                    notified_count += 1
                    
                    # Try to send email
                    try:
                        send_coupon_email(buyer, coupon, discount_label)
                        email_sent_count += 1
                    except Exception as email_error:
                        # Log but do not break the campaign
                        app.logger.warning(f"Failed to send coupon email to {buyer.email}: {email_error}")
                        
                except Exception as notify_error:
                    app.logger.error(f"Failed to notify buyer {buyer.id}: {notify_error}")
                    continue

            try:
                db.session.commit()
                flash(
                    f"✅ Coupon {coupon.code} created! Notified {notified_count} buyer(s) "
                    f"({email_sent_count} emails sent).",
                    'success'
                )
            except Exception as commit_error:
                db.session.rollback()
                app.logger.error(f"Error committing coupon notifications: {commit_error}")
                flash('Coupon created but some notifications failed. Please check logs.', 'warning')
                
            return redirect(url_for('admin_coupons'))

    badge_counts = get_admin_badge_counts()
    return render_template('admin/coupons.html', coupons=coupons, **badge_counts)


@app.route('/admin/coupons/<int:coupon_id>/toggle', methods=['POST'])
@admin_required
def admin_toggle_coupon(coupon_id):
    """Enable or disable a coupon from the admin panel."""
    coupon = Coupon.query.get_or_404(coupon_id)
    coupon.is_active = not coupon.is_active
    db.session.commit()
    flash(f'Coupon {coupon.code} is now {"active" if coupon.is_active else "inactive"}.', 'success')
    return redirect(url_for('admin_coupons'))


# Helper function to log admin actions
def log_admin_action(action, details=None):
    if is_admin() and 'user_id' in session:
        log = AdminSecurityLog(
            user_id=session['user_id'],
            action=action,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            details=details
        )
        db.session.add(log)
        db.session.commit()

@app.route('/admin/profile')
@admin_required
def admin_profile():
    user = db.session.get(User, session['user_id'])
    admin_profile = AdminProfile.query.filter_by(user_id=session['user_id']).first()
    if not admin_profile:
        # Create admin profile if it doesn't exist
        admin_profile = AdminProfile(
            user_id=session['user_id'],
            full_name=f"{user.first_name} {user.last_name}",
            contact_number=user.phone,
            system_role='Administrator'
        )
        db.session.add(admin_profile)
        db.session.commit()

    # Compute avatar URL using helper function
    admin_avatar_url = get_user_avatar_url(user.id, 'admin')
    
    recent_logs = AdminSecurityLog.query.filter_by(user_id=session['user_id']).order_by(AdminSecurityLog.created_at.desc()).limit(10).all()
    badge_counts = get_admin_badge_counts()
    return render_template('admin/profile.html', 
                         user=user, 
                         admin_profile=admin_profile, 
                         recent_logs=recent_logs, 
                         admin_avatar_url=admin_avatar_url,
                         **badge_counts)

@app.route('/admin/update-profile', methods=['POST'])
@admin_required
def update_admin_profile():
    user = db.session.get(User, session['user_id'])
    admin_profile = AdminProfile.query.filter_by(user_id=session['user_id']).first()
    if not admin_profile:
        # Create admin profile record on first update if it doesn't exist yet
        admin_profile = AdminProfile(
            user_id=session['user_id'],
            full_name=f"{user.first_name} {user.last_name}",
            contact_number=user.phone,
            system_role='Administrator'
        )
        db.session.add(admin_profile)
        db.session.flush()

    form = request.form

    # Update user basic info (use get so missing fields don't crash)
    if 'first_name' in form:
        user.first_name = form.get('first_name', user.first_name)
    if 'last_name' in form:
        user.last_name = form.get('last_name', user.last_name)
    if 'email' in form:
        user.email = form.get('email', user.email)
    if 'phone' in form:
        user.phone = form.get('phone', user.phone)

    # Update admin profile core fields (also tolerant of missing keys)
    if 'full_name' in form:
        admin_profile.full_name = form.get('full_name', admin_profile.full_name)
    if 'contact_number' in form:
        admin_profile.contact_number = form.get('contact_number', admin_profile.contact_number)
    if 'system_role' in form:
        admin_profile.system_role = form.get('system_role', admin_profile.system_role)

    admin_profile.updated_at = datetime.utcnow()

    # Optional avatar upload
    file = request.files.get('avatar')
    if file and file.filename:
        try:
            from PIL import Image
            # Ensure target directory exists
            avatar_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'admin_avatars')
            os.makedirs(avatar_dir, exist_ok=True)

            # Save temporary file
            temp_path = os.path.join(avatar_dir, f"tmp_admin_{user.id}")
            file.save(temp_path)

            # Open, normalize and resize, then save as PNG
            img = Image.open(temp_path)
            img = img.convert('RGB')
            img.thumbnail((256, 256))
            final_name = f"admin_avatar_{user.id}.png"
            final_path = os.path.join(avatar_dir, final_name)
            img.save(final_path, format='PNG')
        except Exception:
            # Do not block profile updates if avatar processing fails
            pass
        finally:
            try:
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass
    
    db.session.commit()
    
    # Update session user_name to reflect changes in dropdown
    session['user_name'] = f"{user.first_name} {user.last_name}"
    
    # Update session with new avatar URL for immediate dropdown update
    avatar_rel = os.path.join('admin_avatars', f"admin_avatar_{user.id}.png")
    upload_root = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    avatar_path = os.path.join(upload_root, avatar_rel)
    if os.path.exists(avatar_path):
        avatar_path_normalized = avatar_rel.replace("\\", "/")
        session['navbar_avatar_url'] = url_for('static', filename=f'uploads/{avatar_path_normalized}')
        session['avatar_timestamp'] = int(time.time())  # Force cache refresh
    
    log_admin_action('Profile Updated', 'Admin profile information updated')
    flash('Admin profile updated successfully!', 'success')
    return redirect(url_for('admin_profile'))

@app.route('/admin/users')
@admin_required
def admin_users():
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    role = request.args.get('role', 'all')
    
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.first_name.contains(search),
                User.last_name.contains(search),
                User.email.contains(search)
            )
        )
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    if role != 'all':
        query = query.filter_by(role=role)
    
    users = query.order_by(User.created_at.desc()).all()
    
    log_admin_action('Users List Accessed')
    badge_counts = get_admin_badge_counts()
    return render_template('admin/users.html', 
                         users=users, 
                         search=search, 
                         status=status, 
                         role=role,
                         **badge_counts)


# Add this route to app.py (place it with other @admin_required admin routes)
@app.route('/admin/user/<int:user_id>')
@admin_required
def admin_view_user(user_id):
    """
    Admin-only full profile view for a specific user.
    Shows user core fields, addresses, seller applications, notifications and uploaded documents.
    """
    user = User.query.get_or_404(user_id)

    # Basic related info
    addresses = Address.query.filter_by(user_id=user.id).order_by(Address.is_default.desc(), Address.created_at.asc()).all()
    seller_apps = SellerApplication.query.filter_by(user_id=user.id).order_by(SellerApplication.applied_at.desc()).all()
    notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(50).all()

    # Helpful aggregated counts
    total_orders = Order.query.filter_by(buyer_id=user.id).count()
    total_products = Product.query.filter_by(seller_id=user.id).count()
    reviews = Review.query.filter_by(user_id=user.id).order_by(Review.created_at.desc()).limit(10).all()

    badge_counts = get_admin_badge_counts()
    return render_template('admin/user_profile.html',
                           user=user,
                           addresses=addresses,
                           seller_apps=seller_apps,
                           notifications=notifications,
                           total_orders=total_orders,
                           total_products=total_products,
                           recent_reviews=reviews,
                           **badge_counts)


@app.route('/admin/block-user/<int:user_id>')
@admin_required
def block_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'admin':  # Prevent blocking other admins
        user.status = 'suspended'
        db.session.commit()
        log_admin_action('User Blocked', f'User {user.first_name} {user.last_name} ({user.email}) blocked')
        flash(f'User {user.first_name} {user.last_name} has been blocked.', 'success')
    else:
        flash('Cannot block admin users.', 'error')
    return redirect(url_for('admin_users'))

@app.route('/admin/unblock-user/<int:user_id>')
@admin_required
def unblock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'active'
    db.session.commit()
    log_admin_action('User Unblocked', f'User {user.first_name} {user.last_name} ({user.email}) unblocked')
    flash(f'User {user.first_name} {user.last_name} has been unblocked.', 'success')
    return redirect(url_for('admin_users'))

def _delete_products_for_user(user_id: int):
    """Hard-delete all products owned by user_id, including dependent rows and media.
    If an order contains the seller's items, we remove those items, adjust the order total,
    and delete the order entirely if it becomes empty.
    """
    products = Product.query.filter_by(seller_id=user_id).all()
    pids = [p.id for p in products]
    return _delete_products_by_ids(pids, products_override=products)


def _delete_products_by_ids(product_ids: list[int], products_override=None):
    """Hard-delete specific products by ID, cleaning dependent rows and orders.
    Returns stats dict.
    """
    if not product_ids:
        return {'deleted_products': 0, 'skipped': 0, 'orders_deleted': 0, 'orders_adjusted': 0}

    if products_override is None:
        products = Product.query.filter(Product.id.in_(product_ids)).all()
    else:
        products = products_override

    if not products:
        return {'deleted_products': 0, 'skipped': 0, 'orders_deleted': 0, 'orders_adjusted': 0}

    pids = [p.id for p in products]

    # 1) Orders that contain these products
    items = OrderItem.query.filter(OrderItem.product_id.in_(pids)).all()
    affected_order_ids = set(it.order_id for it in items)
    removed_sum = {}
    for it in items:
        removed_sum[it.order_id] = removed_sum.get(it.order_id, 0.0) + float(it.price_at_time) * int(it.quantity)

    if affected_order_ids:
        # Delete order-linked artifacts for those orders if they end up empty later
        # First remove the specific items from those orders
        OrderItem.query.filter(OrderItem.order_id.in_(affected_order_ids), OrderItem.product_id.in_(pids)).delete(synchronize_session=False)

        # Adjust or delete orders now that items are removed
        orders_deleted = 0
        orders_adjusted = 0
        for oid in list(affected_order_ids):
            o = db.session.get(Order, oid)
            if not o:
                continue
            remaining = OrderItem.query.filter_by(order_id=oid).count()
            if remaining == 0:
                # Clean linked artifacts then delete order
                QRScanLog.query.filter_by(order_id=oid).delete(synchronize_session=False)
                OrderLabel.query.filter_by(order_id=oid).delete(synchronize_session=False)
                ReturnRequest.query.filter_by(order_id=oid).delete(synchronize_session=False)
                # Delete chat messages linked to this order (unified chat system)
                db.session.execute(db.text("DELETE FROM chat_message WHERE order_id = :oid"), {'oid': oid})
                WalletTransaction.query.filter_by(order_id=oid).delete(synchronize_session=False)
                db.session.delete(o)
                orders_deleted += 1
            else:
                dec = float(removed_sum.get(oid, 0.0) or 0.0)
                try:
                    o.total_amount = max(0.0, float(o.total_amount) - dec)
                except Exception:
                    pass
                orders_adjusted += 1
    else:
        orders_deleted = 0
        orders_adjusted = 0

    # 2) Product-dependent rows (scoped to these products)
    # ProductQR.query.filter(ProductQR.product_id.in_(pids)).delete(synchronize_session=False)
    Cart.query.filter(Cart.product_id.in_(pids)).delete(synchronize_session=False)
    Wishlist.query.filter(Wishlist.product_id.in_(pids)).delete(synchronize_session=False)
    # Delete chat messages linked to these products (unified chat system)
    if pids:
        db.session.execute(db.text("DELETE FROM chat_message WHERE product_id = ANY(:pids)"), {'pids': pids})
    Review.query.filter(Review.product_id.in_(pids)).delete(synchronize_session=False)

    # 3) Remove media from disk
    upload_root = os.path.join(app.root_path, app.config.get('UPLOAD_FOLDER', os.path.join('static', 'uploads')))
    def safe_rm(path):
        try:
            if path and os.path.isfile(path):
                os.remove(path)
        except Exception:
            pass

    deleted = 0
    for p in products:
        if p.image_filename:
            safe_rm(os.path.join(upload_root, p.image_filename))
        if p.video_filename:
            safe_rm(os.path.join(upload_root, p.video_filename))
        try:
            if p.gallery:
                for g in (p.gallery or []):
                    safe_rm(os.path.join(upload_root, g))
        except Exception:
            pass
        db.session.delete(p)
        deleted += 1

    return {
        'deleted_products': deleted,
        'skipped': 0,
        'orders_deleted': orders_deleted,
        'orders_adjusted': orders_adjusted,
    }


@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Delete a user account.
    - Seller: deletes all their products and cleans orders that contain them.
    - Buyer: deletes their orders and related artifacts.
    - Admin: allowed except the last remaining admin.
    """
    user = User.query.get_or_404(user_id)

    # Prevent deleting last admin
    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash('Cannot delete the last admin account.', 'danger')
            return redirect(url_for('admin_users'))

    # Role-specific cleanup
    stats = {'deleted_products': 0, 'orders_deleted': 0, 'orders_adjusted': 0}
    if user.role == 'seller':
        stats = _delete_products_for_user(user.id)
    elif user.role == 'buyer':
        # Delete all orders for this buyer
        o_deleted, o_adjusted = _delete_orders_for_buyer(user.id)
        stats['orders_deleted'] = o_deleted
        stats['orders_adjusted'] = o_adjusted

    # Clean other user-linked records
    AdminProfile.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    SellerApplication.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    Follow.query.filter(db.or_(Follow.follower_id == user.id, Follow.seller_id == user.id)).delete(synchronize_session=False)
    Notification.query.filter(db.or_(Notification.user_id == user.id, Notification.actor_user_id == user.id)).delete(synchronize_session=False)
    Cart.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    Wishlist.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    # Delete all chat messages where user is sender or receiver (unified chat system)
    db.session.execute(db.text("DELETE FROM chat_message WHERE sender_id = :uid OR receiver_id = :uid"), {'uid': user.id})
    Address.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    OAuth.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    Review.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    WalletTransaction.query.filter_by(user_id=user.id).delete(synchronize_session=False)

    # Finally remove the user
    db.session.delete(user)
    db.session.commit()

    log_admin_action('User Deleted', f'User ID {user_id} deleted; products removed: {stats.get("deleted_products", 0)}, orders deleted: {stats.get("orders_deleted", 0)}, orders adjusted: {stats.get("orders_adjusted", 0)}')
    flash('User and associated data were deleted successfully.', 'success')
    return redirect(url_for('admin_users'))


def _delete_orders_for_buyer(buyer_id: int) -> tuple[int, int]:
    """Delete all orders for a buyer and related artifacts.
    Returns (orders_deleted, orders_adjusted) — adjusted will be 0 since we delete full orders.
    """
    orders = Order.query.filter_by(buyer_id=buyer_id).all()
    deleted = 0
    for o in orders:
        oid = o.id
        # detach reviews referencing this order (from anyone)
        Review.query.filter_by(order_id=oid).update({Review.order_id: None}, synchronize_session=False)
        # linked artifacts
        QRScanLog.query.filter_by(order_id=oid).delete(synchronize_session=False)
        OrderLabel.query.filter_by(order_id=oid).delete(synchronize_session=False)
        ReturnRequest.query.filter_by(order_id=oid).delete(synchronize_session=False)
        # Delete chat messages linked to this order (unified chat system)
        db.session.execute(db.text("DELETE FROM chat_message WHERE order_id = :oid"), {'oid': oid})
        WalletTransaction.query.filter_by(order_id=oid).delete(synchronize_session=False)
        OrderItem.query.filter_by(order_id=oid).delete(synchronize_session=False)
        db.session.delete(o)
        deleted += 1
    return deleted, 0


@app.route('/seller/delete-account', methods=['POST'])
@seller_required
def seller_delete_account():
    """Allow a seller to delete their own account; also removes their products.
    Ends session after deletion.
    """
    uid = session.get('user_id')
    if not uid:
        return redirect(url_for('login'))

    stats = _delete_products_for_user(uid)

    # Remove user-linked records
    AdminProfile.query.filter_by(user_id=uid).delete(synchronize_session=False)
    SellerApplication.query.filter_by(user_id=uid).delete(synchronize_session=False)
    Follow.query.filter(db.or_(Follow.follower_id == uid, Follow.seller_id == uid)).delete(synchronize_session=False)
    Notification.query.filter(db.or_(Notification.user_id == uid, Notification.actor_user_id == uid)).delete(synchronize_session=False)
    Cart.query.filter_by(user_id=uid).delete(synchronize_session=False)
    Wishlist.query.filter_by(user_id=uid).delete(synchronize_session=False)
    
    # Legacy chat models removed - use unified ChatMessage
    try:
        ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
        if ChatMessage:
            ChatMessage.query.filter(db.or_(ChatMessage.sender_id == uid, ChatMessage.receiver_id == uid)).delete(synchronize_session=False)
    except Exception:
        pass  # ChatMessage table may not exist yet

    user = db.session.get(User, uid)
    if user:
        db.session.delete(user)
    db.session.commit()

    session.clear()
    flash('Your seller account and products were deleted.', 'success')
    return redirect(url_for('index'))


@app.route('/admin/products')
@admin_required
def admin_products():
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    category = request.args.get('category', 'all')
    seller_name = request.args.get('seller', 'all')

    query = Product.query.join(User, Product.seller_id == User.id)

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Product.name.ilike(like),
                Product.description.ilike(like),
                User.first_name.ilike(like),
                User.last_name.ilike(like)
            )
        )

    if status != 'all':
        query = query.filter(Product.status == status)

    if category != 'all':
        # Match by category name
        query = query.join(Category, Product.category_id == Category.id).filter(Category.name == category)

    if seller_name != 'all':
        query = query.filter(User.first_name == seller_name)

    products = query.order_by(Product.created_at.desc()).all()

    log_admin_action('Products List Accessed')
    badge_counts = get_admin_badge_counts()
    return render_template('admin/products.html', 
                         products=products, 
                         search=search, 
                         status=status, 
                         category=category, 
                         seller=seller_name,
                         **badge_counts)

@app.route('/admin/reject-product/<int:product_id>')
@admin_required
def reject_product(product_id):
    product = Product.query.get_or_404(product_id)
    reason = request.args.get('reason', '')
    product.status = 'rejected'
    db.session.commit()
    
    # Notify seller
    db.session.add(Notification(user_id=product.seller_id, message=f'Your product {product.name} was rejected. Reason: {reason or "No reason provided"}'))
    db.session.commit()
    log_admin_action('Product Rejected', f'Product "{product.name}" (ID: {product.id}) rejected')
    flash(f'Product "{product.name}" has been rejected.', 'warning')
    return redirect(url_for('admin_products', status='pending'))

@app.route('/admin/edit-product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    ensure_product_video_column()
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.stock = int(request.form['stock'])
        product.category_id = int(request.form['category_id'])
        # Optional image update
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                filename = datetime.utcnow().strftime('%Y%m%d_%H%M%S_') + filename
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image_filename = filename
        # Optional video update
        if 'video' in request.files:
            v = request.files['video']
            if v and v.filename:
                vext = v.filename.rsplit('.', 1)[-1].lower() if '.' in v.filename else ''
                if vext in ALLOWED_VIDEO_EXT:
                    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)
                    vname = secure_filename(v.filename)
                    vname = datetime.utcnow().strftime('%Y%m%d_%H%M%S_') + vname
                    v.save(os.path.join(app.config['UPLOAD_FOLDER'], 'videos', vname))
                    product.video_filename = 'videos/' + vname
                else:
                    flash('Unsupported video format. Allowed: MP4, WebM, Ogg.', 'danger')
        db.session.commit()
        # Notify seller
        db.session.add(Notification(user_id=product.seller_id, message=f'Admin has updated your product {product.name}.'))
        db.session.commit()
        try:
            available_stock = get_available_stock(product.id)
            socketio.emit('product_stock_update', {
                'product_id': product.id,
                'stock': available_stock,
                'available_stock': available_stock
            }, broadcast=True)
            _emit_seller_stats_update(product.seller_id)
        except Exception:
            pass
        flash('Product updated successfully.', 'success')
        return redirect(url_for('admin_products'))
    categories = Category.query.all()
    badge_counts = get_admin_badge_counts()
    return render_template('admin/edit_product.html', product=product, categories=categories, **badge_counts)

@app.route('/admin/remove-product/<int:product_id>')
@admin_required
def remove_product(product_id):
    product = Product.query.get_or_404(product_id)
    name = product.name
    # Hard-delete and clean dependencies/orders
    stats = _delete_products_by_ids([product.id])
    db.session.commit()
    log_admin_action('Product Deleted', f'Product "{name}" (ID: {product_id}) permanently deleted; orders deleted: {stats.get("orders_deleted",0)}, orders adjusted: {stats.get("orders_adjusted",0)}')
    flash(f'Product "{name}" has been permanently deleted.', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/approve-product/<int:product_id>')
@admin_required
def approve_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.status = 'approved'
    db.session.commit()
        
    log_admin_action('Product Approved', f'Product "{product.name}" (ID: {product.id}) approved')
    
    # Use Shopee-style notification for product approval
    try:
        notify_product_approved(product)
    except Exception as e:
        app.logger.error(f"Failed to send Shopee-style notification: {e}")
        # Fallback to simple notification
        try:
            db.session.add(Notification(user_id=product.seller_id, message=f'Your product {product.name} has been approved and is now live.'))
            db.session.commit()
        except Exception:
            pass
    
    flash(f'Product "{product.name}" has been approved.', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/suspend-product/<int:product_id>')
@admin_required
def suspend_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.status = 'inactive'
    db.session.commit()
    log_admin_action('Product Suspended', f'Product "{product.name}" (ID: {product.id}) suspended')
    flash(f'Product "{product.name}" has been suspended.', 'warning')
    return redirect(url_for('admin_products'))


@app.route('/admin/check-stock-alerts')
@admin_required
def check_stock_alerts():
    """Check all products for low/out of stock and send notifications to sellers"""
    try:
        # Check for low stock (<= 5)
        low_stock_products = Product.query.filter(
            Product.stock <= 5,
            Product.stock > 0,
            Product.status == 'approved'
        ).all()
        
        for product in low_stock_products:
            try:
                notify_low_stock(product)
            except Exception as e:
                app.logger.error(f"Error sending low stock notification for product {product.id}: {e}")
        
        # Check for out of stock
        out_of_stock_products = Product.query.filter(
            Product.stock == 0,
            Product.status == 'approved'
        ).all()
        
        for product in out_of_stock_products:
            try:
                notify_out_of_stock(product)
            except Exception as e:
                app.logger.error(f"Error sending out of stock notification for product {product.id}: {e}")
        
        flash(f'Stock alerts sent: {len(low_stock_products)} low stock, {len(out_of_stock_products)} out of stock.', 'success')
        return redirect(url_for('admin_products'))
    except Exception as e:
        app.logger.error(f"Error checking stock alerts: {e}")
        flash(f'Error checking stock alerts: {str(e)}', 'error')
        return redirect(url_for('admin_products'))

# Bulk action: keep only "Hot Wheels Basic Car" and remove others from buyer-facing places
@app.route('/admin/products/purge-except-hotwheels', methods=['POST'])
@admin_required
def admin_purge_except_hotwheels():
    try:
        # Find products to keep (case-insensitive exact match preferred, fallback to contains pattern)
        keep = Product.query.filter(db.func.lower(Product.name) == db.func.lower('Hot Wheels Basic Car')).all()
        if not keep:
            keep = Product.query.filter(Product.name.ilike('%hot%wheels%basic%car%')).all()
        keep_ids = [p.id for p in keep]
        if not keep_ids:
            flash('No product named "Hot Wheels Basic Car" found. No changes made.', 'warning')
            return redirect(url_for('admin_products'))

        # Soft-remove all other products
        others_q = Product.query.filter(~Product.id.in_(keep_ids))
        affected_products = others_q.count()
        others_q.update({
            Product.status: 'inactive',
            Product.stock: 0,
            Product.featured: False,
            Product.show_in_new_arrival: False
        }, synchronize_session=False)

        # Clean buyer-facing refs: carts, wishlists, hide reviews
        cart_deleted = Cart.query.filter(~Cart.product_id.in_(keep_ids)).delete(synchronize_session=False)
        wishlist_deleted = Wishlist.query.filter(~Wishlist.product_id.in_(keep_ids)).delete(synchronize_session=False)
        Review.query.filter(~Review.product_id.in_(keep_ids)).update({Review.status: 'hidden'}, synchronize_session=False)

        db.session.commit()
        log_admin_action('Bulk Purge Products', f'Kept Hot Wheels Basic Car (IDs: {keep_ids}); deactivated {affected_products} products; removed {cart_deleted} cart items and {wishlist_deleted} wishlist items.')
        flash(f'Kept only "Hot Wheels Basic Car". Deactivated {affected_products} products and cleaned {cart_deleted} cart / {wishlist_deleted} wishlist items.', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.exception('Failed bulk purge except Hot Wheels')
        flash('Failed to purge products. Please try again.', 'danger')
    return redirect(url_for('admin_products'))


@app.route('/admin/nuke-except-hotwheels', methods=['GET', 'POST'])
@admin_required
def admin_nuke_except_hotwheels():
    """
    Permanently delete ALL data except products whose name contains 'Hot Wheels' (case-insensitive).
    Also wipes ALL orders/transactions and notifications. Use with extreme caution.

    Trigger via POST (recommended) or GET with ?confirm=NUKE to allow manual triggering from the browser.
    """
    try:
        # Require explicit confirmation
        confirm = request.values.get('confirm', '').strip().upper()
        if request.method == 'GET' and confirm != 'NUKE':
            flash('Confirmation required. Append ?confirm=NUKE to proceed.', 'warning')
            return redirect(url_for('admin_products'))

        # 1) Identify products to keep (any name containing 'hot' and 'wheels' in order)
        keep = Product.query.filter(Product.name.ilike('%hot%wheels%')).all()
        if not keep:
            # Fallback: keep exact demo name if present
            keep = Product.query.filter(db.func.lower(Product.name) == db.func.lower('Hot Wheels Basic Car')).all()
        keep_ids = [p.id for p in keep]
        if not keep_ids:
            flash("No 'Hot Wheels' products found. Aborting to avoid deleting everything.", 'danger')
            return redirect(url_for('admin_products'))

        # 2) Start wiping transactional data (order-related) first to avoid FK issues
        # Return flows
        ReturnPickup.query.delete(synchronize_session=False)
        # QR logs and labels
        QRScanLog.query.delete(synchronize_session=False)
        OrderLabel.query.delete(synchronize_session=False)
        # Reviews may reference orders; null out order_id to avoid FK blocks, but keep review content for kept products
        Review.query.update({Review.order_id: None}, synchronize_session=False)
        
        # Legacy RiderChatMessage removed - use unified ChatMessage for order chats
        try:
            ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
            if ChatMessage:
                # Delete all order-related chats
                ChatMessage.query.filter(ChatMessage.order_id.isnot(None)).delete(synchronize_session=False)
        except Exception:
            pass  # ChatMessage table may not exist yet
            
        # Order items then orders
        OrderItem.query.delete(synchronize_session=False)
        ReturnRequest.query.delete(synchronize_session=False)
        WalletTransaction.query.delete(synchronize_session=False)
        Order.query.delete(synchronize_session=False)

        # 3) Clear buyer-facing state
        Cart.query.delete(synchronize_session=False)
        Wishlist.query.delete(synchronize_session=False)

        # 4) Remove notifications (all)
        Notification.query.delete(synchronize_session=False)

        # 5) Permanently delete NON-Hot Wheels products and their dependent rows/files
        remove_q = Product.query.filter(~Product.id.in_(keep_ids))
        to_remove = remove_q.all()

        # Delete dependent records for those products only
        if to_remove:
            ids = [p.id for p in to_remove]
            # Product QR codes
            # ProductQR.query.filter(ProductQR.product_id.in_(ids)).delete(synchronize_session=False)
            
            # Legacy StoreChatMessage removed - use unified ChatMessage for product chats
            try:
                ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
                if ChatMessage:
                    # Delete chats tied to these products
                    ChatMessage.query.filter(ChatMessage.product_id.in_(ids)).delete(synchronize_session=False)
            except Exception:
                pass  # ChatMessage table may not exist yet
                
            # Reviews for removed products
            Review.query.filter(Review.product_id.in_(ids)).delete(synchronize_session=False)

            # Remove media files safely
            upload_root = os.path.join(app.root_path, app.config.get('UPLOAD_FOLDER', os.path.join('static', 'uploads')))
            def safe_rm(path):
                try:
                    if path and os.path.isfile(path):
                        os.remove(path)
                except Exception:
                    pass

            for p in to_remove:
                # main image
                if p.image_filename:
                    safe_rm(os.path.join(upload_root, p.image_filename))
                # video
                if p.video_filename:
                    safe_rm(os.path.join(upload_root, p.video_filename))
                # gallery (list of filenames)
                try:
                    if p.gallery:
                        for g in (p.gallery or []):
                            safe_rm(os.path.join(upload_root, g))
                except Exception:
                    pass
                db.session.delete(p)

        # 6) Normalize kept products (activate and restock to 0 to be explicit)
        for kp in Product.query.filter(Product.id.in_(keep_ids)).all():
            kp.status = 'active'
            kp.featured = False
            kp.show_in_new_arrival = False
            kp.stock = kp.stock or 0

        db.session.commit()
        log_admin_action('NUKE EXCEPT HOT WHEELS', f"Kept products {keep_ids}; wiped orders, transactions, notifications; removed {len(to_remove)} other products.")
        flash(f"Database reset complete. Kept Hot Wheels products (IDs: {keep_ids}); removed {len(to_remove)} other products and wiped transactions/notifications.", 'success')
    except Exception:
        db.session.rollback()
        app.logger.exception('admin_nuke_except_hotwheels failed')
        flash('Purge failed. Check logs for details.', 'danger')
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    # Get filter parameters
    status = request.args.get('status', 'all')
    payment_status = request.args.get('payment_status', 'all')
    search = request.args.get('search', '')
    date_range = request.args.get('date_range', 'all')
    payment_method = request.args.get('payment_method', 'all')
    
    # Build query with joins
    query = Order.query.join(User, Order.buyer_id == User.id)
    
    # Apply filters
    if status != 'all':
        query = query.filter(Order.status == status)
    
    if payment_status != 'all':
        query = query.filter(Order.payment_status == payment_status)
    
    if payment_method != 'all':
        query = query.filter(Order.payment_method == payment_method)
    
    # Search functionality
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Order.id.like(search_term),
                User.first_name.like(search_term),
                User.last_name.like(search_term),
                User.email.like(search_term),
                User.phone.like(search_term),
                db.cast(Order.id, db.String).like(search_term)
            )
        )
    
    # Date range filtering
    if date_range != 'all':
        from datetime import datetime, timedelta, timezone
        now = datetime.utcnow()
        
        if date_range == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(Order.created_at >= start_date)
        elif date_range == '7days':
            start_date = now - timedelta(days=7)
            query = query.filter(Order.created_at >= start_date)
        elif date_range == '30days':
            start_date = now - timedelta(days=30)
            query = query.filter(Order.created_at >= start_date)
        elif date_range == '90days':
            start_date = now - timedelta(days=90)
            query = query.filter(Order.created_at >= start_date)
    
    orders = query.order_by(Order.created_at.desc()).all()
    
    log_admin_action('Orders List Accessed')
    badge_counts = get_admin_badge_counts()
    return render_template('admin/orders.html', 
                         orders=orders, 
                         status=status, 
                         payment_status=payment_status,
                         search=search,
                         date_range=date_range,
                         payment_method=payment_method,
                         **badge_counts)

@app.route('/admin/clean-order-removed-items/<int:order_id>', methods=['GET','POST'])
@admin_required
def admin_clean_order_removed_items(order_id):
    order = Order.query.get_or_404(order_id)
    # Optional confirm for GET
    if request.method == 'GET' and request.args.get('confirm') != 'CLEAN':
        flash('Confirmation required. Append ?confirm=CLEAN to proceed.', 'warning')
        return redirect(url_for('admin_orders'))

    # Identify items whose product is missing or not active
    items = list(order.items)
    to_remove_ids = []
    removed_total = 0.0
    for it in items:
        p = it.product
        if (p is None) or (getattr(p, 'status', 'inactive') != 'active'):
            to_remove_ids.append(it.id)
            try:
                removed_total += float(it.price_at_time) * int(it.quantity)
            except Exception:
                pass

    if not to_remove_ids:
        flash('No removed/inactive products found in this order.', 'info')
        return redirect(url_for('admin_orders'))

    # Delete the items
    OrderItem.query.filter(OrderItem.id.in_(to_remove_ids)).delete(synchronize_session=False)

    # Recalculate order or delete if empty
    remaining = OrderItem.query.filter_by(order_id=order.id).count()
    if remaining == 0:
        # Clean linked artifacts then delete order
        QRScanLog.query.filter_by(order_id=order.id).delete(synchronize_session=False)
        OrderLabel.query.filter_by(order_id=order.id).delete(synchronize_session=False)
        ReturnRequest.query.filter_by(order_id=order.id).delete(synchronize_session=False)
        
        # Legacy RiderChatMessage removed - use unified ChatMessage for order chats
        try:
            ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
            if ChatMessage:
                ChatMessage.query.filter_by(order_id=order.id).delete(synchronize_session=False)
        except Exception:
            pass  # ChatMessage table may not exist yet
            
        WalletTransaction.query.filter_by(order_id=order.id).delete(synchronize_session=False)
        db.session.delete(order)
        db.session.commit()
        log_admin_action('Order Deleted (clean removed items)', f'Order ID {order_id} deleted after removing unavailable products')
        flash(f'Order #{order_id} deleted because all items were unavailable.', 'warning')
        return redirect(url_for('admin_orders'))

    # Adjust total
    try:
        order.total_amount = max(0.0, float(order.total_amount) - removed_total)
    except Exception:
        pass
    db.session.commit()

    log_admin_action('Order Cleaned (removed items)', f'Removed {len(to_remove_ids)} unavailable items from Order ID {order_id}; -₱{removed_total:.2f}')
    flash(f'Removed {len(to_remove_ids)} unavailable item(s) from Order #{order_id}.', 'success')
    return redirect(url_for('admin_orders'))


@app.route('/admin/order-details/<int:order_id>')
@admin_required
def admin_order_details(order_id):
    order = Order.query.get_or_404(order_id)
    badge_counts = get_admin_badge_counts()
    return render_template('admin/order_details.html', order=order, **badge_counts)

@app.route('/admin/bulk-update-orders', methods=['POST'])
@admin_required
def bulk_update_orders():
    order_ids = request.form.getlist('order_ids')
    new_status = request.form.get('new_status')
    
    if not order_ids or not new_status:
        flash('Please select orders and a status.', 'error')
        return redirect(url_for('admin_orders'))
    
    updated_count = 0
    for order_id in order_ids:
        order = db.session.get(Order, order_id)
        if order:
            order.status = new_status
            order.updated_at = datetime.utcnow()
            updated_count += 1
    
    db.session.commit()
    log_admin_action('Bulk Order Status Update', f'Updated {updated_count} orders to {new_status}')
    flash(f'Successfully updated {updated_count} orders to {new_status}.', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/print-waybill/<int:order_id>')
@admin_required
def print_waybill(order_id):
    order = Order.query.get_or_404(order_id)
    badge_counts = get_admin_badge_counts()
    return render_template('admin/waybill.html', order=order, **badge_counts)

@app.route('/admin/bulk-print-waybills', methods=['POST'])
@admin_required
def bulk_print_waybills():
    order_ids = request.form.getlist('order_ids')
    
    if not order_ids:
        flash('Please select orders to print waybills.', 'error')
        return redirect(url_for('admin_orders'))
    
    orders = Order.query.filter(Order.id.in_(order_ids)).all()
    return render_template('admin/bulk_waybills.html', orders=orders)

@app.route('/admin/refund-order/<int:order_id>')
@admin_required
def refund_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.payment_status = 'refunded'
    order.status = 'cancelled'
    db.session.commit()
        
    log_admin_action('Order Refunded', f'Order ID: {order.id}, Amount: ${order.total_amount}')
    flash(f'Order #{order.id} has been refunded.', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/cancel-order/<int:order_id>')
@admin_required
def cancel_order_admin(order_id):
    order = Order.query.get_or_404(order_id)
    
    # ⚠️ RULE 2: RETURN STOCK ONLY IF CANCELLED BEFORE PROCESSING
    # Restore stock for each item ONLY if order was not processed yet
    original_status = order.status
    if original_status in ['pending', 'to_pay']:
        released_products = release_stock(order.id)
        app.logger.info(f'Admin cancelled Order {order.id}: released stock for {len(released_products)} product(s)')
    else:
        app.logger.info(f'Admin cancelled Order {order.id}: No stock returned (status: {original_status}, stock_deducted: {order.stock_deducted})')
    
    order.status = 'cancelled'
    if order.payment_status == 'paid':
        order.payment_status = 'refunded'
    
    db.session.commit()
        
    log_admin_action('Order Cancelled', f'Order ID: {order.id} cancelled by admin')
    
    if original_status in ['pending', 'to_pay']:
        flash(f'Order #{order.id} has been cancelled.', 'warning')
    else:
        flash(f'Order #{order.id} has been cancelled.', 'warning')
    
    return redirect(url_for('admin_orders'))

@app.route('/admin/update-order-status/<int:order_id>/<status>')
@admin_required
def update_order_status_admin(order_id, status):
    order = Order.query.get_or_404(order_id)
    
    valid_statuses = ['pending', 'processing', 'ready_for_pickup', 'to_ship', 'delivered', 'completed', 'return_requested', 'returned', 'refunded', 'cancelled']
    if status in valid_statuses:
        order.status = status
        order.updated_at = datetime.utcnow()
        db.session.commit()
        if status == 'completed':
            _release_commissions(order)
        elif status == 'refunded':
            _release_rider_earning(order)
        log_admin_action('Order Status Updated', f'Order ID: {order.id} status changed to {status}')
        flash(f'Order #{order.id} status updated to {status}.', 'success')
    
    return redirect(url_for('admin_orders'))

@app.route('/admin/payments')
@admin_required
def admin_payments():
    payment_status = request.args.get('payment_status', 'all')
    
    query = Order.query.join(User, Order.buyer_id == User.id)
    
    if payment_status != 'all':
        query = query.filter(Order.payment_status == payment_status)
    
    payments = query.order_by(Order.created_at.desc()).all()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(payment_status='paid').scalar() or 0
    pending_amount = db.session.query(db.func.sum(Order.total_amount)).filter_by(payment_status='pending').scalar() or 0
    
    log_admin_action('Payments List Accessed')
    badge_counts = get_admin_badge_counts()
    return render_template('admin/payments.html', payments=payments, payment_status=payment_status, 
                         total_revenue=total_revenue, pending_amount=pending_amount,
                         **badge_counts)

@app.route('/admin/assign-rider', methods=['POST'])
@admin_required
def admin_assign_rider():
    try:
        order_id = int(request.form.get('order_id', '0'))
        rider_user_id = int(request.form.get('rider_user_id', '0'))
    except ValueError:
        flash('Invalid parameters.', 'danger')
        return redirect(request.referrer or url_for('admin_orders'))

    order = Order.query.get_or_404(order_id)
    rider = db.session.get(User, rider_user_id)
    if not rider or rider.role != 'rider':
        flash('Selected user is not a rider.', 'danger')
        return redirect(request.referrer or url_for('admin_orders'))

    order.picked_up_by = rider_user_id
    # Transition to to_ship if order is in processing or ready_for_pickup status
    if order.status in ['processing', 'ready_for_pickup']:
        order.status = 'to_ship'
    db.session.commit()
    try:
        push_notification(rider_user_id, f'Order #{order.id} has been assigned to you.')
        push_notification(order.buyer_id, f'Rider was assigned for Order #{order.id}.')
        for sid in _order_seller_ids(order):
            push_notification(sid, f'Rider assigned for Order #{order.id}.')
    except Exception:
        pass
    flash('Rider assigned successfully.', 'success')
    return redirect(request.referrer or url_for('admin_orders'))


@app.route('/admin/mark-payment-paid/<int:payment_id>')
@admin_required
def mark_payment_paid(payment_id):
    order = Order.query.get_or_404(payment_id)
    order.payment_status = 'paid'
    order.updated_at = datetime.utcnow()
    db.session.commit()
    log_admin_action('Payment Status Updated', f'Payment ID: {payment_id} marked as paid')
    flash(f'Transaction TXN-{payment_id} has been marked as paid.', 'success')
    return redirect(url_for('admin_payments'))

@app.route('/admin/mark-payment-failed/<int:payment_id>')
@admin_required
def mark_payment_failed(payment_id):
    order = Order.query.get_or_404(payment_id)
    
    # Store original status before changing it
    original_status = order.status
    
    # ⚠️ RULE 2: RETURN STOCK ONLY IF PAYMENT FAILED BEFORE PROCESSING
    original_status = order.status
    if original_status in ['pending', 'to_pay']:
        released_products = release_stock(order.id)
        app.logger.info(f'Payment failed for Order {order.id}: released stock for {len(released_products)} product(s)')
    else:
        app.logger.info(f'Payment failed for Order {order.id}: No stock returned (status: {original_status}, stock_deducted: {order.stock_deducted})')
    
    order.payment_status = 'failed'
    order.status = 'cancelled'
    order.updated_at = datetime.utcnow()
    
    db.session.commit()
        
    log_admin_action('Payment Status Updated', f'Payment ID: {payment_id} marked as failed')
    
    if original_status in ['pending', 'to_pay']:
        flash(f'Transaction TXN-{payment_id} has been marked as failed.', 'warning')
    else:
        flash(f'Transaction TXN-{payment_id} has been marked as failed.', 'warning')
    
    return redirect(url_for('admin_payments'))

@app.route('/admin/process-refund/<int:payment_id>')
@admin_required
def process_refund_payment(payment_id):
    order = Order.query.get_or_404(payment_id)
    order.payment_status = 'refunded'
    order.status = 'cancelled'
    order.updated_at = datetime.utcnow()
    db.session.commit()
        
    log_admin_action('Payment Refunded', f'Payment ID: {payment_id} refunded')
    flash(f'Transaction TXN-{payment_id} has been refunded successfully.', 'success')
    return redirect(url_for('admin_payments'))

@app.route('/admin/download-receipt/<int:payment_id>')
@admin_required
def download_receipt(payment_id):
    order = Order.query.get_or_404(payment_id)
    log_admin_action('Receipt Downloaded', f'Receipt for Payment ID: {payment_id} downloaded')
    # Here you would generate and return a PDF receipt
    flash(f'Receipt download for TXN-{payment_id} would be implemented here.', 'info')
    return redirect(url_for('admin_payments'))


# ... (existing code)

@app.route('/admin/reports')
@admin_required
def admin_reports():
    """Admin analytics dashboard with basic date filtering.

    The same filters are also forwarded to the export endpoints so exports
    match what the admin is currently viewing.
    """
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import extract, func

    # --- Read filter parameters from query string ---
    report_type = request.args.get('report_type', 'monthly')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')

    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            start_date = None
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            end_date = None

    now = datetime.utcnow()
    # Default window based on report_type if dates not provided
    if not start_date:
        if report_type == 'daily':
            start_date = now - timedelta(days=1)
        elif report_type == 'weekly':
            start_date = now - timedelta(days=7)
        elif report_type == 'yearly':
            start_date = now - timedelta(days=365)
        else:  # monthly (default)
            start_date = now - timedelta(days=180)
    if not end_date:
        end_date = now

    # Base query for PAID orders in the selected date range
    paid_query = Order.query.filter(Order.payment_status == 'paid')
    if start_date:
        paid_query = paid_query.filter(Order.created_at >= start_date)
    if end_date:
        paid_query = paid_query.filter(Order.created_at < end_date + timedelta(days=1))

    # --- Sales Analytics ---
    total_sales = paid_query.with_entities(func.sum(Order.total_amount)).scalar() or 0
    total_orders = paid_query.count()
    total_users = User.query.filter_by(status='active').count()
    total_products = Product.query.filter_by(status='active').count()

    # Time-series sales data depending on report_type
    sales_labels = []
    sales_values = []

    # For SQLite we can safely use strftime for bucketing
    if report_type == 'daily':
        # Group by day (YYYY-MM-DD)
        rows = paid_query.with_entities(
            func.strftime('%Y-%m-%d', Order.created_at).label('bucket'),
            func.sum(Order.total_amount).label('total')
        ).group_by('bucket').order_by('bucket').all()
        sales_labels = [r.bucket for r in rows]
        sales_values = [float(r.total or 0) for r in rows]
    elif report_type == 'weekly':
        # Group by ISO week (YYYY-Www)
        rows = paid_query.with_entities(
            func.strftime('%Y-W%W', Order.created_at).label('bucket'),
            func.sum(Order.total_amount).label('total')
        ).group_by('bucket').order_by('bucket').all()
        sales_labels = [r.bucket for r in rows]
        sales_values = [float(r.total or 0) for r in rows]
    elif report_type == 'yearly':
        # Group by year (YYYY)
        rows = paid_query.with_entities(
            func.strftime('%Y', Order.created_at).label('bucket'),
            func.sum(Order.total_amount).label('total')
        ).group_by('bucket').order_by('bucket').all()
        sales_labels = [r.bucket for r in rows]
        sales_values = [float(r.total or 0) for r in rows]
    else:
        # Default: group by month (YYYY-MM)
        rows = paid_query.with_entities(
            func.strftime('%Y-%m', Order.created_at).label('bucket'),
            func.sum(Order.total_amount).label('total')
        ).group_by('bucket').order_by('bucket').all()
        sales_labels = [r.bucket for r in rows]
        sales_values = [float(r.total or 0) for r in rows]

    # Top selling products within the same range
    top_products_query = paid_query.join(OrderItem).join(Product)
    top_products = top_products_query.with_entities(
        Product.name.label('name'),
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.price_at_time * OrderItem.quantity).label('total_revenue')
    ).group_by(Product.id, Product.name).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(10).all()

    # Order statistics (also scoped to the same date range)
    order_stats_query = Order.query
    if start_date:
        order_stats_query = order_stats_query.filter(Order.created_at >= start_date)
    if end_date:
        order_stats_query = order_stats_query.filter(Order.created_at < end_date + timedelta(days=1))

    order_stats = {
        'completed': order_stats_query.filter_by(status='completed').count(),
        'pending': order_stats_query.filter_by(status='pending').count(),
        'cancelled': order_stats_query.filter_by(status='cancelled').count(),
        'refunded': order_stats_query.filter(Order.payment_status == 'refunded').count()
    }

    # User growth within the selected date range
    user_growth_query = User.query
    if start_date:
        user_growth_query = user_growth_query.filter(User.created_at >= start_date)
    if end_date:
        user_growth_query = user_growth_query.filter(User.created_at < end_date + timedelta(days=1))

    user_growth = {
        'new_buyers': user_growth_query.filter_by(role='buyer').count(),
        'new_sellers': user_growth_query.filter_by(role='seller').count()
    }

    # Revenue breakdown (5% commission example)
    commission_rate = 5.0
    platform_commission = total_sales * (commission_rate / 100)
    seller_payouts = total_sales - platform_commission
    revenue_breakdown = {
        'platform_commission': platform_commission,
        'seller_payouts': seller_payouts,
        'commission_rate': commission_rate
    }

    # Top sellers by revenue in the selected range
    top_sellers_query = paid_query.join(OrderItem).join(Product).join(User, Product.seller_id == User.id)
    top_sellers_revenue_rows = top_sellers_query.with_entities(
        (User.first_name + ' ' + User.last_name).label('name'),
        func.sum(OrderItem.price_at_time * OrderItem.quantity).label('total_revenue'),
        func.count(func.distinct(Order.id)).label('total_sales')
    ).group_by(User.id).order_by(
        func.sum(OrderItem.price_at_time * OrderItem.quantity).desc()
    ).limit(10).all()

    top_sellers_list = []
    for row in top_sellers_revenue_rows:
        top_sellers_list.append({
            'name': row.name,
            'total_revenue': row.total_revenue,
            'total_sales': row.total_sales
        })

    # Traffic stats (placeholder values for now)
    traffic_stats = {
        'total_visits': '0',
        'unique_visitors': '0',
        'active_users': '0'
    }

    log_admin_action('Reports Accessed')

    # Values for date inputs
    start_date_display = start_date.strftime('%Y-%m-%d') if start_date else ''
    end_date_display = end_date.strftime('%Y-%m-%d') if end_date else ''

    return render_template(
        'admin/reports.html',
        total_sales=total_sales,
        total_orders=total_orders,
        total_users=total_users,
        total_products=total_products,
        sales_labels=sales_labels,
        sales_values=sales_values,
        top_products=top_products,
        order_stats=order_stats,
        user_growth=user_growth,
        revenue_breakdown=revenue_breakdown,
        top_sellers_revenue=top_sellers_list,
        traffic_stats=traffic_stats,
        report_type=report_type,
        start_date=start_date_display,
        end_date=end_date_display
    )



@app.route('/admin/security-settings')
@admin_required
def admin_security_settings():
    admin_profile = AdminProfile.query.filter_by(user_id=session['user_id']).first()
    return render_template('admin/security_settings.html', admin_profile=admin_profile)

@app.route('/admin/update-security', methods=['POST'])
@admin_required
def update_admin_security():
    admin_profile = AdminProfile.query.filter_by(user_id=session['user_id']).first()
    
    admin_profile.two_factor_enabled = 'two_factor' in request.form
    admin_profile.password_reset_required = 'password_reset' in request.form
    admin_profile.updated_at = datetime.utcnow()
    
    db.session.commit()
    log_admin_action('Security Settings Updated')
    flash('Security settings updated successfully!', 'success')
    return redirect(url_for('admin_security_settings'))

@app.route('/admin/activity-logs')
@admin_required
def admin_activity_logs():
    logs = AdminSecurityLog.query.join(User).order_by(AdminSecurityLog.created_at.desc()).limit(100).all()
    return render_template('admin/activity_logs.html', logs=logs)

@app.route('/admin/notifications')
@admin_required
def admin_notifications():
    # Filter out notifications with None created_at and order by created_at
    notifications = Notification.query.filter(
        Notification.user_id == session['user_id'],
        Notification.created_at.isnot(None)
    ).order_by(Notification.created_at.desc()).all()
    
    # Mark all as read when viewed
    Notification.query.filter_by(user_id=session['user_id'], is_read=False).update({Notification.is_read: True})
    db.session.commit()
    return render_template('admin/notifications.html', notifications=notifications)

@app.route('/admin/notifications/summary')
@admin_required
def admin_notifications_summary():
    # JSON for header badge/polling
    user_id = session['user_id']
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    recent = Notification.query.filter(
        Notification.user_id == user_id,
        Notification.created_at.isnot(None)
    ).order_by(Notification.created_at.desc()).limit(5).all()
    return jsonify({
        'unread_count': unread_count,
        'recent': [
            {
                'id': n.id,
                'message': n.message,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S') if n.created_at else 'Just now'
            } for n in recent
        ]
    })
    


@app.route('/admin/add-rider', methods=['GET', 'POST'])
@admin_required
def admin_add_rider():
    if request.method == 'POST':
        # Get form fields
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        employee_id = request.form['employee_id']
        vehicle_type = request.form['vehicle_type']
        vehicle_number = request.form['vehicle_number']

        # Create User (rider)
        user = User(
            first_name=name,
            last_name="",
            email=email,
            password=password,  # hash in production
            phone=phone,
            address="",
            role="rider",
            status="active"
        )
        db.session.add(user)
        db.session.commit()
        flash('Rider account created!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/add_rider.html')


# =========================
# LEGACY CHAT ROUTES - DEPRECATED
# These routes have been replaced by unified_chat_api.py
# Use /api/chat/* and /api/v1/chat/* endpoints from unified_chat_api instead
# =========================

# @app.route('/buyer/messages')
# @login_required
# def buyer_messages():
#     """DEPRECATED: Use unified chat API instead"""
#     flash('This feature has been migrated to the new chat system.', 'info')
#     return redirect(url_for('index'))


# =========================
# Mobile Chat API Endpoints - DEPRECATED
# Use unified_chat_api.py endpoints instead
# =========================

def _chat_user_payload(user):
    if not user:
        return None
    return {
        'id': user.id,
        'name': f"{user.first_name} {user.last_name}".strip(),
        'role': user.role,
        'profile_picture': get_user_avatar_url(user.id, user.role),
    }

def _chat_message_payload(msg, sender, receiver_id):
    return {
        'id': msg.id,
        'sender_id': sender.id,
        'receiver_id': receiver_id,
        'message': msg.message,
        'created_at': msg.created_at.isoformat() if msg.created_at else None,
        'sender': _chat_user_payload(sender),
        'is_read': bool(msg.is_read),
    }

# Legacy chat routes removed - now using unified chat system from unified_chat_api.py
# All chat functionality is handled by /api/chat/* and /api/v1/chat/* endpoints
# See unified_chat_api.py for implementation

# Remove a hero slide
@app.route('/admin/remove-hero-slide/<int:slide_id>', methods=['POST'])
@admin_required
def remove_hero_slide(slide_id):
    slide = HeroSlide.query.get_or_404(slide_id)
    # Optionally remove the image file from disk:
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], slide.image_filename))
    except Exception:
        pass
    db.session.delete(slide)
    db.session.commit()
    flash('Slide removed!', 'info')
    return redirect(url_for('admin_hero_slides'))

# Update slideshow settings (duration & transition)
@app.route('/admin/update-slide-settings', methods=['POST'])
@admin_required
def update_slide_settings():
    slide_duration = request.form.get('slide_duration', 6)
    transition_duration = request.form.get('transition_duration', 0.8)
    # Save these settings - see next section for DB solution
    # Example: Save to ThemeSetting (add columns) or a separate table
    theme = ThemeSetting.query.first()
    theme.slide_duration = float(slide_duration)
    theme.transition_duration = float(transition_duration)
    db.session.commit()
    flash("Slideshow settings updated!", "success")
    return redirect(url_for('admin_hero_slides'))


@app.route('/remove-logo', methods=['POST'])
def remove_logo():
    # Only allow admin!
    if session.get('user_role') != 'admin':
        abort(403)
    # Remove the logo from ThemeSetting
    theme = ThemeSetting.query.first()
    if theme and theme.logo_filename:
        theme.logo_filename = None
        db.session.commit()
    flash('Logo removed.')
    return redirect(url_for('theme_settings'))

@app.route('/notifications/summary')
@login_required
def notifications_summary():
    """Return counts used by global badges (notifications, messages, role-specific)."""
    user_id = session['user_id']
    user = db.session.get(User, user_id)
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    recent = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(5).all()

    # Chat unread count using unified ChatMessage
    unread_chat = 0
    try:
        ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
        if ChatMessage:
            # Count all unread messages where user is receiver
            unread_chat = ChatMessage.query.filter_by(receiver_id=user_id, is_read=False).count()
    except Exception:
        unread_chat = 0

    # Seller-specific order badge
    seller_unread_orders = 0
    try:
        if user.role == 'seller' or session.get('active_role') == 'seller':
            seller_unread_orders = Notification.query.filter_by(user_id=user_id, is_read=False, type='order').count()
    except Exception:
        seller_unread_orders = 0

    # Admin pending counts
    admin_pending = None
    try:
        if user.role == 'admin':
            admin_pending = {
                'seller_applications': SellerApplication.query.filter_by(status='pending').count(),
                'rider_applications': RiderApplication.query.filter_by(status='pending').count(),
                'registrations': User.query.filter_by(status='pending').count(),
            }
    except Exception:
        admin_pending = None

    return jsonify({
        'unread_count': unread_count,
        'recent': [
            {
                'id': n.id,
                'message': n.message,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'image_url': getattr(n, 'image_url', None),
                'link': getattr(n, 'link', None),
                'type': getattr(n, 'type', None)
            } for n in recent
        ],
        'unread_chat_count': unread_chat,
        'seller_unread_orders_count': seller_unread_orders,
        'admin_pending': admin_pending
    })

# Mark all current user's notifications as read (used by rider dashboard UI as well)
@app.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def notifications_mark_all_read():
    try:
        Notification.query.filter_by(user_id=session['user_id'], is_read=False).update({Notification.is_read: True})
        db.session.commit()
        return jsonify({'success': True})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False}), 500

@app.route('/notifications/mark-read/<int:notification_id>', methods=['POST','GET'])
@login_required
def notifications_mark_read(notification_id):
    try:
        n = Notification.query.filter_by(id=notification_id, user_id=session['user_id']).first()
        if not n:
            return jsonify({'success': False, 'error': 'Not found'}), 404
        n.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False}), 500
@app.route('/test-notification')
@login_required
def test_notification():
    """Test route to create a notification for testing with live emit"""
    try:
        push_notification(session['user_id'], 'Test notification - Live badge should appear!')
    finally:
        flash('Test notification created!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/export-report')
@admin_required
def admin_export_report():
    """Entry point used by the Reports page export buttons.

    Supports URLs like /admin/export-report?format=csv&detailed=true and
    forwards to the existing helpers that generate CSV/Excel/PDF.
    """
    fmt = request.args.get('format', 'csv')
    detailed = str(request.args.get('detailed', 'false')).lower() == 'true'

    if detailed:
        return export_detailed_report(fmt)
    return export_report(fmt)


@app.route('/admin/export-report/<format>')
@admin_required
def export_report(format):
    from flask import make_response
    import csv
    import io
    from datetime import datetime as dt
    from sqlalchemy import extract, func
    
    log_admin_action('Report Exported', f'Report exported in {format} format')
    
    # Gather comprehensive report data
    total_sales = db.session.query(db.func.sum(Order.total_amount)).filter_by(payment_status='paid').scalar() or 0
    total_orders = Order.query.count()
    total_users = User.query.count()
    total_products = Product.query.count()
    
    # Order status breakdown
    order_stats = {
        'completed': Order.query.filter_by(status='completed').count(),
        'pending': Order.query.filter_by(status='pending').count(),
        'processing': Order.query.filter_by(status='processing').count(),
        'shipped': Order.query.filter_by(status='shipped').count(),
        'delivered': Order.query.filter_by(status='delivered').count(),
        'cancelled': Order.query.filter_by(status='cancelled').count()
    }
    
    # Payment status breakdown
    payment_stats = {
        'paid': Order.query.filter_by(payment_status='paid').count(),
        'pending': Order.query.filter_by(payment_status='pending').count(),
        'failed': Order.query.filter_by(payment_status='failed').count(),
        'refunded': Order.query.filter_by(payment_status='refunded').count()
    }
    
    # Top selling products
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.price_at_time * OrderItem.quantity).label('revenue')
    ).join(OrderItem).join(Order).filter(
        Order.payment_status == 'paid'
    ).group_by(Product.id, Product.name).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(10).all()
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(50).all()
    
    if format == 'csv':
        # Generate comprehensive CSV report
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Kids & Baby Store - Comprehensive Admin Report'])
        writer.writerow(['Generated on:', dt.now().strftime('%B %d, %Y at %I:%M %p')])
        writer.writerow([])
        
        # Summary Statistics
        writer.writerow(['SUMMARY STATISTICS'])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Sales (Paid Orders)', f'₱{total_sales:,.2f}'])
        writer.writerow(['Total Orders', total_orders])
        writer.writerow(['Total Users', total_users])
        writer.writerow(['Total Products', total_products])
        writer.writerow(['Average Order Value', f'₱{(total_sales / total_orders if total_orders > 0 else 0):,.2f}'])
        writer.writerow([])
        
        # Order Status Breakdown
        writer.writerow(['ORDER STATUS BREAKDOWN'])
        writer.writerow(['Status', 'Count', 'Percentage'])
        for status, count in order_stats.items():
            percentage = (count / total_orders * 100) if total_orders > 0 else 0
            writer.writerow([status.title(), count, f'{percentage:.1f}%'])
        writer.writerow([])
        
        # Payment Status Breakdown
        writer.writerow(['PAYMENT STATUS BREAKDOWN'])
        writer.writerow(['Status', 'Count', 'Percentage'])
        for status, count in payment_stats.items():
            percentage = (count / total_orders * 100) if total_orders > 0 else 0
            writer.writerow([status.title(), count, f'{percentage:.1f}%'])
        writer.writerow([])
        
        # Top Selling Products
        writer.writerow(['TOP 10 SELLING PRODUCTS'])
        writer.writerow(['Rank', 'Product Name', 'Quantity Sold', 'Revenue'])
        for idx, (name, qty, revenue) in enumerate(top_products, 1):
            writer.writerow([idx, name, int(qty), f'₱{revenue:,.2f}'])
        writer.writerow([])
        
        # Recent Orders
        writer.writerow(['RECENT ORDERS (Last 50)'])
        writer.writerow(['Order ID', 'Date', 'Customer', 'Total Amount', 'Payment Status', 'Order Status'])
        for order in recent_orders:
            writer.writerow([
                order.id,
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                f"{order.buyer.first_name} {order.buyer.last_name}",
                f'₱{order.total_amount:,.2f}',
                order.payment_status.title(),
                order.status.title()
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=admin_report_{dt.now().strftime("%Y%m%d_%H%M%S")}.csv'
        return response
        
    elif format == 'excel':
        try:
            import pandas as pd
            from io import BytesIO
            
            # Create Excel file with multiple comprehensive sheets
            output = BytesIO()
            
            # Summary Sheet
            summary_data = pd.DataFrame({
                'Metric': [
                    'Total Sales (Paid Orders)',
                    'Total Orders',
                    'Total Users',
                    'Total Products',
                    'Average Order Value'
                ],
                'Value': [
                    f'₱{total_sales:,.2f}',
                    total_orders,
                    total_users,
                    total_products,
                    f'₱{(total_sales / total_orders if total_orders > 0 else 0):,.2f}'
                ]
            })
            
            # Order Status Sheet
            order_status_df = pd.DataFrame([
                {'Status': status.title(), 'Count': count, 'Percentage': f'{(count / total_orders * 100 if total_orders > 0 else 0):.1f}%'}
                for status, count in order_stats.items()
            ])
            
            # Payment Status Sheet
            payment_status_df = pd.DataFrame([
                {'Status': status.title(), 'Count': count, 'Percentage': f'{(count / total_orders * 100 if total_orders > 0 else 0):.1f}%'}
                for status, count in payment_stats.items()
            ])
            
            # Top Products Sheet
            top_products_df = pd.DataFrame([
                {
                    'Rank': idx,
                    'Product Name': name,
                    'Quantity Sold': int(qty),
                    'Revenue': f'₱{revenue:,.2f}'
                }
                for idx, (name, qty, revenue) in enumerate(top_products, 1)
            ])
            
            # Recent Orders Sheet
            recent_orders_df = pd.DataFrame([
                {
                    'Order ID': order.id,
                    'Date': order.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Customer': f"{order.buyer.first_name} {order.buyer.last_name}",
                    'Total Amount': f'₱{order.total_amount:,.2f}',
                    'Payment Status': order.payment_status.title(),
                    'Order Status': order.status.title()
                }
                for order in recent_orders
            ])
            
            # Write to Excel with formatting
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Write sheets
                summary_data.to_excel(writer, sheet_name='Summary', index=False)
                order_status_df.to_excel(writer, sheet_name='Order Status', index=False)
                payment_status_df.to_excel(writer, sheet_name='Payment Status', index=False)
                top_products_df.to_excel(writer, sheet_name='Top Products', index=False)
                recent_orders_df.to_excel(writer, sheet_name='Recent Orders', index=False)
                
                # Auto-adjust column widths
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename=admin_report_{dt.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            return response
            
        except ImportError:
            flash('Excel export requires pandas and openpyxl packages to be installed.', 'error')
            return redirect(url_for('admin_reports'))
        
    elif format == 'pdf':
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import inch
            from reportlab.platypus import Table, TableStyle
            from reportlab.lib import colors
            
            # Create PDF
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            margin = 50
            
            # Title
            p.setFont("Helvetica-Bold", 18)
            p.drawString(margin, height - 50, "Kids & Baby Store")
            p.setFont("Helvetica", 14)
            p.drawString(margin, height - 70, "Comprehensive Admin Report")
            
            # Date
            p.setFont("Helvetica", 10)
            p.drawString(margin, height - 90, f"Generated: {dt.now().strftime('%B %d, %Y at %I:%M %p')}")
            
            # Draw line
            p.line(margin, height - 100, width - margin, height - 100)
            
            y_position = height - 130
            
            # Summary Statistics
            p.setFont("Helvetica-Bold", 14)
            p.drawString(margin, y_position, "Summary Statistics")
            y_position -= 25
            
            p.setFont("Helvetica", 11)
            summary_items = [
                ("Total Sales (Paid Orders):", f"₱{total_sales:,.2f}"),
                ("Total Orders:", str(total_orders)),
                ("Total Users:", str(total_users)),
                ("Total Products:", str(total_products)),
                ("Average Order Value:", f"₱{(total_sales / total_orders if total_orders > 0 else 0):,.2f}")
            ]
            
            for label, value in summary_items:
                p.drawString(margin + 20, y_position, label)
                p.drawString(margin + 250, y_position, value)
                y_position -= 20
            
            y_position -= 10
            
            # Order Status Breakdown
            if y_position < 200:
                p.showPage()
                y_position = height - 50
            
            p.setFont("Helvetica-Bold", 14)
            p.drawString(margin, y_position, "Order Status Breakdown")
            y_position -= 25
            
            p.setFont("Helvetica", 11)
            for status, count in order_stats.items():
                percentage = (count / total_orders * 100) if total_orders > 0 else 0
                p.drawString(margin + 20, y_position, f"{status.title()}:")
                p.drawString(margin + 250, y_position, f"{count} ({percentage:.1f}%)")
                y_position -= 20
            
            y_position -= 10
            
            # Payment Status Breakdown
            if y_position < 200:
                p.showPage()
                y_position = height - 50
            
            p.setFont("Helvetica-Bold", 14)
            p.drawString(margin, y_position, "Payment Status Breakdown")
            y_position -= 25
            
            p.setFont("Helvetica", 11)
            for status, count in payment_stats.items():
                percentage = (count / total_orders * 100) if total_orders > 0 else 0
                p.drawString(margin + 20, y_position, f"{status.title()}:")
                p.drawString(margin + 250, y_position, f"{count} ({percentage:.1f}%)")
                y_position -= 20
            
            y_position -= 10
            
            # Top Selling Products
            if y_position < 300:
                p.showPage()
                y_position = height - 50
            
            p.setFont("Helvetica-Bold", 14)
            p.drawString(margin, y_position, "Top 10 Selling Products")
            y_position -= 25
            
            p.setFont("Helvetica", 10)
            p.drawString(margin + 20, y_position, "Rank")
            p.drawString(margin + 60, y_position, "Product Name")
            p.drawString(margin + 300, y_position, "Qty Sold")
            p.drawString(margin + 380, y_position, "Revenue")
            y_position -= 3
            p.line(margin, y_position, width - margin, y_position)
            y_position -= 15
            
            for idx, (name, qty, revenue) in enumerate(top_products, 1):
                if y_position < 50:
                    p.showPage()
                    y_position = height - 50
                    p.setFont("Helvetica", 10)
                
                product_name = name[:40] + '...' if len(name) > 40 else name
                p.drawString(margin + 20, y_position, str(idx))
                p.drawString(margin + 60, y_position, product_name)
                p.drawString(margin + 300, y_position, str(int(qty)))
                p.drawString(margin + 380, y_position, f"₱{revenue:,.2f}")
                y_position -= 18
            
            # Footer
            p.setFont("Helvetica-Italic", 8)
            p.drawString(margin, 30, "Kids & Baby Store - Admin Dashboard")
            p.drawString(width - margin - 100, 30, f"Page 1")
            
            p.showPage()
            p.save()
            
            buffer.seek(0)
            response = make_response(buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=admin_report_{dt.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            return response
            
        except ImportError as e:
            flash(f'PDF export requires reportlab package: {str(e)}', 'error')
            return redirect(url_for('admin_reports'))
    else:
        flash('Invalid export format.', 'error')
        return redirect(url_for('admin_reports'))

@app.route('/admin/add-featured-product', methods=['GET', 'POST'])
@admin_required
def admin_add_featured_product():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        category_id = int(request.form['category_id'])
        short_description = request.form['short_description']
        description = request.form['description']
        price = float(request.form['price'])
        sale_price = request.form.get('sale_price')
        stock = int(request.form['stock'])
        sku = request.form.get('sku', '')
        tags = request.form.get('tags', '')
        weight = request.form.get('weight')
        dimensions = request.form.get('dimensions', '')
        brand = request.form.get('brand', '')
        featured = 'featured' in request.form
        status = request.form['status']
        action = request.form.get('action', 'save')
        
        # Handle sale price
        if sale_price and float(sale_price) > 0:
            sale_price = float(sale_price)
        else:
            sale_price = None
            
        # Handle weight
        if weight and weight.isdigit():
            weight = int(weight)
        else:
            weight = None
            
        # Generate SKU if empty
        if not sku:
            import random
            sku_base = name.upper().replace(' ', '-')[:10]
            sku = f"{sku_base}-{random.randint(100, 999)}"
            
        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                filename = timestamp + filename
                
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        # Set status based on action
        if action == 'draft':
            status = 'draft'
        
        # Create new product with admin as seller
        new_product = Product(
            name=name,
            description=f"{short_description}\n\n{description}",
            price=price,
            stock=stock,
            image_filename=image_filename,
            category_id=category_id,
            seller_id=session['user_id'],  # Admin is the seller
            status=status,
            featured=featured
        )
        
        db.session.add(new_product)
        db.session.flush()  # Get product ID
        
        # Store additional product details (extend Product model or use separate table)
        # For now, we'll add them to a JSON field or description
        additional_details = {
            'sku': sku,
            'tags': tags,
            'weight': weight,
            'dimensions': dimensions,
            'brand': brand,
            'short_description': short_description,
            'sale_price': sale_price
        }
        
        # Store additional details in description for now (you could extend the model)
        full_description = f"{short_description}\n\n{description}"
        if sku:
            full_description += f"\n\nSKU: {sku}"
        if brand:
            full_description += f"\nBrand: {brand}"
        if weight:
            full_description += f"\nWeight: {weight}g"
        if dimensions:
            full_description += f"\nDimensions: {dimensions}"
        if tags:
            full_description += f"\nTags: {tags}"
        if sale_price:
            full_description += f"\nSale Price: â‚±{sale_price:.2f}"
            
        new_product.description = full_description
        
        db.session.commit()
        
        log_admin_action('Featured Product Created', f'Product "{name}" created with ID: {new_product.id}')
        
        if action == 'draft':
            flash(f'Product "{name}" saved as draft successfully!', 'info')
        else:
            flash(f'Featured product "{name}" created successfully!', 'success')
        
        return redirect(url_for('admin_dashboard'))
    
    # GET request - show form
    categories = Category.query.all()
    return render_template('admin/add_featured_product.html', categories=categories)

@app.route('/admin/export-detailed-report/<format>')
@admin_required
def export_detailed_report(format):
    from flask import make_response
    import csv
    import io
    from datetime import datetime as dt
    
    log_admin_action('Detailed Report Exported', f'Detailed report exported in {format} format')
    
    if format == 'csv':
        # Generate detailed CSV report with all data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Kids & Baby Store - Detailed Admin Report'])
        writer.writerow(['Generated on:', dt.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # All Orders
        writer.writerow(['All Orders'])
        writer.writerow(['Order ID', 'Buyer Name', 'Total Amount', 'Status', 'Payment Status', 'Date'])
        orders = Order.query.all()
        for order in orders:
            writer.writerow([
                f'#{order.id}',
                f'{order.buyer.first_name} {order.buyer.last_name}',
                f'â‚±{order.total_amount:.2f}',
                order.status,
                order.payment_status,
                order.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        writer.writerow([])
        
        # All Products
        writer.writerow(['All Products'])
        writer.writerow(['Product ID', 'Name', 'Price', 'Stock', 'Seller', 'Status'])
        products = Product.query.all()
        for product in products:
            writer.writerow([
                f'#{product.id}',
                product.name,
                f'â‚±{product.price:.2f}',
                product.stock,
                f'{product.seller.first_name} {product.seller.last_name}',
                product.status
            ])
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=detailed_admin_report_{dt.now().strftime("%Y%m%d_%H%M%S")}.csv'
        return response
        
    else:
        # For Excel and PDF, use same logic as above but with more detailed data
        return export_report(format)  # Fallback to regular export for now

@app.route('/admin/change-password', methods=['POST'])
@admin_required
def change_admin_password():
    user = db.session.get(User, session['user_id'])
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    if user.password != current_password:
        flash('Current password is incorrect.', 'error')
    elif new_password != confirm_password:
        flash('New passwords do not match.', 'error')
    else:
        # Validate new password strength
        is_valid, password_message = validate_password(new_password)
        if not is_valid:
            flash(password_message, 'error')
        else:
            user.password = new_password
            admin_profile = AdminProfile.query.filter_by(user_id=session['user_id']).first()
            if admin_profile:
                admin_profile.password_reset_required = False
                admin_profile.updated_at = datetime.utcnow()
            db.session.commit()
            log_admin_action('Password Changed', 'Admin password changed successfully')
            flash('Password changed successfully!', 'success')
    
    return redirect(url_for('admin_profile'))

@app.route('/seller')
@seller_required
def seller_dashboard():
    seller_id = session['user_id']
    products = Product.query.filter_by(seller_id=seller_id).order_by(Product.created_at.desc()).all()

    # Seller stats (delivered revenue + commissioned sales)
    stats = _compute_seller_stats(seller_id)
    total_products = len(products)
    total_orders = stats['total_orders']
    # Show delivered+completed revenue as Total Sales (real-time), and provide commissioned separately if needed
    total_sales = stats['delivered_revenue']

    # Quick 30-day summary for dashboard (orders, items, AOV, product performance, recent tx)
    from datetime import datetime, timedelta, timezone
    now = datetime.utcnow()
    start_date = now - timedelta(days=30)
    # Base query: seller's order items in range
    q = db.session.query(OrderItem, Order, Product).join(Order).join(Product).filter(
        Product.seller_id == seller_id,
        Order.created_at >= start_date
    ).order_by(Order.created_at.desc())
    sales_rows = q.all()

    # Totals
    order_ids = []
    items_sold = 0
    paid_revenue = 0.0
    for item, order, _ in sales_rows:
        order_ids.append(order.id)
        items_sold += int(item.quantity)
        if order.payment_status == 'paid':
            paid_revenue += float(item.price_at_time) * int(item.quantity)
    unique_orders = len(set(order_ids))
    aov = (paid_revenue / unique_orders) if unique_orders else 0.0

    # Product performance top 5
    product_perf_map = {}
    for item, order, product in sales_rows:
        perf = product_perf_map.setdefault(product.id, {
            'product_id': product.id,
            'product_name': product.name,
            'product_image': product.image_filename,
            'quantity_sold': 0,
            'revenue': 0.0,
            'order_count': set(),
        })
        perf['quantity_sold'] += int(item.quantity)
        if order.payment_status == 'paid':
            perf['revenue'] += float(item.price_at_time) * int(item.quantity)
        perf['order_count'].add(order.id)
    product_performance = [
        {
            **v,
            'order_count': len(v['order_count']),
            'avg_price': (v['revenue'] / v['quantity_sold']) if v['quantity_sold'] else 0.0,
        }
        for v in product_perf_map.values()
    ]
    product_performance.sort(key=lambda x: x['revenue'], reverse=True)
    product_performance = product_performance[:5]

    # Recent transactions (last 5)
    recent_transactions = [
        {
            'order_id': order.id,
            'order_date': order.created_at,
            'product_name': product.name,
            'product_id': product.id,
            'quantity': item.quantity,
            'unit_price': float(item.price_at_time),
            'total': float(item.price_at_time) * int(item.quantity),
            'buyer_name': f"{order.buyer.first_name} {order.buyer.last_name}",
            'order_status': order.status,
            'payment_status': order.payment_status,
        }
        for item, order, product in sales_rows[:5]
    ]

    # Unread chat count for sidebar badge (product chats)
    from sqlalchemy import text
    unread_chat_count = db.session.execute(text("""
        SELECT COUNT(*) FROM chat_message 
        WHERE receiver_id = :seller_id 
        AND is_read = FALSE 
        AND product_id IS NOT NULL
    """), {'seller_id': seller_id}).scalar() or 0

    return render_template('seller/dashboard.html',
                           products=products,
                           total_products=total_products,
                           total_orders=total_orders,
                           total_sales=total_sales,
                           status_counts=stats['status_counts'],
                           commissioned_sales=stats['commissioned_sales'],
                           unread_chat_count=unread_chat_count,
                           dash_unique_orders=unique_orders,
                           dash_items_sold=items_sold,
                           dash_aov=aov,
                           dash_product_performance=product_performance,
                           dash_recent_transactions=recent_transactions)


# ... (other imports and code above unchanged)

@app.route('/seller/add-product', methods=['GET', 'POST'])
@seller_required
def add_product():
    # Ensure schema supports video uploads
    ensure_product_video_column()
    # Compute the next auto-increment Product ID (preview only)
    next_product_id = (db.session.query(db.func.max(Product.id)).scalar() or 0) + 1

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        category_id = int(request.form['category_id'])
        # Optional subcategory (keep existing behavior if not provided)
        subcategory_id = request.form.get('subcategory_id')
        if subcategory_id and subcategory_id.isdigit():
            subcategory_id = int(subcategory_id)
        else:
            subcategory_id = None

        image_filename = None
        gallery_list = []
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                filename = datetime.utcnow().strftime('%Y%m%d_%H%M%S_') + filename
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        # Optional additional images (image2..image5)
        for fld in ('image2','image3','image4','image5'):
            f = request.files.get(fld)
            if f and f.filename:
                fname = secure_filename(f.filename)
                fname = datetime.utcnow().strftime('%Y%m%d_%H%M%S_') + fname
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                gallery_list.append(fname)

        # Optional product video
        video_filename = None
        if 'video' in request.files:
            v = request.files['video']
            if v and v.filename:
                vext = v.filename.rsplit('.', 1)[-1].lower() if '.' in v.filename else ''
                if vext in ALLOWED_VIDEO_EXT:
                    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)
                    vname = secure_filename(v.filename)
                    vname = datetime.utcnow().strftime('%Y%m%d_%H%M%S_') + vname
                    dest = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', vname)
                    # Optional size guard for very large uploads
                    try:
                        v.stream.seek(0, os.SEEK_END)
                        size = v.stream.tell()
                        v.stream.seek(0)
                        if size <= MAX_VIDEO_BYTES:
                            v.save(dest)
                            video_filename = 'videos/' + vname
                        else:
                            flash('Video too large. Maximum 50MB allowed.', 'danger')
                    except Exception:
                        # Fallback if size check not available
                        v.save(dest)
                        video_filename = 'videos/' + vname
                else:
                    flash('Unsupported video format. Allowed: MP4, WebM, Ogg.', 'danger')

        new_product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            subcategory_id=subcategory_id,
            seller_id=session['user_id'],
            image_filename=image_filename,
            video_filename=video_filename,
            gallery=gallery_list or None,
            status='pending'
        )

        db.session.add(new_product)
        db.session.commit()  # After commit, new_product.id is the real auto-increment ID

        try:
            notify_admins(
                f"New product pending approval from {session['user_name']}: {name} (Product ID: {new_product.id})",
                type='product_pending',
                link=f'/admin/products?filter=pending&product_id={new_product.id}',
                image_url=new_product.image_filename if new_product.image_filename else None
            )
        except Exception:
            pass

        flash(f'Product submitted for review. Assigned Product ID: {new_product.id}. It will appear after admin approval.', 'info')
        return redirect(url_for('seller_dashboard'))

    # GET request
    # Get unique categories to avoid duplicates in dropdown
    all_categories = Category.query.filter_by(status='active').order_by(Category.name).all()
    # Remove duplicates by keeping only the first occurrence of each name
    seen_names = set()
    categories = []
    for cat in all_categories:
        if cat.name not in seen_names:
            seen_names.add(cat.name)
            categories.append(cat)
    subcategories = Subcategory.query.filter_by(status='active').order_by(Subcategory.name).all()  # Ensure template has this
    return render_template('seller/add_product.html',
                           categories=categories,
                           subcategories=subcategories,
                           next_product_id=next_product_id)

# ... (rest of file unchanged)

@app.route('/seller/orders')
@seller_required
def seller_orders():
    seller_id = session['user_id']
    
    # Get filter parameters
    status = request.args.get('status', 'all')
    payment_status = request.args.get('payment_status', 'all')
    search = request.args.get('search', '')
    date_range = request.args.get('date_range', 'all')
    payment_method = request.args.get('payment_method', 'all')
    
    # Build query with joins - only orders that contain products from this seller
    query = Order.query.join(OrderItem).join(Product).filter(
        Product.seller_id == seller_id
    ).distinct()
    
    # Apply filters
    if status != 'all':
        if status == 'new':
            # Show all pending orders (new orders that haven't been processed)
            query = query.filter(Order.status == 'pending')
        elif status == 'processing':
            query = query.filter(Order.status == 'processing')
        elif status == 'ready_for_pickup':
            query = query.filter(Order.status == 'ready_for_pickup')
        elif status == 'to_ship':
            query = query.filter(Order.status == 'to_ship')
        elif status == 'delivered':
            query = query.filter(Order.status == 'delivered')
        elif status == 'completed':
            query = query.filter(Order.status == 'completed')
        elif status == 'returns':
            # Orders with return requests
            query = query.join(ReturnRequest).filter(ReturnRequest.status != 'rejected')
    
    if payment_status != 'all':
        query = query.filter(Order.payment_status == payment_status)
    
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Order.id.like(search_term),
                Order.buyer_name.like(search_term),
                Order.buyer_email.like(search_term)
            )
        )
    
    if date_range != 'all':
        now = datetime.utcnow()
        if date_range == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(Order.created_at >= start)
        elif date_range == 'week':
            start = now - timedelta(days=7)
            query = query.filter(Order.created_at >= start)
        elif date_range == 'month':
            start = now - timedelta(days=30)
            query = query.filter(Order.created_at >= start)
    
    if payment_method != 'all':
        query = query.filter(Order.payment_method == payment_method)
    
    # Order by most recent first
    orders = query.order_by(Order.created_at.desc()).all()
    
    # Calculate totals
    total_orders = len(orders)
    total_revenue = 0
    pending_orders = 0
    processing_orders = 0
    completed_orders = 0
    
    for order in orders:
        # Calculate seller's revenue from this order
        seller_items = [item for item in order.items if item.product.seller_id == seller_id]
        order_revenue = sum(item.price_at_time * item.quantity for item in seller_items)
        total_revenue += order_revenue
        
        # Count by status for header badges
        if order.status == 'pending':
            pending_orders += 1
        elif order.status == 'processing':
            processing_orders += 1
        elif order.status == 'completed':
            completed_orders += 1
    
    # Compute per-order seller summaries and "new" status for Manage Orders tabs
    from datetime import datetime, timedelta, timezone
    recent_cutoff = datetime.utcnow() - timedelta(hours=24)

    # Preload seen order IDs for this seller for New Orders logic
    seen_ids = {
        row.order_id for row in SellerOrderSeen.query.filter_by(seller_id=seller_id).all()
    }

    for order in orders:
        seller_items = [item for item in order.items if item.product.seller_id == seller_id]
        order.seller_total = sum(item.price_at_time * item.quantity for item in seller_items)
        order.seller_items_count = sum(item.quantity for item in seller_items)
        order.seller_items = seller_items

        # New Orders tab: pending + unseen (show all new orders regardless of processing status)
        order.is_new = (order.status == 'pending') and (order.id not in seen_ids)
        
        # Processing tab: orders being processed by seller
        order.is_processing_tab = (order.status == 'processing')
        
        # Ready for Pick Up tab
        order.is_ready_tab = (order.status == 'ready_for_pickup')
        
        # To Ship tab
        order.is_to_ship_tab = (order.status == 'to_ship')
        
        # Delivered tab
        order.is_delivered_tab = (order.status == 'delivered')
        
        # Completed tab
        order.is_completed_tab = (order.status == 'completed')
        
        # Returns tab: orders with return requests
        active_returns = [rr for rr in order.return_requests if rr.status != 'rejected']
        order.is_returns_tab = order.status in ['return_requested', 'refunded', 'returned'] or len(active_returns) > 0

    # Unread chat count for sidebar badge (product chats)
    from sqlalchemy import text
    unread_chat_count = db.session.execute(text("""
        SELECT COUNT(*) FROM chat_message 
        WHERE receiver_id = :seller_id 
        AND is_read = FALSE 
        AND product_id IS NOT NULL
    """), {'seller_id': seller_id}).scalar() or 0

    # Unread order count for notification badge: recent orders without a seen record
    unread_order_count = db.session.query(Order).join(OrderItem).join(Product).filter(
        Product.seller_id == seller_id,
        Order.created_at >= recent_cutoff
    ).filter(~Order.id.in_(
        db.session.query(SellerOrderSeen.order_id).filter_by(seller_id=seller_id)
    )).distinct().count()

    return render_template('seller/orders.html', 
                         orders=orders, 
                         status=status, 
                         payment_status=payment_status,
                         search=search,
                         date_range=date_range,
                         payment_method=payment_method,
                         unread_chat_count=unread_chat_count,
                         unread_order_count=unread_order_count,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         pending_orders=pending_orders,
                         processing_orders=processing_orders,
                         completed_orders=completed_orders)


@app.route('/seller/order/<int:order_id>')
@seller_required
def seller_order_detail(order_id):
    seller_id = session['user_id']
    order = Order.query.get_or_404(order_id)

    # Ensure this seller has items in this order
    seller_items = [item for item in order.items if item.product.seller_id == seller_id]
    if not seller_items:
        flash('You are not authorized to view this order.', 'error')
        return redirect(url_for('seller_orders'))

    seller_total = sum(item.price_at_time * item.quantity for item in seller_items)

    # Mark this order as seen for this seller
    exists = SellerOrderSeen.query.filter_by(seller_id=seller_id, order_id=order.id).first()
    if not exists:
        try:
            db.session.add(SellerOrderSeen(seller_id=seller_id, order_id=order.id))
            db.session.commit()
        except Exception:
            db.session.rollback()

    # Unread chat count for sidebar badge (product chats)
    from sqlalchemy import text
    unread_chat_count = db.session.execute(text("""
        SELECT COUNT(*) FROM chat_message 
        WHERE receiver_id = :seller_id 
        AND is_read = FALSE 
        AND product_id IS NOT NULL
    """), {'seller_id': seller_id}).scalar() or 0

    return render_template('seller/order_detail.html',
                           order=order,
                           seller_items=seller_items,
                           seller_total=seller_total,
                           unread_chat_count=unread_chat_count)

@app.route('/seller/stats/summary')
@seller_required
def seller_stats_summary():
    seller_id = session['user_id']
    stats = _compute_seller_stats(seller_id)
    return jsonify({'success': True, 'data': stats})


@app.route('/seller/sales-report')
@seller_required
def seller_sales_report():
    seller_id = session['user_id']
    
    # Get filter parameters - expanded to match order management filters
    date_range = request.args.get('date_range', '30days')
    product_filter = request.args.get('product', 'all')
    status_filter = request.args.get('status', 'all')  # Order status filter
    payment_status_filter = request.args.get('payment_status', 'paid')  # Default to paid for revenue
    payment_method = request.args.get('payment_method', 'all')
    
    # Date range filtering
    from datetime import datetime, timedelta, timezone
    now = datetime.utcnow()
    start_date = None
    
    if date_range == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_range == '7days':
        start_date = now - timedelta(days=7)
    elif date_range == '30days':
        start_date = now - timedelta(days=30)
    elif date_range == '90days':
        start_date = now - timedelta(days=90)
    elif date_range == 'year':
        start_date = now - timedelta(days=365)
    # 'all' means no date filter
    
    # Base query: get all order items for this seller's products
    query = db.session.query(
        OrderItem,
        Order,
        Product
    ).join(Order).join(Product).filter(
        Product.seller_id == seller_id
    )
    
    # Apply payment status filter
    if payment_status_filter != 'all':
        query = query.filter(Order.payment_status == payment_status_filter)
    
    # Apply order status filter
    if status_filter != 'all':
        query = query.filter(Order.status == status_filter)
    
    # Apply payment method filter
    if payment_method != 'all':
        query = query.filter(Order.payment_method == payment_method)
    
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    
    if product_filter != 'all':
        query = query.filter(Product.id == int(product_filter))
    
    # Get all sales data
    sales_data = query.order_by(Order.created_at.desc()).all()
    
    # Calculate summary statistics (legacy, paid order-based)
    legacy_revenue = sum(item.price_at_time * item.quantity for item, order, _ in sales_data if order.payment_status == 'paid')
    
    # Wallet commissions (final revenue after buyer confirms)
    wallet_q = WalletTransaction.query.filter_by(user_id=seller_id, type='credit', source='order_commission')
    if start_date:
        wallet_q = wallet_q.filter(WalletTransaction.created_at >= start_date)
    total_revenue = float(wallet_q.with_entities(db.func.coalesce(db.func.sum(WalletTransaction.amount), 0.0)).scalar() or 0.0)
    total_orders = len(set(order.id for _, order, _ in sales_data))
    total_items_sold = sum(item.quantity for item, _, _ in sales_data)
    paid_orders_count = len(set(order.id for _, order, _ in sales_data if order.payment_status == 'paid'))
    pending_orders_count = len(set(order.id for _, order, _ in sales_data if order.payment_status == 'pending'))
    
    # Order status breakdown
    status_breakdown = {
        'pending': len(set(order.id for _, order, _ in sales_data if order.status == 'pending')),
        'processing': len(set(order.id for _, order, _ in sales_data if order.status == 'processing')),
        'shipped': len(set(order.id for _, order, _ in sales_data if order.status == 'shipped')),
        'completed': len(set(order.id for _, order, _ in sales_data if order.status == 'completed')),
        'cancelled': len(set(order.id for _, order, _ in sales_data if order.status == 'cancelled'))
    }
    
    # Payment status breakdown (kept for reference)
    payment_breakdown = {
        'paid': paid_orders_count,
        'pending': pending_orders_count,
        'failed': len(set(order.id for _, order, _ in sales_data if order.payment_status == 'failed')),
        'refunded': len(set(order.id for _, order, _ in sales_data if order.payment_status == 'refunded'))
    }
    
    # Payment method breakdown
    payment_method_breakdown = {}
    for item, order, product in sales_data:
        method = order.payment_method
        if method not in payment_method_breakdown:
            payment_method_breakdown[method] = {'count': 0, 'revenue': 0}
        if order.payment_status == 'paid':
            payment_method_breakdown[method]['revenue'] += item.price_at_time * item.quantity
        # Count unique orders per method
    for _, order, _ in sales_data:
        method = order.payment_method
        if method in payment_method_breakdown:
            payment_method_breakdown[method]['count'] = len(set(o.id for _, o, _ in sales_data if o.payment_method == method))
    
    # Product performance analysis
    product_stats = {}
    for item, order, product in sales_data:
        if product.id not in product_stats:
            product_stats[product.id] = {
                'product': product,
                'quantity_sold': 0,
                'revenue': 0,
                'order_count': set(),
                'paid_revenue': 0,
                'pending_revenue': 0
            }
        product_stats[product.id]['quantity_sold'] += item.quantity
        product_stats[product.id]['revenue'] += item.price_at_time * item.quantity
        product_stats[product.id]['order_count'].add(order.id)
        
        # Track revenue by payment status
        if order.payment_status == 'paid':
            product_stats[product.id]['paid_revenue'] += item.price_at_time * item.quantity
        elif order.payment_status == 'pending':
            product_stats[product.id]['pending_revenue'] += item.price_at_time * item.quantity
    
    # Convert to list and sort by revenue
    product_performance = [
        {
            'product_id': pid,
            'product_name': stats['product'].name,
            'product_image': stats['product'].image_filename,
            'quantity_sold': stats['quantity_sold'],
            'revenue': stats['revenue'],
            'paid_revenue': stats['paid_revenue'],
            'pending_revenue': stats['pending_revenue'],
            'order_count': len(stats['order_count']),
            'avg_price': stats['revenue'] / stats['quantity_sold'] if stats['quantity_sold'] > 0 else 0,
            'current_stock': stats['product'].stock
        }
        for pid, stats in product_stats.items()
    ]
    product_performance.sort(key=lambda x: x['paid_revenue'], reverse=True)
    
    # Daily sales chart data (last 30 days or selected range)
    daily_sales = {}
    for item, order, product in sales_data:
        date_key = order.created_at.strftime('%Y-%m-%d')
        if date_key not in daily_sales:
            daily_sales[date_key] = {
                'date': date_key, 
                'revenue': 0, 
                'paid_revenue': 0,
                'orders': set(), 
                'items': 0,
                'paid_orders': set()
            }
        daily_sales[date_key]['revenue'] += item.price_at_time * item.quantity
        if order.payment_status == 'paid':
            daily_sales[date_key]['paid_revenue'] += item.price_at_time * item.quantity
            daily_sales[date_key]['paid_orders'].add(order.id)
        daily_sales[date_key]['orders'].add(order.id)
        daily_sales[date_key]['items'] += item.quantity
    
    # Convert to sorted list
    daily_sales_list = [
        {
            'date': data['date'],
            'revenue': data['revenue'],
            'paid_revenue': data['paid_revenue'],
            'order_count': len(data['orders']),
            'paid_order_count': len(data['paid_orders']),
            'items_sold': data['items']
        }
        for date_key, data in daily_sales.items()
    ]
    daily_sales_list.sort(key=lambda x: x['date'])
    
    # Recent transactions (detailed order items) - matches what's in order management
    recent_transactions = [
        {
            'order_id': order.id,
            'order_date': order.created_at,
            'product_name': product.name,
            'product_id': product.id,
            'quantity': item.quantity,
            'unit_price': item.price_at_time,
            'total': item.price_at_time * item.quantity,
            'buyer_name': f"{order.buyer.first_name} {order.buyer.last_name}",
            'buyer_email': order.buyer.email,
            'buyer_phone': order.buyer.phone,
            'order_status': order.status,
            'payment_status': order.payment_status,
            'payment_method': order.payment_method,
            'shipping_address': order.shipping_address,
            'tracking_number': order.tracking_number if hasattr(order, 'tracking_number') else None,
            'stock_deducted': order.stock_deducted if hasattr(order, 'stock_deducted') else False
        }
        for item, order, product in sales_data[:100]  # Increased to 100 for better analysis
    ]
    
    # Get all seller's products for filter dropdown (including inactive for historical data)
    seller_products = Product.query.filter_by(seller_id=seller_id).order_by(Product.name).all()
    
    # Calculate average order value (only paid orders)
    avg_order_value = total_revenue / paid_orders_count if paid_orders_count > 0 else 0
    
    # Potential revenue (pending payments)
    potential_revenue = sum(item.price_at_time * item.quantity for item, order, _ in sales_data if order.payment_status == 'pending')
    
    return render_template('seller/sales_report.html',
                         total_revenue=total_revenue,
                         total_orders=total_orders,
                         paid_orders_count=paid_orders_count,
                         pending_orders_count=pending_orders_count,
                         total_items_sold=total_items_sold,
                         avg_order_value=avg_order_value,
                         potential_revenue=potential_revenue,
                         status_breakdown=status_breakdown,
                         payment_breakdown=payment_breakdown,
                         payment_method_breakdown=payment_method_breakdown,
                         product_performance=product_performance,
                         daily_sales=daily_sales_list,
                         recent_transactions=recent_transactions,
                         seller_products=seller_products,
                         date_range=date_range,
                         product_filter=product_filter,
                         status_filter=status_filter,
                         payment_status_filter=payment_status_filter,
                         payment_method=payment_method,
                         now=datetime.utcnow)

@app.route('/seller/notifications')
@seller_required
def seller_notifications():
    notifications = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.created_at.desc()).all()
    Notification.query.filter_by(user_id=session['user_id'], is_read=False).update({Notification.is_read: True})
    db.session.commit()
    
    # Convert to dict for JSON serialization
    notifications_data = [{
        'id': n.id,
        'message': n.message,
        'title': n.title,
        'image_url': n.image_url,
        'link': n.link,
        'type': n.type,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat() if n.created_at else None,
        'order_id': n.order_id,
        'images': n.images
    } for n in notifications]
    
    return render_template('seller/notifications.html', notifications=notifications_data)

@app.route('/buyer/notifications')
@login_required
def buyer_notifications():
    # Only allow buyers to access this
    user = db.session.get(User, session['user_id'])
    active_role = session.get('active_role', user.role)
    if active_role != 'buyer' and user.role != 'buyer':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
    
    notifications = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.created_at.desc()).all()

    # Build enriched entries with order info when possible
    enriched = []
    for n in notifications:
        order = None
        first_item = None
        tracking = None
        status = None
        try:
            import re as _re
            m = _re.search(r"order\s*#(\d+)", n.message, _re.IGNORECASE)
            if not m:
                m = _re.search(r"Order\s*(\d+)", n.message, _re.IGNORECASE)
            if m:
                oid = int(m.group(1))
                order = Order.query.filter_by(id=oid, buyer_id=session['user_id']).first()
        except Exception:
            order = None
        if order:
            tracking = getattr(order, 'tracking_number', None)
            status = order.status
            try:
                first_item = order.items[0] if order.items else None
            except Exception:
                first_item = None
        # Resolve actor avatar/name for rich chat notifications
        actor = getattr(n, 'actor', None)
        actor_name = None
        actor_avatar = None
        if actor:
            actor_name = f"{actor.first_name} {actor.last_name}"
            # Use user profile picture for riders
            try:
                if actor.profile_picture:
                    actor_avatar = actor.profile_picture
            except Exception:
                actor_avatar = None
        enriched.append({
            'notification': n,
            'order': order,
            'first_item': first_item,
            'tracking': tracking,
            'status': status,
            'actor_name': actor_name,
            'actor_avatar': actor_avatar
        })

    # Mark all as read when viewed
    Notification.query.filter_by(user_id=session['user_id'], is_read=False).update({Notification.is_read: True})
    db.session.commit()
    
    # Convert notifications to dict for JSON serialization
    notifications_data = [{
        'id': n.id,
        'message': n.message,
        'title': n.title,
        'image_url': n.image_url,
        'link': n.link,
        'type': n.type,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat() if n.created_at else None,
        'order_id': n.order_id,
        'images': n.images
    } for n in notifications]
    
    return render_template('buyer_notifications.html', notifications=notifications_data, enriched_notifications=enriched)


@app.route('/seller/products/edit/<int:product_id>', methods=['GET', 'POST'])
@seller_required
def seller_edit_product(product_id):
    ensure_product_video_column()
    product = Product.query.filter_by(id=product_id, seller_id=session['user_id']).first_or_404()
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        # Stock is no longer updated here - sellers must use restock requests
        # product.stock = int(request.form['stock'])  # REMOVED - use restock requests instead
        product.category_id = int(request.form['category_id'])
        # Optional image update
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                filename = datetime.utcnow().strftime('%Y%m%d_%H%M%S_') + filename
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image_filename = filename
        
        # Handle gallery images (image2, image3, image4, image5)
        gallery_images = []
        for i in range(2, 6):
            field_name = f'image{i}'
            if field_name in request.files:
                file = request.files[field_name]
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filename = datetime.utcnow().strftime('%Y%m%d_%H%M%S_') + filename
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    gallery_images.append(filename)
        
        # Update gallery if new images were uploaded
        if gallery_images:
            # Merge with existing gallery images, but prioritize new ones
            existing_gallery = product.gallery or []
            # Replace existing images with new ones in the same positions
            for i, new_image in enumerate(gallery_images):
                index = i  # 0-based index for gallery array
                if index < len(existing_gallery):
                    existing_gallery[index] = new_image
                else:
                    existing_gallery.append(new_image)
            product.gallery = existing_gallery
        # Optional video update
        if 'video' in request.files:
            v = request.files['video']
            if v and v.filename:
                vext = v.filename.rsplit('.', 1)[-1].lower() if '.' in v.filename else ''
                if vext in ALLOWED_VIDEO_EXT:
                    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)
                    vname = secure_filename(v.filename)
                    vname = datetime.utcnow().strftime('%Y%m%d_%H%M%S_') + vname
                    v.save(os.path.join(app.config['UPLOAD_FOLDER'], 'videos', vname))
                    product.video_filename = 'videos/' + vname
                else:
                    flash('Unsupported video format. Allowed: MP4, WebM, Ogg.', 'danger')
        # Status logic depending on previous state
        if product.status == 'active':
            product.status = 'pending'  # Re-review after edits
        elif product.status in ['pending', 'rejected', 'inactive']:
            product.status = 'pending'
        db.session.commit()
        # Notify seller (self)
        db.session.add(Notification(user_id=product.seller_id, message=f'Your product {product.name} was updated.'))
        db.session.commit()
        flash('Product updated successfully! Note: Stock quantity changes require admin approval through the restock request system.', 'info')
        return redirect(url_for('seller_products'))
    categories = Category.query.all()
    # Compute what the seller is allowed to do based on status
    editable = True  # All statuses editable per your rules
    status_note = None
    if product.status == 'active':
        status_note = 'Editing will send the product for admin review again.'
    elif product.status == 'rejected':
        status_note = 'Rejected. You can edit and resubmit.'
    elif product.status == 'pending':
        status_note = 'Pending approval. You can still edit it.'
    return render_template('seller/edit_product.html', product=product, categories=categories, editable=editable, status_note=status_note)

@app.route('/seller/products/delete/<int:product_id>', methods=['POST'])
@seller_required
def seller_delete_product(product_id):
    # Ensure the product belongs to the seller
    product = Product.query.filter_by(id=product_id, seller_id=session['user_id']).first_or_404()

    # Hard-delete the product and clean related data and orders
    stats = _delete_products_by_ids([product.id])
    db.session.commit()

    # Notify admins of deletion
    try:
        notify_admins(f'Seller permanently deleted product: {product.name}')
    except Exception:
        pass
    flash('Product permanently deleted and removed from any orders.', 'success')
    return redirect(url_for('seller_products'))

@app.route('/seller/products')
@seller_required
def seller_products():
    seller_id = session['user_id']
    products = Product.query.filter_by(seller_id=seller_id).order_by(Product.created_at.desc()).all()
    categories = {c.id: c.name for c in Category.query.all()}
    return render_template('seller/products.html', products=products, categories=categories, get_available_stock=get_available_stock)

@app.route('/seller/restock/<int:product_id>', methods=['POST'])
@seller_required
def seller_restock_product(product_id):
    """Submit restock request to admin"""
    # Ensure the product belongs to the seller
    product = Product.query.filter_by(id=product_id, seller_id=session['user_id']).first_or_404()
    
    try:
        # Get restock quantity from form
        restock_quantity = int(request.form.get('restock_quantity', 1))
        
        if restock_quantity <= 0:
            flash('Restock quantity must be greater than 0.', 'error')
            return redirect(url_for('seller_products'))
        
        # Check if there's already a pending restock request
        existing_request = RestockRequest.query.filter_by(
            product_id=product_id, 
            seller_id=session['user_id'],
            status='pending'
        ).first()
        
        if existing_request:
            flash(f'You already have a pending restock request for "{product.name}". Please wait for admin approval.', 'warning')
            return redirect(url_for('seller_products'))
        
        # Create restock request
        restock_request = RestockRequest(
            product_id=product_id,
            seller_id=session['user_id'],
            requested_quantity=restock_quantity
        )
        
        db.session.add(restock_request)
        db.session.commit()
        
        flash(f'Restock request for "{product.name}" ({restock_quantity} items) has been submitted to admin for approval.', 'success')
        
        # Log the restock request
        app.logger.info(f"Seller {session['user_id']} submitted restock request for product {product_id}: {restock_quantity} units")
        
    except ValueError:
        flash('Invalid restock quantity.', 'error')
    except Exception as e:
        app.logger.error(f"Error submitting restock request for product {product_id}: {e}")
        flash('An error occurred while submitting the restock request.', 'error')
    
    return redirect(url_for('seller_products'))

@app.route('/seller/cancel-restock/<int:product_id>', methods=['POST'])
@seller_required
def seller_cancel_restock(product_id):
    """Cancel pending restock request"""
    # Ensure the product belongs to the seller
    product = Product.query.filter_by(id=product_id, seller_id=session['user_id']).first_or_404()
    
    try:
        # Find pending restock request
        restock_request = RestockRequest.query.filter_by(
            product_id=product_id, 
            seller_id=session['user_id'],
            status='pending'
        ).first()
        
        if not restock_request:
            flash('No pending restock request found for this product.', 'error')
            return redirect(url_for('seller_products'))
        
        db.session.delete(restock_request)
        db.session.commit()
        
        flash(f'Restock request for "{product.name}" has been cancelled.', 'success')
        
        # Log the cancellation
        app.logger.info(f"Seller {session['user_id']} cancelled restock request for product {product_id}")
        
    except Exception as e:
        app.logger.error(f"Error cancelling restock request for product {product_id}: {e}")
        flash('An error occurred while cancelling the restock request.', 'error')
    
    return redirect(url_for('seller_products'))

@app.route('/admin/restock-requests')
@admin_required
def admin_restock_requests():
    """Admin page to view and manage restock requests"""
    restock_requests = RestockRequest.query.order_by(RestockRequest.created_at.desc()).all()
    
    # Add product and seller information
    requests_data = []
    for req in restock_requests:
        requests_data.append({
            'id': req.id,
            'product': req.product,
            'seller': req.seller,
            'requested_quantity': req.requested_quantity,
            'approved_quantity': req.approved_quantity,
            'status': req.status,
            'created_at': req.created_at,
            'processed_at': req.processed_at,
            'admin_notes': req.admin_notes
        })
    
    # Count pending requests for badge
    pending_count = RestockRequest.query.filter_by(status='pending').count()
    
    badge_counts = get_admin_badge_counts()
    return render_template('admin/restock_requests.html', 
                         restock_requests=requests_data,
                         **badge_counts)

@app.route('/admin/approve-restock/<int:request_id>', methods=['POST'])
@admin_required
def admin_approve_restock(request_id):
    """Approve a restock request"""
    restock_request = RestockRequest.query.get_or_404(request_id)
    
    try:
        # Get approved quantity from form
        approved_quantity = int(request.form.get('approved_quantity', restock_request.requested_quantity))
        admin_notes = request.form.get('admin_notes', '')
        
        if approved_quantity <= 0:
            flash('Approved quantity must be greater than 0.', 'error')
            return redirect(url_for('admin_restock_requests'))
        
        # Update restock request
        restock_request.status = 'approved'
        restock_request.approved_quantity = approved_quantity
        restock_request.processed_at = datetime.utcnow()
        restock_request.processed_by = session['user_id']
        restock_request.admin_notes = admin_notes
        
        # Update product stock
        product = restock_request.product
        old_stock = product.stock
        product.stock += approved_quantity
        product.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Calculate available stock after approval
        available_stock = get_available_stock(product.id)
        
        # Emit real-time stock update to all users
        try:
            socketio.emit('product_stock_update', {
                'product_id': product.id,
                'stock': available_stock,
                'available_stock': available_stock
            }, broadcast=True)
            
            # Notify seller
            push_notification(restock_request.seller_id, 
                           f'Your restock request for "{product.name}" has been approved! {approved_quantity} items added.')
            
        except Exception as e:
            app.logger.error(f"Socket.IO emit error: {e}")
        
        flash(f'Restock request for "{product.name}" approved! Added {approved_quantity} items to inventory.', 'success')
        
        # Log the approval
        app.logger.info(f"Admin {session['user_id']} approved restock request {request_id} for product {product.id}: {approved_quantity} units")
        
    except ValueError:
        flash('Invalid approved quantity.', 'error')
    except Exception as e:
        app.logger.error(f"Error approving restock request {request_id}: {e}")
        flash('An error occurred while approving the restock request.', 'error')
    
    return redirect(url_for('admin_restock_requests'))

@app.route('/admin/reject-restock/<int:request_id>', methods=['POST'])
@admin_required
def admin_reject_restock(request_id):
    """Reject a restock request"""
    restock_request = RestockRequest.query.get_or_404(request_id)
    
    try:
        admin_notes = request.form.get('admin_notes', '')
        
        # Update restock request
        restock_request.status = 'rejected'
        restock_request.processed_at = datetime.utcnow()
        restock_request.processed_by = session['user_id']
        restock_request.admin_notes = admin_notes
        
        db.session.commit()
        
        # Notify seller
        push_notification(restock_request.seller_id, 
                       f'Your restock request for "{restock_request.product.name}" has been rejected.')
        
        flash(f'Restock request for "{restock_request.product.name}" has been rejected.', 'success')
        
        # Log the rejection
        app.logger.info(f"Admin {session['user_id']} rejected restock request {request_id} for product {restock_request.product.id}")
        
    except Exception as e:
        app.logger.error(f"Error rejecting restock request {request_id}: {e}")
        flash('An error occurred while rejecting the restock request.', 'error')
    
    return redirect(url_for('admin_restock_requests'))

@app.route('/shop')
def shop():
    category_id = request.args.get('category')
    subcategory_id = request.args.get('subcategory')
    sort_by = request.args.get('sort', 'featured')
    search = request.args.get('search', '')
    price_min = request.args.get('price_min', '')
    price_max = request.args.get('price_max', '')

    # Show only approved products in the public shop view (window shopping - no login required)
    query = Product.query.filter_by(status='approved')

    # Category filter
    if category_id:
        try:
            query = query.filter(Product.category_id == int(category_id))
        except ValueError:
            pass

    # Subcategory filter
    if subcategory_id:
        try:
            query = query.filter(Product.subcategory_id == int(subcategory_id))
        except ValueError:
            pass

    # Text search (name + description)
    if search:
        search_filter = or_(
            Product.name.ilike(f'%{search}%'),
            Product.description.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)

    # Price range filters
    try:
        if price_min:
            min_value = float(price_min)
            query = query.filter(Product.price >= min_value)
    except ValueError:
        price_min = ''
    try:
        if price_max:
            max_value = float(price_max)
            query = query.filter(Product.price <= max_value)
    except ValueError:
        price_max = ''

    # Sorting
    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'newest':
        query = query.order_by(Product.created_at.desc())
    else:  # featured
        query = query.order_by(Product.featured.desc(), Product.created_at.desc())

    products = query.all()
    # Compute total sold per product (sum of quantities from completed orders)
    for product in products:
        total_sold = db.session.query(db.func.sum(OrderItem.quantity)).join(Order).filter(
            OrderItem.product_id == product.id,
            Order.status.in_(['completed', 'delivered'])
        ).scalar() or 0
        product.total_sold = int(total_sold)

    # Only show active categories (unique)
    all_categories = Category.query.filter_by(status='active').order_by(Category.name).all()
    # Remove duplicates by keeping only the first occurrence of each name
    seen_names = set()
    categories = []
    for cat in all_categories:
        if cat.name not in seen_names:
            seen_names.add(cat.name)
            categories.append(cat)

    return render_template(
        'shop.html',
        products=products,
        categories=categories,
        current_category=category_id,
        current_subcategory=subcategory_id,
        current_sort=sort_by,
        search=search,
        price_min=price_min,
        price_max=price_max,
    )

@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    # Login check - redirect to login if not authenticated
    if 'user_id' not in session:
        flash('Please login to add items to cart.', 'info')
        return redirect(url_for('login'))
    
    # Admin accounts are view-only; block shopping actions
    try:
        if is_admin():
            msg = 'Admin accounts are view-only and cannot add items to cart.'
            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({'success': False, 'message': msg}), 403
            flash(msg, 'warning')
            return redirect(request.referrer or url_for('product_detail', product_id=product_id))
    except Exception:
        pass
    product = Product.query.get_or_404(product_id)
    
    # Public shop items are purchasable once approved (or already active)
    if product.status not in ['approved', 'active']:
        flash('Product not available.', 'error')
        return redirect(request.referrer or url_for('shop'))
    
    # Check if user is trying to buy their own product
    if product.seller_id == session['user_id']:
        flash('You cannot purchase your own products.', 'error')
        return redirect(request.referrer or url_for('shop'))
    
    # Check available stock (considering reserved orders)
    available_stock = get_available_stock(product_id)
    
    # Check if item already in cart
    cart_item = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    
    if cart_item:
        # Check available stock before increasing quantity
        if cart_item.quantity >= available_stock:
            flash(f'Cannot add more items. Only {available_stock} items available.', 'error')
        else:
            cart_item.quantity += 1
            db.session.commit()
            flash('Item quantity updated in cart.', 'success')
    else:
        # Check available stock before adding new item
        if available_stock <= 0:
            flash('Product is out of stock.', 'error')
        else:
            cart_item = Cart(user_id=session['user_id'], product_id=product_id, quantity=1)
            db.session.add(cart_item)
            db.session.commit()
            if available_stock <= 10:
                flash(f'Product is low stock. Only {available_stock} item(s) available.', 'warning')
            else:
                flash('Product added to cart!', 'success')
    
    # Check if it's an AJAX request
    if request.headers.get('Content-Type') == 'application/json' or request.is_json:
        # Calculate new cart count
        cart_count = Cart.query.filter_by(user_id=session['user_id']).count()
        return jsonify({
            'success': True,
            'message': 'Product added to cart!',
            'cart_count': cart_count
        })
    
    return redirect(request.referrer or url_for('shop'))

@app.route('/add-to-cart-ajax/<int:product_id>', methods=['POST'])
def add_to_cart_ajax(product_id):
    # Login check - redirect to login if not authenticated
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login to add items to cart.', 'redirect': url_for('login')}), 401
    
    # Admin accounts cannot add to cart
    try:
        if is_admin():
            return jsonify({'success': False, 'message': 'Admin accounts are view-only and cannot add items to cart.'}), 403
    except Exception:
        pass
    try:
        product = Product.query.get_or_404(product_id)
    
        # Public shop items are purchasable once approved (or already active)
        if product.status not in ['approved', 'active']:
            return jsonify({'success': False, 'message': 'Product not available.'}), 400
        
        # Check if user is trying to buy their own product
        if product.seller_id == session['user_id']:
            return jsonify({'success': False, 'message': 'You cannot purchase your own products.'}), 400
        
        # Parse requested quantity (defaults to 1)
        data = request.get_json(silent=True) or {}
        try:
            req_qty = int(data.get('qty') or data.get('quantity') or 1)
        except Exception:
            req_qty = 1
        if req_qty < 1:
            req_qty = 1
        
        # Check available stock (considering reserved orders)
        available_stock = get_available_stock(product_id)
        if available_stock <= 0:
            return jsonify({'success': False, 'message': 'Product is out of stock.'}), 400
        
        # Check if item already in cart
        cart_item = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
        
        if cart_item:
            current = int(cart_item.quantity or 0)
            can_add = max(available_stock - current, 0)
            if can_add <= 0:
                return jsonify({'success': False, 'message': f'Cannot add more items. Only {available_stock} available.'}), 400
            add_qty = min(req_qty, can_add)
            cart_item.quantity = current + add_qty
        else:
            add_qty = min(req_qty, available_stock)
            if add_qty <= 0:
                return jsonify({'success': False, 'message': 'Product is out of stock.'}), 400
            cart_item = Cart(user_id=session['user_id'], product_id=product_id, quantity=add_qty)
            db.session.add(cart_item)
        
        db.session.commit()
        
        cart_count = Cart.query.filter_by(user_id=session['user_id']).count()
        msg = 'Added to cart.' if add_qty == req_qty else f'Added {add_qty} (limited by stock).'
        return jsonify({'success': True, 'message': msg, 'cart_count': cart_count, 'new_quantity': cart_item.quantity})
    except Exception:
        return jsonify({'success': False, 'message': 'Error adding product to cart'}), 500


@app.route('/buy-now/<int:product_id>', methods=['GET', 'POST'])
@login_required
def buy_now(product_id):
    """Create a separate cart line for this product (ignoring any existing one) and checkout ONLY that line with the selected qty."""
    # Block admin users
    try:
        if is_admin():
            flash('Admin accounts are view-only and cannot purchase items.', 'warning')
            return redirect(url_for('product_detail', product_id=product_id))
    except Exception:
        pass
    product = Product.query.get_or_404(product_id)

    # Public shop items are purchasable once approved (or already active)
    if product.status not in ['approved', 'active']:
        flash('Product not available.', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    if product.seller_id == session['user_id']:
        flash('You cannot purchase your own products.', 'error')
        return redirect(url_for('product_detail', product_id=product_id))

    # Desired quantity from query string (default 1)
    try:
        req_qty = int(request.args.get('qty', '1'))
    except Exception:
        req_qty = 1
    if req_qty < 1:
        req_qty = 1

    # Stock guard (uses order reservations, not cart contents)
    available_stock = get_available_stock(product_id)
    if available_stock <= 0:
        flash('Product is out of stock.', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    elif available_stock <= 10:
        flash(f'Product is low stock. Only {available_stock} item(s) available.', 'warning')

    add_qty = min(req_qty, max(available_stock, 0))
    if add_qty <= 0:
        flash('Cannot purchase the requested quantity due to stock limits.', 'warning')
        return redirect(url_for('product_detail', product_id=product_id))

    # IMPORTANT: always create a new cart row (do NOT merge with any existing row for same product)
    new_item = Cart(user_id=session['user_id'], product_id=product_id, quantity=add_qty)
    db.session.add(new_item)
    db.session.commit()

    # Redirect to checkout with only this new cart item selected
    return redirect(url_for('checkout', ids=str(new_item.id)))

@app.route('/debug-cart')
@login_required
def debug_cart():
    """Debug route to verify cart sorting"""
    cart_items = Cart.query.filter_by(user_id=session['user_id']).order_by(Cart.created_at.desc()).all()
    
    debug_info = []
    for item in cart_items:
        debug_info.append({
            'id': item.id,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'cart_items': debug_info,
        'total_items': len(debug_info)
    })

@app.route('/test-cart-sort')
@login_required
def test_cart_sort():
    """Test route to verify cart sorting is working"""
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    cart_items.sort(key=lambda x: x.created_at, reverse=True)
    
    result = []
    for i, item in enumerate(cart_items):
        result.append({
            'position': i + 1,
            'id': item.id,
            'product': item.product.name,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': item.created_at.timestamp()
        })
    
    return jsonify({
        'success': True,
        'items': result,
        'message': 'Items should be sorted newest first (position 1 = most recent)'
    })

@app.route('/cart')
@login_required
def cart():
    # Admin cannot use cart
    try:
        if is_admin():
            flash('Admin accounts cannot use the cart.', 'warning')
            return redirect(url_for('index'))
    except Exception:
        pass
    
    # Get cart items and sort by most recent first
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    
    # Sort in Python to guarantee ordering (newest first)
    cart_items.sort(key=lambda x: x.created_at, reverse=True)
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    # Return rendered HTML template with cart data
    return render_template('buyer/cart.html', cart_items=cart_items, total=float(total))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart'))

    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    shipping_fee = 10.0  # Example shipping fee
    
    coupon_code = request.form.get('coupon_code')
    coupon, discount, error = calculate_coupon_discount(coupon_code, subtotal)

    if error:
        flash(error, 'danger')

    total = subtotal - discount + shipping_fee

    if request.method == 'POST':
        # Create order
        new_order = Order(
            buyer_id=session['user_id'],
            total_amount=total,
            payment_method=request.form['payment_method'],
            shipping_address=request.form['address'],
            coupon_id=coupon.get('id') if coupon else None,
            discount_amount=discount
        )
        db.session.add(new_order)
        db.session.flush()  # Get order ID

        # Move items from cart to order items and reserve stock
        for item in cart_items:
            # Reserve stock for this order (do not commit inside reserve_stock)
            ok = reserve_stock(new_order.id, item.product_id, item.quantity)
            if not ok:
                db.session.rollback()
                flash(f'Insufficient stock to reserve {item.quantity} x {item.product.name}', 'error')
                return redirect(url_for('cart'))

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_time=item.product.price
            )
            db.session.add(order_item)
            db.session.delete(item)

        if coupon:
            coupon.used_count = (coupon.used_count or 0) + 1

        # Commit reservations, order and items together
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Failed to place order. Please try again.', 'error')
            return redirect(url_for('cart'))

        flash('Order placed successfully! Stock has been reserved.', 'success')
        return redirect(url_for('order_confirmation', order_id=new_order.id))

    now = datetime.utcnow()
    available_coupons = Coupon.query.filter(
        Coupon.is_active == True,
        (Coupon.valid_from == None) | (Coupon.valid_from <= now),
        (Coupon.valid_until == None) | (Coupon.valid_until >= now),
        (Coupon.max_uses == None) | (Coupon.used_count < Coupon.max_uses)
    ).all()

    # Get user and default address
    user = db.session.get(User, session['user_id'])
    default_address = Address.query.filter_by(user_id=session['user_id'], is_default=True).first()
    
    # If no default address, use first available address
    if not default_address:
        default_address = Address.query.filter_by(user_id=session['user_id']).first()
    
    # Calculate delivery fee automatically based on buyer's address province
    delivery_fee = 36.0  # Default
    if default_address and default_address.province:
        try:
            delivery_fee = calculate_delivery_fee(default_address.province)
        except Exception as e:
            app.logger.warning(f"Failed to calculate delivery fee for province {default_address.province}: {e}")
            delivery_fee = 36.0
    
    # If no default address, use first available address
    if not default_address:
        default_address = Address.query.filter_by(user_id=session['user_id']).first()
    
    # Calculate delivery fee automatically based on buyer's address province
    delivery_fee = 36.0  # Default
    if default_address and default_address.province:
        try:
            delivery_fee = calculate_delivery_fee(default_address.province)
        except Exception as e:
            app.logger.warning(f"Failed to calculate delivery fee for province {default_address.province}: {e}")
            delivery_fee = 36.0

    # Calculate grand total
    grand_total = total + shipping_fee - discount

    return render_template('buyer/checkout.html',
                           cart_items=cart_items,
                           subtotal=subtotal,
                           shipping_fee=shipping_fee,
        delivery_fee=delivery_fee,
                           total=total,
                           discount=discount,
                           grand_total=grand_total,
                           coupon_code=coupon_code,
                           available_coupons=available_coupons,
                           user=user,
                           default_address=default_address)
    # Admin cannot access checkout
    try:
        if is_admin():
            flash('Admin accounts cannot checkout.', 'warning')
            return redirect(url_for('index'))
    except Exception:
        pass
    # Optional: selected cart item IDs passed from cart via ?ids=1,2,3
    raw_ids = (request.args.get('ids') or '').strip()
    selected_ids = []
    if raw_ids:
        try:
            selected_ids = [int(x) for x in raw_ids.split(',') if x.strip().isdigit()]
        except Exception:
            selected_ids = []

    # Load user's cart; if ids provided, filter to those
    base_query = Cart.query.filter_by(user_id=session['user_id'])
    if selected_ids:
        cart_items = base_query.filter(Cart.id.in_(selected_ids)).all()
    else:
        cart_items = base_query.all()
    
    # Sort by most recent first
    cart_items.sort(key=lambda x: x.created_at, reverse=True)

    if not cart_items:
        flash('Please select at least one item to checkout.', 'warning')
        return redirect(url_for('cart'))

    user = db.session.get(User, session['user_id'])

    # Get all user addresses, ordered with default address first
    addresses = Address.query.filter_by(user_id=session['user_id']).order_by(
        Address.is_default.desc(),
        Address.created_at.desc()
    ).all()

    # Get default address or first address
    default_address = next((addr for addr in addresses if addr.is_default), addresses[0] if addresses else None)

    # Check if there's a newly added address to auto-select
    new_address_id = session.pop('new_address_id', None)
    if new_address_id:
        # Find the newly added address
        new_address = next((addr for addr in addresses if addr.id == new_address_id), None)
        if new_address:
            default_address = new_address

    # Check if an address was just edited
    edited_address_id = session.pop('edited_address_id', None)

    total = sum(item.product.price * item.quantity for item in cart_items)
    
    # Calculate province-based delivery fee
    delivery_fee = 36.0  # Default (Laguna)
    if default_address and default_address.province:
        try:
            delivery_fee = calculate_delivery_fee(default_address.province)
        except Exception as e:
            app.logger.warning(f"Failed to calculate delivery fee for province {default_address.province}: {e}")
            delivery_fee = 36.0
    
    shipping_fee = 0.0  # Shipping fee is now separate from delivery fee  # No shipping when nothing selected (safety)

    # Optional coupon from query string for preview
    coupon_code = request.args.get('coupon_code', '').strip()
    discount_amount = 0.0
    coupon_error = None
    applied_coupon = None

    if coupon_code:
        applied_coupon, discount_amount, coupon_error = calculate_coupon_discount(coupon_code, total)
        # If invalid, do not apply discount
        if coupon_error or not applied_coupon:
            discount_amount = 0.0
            applied_coupon = None
        else:
            # Handle free-shipping coupons by zeroing shipping_fee
            if applied_coupon.discount_type == 'free_shipping':
                shipping_fee = 0.0
            # If discount covers entire order (100% or more), waive shipping fee
            elif discount_amount >= total:
                shipping_fee = 0.0

    grand_total = total - discount_amount + delivery_fee
    # Ensure grand_total doesn't go below 0
    grand_total = max(0.0, grand_total)

    # Get available coupons for the user
    available_coupons = Coupon.query.filter(
        Coupon.is_active == True,
        Coupon.valid_from <= datetime.utcnow(),
        (Coupon.valid_until >= datetime.utcnow()) | (Coupon.valid_until == None),
        (Coupon.min_order_amount <= total) | (Coupon.min_order_amount == None)
    ).all()


    return render_template(
        'buyer/checkout.html',
        cart_items=cart_items,
        user=user,
        addresses=addresses,
        default_address=default_address,
        new_address_id=new_address_id,
        edited_address_id=edited_address_id,
        total=total,
        shipping_fee=shipping_fee,
        delivery_fee=delivery_fee,
        grand_total=grand_total,
        coupon_code=coupon_code,
        discount_amount=discount_amount,
        coupon_error=coupon_error,
        applied_coupon=applied_coupon,
        available_coupons=available_coupons,
        selected_cart_item_ids=','.join(str(i) for i in selected_ids)
    )


@app.route('/api/available-coupons')
@token_required
def api_available_coupons():
    """Return active, not-expired, under-limit coupons for the current buyer (Supabase version)."""
    try:
        now = datetime.now(timezone.utc)
        coupons = get_data('coupon', order='created_at.desc')
        if not coupons:
            coupons = []
        
        # Filter active coupons
        filtered_coupons = []
        for c in coupons:
            is_active = c.get('is_active')
            valid_from = c.get('valid_from')
            valid_until = c.get('valid_until')
            max_uses = c.get('max_uses')
            used_count = c.get('used_count', 0)
            
            if not is_active:
                continue
            
            # Check valid_from
            if valid_from:
                try:
                    if isinstance(valid_from, str):
                        valid_from = datetime.fromisoformat(valid_from.replace('Z', '+00:00'))
                    if valid_from.tzinfo is None:
                        valid_from = valid_from.replace(tzinfo=timezone.utc)
                    if valid_from > now:
                        continue
                except:
                    pass
            
            # Check valid_until
            if valid_until:
                try:
                    if isinstance(valid_until, str):
                        valid_until = datetime.fromisoformat(valid_until.replace('Z', '+00:00'))
                    if valid_until.tzinfo is None:
                        valid_until = valid_until.replace(tzinfo=timezone.utc)
                    if valid_until < now:
                        continue
                except:
                    pass
            
            # Check usage limit
            if max_uses is not None and used_count >= max_uses:
                continue
            
            filtered_coupons.append(c)
        
        return jsonify({
            'success': True,
            'coupons': [
                {
                    'id': c.get('id'),
                    'code': c.get('code'),
                    'description': c.get('description'),
                    'discount_type': c.get('discount_type'),
                    'discount_value': c.get('discount_value'),
                    'min_order_amount': c.get('min_order_amount'),
                } for c in filtered_coupons
            ]
        })
    except Exception as e:
        app.logger.error(f'/api/available-coupons error: {e}')
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/track-order/<tracking_number>')
def track_order(tracking_number):
    order = Order.query.filter_by(tracking_number=tracking_number).first()
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('index'))
    return render_template('track_order.html', order=order)


@app.route('/track-order-search', methods=['GET', 'POST'])
def track_order_search():
    if request.method == 'POST':
        tracking_number = request.form.get('tracking_number')
        return redirect(url_for('track_order', tracking_number=tracking_number))
    return render_template('track_order_search.html')

@app.route('/process-order', methods=['POST'])
@login_required
def process_order():
    try:
        if is_admin():
            flash('Admin accounts cannot place orders.', 'warning')
            return redirect(url_for('index'))
    except Exception:
        pass

    raw_ids = (request.form.get('selected_cart_item_ids') or '').strip()
    selected_ids = []
    if raw_ids:
        try:
            selected_ids = [int(x) for x in raw_ids.split(',') if x.strip().isdigit()]
        except Exception:
            selected_ids = []

    base_query = Cart.query.filter_by(user_id=session['user_id'])
    cart_items = base_query.filter(Cart.id.in_(selected_ids)).all() if selected_ids else base_query.all()
    cart_items.sort(key=lambda x: x.created_at, reverse=True)

    if not cart_items:
        flash('Please select at least one item to checkout.', 'warning')
        return redirect(url_for('cart'))

    payment_method = request.form['payment_method']
    coupon_code = request.form.get('coupon_code', '').strip()

    default_address = None
    address_id = request.form.get('address_id')
    if address_id:
        selected_address = Address.query.filter_by(id=address_id, user_id=session['user_id']).first()
        if selected_address:
            shipping_address = selected_address.full_address
            default_address = selected_address
        else:
            flash('Invalid address selected.', 'error')
            return redirect(url_for('checkout', ids=raw_ids))
    else:
        shipping_address = request.form.get('shipping_address', '')
        if not shipping_address:
            flash('Please select or enter a shipping address.', 'error')
            return redirect(url_for('checkout', ids=raw_ids))
        default_address = Address.query.filter_by(user_id=session['user_id'], is_default=True).first()

    for cart_item in cart_items:
        if getattr(cart_item.product, 'status', 'active') != 'active':
            flash(f'{cart_item.product.name} is inactive and cannot be purchased.', 'error')
            return redirect(url_for('cart'))
        available_stock = cart_item.product.stock
        if cart_item.quantity > available_stock:
            flash(f'Insufficient stock for {cart_item.product.name}. Only {available_stock} items available.', 'error')
            return redirect(url_for('cart'))

    total = sum(item.product.price * item.quantity for item in cart_items)
    
    # Calculate province-based delivery fee
    delivery_fee = 36.0  # Default (Laguna)
    if default_address and default_address.province:
        try:
            delivery_fee = calculate_delivery_fee(default_address.province)
        except Exception as e:
            app.logger.warning(f"Failed to calculate delivery fee for province {default_address.province}: {e}")
            delivery_fee = 36.0
    
    shipping_fee = 0.0  # Shipping fee is now separate from delivery fee
    discount_amount = 0.0
    applied_coupon = None

    if coupon_code:
        applied_coupon, discount_amount, coupon_error = calculate_coupon_discount(coupon_code, total)
        if coupon_error or not applied_coupon:
            flash(coupon_error or 'Invalid coupon code.', 'danger')
            return redirect(url_for('checkout'))

        if applied_coupon.discount_type == 'free_shipping' or discount_amount >= total:
            shipping_fee = 0.0

    grand_total = max(0.0, total - discount_amount + delivery_fee)

    new_order = Order(
        buyer_id=session['user_id'],
        total_amount=grand_total,
        payment_method=payment_method,
        shipping_address=shipping_address,
        status='pending',
        delivery_fee=delivery_fee,
        shipping_fee=shipping_fee
    )
    db.session.add(new_order)
    db.session.flush()

    qr_code = generate_qr_code(new_order.id)
    tracking_number = generate_tracking_number()
    batch_code = generate_batch_code()

    new_order.qr_code = qr_code
    new_order.tracking_number = tracking_number
    new_order.batch_code = batch_code
    new_order.label_generated_at = datetime.utcnow()

    try:
        # SHOPEE-STYLE: Immediately deduct stock from Product.stock
        for cart_item in cart_items:
            product = db.session.query(Product).filter_by(id=cart_item.product_id).with_for_update().first()
            
            if not product or product.stock < cart_item.quantity:
                db.session.rollback()
                flash(f'Insufficient stock for {cart_item.product.name}. Only {product.stock if product else 0} items available.', 'error')
                return redirect(url_for('cart'))
            
            # Immediately deduct stock (Shopee-style)
            product.stock = product.stock - cart_item.quantity
            
            db.session.add(OrderItem(
                order_id=new_order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price_at_time=cart_item.product.price
            ))
            
            # Broadcast stock update to all clients
            try:
                broadcast_stock_update(product.id)
            except Exception:
                pass

        new_order.stock_deducted = True

        db.session.add(OrderLabel(
            order_id=new_order.id,
            qr_code=qr_code,
            tracking_number=tracking_number,
            batch_code=batch_code,
            label_data=create_order_label_data(new_order),
            status='generated'
        ))

        if applied_coupon:
            applied_coupon.used_count = (applied_coupon.used_count or 0) + 1

        if selected_ids:
            Cart.query.filter(Cart.user_id == session['user_id'], Cart.id.in_(selected_ids)).delete(synchronize_session=False)
        else:
            Cart.query.filter_by(user_id=session['user_id']).delete()

        seller_ids = {item.product.seller_id for item in new_order.items}
        for seller_id in seller_ids:
            try:
                push_notification(
                    seller_id,
                    f'New order #{new_order.id} received!',
                    link=url_for('seller_orders'),
                    type='order',
                    order_id=new_order.id
                )
            except Exception:
                db.session.add(Notification(user_id=seller_id, message=f'New order #{new_order.id} received!', type='order'))

            first_item = new_order.items[0]
            try:
                socketio.emit('new_order', {
                    'order_id': new_order.id,
                    'created_at': new_order.created_at.isoformat(),
                    'buyer_name': f"{new_order.buyer.first_name} {new_order.buyer.last_name}",
                    'buyer_email': new_order.buyer.email,
                    'product_name': first_item.product.name,
                    'product_image': first_item.product.image_filename,
                    'quantity': first_item.quantity,
                    'unit_price': float(first_item.price_at_time),
                    'total_amount': float(new_order.total_amount),
                    'payment_method': new_order.payment_method
                }, room=f'user_{seller_id}')
            except Exception:
                pass

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Order processing failed: {str(e)}')
        flash('An error occurred while processing your order. Please try again.', 'danger')
        return redirect(url_for('cart'))

    return redirect(url_for('order_confirmation', order_id=new_order.id))

@app.route('/order-confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.filter_by(id=order_id, buyer_id=session['user_id']).first_or_404()
    # On the order confirmation page we show a custom success UI, so hide global flash alerts
    return render_template('order_confirmation.html', order=order, hide_flashes=True)


@app.route('/buyer/order/<int:order_id>')
@login_required
def buyer_order_detail(order_id):
    order = Order.query.filter_by(id=order_id, buyer_id=session['user_id']).first_or_404()
    # Calculate estimated delivery date
    estimated_delivery = order.created_at + timedelta(days=3)
    return render_template('buyer/order_detail.html', order=order, estimated_delivery=estimated_delivery)

@app.route('/cancel-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def cancel_order(order_id):
    print(f"Cancel order route accessed: order_id={order_id}, method={request.method}")
    
    # Handle GET request - show confirmation page
    if request.method == 'GET':
        order = Order.query.filter_by(id=order_id, buyer_id=session['user_id']).first()
        if not order:
            flash('Order not found.', 'danger')
            return redirect(url_for('my_orders'))
        if order.status not in ['pending', 'to_pay']:
            flash(f'Order cannot be cancelled. Current status: {order.status}', 'danger')
            return redirect(url_for('my_orders'))
        return render_template('cancel_order.html', order=order)
    
    # Handle POST request - process cancellation
    order = Order.query.filter_by(id=order_id, buyer_id=session['user_id']).first()
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('my_orders'))
    
    if order.status not in ['pending', 'to_pay']:
        flash(f'Order cannot be cancelled. Current status: {order.status}', 'danger')
        return redirect(url_for('my_orders'))
    
    # Read cancellation reasons from form (REQUIRED)
    reasons = request.form.getlist('cancel_reasons') or []
    other = (request.form.get('cancel_other') or '').strip()
    
    # Validate that at least one reason is provided
    if not reasons and not other:
        flash('Please select at least one reason before cancelling your order.', 'danger')
        return redirect(url_for('my_orders'))
    
    reason_text = ', '.join(reasons)
    if other:
        reason_text = (reason_text + (', ' if reason_text else '') + f'Other: {other}').strip(', ')
    
    # Store original status before changing it
    original_status = order.status
    
    # ⚠️ RULE 2: RETURN STOCK ONLY IF BUYER CANCELS BEFORE SELLER PROCESSES
    # Stock should only return if order was still pending/to_pay (not processed by seller yet)
    # SHOPEE RULE: Restore stock only if order was pending/to_pay/processing (not shipped/completed)
    if original_status in ['pending', 'to_pay', 'processing']:
        for item in order.items:
            product = db.session.get(Product, item.product_id)
            if product:
                product.stock += item.quantity
        db.session.flush()
        for item in order.items:
            broadcast_stock_update(item.product_id)
        app.logger.info(f'Order {order.id} cancelled: restored stock for {len(order.items)} product(s)')
    else:
        app.logger.info(f'Order {order.id} cancelled: No stock restored (order already shipped/completed)')
    
    # Persist note
    note = f"[Buyer Cancellation] {reason_text}" if reason_text else "[Buyer Cancellation]"
    order.delivery_notes = ((order.delivery_notes or '') + f"\n{datetime.utcnow().isoformat()} {note}").strip()
    order.status = 'cancelled'
    order.updated_at = datetime.utcnow()
    
    db.session.commit()
        
    
    # Notify buyer (self) and sellers
    push_notification(order.buyer_id, f'Your order #{order.id} has been cancelled successfully.')
    for sid in _order_seller_ids(order):
        push_notification(sid, f'Order #{order.id} was cancelled by the buyer.')
    
    # Emit real-time cancellation event to seller's Socket.IO room
    try:
        socketio.emit('order_cancelled', {
            'order_id': order.id,
            'buyer_id': order.buyer_id,
            'message': f'Order #{order.id} has been cancelled by buyer'
        }, room='sellers')
    except Exception:
        pass
    
    flash('Your order has been cancelled successfully.', 'success')
    return redirect(url_for('my_orders', tab='cancelled'))


@app.route('/api/qr-scan', methods=['POST'])
def api_qr_scan():
    """API endpoint for Android app QR scanning (Supabase version)."""
    try:
        data = request.get_json()
        qr_code = data.get('qr_code')
        scan_type = data.get('scan_type')  # packing, pickup, delivery, return
        rider_id = data.get('rider_id')
        scan_notes = data.get('scan_notes', '')
        
        if not qr_code or not scan_type:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        order_labels = get_data('order_label', filters={'qr_code': qr_code})
        if not order_labels or len(order_labels) == 0:
            return jsonify({'success': False, 'message': 'QR Code not found'}), 404
        
        order_label = order_labels[0]
        order_id = order_label.get('order_id')
        
        order = get_data_by_id('order', order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        # Update order label status based on scan type
        now = datetime.utcnow().isoformat()
        update_data = {}
        
        if scan_type == 'packing':
            update_data['status'] = 'packed'
            update_data['packed_at'] = now
            update_data['packed_by'] = rider_id
            update_data['shipping_notes'] = scan_notes
        elif scan_type == 'pickup':
            update_data['status'] = 'picked_up'
            update_data['picked_up_at'] = now
            update_data['picked_up_by'] = rider_id
        elif scan_type == 'delivery':
            update_data['status'] = 'delivered'
            update_data['delivered_at'] = now
            update_data['delivered_by'] = rider_id
            update_data['delivery_notes'] = scan_notes
        elif scan_type == 'return':
            update_data['status'] = 'returned'
            update_data['returned_at'] = now
            update_data['returned_by'] = rider_id
            update_data['return_notes'] = scan_notes
        
        if update_data:
            updated = update_data_by_id('order_label', order_label.get('id'), update_data)
            if updated:
                order_label = updated
        
        # Log the scan
        scan_log_data = {
            'order_id': order.get('id'),
            'order_label_id': order_label.get('id'),
            'qr_code': qr_code,
            'scanned_by': rider_id,
            'scan_type': scan_type,
            'scan_notes': scan_notes,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'created_at': now
        }
        insert_data('qr_scan_log', scan_log_data)
        
        # Get buyer info
        buyer = get_data_by_id('user', order.get('buyer_id'))
        customer_name = f"{buyer.get('first_name', '')} {buyer.get('last_name', '')}".strip() if buyer else 'Unknown'
        customer_phone = buyer.get('phone', '') if buyer else ''
        
        return jsonify({
            'success': True,
            'message': f'QR Code scanned successfully! Status updated to {scan_type}',
            'order_id': order.get('id'),
            'order_status': order_label.get('status'),
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'shipping_address': order.get('shipping_address')
        })
        
    except Exception as e:
        app.logger.error(f'/api/qr-scan error: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/qr-info/<qr_code>')
def api_qr_info(qr_code):
    """API endpoint to get QR code information for Android app (Supabase version)."""
    try:
        order_labels = get_data('order_label', filters={'qr_code': qr_code})
        if not order_labels or len(order_labels) == 0:
            return jsonify({'success': False, 'message': 'QR Code not found'}), 404
        
        order_label = order_labels[0]
        order_id = order_label.get('order_id')
        
        order = get_data_by_id('order', order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        # Get buyer info
        buyer = get_data_by_id('user', order.get('buyer_id'))
        customer_name = f"{buyer.get('first_name', '')} {buyer.get('last_name', '')}".strip() if buyer else 'Unknown'
        customer_phone = buyer.get('phone', '') if buyer else ''
        
        # Get order items
        order_items = get_data('order_item', filters={'order_id': order_id})
        if not order_items:
            order_items = []
        
        items = []
        for item in order_items:
            product = get_data_by_id('product', item.get('product_id'))
            if product:
                seller = get_data_by_id('user', product.get('seller_id'))
                seller_name = f"{seller.get('first_name', '')} {seller.get('last_name', '')}".strip() if seller else 'Unknown'
                
                items.append({
                    'product_name': product.get('name', ''),
                    'quantity': item.get('quantity', 0),
                    'price': float(item.get('price_at_time', 0)),
                    'seller_name': seller_name
                })
        
        return jsonify({
            'success': True,
            'order_id': order.get('id'),
            'tracking_number': order.get('tracking_number'),
            'status': order_label.get('status'),
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'shipping_address': order.get('shipping_address'),
            'total_amount': float(order.get('total_amount', 0)),
            'payment_method': order.get('payment_method'),
            'order_date': order.get('created_at'),
        'created_at': order.get('created_at'),
            'items': items
        })
        
    except Exception as e:
        app.logger.error(f'/api/qr-info error: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/qr-scan', methods=['GET', 'POST'])
@admin_required
def admin_qr_scan():
    """Admin QR code scanning interface"""
    if request.method == 'POST':
        qr_code = request.form.get('qr_code')
        scan_type = request.form.get('scan_type')
        scan_notes = request.form.get('scan_notes', '')
        
        order_label = OrderLabel.query.filter_by(qr_code=qr_code).first()
        if not order_label:
            flash('QR Code not found!', 'error')
            return redirect(url_for('admin_qr_scan'))
        
        # Update order label status based on scan type
        if scan_type == 'packing':
            order_label.status = 'packed'
            order_label.packed_at = datetime.utcnow()
            order_label.packed_by = session['user_id']
            order_label.shipping_notes = scan_notes
        elif scan_type == 'pickup':
            order_label.status = 'picked_up'
            order_label.picked_up_at = datetime.utcnow()
            order_label.picked_up_by = session['user_id']
        elif scan_type == 'delivery':
            order_label.status = 'delivered'
            order_label.delivered_at = datetime.utcnow()
            order_label.delivered_by = session['user_id']
            order_label.delivery_notes = scan_notes
        elif scan_type == 'return':
            order_label.status = 'returned'
            order_label.returned_at = datetime.utcnow()
            order_label.returned_by = session['user_id']
            order_label.return_notes = scan_notes
        
        # Log the scan
        scan_log = QRScanLog(
            order_id=order_label.order_id,
            order_label_id=order_label.id,
            qr_code=qr_code,
            scanned_by=session['user_id'],
            scan_type=scan_type,
            scan_notes=scan_notes,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(scan_log)
        db.session.commit()
        
        flash(f'QR Code scanned successfully! Status updated to {scan_type}.', 'success')
        return redirect(url_for('admin_qr_scan'))
    
    return render_template('admin/qr_scan.html')

@app.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def admin_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        if name and not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
            db.session.commit()
            flash('Category added!', 'success')
        else:
            flash('Category already exists or invalid.', 'error')
    categories = Category.query.order_by(Category.name).all()
    badge_counts = get_admin_badge_counts()
    return render_template('admin/categories.html', 
                         categories=categories, 
                         now=datetime.utcnow,
                         **badge_counts)

@app.route('/admin/categories/activate/<int:category_id>', methods=['POST'])
@admin_required
def activate_category(category_id):
    category = Category.query.get_or_404(category_id)
    category.status = 'active'
    db.session.commit()
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'status': 'active',
            'message': 'Category set to active.'
        })
    
    flash('Category set to active.', 'success')
    return redirect(url_for('admin_categories'))


@app.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
@admin_required
def soft_delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    category.status = 'inactive'
    db.session.commit()
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'status': 'inactive',
            'message': 'Category set to inactive.'
        })
    
    flash('Category set to inactive.', 'info')
    return redirect(url_for('admin_categories'))

# --- CATEGORY EDIT / PERMANENT DELETE ROUTES ---
@app.route('/admin/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    """
    Simple edit view for categories. GET shows a small edit form (rendered inline)
    POST updates name/description/status and optionally processes an uploaded cover image.
    """
    category = Category.query.get_or_404(category_id)

    if request.method == 'POST':
        # Basic fields
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', category.status)

        if name:
            category.name = name
        category.description = description
        category.status = status

        # Optional cover image upload (same processing as update_category_cover)
        file = request.files.get('cover_image')
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Invalid cover file type. Use JPG or PNG.', 'danger')
                return redirect(url_for('edit_category', category_id=category.id))

            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'categories')
            os.makedirs(upload_dir, exist_ok=True)
            try:
                img = Image.open(file.stream).convert('RGB')
                target_w, target_h = 1000, 150
                img_w, img_h = img.size
                target_ratio = target_w / target_h
                img_ratio = img_w / img_h

                if img_ratio > target_ratio:
                    new_w = int(target_ratio * img_h)
                    left = (img_w - new_w) // 2
                    img = img.crop((left, 0, left + new_w, img_h))
                else:
                    new_h = int(img_w / target_ratio)
                    top = (img_h - new_h) // 2
                    img = img.crop((0, top, img_w, top + new_h))

                img = img.resize((target_w, target_h), Image.LANCZOS)

                filename = f"cat_{category_id}_{int(time.time())}.jpg"
                filepath = os.path.join(upload_dir, filename)
                img.save(filepath, format='JPEG', quality=85)

                # remove old file if exists
                old = category.cover_image_filename
                if old:
                    try:
                        old_path = os.path.join(upload_dir, old)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except Exception:
                        app.logger.exception("Failed to remove old category cover")

                category.cover_image_filename = filename
            except Exception:
                app.logger.exception("Failed processing uploaded category cover")
                flash('Failed to process uploaded image.', 'danger')
                return redirect(url_for('edit_category', category_id=category.id))

        db.session.commit()
        flash('Category updated successfully.', 'success')
        return redirect(url_for('admin_categories'))

    # GET -> show small inline edit page using the same base layout
    # Keeps UI consistent without requiring a new template file.
    return render_template_string("""
    {% extends "base.html" %}
    {% block title %}Edit Category - {{ category.name }}{% endblock %}
    {% block content %}
    <div class="container py-4">
      <div class="card shadow-sm">
        <div class="card-header">
          <h5 class="mb-0">Edit Category: {{ category.name }}</h5>
        </div>
        <div class="card-body">
          <form method="POST" enctype="multipart/form-data">
            <div class="mb-3">
              <label class="form-label">Name</label>
              <input class="form-control" name="name" value="{{ category.name }}" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea class="form-control" name="description" rows="3">{{ category.description or '' }}</textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Status</label>
              <select class="form-select" name="status">
                <option value="active" {% if category.status == 'active' %}selected{% endif %}>Active</option>
                <option value="inactive" {% if category.status != 'active' %}selected{% endif %}>Inactive</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Cover Image (optional, recommended 1000Ã—150)</label>
              <input type="file" name="cover_image" accept="image/png,image/jpeg" class="form-control">
              <div class="form-text">If provided, this will overwrite the current cover.</div>
            </div>

            <div class="d-flex gap-2">
              <button class="btn btn-primary" type="submit">Save changes</button>
              <a href="{{ url_for('admin_categories') }}" class="btn btn-secondary">Back to Categories</a>
            </div>
          </form>
        </div>
      </div>
    </div>
    {% endblock %}
    """, category=category)


@app.route('/admin/categories/delete-permanent/<int:category_id>', methods=['POST'], endpoint='delete_category')
@admin_required
def delete_category(category_id):
    """
    Permanently delete a category (this is the endpoint your template expects:
    url_for('delete_category', category_id=...)). This will remove the DB row
    and associated cover file if present.
    """
    category = Category.query.get_or_404(category_id)
    # Remove cover image from disk if present
    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'categories')
    old = category.cover_image_filename
    try:
        if old:
            old_path = os.path.join(upload_dir, old)
            if os.path.exists(old_path):
                os.remove(old_path)
    except Exception:
        app.logger.exception("Failed to remove category cover while deleting category")

    # Optionally: you might want to reassign or delete related subcategories/products first.
    # For now, attempt to delete row and commit (will fail if FK constraints prevent deletion).
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category permanently deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.exception("Failed to permanently delete category: %s", e)
        flash('Failed to delete category. Make sure there are no dependent records (products/subcategories).', 'danger')

    return redirect(url_for('admin_categories'))

@app.route('/admin/category/<int:category_id>/update-cover', methods=['POST'])
@admin_required
def update_category_cover(category_id):
    category = Category.query.get_or_404(category_id)
    file = request.files.get('cover_image')
    if not file or not file.filename:
        flash('No file selected.', 'warning')
        return redirect(url_for('admin_categories'))

    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload JPG or PNG.', 'danger')
        return redirect(url_for('admin_categories'))

    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'categories')
    os.makedirs(upload_dir, exist_ok=True)

    try:
        img = Image.open(file.stream).convert('RGB')
        target_w, target_h = 1000, 150
        img_w, img_h = img.size
        target_ratio = target_w / target_h
        img_ratio = img_w / img_h

        if img_ratio > target_ratio:
            new_w = int(target_ratio * img_h)
            left = (img_w - new_w) // 2
            img = img.crop((left, 0, left + new_w, img_h))
        else:
            new_h = int(img_w / target_ratio)
            top = (img_h - new_h) // 2
            img = img.crop((0, top, img_w, top + new_h))

        img = img.resize((target_w, target_h), Image.LANCZOS)

        ext = 'jpg'
        base = secure_filename(category.name.replace(' ', '_').lower())[:50]
        filename = f"cat_{category_id}_{int(time.time())}.{ext}"
        filepath = os.path.join(upload_dir, filename)
        img.save(filepath, format='JPEG', quality=85)

        # remove old file if exists
        old = category.cover_image_filename
        if old:
            try:
                old_path = os.path.join(upload_dir, old)
                if os.path.exists(old_path):
                    os.remove(old_path)
            except Exception:
                app.logger.exception("Failed to remove old category cover")

        category.cover_image_filename = filename
        db.session.commit()
        flash('Category cover updated.', 'success')
    except Exception as e:
        app.logger.exception("Error saving category cover")
        flash('Failed to save cover image. Try again.', 'error')

    return redirect(url_for('admin_categories'))



@app.route('/admin/theme-settings', methods=['GET', 'POST'])
@admin_required
def theme_settings():
    theme = ThemeSetting.query.first()
    # If theme row doesn't exist, create one!
    if theme is None:
        theme = ThemeSetting(
            site_name="Kids & Baby Store",
            primary_color="#0066ff",
            secondary_color="#59b5fc",
            footer_color="#232323"
        )
        db.session.add(theme)
        db.session.commit()
    if request.method == 'POST':
        # Handle logo upload
        file = request.files.get('logo')
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            theme.logo_filename = filename

        theme.site_name = request.form.get('site_name', theme.site_name)
        theme.primary_color = request.form.get('primary_color', theme.primary_color)
        theme.secondary_color = request.form.get('secondary_color', theme.secondary_color)
        theme.footer_color = request.form.get('footer_color', theme.footer_color)
        db.session.commit()
        flash('Theme updated!', 'success')
        return redirect(url_for('theme_settings'))
    badge_counts = get_admin_badge_counts()
    return render_template('admin/theme_settings.html', theme=theme, **badge_counts)

@app.route('/admin/toggle-new-arrival/<int:product_id>', methods=['POST'])
@admin_required
def admin_toggle_new_arrival(product_id):
    product = Product.query.get_or_404(product_id)
    product.show_in_new_arrival = not bool(product.show_in_new_arrival)
    db.session.commit()
    flash(f'Updated New Arrival status for "{product.name}".', 'success')
    return redirect(request.referrer or url_for('admin_products'))


@app.route('/seller/print-label/<int:order_id>')
@seller_required
def seller_print_label(order_id):
    """Print shipping label for seller"""
    order = Order.query.get_or_404(order_id)
    order_label = OrderLabel.query.filter_by(order_id=order_id).first()
    
    if not order_label:
        flash('Order label not found!', 'error')
        return redirect(url_for('seller_orders'))
    
    # Check if seller has products in this order
    seller_has_products = any(item.product.seller_id == session['user_id'] for item in order.items)
    if not seller_has_products:
        flash('You are not authorized to view this order.', 'error')
        return redirect(url_for('seller_orders'))
    
    # Get seller's application information
    seller_app = SellerApplication.query.filter_by(user_id=session['user_id'], status='approved').first()
    
    # Generate QR code image
    qr_image = create_qr_image(order_label.qr_code)
    
    return render_template('seller/print_label.html', 
                         order=order, 
                         order_label=order_label,
                         qr_image=qr_image,
                         seller_app=seller_app)

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    data = request.json
    
    # PayMongo checkout session creation
    headers = {
        'Authorization': f'Basic {PAYMONGO_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'data': {
            'attributes': {
                'amount': int(data['amount'] * 100),  # Convert to centavos
                'currency': 'PHP',
                'description': f'Order from Kids & Baby Store',
                'line_items': data['line_items'],
                'payment_method_types': ['card', 'gcash', 'paymaya'],
                'success_url': request.url_root + f'payment-success?order_id={data["order_id"]}',
                'cancel_url': request.url_root + 'cart'
            }
        }
    }
    
    try:
        response = requests.post(
            'https://api.paymongo.com/v1/checkout_sessions',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            checkout_data = response.json()
            return jsonify({'success': True, 'checkout_url': checkout_data['data']['attributes']['checkout_url']})
        else:
            return jsonify({'success': False, 'error': 'Payment session creation failed'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})



@app.route('/payment-success')
@login_required
def payment_success():
    order_id = request.args.get('order_id')
    if order_id:
        order = Order.query.filter_by(id=order_id, buyer_id=session['user_id']).first()
        if order:
            order.payment_status = 'paid'
            db.session.commit()
            flash('Payment successful! Your order is confirmed.', 'success')
        return redirect(url_for('order_confirmation', order_id=order_id))
    return redirect(url_for('index'))

@app.route('/update-cart', methods=['POST'])
@login_required
def update_cart():
    data = request.json
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    cart_item = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    
    if cart_item:
        if quantity > 0:
            cart_item.quantity = quantity
        else:
            db.session.delete(cart_item)
        
        db.session.commit()
        
        # Calculate new totals
        cart_items = Cart.query.filter_by(user_id=session['user_id']).order_by(Cart.created_at.desc()).all()
        total = sum(item.product.price * item.quantity for item in cart_items)
        cart_count = len(cart_items)
        # --- START: Add item_total for this cart item ---
        item_total = cart_item.product.price * cart_item.quantity if quantity > 0 else 0
        # --- END ---
        return jsonify({
            'success': True,
            'total': total,
            'cart_count': cart_count,
            'item_total': item_total  # Added for per-item price update
        })
    
    return jsonify({'success': False})

@app.route('/remove-from-cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).delete()
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))

@app.route('/update-cart-quantity', methods=['POST'])
@login_required
def update_cart_quantity():
    data = request.get_json()
    cart_item_id = data.get('cart_item_id')
    new_quantity = data.get('quantity')
    
    if not cart_item_id or not new_quantity:
        return jsonify({'success': False, 'message': 'Invalid data'})
    
    # Get the cart item
    cart_item = Cart.query.filter_by(id=cart_item_id, user_id=session['user_id']).first()
    
    if not cart_item:
        return jsonify({'success': False, 'message': 'Cart item not found'})
    
    # Check if quantity is valid
    if new_quantity < 1:
        return jsonify({'success': False, 'message': 'Quantity must be at least 1'})
    
    # Check available stock (considering reserved orders)
    available_stock = get_available_stock(cart_item.product_id)
    if new_quantity > available_stock:
        return jsonify({'success': False, 'message': f'Only {available_stock} items available in stock'})
    
    # Update quantity
    cart_item.quantity = new_quantity
    db.session.commit()
    
    # Calculate totals
    item_total = cart_item.product.price * new_quantity
    cart_total = sum(item.product.price * item.quantity for item in Cart.query.filter_by(user_id=session['user_id']).order_by(Cart.created_at.desc()).all())
    
    return jsonify({
        'success': True,
        'item_total': item_total,
        'cart_total': cart_total,
        'max_stock': available_stock
    })

@app.route('/remove-from-cart', methods=['POST'])
@login_required
def remove_from_cart_ajax():
    data = request.get_json()
    cart_item_id = data.get('cart_item_id')
    
    if not cart_item_id:
        return jsonify({'success': False, 'message': 'Invalid data'})
    
    # Get the cart item
    cart_item = Cart.query.filter_by(id=cart_item_id, user_id=session['user_id']).first()
    
    if not cart_item:
        return jsonify({'success': False, 'message': 'Cart item not found'})
    
    # Remove the item
    db.session.delete(cart_item)
    db.session.commit()
    
    # Calculate new cart total
    cart_total = sum(item.product.price * item.quantity for item in Cart.query.filter_by(user_id=session['user_id']).order_by(Cart.created_at.desc()).all())
    
    return jsonify({
        'success': True,
        'cart_total': cart_total
    })

@app.route('/update-order-status/<int:order_id>/<status>')
@seller_required
def update_order_status(order_id, status):
    order = Order.query.get_or_404(order_id)
    
    # Check if seller owns any products in this order
    seller_products = [item.product_id for item in order.items if item.product.seller_id == session['user_id']]
    
    if not seller_products:
        return redirect(url_for('seller_orders'))

# Prevent seller updates once a rider has accepted/picked up the order
    if order.status in ['to_ship', 'in_transit', 'delivered']:
        flash('This order is now handled by a rider and can no longer be updated by the seller.', 'warning')
        return redirect(url_for('seller_orders'))

    # Only allow 'processing' and 'ready_for_pickup' on seller side
    valid_statuses = ['processing', 'ready_for_pickup']
    if status not in valid_statuses:
        flash('Invalid status for seller. Use "Confirm" then "Ready to Pick Up".', 'error')
        return redirect(url_for('seller_orders'))

    order.status = status
    order.updated_at = datetime.utcnow()

    # Notify buyer based on status
    if status == 'processing':
        try:
            push_notification(order.buyer_id, f'Your order #{order.id} is processing.')
        except Exception:
            db.session.add(Notification(user_id=order.buyer_id, message=f'Your order #{order.id} is processing.'))
    elif status == 'ready_for_pickup':
        # Show out-for-delivery message instead of ready-for-pickup
        msg = f'Your order #{order.id} is out for delivery.'
        db.session.add(Notification(user_id=order.buyer_id, message=msg))
        try:
            socketio.emit('order_available', {
                'order_id': order.id,
                'total_amount': order.total_amount,
                'seller_ids': list({it.product.seller_id for it in order.items})
            }, room='riders')
        except Exception:
            pass

    db.session.commit()
    try:
        _emit_seller_stats_update(session['user_id'])
    except Exception:
        pass
    flash(f'Order status updated to {status}.', 'success')
    return redirect(url_for('seller_orders'))

@app.route('/seller/confirm-order/<int:order_id>')
@seller_required
def seller_confirm_order(order_id):
    """Seller confirms order. Reserve stock implicitly; real stock is deducted upon delivery."""
    order = Order.query.get_or_404(order_id)

    # Check if seller owns any products in this order
    seller_products = [item for item in order.items if item.product.seller_id == session['user_id']]

    if not seller_products:
        flash('You are not authorized to confirm this order.', 'error')
        return redirect(url_for('seller_orders'))

    if order.status != 'pending':
        flash('Order is not in pending status.', 'error')
        return redirect(url_for('seller_orders'))

    try:
        # Handle stock management - stock is now automatically reserved when orders are placed
        # No need to auto-increase stock when confirming orders

        # Update order status only
        order.status = 'processing'
        db.session.commit()
        

        push_notification(order.buyer_id, f'Your order is now being processed.')
        flash('Order confirmed successfully. Preparing for pickup.', 'success')

        # Update seller stats panel
        _emit_seller_stats_update(session['user_id'])
    except Exception:
        db.session.rollback()
        flash('Error confirming order. Please try again.', 'error')

    return redirect(url_for('seller_orders'))

@app.route('/seller/order/<int:order_id>/process', methods=['POST'])
@seller_required
def seller_process_order(order_id):
    """Seller processes an order (moves from pending to processing)."""
    order = Order.query.get_or_404(order_id)
    
    # Check if seller owns any products in this order
    seller_products = [item for item in order.items if item.product.seller_id == session['user_id']]
    
    if not seller_products:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'You are not authorized to process this order.'})
        flash('You are not authorized to process this order.', 'error')
        return redirect(url_for('seller_orders'))
    
    if order.status != 'pending':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Order must be pending to be processed.'})
        flash('Order must be pending to be processed.', 'error')
        return redirect(url_for('seller_orders'))
    
    try:
        # Update order status
        order.status = 'processing'
        order.updated_at = datetime.utcnow()

        # Handle stock management - stock is now automatically reserved when orders are placed
        # No need to auto-increase stock when processing orders

        # Mark as seen by seller (remove from new orders)
        seen_record = SellerOrderSeen.query.filter_by(seller_id=session['user_id'], order_id=order.id).first()
        if not seen_record:
            try:
                db.session.add(SellerOrderSeen(seller_id=session['user_id'], order_id=order.id))
                db.session.flush()
            except Exception:
                db.session.rollback()
                pass

        db.session.commit()
        

        # Notify buyer
        try:
            push_notification(order.buyer_id, f'Your order #{order.id} is now being processed.')
        except Exception:
            db.session.add(Notification(user_id=order.buyer_id, message=f'Your order #{order.id} is now being processed.'))

        # Update seller stats
        try:
            _emit_seller_stats_update(session['user_id'])
        except Exception:
            pass
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Order processed successfully.'})
        
        flash('Order processed successfully.', 'success')
        return redirect(url_for('seller_orders'))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'seller_process_order error for order {order_id}: {e}')
        import traceback
        app.logger.error(traceback.format_exc())
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': f'Error processing order: {str(e)}'})
        flash(f'Error processing order: {str(e)}', 'error')
        return redirect(url_for('seller_orders'))

@app.route('/seller/order/<int:order_id>/ready-for-pickup', methods=['POST'])
@seller_required
def seller_ready_for_pickup(order_id):
    """Seller marks an order ready for pickup. Broadcasts to available riders only."""
    order = Order.query.get_or_404(order_id)

    # Check if seller owns any products in this order
    seller_id = session['user_id']
    seller_products = [item for item in order.items if item.product.seller_id == seller_id]
    if not seller_products:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'You are not authorized to mark this order as ready for pickup.'})
        flash('You are not authorized to mark this order as ready for pickup.', 'error')
        return redirect(url_for('seller_orders'))

    # Only from pending/processing
    if order.status not in ['pending', 'processing']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Order must be pending/processing before marking as ready.'})
        flash('Order must be pending/processing before marking as ready.', 'error')
        return redirect(url_for('seller_orders'))

    order.status = 'ready_for_pickup'
    order.packed_at = datetime.utcnow()
    order.packed_by = seller_id
    
    # Handle stock management - add requested quantity to available stock if needed
    for item in seller_products:
        current_stock = item.product.stock
        requested_quantity = item.quantity
        
        # If requested quantity exceeds current stock, add the difference to available stock
        if requested_quantity > current_stock:
            stock_to_add = requested_quantity - current_stock
            item.product.stock += stock_to_add
            
            # Log the stock addition for reference
            print(f"Added {stock_to_add} units to product {item.product.name} (ID: {item.product.id}) - New stock: {item.product.stock}")
    
    db.session.commit()
        

    # Notify buyer and broadcast to available riders (buyer sees out-for-delivery)
    push_notification(order.buyer_id, f'Your order #{order.id} is out for delivery.')
    try:
        available = User.query.filter(User.role == 'rider', User.status == 'active').all()
        payload = {
            'order_id': order.id,
            'total_amount': order.total_amount,
            'seller_id': seller_id
        }
        for r in available:
            socketio.emit('order_available', payload, room=f'user_{r.id}')
        _emit_seller_stats_update(seller_id)
    except Exception:
        pass

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Order marked ready for pickup.'})
    
    flash('Order marked ready for pickup.', 'success')
    return redirect(url_for('seller_orders'))

@app.route('/seller/cancel-order/<int:order_id>')
@seller_required
def seller_cancel_order(order_id):
    """Disabled: cancellation is rider-only per system rules."""
    flash('Cancellation is handled by riders. Please coordinate with the assigned rider or admin.', 'warning')
    return redirect(url_for('seller_orders'))

# PHASE 4: Return and Refund Flow Routes

@app.route('/buyer/order/<int:order_id>/request-return', methods=['POST'])
@login_required
def buyer_request_return(order_id):
    """Buyer requests a return for an order. Updates order status to return_requested."""
    order = Order.query.get_or_404(order_id)
    
    # Verify buyer owns this order
    if order.buyer_id != session['user_id']:
        flash('You are not authorized to request a return for this order.', 'error')
        return redirect(url_for('my_orders'))
    
    # Only completed or delivered orders can be returned
    if order.status not in ['completed', 'delivered']:
        flash('Only completed or delivered orders can be returned.', 'error')
        return redirect(url_for('my_orders'))
    
    return_reason = request.form.get('return_reason', '').strip()
    if not return_reason:
        flash('Please provide a reason for the return.', 'error')
        return redirect(url_for('my_orders'))
    
    # Update order status and save return reason
    order.status = 'return_requested'
    order.return_reason = return_reason
    order.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Notify all sellers in this order
    for item in order.items:
        if item.product.seller_id != session['user_id']:
            try:
                push_notification(item.product.seller_id, f'Buyer requested return for order #{order.id}. Reason: {return_reason}')
            except Exception:
                db.session.add(Notification(user_id=item.product.seller_id, message=f'Buyer requested return for order #{order.id}. Reason: {return_reason}'))
    
    db.session.commit()
    flash('Return request submitted. Sellers will review your request.', 'info')
    return redirect(url_for('my_orders'))

@app.route('/seller/order/<int:order_id>/approve-return', methods=['POST'])
@seller_required
def seller_approve_return(order_id):
    """Seller approves a return request. Updates status to return_ready_for_pickup and resets rider_id."""
    order = Order.query.get_or_404(order_id)
    
    # Check if seller owns any products in this order
    seller_products = [item for item in order.items if item.product.seller_id == session['user_id']]
    if not seller_products:
        flash('You are not authorized to approve returns for this order.', 'error')
        return redirect(url_for('seller_orders'))
    
    # Only return_requested orders can be approved
    if order.status != 'return_requested':
        flash('Order is not in return_requested status.', 'error')
        return redirect(url_for('seller_orders'))
    
    # Update order status and reset rider for return pickup
    order.status = 'return_ready_for_pickup'
    order.rider_id = None  # Reset rider for first-come-first-serve return pickup
    order.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Notify buyer
    try:
        push_notification(order.buyer_id, f'Your return request for order #{order.id} has been approved. A rider will pick up the item.')
    except Exception:
        db.session.add(Notification(user_id=order.buyer_id, message=f'Your return request for order #{order.id} has been approved. A rider will pick up the item.'))
    
    # Broadcast to available riders for return pickup
    try:
        from sqlalchemy import or_
        available = User.query.filter(User.role == 'rider', User.status == 'active').all()
        payload = {
            'order_id': order.id,
            'type': 'return_pickup',
            'total_amount': order.total_amount
        }
        for r in available:
            socketio.emit('return_pickup_available', payload, room=f'user_{r.id}')
    except Exception:
        pass
    
    db.session.commit()
    flash('Return approved. Rider will pick up the item from the buyer.', 'success')
    return redirect(url_for('seller_orders'))

@app.route('/rider/order/<int:order_id>/accept-return', methods=['POST'])
@login_required
@rider_required
def rider_accept_return(order_id):
    """Rider accepts a return pickup. Uses same race condition prevention as regular orders."""
    # Race condition prevention: check status and rider_id in one query
    order = Order.query.filter_by(id=order_id, status='return_ready_for_pickup', rider_id=None).first()
    
    if not order:
        flash('This return pickup has already been accepted by another rider.', 'error')
        return redirect(url_for('rider_dashboard'))
    
    # Assign rider and update status atomically
    order.rider_id = session['user_id']
    order.status = 'return_accepted_by_rider'
    order.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Notify buyer and sellers
    try:
        push_notification(order.buyer_id, f'Rider accepted return pickup for order #{order.id}.')
    except Exception:
        db.session.add(Notification(user_id=order.buyer_id, message=f'Rider accepted return pickup for order #{order.id}.'))
    
    for item in order.items:
        if item.product.seller_id != session['user_id']:
            try:
                push_notification(item.product.seller_id, f'Rider accepted return pickup for order #{order.id}.')
            except Exception:
                db.session.add(Notification(user_id=item.product.seller_id, message=f'Rider accepted return pickup for order #{order.id}.'))
    
    # Broadcast to all riders that return pickup is taken
    socketio.emit('return_pickup_taken', {'order_id': order.id}, broadcast=True)
    
    db.session.commit()
    flash('Return pickup accepted.', 'success')
    return redirect(url_for('rider_dashboard'))

@app.route('/rider/order/<int:order_id>/complete-return', methods=['POST'])
@login_required
@rider_required
def rider_complete_return(order_id):
    """Rider marks return as delivered back to seller."""
    order = Order.query.get_or_404(order_id)
    
    # Verify this rider is assigned
    if order.rider_id != session['user_id']:
        flash('You are not assigned to this return.', 'error')
        return redirect(url_for('rider_dashboard'))
    
    # Only return_accepted_by_rider or return_in_transit can be completed
    if order.status not in ['return_accepted_by_rider', 'return_in_transit']:
        flash('Return is not in the correct status to complete.', 'error')
        return redirect(url_for('rider_dashboard'))
    
    # Update order status
    order.status = 'return_delivered'
    order.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Notify seller
    for item in order.items:
        try:
            push_notification(item.product.seller_id, f'Returned item for order #{order.id} has been delivered back to you.')
        except Exception:
            db.session.add(Notification(user_id=item.product.seller_id, message=f'Returned item for order #{order.id} has been delivered back to you.'))
    
    db.session.commit()
    flash('Return completed. Item delivered back to seller.', 'success')
    return redirect(url_for('rider_dashboard'))

@app.route('/seller/order/<int:order_id>/refund', methods=['POST'])
@seller_required
def seller_refund_order(order_id):
    """Seller processes refund after item is returned."""
    order = Order.query.get_or_404(order_id)
    
    # Check if seller owns any products in this order
    seller_products = [item for item in order.items if item.product.seller_id == session['user_id']]
    if not seller_products:
        flash('You are not authorized to refund this order.', 'error')
        return redirect(url_for('seller_orders'))
    
    # Only return_delivered orders can be refunded
    if order.status != 'return_delivered':
        flash('Order must be return_delivered before refunding.', 'error')
        return redirect(url_for('seller_orders'))
    
    # Update order status and payment status
    order.status = 'refunded'
    order.payment_status = 'refunded'
    order.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Notify buyer
    try:
        push_notification(order.buyer_id, f'Your refund for order #{order.id} has been processed.')
    except Exception:
        db.session.add(Notification(user_id=order.buyer_id, message=f'Your refund for order #{order.id} has been processed.'))
    
    db.session.commit()
    flash('Refund processed successfully.', 'success')
    return redirect(url_for('seller_orders'))

@app.route('/seller/add-tracking/<int:order_id>')
@seller_required
def add_tracking_number(order_id):
    """Disabled: tracking and delivery are handled by riders in the new workflow."""
    flash('Tracking and delivery are handled by riders. Use "Ready to Pick Up" and let riders handle pickup and delivery.', 'info')
    return redirect(url_for('seller_orders'))

@app.route('/profile')
@login_required
def profile():
    user = db.session.query(User).options(joinedload(User.addresses)).filter_by(id=session['user_id']).first()
    active_role = session.get('active_role', user.role)
    
    if user.role == 'admin':
        return redirect(url_for('admin_profile'))
    elif active_role == 'seller':
        return redirect(url_for('seller_profile'))
    elif user.role == 'rider' or active_role == 'rider':
        return redirect(url_for('rider_dashboard'))
    else:
        # Buyer profile
        addresses = Address.query.filter_by(user_id=session['user_id']).all()
        return render_template('buyer/buyer_profile.html', user=user, addresses=addresses)

@app.route('/buyer-profile')
@login_required
def buyer_profile():
    user = db.session.get(User, session['user_id'])
    addresses = Address.query.filter_by(user_id=session['user_id']).all()
    return render_template('buyer/buyer_profile.html', user=user, addresses=addresses)

@app.route('/buyer/order/<int:order_id>/received', methods=['POST'])
@login_required
def buyer_confirm_received(order_id):
    """Buyer taps 'Order Received' -> status completed and release commissions."""
    order = Order.query.get_or_404(order_id)
    if order.buyer_id != session['user_id']:
        flash('You are not allowed to confirm this order.', 'error')
        return redirect(url_for('dashboard'))
    if order.status != 'delivered':
        flash('Order must be delivered before confirmation.', 'warning')
        return redirect(url_for('dashboard'))

    order.status = 'completed'
    order.updated_at = datetime.utcnow()
    db.session.commit()
        

    # Release commissions and notify
    _release_commissions(order)
    push_notification(order.buyer_id, f'Thank you! Order #{order.id} marked as received.')
    for sid in _order_seller_ids(order):
        push_notification(sid, f'Order #{order.id} completed. Commission released.')
        _emit_seller_stats_update(sid)
    if order.picked_up_by:
        push_notification(order.picked_up_by, f'Order #{order.id} completed. Commission released.')

    # Optional: notify admins as well
    for a in _admins():
        admin_id = _entity_id(a)
        if admin_id:
            push_notification(admin_id, f'Order #{order.id} completed by buyer. Commissions released.')

    flash('Order confirmed. Thank you!', 'success')
    return redirect(url_for('my_orders'))

@app.route('/seller-profile')
@seller_required
def seller_profile():
    user = db.session.get(User, session['user_id'])
    seller_app = SellerApplication.query.filter_by(user_id=session['user_id'], status='approved').first()
    
    # Get seller statistics
    total_products = Product.query.filter_by(seller_id=session['user_id']).count()
    total_orders = db.session.query(Order).join(OrderItem).join(Product).filter(Product.seller_id == session['user_id']).count()
    total_sales = db.session.query(db.func.sum(OrderItem.price_at_time * OrderItem.quantity)).join(Product).filter(Product.seller_id == session['user_id'], Order.payment_status == 'paid').scalar() or 0
    
    return render_template('seller_profile.html', user=user, seller_app=seller_app, 
                         total_products=total_products, total_orders=total_orders, total_sales=total_sales)

@app.route('/update-store-info', methods=['POST'])
@seller_required
def update_store_info():
    seller_app = SellerApplication.query.filter_by(user_id=session['user_id'], status='approved').first()
    if not seller_app:
        flash('Seller application not found.', 'error')
        return redirect(url_for('seller_profile'))
    
    seller_app.store_name = request.form['store_name']
    seller_app.store_category = request.form['store_category']
    
    # Handle store logo upload
    if 'store_logo' in request.files:
        file = request.files['store_logo']
        if file and file.filename:
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{session['user_id']}_store_logo_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'documents', filename)
            file.save(file_path)
            seller_app.store_logo = f"/static/uploads/documents/{filename}"
    
    # Commit with retry logic for connection issues
    max_retries = 3
    for attempt in range(max_retries):
        try:
            db.session.commit()
            flash('Store information updated successfully!', 'success')
            return redirect(url_for('seller_profile'))
        except Exception as e:
            db.session.rollback()
            if attempt < max_retries - 1:
                # Wait a moment before retrying
                time.sleep(0.5)
                continue
            else:
                # Log the error and show user-friendly message
                app.logger.error(f"Database error in update_store_info: {str(e)}")
                flash('An error occurred while updating your store information. Please try again.', 'error')
                return redirect(url_for('seller_profile'))

@app.route('/update-store-description', methods=['POST'])
@seller_required
def update_store_description():
    seller_app = SellerApplication.query.filter_by(user_id=session['user_id'], status='approved').first()
    if not seller_app:
        flash('Seller application not found.', 'error')
        return redirect(url_for('seller_profile'))
    
    seller_app.store_description = request.form['store_description']
    seller_app.store_mission = request.form.get('store_mission', '')
    
    # Commit with retry logic for connection issues
    max_retries = 3
    for attempt in range(max_retries):
        try:
            db.session.commit()
            flash('Store description updated successfully!', 'success')
            return redirect(url_for('seller_profile'))
        except Exception as e:
            db.session.rollback()
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue
            else:
                app.logger.error(f"Database error in update_store_description: {str(e)}")
                flash('An error occurred while updating your store description. Please try again.', 'error')
                return redirect(url_for('seller_profile'))

@app.route('/update-return-policy', methods=['POST'])
@seller_required
def update_return_policy():
    seller_app = SellerApplication.query.filter_by(user_id=session['user_id'], status='approved').first()
    if not seller_app:
        flash('Seller application not found.', 'error')
        return redirect(url_for('seller_profile'))
    
    seller_app.return_policy = request.form['return_policy']
    seller_app.return_days = int(request.form.get('return_days', 7))
    seller_app.refund_method = request.form.get('refund_method', 'Original Payment Method')
    
    # Commit with retry logic for connection issues
    max_retries = 3
    for attempt in range(max_retries):
        try:
            db.session.commit()
            flash('Return policy updated successfully!', 'success')
            return redirect(url_for('seller_profile'))
        except Exception as e:
            db.session.rollback()
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue
            else:
                app.logger.error(f"Database error in update_return_policy: {str(e)}")
                flash('An error occurred while updating your return policy. Please try again.', 'error')
                return redirect(url_for('seller_profile'))

@app.route('/upload-business-documents', methods=['POST'])
@seller_required
def upload_business_documents():
    seller_app = SellerApplication.query.filter_by(user_id=session['user_id'], status='approved').first()
    if not seller_app:
        flash('Seller application not found.', 'error')
        return redirect(url_for('seller_profile'))
    
    # Handle business registration upload
    if 'business_registration' in request.files:
        file = request.files['business_registration']
        if file and file.filename:
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{session['user_id']}_business_reg_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'documents', filename)
            file.save(file_path)
            seller_app.business_registration = f"/static/uploads/documents/{filename}"
    
    # Handle valid ID upload
    if 'valid_id' in request.files:
        file = request.files['valid_id']
        if file and file.filename:
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{session['user_id']}_valid_id_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'documents', filename)
            file.save(file_path)
            seller_app.valid_id = f"/static/uploads/documents/{filename}"
    
    db.session.commit()
    flash('Business documents uploaded successfully!', 'success')
    return redirect(url_for('seller_profile'))

@app.route('/update-seller-info', methods=['POST'])
@seller_required
def update_seller_info():
    user = db.session.get(User, session['user_id'])
    seller_app = SellerApplication.query.filter_by(user_id=session['user_id'], status='approved').first()
    
    # Update user info
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.phone = request.form['phone']
    
    # Update seller app info
    if seller_app:
        seller_app.business_address = request.form['business_address']
        seller_app.gcash_number = request.form.get('gcash_number', '')
    
    db.session.commit()
    
    # Update session user_name to reflect changes in dropdown
    session['user_name'] = f"{user.first_name} {user.last_name}"
    
    # Update session with new avatar URL for immediate dropdown update
    avatar_rel = os.path.join('user_avatars', f"user_avatar_{user.id}.png")
    upload_root = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    avatar_path = os.path.join(upload_root, avatar_rel)
    if os.path.exists(avatar_path):
        avatar_path_normalized = avatar_rel.replace("\\", "/")
        session['navbar_avatar_url'] = url_for('static', filename=f'uploads/{avatar_path_normalized}')
        session['avatar_timestamp'] = int(time.time())  # Force cache refresh
    
    flash('Seller information updated successfully!', 'success')
    return redirect(url_for('seller_profile'))

@app.route('/my-orders')
@login_required
def my_orders():
    user_id = session['user_id']
    # Fetch all orders for buyer
    all_orders = Order.query.filter_by(buyer_id=user_id).order_by(Order.created_at.desc()).all()

    # Groupings for tabs
    # To Pay: ALL pending orders (both COD and non-COD) that haven't been processed by seller
    to_pay = [o for o in all_orders if o.status in ['pending', 'to_pay']]
    to_ship = [o for o in all_orders if o.status in ['processing', 'ready_for_pickup']]
    to_receive = [o for o in all_orders if o.status in ['to_ship', 'in_transit', 'delivered']]
    completed = [o for o in all_orders if o.status == 'completed']
    cancelled = [o for o in all_orders if o.status == 'cancelled']

    # Buyer returns list for the Returns/Refund tab
    returns = ReturnRequest.query.filter_by(buyer_id=user_id).order_by(ReturnRequest.created_at.desc()).all()

    # Add review eligibility for each order item
    for order in all_orders:
        for item in order.items:
            can_review, order_id, message = can_user_review_product(user_id, item.product_id)
            item.can_review = can_review
            item.review_message = message
            # Track if already reviewed to show "Rated" state
            item.has_review = Review.query.filter_by(user_id=user_id, product_id=item.product_id).first() is not None

    active_tab = request.args.get('tab', 'to_pay')

    return render_template('buyer/my_orders.html',
        orders=all_orders,
        to_pay=to_pay,
        to_ship=to_ship,
        to_receive=to_receive,
        completed=completed,
        cancelled=cancelled,
        returns=returns,
        active_tab=active_tab
    )

@app.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = Wishlist.query.filter_by(user_id=session['user_id']).all()
    return render_template('wishlist.html', wishlist_items=wishlist_items)

@app.route('/add-to-wishlist/<int:product_id>')
@login_required
def add_to_wishlist(product_id):
    existing = Wishlist.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    if not existing:
        wishlist_item = Wishlist(user_id=session['user_id'], product_id=product_id)
        db.session.add(wishlist_item)
        db.session.commit()
        flash('Added to wishlist!', 'success')
    else:
        flash('Item already in wishlist.', 'info')
    return redirect(request.referrer or url_for('shop'))

@app.route('/remove-from-wishlist/<int:product_id>')
@login_required
def remove_from_wishlist(product_id):
    Wishlist.query.filter_by(user_id=session['user_id'], product_id=product_id).delete()
    db.session.commit()
    flash('Removed from wishlist.', 'info')
    return redirect(url_for('wishlist'))

@app.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Upload and save a square PNG avatar for the current user under
    static/uploads/user_avatars/user_avatar_{user.id}.png
    """
    try:
        user = db.session.get(User, session['user_id'])
        if 'avatar' not in request.files:
            flash('No file provided.', 'error')
            return redirect(url_for('profile'))
        f = request.files['avatar']
        if not f or not f.filename:
            flash('Please choose an image.', 'warning')
            return redirect(url_for('profile'))
        # Validate extension
        ext = (f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else '')
        if ext not in ALLOWED_IMAGE_EXT:
            flash('Unsupported image type. Please upload JPG or PNG.', 'danger')
            return redirect(url_for('profile'))
        # Ensure folder exists
        avatar_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'user_avatars')
        os.makedirs(avatar_dir, exist_ok=True)
        # Load image and convert to 1:1 square PNG
        img = Image.open(f.stream).convert('RGBA')
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side)).resize((256, 256), Image.LANCZOS)
        # Save as canonical filename the UI expects
        out_path = os.path.join(avatar_dir, f'user_avatar_{user.id}.png')
        img.save(out_path, format='PNG', optimize=True)
        
        # Update session with new avatar URL for immediate dropdown update
        avatar_rel = os.path.join('user_avatars', f"user_avatar_{user.id}.png")
        avatar_path_normalized = avatar_rel.replace("\\", "/")
        session['navbar_avatar_url'] = url_for('static', filename=f'uploads/{avatar_path_normalized}')
        session['avatar_timestamp'] = int(time.time())  # Force cache refresh
        
        flash('Profile picture updated!', 'success')
    except Exception as e:
        app.logger.exception('Failed to upload avatar: %s', e)
        flash('Failed to upload profile picture. Please try again.', 'danger')
    return redirect(url_for('profile'))


@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    user = db.session.get(User, session['user_id'])
    active_role = session.get('active_role', user.role)
    
    # Get form data with fallbacks to existing values
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    
    # Validate and update first name (required)
    if first_name:
        user.first_name = first_name
    elif not user.first_name:
        flash('First name is required.', 'error')
        if user.role == 'admin':
            return redirect(url_for('admin_profile'))
        elif active_role == 'seller':
            return redirect(url_for('seller_profile'))
        else:
            return redirect(url_for('buyer_profile'))
    
    # Validate and update last name (required)
    if last_name:
        user.last_name = last_name
    elif not user.last_name:
        flash('Last name is required.', 'error')
        if user.role == 'admin':
            return redirect(url_for('admin_profile'))
        elif active_role == 'seller':
            return redirect(url_for('seller_profile'))
        else:
            return redirect(url_for('buyer_profile'))
    
    # Validate and update phone number (optional but validated if provided)
    if phone:
        # Remove common separators and spaces
        phone_cleaned = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        if not phone_cleaned.isdigit() or len(phone_cleaned) < 10:
            flash('Please enter a valid phone number (at least 10 digits).', 'error')
            if user.role == 'admin':
                return redirect(url_for('admin_profile'))
            elif active_role == 'seller':
                return redirect(url_for('seller_profile'))
            else:
                return redirect(url_for('buyer_profile'))
        user.phone = phone
    
    # Update address (optional)
    if address:
        user.address = address
    
    db.session.commit()
    session['user_name'] = f"{user.first_name} {user.last_name}"
    
    # Update session with new avatar URL for immediate dropdown update
    avatar_rel = os.path.join('user_avatars', f"user_avatar_{user.id}.png")
    upload_root = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    avatar_path = os.path.join(upload_root, avatar_rel)
    if os.path.exists(avatar_path):
        avatar_path_normalized = avatar_rel.replace("\\", "/")
        session['navbar_avatar_url'] = url_for('static', filename=f'uploads/{avatar_path_normalized}')
        session['avatar_timestamp'] = int(time.time())  # Force cache refresh
    
    # Provide specific feedback about what was updated
    updated_fields = []
    if first_name: updated_fields.append('name')
    if phone: updated_fields.append('phone number')
    if address: updated_fields.append('address')
    
    if updated_fields:
        fields_text = ', '.join(updated_fields)
        flash(f'Profile updated successfully! Updated: {fields_text}.', 'success')
    else:
        flash('No changes were made to your profile.', 'info')
    
    # Redirect based on user role
    if user.role == 'admin':
        return redirect(url_for('admin_profile'))
    elif active_role == 'seller':
        return redirect(url_for('seller_profile'))
    else:
        return redirect(url_for('buyer_profile'))

# --- Add this route to allow sellers to remove their store logo ---
@app.route('/remove-store-logo', methods=['POST'])
@seller_required
def remove_store_logo():
    """
    Remove the current seller store logo (file on disk + DB field).
    Only available to the logged-in seller who owns the SellerApplication.
    """
    seller_app = SellerApplication.query.filter_by(user_id=session['user_id']).first()
    if not seller_app:
        flash('Seller application not found.', 'error')
        return redirect(url_for('seller_profile'))

    if not seller_app.store_logo:
        flash('No store logo to remove.', 'info')
        return redirect(url_for('seller_profile'))

    try:
        logo_path = seller_app.store_logo  # e.g. "/static/uploads/documents/xxx.png" or "uploads/..."
        # Resolve filesystem path robustly
        if logo_path.startswith('/'):
            fs_path = os.path.join(app.root_path, logo_path.lstrip('/'))
        else:
            # If saved without leading slash assume it's relative to static/
            fs_path = os.path.join(app.root_path, 'static', logo_path)

        # Remove file if it exists
        if os.path.exists(fs_path):
            os.remove(fs_path)

        # Clear DB field
        seller_app.store_logo = None
        db.session.commit()

        flash('Store logo removed successfully.', 'success')
    except Exception as e:
        app.logger.exception("Failed to remove store logo")
        db.session.rollback()
        flash('Failed to remove store logo. Please try again later.', 'danger')

    return redirect(url_for('seller_profile'))


@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    user = db.session.get(User, session['user_id'])
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    if user.password != current_password:
        flash('Current password is incorrect.', 'error')
    elif new_password != confirm_password:
        flash('New passwords do not match.', 'error')
    else:
        user.password = new_password
        
        # Update security settings
        user.two_factor_enabled = 'two_factor' in request.form
        user.email_notifications = 'email_notifications' in request.form
        
        db.session.commit()
        flash('Password and security settings updated successfully!', 'success')
    
    # Redirect based on user role
    if is_seller():
        return redirect(url_for('seller_profile'))
    else:
        return redirect(url_for('profile'))


@app.route('/add-address', methods=['POST'])
@login_required
def add_address():
    """
    FIX: Use .get() for 'label' to avoid BadRequestKeyError when the field is missing.
    All other logic unchanged exactly as requested.
    """
    label = request.form.get('label', 'Address')  # <-- changed from request.form['label']
    full_address = request.form['full_address']
    is_default = 'is_default' in request.form
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    region = request.form.get('region')
    province = request.form.get('province')
    city = request.form.get('city')
    barangay = request.form.get('barangay')
    street = request.form.get('street_address') or request.form.get('street')
    if is_default:
        Address.query.filter_by(user_id=session['user_id'], is_default=True).update({'is_default': False})
    new_address = Address(
        user_id=session['user_id'],
        label=label,
        full_address=full_address,
        is_default=is_default,
        latitude=float(latitude) if latitude else None,
        longitude=float(longitude) if longitude else None,
        region=region or None,
        province=province or None,
        city=str(city) if city else None,
        barangay=barangay or None,
        street=street or None
    )
    db.session.add(new_address)
    db.session.commit()
    
    # Store the newly added address ID in session for auto-selection
    session['new_address_id'] = new_address.id
    
    flash('Address added successfully!', 'success')
    
    # Redirect to referring page or profile
    return_to = request.form.get('return_to') or request.referrer
    if return_to and 'checkout' in return_to:
        return redirect(url_for('checkout'))
    return redirect(url_for('profile'))

# ... keep all existing imports and code above unchanged ...

@app.route('/edit-address/<int:address_id>', methods=['POST'])
@login_required
def edit_address(address_id):
    """Edit an existing address record for the logged-in user."""
    address = Address.query.filter_by(id=address_id, user_id=session['user_id']).first_or_404()

    # Basic required fields (same as simple add form)
    label = request.form.get('label', address.label).strip()
    full_address = request.form.get('full_address', address.full_address).strip()
    is_default = 'is_default' in request.form

    # Optional structured fields (used by advanced add modal if present)
    region = request.form.get('region')
    province = request.form.get('province')
    city = request.form.get('city')
    barangay = request.form.get('barangay')
    street = request.form.get('street_address') or request.form.get('street')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    # If setting this as default, unset previous default
    if is_default:
        Address.query.filter_by(user_id=session['user_id'], is_default=True).update({'is_default': False})

    # Apply updates
    address.label = label or address.label
    address.full_address = full_address or address.full_address
    address.is_default = is_default

    # Update optional structured fields only if provided
    if region: address.region = region
    if province: address.province = province
    if city: address.city = str(city)
    if barangay: address.barangay = barangay
    if street: address.street = street
    if latitude:
        try: address.latitude = float(latitude)
        except ValueError: pass
    if longitude:
        try: address.longitude = float(longitude)
        except ValueError: pass

    db.session.commit()
    
    # Store the edited address ID in session for feedback
    session['edited_address_id'] = address.id
    
    flash('Address updated successfully!', 'success')
    
    # Redirect to referring page or profile
    return_to = request.form.get('return_to') or request.referrer
    if return_to and 'checkout' in return_to:
        return redirect(url_for('checkout'))
    return redirect(url_for('profile'))

# ... keep the rest of the file below unchanged ...


@app.route('/api/get-address/<int:address_id>')
@login_required
def get_address_details(address_id):
    """API endpoint to get address details as JSON for editing (Supabase version)."""
    try:
        addresses = get_data('address', filters={'id': address_id, 'user_id': session['user_id']})
        if not addresses or len(addresses) == 0:
            return jsonify({'success': False, 'message': 'Address not found'}), 404
        
        address = addresses[0]
        
        return jsonify({
            'success': True,
            'address': {
                'id': address.get('id'),
                'label': address.get('label'),
                'full_address': address.get('full_address'),
                'street': address.get('street') or '',
                'region': address.get('region') or '',
                'province': address.get('province') or '',
                'city': address.get('city') or '',
                'barangay': address.get('barangay') or '',
                'is_default': address.get('is_default')
            }
        })
    except Exception as e:
        app.logger.error(f'/api/get-address error: {e}')
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/delete-address/<int:address_id>')
@login_required
def delete_address(address_id):
    address = Address.query.filter_by(id=address_id, user_id=session['user_id']).first_or_404()
    db.session.delete(address)
    db.session.commit()
    flash('Address deleted.', 'info')
    return redirect(url_for('profile'))

@app.route('/google-login')
def google_login():
    return redirect(url_for("google.login"))

@app.route('/check-password-strength', methods=['POST'])
def check_password_strength():
    """API endpoint for real-time password strength checking"""
    data = request.get_json()
    password = data.get('password', '')
    
    if not password:
        return jsonify({'strength': 0, 'level': 'weak', 'message': 'Enter a password'})
    
    strength = calculate_password_strength(password)
    
    if strength < 40:
        level = 'weak'
        color = 'danger'
    elif strength < 70:
        level = 'medium'
        color = 'warning'
    else:
        level = 'strong'
        color = 'success'
    
    is_valid, message = validate_password(password)
    
    return jsonify({
        'strength': strength,
        'level': level,
        'color': color,
        'is_valid': is_valid,
        'message': message
    })


# ... (existing imports, models, routes above)

from werkzeug.utils import secure_filename

# --- Add this route below your other routes ---

@app.route('/submit-review/<int:product_id>', methods=['POST'])
@login_required
def submit_review(product_id):
    product = Product.query.get_or_404(product_id)
    user_id = session['user_id']
    
    # Verify user can review this product
    can_review, order_id, message = can_user_review_product(user_id, product_id)
    if not can_review:
        flash(message, 'error')
        return redirect(request.referrer or url_for('product_detail', product_id=product_id))
    
    # Validate rating
    try:
        rating = int(request.form.get('rating', 0))
        if rating < 1 or rating > 5:
            flash('Please provide a rating between 1 and 5 stars.', 'error')
            return redirect(request.referrer or url_for('product_detail', product_id=product_id))
    except ValueError:
        flash('Invalid rating value.', 'error')
        return redirect(request.referrer or url_for('product_detail', product_id=product_id))
    
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()  # optional per requirement
    
    # Handle multiple media uploads (images/videos)
    media_files = request.files.getlist('media[]') or []
    saved_media = []
    first_image_filename = None
    review_img_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'reviews')
    review_vid_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'reviews', 'videos')
    os.makedirs(review_img_dir, exist_ok=True)
    os.makedirs(review_vid_dir, exist_ok=True)

    for f in media_files:
        if not f or not f.filename:
            continue
        ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
        safe_name = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id}_{product_id}_{f.filename}")
        try:
            if ext in ALLOWED_IMAGE_EXT:
                path = os.path.join(review_img_dir, safe_name)
                f.save(path)
                url_path = f"reviews/{safe_name}"
                saved_media.append({'type': 'image', 'path': f"/static/uploads/{url_path}"})
                if not first_image_filename:
                    first_image_filename = safe_name
            elif ext in ALLOWED_VIDEO_EXT:
                f.seek(0, os.SEEK_END)
                size = f.tell()
                f.seek(0)
                if size and size > MAX_VIDEO_BYTES:
                    flash('Video too large. Max 50MB.', 'warning')
                    continue
                path = os.path.join(review_vid_dir, safe_name)
                f.save(path)
                url_path = f"reviews/videos/{safe_name}"
                saved_media.append({'type': 'video', 'path': f"/static/uploads/{url_path}"})
            else:
                flash('Unsupported file type skipped.', 'warning')
        except Exception:
            flash('Failed to upload one of the files. Skipped.', 'warning')
            continue

    # Save review with verified purchase
    new_review = Review(
        product_id=product_id,
        user_id=user_id,
        rating=rating,
        title=title,
        content=content or None,
        status='published',
        created_at=datetime.utcnow(),
        image_filename=first_image_filename,  # legacy image support
        media=saved_media if saved_media else None,
        verified_purchase=True,  # User has been verified through can_user_review_product
        order_id=order_id  # Link to the purchase order
    )

    db.session.add(new_review)
    db.session.commit()

    flash('Thank you for your verified review!', 'success')
    # After rating, go back to My Orders so the button shows "Rated"
    if request.referrer and '/my-orders' in request.referrer:
        return redirect(url_for('my_orders', tab='completed'))
    return redirect(url_for('product_detail', product_id=product_id, _anchor='reviews'))


@app.route('/set-role/<role>')
@login_required
def set_role(role):
    user = db.session.get(User, session['user_id'])
    role = (role or '').strip().lower()
    if role == 'buyer':
        session['active_role'] = 'buyer'
        flash('Switched to Buyer mode', 'success')
        return redirect(request.referrer or url_for('index'))
    if role == 'seller':
        seller_app = SellerApplication.query.filter_by(user_id=user.id, status='approved').first()
        if user.role == 'seller' or seller_app:
            session['active_role'] = 'seller'
            flash('Switched to Seller mode', 'success')
            return redirect(url_for('seller_dashboard'))
        flash('You are not approved as a seller yet.', 'error')
        return redirect(request.referrer or url_for('index'))
    if role == 'rider':
        # Optional: allow riders to set active role if they are a rider
        if user.role == 'rider':
            session['active_role'] = 'rider'
            flash('Switched to Rider mode', 'success')
            return redirect(url_for('rider_dashboard'))
        flash('Rider mode is not available for your account.', 'error')
        return redirect(request.referrer or url_for('index'))
    flash('Unknown role.', 'error')
    return redirect(request.referrer or url_for('index'))


@app.route('/switch-role')
@login_required
def switch_role():
    user = db.session.get(User, session['user_id'])
    current_active_role = session.get('active_role', user.role)
    
    # Check if user has an approved seller application
    seller_app = SellerApplication.query.filter_by(user_id=user.id, status='approved').first()
    
    if current_active_role == 'buyer':
        # Switch to seller mode
        if user.role == 'seller' or seller_app:
            session['active_role'] = 'seller'
            flash('Switched to Seller mode', 'success')
            return redirect(url_for('seller_dashboard'))
        else:
            flash('You are not approved as a seller yet.', 'error')
    elif current_active_role == 'seller':
        # Switch to buyer mode
        session['active_role'] = 'buyer'
        flash('Switched to Buyer mode', 'success')
        return redirect(url_for('index'))
    else:
        flash('Role switching not available for your account type.', 'error')
    
    return redirect(request.referrer or url_for('index'))


@app.route('/store/<int:seller_id>')
def store_page(seller_id):
    seller = User.query.get_or_404(seller_id)
    seller_app = SellerApplication.query.filter_by(user_id=seller_id, status='approved').first()
    if not seller_app:
        flash('Store not found or not approved.', 'error')
        return redirect(url_for('shop'))

    # products and categories
    products = Product.query.filter_by(seller_id=seller_id, status='active').all()
    categories = Category.query.all()
    now = datetime.now(timezone.utc)
    # Filter new arrivals (products added in the last 30 days)
    new_arrivals = [p for p in products if p.created_at and p.created_at > (now - timedelta(days=30))]
    # Filter top selling (example: sort by sold attribute, if exists)
    top_selling = sorted(products, key=lambda p: getattr(p, 'sold', 0), reverse=True)[:6]

    # Followers count (accurate)
    try:
        followers_count = Follow.query.filter_by(seller_id=seller_id).count()
    except Exception:
        followers_count = 0

    # Average rating across this seller's published reviews
    try:
        avg_rating = db.session.query(db.func.avg(Review.rating))\
            .join(Product, Review.product_id == Product.id)\
            .filter(Product.seller_id == seller_id, Review.status == 'published')\
            .scalar()
        store_rating = float(avg_rating) if avg_rating is not None else 0.0
    except Exception:
        store_rating = 0.0

    # Is current user following this store?
    is_following = False
    if 'user_id' in session:
        is_following = Follow.query.filter_by(follower_id=session['user_id'], seller_id=seller_id).first() is not None

    # Get store background image URL
    store_background_url = None
    if seller_app.store_background:
        store_background_url = _safe_upload_url(seller_app.store_background)

    return render_template(
        'store_page.html',
        seller=seller,
        seller_app=seller_app,
        store_rating=round(store_rating, 1),
        followers_count=followers_count,
        is_following=is_following,
        products=products,
        categories=categories,
        new_arrivals=new_arrivals,
        top_selling=top_selling,
        store_rating_raw=store_rating,  # optional if you want unrounded value in template
        store_background_url=store_background_url  # Pass background image URL to template
    )

@app.route('/follow-store/<int:seller_id>', methods=['POST'])
@login_required
def follow_store(seller_id):
    # Prevent self-follow
    if session.get('user_id') == seller_id:
        flash('You cannot follow your own store.', 'warning')
        return redirect(url_for('store_page', seller_id=seller_id))

    existing = Follow.query.filter_by(follower_id=session['user_id'], seller_id=seller_id).first()
    if existing:
        # Unfollow
        try:
            db.session.delete(existing)
            db.session.commit()
            flash('You have unfollowed this store.', 'info')
        except Exception:
            db.session.rollback()
            app.logger.exception("Failed to unfollow store")
            flash('Unable to unfollow at the moment. Please try again.', 'danger')
    else:
        # Follow
        try:
            new_follow = Follow(follower_id=session['user_id'], seller_id=seller_id)
            db.session.add(new_follow)
            db.session.commit()
            flash('You are now following this store!', 'success')
        except Exception:
            db.session.rollback()
            app.logger.exception("Failed to follow store")
            flash('Unable to follow at the moment. Please try again.', 'danger')

    return redirect(url_for('store_page', seller_id=seller_id))


# ... keep existing imports ...

@app.template_filter('comma')
def comma_format(value, digits=None):
    """
    Format numbers with thousands separators.
    - Accepts int, float, or numeric strings (with or without commas).
    - For floats, defaults to 2 decimal places (configurable via |comma(2)).
    - Falls back to string if value isn't numeric.
    Usage:
      {{ 1234567 | comma }}           -> "1,234,567"
      {{ 1234567.8 | comma }}         -> "1,234,567.80"
      {{ 1234567.891 | comma(3) }}    -> "1,234,567.891"
      {{ "1234567.8" | comma }}       -> "1,234,567.80"
    """
    try:
        # Normalize strings to numeric first
        if isinstance(value, str):
            cleaned = value.strip().replace(',', '')
            # Try integer first
            if cleaned.isdigit():
                value = int(cleaned)
            else:
                value = float(cleaned)

        # Integers
        if isinstance(value, int):
            return f"{value:,}"

        # Floats
        if isinstance(value, float):
            if digits is None:
                digits = 2
            return f"{value:,.{digits}f}"

        # Other numeric-like types (Decimal, etc.)
        try:
            as_float = float(value)
            if digits is None:
                digits = 2
            return f"{as_float:,.{digits}f}"
        except Exception:
            return str(value)
    except Exception:
        # As a last resort, just stringify
        return str(value)

# ... rest of app.py unchanged ...

@app.route('/chat')
@login_required
def chat_list():
    user_id = session['user_id']
    active_role = session.get('active_role', 'buyer')
    
    # Get ChatMessage model from unified chat system
    ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
    if not ChatMessage:
        return render_template('store_chat.html', chats=[], users_by_id={}, chat_messages=[], selected_chat=None)
    
    # Build conversation list with expected fields for template
    convos = []
    users_by_id = {}
    
    # Get unique peer IDs (users current user has chatted with)
    from sqlalchemy import or_, and_
    subq_sent = db.session.query(ChatMessage.receiver_id).filter(ChatMessage.sender_id == user_id).distinct()
    subq_received = db.session.query(ChatMessage.sender_id).filter(ChatMessage.receiver_id == user_id).distinct()
    
    peer_ids = set()
    for row in subq_sent.all():
        peer_ids.add(row[0])
    for row in subq_received.all():
        peer_ids.add(row[0])
    
    if peer_ids:
        users_by_id = {u.id: u for u in User.query.filter(User.id.in_(peer_ids)).all()}
        
        for peer_id in peer_ids:
            # Get last message
            last = ChatMessage.query.filter(
                or_(
                    and_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == peer_id),
                    and_(ChatMessage.sender_id == peer_id, ChatMessage.receiver_id == user_id)
                )
            ).order_by(ChatMessage.created_at.desc()).first()
            
            # Count unread messages from this peer
            unread = ChatMessage.query.filter_by(sender_id=peer_id, receiver_id=user_id, is_read=False).count()
            
            # Create conversation object (use seller_id for backward compatibility with template)
            convos.append(type('Obj', (), {
                'seller_id': peer_id,
                'buyer_id': peer_id,
                'last_message': getattr(last, 'message', ''),
                'unread_count': unread
            }))
        
        # Sort by last message time
        convos.sort(key=lambda c: getattr(ChatMessage.query.filter(
            or_(
                and_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == c.seller_id),
                and_(ChatMessage.sender_id == c.seller_id, ChatMessage.receiver_id == user_id)
            )
        ).order_by(ChatMessage.created_at.desc()).first(), 'created_at', datetime.min), reverse=True)
    
    return render_template('store_chat.html', chats=convos, users_by_id=users_by_id, chat_messages=[], selected_chat=None)

@app.route('/chat/<int:seller_id>', methods=['GET', 'POST'])
@login_required
def chat_window(seller_id):
    buyer_id = session['user_id']
    product_id = request.args.get('product_id', type=int)
    seller = User.query.get_or_404(seller_id)
    
    # Get ChatMessage model from unified chat system
    ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
    if not ChatMessage:
        return render_template('store_chat.html', chats=[], users_by_id={}, chat_messages=[], selected_chat=seller)
    
    # Get all messages between buyer and seller
    from sqlalchemy import or_, and_
    chat_messages = ChatMessage.query.filter(
        or_(
            and_(ChatMessage.sender_id == buyer_id, ChatMessage.receiver_id == seller_id),
            and_(ChatMessage.sender_id == seller_id, ChatMessage.receiver_id == buyer_id)
        )
    ).order_by(ChatMessage.created_at.asc()).all()
    
    # Mark all messages from seller as read
    unread_msgs = ChatMessage.query.filter_by(sender_id=seller_id, receiver_id=buyer_id, is_read=False).all()
    for msg in unread_msgs:
        msg.is_read = True
    db.session.commit()

    # Get all seller products for attachment
    buyer_products = Product.query.filter_by(seller_id=seller_id, status='active').all()
    prefill_product = None
    prefill_message = ""
    if product_id:
        prefill_product = db.session.get(Product, product_id)
        if prefill_product:
            prefill_message = f"Hi, I am interested in the {prefill_product.name} (₱{prefill_product.price:,.2f}). Is this item still available?"

    # Handle POST (send message)
    if request.method == 'POST':
        message = request.form.get('message')
        attached_product_id = request.form.get('product_id') or None
        chat = ChatMessage(
            sender_id=buyer_id,
            receiver_id=seller_id,
            message=message,
            product_id=attached_product_id if attached_product_id else None,
            created_at=datetime.utcnow(),
            is_read=False
        )
        db.session.add(chat)
        db.session.commit()
        return redirect(url_for('chat_window', seller_id=seller_id))

    # Build users_by_id and computed chat list for sidebar badges
    users_by_id = {seller.id: seller}
    # Compose a minimal sidebar with single selected chat and unread=0
    chats = []
    last_msg = chat_messages[-1].message if chat_messages else ''
    chats.append(type('Obj', (), {'seller_id': seller.id, 'last_message': last_msg, 'unread_count': 0}))
    return render_template(
        'store_chat.html',
        chats=chats,
        users_by_id=users_by_id,
        chat_messages=chat_messages,
        selected_chat=seller,
        buyer_products=buyer_products,
        prefill_product=prefill_product,
        prefill_message=prefill_message
    )

# Seller chat with buyers
@app.route('/seller/chat/<int:buyer_id>', methods=['GET', 'POST'])
@login_required
@seller_required
def seller_chat_with_buyer(buyer_id):
    seller_id = session['user_id']
    buyer = User.query.get_or_404(buyer_id)
    
    # Get ChatMessage model from unified chat system
    ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
    if not ChatMessage:
        return render_template('seller_chat.html', chats=[], users_by_id={}, chat_messages=[], selected_chat=buyer)
    
    # Get chat messages between this seller and buyer
    from sqlalchemy import or_, and_
    chat_messages = ChatMessage.query.filter(
        or_(
            and_(ChatMessage.sender_id == buyer_id, ChatMessage.receiver_id == seller_id),
            and_(ChatMessage.sender_id == seller_id, ChatMessage.receiver_id == buyer_id)
        )
    ).order_by(ChatMessage.created_at.asc()).all()
    
    # Mark all messages from buyer as read
    unread_msgs = ChatMessage.query.filter_by(sender_id=buyer_id, receiver_id=seller_id, is_read=False).all()
    for msg in unread_msgs:
        msg.is_read = True
    db.session.commit()
    
    # Get seller products for attachment
    seller_products = Product.query.filter_by(seller_id=seller_id, status='active').all()
    
    # Get buyer's orders to find associated riders
    buyer_orders = Order.query.filter_by(buyer_id=buyer_id).filter(Order.rider_id.isnot(None)).order_by(Order.created_at.desc()).all()
    rider_ids = list(set([order.rider_id for order in buyer_orders if order.rider_id]))
    riders = User.query.filter(User.id.in_(rider_ids)).all() if rider_ids else []
    
    # Handle POST (send message)
    if request.method == 'POST':
        message = request.form.get('message')
        attached_product_id = request.form.get('product_id') or None
        
        if message:
            chat = ChatMessage(
                sender_id=seller_id,
                receiver_id=buyer_id,
                message=message,
                product_id=attached_product_id if attached_product_id else None,
                created_at=datetime.utcnow(),
                is_read=False
            )
            db.session.add(chat)
            db.session.commit()
            return redirect(url_for('seller_chat_with_buyer', buyer_id=buyer_id))
    
    # Build users_by_id with buyer and riders
    users_by_id = {buyer.id: buyer}
    for rider in riders:
        users_by_id[rider.id] = rider
    
    # Get all unique buyers who have chatted with this seller
    subq_sent = db.session.query(ChatMessage.receiver_id).filter(ChatMessage.sender_id == seller_id).distinct()
    subq_received = db.session.query(ChatMessage.sender_id).filter(ChatMessage.receiver_id == seller_id).distinct()
    
    peer_ids = set()
    for row in subq_sent.all():
        peer_ids.add(row[0])
    for row in subq_received.all():
        peer_ids.add(row[0])
    
    chats = []
    for peer_id in peer_ids:
        chat_buyer = User.query.get(peer_id)
        if chat_buyer:
            users_by_id[chat_buyer.id] = chat_buyer
            last_msg_obj = ChatMessage.query.filter(
                or_(
                    and_(ChatMessage.sender_id == seller_id, ChatMessage.receiver_id == peer_id),
                    and_(ChatMessage.sender_id == peer_id, ChatMessage.receiver_id == seller_id)
                )
            ).order_by(ChatMessage.created_at.desc()).first()
            
            unread = ChatMessage.query.filter_by(
                sender_id=peer_id,
                receiver_id=seller_id,
                is_read=False
            ).count()
            
            chats.append(type('Obj', (), {
                'buyer_id': chat_buyer.id,
                'last_message': last_msg_obj.message if last_msg_obj else '',
                'unread_count': unread
            }))
    
    return render_template(
        'seller_chat.html',
        chats=chats,
        users_by_id=users_by_id,
        chat_messages=chat_messages,
        selected_chat=buyer,
        seller_products=seller_products,
        riders=riders
    )


@app.route('/seller/chat/rider/<int:rider_id>', methods=['GET', 'POST'])
@login_required
@seller_required
def seller_chat_rider(rider_id):
    """Seller chat with rider using UNIFIED chat system"""
    seller_id = session['user_id']
    order_id = request.args.get('order_id', type=int)
    
    rider = User.query.get_or_404(rider_id)
    
    from sqlalchemy import text
    
    # Query unified chat_message table
    chat_messages = db.session.execute(
        text("""
            SELECT id, sender_id, receiver_id, message, is_read, created_at
            FROM chat_message
            WHERE (sender_id = :seller_id AND receiver_id = :rider_id)
               OR (sender_id = :rider_id AND receiver_id = :seller_id)
            ORDER BY created_at ASC
        """),
        {'seller_id': seller_id, 'rider_id': rider_id}
    ).fetchall()
    
    # Mark messages from rider as read
    db.session.execute(
        text("""
            UPDATE chat_message
            SET is_read = TRUE
            WHERE sender_id = :rider_id
              AND receiver_id = :seller_id
              AND is_read = FALSE
        """),
        {'rider_id': rider_id, 'seller_id': seller_id}
    )
    db.session.commit()
    
    # Handle POST (send message)
    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        if message:
            # Insert into unified chat_message table
            db.session.execute(
                text("""
                    INSERT INTO chat_message (sender_id, receiver_id, message, order_id, is_read, created_at)
                    VALUES (:sender, :receiver, :msg, :order, FALSE, :created)
                """),
                {
                    'sender': seller_id,
                    'receiver': rider_id,
                    'msg': message,
                    'order': order_id,
                    'created': datetime.utcnow()
                }
            )
            db.session.commit()
            
            # Send notification to rider
            try:
                seller_user = db.session.get(User, seller_id)
                push_notification(
                    rider_id,
                    f"Seller {seller_user.first_name} sent you a message.",
                    link=url_for('rider_chat_conversations'),
                    actor_user_id=seller_id,
                    type='chat'
                )
                # Emit to rider's room
                socketio.emit('new_message', {
                    'sender_id': seller_id,
                    'sender_name': f"{seller_user.first_name} {seller_user.last_name}",
                    'message': message,
                    'created_at': datetime.utcnow().isoformat()
                }, room=f'user_{rider_id}')
            except Exception as e:
                print(f"Error sending notification: {e}")
            
            return redirect(url_for('seller_chat_rider', rider_id=rider_id, order_id=order_id))
    
    rider_profile = DeliveryPersonnel.query.filter_by(user_id=rider_id).first()
    order = Order.query.get(order_id) if order_id else None
    rider_avatar_url = get_user_avatar_url(rider.id, rider.role)
    
    return render_template('seller/rider_chat.html', 
                         chat_messages=chat_messages, 
                         rider=rider,
                         rider_avatar_url=rider_avatar_url, 
                         rider_profile=rider_profile,
                         order=order,
                         seller_id=seller_id)

@app.route('/seller/inbox')
@login_required
def seller_inbox():
    """Seller inbox - view all buyer messages using unified chat_message table"""
    try:
        seller_id = session['user_id']
        buyer_id = request.args.get('buyer_id', type=int)
        
        from sqlalchemy import text
        
        # Get all unique buyers AND riders who messaged this seller
        buyers_result = db.session.execute(text("""
            SELECT DISTINCT 
                u.id, 
                u.first_name, 
                u.last_name, 
                u.profile_picture,
                u.role,
                (SELECT COUNT(*) FROM chat_message 
                 WHERE sender_id = u.id 
                 AND receiver_id = :seller_id 
                 AND is_read = FALSE) as unread_count,
                (SELECT message FROM chat_message 
                 WHERE (sender_id = u.id AND receiver_id = :seller_id)
                    OR (sender_id = :seller_id AND receiver_id = u.id)
                 ORDER BY created_at DESC LIMIT 1) as last_message,
                (SELECT created_at FROM chat_message 
                 WHERE (sender_id = u.id AND receiver_id = :seller_id)
                    OR (sender_id = :seller_id AND receiver_id = u.id)
                 ORDER BY created_at DESC LIMIT 1) as last_message_time
            FROM "user" u
            WHERE EXISTS (
                SELECT 1 FROM chat_message cm
                WHERE (cm.sender_id = u.id AND cm.receiver_id = :seller_id)
                   OR (cm.sender_id = :seller_id AND cm.receiver_id = u.id)
            )
            ORDER BY last_message_time DESC
        """), {'seller_id': seller_id})
        
        buyers = []
        for row in buyers_result:
            peer_id = row[0]
            peer_role = row[4] or 'buyer'
            avatar_url = get_user_avatar_url(peer_id, peer_role)
            buyer_obj = type('obj', (object,), {
                'id': peer_id,
                'first_name': row[1],
                'last_name': row[2],
                'profile_picture': avatar_url,
                'avatar': avatar_url,
                'role': peer_role,
                'unread_count': row[5] or 0,
                'last_message': type('obj', (object,), {
                    'message': row[6],
                    'created_at': row[7]
                })() if row[6] else None
            })()
            buyers.append(buyer_obj)
        
        # Get chat thread if buyer selected
        chat_thread = []
        if buyer_id:
            # Mark messages as read
            db.session.execute(text("""
                UPDATE chat_message
                SET is_read = TRUE
                WHERE sender_id = :buyer_id
                AND receiver_id = :seller_id
                AND is_read = FALSE
            """), {'buyer_id': buyer_id, 'seller_id': seller_id})
            db.session.commit()
            
            # Get messages
            messages_result = db.session.execute(text("""
                SELECT 
                    cm.id,
                    cm.sender_id,
                    cm.receiver_id,
                    cm.message,
                    cm.product_id,
                    cm.is_read,
                    cm.created_at,
                    u.first_name,
                    u.last_name,
                    u.profile_picture,
                    p.id as prod_id,
                    p.name as prod_name,
                    p.price as prod_price,
                    p.image_filename as prod_image
                FROM chat_message cm
                JOIN "user" u ON cm.sender_id = u.id
                LEFT JOIN product p ON cm.product_id = p.id
                WHERE (cm.sender_id = :seller_id AND cm.receiver_id = :buyer_id)
                   OR (cm.sender_id = :buyer_id AND cm.receiver_id = :seller_id)
                ORDER BY cm.created_at ASC
            """), {'seller_id': seller_id, 'buyer_id': buyer_id})
            
            for row in messages_result:
                sender_id = row[1]
                sender_user = db.session.get(User, sender_id)
                sender_role = (
                    'seller' if sender_id == seller_id
                    else (sender_user.role if sender_user else 'buyer')
                )
                sender_avatar = get_user_avatar_url(
                    sender_id,
                    sender_user.role if sender_user else sender_role,
                )
                msg_obj = type('obj', (object,), {
                    'id': row[0],
                    'sender_id': sender_id,
                    'buyer_id': buyer_id,
                    'seller_id': seller_id,
                    'message': row[3],
                    'product_id': row[4],
                    'is_read': row[5],
                    'created_at': row[6],
                    'sender_role': sender_role,
                    'sender_avatar': sender_avatar,
                    'buyer': type('obj', (object,), {
                        'first_name': row[7] if row[1] == buyer_id else '',
                        'last_name': row[8] if row[1] == buyer_id else '',
                        'profile_picture': sender_avatar if row[1] == buyer_id else get_user_avatar_url(buyer_id, 'buyer'),
                        'avatar': sender_avatar if row[1] == buyer_id else get_user_avatar_url(buyer_id, 'buyer'),
                    })(),
                    'seller': type('obj', (object,), {
                        'first_name': row[7] if row[1] == seller_id else '',
                        'last_name': row[8] if row[1] == seller_id else ''
                    })(),
                    'product': type('obj', (object,), {
                        'id': row[10],
                        'name': row[11],
                        'price': float(row[12]) if row[12] else 0,
                        'image_filename': row[13]
                    })() if row[10] else None
                })()
                chat_thread.append(msg_obj)
        
        # Get seller's products for quick product sharing
        products = Product.query.filter_by(seller_id=seller_id, status='active').all()
        
        # Get seller's store logo from SellerApplication
        seller_app = SellerApplication.query.filter_by(user_id=seller_id, status='approved').first()
        seller_store_logo = seller_app.store_logo if seller_app and seller_app.store_logo else url_for('static', filename='uploads/seller_avatar_placeholder.png')
        
        quick_replies = [
            "Hello! How can I help you today?",
            "This product is available.",
            "Shipping is usually 1-3 days.",
            "Thank you for your order!"
        ]
        
        # Calculate unread chat count for sidebar badge
        unread_chat_count = db.session.execute(text("""
            SELECT COUNT(*) FROM chat_message
            WHERE receiver_id = :seller_id
            AND sender_id != :seller_id
            AND is_read = FALSE
        """), {'seller_id': seller_id}).scalar() or 0
        
        return render_template(
            'seller/inbox.html',
            buyers=buyers,
            chat_thread=chat_thread,
            products=products,
            quick_replies=quick_replies,
            selected_buyer_id=buyer_id,
            unread_chat_count=unread_chat_count,
            seller_store_logo=seller_store_logo
        )
        
    except Exception as e:
        print(f"[ERROR] seller_inbox: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading inbox', 'error')
        return redirect(url_for('seller_dashboard'))



@app.route('/rider-register')
def rider_register():
    """Public rider registration entry point.

    Shows the dedicated rider signup form, which posts to /register with role="rider".
    """
    return render_template('rider/register.html')


# -----------------------------
# Rider Dashboard and API
# -----------------------------

@app.route('/rider')
@login_required
@rider_required
def rider_dashboard():
    user_id = session['user_id']
    user = db.session.get(User, user_id)
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(20).all()
    unread_notifications_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()

    earnings_today = get_user_earnings(user_id, 'today')
    earnings_week = get_user_earnings(user_id, 'week')
    earnings_month = get_user_earnings(user_id, 'month')

    # Completed deliveries count (delivered by this rider)
    completed_deliveries = Order.query.filter(
        Order.delivered_by == user_id,
        Order.status.in_(['delivered', 'completed'])
    ).count()

    # Rider payout metrics
    delivered_not_completed = Order.query.filter(
        Order.picked_up_by == user_id,
        Order.status == 'delivered'
    ).all()
    pending_payout_amount = sum(float(o.delivery_fee) if hasattr(o, 'delivery_fee') and o.delivery_fee else 36.0 for o in delivered_not_completed)
    released_amount = WalletTransaction.query.with_entities(db.func.coalesce(db.func.sum(WalletTransaction.amount), 0.0))\
        .filter_by(user_id=user_id, type='credit', source='order_commission').scalar() or 0.0

    # Earnings trend (last 14 days)
    from sqlalchemy import func
    days = 14
    base_q = db.session.query(
        func.date(WalletTransaction.created_at).label('d'),
        func.coalesce(func.sum(WalletTransaction.amount), 0.0).label('amt')
    ).filter(
        WalletTransaction.user_id == user_id,
        WalletTransaction.type == 'credit',
        WalletTransaction.source == 'order_commission'
    ).group_by(func.date(WalletTransaction.created_at)).all()
    by_date = {str(d): float(a) for d, a in base_q}
    from datetime import date, timedelta
    labels = []
    values = []
    today = date.today()
    for i in range(days-1, -1, -1):
        dt = today - timedelta(days=i)
        key = dt.strftime('%Y-%m-%d')
        labels.append(key)
        values.append(round(by_date.get(key, 0.0), 2))

    # Available orders for immediate render (subset)
    available_orders = Order.query.filter_by(status='ready_for_pickup').order_by(Order.created_at.asc()).limit(20).all()

    # Active orders for this rider
    active_orders = Order.query.filter(
        Order.picked_up_by == user_id,
        Order.status.in_(['to_ship', 'in_transit'])
    ).order_by(Order.updated_at.desc()).all()

    is_online = user.status == 'active'

# Return pickups counters for quick access on dashboard
    returns_available_count = ReturnPickup.query.filter_by(status='available').count()
    returns_active_count = ReturnPickup.query.filter(ReturnPickup.rider_id==user_id, ReturnPickup.status.in_(['waiting_rider_pickup','rider_picked_up','rider_delivered_to_seller'])).count()

    return render_template('rider/dashboard.html',
                           rider=user,
                           notifications=notifications,
                           earnings_today=earnings_today,
                           earnings_week=earnings_week,
                           earnings_month=earnings_month,
                           completed_deliveries=completed_deliveries,
                           pending_payout_amount=pending_payout_amount,
                           released_amount=released_amount,
                           is_online=is_online,
                           earnings_labels=labels,
                           earnings_values=values,
                           available_orders=available_orders,
                           active_orders=active_orders,
                           returns_available_count=returns_available_count,
                           returns_active_count=returns_active_count,
                           unread_notifications_count=unread_notifications_count)


@app.route('/rider/orders')
@login_required
@rider_required
def rider_orders_list():
    user_id = session['user_id']
    status = request.args.get('status', 'all')
    search = request.args.get('q', '').strip()
    date_from = request.args.get('from')
    date_to = request.args.get('to')

    # Incoming ready_for_pickup orders (not yet assigned)
    incoming_q = Order.query.filter_by(status='ready_for_pickup')

    # My orders
    my_q = Order.query.filter(Order.picked_up_by == user_id)

    # Apply filters to my orders
    if status != 'all':
        my_q = my_q.filter(Order.status == status)
    if search:
        my_q = my_q.join(User, Order.buyer_id == User.id).filter(
            db.or_(db.cast(Order.id, db.String).ilike(f"%{search}%"),
                   User.first_name.ilike(f"%{search}%"),
                   User.last_name.ilike(f"%{search}%"))
        )
    from datetime import datetime as _dt
    try:
        if date_from:
            my_q = my_q.filter(Order.created_at >= _dt.strptime(date_from, '%Y-%m-%d'))
        if date_to:
            my_q = my_q.filter(Order.created_at <= _dt.strptime(date_to, '%Y-%m-%d'))
    except Exception:
        pass

    incoming_orders = incoming_q.order_by(Order.created_at.asc()).all()
    my_orders = my_q.order_by(Order.created_at.desc()).all()

    return render_template('rider/orders.html', incoming_orders=incoming_orders, my_orders=my_orders, status=status, q=search, date_from=date_from or '', date_to=date_to or '')


@app.route('/rider/orders/<int:order_id>')
@login_required
@rider_required
def rider_order_detail(order_id):
    user_id = session['user_id']
    order = Order.query.get_or_404(order_id)
    # Allow viewing if it's ready or belongs to rider
    if not (order.status == 'ready_for_pickup' or order.picked_up_by == user_id):
        flash('You are not allowed to view this order.', 'error')
        return redirect(url_for('rider_orders_list'))

    # Ensure QR code exists
    if not getattr(order, 'qr_code', None):
        try:
            order.qr_code = generate_qr_code(order.id)
            db.session.commit()
        except Exception:
            db.session.rollback()
    qr_img_b64 = create_qr_image(order.qr_code) if order.qr_code else None

    # Resolve seller info (first item)
    seller = None
    store_name = None
    pickup_address = None
    try:
        first_item = order.items[0] if order.items else None
        if first_item:
            seller = first_item.product.seller
            appq = SellerApplication.query.filter_by(user_id=seller.id, status='approved').first()
            store_name = appq.store_name if appq else None
            pickup_address = appq.business_address if appq else None
    except Exception:
        pass

    return render_template('rider/order_detail.html', order=order, qr_img_b64=qr_img_b64, seller=seller, store_name=store_name, pickup_address=pickup_address)


@app.route('/rider/profile')
@login_required
@rider_required
def rider_profile_settings():
    user = db.session.get(User, session['user_id'])
    return render_template('rider/profile.html', user=user, rider_profile=user)


@app.route('/rider/profile', methods=['POST'])
@login_required
@rider_required
def rider_profile_update():
    user = db.session.get(User, session['user_id'])

    # Update personal info
    first = request.form.get('first_name', user.first_name).strip()
    last = request.form.get('last_name', user.last_name).strip()
    phone_raw = request.form.get('phone', user.phone or '').strip()
    phone_digits = ''.join(ch for ch in (phone_raw or '') if ch.isdigit())
    if phone_digits and len(phone_digits) != 11:
        flash('Contact number must be exactly 11 digits.', 'danger')
        return redirect(url_for('rider_profile_settings'))

    user.first_name = first or user.first_name
    user.last_name = last or user.last_name
    if phone_digits:
        user.phone = phone_digits

    user.address = request.form.get('address', user.address or '')

    # ID document upload
    idf = request.files.get('id_document')
    if idf and idf.filename:
        safe = secure_filename(idf.filename)
        filename = datetime.utcnow().strftime('%Y%m%d_%H%M%S_') + safe
        dest_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'documents')
        os.makedirs(dest_dir, exist_ok=True)
        idf.save(os.path.join(dest_dir, filename))
        user.valid_id = f"/static/uploads/documents/{filename}"

    # Avatar upload
    file = request.files.get('avatar')
    if file and file.filename:
        try:
            from PIL import Image
            avatar_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'user_avatars')
            os.makedirs(avatar_dir, exist_ok=True)
            temp_path = os.path.join(avatar_dir, f"tmp_user_{user.id}")
            file.save(temp_path)
            img = Image.open(temp_path)
            img = img.convert('RGB')
            img.thumbnail((256, 256))
            final_name = f"user_avatar_{user.id}.png"
            img.save(os.path.join(avatar_dir, final_name), format='PNG')
            user.profile_picture = f"/static/uploads/user_avatars/{final_name}"
        except Exception:
            pass
        finally:
            try:
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass

    db.session.commit()
    
    # Update session user_name to reflect changes in dropdown
    session['user_name'] = f"{user.first_name} {user.last_name}"
    
    # Update session with new avatar URL for immediate dropdown update
    avatar_rel = os.path.join('user_avatars', f"user_avatar_{user.id}.png")
    upload_root = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    avatar_path = os.path.join(upload_root, avatar_rel)
    if os.path.exists(avatar_path):
        avatar_path_normalized = avatar_rel.replace("\\", "/")
        session['navbar_avatar_url'] = url_for('static', filename=f'uploads/{avatar_path_normalized}')
        session['avatar_timestamp'] = int(time.time())  # Force cache refresh
    
    flash('Profile updated successfully.', 'success')
    return redirect(url_for('rider_profile_settings'))


@app.route('/rider/notifications')
@login_required
@rider_required
def rider_notifications():
    user_id = session['user_id']
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    Notification.query.filter_by(user_id=user_id, is_read=False).update({Notification.is_read: True})
    db.session.commit()
    
    # Convert to dict for JSON serialization
    notifications_data = [{
        'id': n.id,
        'message': n.message,
        'title': n.title,
        'image_url': n.image_url,
        'link': n.link,
        'type': n.type,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat() if n.created_at else None,
        'order_id': n.order_id,
        'images': n.images
    } for n in notifications]
    
    return render_template('rider/notifications.html', notifications=notifications_data)


@app.route('/rider/toggle-availability', methods=['POST'])
@login_required
@rider_required
def rider_toggle_availability():
    user_id = session['user_id']
    rp = DeliveryPersonnel.query.filter_by(user_id=user_id).first()
    if not rp:
        return jsonify({'success': False, 'message': 'No rider profile found.'}), 400
    # Toggle between on_duty and off_duty
    rp.status = 'off_duty' if rp.status == 'on_duty' else 'on_duty'
    db.session.commit()
    return jsonify({'success': True, 'status': rp.status})


@app.route('/rider/orders/available')
@login_required
@rider_required
def rider_available_orders():
    # Only show orders marked ready_for_pickup (not yet accepted). In this flow, orders are single-seller.
    orders = Order.query.filter_by(status='ready_for_pickup').order_by(Order.created_at.asc()).all()

    def _default_coords(uid):
        addr = Address.query.filter_by(user_id=uid, is_default=True).first()
        if addr and addr.latitude is not None and addr.longitude is not None:
            return float(addr.latitude), float(addr.longitude)
        return None, None

    def _haversine_km(lat1, lon1, lat2, lon2):
        from math import radians, sin, cos, asin, sqrt
        R = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
        c = 2*asin(sqrt(a))
        return R*c

    as_dict = []
    for o in orders:
        # Resolve primary seller and pickup address (best-effort)
        seller = o.items[0].product.seller if o.items else None
        seller_name = f"{seller.first_name} {seller.last_name}" if seller else "Seller"
        pickup_address = None
        try:
            if seller and getattr(seller, 'seller_applications', None):
                appq = seller.seller_applications.filter_by(status='approved').first()
                if appq and appq.business_address:
                    pickup_address = appq.business_address
        except Exception:
            pickup_address = None

        # Distance best-effort: default addresses if both sides have coordinates
        dist_km = None
        try:
            if seller:
                s_lat, s_lon = _default_coords(seller.id)
                b_lat, b_lon = _default_coords(o.buyer_id)
                if s_lat is not None and b_lat is not None:
                    dist_km = round(_haversine_km(s_lat, s_lon, b_lat, b_lon), 1)
        except Exception:
            dist_km = None

        as_dict.append({
            'id': o.id,
            'total_amount': float(o.total_amount),
            'created_at': o.created_at.isoformat(),
            'seller_ids': list({it.product.seller_id for it in o.items}),
            'seller_name': seller_name,
            'pickup_address': pickup_address,
            'dropoff_address': o.shipping_address,
            'fare_estimate': round(float(o.delivery_fee) if hasattr(o, 'delivery_fee') and o.delivery_fee else 36.0, 2),
            'distance_km': dist_km
        })
    return jsonify({'orders': as_dict})


def _order_seller_ids(order):
    return list({it.product.seller_id for it in order.items})


def _emit_order_update(event_name, order):
    payload = {
        'order_id': order.id,
        'status': order.status,
        'total_amount': order.total_amount
    }
    # Push to buyer
    try:
        socketio.emit(event_name, payload, room=f'user_{order.buyer_id}')
    except Exception:
        pass
    # Push to each seller involved
    for sid in _order_seller_ids(order):
        try:
            socketio.emit(event_name, payload, room=f'user_{sid}')
        except Exception:
            pass


def _compute_seller_stats(seller_id: int) -> dict:
    """Compute seller stats used by dashboard and real-time updates."""
    from sqlalchemy import func, distinct
    # Total orders containing this seller's products
    total_orders = db.session.query(func.count(distinct(Order.id))).join(OrderItem).join(Product)\
        .filter(Product.seller_id == seller_id).scalar() or 0

    # Delivered + completed revenue (seller-side item sum)
    delivered_statuses = ['delivered', 'completed']
    delivered_revenue = db.session.query(func.coalesce(func.sum(OrderItem.price_at_time * OrderItem.quantity), 0.0))\
        .join(Order).join(Product).filter(
            Product.seller_id == seller_id,
            Order.status.in_(delivered_statuses)
        ).scalar() or 0.0

    # Commissioned sales (wallet credits already released)
    commissioned_sales = db.session.query(func.coalesce(func.sum(WalletTransaction.amount), 0.0))\
        .filter(
            WalletTransaction.user_id == seller_id,
            WalletTransaction.type == 'credit',
            WalletTransaction.source == 'order_commission'
        ).scalar() or 0.0

    # Order status breakdown for this seller (distinct orders per status)
    def _status_count(st):
        return db.session.query(func.count(distinct(Order.id))).join(OrderItem).join(Product).filter(
            Product.seller_id == seller_id,
            Order.status == st
        ).scalar() or 0

    status_counts = {
        'pending': _status_count('pending'),
        'ready_for_pickup': _status_count('ready_for_pickup'),
        'completed': _status_count('completed'),
        'cancelled': _status_count('cancelled'),
        'delivered': _status_count('delivered')
    }

    return {
        'total_orders': int(total_orders),
        'delivered_revenue': float(delivered_revenue),
        'commissioned_sales': float(commissioned_sales),
        'status_counts': status_counts
    }


def _emit_seller_stats_update(seller_id: int):
    try:
        stats = _compute_seller_stats(seller_id)
        socketio.emit('seller_stats_update', stats, room=f'user_{seller_id}')
    except Exception:
        pass


def _deduct_stock_for_order_if_needed(order: 'Order'):
    """Idempotently deduct real stock for all products in the order if not yet deducted."""
    if getattr(order, 'stock_deducted', False):
        return
    complete_stock_reservation(order.id)


@app.route('/rider/order/<int:order_id>/json')
@login_required
@rider_required
def rider_order_json(order_id):
    order = Order.query.get_or_404(order_id)
    # Rider can view only if ready_for_pickup or assigned to them
    if order.status not in ['ready_for_pickup','to_ship','in_transit','delivered']:
        return jsonify({'error':'Not viewable'}), 403
    if order.status != 'ready_for_pickup' and order.picked_up_by != session['user_id']:
        return jsonify({'error':'Not viewable'}), 403

    # Ensure QR exists and prepare base64 image for modal
    if not getattr(order, 'qr_code', None):
        try:
            order.qr_code = generate_qr_code(order.id)
            db.session.commit()
        except Exception:
            db.session.rollback()
    qr_img_b64 = create_qr_image(order.qr_code) if order.qr_code else None

    # Seller + store info (first seller in order)
    seller = None
    store_name = None
    pickup_address = None
    try:
        first_item = order.items[0] if order.items else None
        if first_item:
            seller = first_item.product.seller
            appq = SellerApplication.query.filter_by(user_id=seller.id, status='approved').first()
            store_name = appq.store_name if appq else None
            pickup_address = appq.business_address if appq else None
    except Exception:
        pass

    items = []
    for it in order.items:
        items.append({
            'name': it.product.name,
            'qty': it.quantity,
            'price': float(it.price_at_time),
            'seller_id': it.product.seller_id
        })

    return jsonify({
        'id': order.id,
        'buyer': {
            'name': f"{order.buyer.first_name} {order.buyer.last_name}",
            'phone': order.buyer.phone,
            'email': order.buyer.email
        },
        'shipping_address': order.shipping_address,
        'total_amount': float(order.total_amount),
        'items': items,
        'status': order.status,
        'seller': {
            'name': f"{seller.first_name} {seller.last_name}" if seller else None,
            'store_name': store_name,
        },
        'pickup_address': pickup_address,
        'qr_code': order.qr_code,
        'qr_image': (f"data:image/png;base64,{qr_img_b64}" if qr_img_b64 else None)
    })

@app.route('/rider/order/<int:order_id>/mark-delivered', methods=['POST'])
@login_required
@rider_required
def rider_mark_delivered(order_id):
    """Rider marks an order as delivered (moves from to_ship to delivered)."""
    order = Order.query.get_or_404(order_id)
    
    # Verify this order is assigned to this rider and in correct status
    if order.picked_up_by != session['user_id'] or order.status != 'to_ship':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Order cannot be marked as delivered.'})
        flash('Order cannot be marked as delivered.', 'error')
        return redirect(url_for('rider_orders_list'))
    
    try:
        # Update order status
        order.status = 'delivered'
        order.updated_at = datetime.utcnow()

        # Finalize the reserved stock lock on delivery.
        if not order.stock_deducted:
            complete_stock_reservation(order.id)
            app.logger.info(f'Order {order.id} delivered: reserved stock finalized')
        
        db.session.commit()
        
        
        # Send notifications to buyer and sellers
        try:
            push_notification(order.buyer_id, f'Order #{order.id} has been delivered! Please confirm receipt.')
            for seller_id in _order_seller_ids(order):
                push_notification(seller_id, f'Order #{order.id} has been delivered to buyer.')
        except Exception:
            pass
        
        # Emit socket events for real-time updates
        _emit_order_update('order_delivered', order)
        
        # Update seller stats
        for seller_id in _order_seller_ids(order):
            _emit_seller_stats_update(seller_id)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Order marked as delivered.'})
        flash('Order marked as delivered successfully.', 'success')
        return redirect(url_for('rider_orders_list'))
        
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Error marking order as delivered.'})
        flash('Error marking order as delivered. Please try again.', 'error')
        return redirect(url_for('rider_orders_list'))


@app.route('/buyer/order/<int:order_id>/confirm-receipt', methods=['POST'])
@login_required
def buyer_confirm_receipt(order_id):
    """Buyer confirms order receipt (moves from delivered to completed)."""
    order = Order.query.get_or_404(order_id)
    
    # Verify this order belongs to the buyer and is in delivered status
    if order.buyer_id != session['user_id'] or order.status != 'delivered':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Order cannot be confirmed.'})
        flash('Order cannot be confirmed.', 'error')
        return redirect(url_for('my_orders'))
    
    try:
        # Update order status
        order.status = 'completed'
        order.updated_at = datetime.utcnow()
        
        # ℹ️ RULE 4: ORDER COMPLETION DOES NOT RETURN STOCK
        # Stock was already deducted when order was placed, so no action needed here
        # Even if all stocks are bought, product stays Out of Stock
        app.logger.info(f'Order {order.id} completed: No stock action taken (already deducted at order placement)')
        
        db.session.commit()
        
        
        # Release commissions to rider, sellers, and admins
        # Rider gets delivery_fee, sellers get 85% split, admins get 15%
        _release_commissions(order)
        
        # Use Shopee-style notification for order completion
        try:
            notify_order_completed(order)
        except Exception as e:
            app.logger.error(f"Failed to send Shopee-style notification: {e}")
        
        # Emit socket events for real-time updates
        _emit_order_update('order_completed', order)
        
        # Update seller stats
        for seller_id in _order_seller_ids(order):
            _emit_seller_stats_update(seller_id)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Order confirmed and completed!'})
        flash('Order confirmed successfully! Thank you for your purchase.', 'success')
        return redirect(url_for('my_orders'))
        
    except Exception as e:
        db.session.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Error confirming order.'})
        flash('Error confirming order. Please try again.', 'error')
        return redirect(url_for('my_orders'))


def _order_seller_ids(order):
    """Helper function to get all seller IDs for an order."""
    return list(set(item.product.seller_id for item in order.items))


def _emit_seller_stats_update(seller_id):
    """Emit real-time stats update to seller."""
    try:
        # Import socketio here to avoid circular imports
        from flask_socketio import emit
        socketio.emit('stats_update', room=f'seller_{seller_id}')
    except Exception:
        pass


@app.route('/rider/order/<int:order_id>/accept', methods=['POST'])
@login_required
@rider_required
def rider_accept_order(order_id):
    # Race condition prevention: check status and rider_id in one query
    order = Order.query.filter_by(id=order_id, status='ready_for_pickup', rider_id=None).first()
    
    if not order:
        # Order was already taken by another rider
        flash('This order has already been accepted by another rider.', 'error')
        return redirect(url_for('rider_dashboard'))
    
    # Assign rider and update status atomically
    order.rider_id = session['user_id']
    order.picked_up_by = session['user_id']
    order.picked_up_at = datetime.utcnow()
    order.status = 'accepted_by_rider'
    order.updated_at = datetime.utcnow()
    db.session.commit()
        

    # Notify buyer and sellers
    push_notification(order.buyer_id, f'Rider accepted order #{order.id}.')
    for sid in _order_seller_ids(order):
        push_notification(sid, f'Your order #{order.id} was accepted by a rider.')

    # Broadcast to all riders that order is taken
    socketio.emit('order_taken', {'order_id': order.id}, broadcast=True)
    
    _emit_order_update('order_accepted', order)
    flash('Order accepted.', 'success')
    return redirect(url_for('rider_dashboard'))


@app.route('/rider/order/<int:order_id>/reject', methods=['POST'])
@login_required
@rider_required
def rider_reject_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != 'ready_for_pickup':
        flash('Order is not available for rejection.', 'error')
        return redirect(url_for('rider_dashboard'))

    # Order remains in ready_for_pickup status for other riders to see
    # Just remove it from this rider's view
    flash('Order rejected. Available for other riders.', 'info')
    return redirect(url_for('rider_dashboard'))


@app.route('/rider/order/<int:order_id>/picked-up', methods=['POST'])
@login_required
@rider_required
def rider_mark_picked_up(order_id):
    order = Order.query.get_or_404(order_id)
    if order.picked_up_by != session['user_id']:
        flash('You cannot mark this order as picked up.', 'error')
        return redirect(url_for('rider_dashboard'))
    # Normalize to new flow: picked up => to_ship
    order.status = 'to_ship'
    if not order.picked_up_at:
        order.picked_up_at = datetime.utcnow()
    db.session.commit()

    push_notification(order.buyer_id, f'Rider picked up order #{order.id}.')
    for sid in _order_seller_ids(order):
        push_notification(sid, f'Order #{order.id} picked up by rider.')

    _emit_order_update('order_picked_up', order)
    flash('Order marked as picked up.', 'success')
    return redirect(url_for('rider_dashboard'))


@app.route('/rider/active/<int:order_id>')
@login_required
@rider_required
def rider_active_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.picked_up_by != session['user_id'] and order.status not in ['ready_for_pickup','to_ship','in_transit','delivered']:
        flash('Not allowed to view this order.', 'error')
        return redirect(url_for('rider_dashboard'))
    # Resolve pickup address
    seller = order.items[0].product.seller if order.items else None
    pickup_address = None
    try:
        if seller and getattr(seller, 'seller_applications', None):
            appq = seller.seller_applications.filter_by(status='approved').first()
            if appq and appq.business_address:
                pickup_address = appq.business_address
    except Exception:
        pickup_address = None
    # Buyer default address for lat/lng
    s_lat = s_lon = b_lat = b_lon = None
    try:
        s_addr = Address.query.filter_by(user_id=seller.id, is_default=True).first() if seller else None
        b_addr = Address.query.filter_by(user_id=order.buyer_id, is_default=True).first()
        if s_addr and s_addr.latitude is not None and s_addr.longitude is not None:
            s_lat, s_lon = float(s_addr.latitude), float(s_addr.longitude)
        if b_addr and b_addr.latitude is not None and b_addr.longitude is not None:
            b_lat, b_lon = float(b_addr.latitude), float(b_addr.longitude)
    except Exception:
        pass
    return render_template('rider/active.html', order=order, pickup_address=pickup_address,
                           s_lat=s_lat, s_lon=s_lon, b_lat=b_lat, b_lon=b_lon)


@app.route('/rider/order/<int:order_id>/problem', methods=['POST'])
@login_required
@rider_required
def rider_problem_report(order_id):
    order = Order.query.get_or_404(order_id)
    if order.picked_up_by and order.picked_up_by != session['user_id']:
        return jsonify({'success': False, 'message': 'Not allowed'}), 403
    note = request.form.get('note', '').strip() or 'Problem reported by rider.'
    order.delivery_notes = (order.delivery_notes or '') + f"\n[{datetime.utcnow().isoformat()}] {note}"
    db.session.commit()
    push_notification(order.buyer_id, f'Rider reported a delivery issue for Order #{order.id}.')
    for sid in _order_seller_ids(order):
        push_notification(sid, f'Rider reported a delivery issue for Order #{order.id}.')
    return jsonify({'success': True})


@app.route('/rider/order/<int:order_id>/cancel', methods=['POST'])
@login_required
@rider_required
def rider_cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status not in ['ready_for_pickup', 'to_ship', 'in_transit'] or \
       (order.picked_up_by and order.picked_up_by != session['user_id']):
        flash('You cannot cancel this order now.', 'error')
        return redirect(url_for('rider_dashboard'))

    order.status = 'cancelled'
    order.updated_at = datetime.utcnow()
    # Reset assignment if any
    if order.picked_up_by == session['user_id']:
        order.picked_up_by = None
    db.session.commit()
        

    push_notification(order.buyer_id, f'Order #{order.id} was cancelled by rider.')
    for sid in _order_seller_ids(order):
        push_notification(sid, f'Order #{order.id} was cancelled by rider.')

    _emit_order_update('order_cancelled', order)
    flash('Order cancelled.', 'info')
    return redirect(url_for('rider_dashboard'))


@app.route('/registration-status')
def registration_status():
    """Simple confirmation view shown after a successful registration.

    Displays a professional confirmation message and current review status
    for buyers and riders (front-end status only).
    """
    role = (request.args.get('role') or 'buyer').strip().lower()
    if role not in ('buyer', 'rider'):
        role = 'buyer'
    return render_template('registration_status.html', role=role)


@app.route('/admin/approve-rider/<int:app_id>', methods=['GET', 'POST'])
@admin_required
def approve_rider(app_id):
    application = RiderApplication.query.get_or_404(app_id)
    application.status = 'approved'
    application.reviewed_at = datetime.utcnow()
    application.reviewed_by = session['user_id']
    
    # Set user role to 'rider' and status to 'active'
    application.user.role = 'rider'
    application.user.status = 'active'
    application.user.email_verified = True  # Treat admin approval as verification
    db.session.commit()
    
    # In-app notification
    try:
        db.session.add(Notification(
            user_id=application.user.id, 
            message='Your rider application has been approved! You can now start accepting delivery orders.'
        ))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to create notification for rider {application.user.id}: {e}")
    
    # Send approval email
    try:
        send_rider_status_email(application.user.email, approved=True, user_name=f"{application.user.first_name} {application.user.last_name}")
    except Exception as e:
        app.logger.exception(f"Failed to send approval email to {application.user.email}: {e}")
    
    flash('Rider application approved successfully!', 'success')
    return redirect(url_for('admin_rider_applications'))


@app.route('/admin/reject-rider/<int:app_id>', methods=['POST'])
@admin_required
def reject_rider(app_id):
    application = RiderApplication.query.get_or_404(app_id)
    application.status = 'rejected'
    application.reviewed_at = datetime.utcnow()
    application.reviewed_by = session['user_id']
    
    # Get rejection reason from form if provided
    reason = request.form.get('reason', '')
    
    # Set user status to rejected
    application.user.status = 'rejected'
    db.session.commit()
    
    # In-app notification
    try:
        db.session.add(Notification(
            user_id=application.user.id, 
            message='Your rider application was not approved. Please contact support for more information.'
        ))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to create notification for rider {application.user.id}: {e}")
    
    # Send rejection email
    try:
        send_rider_status_email(
            application.user.email, 
            approved=False, 
            user_name=f"{application.user.first_name} {application.user.last_name}",
            reason=reason
        )
    except Exception as e:
        app.logger.exception(f"Failed to send rejection email to {application.user.email}: {e}")
    
    flash('Rider application rejected.', 'info')
    return redirect(url_for('admin_rider_applications'))




@app.route('/seller/send-message/<int:buyer_id>', methods=['POST'])
@login_required
def send_chat_message(buyer_id):
    """Send message from seller to buyer using unified chat_message table"""
    try:
        seller_id = session['user_id']
        
        # Get message from form or JSON
        if request.is_json:
            data = request.get_json()
            message = data.get('message', '').strip()
            product_id = data.get('product_id')
        else:
            message = request.form.get('message', '').strip()
            product_id = request.form.get('product_id')
        
        if not message:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Message is required'}), 400
            flash('Message is required', 'error')
            return redirect(url_for('seller_inbox', buyer_id=buyer_id))
        
        from sqlalchemy import text
        
        # Insert message into chat_message table
        result = db.session.execute(text("""
            INSERT INTO chat_message (sender_id, receiver_id, message, product_id, is_read, created_at)
            VALUES (:sender_id, :receiver_id, :message, :product_id, FALSE, :created_at)
            RETURNING id, created_at
        """), {
            'sender_id': seller_id,
            'receiver_id': buyer_id,
            'message': message,
            'product_id': product_id if product_id else None,
            'created_at': datetime.utcnow()
        })
        
        msg_row = result.fetchone()
        db.session.commit()
        
        # Send real-time notification via Socket.IO
        try:
            seller_result = db.session.execute(text("""
                SELECT first_name, last_name FROM "user" WHERE id = :seller_id
            """), {'seller_id': seller_id})
            seller_row = seller_result.fetchone()
            
            if seller_row:
                socketio.emit('new_message', {
                    'message_id': msg_row[0],
                    'sender_id': seller_id,
                    'sender_name': f"{seller_row[0]} {seller_row[1]}",
                    'sender_role': 'seller',
                    'message': message,
                    'product_id': product_id,
                    'created_at': msg_row[1].isoformat()
                }, room=f'user_{buyer_id}')
                
                # Also send push notification
                push_notification(
                    buyer_id,
                    'New message from seller.',
                    type='chat',
                    link=url_for('chat_window', seller_id=seller_id) if 'chat_window' in dir() else None,
                    actor_user_id=seller_id
                )
        except Exception as e:
            print(f"[WARNING] Socket.IO/notification failed: {e}")
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': {
                    'id': msg_row[0],
                    'sender_id': seller_id,
                    'receiver_id': buyer_id,
                    'message': message,
                    'created_at': msg_row[1].isoformat()
                }
            })
        else:
            flash('Message sent successfully', 'success')
            return redirect(url_for('seller_inbox', buyer_id=buyer_id))
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] send_chat_message: {e}")
        import traceback
        traceback.print_exc()
        
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash('Error sending message', 'error')
            return redirect(url_for('seller_inbox', buyer_id=buyer_id))


@app.route('/send-message/<int:seller_id>', methods=['POST'])
@login_required
def send_message(seller_id):
    buyer_id = session['user_id']
    message = request.form['message']
    product_id = request.form.get('product_id')
    chat_msg = StoreChatMessage(
        buyer_id=buyer_id,
        seller_id=seller_id,
        product_id=product_id if product_id else None,
        message=message,
        sender_role='buyer'
    )
    db.session.add(chat_msg)
    db.session.commit()
    try:
        push_notification(
            seller_id,
            'New message from a buyer.',
            type='chat',
            link=url_for('seller_inbox', buyer_id=buyer_id),
            actor_user_id=buyer_id
        )
    except Exception:
        pass
    try:
        socketio.emit('new_message', {
            'from_user_id': buyer_id,
            'to_user_id': seller_id,
            'sender_role': 'buyer',
            'message': message
        }, room=f'user_{seller_id}')
    except Exception:
        pass
    return redirect(url_for('chat_window', seller_id=seller_id))

# ===== Return & Refund Routes =====
@app.route('/buyer/returns')
@login_required
def buyer_returns_index():
    rr = ReturnRequest.query.filter(
        ReturnRequest.buyer_id == session['user_id'],
        ReturnRequest.status != 'cancelled'
    ).order_by(ReturnRequest.created_at.desc()).all()
    return render_template('buyer/returns_index.html', requests=rr)

@app.route('/buyer/returns/new/<int:order_item_id>', methods=['GET','POST'])
@login_required
def buyer_new_return(order_item_id):
    item = OrderItem.query.get_or_404(order_item_id)
    order = Order.query.get_or_404(item.order_id)
    if order.buyer_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('my_orders'))
    # Eligibility: delivered OR completed within 7 days
    eligible = False
    if order.status == 'delivered':
        eligible = True
    elif order.status == 'completed':
        try:
            if order.delivered_at and (datetime.utcnow() - order.delivered_at) <= timedelta(days=7):
                eligible = True
        except Exception:
            eligible = False
    if not eligible:
        flash('Return/Refund can only be requested after delivery and within 7 days of completion.', 'warning')
        return redirect(url_for('my_orders'))

    # Prevent duplicate active request for same item
    dup = ReturnRequest.query.filter(
        ReturnRequest.order_item_id == item.id,
        ReturnRequest.status.in_(['submitted','waiting_seller_approval','refund_approved','return_approved','waiting_rider_pickup','rider_picked_up_item','rider_delivered_to_seller','seller_checking_item','refund_processing'])
    ).first()
    if dup:
        return redirect(url_for('buyer_return_detail', return_id=dup.id))

    if request.method == 'POST':
        request_type = (request.form.get('request_type') or '').strip().lower()  # 'return' | 'refund'
        reason = (request.form.get('reason') or '').strip()
        reason_other = (request.form.get('reason_other') or '').strip()
        description = (request.form.get('description') or '').strip()
        qty = max(1, min(int(request.form.get('quantity','1') or 1), int(item.quantity)))

        # Server-side validations using unified 'media[]'
        errors = []
        if request_type not in ('return','refund'):
            errors.append('Please select Return or Refund.')
        if not reason:
            errors.append('Please select a reason for your return/refund.')
        if reason == 'Others' and not reason_other:
            errors.append('Please provide the reason details for "Others".')
        media_list = [f for f in request.files.getlist('media[]') if f and f.filename]
        if len(media_list) == 0:
            errors.append('Please upload at least one photo or video as evidence.')
        # limit
        if len(media_list) > 6:
            media_list = media_list[:6]
        if not description:
            errors.append('Please describe the issue in the description box.')

        # Classify by extension
        ALLOWED_IMAGES = {'jpg','jpeg','png'}
        ALLOWED_VIDEOS = {'mp4','mov'}
        imgs = []
        vids = []
        for f in media_list:
            ext = (f.filename.rsplit('.',1)[-1] if '.' in f.filename else '').lower()
            if ext in ALLOWED_IMAGES:
                imgs.append(f)
            elif ext in ALLOWED_VIDEOS:
                vids.append(f)
            else:
                errors.append(f'Unsupported file type: {ext}. Allowed: JPG, PNG, MP4, MOV.')
        # Only keep first video if multiple
        if len(vids) > 1:
            vids = vids[:1]

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('buyer/return_form.html', order=order, item=item)

        rr = ReturnRequest(
            order_id=order.id,
            order_item_id=item.id,
            buyer_id=order.buyer_id,
            seller_id=item.product.seller_id,
            reason=reason,
            reason_other=reason_other if reason == 'Others' else None,
            description=description,
            quantity=qty,
            request_type=request_type,
            status='submitted'
        )
        db.session.add(rr)
        db.session.flush()
        # Evidence uploads
        saved_images = []
        base_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'returns', str(rr.id))
        os.makedirs(os.path.join(base_dir, 'images'), exist_ok=True)
        for f in imgs[:6]:
            name = datetime.utcnow().strftime('%Y%m%d_%H%M%S_') + secure_filename(f.filename)
            f.save(os.path.join(base_dir, 'images', name))
            saved_images.append(f'returns/{rr.id}/images/{name}')
        # Save first video if any
        video_path = None
        if vids:
            os.path.exists(os.path.join(base_dir, 'video')) or os.makedirs(os.path.join(base_dir, 'video'), exist_ok=True)
            v = vids[0]
            vname = datetime.utcnow().strftime('%Y%m%d_%H%M%S_') + secure_filename(v.filename)
            v.save(os.path.join(base_dir, 'video', vname))
            video_path = f'returns/{rr.id}/video/{vname}'
        
        # Update the return request with saved media paths
        rr.images = saved_images if saved_images else None
        rr.video_filename = video_path
        db.session.commit()
        # Update order status (buyer-facing) to indicate submission
        try:
            order.status = 'return_submitted'
            order.updated_at = datetime.utcnow()
        except Exception:
            pass
        db.session.commit()
        
        # Notify seller about return request
        try:
            from shopee_notification_system import create_notification
            create_notification(
                user_id=item.product.seller_id,
                title="Return/Refund Request",
                message=f'Buyer requested return/refund for Order #{order.id} — {item.product.name}. Reason: {reason}',
                notification_type='order',
                order_id=order.id,
                action_url=f'/seller/returns/{rr.id}'
            )
        except Exception as e:
            print(f"Error sending seller notification: {e}")
            # Fallback to push_notification
            push_notification(item.product.seller_id, f'Return/Refund requested for Order #{order.id} — {item.product.name}.')

        # Notify buyer about submission
        try:
            from shopee_notification_system import create_notification
            create_notification(
                user_id=order.buyer_id,
                title="Return Request Submitted",
                message=f'Your return/refund request RR-{rr.id} has been submitted. Seller will review it soon.',
                notification_type='order',
                order_id=order.id,
                action_url=f'/buyer/returns/{rr.id}'
            )
        except Exception as e:
            print(f"Error sending buyer notification: {e}")
            push_notification(order.buyer_id, f'Return/Refund request RR-{rr.id} submitted.')

        _emit_return_update(rr)
        flash('Return/Refund Request Submitted Successfully', 'success')
        return redirect(url_for('buyer_return_detail', return_id=rr.id))

    return render_template('buyer/return_form.html', order=order, item=item)

@app.route('/buyer/returns/<int:return_id>')
@login_required
def buyer_return_detail(return_id):
    rr = ReturnRequest.query.get_or_404(return_id)
    if rr.buyer_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('buyer_returns_index'))
    return render_template('buyer/return_detail.html', rr=rr)

@app.route('/buyer/returns/<int:return_id>/cancel', methods=['POST'])
@login_required
def buyer_return_cancel(return_id):
    rr = ReturnRequest.query.get_or_404(return_id)
    if rr.buyer_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('buyer_returns_index'))
    if rr.status not in ['submitted', 'waiting_seller_approval', 'seller_reviewing']:
        flash('You can cancel only before the seller processes your request.', 'warning')
        return redirect(url_for('buyer_return_detail', return_id=return_id))
    rr.status = 'cancelled'
    db.session.commit()
    push_notification(rr.seller_id, f'Buyer cancelled the return/refund request RR-{rr.id}.')
    flash('Return request cancelled successfully! You can submit a new request anytime.', 'success')
    return redirect(url_for('buyer_returns_index'))

# Seller review actions
@app.route('/seller/returns')
@seller_required
def seller_returns_index():
    seller_id = session['user_id']

    # Get all return requests for this seller EXCEPT cancelled ones
    all_return_requests = ReturnRequest.query.filter(
        ReturnRequest.seller_id == seller_id,
        ReturnRequest.status != 'cancelled'
    ).order_by(ReturnRequest.created_at.desc()).all()

    # Filter pending requests - only show submitted status
    pending_requests = [r for r in all_return_requests if r.status in [
        'submitted', 'seller_reviewing', 'waiting_seller_approval'
    ]]

    # Get completed returns/refunds for this seller - only fully completed ones
    completed_returns = ReturnRequest.query.filter(
        ReturnRequest.seller_id == seller_id,
        ReturnRequest.status.in_(['completed', 'refunded', 'rejected'])
    ).order_by(ReturnRequest.updated_at.desc()).all()

    # Get statistics
    total_requests = len(all_return_requests)
    pending_count = len(pending_requests)
    completed_count = len(completed_returns)
    approved_requests = len([r for r in all_return_requests if r.status in ['waiting_rider_pickup', 'rider_to_seller', 'item_received_by_seller', 'refund_processing', 'refunded']])

    return render_template('seller/returns.html',
                         requests=pending_requests,  # Only pending requests
                         completed_returns=completed_returns,
                         total_requests=total_requests,
                         pending_requests=pending_count,
                         completed_count=completed_count,
                         approved_requests=approved_requests)

@app.route('/seller/returns/<int:return_id>')
@seller_required
def seller_return_detail(return_id):
    rr = ReturnRequest.query.get_or_404(return_id)
    if rr.seller_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('seller_returns_index'))
    
    # Mark as under review if this is the first view
    if rr.status == 'submitted':
        rr.status = 'waiting_seller_approval'
        db.session.commit()
    
    def _parse_media_list(value):
        if not value:
            return []
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            if raw.startswith('['):
                try:
                    decoded = json.loads(raw)
                    if isinstance(decoded, list):
                        return [str(v).strip() for v in decoded if str(v).strip()]
                except Exception:
                    pass
            return [raw]
        return []

    def _to_media_url(path):
        if not path:
            return None
        p = str(path).strip()
        if not p:
            return None
        if p.startswith('http://') or p.startswith('https://'):
            return p
        if p.startswith('/static/'):
            return p
        if p.startswith('static/'):
            return f'/{p}'
        clean = p.lstrip('/')
        if clean.startswith('uploads/'):
            return url_for('static', filename=clean)
        return url_for('static', filename=f'uploads/{clean}')

    rr_image_urls = [_to_media_url(v) for v in _parse_media_list(rr.images)]
    rr_image_urls = [u for u in rr_image_urls if u]

    rr_video_urls = [_to_media_url(v) for v in _parse_media_list(rr.video_filename)]
    rr_video_urls = [u for u in rr_video_urls if u]

    product = rr.order_item.product if rr.order_item and rr.order_item.product else None
    if not product and rr.order_item and rr.order_item.product_id:
        product = db.session.get(Product, rr.order_item.product_id)

    product_name = product.name if product else 'Product unavailable'
    product_image_url = None
    if product and product.image_filename:
        product_image_url = _to_media_url(product.image_filename)

    return render_template(
        'seller/return_detail.html',
        rr=rr,
        rr_image_urls=rr_image_urls,
        rr_video_urls=rr_video_urls,
        rr_product_name=product_name,
        rr_product_image_url=product_image_url
    )

@app.route('/seller/returns/<int:return_id>/approve', methods=['POST'])
@seller_required
def seller_return_approve(return_id):
    rr = ReturnRequest.query.get_or_404(return_id)
    if rr.seller_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('seller_returns_index'))
    
    # As requested: when seller accepts, set item to refunded and move to returns tab.
    rr.status = 'refunded'
    rr.processed_at = datetime.utcnow()
    rr.processed_by = session['user_id']

    try:
        amount = float(rr.order_item.price_at_time or 0) * int(rr.quantity or 1)
        if amount > 0:
            credit_wallet(rr.buyer_id, amount, 'return_refund', rr.order_id)
            rr.refund_amount = amount
    except Exception as e:
        app.logger.error(f"Refund processing error: {e}")

    rr.order.status = 'refunded'
    rr.order.payment_status = 'refunded'
    rr.order.updated_at = datetime.utcnow()

    db.session.commit()
    rider_earning_released = _finalize_rider_earning_after_return(rr.order, refund_approved=True)
    
    # Notify buyer about approval and refund
    try:
        from shopee_notification_system import create_notification
        refund_msg = f'₱{rr.refund_amount:.2f}' if hasattr(rr, 'refund_amount') and rr.refund_amount else 'Your payment'
        create_notification(
            user_id=rr.buyer_id,
            title="Return Approved & Refunded",
            message=f'Your return request RR-{rr.id} has been approved. {refund_msg} has been refunded to your wallet.',
            notification_type='payment',
            order_id=rr.order_id,
            action_url=f'/buyer/wallet'
        )
    except Exception as e:
        print(f"Error sending approval notification: {e}")
        # Fallback to push_notification
        push_notification(rr.buyer_id, f'Return request RR-{rr.id} has been approved and refunded.')
    
    rider_id = _order_rider_id(rr.order)
    if rider_id and rider_earning_released:
        push_notification(rider_id, f'Order #{rr.order_id} delivery earnings have been released.')
    _emit_return_update(rr)
    
    return redirect(url_for('seller_return_detail', return_id=return_id))

@app.route('/seller/returns/<int:return_id>/reject', methods=['POST'])
@seller_required
def seller_return_reject(return_id):
    rr = ReturnRequest.query.get_or_404(return_id)
    if rr.seller_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('seller_returns_index'))
    rr.status = 'rejected'
    rr.seller_response_reason = (request.form.get('seller_reason') or 'No reason provided.').strip()
    rr.processed_at = datetime.utcnow()
    rr.processed_by = session['user_id']
    
    # Keep order status as completed when return is rejected
    if rr.order.status != 'completed':
        rr.order.status = 'completed'
        rr.order.updated_at = datetime.utcnow()
    
    db.session.commit()
    _finalize_rider_earning_after_return(rr.order, refund_approved=False)
    
    # Notify buyer about rejection
    try:
        from shopee_notification_system import create_notification
        create_notification(
            user_id=rr.buyer_id,
            title="Return Request Rejected",
            message=f'Your return request RR-{rr.id} for Order #{rr.order_id} was rejected. Reason: {rr.seller_response_reason}',
            notification_type='order',
            order_id=rr.order_id,
            action_url=f'/buyer/orders/{rr.order_id}'
        )
    except Exception as e:
        print(f"Error sending rejection notification: {e}")
        # Fallback to push_notification
        push_notification(rr.buyer_id, f'Return request RR-{rr.id} was rejected. Reason: {rr.seller_response_reason}')
    
    rider_id = _order_rider_id(rr.order)
    if rider_id:
        push_notification(rider_id, f'Order #{rr.order_id} completed. Your delivery earnings have been released.')
    _emit_return_update(rr)
    return redirect(url_for('seller_return_detail', return_id=return_id))

@app.route('/seller/returns/<int:return_id>/mark-received', methods=['POST'])
@seller_required
def seller_return_mark_received(return_id):
    rr = ReturnRequest.query.get_or_404(return_id)
    if rr.seller_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('seller_returns_index'))
    
    # Update status to show seller is checking item
    rr.status = 'seller_checking_item'
    db.session.commit()
    _emit_return_update(rr)
    
    return redirect(url_for('seller_return_detail', return_id=return_id))

@app.route('/seller/returns/<int:return_id>/start-refund', methods=['POST'])
@seller_required
def seller_return_start_refund(return_id):
    rr = ReturnRequest.query.get_or_404(return_id)
    if rr.seller_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('seller_returns_index'))
    rr.status = 'refund_processing'
    db.session.commit()
    _emit_return_update(rr)
    push_notification(rr.buyer_id, f'Refund for RR-{rr.id} is processing.')
    return redirect(url_for('seller_return_detail', return_id=return_id))

@app.route('/seller/returns/<int:return_id>/complete', methods=['POST'])
@seller_required
def seller_return_complete(return_id):
    rr = ReturnRequest.query.get_or_404(return_id)
    if rr.seller_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('seller_returns_index'))
    
    # Credit buyer wallet
    try:
        amount = float(rr.order_item.price_at_time) * int(rr.order_item.quantity)
        credit_wallet(rr.buyer_id, amount, 'return_refund', rr.order_id)
        rr.refund_amount = amount
    except Exception:
        app.logger.exception('Failed to credit refund for RR-%s', rr.id)
    
    # Update status to final refunded state
    rr.status = 'refunded'
    
    # Update order status
    rr.order.status = 'refunded'
    rr.order.payment_status = 'refunded'
    rr.order.updated_at = datetime.utcnow()
    
    db.session.commit()
    rider_earning_released = _finalize_rider_earning_after_return(rr.order, refund_approved=True)
    _emit_return_update(rr)
    push_notification(rr.buyer_id, f'Refund for RR-{rr.id} completed. Amount credited to your wallet.')
    rider_id = _order_rider_id(rr.order)
    if rider_id and rider_earning_released:
        push_notification(rider_id, f'Order #{rr.order_id} delivery earnings have been released.')
    try:
        user = db.session.get(User, rr.buyer_id)
        _send_refund_email(user, amount, rr.order_id)
    except Exception:
        pass
    flash('Return/refund completed successfully.', 'success')
    return redirect(url_for('seller_return_detail', return_id=return_id))

# Rider chat routes
@app.route('/rider/chat/<int:buyer_id>', methods=['GET', 'POST'])
@login_required
@rider_required
def rider_chat_thread(buyer_id):
    rider_id = session['user_id']
    
    # Get ChatMessage model from unified chat system
    ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
    if not ChatMessage:
        buyer = db.session.get(User, buyer_id)
        return render_template('rider/chat.html', thread=[], buyer=buyer, buyer_avatar_url=None)
    
    if request.method == 'POST':
        msg = (request.form.get('message') or '').strip()
        if msg:
            chat_msg = ChatMessage(sender_id=rider_id, receiver_id=buyer_id, message=msg, is_read=False)
            db.session.add(chat_msg)
            db.session.commit()
            try:
                rider_user = db.session.get(User, rider_id)
                rp = DeliveryPersonnel.query.filter_by(user_id=rider_id).first()
                img = getattr(rp, 'photo_path', None) or url_for('static', filename='user_avatar.png')
                push_notification(
                    buyer_id,
                    f"Rider {rider_user.first_name} messaged you.",
                    image_url=img,
                    link=url_for('buyer_rider_chat', rider_id=rider_id),
                    actor_user_id=rider_id,
                    type='chat'
                )
                socketio.emit('chat_rider', {'from': 'rider', 'message': msg}, room=f'user_{buyer_id}')
            except Exception:
                pass
        return redirect(url_for('rider_chat_thread', buyer_id=buyer_id))

    # Load thread and mark buyer messages as read
    from sqlalchemy import or_, and_
    unread_msgs = ChatMessage.query.filter_by(sender_id=buyer_id, receiver_id=rider_id, is_read=False).all()
    for msg in unread_msgs:
        msg.is_read = True
    db.session.commit()
    
    thread = ChatMessage.query.filter(
        or_(
            and_(ChatMessage.sender_id == buyer_id, ChatMessage.receiver_id == rider_id),
            and_(ChatMessage.sender_id == rider_id, ChatMessage.receiver_id == buyer_id)
        )
    ).order_by(ChatMessage.created_at.asc()).all()
    
    buyer = db.session.get(User, buyer_id)
    # Use helper function to get buyer avatar URL
    buyer_avatar_url = get_user_avatar_url(buyer_id, buyer.role if buyer else None)
    return render_template('rider/chat.html', thread=thread, buyer=buyer, buyer_avatar_url=buyer_avatar_url)

@app.route('/buyer/chat/rider/<int:rider_id>', methods=['GET', 'POST'])
@login_required
def buyer_rider_chat(rider_id):
    buyer_id = session['user_id']
    
    # Get ChatMessage model from unified chat system
    ChatMessage = db.Model.registry._class_registry.get('ChatMessage')
    if not ChatMessage:
        rider = db.session.get(User, rider_id)
        rider_profile = DeliveryPersonnel.query.filter_by(user_id=rider_id).first()
        return render_template('buyer/rider_chat.html', thread=[], rider=rider, rider_profile=rider_profile)
    
    # Only buyers should initiate; admins/sellers/riders will still be allowed for simplicity
    if request.method == 'POST':
        msg = (request.form.get('message') or '').strip()
        if msg:
            chat_msg = ChatMessage(sender_id=buyer_id, receiver_id=rider_id, message=msg, is_read=False)
            db.session.add(chat_msg)
            db.session.commit()
            try:
                buyer_user = db.session.get(User, buyer_id)
                img = url_for('static', filename='user_avatar.png')
                push_notification(
                    rider_id,
                    f"Buyer {buyer_user.first_name} sent you a message.",
                    image_url=img,
                    link=url_for('rider_chat_thread', buyer_id=buyer_id),
                    actor_user_id=buyer_id,
                    type='chat'
                )
                socketio.emit('chat_rider', {'from': 'buyer', 'message': msg}, room=f'user_{rider_id}')
            except Exception:
                pass
        return redirect(url_for('buyer_rider_chat', rider_id=rider_id))

    # Mark rider messages as read
    from sqlalchemy import or_, and_
    unread_msgs = ChatMessage.query.filter_by(sender_id=rider_id, receiver_id=buyer_id, is_read=False).all()
    for msg in unread_msgs:
        msg.is_read = True
    db.session.commit()
    
    thread = ChatMessage.query.filter(
        or_(
            and_(ChatMessage.sender_id == buyer_id, ChatMessage.receiver_id == rider_id),
            and_(ChatMessage.sender_id == rider_id, ChatMessage.receiver_id == buyer_id)
        )
    ).order_by(ChatMessage.created_at.asc()).all()
    
    rider = db.session.get(User, rider_id)
    # Rider profile for avatar
    rider_profile = DeliveryPersonnel.query.filter_by(user_id=rider_id).first()
    return render_template('buyer/rider_chat.html', thread=thread, rider=rider, rider_profile=rider_profile)

# Rider flows for return pickups
@app.route('/rider/returns')
@login_required
@rider_required
def rider_returns():
    available = ReturnPickup.query.filter_by(status='available').all()
    active = ReturnPickup.query.filter(ReturnPickup.rider_id==session['user_id'], ReturnPickup.status.in_(['waiting_rider_pickup','rider_picked_up','rider_delivered_to_seller'])).all()
    return render_template('rider/returns.html', available=available, active=active)

@app.route('/rider/returns/<int:task_id>/accept', methods=['POST'])
@login_required
@rider_required
def rider_return_accept(task_id):
    t = ReturnPickup.query.get_or_404(task_id)
    if t.status != 'available':
        flash('Task not available.', 'warning')
        return redirect(url_for('rider_returns'))
    t.status = 'waiting_rider_pickup'
    t.rider_id = session['user_id']
    db.session.commit()
    rr = t.return_request
    rr.status = 'waiting_rider_pickup'
    db.session.commit()
    _emit_return_update(rr, {'pickup_status': t.status})
    push_notification(rr.buyer_id, f'Rider accepted your return pickup RR-{rr.id} and is on the way.')
    return redirect(url_for('rider_returns'))

@app.route('/rider/returns/<int:task_id>/to-pickup', methods=['POST'])
@login_required
@rider_required
def rider_return_to_pickup(task_id):
    t = ReturnPickup.query.get_or_404(task_id)
    if t.rider_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('rider_returns'))
    t.status = 'waiting_rider_pickup'
    db.session.commit()
    rr = t.return_request
    rr.status = 'waiting_rider_pickup'
    db.session.commit()
    _emit_return_update(rr, {'pickup_status': t.status})
    return redirect(url_for('rider_returns'))

@app.route('/rider/returns/<int:task_id>/picked-up', methods=['POST'])
@login_required
@rider_required
def rider_return_picked_up(task_id):
    t = ReturnPickup.query.get_or_404(task_id)
    if t.rider_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('rider_returns'))
    t.status = 'rider_picked_up'
    t.picked_up_at = datetime.utcnow()
    db.session.commit()
    rr = t.return_request
    rr.status = 'rider_picked_up_item'
    db.session.commit()
    _emit_return_update(rr, {'pickup_status': t.status})
    push_notification(rr.buyer_id, f'Rider picked up your return parcel RR-{rr.id}.')
    return redirect(url_for('rider_returns'))

@app.route('/rider/returns/<int:task_id>/to-seller', methods=['POST'])
@login_required
@rider_required
def rider_return_to_seller(task_id):
    t = ReturnPickup.query.get_or_404(task_id)
    if t.rider_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('rider_returns'))
    t.status = 'rider_delivered_to_seller'
    db.session.commit()
    rr = t.return_request
    rr.status = 'rider_delivered_to_seller'
    db.session.commit()
    _emit_return_update(rr, {'pickup_status': t.status})
    push_notification(rr.buyer_id, f'Return parcel RR-{rr.id} has been delivered to the seller.')
    return redirect(url_for('rider_returns'))

@app.route('/rider/returns/<int:task_id>/not-delivered', methods=['POST'])
@login_required
@rider_required
def rider_return_not_delivered(task_id):
    t = ReturnPickup.query.get_or_404(task_id)
    if t.rider_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('rider_returns'))
    t.status = 'not_delivered'
    db.session.commit()
    rr = t.return_request
    try:
        rr.status = 'return_failed'
        db.session.commit()
    except Exception:
        pass
    _emit_return_update(rr, {'pickup_status': t.status})
    push_notification(rr.buyer_id, f'Return parcel RR-{rr.id} delivery attempt failed.')
    return redirect(url_for('rider_returns'))

@app.route('/rider/returns/<int:task_id>/delivered', methods=['POST'])
@login_required
@rider_required
def rider_return_delivered(task_id):
    t = ReturnPickup.query.get_or_404(task_id)
    if t.rider_id != session['user_id']:
        flash('Not allowed.', 'danger')
        return redirect(url_for('rider_returns'))
    t.status = 'delivered'
    t.delivered_at = datetime.utcnow()
    db.session.commit()
    rr = t.return_request
    
    # ⚠️ RULE 3: RETURN & REFUND STILL DEDUCTS STOCK
    # Returned items NEVER return to stock - always deduct again
    try:
        product = rr.order_item.product
        order = rr.order
        returned_quantity = int(rr.quantity)
        
        # Always deduct stock for returns (never add back to inventory)
        product.stock = max(0, int(product.stock) - returned_quantity)
        
        app.logger.info(f'Stock deducted by rider delivery: Product {product.id} (-{returned_quantity}) => {product.stock}')
        
        # Broadcast real-time stock update
        try:
            available_stock = get_available_stock(product.id)
            socketio.emit('product_stock_update', {
                'product_id': product.id,
                'stock': available_stock,
                'available_stock': available_stock
            }, broadcast=True)
            _emit_seller_stats_update(product.seller_id)
        except Exception:
            pass
    except Exception:
        app.logger.exception('Stock deduction failed for rider delivery RR-%s', rr.id)
    
    # Mark buyer-facing "Returned to Seller – Completed" state
    rr.status = 'item_received_by_seller'
    db.session.commit()
    _emit_return_update(rr, {'pickup_status': t.status})
    push_notification(rr.buyer_id, f'Return parcel RR-{rr.id} delivered to seller. Waiting for seller confirmation.')
    return redirect(url_for('rider_returns'))

# --- Stock Correction Route ---
@app.route('/admin/correct-stock/<int:product_id>/<int:quantity_change>', methods=['POST'])
@admin_required
def admin_correct_stock(product_id, quantity_change):
    """Admin route to manually correct stock levels"""
    product = Product.query.get_or_404(product_id)
    old_stock = product.stock
    product.stock += quantity_change  # negative to deduct, positive to add
    
    # Ensure stock doesn't go below 0
    if product.stock < 0:
        product.stock = 0
    
    db.session.commit()
    
    # Broadcast real-time stock update
    try:
        available_stock = get_available_stock(product.id)
        socketio.emit('product_stock_update', {
            'product_id': product.id,
            'stock': available_stock,
            'available_stock': available_stock
        }, broadcast=True)
        _emit_seller_stats_update(product.seller_id)
    except Exception:
        pass
    
    action = "deducted" if quantity_change < 0 else "added"
    log_admin_action('Stock Correction', f'Product {product_id} ({product.name}): {quantity_change} units {action}. Stock changed from {old_stock} to {product.stock}')
    
    flash(f'Stock corrected for {product.name}: {old_stock} → {product.stock} ({action} {abs(quantity_change)} units)', 'success')
    return redirect(url_for('admin_products'))

# --- Search suggestions API ---
@app.route('/api/search/suggest')
def api_search_suggest():
    """
    Lightweight autosuggest endpoint used by the global search box (Supabase version).
    Returns up to ?limit (default 5) matches for products and stores/brands.

    Response shape expected by frontend (see templates/base.html):
      {
        "products": [ {"id": 1, "name": "..", "price": 123.45, "image": "/static/uploads/..."}, ... ],
        "stores":   [ {"id": 9, "name": "Store Name", "logo": "/static/uploads/..."}, ... ]
      }
    """
    try:
        q = (request.args.get('q') or '').strip()
        if not q:
            return jsonify({"products": [], "stores": []})

        # Bound limit to prevent heavy queries
        try:
            limit = int(request.args.get('limit', 5))
        except Exception:
            limit = 5
        limit = max(1, min(limit, 10))

        # Products: match on name or description; only active
        try:
            all_products = get_data('product', filters={'status': 'active'}, limit=limit * 5)
            if not all_products:
                all_products = []
            
            # Client-side filtering for name/description match
            product_rows = []
            for p in all_products:
                name = p.get('name', '').lower()
                description = p.get('description', '').lower()
                if q.lower() in name or q.lower() in description:
                    product_rows.append(p)
                    if len(product_rows) >= limit:
                        break
        except Exception:
            product_rows = []

        products = []
        for p in product_rows:
            try:
                img = url_for('static', filename=f'uploads/{p.get("image_filename")}') if p.get('image_filename') else None
            except Exception:
                img = None
            try:
                price = float(p.get('price', 0)) if p.get('price') is not None else None
            except Exception:
                price = None
            products.append({
                'id': p.get('id'),
                'name': p.get('name'),
                'price': price,
                'image': img,
            })

        # Stores/Brands: SellerApplication (approved) by store_name
        try:
            all_stores = get_data('seller_application', filters={'status': 'approved'}, limit=limit * 5)
            if not all_stores:
                all_stores = []
            
            # Client-side filtering for store_name match
            store_rows = []
            for s in all_stores:
                store_name = s.get('store_name', '').lower()
                if q.lower() in store_name:
                    store_rows.append(s)
                    if len(store_rows) >= limit:
                        break
        except Exception:
            store_rows = []

        stores = []
        for s in store_rows:
            try:
                logo = url_for('static', filename=f'uploads/{s.get("store_logo")}') if s.get('store_logo') else None
            except Exception:
                logo = None
            stores.append({
                'id': s.get('user_id'),   # seller id used by /store/<id>
                'name': s.get('store_name'),
                'logo': logo,
            })

        return jsonify({'products': products, 'stores': stores})
    except Exception as e:
        app.logger.error(f'/api/search/suggest error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# UNIFIED E-COMMERCE API - Architecture aligned endpoints (/api/*)
@app.route('/api/apply-coupon', methods=['POST'])
@token_required
def api_apply_coupon():
    """Apply coupon code to cart (Supabase version)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request data.'}), 400
        
        coupon_code = data.get('coupon_code')
        if not coupon_code:
            return jsonify({'success': False, 'message': 'Coupon code is required.'}), 400

        app.logger.info(f'Applying coupon code: {coupon_code} for user: {request.current_user_id}')

        # Get cart items for current user
        cart_items = get_data('cart', filters={'user_id': request.current_user_id})
        if not cart_items:
            cart_items = []
        
        app.logger.info(f'Cart items found: {len(cart_items)}')
        
        # Calculate subtotal
        subtotal = 0
        for item in cart_items:
            product = get_data_by_id('product', item.get('product_id'))
            if product and product.get('status') == 'approved':
                subtotal += float(product.get('price', 0)) * (item.get('quantity') or 0)

        app.logger.info(f'Calculated subtotal: {subtotal}')

        coupon, discount_amount, error = calculate_coupon_discount(coupon_code, subtotal)

        if error:
            app.logger.warning(f'Coupon validation failed: {error}')
            return jsonify({'success': False, 'message': error}), 400

        app.logger.info(f'Coupon applied successfully: {coupon_code}, discount: {discount_amount}')

        return jsonify({
            'success': True,
            'message': 'Coupon applied successfully.',
            'discount_amount': discount_amount,
            'coupon': {
                'id': coupon.get('id'),
                'code': coupon.get('code'),
                'description': coupon.get('description'),
                'discount_type': coupon.get('discount_type'),
                'discount_value': coupon.get('discount_value'),
            }
        })
    except Exception as e:
        app.logger.error(f'/api/apply-coupon error: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

# ============================================================================

ARCH_ORDER_STATUSES = {
    'pending',
    'processing',
    'ready_for_pickup',
    'picked_up',
    'out_for_delivery',
    'delivered',
    'return_requested',
    'refunded',
    'cancelled',
}

STATUS_ALIASES = {
    'to ship': 'processing',
    'to_ship': 'processing',
    'ready for pickup': 'ready_for_pickup',
    'ready_for_pickup': 'ready_for_pickup',
    'picked up': 'picked_up',
    'picked_up': 'picked_up',
    'out for delivery': 'out_for_delivery',
    'out_for_delivery': 'out_for_delivery',
    'in transit': 'out_for_delivery',  # Mobile app uses in_transit for out_for_delivery
    'in_transit': 'out_for_delivery',  # Mobile app uses in_transit for out_for_delivery
    'completed': 'delivered',
    'complete': 'delivered',
}

BUYER_STATUS_LABELS = {
    'pending': 'Pending',
    'processing': 'To Ship',
    'ready_for_pickup': 'To Ship',
    'picked_up': 'Out for Delivery',
    'out_for_delivery': 'Out for Delivery',
    'delivered': 'Delivered',
    'return_requested': 'Return & Refund Requested',
    'refunded': 'Refunded',
    'cancelled': 'Cancelled',
}

def _safe_upload_url(filename):
    if not filename:
        return None
    # If already a full URL, return as-is
    if filename.startswith('http'):
        return filename
    # If starts with /static/, return as-is (already a valid path)
    if filename.startswith('/static/'):
        return filename
    # If starts with just /, assume it's a valid path from root
    if filename.startswith('/'):
        return filename
    # Otherwise, assume it's just a filename in uploads folder
    try:
        return url_for('static', filename=f'uploads/{filename}')
    except Exception:
        return f'/static/uploads/{filename}'

def _current_user():
    return User.query.filter_by(id=request.current_user_id).first()

def _normalize_status(status_value):
    if status_value is None:
        return None
    status = str(status_value).strip().lower().replace('-', '_')
    status = STATUS_ALIASES.get(status, status)
    if status not in ARCH_ORDER_STATUSES:
        return None
    return status

def _serialize_user_api_dict(user):
    """Serialize user dict from Supabase for API response"""
    uid = user.get('id')
    role = user.get('role')
    profile_image = None
    if uid:
        try:
            profile_image = get_user_avatar_url(uid, role)
        except Exception:
            profile_image = user.get('profile_picture') or user.get('profile_image')
    return {
        'id': uid,
        'name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
        'first_name': user.get('first_name'),
        'last_name': user.get('last_name'),
        'email': user.get('email'),
        'phone': user.get('phone'),
        'address': user.get('address'),
        'role': role,
        'status': user.get('status'),
        'profile_image': profile_image,
        'profile_picture': profile_image,
    }

def _serialize_user_api(user):
    profile_image = get_user_avatar_url(user.id, user.role)
    return {
        'id': user.id,
        'name': f'{user.first_name} {user.last_name}'.strip(),
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone': user.phone,
        'address': user.address,
        'role': user.role,
        'status': user.status,
        'profile_image': profile_image,
        'profile_picture': profile_image,
    }

def _serialize_product_api_dict(product):
    """Serialize product dict from Supabase for API response - with seller info"""
    try:
        # Parse gallery if it's a string JSON
        gallery = []
        if product.get('gallery'):
            try:
                if isinstance(product.get('gallery'), str):
                    gallery = json.loads(product.get('gallery'))
                else:
                    gallery = product.get('gallery') if isinstance(product.get('gallery'), list) else []
            except:
                gallery = []
        
        # Convert gallery filenames to full URLs
        gallery_urls = [_safe_upload_url(img) for img in gallery if img]
        
        # Handle video filename
        videos = []
        if product.get('video_filename'):
            videos.append(_safe_upload_url(product.get('video_filename')))
        
        # Get seller info using local ORM for performance
        seller_name = None
        store_name = None
        store_logo = None
        store_background = None
        
        if product.get('seller_id'):
            if USE_LOCAL_ORM_FALLBACK:
                seller = User.query.get(product.get('seller_id'))
                if seller:
                    seller_name = f"{seller.first_name} {seller.last_name}".strip() if hasattr(seller, 'first_name') else None
                    seller_app = SellerApplication.query.filter_by(user_id=seller.id, status='approved').first()
                    if seller_app:
                        store_name = seller_app.store_name if hasattr(seller_app, 'store_name') else None
                        store_logo = _safe_upload_url(seller_app.store_logo) if hasattr(seller_app, 'store_logo') and seller_app.store_logo else None
                        store_background = _safe_upload_url(seller_app.store_background) if hasattr(seller_app, 'store_background') and seller_app.store_background else None
        
        return {
            'id': product.get('id'),
            'name': product.get('name'),
            'description': product.get('description'),
            'price': float(product.get('price') or 0),
            'stock': int(product.get('stock') or 0),
            'reserved_stock': int(product.get('reserved_stock') or 0),
            'available_stock': int(product.get('stock') or 0) - int(product.get('reserved_stock') or 0),
            'seller_id': product.get('seller_id'),
            'seller_name': seller_name,
            'store_name': store_name,
            'store_logo': store_logo,
            'store_background': store_background,
            'category_id': product.get('category_id'),
            'subcategory_id': product.get('subcategory_id'),
            'image': _safe_upload_url(product.get('image_filename')),
            'image_url': _safe_upload_url(product.get('image_filename')),
            'gallery': gallery_urls,
            'images': gallery_urls,
            'videos': videos,
            'rating': product.get('rating', 0.0),
            'review_count': product.get('review_count', 0),
            'reviews': [],
            'created_at': product.get('created_at'),
        }
    except Exception as e:
        app.logger.error(f"Error serializing product: {e}")
        return {
            'id': product.get('id'),
            'name': product.get('name'),
            'description': product.get('description'),
            'price': float(product.get('price') or 0),
            'stock': int(product.get('stock') or 0),
            'reserved_stock': int(product.get('reserved_stock') or 0),
            'available_stock': int(product.get('stock') or 0) - int(product.get('reserved_stock') or 0),
            'seller_id': product.get('seller_id'),
            'seller_name': None,
            'store_name': None,
            'store_logo': None,
            'store_background': None,
            'category_id': product.get('category_id'),
            'subcategory_id': product.get('subcategory_id'),
            'image': _safe_upload_url(product.get('image_filename')),
            'image_url': _safe_upload_url(product.get('image_filename')),
            'gallery': [],
            'images': [],
            'videos': [],
            'rating': 0,
            'review_count': 0,
            'reviews': [],
            'created_at': product.get('created_at'),
        }

def _serialize_product_api(product):
    # Parse gallery if it's a string JSON
    gallery = []
    if product.gallery:
        try:
            if isinstance(product.gallery, str):
                import json
                gallery = json.loads(product.gallery)
            else:
                gallery = product.gallery if isinstance(product.gallery, list) else []
        except:
            gallery = []
    
    # Convert gallery filenames to full URLs
    gallery_urls = [_safe_upload_url(img) for img in gallery if img]
    
    # Get seller application info if it exists
    seller_app = None
    if product.seller and hasattr(product.seller, 'seller_applications'):
        seller_app = product.seller.seller_applications[0] if product.seller.seller_applications else None
    
    avg_rating = db.session.query(db.func.avg(Review.rating)).filter_by(product_id=product.id, status='published').scalar() or 0
    review_count = db.session.query(db.func.count(Review.id)).filter_by(product_id=product.id, status='published').scalar() or 0

    latest_reviews = (
        Review.query
        .filter_by(product_id=product.id, status='published')
        .order_by(Review.created_at.desc())
        .limit(5)
        .all()
    )

    reviews_payload = []
    for review in latest_reviews:
        reviews_payload.append({
            'id': review.id,
            'user_name': f'{review.user.first_name} {review.user.last_name}'.strip() if review.user else 'Anonymous',
            'rating': review.rating,
            'title': review.title,
            'content': review.content,
            'created_at': review.created_at.isoformat() if review.created_at else None,
            'verified_purchase': bool(review.verified_purchase),
            'media': review.media or [],
        })

    return {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': float(product.price or 0),
        'stock': int(product.stock or 0),
        'seller_id': product.seller_id,
        'seller_name': f'{product.seller.first_name} {product.seller.last_name}'.strip() if product.seller else None,
        'store_name': seller_app.store_name if seller_app else None,
        'store_logo': _safe_upload_url(seller_app.store_logo) if seller_app and seller_app.store_logo else None,
        'store_background': _safe_upload_url(seller_app.store_background) if seller_app and seller_app.store_background else None,
        'store_background_url': _safe_upload_url(seller_app.store_background) if seller_app and seller_app.store_background else None,
        'category_id': product.category_id,
        'subcategory_id': product.subcategory_id,
        'image': _safe_upload_url(product.image_filename),
        'image_url': _safe_upload_url(product.image_filename),
        'gallery': gallery_urls,
        'images': gallery_urls,
        'rating': round(float(avg_rating), 1),
        'review_count': int(review_count),
        'reviews': reviews_payload,
        'created_at': product.created_at.isoformat() if product.created_at else None,
    }

def _serialize_order_api_dict(order):
    """Serialize order dict from Supabase for API response"""
    rider_id = order.get('rider_id') or order.get('picked_up_by') or order.get('delivered_by')
    
    # Get buyer info
    buyer_id = order.get('buyer_id')
    buyer = get_data_by_id('user', buyer_id) if buyer_id else None
    buyer_name = f"{buyer.get('first_name', '')} {buyer.get('last_name', '')}".strip() if buyer else None
    buyer_phone = buyer.get('phone') if buyer else None
    buyer_email = buyer.get('email') if buyer else None
    
    # Get rider info
    rider_name = None
    rider_phone = None
    rider_profile_picture = None
    if rider_id:
        rider = get_data_by_id('user', rider_id)
        if rider:
            rider_name = f"{rider.get('first_name', '')} {rider.get('last_name', '')}".strip()
            rider_phone = rider.get('phone')
            rider_profile_picture = rider.get('profile_picture')
        else:
            app.logger.warning(f'⚠️ Order #{order.get("id")}: Rider #{rider_id} not found in get_data_by_id')
    
    # Debug logging for rider info
    if order.get('id'):
        app.logger.info(f'📦 _serialize_order_api_dict - Order #{order.get("id")}: rider_id={rider_id}, rider_name={rider_name}, rider_phone={rider_phone}, rider_profile_picture={rider_profile_picture}')
    
    # Get order items
    order_items = get_data('order_item', filters={'order_id': order.get('id')})
    if not order_items:
        order_items = []
    items = []
    for item in order_items:
        # Get product info
        product = None
        if item.get('product_id'):
            products = get_data('product', filters={'id': item.get('product_id')})
            if products:
                product = products[0]
        
        items.append({
            'id': item.get('id'),
            'product_id': item.get('product_id'),
            'product_name': product.get('name') if product else None,
            'product_image': _safe_upload_url(product.get('image_filename')) if product else None,
            'quantity': int(item.get('quantity') or 0),
            'price': float(item.get('price_at_time') or 0),
            'subtotal': float((item.get('quantity') or 0) * (item.get('price_at_time') or 0)),
            'seller_id': product.get('seller_id') if product else None,
        })
    
    # Check if order has been rated
    has_rating = False
    try:
        reviews = get_data('review', filters={'order_id': order.get('id')})
        has_rating = reviews is not None and len(reviews) > 0
    except Exception:
        pass
    
    return {
        'id': order.get('id'),
        'buyer_id': order.get('buyer_id'),
        'buyer_name': buyer_name,
        'buyer_phone': buyer_phone,
        'buyer_email': buyer_email,
        'rider_id': rider_id,
        'rider_name': rider_name,
        'rider_phone': rider_phone,
        'rider_profile_picture': rider_profile_picture,
        'status': order.get('status'),
        'total_amount': float(order.get('total_amount') or 0),
        'payment_method': order.get('payment_method'),
        'payment_status': order.get('payment_status'),
        'shipping_address': order.get('shipping_address'),
        'recipient_name': order.get('recipient_name'),
        'recipient_phone': order.get('recipient_phone'),
        'order_date': order.get('created_at'),
        'created_at': order.get('created_at'),
        'updated_at': order.get('updated_at'),
        'qr_code': order.get('qr_code'),
        'tracking_number': order.get('tracking_number'),
        'proof_photo_url': order.get('proof_photo_url'),
        'has_rating': has_rating,
        'items': items,
    }

def _serialize_order_item_api(item):
    product = item.product
    return {
        'id': item.id,
        'product_id': item.product_id,
        'product_name': product.name if product else None,
        'product_image': _safe_upload_url(product.image_filename) if product else None,
        'quantity': int(item.quantity or 0),
        'price': float(item.price_at_time or 0),
        'subtotal': float((item.quantity or 0) * (item.price_at_time or 0)),
        'seller_id': product.seller_id if product else None,
    }

def _serialize_order_api(order):
    rider_id = order.rider_id or order.picked_up_by or order.delivered_by
    return {
        'id': order.id,
        'buyer_id': order.buyer_id,
        'rider_id': rider_id,
        'status': order.status,
        'status_label': BUYER_STATUS_LABELS.get(order.status, order.status.replace('_', ' ').title()),
        'total_price': float(order.total_amount or 0),
        'payment_method': order.payment_method,
        'payment_status': order.payment_status,
        'delivery_address': order.shipping_address,
        'created_at': order.created_at.isoformat() if order.created_at else None,
        'updated_at': order.updated_at.isoformat() if order.updated_at else None,
        'items': [_serialize_order_item_api(item) for item in order.items],
    }

def _serialize_cart_dict(user_id):
    """Serialize cart from Supabase for API response"""
    cart_rows = get_data('cart', filters={'user_id': user_id})
    if not cart_rows:
        return {'items': [], 'item_count': 0, 'total_price': 0.0}
    
    items = []
    total_price = 0.0
    for row in cart_rows:
        # Get product info
        products = get_data('product', filters={'id': row.get('product_id')})
        if not products or len(products) == 0:
            continue
        product = products[0]
        
        if product.get('status') not in ['approved', 'active']:
            continue
        
        price = float(product.get('price') or 0)
        subtotal = price * (row.get('quantity') or 0)
        total_price += subtotal
        items.append({
            'id': row.get('id'),
            'product_id': row.get('product_id'),
            'product_name': product.get('name'),
            'product_image': _safe_upload_url(product.get('image_filename')),
            'quantity': row.get('quantity'),
            'price': price,
            'stock': product.get('stock'),
            'subtotal': float(subtotal),
        })
    return {
        'items': items,
        'item_count': len(items),
        'total_price': float(total_price),
    }

def _serialize_cart(user_id):
    cart_rows = Cart.query.filter_by(user_id=user_id).all()
    items = []
    total_price = 0.0
    for row in cart_rows:
        if not row.product or row.product.status not in ['approved', 'active']:
            continue
        price = float(row.product.price or 0)
        subtotal = price * (row.quantity or 0)
        total_price += subtotal
        items.append({
            'id': row.id,
            'product_id': row.product_id,
            'product_name': row.product.name,
            'product_image': _safe_upload_url(row.product.image_filename),
            'quantity': row.quantity,
            'price': price,
            'stock': row.product.stock,
            'subtotal': float(subtotal),
        })
    return {
        'items': items,
        'item_count': len(items),
        'total_price': float(total_price),
    }

def _validate_user_password(user, password):
    hashed = user.password or ''
    if hashed.startswith('$2a$') or hashed.startswith('$2b$') or hashed.startswith('$2y$'):
        return verify_password(password, hashed)
    return password == hashed

def _resolve_category_for_product(payload):
    category_id = payload.get('category_id')
    category = None
    if category_id:
        category = db.session.get(Category, int(category_id))
        if not category:
            return None, None
    else:
        category = Category.query.filter_by(status='active').first() or Category.query.first()
        if not category:
            category = Category(name='General', status='active')
            db.session.add(category)
            db.session.flush()
    subcategory_id = payload.get('subcategory_id')
    if subcategory_id:
        subcategory = db.session.get(Subcategory, int(subcategory_id))
        if not subcategory or subcategory.category_id != category.id:
            return None, None
        return category.id, subcategory.id
    return category.id, None

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({'success': True, 'message': 'API is healthy'})

@app.route('/api/login', methods=['POST'])
def api_login():
    """
    API endpoint for mobile user login (Supabase version).
    - Authenticates against Supabase
    - Verifies hashed password
    - Checks account status
    - Returns JWT on success
    """
    data = request.get_json(silent=True) or {}
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email'].strip().lower()
    password = data['password']

    app.logger.info(f"=== LOGIN ATTEMPT ===")
    app.logger.info(f"Email: {email}")
    app.logger.info(f"Password length: {len(password)}")

    # Fetch user from Supabase
    users = get_data('user', filters={'email': email})
    app.logger.info(f"Found users: {len(users) if users else 0}")
    
    if not users or len(users) == 0:
        app.logger.error(f"User not found for email: {email}")
        return jsonify({'error': 'Invalid email or password'}), 401
    
    user = users[0]
    app.logger.info(f"User ID: {user.get('id')}")
    app.logger.info(f"User status: {user.get('status')}")
    app.logger.info(f"User role: {user.get('role')}")

    # --- Account Status Check ---
    if user.get('status') == 'pending':
        app.logger.error(f"Account pending approval for user: {email}")
        return jsonify({'error': 'Account pending approval'}), 403
    if user.get('status') == 'rejected':
        app.logger.error(f"Account rejected for user: {email}")
        return jsonify({'error': 'Account rejected'}), 403
    if user.get('status') != 'active':
        app.logger.error(f"Account not active (status: {user.get('status')}) for user: {email}")
        return jsonify({'error': 'Account is not active'}), 403

    # --- Password Verification ---
    app.logger.info(f"Attempting password verification...")
    password_valid = verify_password(password, user.get('password'))
    app.logger.info(f"Password valid: {password_valid}")
    
    if not password_valid:
        app.logger.error(f"Password verification failed for user: {email}")
        return jsonify({'error': 'Invalid email or password'}), 401

    # --- Generate Tokens ---
    tokens = generate_tokens(user.get('id'), user.get('role'))
    app.logger.info(f"Login successful for user: {email}")
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.get('id'),
            'first_name': user.get('first_name'),
            'last_name': user.get('last_name'),
            'email': user.get('email'),
            'role': user.get('role')
        },
        'tokens': tokens
    }), 200

@app.route('/api/register', methods=['POST'])
def api_register():
    """
    API endpoint for mobile user registration (Supabase version).
    - Validates input
    - Checks for duplicate emails
    - Hashes password
    - Creates a new User with 'pending' status
    - Saves to Supabase database
    - Returns success message
    """
    try:
        data = request.get_json(silent=True) or {}

        first_name = str(data.get('first_name', '')).strip()
        last_name = str(data.get('last_name', '')).strip()
        email = str(data.get('email', '')).strip().lower()
        raw_phone = str(data.get('phone', '')).strip()
        password = str(data.get('password', ''))
        role = str(data.get('role', 'buyer')).strip().lower() or 'buyer'

        street = str(data.get('street_address', '')).strip()
        barangay = str(data.get('barangay', '')).strip()
        city = str(data.get('city', '')).strip()
        province = str(data.get('province', '')).strip()
        region = str(data.get('region', '')).strip()
        address = str(data.get('address', '')).strip() or ', '.join(
            part for part in [street, barangay, city, province, region] if part
        )

        if role not in ('buyer', 'rider'):
            return jsonify({'error': 'Only buyer and rider registration is allowed via mobile API'}), 400

        if not all([first_name, last_name, email, raw_phone, address, password]):
            return jsonify({'error': 'first_name, last_name, email, phone, address, and password are required'}), 400

        phone = ''.join(ch for ch in raw_phone if ch.isdigit())
        if len(phone) != 11:
            return jsonify({'error': 'Phone number must be exactly 11 digits'}), 400

        if not email.endswith('@gmail.com'):
            return jsonify({'error': 'Please register using a Gmail address.'}), 400

        # Check if email already exists in Supabase
        existing_users = get_data('user', filters={'email': email})
        if existing_users and len(existing_users) > 0:
            existing_user = existing_users[0]
            user_status = existing_user.get('status', '').lower()
            
            # Check for pending approval
            if user_status == 'pending':
                return jsonify({'error': 'This email is already registered and waiting for admin approval. Please wait for approval or contact support.'}), 409
            
            # Check for other non-rejected statuses
            if user_status != 'rejected':
                return jsonify({'error': 'This email address is already registered. Please use a different email or try logging in.'}), 409
            
            # If rejected, allow re-registration (will update the existing record)
            # Note: You may want to handle this differently based on your business logic

        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400

        user_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': hash_password(password),
            'phone': phone,
            'address': address,
            'role': role,
            'status': 'pending',
        }
        
        app.logger.info(f'Attempting to create user: {email} with role: {role}')
        user = insert_data('user', user_data)
        
        if not user:
            # Fallback to local ORM
            app.logger.warning(f'Supabase insert failed for {email}, trying local ORM')
            try:
                new_user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=hash_password(password),
                    phone=phone,
                    address=address,
                    role=role,
                    status='pending'
                )
                db.session.add(new_user)
                db.session.commit()
                app.logger.info(f'User created via ORM: {email} with ID: {new_user.id}')
                user = {
                    'id': new_user.id,
                    'first_name': new_user.first_name,
                    'last_name': new_user.last_name,
                    'email': new_user.email,
                    'phone': new_user.phone,
                    'address': new_user.address,
                    'role': new_user.role,
                    'status': new_user.status
                }
            except Exception as orm_error:
                db.session.rollback()
                app.logger.error(f'ORM fallback failed for {email}: {orm_error}')
                return jsonify({'error': f'Failed to create user: {str(orm_error)}'}), 500
        else:
            app.logger.info(f'User created via Supabase: {email} with ID: {user.get("id")}')

        user_id = user.get('id')

        if role == 'rider':
            vehicle_type = str(data.get('vehicle_type', '')).strip()
            vehicle_number = str(data.get('vehicle_number', '')).strip()
            if not vehicle_type or not vehicle_number:
                # Rollback user creation
                try:
                    delete_data_by_id('user', user_id)
                except:
                    # If Supabase delete fails, try ORM
                    try:
                        user_to_delete = db.session.get(User, user_id)
                        if user_to_delete:
                            db.session.delete(user_to_delete)
                            db.session.commit()
                    except:
                        db.session.rollback()
                return jsonify({'error': 'vehicle_type and vehicle_number are required for rider registration'}), 400

            rider_application_data = {
                'user_id': user_id,
                'vehicle_type': vehicle_type,
                'vehicle_number': vehicle_number,
                'status': 'pending',
            }
            rider_app = insert_data('rider_application', rider_application_data)
            
            if not rider_app:
                # Fallback to ORM
                try:
                    rider_app_orm = RiderApplication(
                        user_id=user_id,
                        vehicle_type=vehicle_type,
                        vehicle_number=vehicle_number,
                        status='pending'
                    )
                    db.session.add(rider_app_orm)
                    db.session.commit()
                    app.logger.info(f'Rider application created via ORM for user {user_id}')
                except Exception as rider_error:
                    db.session.rollback()
                    app.logger.error(f'Failed to create rider application: {rider_error}')

        # Notify admins about new registration
        try:
            account_type = 'Rider' if role == 'rider' else 'Buyer'
            notify_admins(
                f'New {account_type} mobile registration pending approval: '
                f'{first_name} {last_name} ({email})'
            )
        except Exception as e:
            app.logger.exception(f'Failed to notify admins: {e}')
        
        # Send registration confirmation email to user
        try:
            account_type = 'Rider' if role == 'rider' else 'Buyer'
            subject = '🎉 Welcome to Kids Kingdom! Registration Received'
            
            # Create beautiful HTML email
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .email-container {{
            max-width: 600px;
            margin: 40px auto;
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 30px;
            text-align: center;
            color: white;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
            font-weight: 800;
            letter-spacing: 1px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .header .emoji {{
            font-size: 60px;
            margin-bottom: 10px;
            display: block;
            animation: bounce 2s infinite;
        }}
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 24px;
            color: #333;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        .message {{
            font-size: 16px;
            line-height: 1.8;
            color: #555;
            margin-bottom: 30px;
        }}
        .status-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: 600;
            font-size: 14px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
        }}
        .details-box {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 15px;
            padding: 25px;
            margin: 25px 0;
            border-left: 5px solid #667eea;
        }}
        .details-title {{
            font-size: 18px;
            font-weight: 700;
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }}
        .details-title::before {{
            content: "📋";
            margin-right: 10px;
            font-size: 24px;
        }}
        .detail-row {{
            display: flex;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.5);
        }}
        .detail-row:last-child {{
            border-bottom: none;
        }}
        .detail-label {{
            font-weight: 600;
            color: #555;
            min-width: 100px;
        }}
        .detail-value {{
            color: #333;
            font-weight: 500;
        }}
        .info-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            border-radius: 10px;
            margin: 25px 0;
        }}
        .info-box p {{
            margin: 0;
            color: #856404;
            font-size: 14px;
            line-height: 1.6;
        }}
        .info-box strong {{
            display: block;
            margin-bottom: 8px;
            font-size: 16px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 3px solid #667eea;
        }}
        .footer-logo {{
            font-size: 24px;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        .footer-text {{
            color: #6c757d;
            font-size: 14px;
            line-height: 1.6;
        }}
        .social-icons {{
            margin-top: 20px;
        }}
        .social-icons span {{
            font-size: 24px;
            margin: 0 8px;
        }}
        .divider {{
            height: 3px;
            background: linear-gradient(90deg, transparent, #667eea, transparent);
            margin: 30px 0;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <span class="emoji">🎉</span>
            <h1>KIDS KINGDOM</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Your Trusted Kids & Baby Store</p>
        </div>
        
        <div class="content">
            <div class="greeting">Hi {first_name}! 👋</div>
            
            <div class="message">
                <strong>Thank you for choosing Kids Kingdom!</strong><br>
                We're excited to have you join our community of parents and caregivers who trust us for quality kids and baby products.
            </div>
            
            <div class="status-badge">
                ⏳ Registration Pending Approval
            </div>
            
            <div class="info-box">
                <strong>📌 What happens next?</strong>
                <p>
                    Our admin team is reviewing your registration. This usually takes <strong>24-48 hours</strong>. 
                    You'll receive an email notification once your account is approved and ready to use!
                </p>
            </div>
            
            <div class="details-box">
                <div class="details-title">Your Account Details</div>
                <div class="detail-row">
                    <div class="detail-label">👤 Name:</div>
                    <div class="detail-value">{first_name} {last_name}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">📧 Email:</div>
                    <div class="detail-value">{email}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-label">🎭 Role:</div>
                    <div class="detail-value">{account_type}</div>
                </div>
            </div>
            
            <div class="divider"></div>
            
            <div class="message" style="text-align: center; color: #667eea; font-weight: 600;">
                Thank you for your patience! 💙
            </div>
        </div>
        
        <div class="footer">
            <div class="footer-logo">KIDS KINGDOM</div>
            <div class="footer-text">
                Quality Products for Your Little Ones<br>
                Making Parenting Easier, One Product at a Time
            </div>
            <div class="social-icons">
                <span>📱</span>
                <span>💬</span>
                <span>🌐</span>
            </div>
            <div style="margin-top: 20px; font-size: 12px; color: #adb5bd;">
                © 2026 Kids Kingdom. All rights reserved.
            </div>
        </div>
    </div>
</body>
</html>
            """
            
            # Create plain text fallback
            text_body = (
                f"Hi {first_name}!\n\n"
                f"🎉 Welcome to Kids Kingdom!\n\n"
                f"Thank you for choosing Kids Kingdom! We're excited to have you join our community.\n\n"
                f"⏳ REGISTRATION STATUS: Pending Approval\n\n"
                f"What happens next?\n"
                f"Our admin team is reviewing your registration. This usually takes 24-48 hours.\n"
                f"You'll receive an email notification once your account is approved!\n\n"
                f"YOUR ACCOUNT DETAILS:\n"
                f"👤 Name: {first_name} {last_name}\n"
                f"📧 Email: {email}\n"
                f"🎭 Role: {account_type}\n\n"
                f"Thank you for your patience! 💙\n\n"
                f"---\n"
                f"KIDS KINGDOM\n"
                f"Quality Products for Your Little Ones\n"
                f"© 2026 Kids Kingdom. All rights reserved."
            )
            
            # Create multipart message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = app.config['MAIL_SENDER']
            msg['To'] = email
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
                smtp.send_message(msg)
            app.logger.info(f'Registration confirmation email sent to {email}')
        except Exception as e:
            app.logger.exception(f'Failed to send registration confirmation email to {email}: {e}')

        return jsonify({
            'success': True,
            'message': 'Registration successful. Your account is pending admin approval.',
            'user': _serialize_user_api_dict(user),
        }), 201
    except Exception as e:
        app.logger.error(f'/api/register error: {e}')
        app.logger.exception('Full registration error traceback:')
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """Refresh access token (Supabase version)."""
    try:
        data = request.get_json(silent=True) or {}
        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return jsonify({'error': 'Refresh token is required'}), 400
        payload = verify_token(refresh_token, 'refresh')
        if not payload:
            return jsonify({'error': 'Invalid or expired refresh token'}), 401
        
        user = get_data_by_id('user', payload.get('user_id'))
        if not user or user.get('status') != 'active':
            return jsonify({'error': 'User not found or inactive'}), 401
        
        tokens = generate_tokens(user.get('id'), user.get('role'))
        return jsonify({
            'success': True,
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'expires_in': tokens['expires_in'],
        })
    except Exception as e:
        app.logger.error(f'/api/refresh error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products', methods=['GET'])
def api_products():
    """
    API endpoint to get all approved products from Supabase.
    - Fetches products with 'active' status
    - Serializes products to JSON
    - Includes image URLs
    """
    try:
        search = (request.args.get('search') or '').strip()
        seller_id = request.args.get('seller_id')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        in_stock = request.args.get('in_stock')

        # Build filters for Supabase
        filters = {'status': ['approved', 'active']}
        if seller_id:
            filters['seller_id'] = seller_id
        
        # Fetch from Supabase
        products = get_data('product', filters=filters, order='created_at.desc')
        
        if not products:
            return jsonify([])
        
        # Apply additional filters that can't be done with simple eq filters
        filtered_products = []
        for product in products:
            # Search filter
            if search:
                name_match = search.lower() in product.get('name', '').lower()
                desc_match = search.lower() in product.get('description', '').lower()
                if not (name_match or desc_match):
                    continue
            
            # Price filters
            if min_price and product.get('price', 0) < float(min_price):
                continue
            if max_price and product.get('price', 0) > float(max_price):
                continue
            
            # Stock filter
            if in_stock in ('1', 'true', 'True') and product.get('stock', 0) <= 0:
                continue
            
            filtered_products.append(product)
        
        # Calculate ratings for all products
        from rating_helper import add_ratings_to_products
        filtered_products = add_ratings_to_products(db, Review, filtered_products)
        
        return jsonify([_serialize_product_api_dict(product) for product in filtered_products])
    except Exception as e:
        app.logger.error(f'/api/products GET error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products', methods=['POST'])
@token_required
@role_required('seller', 'admin')
def api_create_product():
    """Create a new product (Supabase version)."""
    try:
        data = request.get_json(silent=True) or {}
        name = str(data.get('name', '')).strip()
        description = str(data.get('description', '')).strip()
        if not name or not description:
            return jsonify({'error': 'name and description are required'}), 400
        try:
            price = float(data.get('price', 0))
            stock = int(data.get('stock', 0))
        except Exception:
            return jsonify({'error': 'price and stock must be numeric'}), 400
        if price < 0 or stock < 0:
            return jsonify({'error': 'price and stock must be non-negative'}), 400

        category_id, subcategory_id = _resolve_category_for_product(data)
        if category_id is None:
            return jsonify({'error': 'Invalid category/subcategory'}), 400

        seller_id = request.current_user_id
        if request.current_user_role == 'admin' and data.get('seller_id'):
            sellers = get_data('user', filters={'id': int(data.get('seller_id')), 'role': 'seller', 'status': 'active'})
            if not sellers or len(sellers) == 0:
                return jsonify({'error': 'Provided seller_id is invalid'}), 400
            seller_id = sellers[0].get('id')

        product_data = {
            'name': name,
            'description': description,
            'price': price,
            'stock': stock,
            'seller_id': seller_id,
            'category_id': category_id,
            'subcategory_id': subcategory_id,
            'status': 'active',
        }
        product = insert_data('product', product_data)
        
        if not product:
            return jsonify({'error': 'Failed to create product'}), 500
        
        return jsonify({'success': True, 'product': _serialize_product_api_dict(product)}), 201
    except Exception as e:
        app.logger.error(f'/api/products POST error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
@token_required
@role_required('seller', 'admin')
def api_update_product(product_id):
    """Update a product (Supabase version)."""
    try:
        products = get_data('product', filters={'id': product_id})
        if not products or len(products) == 0:
            return jsonify({'error': 'Product not found'}), 404
        
        product = products[0]
        
        if request.current_user_role == 'seller' and product.get('seller_id') != request.current_user_id:
            return jsonify({'error': 'You can only update your own products'}), 403

        data = request.get_json(silent=True) or {}
        update_data = {}
        
        if 'name' in data:
            name = str(data.get('name') or '').strip()
            if not name:
                return jsonify({'error': 'name cannot be empty'}), 400
            update_data['name'] = name
        if 'description' in data:
            description = str(data.get('description') or '').strip()
            if not description:
                return jsonify({'error': 'description cannot be empty'}), 400
            update_data['description'] = description
        if 'price' in data:
            try:
                price = float(data.get('price'))
            except Exception:
                return jsonify({'error': 'price must be numeric'}), 400
            if price < 0:
                return jsonify({'error': 'price must be non-negative'}), 400
            update_data['price'] = price
        if 'stock' in data:
            try:
                stock = int(data.get('stock'))
            except Exception:
                return jsonify({'error': 'stock must be numeric'}), 400
            if stock < 0:
                return jsonify({'error': 'stock must be non-negative'}), 400
            update_data['stock'] = stock
        if 'status' in data:
            update_data['status'] = str(data.get('status')).strip().lower()

        if 'category_id' in data or 'subcategory_id' in data:
            category_id, subcategory_id = _resolve_category_for_product(data)
            if category_id is None:
                return jsonify({'error': 'Invalid category/subcategory'}), 400
            update_data['category_id'] = category_id
            update_data['subcategory_id'] = subcategory_id

        if update_data:
            updated = update_data_by_id('product', product_id, update_data)
            if updated:
                product = updated

        return jsonify({'success': True, 'product': _serialize_product_api_dict(product)})
    except Exception as e:
        app.logger.error(f'/api/products/{product_id} PUT error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@token_required
@role_required('seller', 'admin')
def api_delete_product(product_id):
    """Delete a product (Supabase version)."""
    try:
        products = get_data('product', filters={'id': product_id})
        if not products or len(products) == 0:
            return jsonify({'error': 'Product not found'}), 404
        
        product = products[0]
        
        if request.current_user_role == 'seller' and product.get('seller_id') != request.current_user_id:
            return jsonify({'error': 'You can only delete your own products'}), 403
        
        update_data_by_id('product', product_id, {'status': 'deleted'})
        return jsonify({'success': True, 'message': 'Product deleted'})
    except Exception as e:
        app.logger.error(f'/api/products/{product_id} DELETE error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cart', methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_required
def api_get_cart():
    """
    API endpoint for cart operations (Supabase version).
    GET: Get cart items for current user
    POST: Add item to cart
    PUT: Update cart item quantity
    DELETE: Remove item from cart
    """
    try:
        user_id = request.current_user_id
        
        if request.method == 'GET':
            # Prefer Supabase-backed cart, but fall back to local ORM when empty or unavailable
            cart_data = _serialize_cart_dict(user_id)
            if not cart_data or not cart_data.get('items'):
                cart_data = _serialize_cart(user_id)
            return jsonify(cart_data['items'])

        if request.method == 'POST':
            data = request.get_json(silent=True) or {}
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            try:
                product_id = int(product_id)
                quantity = int(quantity)
            except Exception:
                return jsonify({'error': 'product_id and quantity are required'}), 400
            if quantity <= 0:
                return jsonify({'error': 'quantity must be greater than 0'}), 400

            product = get_data_by_id('product', product_id)
            if not product:
                orm_product = db.session.get(Product, product_id)
                if orm_product:
                    product = {
                        'id': orm_product.id,
                        'name': orm_product.name,
                        'description': orm_product.description,
                        'price': orm_product.price,
                        'stock': orm_product.stock,
                        'seller_id': orm_product.seller_id,
                        'category_id': orm_product.category_id,
                        'subcategory_id': orm_product.subcategory_id,
                        'image_filename': orm_product.image_filename,
                        'gallery': orm_product.gallery,
                        'video_filename': orm_product.video_filename,
                        'status': orm_product.status,
                        'featured': orm_product.featured,
                        'created_at': orm_product.created_at,
                    }
            if not product or product.get('status') not in ['approved', 'active']:
                return jsonify({'error': 'Product not found'}), 404

            existing = get_data('cart', filters={'user_id': user_id, 'product_id': product_id})
            requested_qty = quantity + (existing[0].get('quantity') if existing else 0)
            if product.get('stock', 0) < requested_qty:
                return jsonify({'error': f'Only {product.get("stock")} item(s) left in stock'}), 400

            if existing:
                update_data_by_id('cart', existing[0].get('id'), {'quantity': requested_qty})
                updated = _serialize_cart_dict(user_id)
                item = next((x for x in updated['items'] if x.get('product_id') == product_id), None)
                return jsonify({'success': True, 'message': 'Item updated in cart', 'cart_item': item}), 200
            else:
                result = insert_data('cart', {'user_id': user_id, 'product_id': product_id, 'quantity': quantity})
                # If Supabase insert failed due to RLS or network, fallback to local ORM serialization
                if not result:
                    try:
                        # ensure Cart model is used for local insert if insert_data fallback already created a row
                        cart_obj = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
                        db.session.add(cart_obj)
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
                # Prefer Supabase-backed serialization, otherwise use ORM serializer
                updated = _serialize_cart_dict(user_id)
                if not updated or not updated.get('items'):
                    updated = _serialize_cart(user_id)
                item = next((x for x in updated['items'] if x.get('product_id') == product_id), None)
                return jsonify({'success': True, 'message': 'Item added to cart', 'cart_item': item}), 201

        if request.method == 'PUT':
            data = request.get_json(silent=True) or {}
            cart_item_id = data.get('cart_item_id')
            quantity = data.get('quantity')
            try:
                cart_item_id = int(cart_item_id)
                quantity = int(quantity)
            except Exception:
                return jsonify({'error': 'cart_item_id and quantity are required'}), 400
            if quantity <= 0:
                return jsonify({'error': 'quantity must be greater than 0'}), 400

            items = get_data('cart', filters={'id': cart_item_id, 'user_id': user_id})
            if not items or len(items) == 0:
                return jsonify({'error': 'Cart item not found'}), 404
            
            item = items[0]
            
            # Get product to check stock
            products = get_data('product', filters={'id': item.get('product_id')})
            if not products:
                orm_product = db.session.get(Product, item.get('product_id'))
                if orm_product:
                    products = [{
                        'id': orm_product.id,
                        'name': orm_product.name,
                        'description': orm_product.description,
                        'price': orm_product.price,
                        'stock': orm_product.stock,
                        'seller_id': orm_product.seller_id,
                        'category_id': orm_product.category_id,
                        'subcategory_id': orm_product.subcategory_id,
                        'image_filename': orm_product.image_filename,
                        'gallery': orm_product.gallery,
                        'video_filename': orm_product.video_filename,
                        'status': orm_product.status,
                        'featured': orm_product.featured,
                        'created_at': orm_product.created_at,
                    }]
            if not products or len(products) == 0 or products[0].get('status') not in ['approved', 'active']:
                return jsonify({'error': 'Product is no longer available'}), 400
            
            product = products[0]
            if product.get('stock', 0) < quantity:
                return jsonify({'error': f'Only {product.get("stock")} item(s) left in stock'}), 400
            
            update_data_by_id('cart', cart_item_id, {'quantity': quantity})
            updated = _serialize_cart_dict(user_id)
            item_payload = next((x for x in updated['items'] if x.get('id') == cart_item_id), None)
            return jsonify({'success': True, 'message': 'Cart updated', 'cart_item': item_payload})

        # DELETE method
        data = request.get_json(silent=True) or {}
        cart_item_id = request.args.get('cart_item_id') or data.get('cart_item_id')
        try:
            cart_item_id = int(cart_item_id)
        except Exception:
            return jsonify({'error': 'cart_item_id is required'}), 400
        
        items = get_data('cart', filters={'id': cart_item_id, 'user_id': user_id})
        if not items or len(items) == 0:
            return jsonify({'error': 'Cart item not found'}), 404
        
        delete_data_by_id('cart', cart_item_id)
        return jsonify({'success': True, 'message': 'Item removed'})
    except Exception as e:
        app.logger.error(f'/api/cart error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/orders', methods=['GET', 'POST'])
@token_required
def api_get_orders():
    """
    API endpoint for orders (Supabase version).
    GET: Get orders for current user
    POST: Create a new order
    """
    try:
        user_id = request.current_user_id
        if request.method == 'GET':
            orders = get_data('order', filters={'buyer_id': user_id}, order='created_at.desc')
            if not orders:
                return jsonify([])
            return jsonify([_serialize_order_api_dict(order) for order in orders])

        data = request.get_json(silent=True) or {}
        incoming_items = data.get('items') or []
        use_cart = data.get('use_cart', False)
        payment_method = str(data.get('payment_method', 'cod')).strip().lower() or 'cod'
        shipping_address = (data.get('delivery_address') or data.get('shipping_address') or '').strip()
        rider_id = data.get('rider_id')

        if not shipping_address:
            return jsonify({'error': 'delivery_address is required'}), 400

        # Get user address if not provided
        if not shipping_address:
            user = get_data_by_id('user', user_id)
            if user:
                shipping_address = user.get('address', '')
        
        if not shipping_address:
            return jsonify({'error': 'delivery_address is required'}), 400

        normalized_items = []
        if use_cart or not incoming_items:
            cart_rows = get_data('cart', filters={'user_id': user_id})
            incoming_items = [{'product_id': row.get('product_id'), 'quantity': row.get('quantity')} for row in cart_rows] if cart_rows else []
        
        for row in incoming_items:
            try:
                product_id = int(row.get('product_id'))
                quantity = int(row.get('quantity', 1))
            except Exception:
                return jsonify({'error': 'Invalid order item payload'}), 400
            if quantity <= 0:
                return jsonify({'error': 'Order item quantity must be greater than 0'}), 400

            product = get_data_by_id('product', product_id)
            if not product or product.get('status') not in ['approved', 'active']:
                orm_product = db.session.get(Product, product_id)
                if orm_product and orm_product.status in ['approved', 'active']:
                    product = {
                        'id': orm_product.id,
                        'name': orm_product.name,
                        'description': orm_product.description,
                        'price': orm_product.price,
                        'stock': orm_product.stock,
                        'seller_id': orm_product.seller_id,
                        'category_id': orm_product.category_id,
                        'subcategory_id': orm_product.subcategory_id,
                        'image_filename': orm_product.image_filename,
                        'gallery': orm_product.gallery,
                        'video_filename': orm_product.video_filename,
                        'status': orm_product.status,
                        'featured': orm_product.featured,
                        'created_at': orm_product.created_at,
                    }
            if not product or product.get('status') not in ['approved', 'active']:
                return jsonify({'error': f'Product {product_id} not found'}), 404

            if product.get('stock', 0) < quantity:
                return jsonify({'error': f'Insufficient stock for {product.get("name")}'},), 400
            normalized_items.append((product, quantity))

        if not normalized_items:
            return jsonify({'error': 'Order must contain at least one item'}), 400

        rider_user = None
        if rider_id is not None:
            try:
                rider_id = int(rider_id)
            except Exception:
                return jsonify({'error': 'rider_id must be numeric'}), 400
            riders = get_data('user', filters={'id': rider_id, 'role': 'rider', 'status': 'active'})
            if not riders or len(riders) == 0:
                return jsonify({'error': 'rider_id is invalid'}), 400
            rider_user = riders[0]

        total = 0.0
        
        # Create order
        order_data = {
            'buyer_id': user_id,
            'rider_id': rider_user.get('id') if rider_user else None,
            'total_amount': 0,
            'status': 'pending',
            'payment_method': payment_method,
            'payment_status': 'pending',
            'shipping_address': shipping_address,
            'stock_deducted': False
        }
        order = insert_data('order', order_data)
        
        if not order:
            return jsonify({'error': 'Failed to create order'}), 500

        order_id = order.get('id')

        # Create order items and update product stock
        for product, quantity in normalized_items:
            subtotal = float(product.get('price', 0)) * quantity
            total += subtotal
            
            order_item_data = {
                'order_id': order_id,
                'product_id': product.get('id'),
                'quantity': quantity,
                'price_at_time': float(product.get('price', 0))
            }
            insert_data('order_item', order_item_data)
            
            # Update product stock
            new_stock = max(0, int(product.get('stock', 0)) - quantity)
            update_data_by_id('product', product.get('id'), {'stock': new_stock})

        # Update order total
        update_data_by_id('order', order_id, {'total_amount': total, 'stock_deducted': True})

        # Clear cart
        delete_data('cart', filters={'user_id': user_id})
        
        # Fetch the complete order with items
        complete_order = get_data_by_id('order', order_id)
        if complete_order:
            return jsonify({'success': True, 'order': _serialize_order_api_dict(complete_order)}), 201
        
        return jsonify({'success': True, 'order_id': order_id}), 201
    except Exception as e:
        app.logger.error(f'/api/orders POST error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/orders/user', methods=['GET'])
@token_required
@role_required('buyer')
def api_orders_user():
    """Get orders for current buyer (Supabase version)."""
    try:
        user_id = request.current_user_id
        status = _normalize_status(request.args.get('status')) if request.args.get('status') else None
        
        filters = {'buyer_id': user_id}
        if status:
            filters['status'] = status
        
        orders = get_data('order', filters=filters, order='created_at.desc')
        if not orders:
            return jsonify({'success': True, 'orders': []})
        
        return jsonify({'success': True, 'orders': [_serialize_order_api_dict(order) for order in orders]})
    except Exception as e:
        app.logger.error(f'/api/orders/user error: {e}')
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/user/profile', methods=['GET', 'PUT'])
@token_required
def api_user_profile():
    """Get/update current user profile via non-versioned API for Flutter compatibility (Supabase version)."""
    try:
        user_id = request.current_user_id
        orm_user = db.session.get(User, user_id)
        user = get_data_by_id('user', user_id)
        if not user and not orm_user:
            return jsonify({'error': 'User not found'}), 404

        if request.method == 'GET':
            if orm_user:
                return jsonify({'success': True, 'user': _serialize_user_api(orm_user)})
            return jsonify({'success': True, 'user': _serialize_user_api_dict(user)})

        data = request.get_json(silent=True) or {}
        update_data = {}
        if 'first_name' in data:
            update_data['first_name'] = str(data.get('first_name') or '').strip()
        if 'last_name' in data:
            update_data['last_name'] = str(data.get('last_name') or '').strip()
        if 'phone' in data:
            update_data['phone'] = str(data.get('phone') or '').strip()
        if 'address' in data:
            update_data['address'] = str(data.get('address') or '').strip()

        if update_data:
            if orm_user:
                for key, value in update_data.items():
                    if hasattr(orm_user, key):
                        setattr(orm_user, key, value)
                db.session.commit()
            else:
                updated_user = update_data_by_id('user', user_id, update_data)
                if updated_user:
                    user = updated_user

        if orm_user:
            db.session.refresh(orm_user)
            return jsonify({'success': True, 'user': _serialize_user_api(orm_user)})
        return jsonify({'success': True, 'user': _serialize_user_api_dict(user)})
    except Exception as e:
        app.logger.error(f'/api/user/profile error: {e}')
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/rider/earnings', methods=['GET'])
@app.route('/api/v1/rider/earnings', methods=['GET'])
@token_required
@role_required('rider')
def api_rider_earnings():
    """Return rider earnings from wallet transactions."""
    try:
        rider_id = request.current_user_id
        return jsonify({
            'success': True,
            'total': get_user_earnings(rider_id, None, RIDER_WALLET_SOURCES),
            'today': get_user_earnings(rider_id, 'today', RIDER_WALLET_SOURCES),
            'week': get_user_earnings(rider_id, 'week', RIDER_WALLET_SOURCES),
            'month': get_user_earnings(rider_id, 'month', RIDER_WALLET_SOURCES),
        })
    except Exception as e:
        app.logger.error(f'/api/rider/earnings error: {e}')
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/products/<int:product_id>/reviews', methods=['GET'])
def api_product_reviews(product_id):
    """Public review listing for a product."""
    try:
        product = get_data_by_id('product', product_id)
        if not product or product.get('status') not in ['approved', 'active']:
            orm_product = db.session.get(Product, product_id)
            if orm_product and orm_product.status in ['approved', 'active']:
                product = {
                    'id': orm_product.id,
                    'name': orm_product.name,
                    'description': orm_product.description,
                    'price': orm_product.price,
                    'stock': orm_product.stock,
                    'seller_id': orm_product.seller_id,
                    'category_id': orm_product.category_id,
                    'subcategory_id': orm_product.subcategory_id,
                    'image_filename': orm_product.image_filename,
                    'gallery': orm_product.gallery,
                    'video_filename': orm_product.video_filename,
                    'status': orm_product.status,
                    'featured': orm_product.featured,
                    'created_at': orm_product.created_at,
                }
        if not product or product.get('status') not in ['approved', 'active']:
            return jsonify({'error': 'Product not found'}), 404

        reviews = get_data('review', filters={'product_id': product_id, 'status': 'published'}, order='created_at.desc')
        if not reviews:
            reviews = []

        payload = []
        for review in reviews:
            # Get user info
            user = get_data_by_id('user', review.get('user_id'))
            user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() if user else 'Anonymous'
            
            user_avatar = None
            if user and user.get('id'):
                try:
                    user_avatar = get_user_avatar_url(user.get('id'), user.get('role', 'buyer'))
                except Exception:
                    user_avatar = user.get('profile_picture')
            
            media = review.get('media') or []
            # Parse media if it's a JSON string
            if isinstance(media, str):
                try:
                    media = json.loads(media) or []
                except:
                    media = []
            if review.get('image_filename'):
                media = [{'type': 'image', 'path': _safe_upload_url(review.get('image_filename'))}] + media
            payload.append({
                'id': review.get('id'),
                'product_id': review.get('product_id'),
                'user_id': review.get('user_id'),
                'user_name': user_name,
                'buyer_name': review.get('buyer_name') or user_name,
                'user_avatar': user_avatar,
                'buyer_avatar': review.get('buyer_avatar') or user_avatar,
                'order_id': review.get('order_id'),
                'rating': review.get('rating'),
                'title': review.get('title'),
                'content': review.get('content'),
                'verified_purchase': bool(review.get('verified_purchase')),
                'media': media,
                'created_at': review.get('created_at'),
            })

        # Calculate average rating
        avg_rating = 0
        if reviews:
            total = sum(r.get('rating', 0) for r in reviews)
            avg_rating = total / len(reviews)
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'average_rating': round(float(avg_rating), 1),
            'review_count': len(payload),
            'reviews': payload,
        })
    except Exception as e:
        app.logger.error(f'/api/products/{product_id}/reviews error: {e}')
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/reviews', methods=['POST'])
@token_required
@role_required('buyer')
def api_create_review():
    """Create a verified purchase review with media upload support."""
    try:
        # Handle both JSON and multipart form data
        if request.content_type and 'multipart/form-data' in request.content_type:
            product_id = request.form.get('product_id')
            rating = request.form.get('rating')
            title = request.form.get('title', '').strip() or None
            content = request.form.get('content', '').strip() or None
        else:
            data = request.get_json(silent=True) or {}
            product_id = data.get('product_id')
            rating = data.get('rating')
            title = str(data.get('title') or '').strip() or None
            content = str(data.get('content') or '').strip() or None

        try:
            product_id = int(product_id)
            rating = int(rating)
        except Exception:
            return jsonify({'success': False, 'error': 'product_id and rating are required'}), 400

        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'error': 'rating must be between 1 and 5'}), 400

        product = get_data_by_id('product', product_id)
        if not product or product.get('status') not in ['approved', 'active']:
            orm_product = db.session.get(Product, product_id)
            if orm_product and orm_product.status in ['approved', 'active']:
                product = {
                    'id': orm_product.id,
                    'name': orm_product.name,
                    'status': orm_product.status,
                }
        if not product or product.get('status') not in ['approved', 'active']:
            return jsonify({'success': False, 'error': 'Product not found'}), 404

        can_review, order_id, message = can_user_review_product(request.current_user_id, product_id)
        if not can_review:
            return jsonify({'success': False, 'error': message}), 403

        # Process media files
        media = []
        if request.files:
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'reviews')
            os.makedirs(upload_dir, exist_ok=True)
            
            for key in request.files:
                # Accept both media[0] and media_0 formats
                if key.startswith('media[') or key.startswith('media_'):
                    file = request.files[key]
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                        filename = timestamp + filename
                        ext = filename.rsplit('.', 1)[-1].lower()
                        media_type = 'video' if ext in ['mp4', 'mov', 'avi', 'mkv', 'webm'] else 'image'
                        filepath = os.path.join(upload_dir, filename)
                        file.save(filepath)
                        media.append({'type': media_type, 'path': f'/static/uploads/reviews/{filename}'})
        else:
            # Handle JSON with URLs
            data = request.get_json(silent=True) or {}
            image_urls = data.get('image_urls') or []
            video_urls = data.get('video_urls') or []
            for path in image_urls:
                if path:
                    media.append({'type': 'image', 'path': str(path)})
            for path in video_urls:
                if path:
                    media.append({'type': 'video', 'path': str(path)})

        # Get buyer info for display
        buyer = get_data_by_id('user', request.current_user_id)
        buyer_name = f"{buyer.get('first_name', '')} {buyer.get('last_name', '')}".strip() or 'Anonymous'
        buyer_avatar = buyer.get('profile_image')

        review_data = {
            'product_id': product_id,
            'user_id': request.current_user_id,
            'buyer_id': request.current_user_id,
            'buyer_name': buyer_name,
            'buyer_avatar': buyer_avatar,
            'order_id': order_id,
            'rating': rating,
            'title': title,
            'content': content,
            'status': 'published',
            'media': json.dumps(media) if media else None,
            'verified_purchase': True,
            'created_at': datetime.utcnow().isoformat(),
        }
        review = insert_data('review', review_data)
        
        if not review:
            return jsonify({'success': False, 'error': 'Failed to create review'}), 500

        return jsonify({'success': True, 'message': 'Review submitted successfully!', 'review_id': review.get('id')}), 201
    except Exception as e:
        app.logger.error(f'/api/reviews POST error: {e}')
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/orders/rider', methods=['GET'])
@token_required
@role_required('rider')
def api_orders_rider():
    """Get orders for current rider with complete buyer and item information."""
    try:
        rider_id = request.current_user_id
        from sqlalchemy.orm import joinedload

        # Use direct SQL query with eager loading
        orders = Order.query.options(
            joinedload(Order.buyer),
            joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.seller)
        ).filter(
            db.or_(
                Order.rider_id == rider_id,
                Order.picked_up_by == rider_id,
                Order.delivered_by == rider_id
            )
        ).order_by(Order.created_at.desc()).all()

        payload = []
        for order in orders:
            # Build items list with product details
            items_list = []
            seller_info = None
            for item in order.items:
                product = item.product
                items_list.append({
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_name': product.name if product else 'Unknown',
                    'product_image': product.image_filename if product else None,
                    'quantity': item.quantity,
                    'price': float(item.price_at_time),
                })
                
                # Get seller info from first item
                if not seller_info and product and product.seller:
                    seller = product.seller
                    # Get seller business address from application
                    seller_address = seller.address
                    try:
                        seller_app = SellerApplication.query.filter_by(
                            user_id=seller.id, 
                            status='approved'
                        ).first()
                        if seller_app and seller_app.business_address:
                            seller_address = seller_app.business_address
                    except:
                        pass
                    
                    seller_info = {
                        'id': seller.id,
                        'name': f"{seller.first_name} {seller.last_name}",
                        'phone': seller.phone,
                        'address': seller_address,
                    }
            
            # Build complete order object
            order_data = {
                'id': order.id,
                'buyer_id': order.buyer_id,
                'rider_id': order.rider_id,
                'status': order.status,
                'payment_method': order.payment_method,
                'payment_status': order.payment_status,
                'total_amount': float(order.total_amount),
                'shipping_fee': 0.0,
                'subtotal': float(order.total_amount),
                'discount': 0.0,
                'shipping_address': order.shipping_address,
                'recipient_name': order.recipient_name or '',
                'recipient_phone': order.recipient_phone or '',
                'notes': order.notes,
                'order_date': order.created_at.isoformat() if order.created_at else None,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
                'items': items_list,
            }
            
            # Add buyer information
            if order.buyer:
                order_data['buyer_name'] = f"{order.buyer.first_name} {order.buyer.last_name}"
                order_data['buyer_phone'] = order.buyer.phone
                order_data['buyer_email'] = order.buyer.email
                order_data['customer'] = {
                    'id': order.buyer.id,
                    'first_name': order.buyer.first_name,
                    'last_name': order.buyer.last_name,
                    'email': order.buyer.email,
                    'phone': order.buyer.phone,
                }
            
            # Add seller information
            if seller_info:
                order_data['seller_name'] = seller_info['name']
                order_data['seller_address'] = seller_info['address']
                order_data['seller_phone'] = seller_info['phone']
            
            payload.append(order_data)
        
        return jsonify({'success': True, 'orders': payload})
    except Exception as e:
        app.logger.error(f'/api/orders/rider error: {e}')
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/orders/available', methods=['GET'])
@token_required
@role_required('rider')
def api_orders_available():
    """Get all available orders ready for pickup (no rider assigned)."""
    try:
        from sqlalchemy.orm import joinedload

        # Query orders that are ready for pickup and have no rider assigned
        orders = Order.query.options(
            joinedload(Order.buyer),
            joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.seller)
        ).filter(
            Order.rider_id == None,
            Order.status.in_(['ready_for_pickup', 'to_ship', 'pending'])
        ).order_by(Order.created_at.desc()).all()

        payload = []
        for order in orders:
            # Build items list with product details
            items_list = []
            seller_info = None
            for item in order.items:
                product = item.product
                items_list.append({
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_name': product.name if product else 'Unknown',
                    'product_image': product.image_filename if product else None,
                    'quantity': item.quantity,
                    'price': float(item.price_at_time),
                })
                
                # Get seller info from first item
                if not seller_info and product and product.seller:
                    seller = product.seller
                    # Get seller business address from application
                    seller_address = seller.address
                    try:
                        seller_app = SellerApplication.query.filter_by(
                            user_id=seller.id, 
                            status='approved'
                        ).first()
                        if seller_app and seller_app.business_address:
                            seller_address = seller_app.business_address
                    except:
                        pass
                    
                    seller_info = {
                        'id': seller.id,
                        'name': f"{seller.first_name} {seller.last_name}",
                        'phone': seller.phone,
                        'address': seller_address,
                    }
            
            # Build complete order object
            order_data = {
                'id': order.id,
                'buyer_id': order.buyer_id,
                'rider_id': order.rider_id,
                'status': order.status,
                'payment_method': order.payment_method,
                'payment_status': order.payment_status,
                'total_amount': float(order.total_amount),
                'shipping_fee': 0.0,
                'subtotal': float(order.total_amount),
                'discount': 0.0,
                'shipping_address': order.shipping_address,
                'recipient_name': order.recipient_name or '',
                'recipient_phone': order.recipient_phone or '',
                'notes': order.notes,
                'order_date': order.created_at.isoformat() if order.created_at else None,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
                'items': items_list,
            }
            
            # Add buyer information
            if order.buyer:
                order_data['buyer_name'] = f"{order.buyer.first_name} {order.buyer.last_name}"
                order_data['buyer_phone'] = order.buyer.phone
                order_data['buyer_email'] = order.buyer.email
                order_data['customer'] = {
                    'id': order.buyer.id,
                    'first_name': order.buyer.first_name,
                    'last_name': order.buyer.last_name,
                    'email': order.buyer.email,
                    'phone': order.buyer.phone,
                }
            
            # Add seller information
            if seller_info:
                order_data['seller_name'] = seller_info['name']
                order_data['seller_address'] = seller_info['address']
                order_data['seller_phone'] = seller_info['phone']
            
            payload.append(order_data)
        
        return jsonify({'success': True, 'orders': payload})
    except Exception as e:
        app.logger.error(f'/api/orders/available error: {e}')
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/v1/orders/seller', methods=['GET'])
@token_required
@role_required('seller')
def api_v1_orders_seller():
    """Get orders for a seller (mobile API v1) (Supabase version)."""
    try:
        seller_id = request.current_user_id
        status = _normalize_status(request.args.get('status')) if request.args.get('status') else None
        
        # Get all products for this seller
        products = get_data('product', filters={'seller_id': seller_id})
        if not products:
            return jsonify({'success': True, 'orders': []})
        
        product_ids = [p.get('id') for p in products]
        
        # Get order items for these products
        all_order_items = []
        for pid in product_ids:
            items = get_data('order_item', filters={'product_id': pid})
            all_order_items.extend(items)
        
        if not all_order_items:
            return jsonify({'success': True, 'orders': []})
        
        # Get unique order IDs
        order_ids = list(set(item.get('order_id') for item in all_order_items))
        
        # Get orders
        orders = []
        for oid in order_ids:
            order = get_data_by_id('order', oid)
            if order:
                if not status or order.get('status') == status:
                    orders.append(order)
        
        return jsonify({'success': True, 'orders': [_serialize_order_api_dict(order) for order in orders]})
    except Exception as e:
        app.logger.error(f'/api/orders/seller error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/orders/status', methods=['PUT'])
@token_required
@role_required('seller', 'rider', 'admin')
def api_update_order_status():
    """Update order status (Supabase version)."""
    try:
        data = request.get_json(silent=True) or {}
        order_id = data.get('order_id')
        new_status = _normalize_status(data.get('status'))
        rider_id = data.get('rider_id')
        if not order_id or not new_status:
            return jsonify({'error': 'order_id and a valid status are required'}), 400
        
        order = get_data_by_id('order', order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        actor_role = request.current_user_role
        update_data = {}
        
        if actor_role == 'seller':
            # Check if seller can manage this order
            order_items = get_data('order_item', filters={'order_id': order_id})
            seller_can_manage = False
            for item in order_items:
                product = get_data_by_id('product', item.get('product_id'))
                if product and product.get('seller_id') == request.current_user_id:
                    seller_can_manage = True
                    break
            
            if not seller_can_manage:
                return jsonify({'error': 'Order is not associated with your products'}), 403
            if new_status not in ('processing', 'ready_for_pickup'):
                return jsonify({'error': 'Seller can only set Processing or Ready for Pickup'}), 403
        elif actor_role == 'rider':
            if new_status not in ('picked_up', 'out_for_delivery', 'delivered'):
                return jsonify({'error': 'Rider can only set Picked Up, Out for Delivery, or Delivered'}), 403
            assigned_rider_id = order.get('rider_id') or order.get('picked_up_by') or order.get('delivered_by')
            if assigned_rider_id and assigned_rider_id != request.current_user_id:
                return jsonify({'error': 'Order is assigned to another rider'}), 403
            if not assigned_rider_id:
                update_data['rider_id'] = request.current_user_id
        else:
            if new_status not in ARCH_ORDER_STATUSES:
                return jsonify({'error': 'Invalid status'}), 400

        if rider_id is not None and actor_role in ('seller', 'admin'):
            try:
                rider_id = int(rider_id)
            except Exception:
                return jsonify({'error': 'rider_id must be numeric'}), 400
            riders = get_data('user', filters={'id': rider_id, 'role': 'rider', 'status': 'active'})
            if not riders or len(riders) == 0:
                return jsonify({'error': 'rider_id is invalid'}), 400
            update_data['rider_id'] = riders[0].get('id')

        now = datetime.utcnow()
        if new_status == 'picked_up':
            picked_up_by = request.current_user_id if actor_role == 'rider' else (order.get('picked_up_by') or order.get('rider_id'))
            update_data['picked_up_by'] = picked_up_by
            update_data['picked_up_at'] = now.isoformat()
            if actor_role == 'rider' and not order.get('rider_id'):
                update_data['rider_id'] = request.current_user_id
        elif new_status == 'delivered':
            delivered_by = request.current_user_id if actor_role == 'rider' else (order.get('delivered_by') or order.get('rider_id'))
            update_data['delivered_by'] = delivered_by
            update_data['delivered_at'] = now.isoformat()
            if actor_role == 'rider' and not order.get('rider_id'):
                update_data['rider_id'] = request.current_user_id

        update_data['status'] = new_status
        update_data['updated_at'] = now.isoformat()
        
        updated_order = update_data_by_id('order', order_id, update_data)
        if updated_order:
            order = updated_order

        try:
            order_orm = db.session.get(Order, order_id)
            if order_orm:
                if new_status == 'completed':
                    _release_commissions(order_orm)
                elif new_status == 'refunded':
                    _release_rider_earning(order_orm)
        except Exception as e:
            app.logger.error(f'Failed to release earnings for order {order_id}: {e}')
        
        return jsonify({'success': True, 'order': _serialize_order_api_dict(order)})
    except Exception as e:
        app.logger.error(f'/api/orders/status error: {e}')
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# MOBILE API v1 - REST Endpoints for Flutter Mobile App
# ============================================================================

# API Authentication Endpoints
@app.route('/api/v1/auth/login', methods=['POST'])
def api_v1_login():
    """Mobile API login endpoint with JWT tokens (Supabase version)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        users = get_data('user', filters={'email': email})
        if not users or len(users) == 0:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = users[0]
        
        # Check password (support both bcrypt and legacy)
        password_valid = False
        user_password = user.get('password', '')
        if user_password and user_password.startswith('$2b$'):
            password_valid = verify_password(password, user_password)
        else:
            # Legacy password check (plain text comparison - should be migrated)
            password_valid = (password == user_password)
        
        if not password_valid:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check user status - require admin approval
        user_status = user.get('status')
        if user_status == 'pending':
            return jsonify({'error': 'Your account is pending admin approval.'}), 401
        elif user_status == 'rejected':
            return jsonify({'error': 'Account was rejected. Please contact support'}), 401
        elif user_status == 'suspended':
            return jsonify({'error': 'Account is suspended. Please contact support'}), 401
        elif user_status != 'active':
            return jsonify({'error': 'Account is not active'}), 401
        
        # Generate JWT tokens
        tokens = generate_tokens(user.get('id'), user.get('role'))
        
        # Return user data and tokens
        return jsonify({
            'success': True,
            'user': {
                'id': user.get('id'),
                'email': user.get('email'),
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'role': user.get('role'),
                'phone': user.get('phone'),
                'profile_image': get_user_avatar_url(user.get('id'), user.get('role'))
            },
            'tokens': tokens
        })
        
    except Exception as e:
        app.logger.error(f"API v1 login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/auth/register', methods=['POST'])
def api_v1_register():
    """Mobile API registration endpoint (Supabase version)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        # Extract required fields
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone = data.get('phone', '').strip()
        role = data.get('role', 'buyer').strip().lower()
        address = data.get('address', '').strip()

        # Validate required fields
        if not all([email, password, first_name, last_name, phone]):
            return jsonify({'error': 'All required fields must be provided: email, password, first_name, last_name, phone'}), 400
        
        if role not in ['buyer', 'rider']:
            return jsonify({'error': 'Invalid role. Must be buyer or rider'}), 400
        
        # Verify email using EmailListVerify API (if configured)
        api_key = os.getenv('EMAILLISTVERIFY_API_KEY') or os.getenv('EMAILLISTVERIFY_SECRET')
        if api_key:
            is_valid_email = verify_email_with_emaillistverify(email)
            if not is_valid_email:
                return jsonify({'error': 'Please enter a valid email address. We could not verify this email.'}), 400
        
        # Check if email already exists
        existing_users = get_data('user', filters={'email': email})
        if existing_users and len(existing_users) > 0:
            return jsonify({'error': 'Email already registered'}), 409
            
        # Hash password
        hashed_password = hash_password(password)
        
        # Create new user
        new_user_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': hashed_password,
            'phone': phone,
            'address': address,
            'role': role,
            'status': 'pending',  # All roles require approval
            'email_verified': False, # Verification happens on approval
            'created_at': datetime.utcnow().isoformat()
        }
        
        new_user = insert_data('user', new_user_data)
        if not new_user:
            return jsonify({'error': 'Failed to create user'}), 500
        
        # If rider, create RiderApplication record
        if role == 'rider':
            try:
                vehicle_type = data.get('vehicle_type', 'motorcycle').strip()
                vehicle_number = data.get('vehicle_number', '').strip()
                
                rider_app_data = {
                    'user_id': new_user.get('id'),
                    'vehicle_type': vehicle_type,
                    'vehicle_number': vehicle_number,
                    'status': 'pending',
                    'applied_at': datetime.utcnow().isoformat()
                }
                
                rider_app = insert_data('rider_application', rider_app_data)
                if not rider_app:
                    app.logger.error(f"Failed to create RiderApplication for user {new_user.get('id')}")
                else:
                    app.logger.info(f"RiderApplication created for user {new_user.get('id')}")
            except Exception as e:
                app.logger.error(f"Error creating RiderApplication: {e}")
        
        # Notify admin of new registration
        try:
            admin_users = get_data('user', filters={'role': 'admin'})
            if admin_users:
                for admin in admin_users:
                    notification_data = {
                        'user_id': admin.get('id'),
                        'message': f'New {role} registration: {first_name} {last_name} ({email}) is awaiting approval.',
                        'created_at': datetime.utcnow().isoformat()
                    }
                    insert_data('notification', notification_data)
        except Exception as e:
            app.logger.error(f"Failed to create admin notification for new user: {e}")

        # Return a success message, but no tokens yet
        return jsonify({
            'success': True,
            'message': 'Registration successful. Your account is now pending admin approval.'
        }), 201

    except Exception as e:
        app.logger.error(f"API v1 registration error: {e}")
        return jsonify({'error': 'An internal error occurred during registration.'}), 500

@app.route('/api/v1/auth/refresh', methods=['POST'])
def api_v1_refresh_token():
    """Refresh access token using refresh token (Supabase version)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return jsonify({'error': 'Refresh token is required'}), 400
        
        # Verify refresh token
        payload = verify_token(refresh_token, 'refresh')
        if not payload:
            return jsonify({'error': 'Invalid or expired refresh token'}), 401
        
        # Get user
        user = get_data_by_id('user', payload['user_id'])
        if not user or user.get('status') != 'active':
            return jsonify({'error': 'User not found or inactive'}), 401
        
        # Generate new tokens
        tokens = generate_tokens(user.get('id'), user.get('role'))
        
        return jsonify({
            'success': True,
            'tokens': tokens
        })
        
    except Exception as e:
        app.logger.error(f"API v1 refresh token error: {e}")
        return jsonify({'error': 'Internal server error'}), 500



@app.route('/api/v1/auth/forgot-password', methods=['POST'])
def api_v1_forgot_password():
    """Send password reset code to user's email (Mobile API) - FIXED VERSION."""
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON data', 'error_type': 'invalid_request'}), 400
        
        email = (data.get('email') or '').strip()
        if not email:
            return jsonify({'success': False, 'error': 'Email is required', 'error_type': 'missing_email'}), 400
        
        # Check if user exists using ORM
        try:
            user = User.query.filter_by(email=email).first()
        except Exception as e:
            app.logger.error(f"Database query error: {str(e)}")
            return jsonify({'success': False, 'error': 'Database error. Please try again.', 'error_type': 'database_error'}), 500
        
        if not user:
            return jsonify({'success': False, 'error': 'No account found with this email address', 'error_type': 'user_not_found'}), 404
        
        # Generate 6-digit reset code
        reset_code = str(random.randint(100000, 999999))
        
        # Store code using ORM
        try:
            user.verification_code = reset_code
            db.session.commit()
            app.logger.info(f"Reset code generated for {email}: {reset_code}")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Failed to save reset code: {str(e)}")
            return jsonify({'success': False, 'error': 'Failed to generate reset code. Please try again.', 'error_type': 'code_generation_failed'}), 500
        
        # Send email
        try:
            if send_verification_email(email, reset_code):
                app.logger.info(f"Password reset code sent to {email}")
                return jsonify({'success': True, 'message': 'Reset code sent to your email. Please check your inbox.'}), 200
            else:
                app.logger.error(f"Failed to send reset email to {email}")
                return jsonify({'success': False, 'error': 'Failed to send email. Please check your email address and try again.', 'error_type': 'email_failed'}), 500
        except Exception as e:
            app.logger.error(f"Email sending error: {str(e)}")
            return jsonify({'success': False, 'error': 'Failed to send email. Please try again later.', 'error_type': 'email_error'}), 500
        
    except Exception as e:
        app.logger.error(f"Unexpected error in forgot password: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': 'An unexpected error occurred. Please try again.', 'error_type': 'server_error'}), 500


@app.route('/api/v1/auth/reset-password', methods=['POST'])
def api_v1_reset_password():
    """Reset user password with verification code (Mobile API) - FIXED VERSION."""
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON data', 'error_type': 'invalid_request'}), 400
        
        email = (data.get('email') or '').strip()
        code = (data.get('code') or '').strip()
        new_password = data.get('new_password')
        
        # Validate required fields
        if not email:
            return jsonify({'success': False, 'error': 'Email is required', 'error_type': 'missing_email'}), 400
        if not code:
            return jsonify({'success': False, 'error': 'Reset code is required', 'error_type': 'missing_code'}), 400
        if not new_password:
            return jsonify({'success': False, 'error': 'New password is required', 'error_type': 'missing_password'}), 400
        
        # Validate password strength
        is_valid, password_message = validate_password(new_password)
        if not is_valid:
            return jsonify({'success': False, 'error': password_message, 'error_type': 'weak_password'}), 400
        
        # Find user using ORM
        try:
            user = User.query.filter_by(email=email).first()
        except Exception as e:
            app.logger.error(f"Database query error: {str(e)}")
            return jsonify({'success': False, 'error': 'Database error. Please try again.', 'error_type': 'database_error'}), 500
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found', 'error_type': 'user_not_found'}), 404
        
        # Verify reset code
        if not user.verification_code:
            return jsonify({'success': False, 'error': 'No reset code found. Please request a new code.', 'error_type': 'no_code'}), 400
        
        if user.verification_code != code:
            return jsonify({'success': False, 'error': 'Invalid verification code. Please check your email and try again.', 'error_type': 'invalid_code'}), 400
        
        # Update password using ORM
        try:
            user.password = new_password
            user.verification_code = None
            db.session.commit()
            app.logger.info(f"Password reset successful for {email}")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Database update error: {str(e)}")
            return jsonify({'success': False, 'error': 'Failed to update password. Please try again.', 'error_type': 'update_failed'}), 500
        
        # Send confirmation email (don't fail if this fails)
        try:
            from email.utils import formataddr
            subject = 'Kids Kingdom - Password Changed Successfully'
            body = f'''Hello {user.first_name},

Your password has been successfully changed.

If you didn't make this change, please contact us immediately at support@kidskingdom.com

Best regards,
Kids Kingdom Team'''
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = formataddr(('Kids Kingdom', app.config['MAIL_SENDER']))
            msg['To'] = email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
                smtp.send_message(msg)
            app.logger.info(f"Confirmation email sent to {email}")
        except Exception as e:
            app.logger.warning(f"Failed to send confirmation email: {str(e)}")
        
        return jsonify({'success': True, 'message': 'Password reset successfully. You can now login with your new password.'}), 200
        
    except Exception as e:
        app.logger.error(f"Unexpected error in reset password: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': 'An unexpected error occurred. Please try again.', 'error_type': 'server_error'}), 500


# Product API Endpoints

# --- Admin API: List pending users and approve user ---
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/api/v1/admin/users', methods=['GET'])
@jwt_required()
def get_pending_users():
    """Get a list of users pending approval (Supabase version)."""
    try:
        current_user_id = get_jwt_identity()
        user = get_data_by_id('user', current_user_id)

        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403

        # FIXED: Order by latest first (desc)
        pending_users = get_data('user', filters={'status': 'pending'}, order='created_at.desc')
        if not pending_users:
            pending_users = []
        
        users_data = []
        for u in pending_users:
            created_at_utc = u.get('created_at')
            # Convert to PH time for display
            if isinstance(created_at_utc, str):
                try:
                    created_at_utc = datetime.fromisoformat(created_at_utc.replace('Z', '+00:00'))
                except:
                    created_at_utc = None
            
            users_data.append({
                'id': u.get('id'),
                'first_name': u.get('first_name'),
                'last_name': u.get('last_name'),
                'email': u.get('email'),
                'phone': u.get('phone'),
                'role': u.get('role'),
                'created_at': u.get('created_at'),  # Keep UTC for sorting
                'created_at_ph': format_ph_datetime(created_at_utc)  # Add PH time
            })

        return jsonify(users_data), 200

    except Exception as e:
        app.logger.error(f"Error fetching pending users: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/v1/admin/users/<int:user_id>/approve', methods=['POST'])
@jwt_required()
def approve_user(user_id):
    """Approve a user registration (Supabase version)."""
    try:
        current_user_id = get_jwt_identity()
        admin_user = get_data_by_id('user', current_user_id)

        if not admin_user or admin_user.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403

        user_to_approve = get_data_by_id('user', user_id)

        if not user_to_approve:
            return jsonify({'error': 'User not found'}), 404

        if user_to_approve.get('status') != 'pending':
            return jsonify({'error': 'User is not pending approval'}), 400

        # Update user status to active
        update_data = {'status': 'active', 'approved_by': admin_user.get('id'), 'approved_at': datetime.utcnow().isoformat()}
        updated_user = update_data_by_id('user', user_id, update_data)
        
        # If user is a rider, also approve their rider application
        if user_to_approve.get('role') == 'rider':
            rider_apps = get_data('rider_application', filters={'user_id': user_id})
            if rider_apps and len(rider_apps) > 0:
                update_data_by_id('rider_application', rider_apps[0].get('id'), {'status': 'approved'})
                
                # Send rider approval email
                try:
                    user_name = f"{user_to_approve.get('first_name', '')} {user_to_approve.get('last_name', '')}".strip()
                    send_rider_status_email(user_to_approve.get('email'), approved=True, user_name=user_name)
                    app.logger.info(f'Rider approval email sent to {user_to_approve.get("email")}')
                except Exception as email_error:
                    app.logger.exception(f"Failed to send rider approval email: {email_error}")
        else:
            # Send buyer/seller approval email
            try:
                user_name = f"{user_to_approve.get('first_name', '')} {user_to_approve.get('last_name', '')}".strip()
                user_email = user_to_approve.get('email')
                user_role = user_to_approve.get('role', 'buyer').capitalize()
                
                subject = f'🎉 Your {user_role} Account is Approved!'
                
                html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white; }}
        .content {{ padding: 30px; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #6c757d; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Account Approved!</h1>
        </div>
        <div class="content">
            <p>Hi {user_name}!</p>
            <p><strong>Great news!</strong> Your {user_role} account has been approved by our admin team.</p>
            <p>You can now log in and start using Kids Kingdom!</p>
            <p style="text-align: center;">
                <a href="https://kids-kingdom.onrender.com/login" class="button">Login Now</a>
            </p>
            <p>Thank you for joining Kids Kingdom! 💙</p>
        </div>
        <div class="footer">
            <p>© 2026 Kids Kingdom. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
                """
                
                text_body = f"""
🎉 Your {user_role} Account is Approved!

Hi {user_name}!

Great news! Your {user_role} account has been approved by our admin team.

You can now log in and start using Kids Kingdom!

Login at: https://kids-kingdom.onrender.com/login

Thank you for joining Kids Kingdom! 💙

---
© 2026 Kids Kingdom. All rights reserved.
                """
                
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = app.config['MAIL_SENDER']
                msg['To'] = user_email
                
                part1 = MIMEText(text_body, 'plain', 'utf-8')
                part2 = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(part1)
                msg.attach(part2)
                
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(app.config['MAIL_SENDER'], app.config['MAIL_APP_PASSWORD'])
                    smtp.send_message(msg)
                app.logger.info(f'Approval email sent to {user_email}')
            except Exception as email_error:
                app.logger.exception(f"Failed to send approval email: {email_error}")

        return jsonify({'success': True, 'message': f'User {user_to_approve.get("email")} approved.'}), 200

    except Exception as e:
        app.logger.error(f"Error approving user {user_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/v1/admin/rider-applications', methods=['GET'])
@jwt_required()
def get_rider_applications():
    """Get a list of rider applications (Supabase version)."""
    try:
        current_user_id = get_jwt_identity()
        user = get_data_by_id('user', current_user_id)

        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403

        # Get all rider applications ordered by latest first
        rider_apps = get_data('rider_application', order='applied_at.desc')
        if not rider_apps:
            rider_apps = []
        
        apps_data = []
        for app in rider_apps:
            # Get user details
            user_id = app.get('user_id')
            user_data = get_data_by_id('user', user_id) if user_id else None
            
            applied_at_utc = app.get('applied_at')
            if isinstance(applied_at_utc, str):
                try:
                    applied_at_utc = datetime.fromisoformat(applied_at_utc.replace('Z', '+00:00'))
                except:
                    applied_at_utc = None
            
            apps_data.append({
                'id': app.get('id'),
                'user_id': user_id,
                'user_name': f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}" if user_data else 'Unknown',
                'email': user_data.get('email') if user_data else 'N/A',
                'phone': user_data.get('phone') if user_data else 'N/A',
                'vehicle_type': app.get('vehicle_type'),
                'vehicle_number': app.get('vehicle_number'),
                'employee_id': app.get('employee_id'),
                'status': app.get('status'),
                'applied_at': app.get('applied_at'),  # Keep UTC for sorting
                'applied_at_ph': format_ph_datetime(applied_at_utc),  # Add PH time
                'reviewed_at': app.get('reviewed_at'),
                'reviewed_by': app.get('reviewed_by')
            })

        return jsonify(apps_data), 200

    except Exception as e:
        app.logger.error(f"Error fetching rider applications: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/v1/admin/rider-applications/<int:app_id>/approve', methods=['POST'])
@jwt_required()
def approve_rider_application(app_id):
    """Approve a rider application (Supabase version)."""
    try:
        current_user_id = get_jwt_identity()
        admin_user = get_data_by_id('user', current_user_id)

        if not admin_user or admin_user.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403

        rider_app = get_data_by_id('rider_application', app_id)

        if not rider_app:
            return jsonify({'error': 'Rider application not found'}), 404

        if rider_app.get('status') != 'pending':
            return jsonify({'error': 'Application is not pending'}), 400

        # Update application status
        update_data = {
            'status': 'approved',
            'reviewed_at': datetime.utcnow().isoformat(),
            'reviewed_by': admin_user.get('id')
        }
        update_data_by_id('rider_application', app_id, update_data)
        
        # Also update user status to active and role to rider
        user_id = rider_app.get('user_id')
        update_data_by_id('user', user_id, {
            'status': 'active',
            'role': 'rider',
            'email_verified': True
        })
        
        # Get user details for email
        user = get_data_by_id('user', user_id)
        
        # Send approval email
        try:
            if user:
                user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                send_rider_status_email(user.get('email'), approved=True, user_name=user_name)
                app.logger.info(f'Approval email sent to rider {user.get("email")}')
        except Exception as email_error:
            app.logger.exception(f"Failed to send approval email to rider: {email_error}")
            # Don't fail the approval if email fails

        return jsonify({'success': True, 'message': 'Rider application approved'}), 200

    except Exception as e:
        app.logger.error(f"Error approving rider application {app_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/v1/admin/rider-applications/<int:app_id>/reject', methods=['POST'])
@jwt_required()
def reject_rider_application(app_id):
    """Reject a rider application (Supabase version)."""
    try:
        current_user_id = get_jwt_identity()
        admin_user = get_data_by_id('user', current_user_id)

        if not admin_user or admin_user.get('role') != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403

        rider_app = get_data_by_id('rider_application', app_id)

        if not rider_app:
            return jsonify({'error': 'Rider application not found'}), 404

        if rider_app.get('status') != 'pending':
            return jsonify({'error': 'Application is not pending'}), 400

        # Update application status
        update_data = {
            'status': 'rejected',
            'reviewed_at': datetime.utcnow().isoformat(),
            'reviewed_by': admin_user.get('id')
        }
        update_data_by_id('rider_application', app_id, update_data)

        return jsonify({'success': True, 'message': 'Rider application rejected'}), 200

    except Exception as e:
        app.logger.error(f"Error rejecting rider application {app_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/v1/products', methods=['GET'])
def api_v1_products():
    """Get products with pagination, filtering, and search (Supabase version)."""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        category_id = request.args.get('category_id', type=int)
        subcategory_id = request.args.get('subcategory_id', type=int)
        seller_id = request.args.get('seller_id', type=int)
        search = request.args.get('search', '').strip()
        featured = request.args.get('featured', type=bool)
        sort_by = request.args.get('sort_by', 'created_at')  # created_at, price, name
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build filters
        filters = {'status': ['approved', 'active']}
        if category_id:
            filters['category_id'] = category_id
        if subcategory_id:
            filters['subcategory_id'] = subcategory_id
        if seller_id:
            filters['seller_id'] = seller_id
        if featured is not None:
            filters['featured'] = featured
        
        # Determine sort order
        if sort_order == 'asc':
            order = f'{sort_by}.asc'
        else:
            order = f'{sort_by}.desc'
        
        # Fetch products with limit for pagination (client-side filtering for search)
        offset = (page - 1) * per_page
        limit = per_page
        
        if search:
            # Fetch more products for client-side search filtering
            all_products = get_data('product', filters=filters, order=order, limit=500)
            if not all_products:
                all_products = []
            
            # Client-side filtering for search
            filtered_products = []
            for p in all_products:
                name = p.get('name', '').lower()
                description = p.get('description', '').lower()
                if search.lower() in name or search.lower() in description:
                    filtered_products.append(p)
            
            # Apply pagination to filtered results
            total = len(filtered_products)
            paginated_products = filtered_products[offset:offset + limit]
        else:
            # No search, use Supabase filtering directly
            paginated_products = get_data('product', filters=filters, order=order, limit=limit, offset=offset)
            if not paginated_products:
                paginated_products = []
            
            # Get total count
            total = count_data('product', filters=filters)
            if total is None:
                total = len(paginated_products)
        
        # Format products using the API serialization function
        products = [_serialize_product_api_dict(p) for p in paginated_products]
        
        # Calculate pagination info
        if total is None or total == 0:
            total = len(products)
        total_pages = (total + per_page - 1) // per_page if total > 0 else 1
        has_next = page < total_pages
        has_prev = page > 1
        
        return jsonify({
            'success': True,
            'products': products,
            'pagination': {
                'page': page,
                'pages': total_pages,
                'per_page': per_page,
                'total': total,
                'has_next': has_next,
                'has_prev': has_prev
            }
        })
        
    except Exception as e:
        app.logger.error(f"API v1 products error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/products/sync', methods=['GET'])
@token_required
def api_v1_products_sync():
    """Get only products that have been added or modified since last sync timestamp
    
    Query params:
    - last_sync: ISO8601 timestamp (e.g., 2024-04-17T12:30:00)
    - per_page: max results (default: 50)
    
    Returns: Products modified/added since last_sync timestamp
    """
    try:
        last_sync_str = request.args.get('last_sync')
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        # Default to fetching all if no timestamp provided
        filters = {'status': 'active'}
        
        if last_sync_str:
            try:
                last_sync = datetime.fromisoformat(last_sync_str.replace('Z', '+00:00'))
                # Make naive to match database timestamps (avoid offset-naive vs offset-aware comparison)
                if last_sync.tzinfo is not None:
                    last_sync = last_sync.replace(tzinfo=None)
                filters['created_at'] = f'gte.{last_sync.isoformat()}'
            except (ValueError, AttributeError):
                pass  # Invalid timestamp, fetch all
        
        # Fetch products ordered by created_at desc
        products = get_data('product', filters=filters, order='created_at.desc', limit=per_page)
        if not products:
            products = []
        
        # Format products
        formatted_products = []
        for product in products:
            product_id = product.get('id')
            
            # Calculate average rating
            reviews = get_data('review', filters={'product_id': product_id, 'status': 'published'})
            if reviews:
                avg_rating = sum(r.get('rating', 0) for r in reviews) / len(reviews)
                review_count = len(reviews)
            else:
                avg_rating = 0
                review_count = 0
            
            # Get seller info
            seller_id = product.get('seller_id')
            seller = get_data_by_id('user', seller_id) if seller_id else None
            seller_app = None
            if seller_id:
                seller_apps = get_data('seller_application', filters={'user_id': seller_id, 'status': 'approved'})
                if seller_apps:
                    seller_app = seller_apps[0]
            
            formatted_products.append({
                'id': product.get('id'),
                'name': product.get('name'),
                'description': product.get('description'),
                'price': float(product.get('price', 0)),
                'stock': product.get('stock', 0),
                'image': _safe_upload_url(product.get('image_filename')) if product.get('image_filename') else None,
                'gallery': product.get('gallery') or [],
                'category': product.get('category_id'),  # Would need to fetch category name separately
                'category_id': product.get('category_id'),
                'seller_id': seller_id,
                'seller': {
                    'id': seller.get('id') if seller else None,
                    'name': f"{seller.get('first_name', '')} {seller.get('last_name', '')}".strip() if seller else None,
                    'store_name': seller_app.get('store_name') if seller_app else None,
                    'store_logo': _safe_upload_url(seller_app.get('store_logo')) if seller_app and seller_app.get('store_logo') else None
                },
                'rating': float(avg_rating),
                'review_count': review_count,
                'created_at': product.get('created_at'),
                'updated_at': product.get('updated_at')
            })
        
        return jsonify({
            'success': True,
            'products': formatted_products,
            'last_sync': last_sync_str or datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"API v1 products sync error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/products/<int:product_id>', methods=['GET'])
def api_v1_product_detail(product_id):
    """Get detailed product information (Supabase version)."""
    try:
        orm_product = db.session.get(Product, product_id)
        if orm_product and orm_product.status in ['approved', 'active']:
            product = {
                'id': orm_product.id,
                'name': orm_product.name,
                'description': orm_product.description,
                'price': orm_product.price,
                'stock': orm_product.stock,
                'seller_id': orm_product.seller_id,
                'category_id': orm_product.category_id,
                'subcategory_id': orm_product.subcategory_id,
                'image_filename': orm_product.image_filename,
                'gallery': orm_product.gallery,
                'video_filename': orm_product.video_filename,
                'status': orm_product.status,
                'featured': orm_product.featured,
                'created_at': orm_product.created_at,
            }
            # Build the response directly from the local ORM row.
            reviews = get_data('review', filters={'product_id': product_id, 'status': 'published'}, order='created_at.desc', limit=10)
            if not reviews:
                reviews = []

            all_reviews = get_data('review', filters={'product_id': product_id})
            if all_reviews:
                avg_rating = sum(r.get('rating', 0) for r in all_reviews) / len(all_reviews)
                review_count = len(all_reviews)
            else:
                avg_rating = 0
                review_count = 0

            review_data = []
            for review in reviews:
                user = get_data_by_id('user', review.get('user_id'))
                user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() if user else 'Unknown'
                review_data.append({
                    'id': review.get('id'),
                    'rating': review.get('rating'),
                    'title': review.get('title'),
                    'content': review.get('content'),
                    'user_name': user_name,
                    'created_at': review.get('created_at'),
                    'verified_purchase': review.get('verified_purchase')
                })

            seller_id = product.get('seller_id')
            seller = get_data_by_id('user', seller_id) if seller_id else None
            seller_app = None
            if seller_id:
                seller_apps = get_data('seller_application', filters={'user_id': seller_id, 'status': 'approved'})
                if seller_apps:
                    seller_app = seller_apps[0]

            return jsonify({
                'success': True,
                'product': {
                    'id': product.get('id'),
                    'name': product.get('name'),
                    'description': product.get('description'),
                    'price': float(product.get('price', 0)),
                    'stock': product.get('stock', 0),
                    'image': url_for('static', filename=f'uploads/{product.get("image_filename")}') if product.get('image_filename') else None,
                    'gallery': product.get('gallery') or [],
                    'video': url_for('static', filename=f'uploads/{product.get("video_filename")}') if product.get('video_filename') else None,
                    'category_id': product.get('category_id'),
                    'subcategory_id': product.get('subcategory_id'),
                    'seller_id': seller_id,
                    'seller_name': f"{seller.get('first_name', '')} {seller.get('last_name', '')}".strip() if seller else None,
                    'store_name': seller_app.get('store_name') if seller_app else None,
                    'store_logo': _safe_upload_url(seller_app.get('store_logo')) if seller_app and seller_app.get('store_logo') else None,
                    'store_background': _safe_upload_url(seller_app.get('store_background')) if seller_app and seller_app.get('store_background') else None,
                    'seller': {
                        'id': seller.get('id') if seller else None,
                        'name': f"{seller.get('first_name', '')} {seller.get('last_name', '')}".strip() if seller else None,
                        'store_name': seller_app.get('store_name') if seller_app else None,
                        'store_logo': _safe_upload_url(seller_app.get('store_logo')) if seller_app and seller_app.get('store_logo') else None
                    },
                    'featured': product.get('featured'),
                    'rating': round(float(avg_rating), 1),
                    'review_count': review_count,
                    'reviews': review_data,
                    'created_at': product.get('created_at')
                }
            })
        else:
            product = get_data_by_id('product', product_id)
        if not product or product.get('status') not in ['approved', 'active']:
            return jsonify({'error': 'Product not found'}), 404
        
        # Get product reviews
        reviews = get_data('review', filters={'product_id': product_id, 'status': 'published'}, order='created_at.desc', limit=10)
        if not reviews:
            reviews = []
        
        # Calculate average rating
        all_reviews = get_data('review', filters={'product_id': product_id})
        if all_reviews:
            avg_rating = sum(r.get('rating', 0) for r in all_reviews) / len(all_reviews)
            review_count = len(all_reviews)
        else:
            avg_rating = 0
            review_count = 0
        
        # Format reviews
        review_data = []
        for review in reviews:
            user = get_data_by_id('user', review.get('user_id'))
            user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() if user else 'Unknown'
            
            # Parse media if it's a JSON string
            media = review.get('media') or []
            if isinstance(media, str):
                try:
                    media = json.loads(media) or []
                except:
                    media = []
            
            review_data.append({
                'id': review.get('id'),
                'rating': review.get('rating'),
                'title': review.get('title'),
                'content': review.get('content'),
                'user_name': user_name,
                'created_at': review.get('created_at'),
                'verified_purchase': review.get('verified_purchase'),
                'media': media
            })
        
        # Get seller info
        seller_id = product.get('seller_id')
        seller = get_data_by_id('user', seller_id) if seller_id else None
        seller_app = None
        if seller_id:
            seller_apps = get_data('seller_application', filters={'user_id': seller_id, 'status': 'approved'})
            if seller_apps:
                seller_app = seller_apps[0]
        
        return jsonify({
            'success': True,
            'product': {
                'id': product.get('id'),
                'name': product.get('name'),
                'description': product.get('description'),
                'price': float(product.get('price', 0)),
                'stock': product.get('stock', 0),
                'image': url_for('static', filename=f'uploads/{product.get("image_filename")}') if product.get('image_filename') else None,
                'gallery': product.get('gallery') or [],
                'video': url_for('static', filename=f'uploads/{product.get("video_filename")}') if product.get('video_filename') else None,
                'category_id': product.get('category_id'),
                'subcategory_id': product.get('subcategory_id'),
                'seller_id': seller_id,
                'seller': {
                    'id': seller.get('id') if seller else None,
                    'name': f"{seller.get('first_name', '')} {seller.get('last_name', '')}".strip() if seller else None,
                    'store_name': seller_app.get('store_name') if seller_app else None,
                    'store_logo': _safe_upload_url(seller_app.get('store_logo')) if seller_app and seller_app.get('store_logo') else None
                },
                'featured': product.get('featured'),
                'rating': round(float(avg_rating), 1),
                'review_count': review_count,
                'reviews': review_data,
                'created_at': product.get('created_at')
            }
        })
        
    except Exception as e:
        app.logger.error(f"API v1 product detail error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Order API Endpoints
@app.route('/api/v1/orders', methods=['GET', 'POST'])
@token_required
def api_v1_orders():
    """Handle order operations - GET (list) and POST (create) (Supabase version)."""
    try:
        if request.method == 'GET':
            # List user's orders
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)
            status = request.args.get('status')
            
            filters = {'buyer_id': request.current_user_id}
            if status:
                filters['status'] = status
            
            offset = (page - 1) * per_page
            limit = per_page
            
            orders = get_data('order', filters=filters, order='created_at.desc', limit=limit, offset=offset)
            if not orders:
                orders = []
            
            # Get total count
            total = count_data('order', filters=filters)
            
            formatted_orders = []
            for order in orders:
                # Get order items
                order_items = get_data('order_item', filters={'order_id': order.get('id')})
                if not order_items:
                    order_items = []
                
                items = []
                for item in order_items:
                    product = get_data_by_id('product', item.get('product_id'))
                    items.append({
                        'id': item.get('id'),
                        'product_id': item.get('product_id'),
                        'product_name': product.get('name') if product else 'Unknown',
                        'product_image': url_for('static', filename=f'uploads/{product.get("image_filename")}') if product and product.get('image_filename') else None,
                        'quantity': item.get('quantity'),
                        'price': float(item.get('price', 0)),
                        'subtotal': float(item.get('quantity', 0) * item.get('price', 0))
                    })
                
                formatted_orders.append({
                    'id': order.get('id'),
                    'total_amount': float(order.get('total_amount', 0)),
                    'status': order.get('status'),
                    'payment_method': order.get('payment_method'),
                    'payment_status': order.get('payment_status'),
                    'delivery_address': order.get('delivery_address'),
                    'items': items,
                    'order_date': order.get('created_at'),
        'created_at': order.get('created_at'),
                    'updated_at': order.get('updated_at')
                })
            
            # Calculate pagination info
            total_pages = (total + per_page - 1) // per_page
            has_next = page < total_pages
            has_prev = page > 1
            
            return jsonify({
                'success': True,
                'orders': formatted_orders,
                'pagination': {
                    'page': page,
                    'pages': total_pages,
                    'per_page': per_page,
                    'total': total,
                    'has_next': has_next,
                    'has_prev': has_prev
                }
            })
        
        elif request.method == 'POST':
            # Create new order
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            items = data.get('items', [])
            delivery_address = data.get('delivery_address', '').strip()
            payment_method = data.get('payment_method', 'cod').strip()
            
            if not items:
                return jsonify({'error': 'Order must contain at least one item'}), 400
            if not delivery_address:
                return jsonify({'error': 'Delivery address is required'}), 400
            
            # Validate stock and calculate total
            total_amount = 0
            order_items_data = []
            
            for item_data in items:
                product_id = item_data.get('product_id')
                quantity = item_data.get('quantity', 1)
                
                if not product_id or quantity <= 0:
                    return jsonify({'error': 'Invalid item data'}), 400
                
                product = get_data_by_id('product', product_id)
                if not product or product.get('status') != 'approved':
                    return jsonify({'error': f'Product {product_id} not found'}), 404
                
                if product.get('stock', 0) < quantity:
                    return jsonify({'error': f'Insufficient stock for product {product.get("name")}'}, 400)
                
                subtotal = float(product.get('price', 0)) * quantity
                total_amount += subtotal
                
                order_items_data.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'price': float(product.get('price', 0))
                })
            
            # Create order
            order_data = {
                'buyer_id': request.current_user_id,
                'total_amount': total_amount,
                'delivery_address': delivery_address,
                'payment_method': payment_method,
                'status': 'pending',
                'payment_status': 'pending',
                'created_at': datetime.utcnow().isoformat()
            }
            
            new_order = insert_data('order', order_data)
            if not new_order:
                return jsonify({'error': 'Failed to create order'}), 500
            
            order_id = new_order.get('id')
            
            # Create order items and update stock
            seller_ids = set()
            for item_data in order_items_data:
                order_item_data = {
                    'order_id': order_id,
                    'product_id': item_data['product_id'],
                    'quantity': item_data['quantity'],
                    'price': item_data['price']
                }
                insert_data('order_item', order_item_data)
                
                # Update product stock
                product = get_data_by_id('product', item_data['product_id'])
                if product:
                    new_stock = product.get('stock', 0) - item_data['quantity']
                    update_data_by_id('product', item_data['product_id'], {'stock': new_stock})
                    # Collect seller IDs for notification
                    seller_ids.add(product.get('seller_id'))
            
            # Use Shopee-style notification for order placement
            try:
                # Get order object for Shopee notification
                order_obj = db.session.get(Order, order_id) if USE_LOCAL_ORM_FALLBACK else None
                if order_obj:
                    notify_order_placed(order_obj)
                else:
                    # Fallback to push_notification for Supabase
                    for seller_id in seller_ids:
                        push_notification(
                            seller_id,
                            f'New order #{order_id} received!',
                            type='order',
                            order_id=order_id
                        )
            except Exception as e:
                app.logger.error(f"Error sending Shopee-style notification: {e}")
                # Fallback to simple notification
                for seller_id in seller_ids:
                    try:
                        push_notification(
                            seller_id,
                            f'New order #{order_id} received!',
                            type='order',
                            order_id=order_id
                        )
                    except Exception:
                        pass
            
            return jsonify({
                'success': True,
                'order': {
                    'id': order_id,
                    'total_amount': total_amount,
                    'status': 'pending',
                    'payment_method': payment_method,
                    'delivery_address': delivery_address,
                    'created_at': new_order.get('created_at')
                }
            }), 201
            
    except Exception as e:
        app.logger.error(f"API v1 orders error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/orders/<int:order_id>', methods=['GET'])
@token_required
def api_v1_order_detail(order_id):
    """Get detailed order information (Supabase version)."""
    try:
        orders = get_data('order', filters={'id': order_id, 'buyer_id': request.current_user_id})
        if not orders or len(orders) == 0:
            return jsonify({'error': 'Order not found'}), 404
        
        order = orders[0]
        
        # Get order items
        order_items = get_data('order_item', filters={'order_id': order_id})
        if not order_items:
            order_items = []
        
        items = []
        for item in order_items:
            product = get_data_by_id('product', item.get('product_id'))
            items.append({
                'id': item.get('id'),
                'product_id': item.get('product_id'),
                'product_name': product.get('name') if product else 'Unknown',
                'product_description': product.get('description') if product else None,
                'product_image': url_for('static', filename=f'uploads/{product.get("image_filename")}') if product and product.get('image_filename') else None,
                'quantity': item.get('quantity'),
                'price': float(item.get('price', 0)),
                'subtotal': float(item.get('quantity', 0) * item.get('price', 0))
            })
        
        return jsonify({
            'success': True,
            'order': {
                'id': order.get('id'),
                'total_amount': float(order.get('total_amount', 0)),
                'status': order.get('status'),
                'payment_method': order.get('payment_method'),
                'payment_status': order.get('payment_status'),
                'delivery_address': order.get('delivery_address'),
                'items': items,
                'order_date': order.get('created_at'),
        'created_at': order.get('created_at'),
                'updated_at': order.get('updated_at')
            }
        })
        
    except Exception as e:
        app.logger.error(f"API v1 order detail error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# User Profile API Endpoints
@app.route('/api/v1/user/profile', methods=['GET', 'PUT'])
@token_required
def api_v1_user_profile():
    """Get or update user profile (Supabase version)."""
    try:
        user = get_data_by_id('user', request.current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'user': {
                    'id': user.get('id'),
                    'email': user.get('email'),
                    'first_name': user.get('first_name'),
                    'last_name': user.get('last_name'),
                    'phone': user.get('phone'),
                    'role': user.get('role'),
                    'profile_image': url_for('static', filename=f'uploads/{user.get("profile_image")}') if user.get('profile_image') else None,
                    'address': user.get('address'),
                    'status': user.get('status')
                }
            })
        
        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Update allowed fields
            update_data = {}
            if 'first_name' in data:
                update_data['first_name'] = data['first_name'].strip()
            if 'last_name' in data:
                update_data['last_name'] = data['last_name'].strip()
            if 'phone' in data:
                update_data['phone'] = data['phone'].strip()
            if 'address' in data:
                update_data['address'] = data['address'].strip()
            
            updated_user = update_data_by_id('user', request.current_user_id, update_data)
            if not updated_user:
                return jsonify({'error': 'Failed to update user'}), 500
            
            return jsonify({
                'success': True,
                'user': {
                    'id': updated_user.get('id'),
                    'email': updated_user.get('email'),
                    'first_name': updated_user.get('first_name'),
                    'last_name': updated_user.get('last_name'),
                    'phone': updated_user.get('phone'),
                    'role': updated_user.get('role'),
                    'address': updated_user.get('address')
                }
            })
            
    except Exception as e:
        app.logger.error(f"API v1 user profile error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Categories API Endpoint
@app.route('/api/v1/categories', methods=['GET'])
def api_v1_categories():
    """Get all categories with subcategories (Supabase version)."""
    try:
        categories = get_data('category', order='name')
        if not categories:
            categories = []
        
        result = []
        for category in categories:
            category_id = category.get('id')
            subcategories = get_data('subcategory', filters={'category_id': category_id}, order='name')
            if not subcategories:
                subcategories = []
            
            subcategory_list = []
            for subcat in subcategories:
                subcategory_list.append({
                    'id': subcat.get('id'),
                    'name': subcat.get('name')
                })
            
            result.append({
                'id': category.get('id'),
                'name': category.get('name'),
                'subcategories': subcategory_list
            })
        
        return jsonify({
            'success': True,
            'categories': result
        })
        
    except Exception as e:
        app.logger.error(f"API v1 categories error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Cart API Endpoints
@app.route('/api/v1/cart', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/api/v1/buyer/cart/add', methods=['POST'])
@token_required
def api_v1_cart():
    """Cart operations for mobile app using optimized SQL query."""
    try:
        if request.method == 'GET':
            from sqlalchemy.orm import joinedload

            # Use direct SQL query with eager loading instead of HTTP REST API
            cart_items = Cart.query.options(
                joinedload(Cart.product)
            ).filter_by(user_id=request.current_user_id).all()

            items = []
            total = 0

            for item in cart_items:
                if item.product and item.product.status in ['active', 'approved']:
                    price = float(item.product.price)
                    quantity = item.quantity
                    subtotal = price * quantity
                    total += subtotal

                    items.append({
                        'id': item.id,
                        'product_id': item.product_id,
                        'product_name': item.product.name,
                        'product_image': url_for('static', filename=f'uploads/{item.product.image_filename}') if item.product.image_filename else None,
                        'price': price,
                        'quantity': quantity,
                        'stock': item.product.stock,
                        'subtotal': float(subtotal)
                    })
            
            return jsonify({
                'success': True,
                'cart_items': items,
                'total_amount': float(total),
                'item_count': len(items)
            })
        
        elif request.method == 'POST':
            # Add item to cart
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            
            if not product_id or quantity <= 0:
                return jsonify({'error': 'Invalid product or quantity'}), 400
            
            product = get_data_by_id('product', product_id)
            if not product or product.get('status') != 'approved':
                return jsonify({'error': 'Product not found'}), 404
            
            if product.get('stock', 0) < quantity:
                return jsonify({'error': 'Insufficient stock'}), 400
            
            # Check if item already in cart
            existing_items = get_data('cart', filters={'user_id': request.current_user_id, 'product_id': product_id})
            
            cart_item_id = None
            new_quantity = quantity
            
            if existing_items and len(existing_items) > 0:
                # Update existing cart item
                cart_item = existing_items[0]
                cart_item_id = cart_item.get('id')
                new_quantity = cart_item.get('quantity', 0) + quantity
                update_data_by_id('cart', cart_item_id, {'quantity': new_quantity})
            else:
                # Create new cart item
                new_cart_item = insert_data('cart', {
                    'user_id': request.current_user_id,
                    'product_id': product_id,
                    'quantity': quantity
                })
                if new_cart_item:
                    cart_item_id = new_cart_item.get('id')
                    new_quantity = quantity
            
            # Return the cart item that was created/updated
            price = float(product.get('price', 0))
            subtotal = price * new_quantity
            cart_item_response = {
                'id': cart_item_id,
                'product_id': product_id,
                'product_name': product.get('name'),
                'product_image': url_for('static', filename=f'uploads/{product.get("image_filename")}') if product.get('image_filename') else None,
                'price': price,
                'quantity': new_quantity,
                'stock': product.get('stock', 0),
                'subtotal': float(subtotal)
            }
            
            return jsonify({'success': True, 'message': 'Item added to cart', 'cart_item': cart_item_response}), 201
        
        elif request.method == 'PUT':
            # Update cart item quantity
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            cart_item_id = data.get('cart_item_id')
            quantity = data.get('quantity', 1)
            
            if not cart_item_id or quantity <= 0:
                return jsonify({'error': 'Invalid cart item or quantity'}), 400
            
            cart_items = get_data('cart', filters={'id': cart_item_id, 'user_id': request.current_user_id})
            if not cart_items or len(cart_items) == 0:
                return jsonify({'error': 'Cart item not found'}), 404
            
            cart_item = cart_items[0]
            product_id = cart_item.get('product_id')
            
            product = get_data_by_id('product', product_id)
            if not product or product.get('stock', 0) < quantity:
                return jsonify({'error': 'Insufficient stock'}), 400
            
            updated_cart = update_data_by_id('cart', cart_item_id, {'quantity': quantity})
            
            # Return the updated cart item
            price = float(product.get('price', 0))
            subtotal = price * quantity
            cart_item_response = {
                'id': cart_item_id,
                'product_id': product_id,
                'product_name': product.get('name'),
                'product_image': url_for('static', filename=f'uploads/{product.get("image_filename")}') if product.get('image_filename') else None,
                'price': price,
                'quantity': quantity,
                'stock': product.get('stock', 0),
                'subtotal': float(subtotal)
            }
            
            return jsonify({'success': True, 'message': 'Cart updated', 'cart_item': cart_item_response})
        
        elif request.method == 'DELETE':
            # Remove item from cart
            cart_item_id = request.args.get('cart_item_id', type=int)
            
            if not cart_item_id:
                return jsonify({'error': 'Cart item ID required'}), 400
            
            cart_items = get_data('cart', filters={'id': cart_item_id, 'user_id': request.current_user_id})
            if not cart_items or len(cart_items) == 0:
                return jsonify({'error': 'Cart item not found'}), 404
            
            delete_data_by_id('cart', cart_item_id)
            
            return jsonify({'success': True, 'message': 'Item removed from cart'})
            
    except Exception as e:
        app.logger.error(f"API v1 cart error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Wishlist API Endpoints
@app.route('/api/v1/wishlist', methods=['GET', 'POST', 'DELETE'])
@token_required
def api_v1_wishlist():
    """Wishlist operations for mobile app (optimized with ORM)."""
    try:
        if request.method == 'GET':
            # Optimized: Single query with JOIN
            wishlist_items = db.session.query(Wishlist, Product).join(
                Product, Wishlist.product_id == Product.id
            ).filter(
                Wishlist.user_id == request.current_user_id,
                Product.status.in_(['active', 'approved'])
            ).all()
            
            items = []
            for wishlist, product in wishlist_items:
                items.append({
                    'id': wishlist.id,
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_image': url_for('static', filename=f'uploads/{product.image_filename}') if product.image_filename else None,
                    'price': float(product.price),
                    'stock': product.stock,
                    'added_at': wishlist.created_at.isoformat() if wishlist.created_at else None
                })
            
            return jsonify({
                'success': True,
                'wishlist_items': items
            })
        
        elif request.method == 'POST':
            # Add item to wishlist
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            product_id = data.get('product_id')
            if not product_id:
                return jsonify({'error': 'Product ID required'}), 400
            
            # Optimized: Single query to check product and existing wishlist
            product = db.session.get(Product, product_id)
            
            # Better error logging
            if not product:
                app.logger.warning(f"Wishlist add failed: Product {product_id} does not exist in database")
                return jsonify({'error': 'Product not found'}), 404
            
            # Accept both 'active' and 'approved' status
            if product.status not in ['active', 'approved']:
                app.logger.warning(f"Wishlist add failed: Product {product_id} has status '{product.status}' (not active/approved)")
                return jsonify({'error': f'Product is not available (status: {product.status})'}), 404
            
            # Check if already in wishlist
            existing = Wishlist.query.filter_by(
                user_id=request.current_user_id,
                product_id=product_id
            ).first()
            
            if existing:
                return jsonify({'success': True, 'message': 'Product already in wishlist'}), 200
            
            # Add to wishlist
            new_wishlist_item = Wishlist(
                user_id=request.current_user_id,
                product_id=product_id
            )
            db.session.add(new_wishlist_item)
            db.session.commit()
            
            app.logger.info(f"Added product {product_id} to wishlist for user {request.current_user_id}")
            return jsonify({'success': True, 'message': 'Added to wishlist'}), 201
        
        elif request.method == 'DELETE':
            # Remove item from wishlist
            product_id = request.args.get('product_id', type=int)
            
            if not product_id:
                return jsonify({'error': 'Product ID required'}), 400
            
            # Optimized: Direct delete
            wishlist_item = Wishlist.query.filter_by(
                user_id=request.current_user_id,
                product_id=product_id
            ).first()
            
            if not wishlist_item:
                return jsonify({'error': 'Item not found in wishlist'}), 404
            
            db.session.delete(wishlist_item)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Removed from wishlist'})
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"API v1 wishlist error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# MOBILE API v1 - Missing Order Endpoints
# ============================================================================

@app.route('/api/v1/health', methods=['GET'])
def api_v1_health():
    """Health check endpoint for mobile app (Supabase version)."""
    try:
        # Test Supabase connectivity
        test_data = get_data('user', filters={'id': 0}, limit=1)  # Simple test query
        return jsonify({
            'status': 'ok',
            'message': 'Server is running',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Server is not healthy',
            'timestamp': datetime.utcnow().isoformat()
        }), 503


@app.route('/api/v1/orders/user', methods=['GET'])
@token_required
@role_required('buyer')
def api_v1_orders_user():
    """Get orders for a buyer (mobile API v1) - OPTIMIZED (Supabase version)."""
    try:
        status = _normalize_status(request.args.get('status')) if request.args.get('status') else None
        filters = {'buyer_id': request.current_user_id}
        if status:
            filters['status'] = status
        
        # Get orders with limit
        orders = get_data('order', filters=filters, order='created_at.desc', limit=50)
        if not orders:
            return jsonify({'success': True, 'orders': []})
        
        # OPTIMIZATION: Batch fetch all related data
        order_ids = [o.get('id') for o in orders]
        
        # Fetch ALL order items in ONE query (instead of N queries)
        all_order_items = get_data('order_item', filters={'order_id': f"in.({','.join(map(str, order_ids))})"}) if order_ids else []
        
        # Group items by order_id and collect product IDs
        items_by_order = {}
        product_ids = set()
        for item in all_order_items:
            order_id = item.get('order_id')
            if order_id not in items_by_order:
                items_by_order[order_id] = []
            items_by_order[order_id].append(item)
            if item.get('product_id'):
                product_ids.add(item.get('product_id'))
        
        # Fetch ALL products in ONE query (instead of N queries)
        products_dict = {}
        if product_ids:
            products = get_data('product', filters={'id': f"in.({','.join(map(str, product_ids))})"}) or []
            products_dict = {p.get('id'): p for p in products}
        
        # Serialize all orders with pre-fetched data
        result = []
        for order in orders:
            order_id = order.get('id')
            order_items = items_by_order.get(order_id, [])
            
            items = []
            for item in order_items:
                product_id = item.get('product_id')
                product = products_dict.get(product_id)
                
                items.append({
                    'id': item.get('id'),
                    'product_id': product_id,
                    'product_name': product.get('name') if product else None,
                    'product_image': _safe_upload_url(product.get('image_filename')) if product else None,
                    'quantity': int(item.get('quantity') or 0),
                    'price': float(item.get('price_at_time') or 0),
                    'subtotal': float((item.get('quantity') or 0) * (item.get('price_at_time') or 0)),
                    'seller_id': product.get('seller_id') if product else None,
                })
            
            rider_id = order.get('rider_id') or order.get('picked_up_by') or order.get('delivered_by')
            
            result.append({
                'id': order.get('id'),
                'buyer_id': order.get('buyer_id'),
                'rider_id': rider_id,
                'status': order.get('status'),
                'total_amount': float(order.get('total_amount') or 0),
                'payment_method': order.get('payment_method'),
                'payment_status': order.get('payment_status'),
                'shipping_address': order.get('shipping_address'),
                'order_date': order.get('created_at'),
        'created_at': order.get('created_at'),
                'updated_at': order.get('updated_at'),
                'qr_code': order.get('qr_code'),
                'tracking_number': order.get('tracking_number'),
                'items': items,
            })
        
        return jsonify({'success': True, 'orders': result})
        
    except Exception as e:
        app.logger.error(f'/api/v1/orders/user error: {e}')
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/v1/orders/rider', methods=['GET'])
@token_required
@role_required('rider')
def api_v1_orders_rider():
    """Get orders for a rider (mobile API v1) (Supabase version)."""
    try:
        # Fetch all orders and filter client-side for OR conditions
        all_orders = get_data('order', order='created_at.desc', limit=1000)
        if not all_orders:
            all_orders = []
        
        orders = []
        current_user_id = request.current_user_id
        for order in all_orders:
            if (order.get('rider_id') == current_user_id or 
                order.get('picked_up_by') == current_user_id or 
                order.get('delivered_by') == current_user_id):
                orders.append(order)
        
        payload = []
        for order in orders:
            row = _serialize_order_api_dict(order)
            buyer_id = order.get('buyer_id')
            if buyer_id:
                buyer = get_data_by_id('user', buyer_id)
                row['customer'] = _serialize_user_api_dict(buyer) if buyer else None
            else:
                row['customer'] = None
            payload.append(row)
        return jsonify({'success': True, 'orders': payload})
    except Exception as e:
        app.logger.error(f'/api/v1/orders/rider error: {e}')
        return jsonify({'error': 'Internal server error'}), 500






@app.route('/api/v1/rider/orders/<int:order_id>/decline', methods=['POST'])
@token_required
@role_required('rider')
def api_rider_decline_order(order_id):
    """Rider declines a delivery order (mobile API)"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        order = get_data_by_id('order', order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check if rider is assigned
        if order.get('rider_id') != request.current_user_id:
            return jsonify({'error': 'Not authorized to decline this order'}), 403
        
        # Unassign rider and revert status
        update_data = {
            'rider_id': None,
            'status': 'ready_for_pickup',
            'delivery_notes': f"Declined by rider: {reason}",
            'updated_at': datetime.utcnow().isoformat()
        }
        
        success = update_data_by_id('order', order_id, update_data)
        
        if not success:
            return jsonify({'error': 'Failed to decline order'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Order declined successfully'
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error declining order: {e}")
        return jsonify({'error': 'Failed to decline order'}), 500






@app.route('/api/v1/rider/orders/<int:order_id>/mark-delivered', methods=['POST'])
@token_required
@role_required('rider')
def api_rider_mark_delivered(order_id):
    """Rider marks order as delivered (mobile API)"""
    try:
        order = get_data_by_id('order', order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if order.get('rider_id') != request.current_user_id:
            return jsonify({'error': 'Not authorized'}), 403
        
        if order.get('status') != 'in_transit':
            return jsonify({'error': 'Order must be in transit to mark as delivered'}), 400
        
        # Update order status to delivered
        update_result = update_data_by_id('order', order_id, {
            'status': 'delivered',
            'delivered_at': datetime.utcnow().isoformat(),
            'delivered_by': request.current_user_id,
            'updated_at': datetime.utcnow().isoformat()
        })
        if not update_result:
            return jsonify({'error': 'Failed to mark order as delivered'}), 500
        
# Notify buyer
        try:
            buyer_id = order.get('buyer_id')
            if buyer_id:
                push_notification(
                    buyer_id,
                    f'Your order #{order_id} has been delivered! Please confirm receipt.',
                    type='order',
                    link=f'/buyer/order/{order_id}',
                    order_id=order_id
                )
        except Exception as e:
            app.logger.error(f"Failed to notify buyer: {e}")
        
        # Notify seller(s)
        try:
            order_items = get_data('order_item', filters={'order_id': order_id})
            if order_items:
                seller_ids = set()
                for item in order_items:
                    product = get_data_by_id('product', item.get('product_id'))
                    if product and product.get('seller_id'):
                        seller_ids.add(product.get('seller_id'))
                
                for seller_id in seller_ids:
                    push_notification(
                        seller_id,
                        f'Order #{order_id} has been delivered to the buyer.',
                        type='order',
                        link=f'/seller/orders/{order_id}',
                        order_id=order_id
                    )
        except Exception as e:
            app.logger.error(f"Failed to notify sellers: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Order marked as delivered successfully',
            'order': {
                'id': order_id,
                'status': 'delivered'
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error marking order as delivered: {e}")
        return jsonify({'error': 'Failed to mark order as delivered'}), 500


@app.route('/api/v1/rider/available-orders', methods=['GET'])
@token_required
@role_required('rider')
def api_rider_available_orders():
    """Get available orders for rider (FCFS - orders not yet accepted)"""
    try:
        # Get orders that are ready for pickup and not yet assigned to a rider
        orders = db.session.query(Order).filter(
            Order.status.in_(['ready_for_pickup', 'to_ship', 'pending']),
            Order.rider_id.is_(None)
        ).all()
        
        orders_data = []
        for order in orders:
            # Get buyer info
            buyer = db.session.get(User, order.buyer_id)
            buyer_name = f"{buyer.first_name} {buyer.last_name}" if buyer else 'Unknown Buyer'
            buyer_phone = buyer.phone if buyer else ''
            buyer_email = buyer.email if buyer else ''
            
            # Get seller info from order items' products
            seller_names = set()
            seller_addresses = set()
            if hasattr(order, 'items') and order.items:
                for item in order.items:
                    if hasattr(item, 'product') and item.product:
                        if hasattr(item.product, 'seller_id') and item.product.seller_id:
                            seller = db.session.get(User, item.product.seller_id)
                            if seller:
                                seller_names.add(f"{seller.first_name} {seller.last_name}")
                                if seller.address:
                                    seller_addresses.add(seller.address)
            
            seller_name = ', '.join(seller_names) if seller_names else 'Unknown Seller'
            seller_address = ', '.join(seller_addresses) if seller_addresses else ''
            
            order_dict = {
                'id': order.id,
                'status': order.status,
                'total_amount': float(order.total_amount) if order.total_amount else 0,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'order_date': order.created_at.isoformat() if order.created_at else None,
                'buyer_id': order.buyer_id,
                'buyer_name': buyer_name,
                'buyer_phone': buyer_phone,
                'buyer_email': buyer_email,
                'seller_name': seller_name,
                'seller_address': seller_address,
                'shipping_address': order.shipping_address or '',
                'delivery_address': order.delivery_address or '',
                'recipient_name': order.recipient_name or '',
                'recipient_phone': order.recipient_phone or '',
                'payment_method': order.payment_method or 'cod',
                'payment_status': order.payment_status or 'pending',
            }
            
            # Calculate delivery fee from address
            address = order.shipping_address or order.delivery_address
            province = extract_province_from_address(address)
            delivery_fee = calculate_delivery_fee_from_address(address)
            app.logger.info(f"Order #{order.id}: Address='{address}' -> Province='{province}' -> Fee=₱{delivery_fee}")
            order_dict['delivery_fee'] = delivery_fee
            order_dict['items'] = []
        
            
            # Add order items if available
            if hasattr(order, 'items') and order.items:
                for item in order.items:
                    item_dict = {
                        'id': item.id if hasattr(item, 'id') else None,
                        'product_id': item.product_id if hasattr(item, 'product_id') else None,
                        'quantity': item.quantity if hasattr(item, 'quantity') else 1,
                        'price': float(item.price) if hasattr(item, 'price') and item.price else 0,
                    }
                    if hasattr(item, 'product') and item.product:
                        item_dict['product_name'] = item.product.name or ''
                        product_image = item.product.image_filename or ''
                        item_dict['product_image'] = f'/static/uploads/{product_image}' if product_image else ''
                    order_dict['items'].append(item_dict)
            
            orders_data.append(order_dict)
        
        return jsonify({
            'success': True,
            'orders': orders_data
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching available orders: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch available orders'
        }), 500


@app.route('/api/v1/rider/my-deliveries', methods=['GET'])
@token_required
@role_required('rider')
def api_rider_my_deliveries():
    """Get deliveries assigned to the current rider"""
    try:
        rider_id = request.current_user_id
        status_filter = request.args.get('status')
        
        query = db.session.query(Order).filter(Order.rider_id == rider_id)
        
        # Optional status filter
        if status_filter:
            query = query.filter(Order.status == status_filter)
        
        orders = query.all()
        
        orders_data = []
        for order in orders:
            # Get buyer info
            buyer = db.session.get(User, order.buyer_id)
            buyer_name = f"{buyer.first_name} {buyer.last_name}" if buyer else 'Unknown Buyer'
            buyer_phone = buyer.phone if buyer else ''
            buyer_email = buyer.email if buyer else ''
            
            # Get seller info from order items' products
            seller_names = set()
            seller_addresses = set()
            if hasattr(order, 'items') and order.items:
                for item in order.items:
                    if hasattr(item, 'product') and item.product:
                        if hasattr(item.product, 'seller_id') and item.product.seller_id:
                            seller = db.session.get(User, item.product.seller_id)
                            if seller:
                                seller_names.add(f"{seller.first_name} {seller.last_name}")
                                if seller.address:
                                    seller_addresses.add(seller.address)
            
            seller_name = ', '.join(seller_names) if seller_names else 'Unknown Seller'
            seller_address = ', '.join(seller_addresses) if seller_addresses else ''
            
            order_dict = {
                'id': order.id,
                'status': order.status,
                'total_amount': float(order.total_amount) if order.total_amount else 0,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'order_date': order.created_at.isoformat() if order.created_at else None,
                'buyer_id': order.buyer_id,
                'buyer_name': buyer_name,
                'buyer_phone': buyer_phone,
                'buyer_email': buyer_email,
                'seller_name': seller_name,
                'seller_address': seller_address,
                'shipping_address': order.shipping_address or '',
                'delivery_address': order.delivery_address or '',
                'recipient_name': order.recipient_name or '',
                'recipient_phone': order.recipient_phone or '',
                'payment_method': order.payment_method or 'cod',
                'payment_status': order.payment_status or 'pending',
                'rider_earnings': float(order.rider_earnings) if order.rider_earnings else 0,
                'items': []
            }
            
            # Add order items if available
            if hasattr(order, 'items') and order.items:
                for item in order.items:
                    item_dict = {
                        'id': item.id if hasattr(item, 'id') else None,
                        'product_id': item.product_id if hasattr(item, 'product_id') else None,
                        'quantity': item.quantity if hasattr(item, 'quantity') else 1,
                        'price': float(item.price) if hasattr(item, 'price') and item.price else 0,
                    }
                    if hasattr(item, 'product') and item.product:
                        item_dict['product_name'] = item.product.name or ''
                        product_image = item.product.image_filename or ''
                        item_dict['product_image'] = f'/static/uploads/{product_image}' if product_image else ''
                    order_dict['items'].append(item_dict)
            
            orders_data.append(order_dict)
        
        return jsonify({
            'success': True,
            'orders': orders_data
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching rider deliveries: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch deliveries'
        }), 500


@app.route('/api/v1/rider/orders/<int:order_id>/upload-proof', methods=['POST'])
@token_required
@role_required('rider')
def api_rider_upload_proof(order_id):
    """Upload delivery proof photo"""
    import os
    try:
        order = get_data_by_id('order', order_id)
        if not order:
            return jsonify({'error': 'Order not found', 'success': False}), 404

        if order.get('rider_id') != request.current_user_id:
            return jsonify({'error': 'Not authorized', 'success': False}), 403

        if 'proof_photo' not in request.files:
            return jsonify({'error': 'No file provided', 'success': False}), 400

        file = request.files['proof_photo']
        if file.filename == '':
            return jsonify({'error': 'No file selected', 'success': False}), 400

        # Save file
        filename = f"proof_{order_id}_{int(datetime.utcnow().timestamp())}.jpg"
        upload_folder = os.path.join('static', 'uploads', 'delivery_proofs')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Update order with proof photo URL
        photo_url = f"/static/uploads/delivery_proofs/{filename}"
        update_data_by_id('order', order_id, {
            'proof_photo_url': photo_url,
            'updated_at': datetime.utcnow().isoformat()
        })

        return jsonify({
            'success': True,
            'photo_url': photo_url
        }), 200

    except Exception as e:
        app.logger.error(f"Error uploading proof: {e}")
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/v1/rider/accept-order', methods=['POST'])
@token_required
@role_required('rider')
def api_rider_accept_order_endpoint():
    """Rider accepts an order (FCFS with row-level locking)"""
    try:
        data = request.get_json(silent=True) or {}
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({
                'success': False,
                'error': 'order_id is required'
            }), 400
        
        rider_id = request.current_user_id

        # Check if rider is active
        rider = db.session.get(User, rider_id)
        if not rider or rider.status != 'active':
            return jsonify({
                'success': False,
                'error': 'Your account is not active. Please contact support.'
            }), 403

        # Row-level locking for FCFS
        order = db.session.query(Order).filter(
            Order.id == order_id
        ).with_for_update().first()

        if not order:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404

        # FCFS Check
        if order.status != 'ready_for_pickup' and order.status != 'to_ship' and order.status != 'pending':
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Order already taken by another rider',
                'conflict': True
            }), 409

        if order.rider_id is not None:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Order already taken by another rider',
                'conflict': True
            }), 409

        # Calculate rider earnings (15% of order total)
        rider_earnings = float(order.delivery_fee if order.delivery_fee else 36.0)

        # Update order - skip pickup confirmation, go straight to in_transit
        order.status = 'in_transit'
        order.rider_id = rider_id
        order.picked_up_by = rider_id
        order.picked_up_at = datetime.utcnow()
        order.rider_earnings = rider_earnings
        order.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Order accepted successfully',
            'order': {
                'id': order.id,
                'status': order.status,
                'rider_earnings': rider_earnings
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error accepting order: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to accept order'
        }), 500


@app.route('/api/v1/rider/orders/<int:order_id>/accept', methods=['POST'])
@token_required
@role_required('rider')
def api_rider_accept_order(order_id):
    """Rider accepts an order (FCFS with row-level locking)"""
    try:
        rider_id = request.current_user_id

        # Check if rider is active (token_required already validates this, but keeping for safety)
        rider = db.session.get(User, rider_id)
        if not rider or rider.status != 'active':
            return jsonify({
                'success': False,
                'error': 'Your account is not active. Please contact support.'
            }), 403

        # Row-level locking for FCFS
        order = db.session.query(Order).filter(
            Order.id == order_id
        ).with_for_update().first()

        if not order:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404

        # FCFS Check
        if order.status != 'ready_for_pickup' and order.status != 'to_ship' and order.status != 'pending':
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Order already taken by another rider',
                'conflict': True
            }), 409

        if order.rider_id is not None:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Order already taken by another rider',
                'conflict': True
            }), 409

        # Calculate rider earnings (15% of order total)
        rider_earnings = float(order.delivery_fee if order.delivery_fee else 36.0)

        # Update order - skip pickup confirmation, go straight to in_transit
        order.status = 'in_transit'
        order.rider_id = rider_id
        order.picked_up_by = rider_id
        order.picked_up_at = datetime.utcnow()
        order.rider_earnings = rider_earnings
        order.updated_at = datetime.utcnow()

        db.session.commit()

        # Use Shopee-style notification for rider acceptance
        try:
            notify_order_accepted_by_rider(order)
        except Exception as e:
            app.logger.error(f"Failed to send Shopee-style notification: {e}")
            # Fallback to simple notification
            try:
                rider_name = f"{rider.first_name} {rider.last_name}".strip()
                
                # Notify buyer
                push_notification(
                    user_id=order.buyer_id,
                    message=f'Rider {rider_name} has been assigned to deliver your order #{order.id}.',
                    type='rider_assigned',
                    order_id=order.id
                )
                
                # Notify seller
                if order.items and order.items[0].product:
                    seller_id = order.items[0].product.seller_id
                    push_notification(
                        user_id=seller_id,
                        message=f'Rider {rider_name} has accepted order #{order.id}.',
                        type='rider_assigned',
                        order_id=order.id
                    )
            except Exception:
                pass

        return jsonify({
            'success': True,
            'message': 'Order accepted successfully',
            'order': {
                'id': order.id,
                'status': order.status,
                'rider_earnings': rider_earnings
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error accepting order: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to accept order'
        }), 500


@app.route('/api/v1/orders/status', methods=['PUT'])
@token_required
@role_required('seller', 'rider', 'admin')
def api_v1_update_order_status():
    """Update order status (mobile API v1) (Supabase version)."""
    try:
        data = request.get_json(silent=True) or {}
        order_id = data.get('order_id')
        new_status = _normalize_status(data.get('status'))
        rider_id = data.get('rider_id')
        if not order_id or not new_status:
            return jsonify({'error': 'order_id and a valid status are required'}), 400
        order = get_data_by_id('order', order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        actor_role = request.current_user_role
        if actor_role == 'seller':
            # Check if seller can manage this order
            order_items = get_data('order_item', filters={'order_id': order_id})
            if not order_items:
                order_items = []
            
            seller_can_manage = False
            for item in order_items:
                product = get_data_by_id('product', item.get('product_id'))
                if product and product.get('seller_id') == request.current_user_id:
                    seller_can_manage = True
                    break
            
            if not seller_can_manage:
                return jsonify({'error': 'Order is not associated with your products'}), 403
            if new_status not in ('processing', 'ready_for_pickup'):
                return jsonify({'error': 'Seller can only set Processing or Ready for Pickup'}), 403
        elif actor_role == 'rider':
            if new_status not in ('picked_up', 'out_for_delivery', 'delivered'):
                return jsonify({'error': 'Rider can only set Picked Up, Out for Delivery, or Delivered'}), 403
            assigned_rider_id = order.get('rider_id') or order.get('picked_up_by') or order.get('delivered_by')
            if assigned_rider_id and assigned_rider_id != request.current_user_id:
                return jsonify({'error': 'Order is assigned to another rider'}), 403
            if not assigned_rider_id:
                update_data_by_id('order', order_id, {'rider_id': request.current_user_id})
                order['rider_id'] = request.current_user_id
        else:
            if new_status not in ARCH_ORDER_STATUSES:
                return jsonify({'error': 'Invalid status'}), 400

        if rider_id is not None and actor_role in ('seller', 'admin'):
            try:
                rider_id = int(rider_id)
            except Exception:
                return jsonify({'error': 'rider_id must be numeric'}), 400
            rider = get_data('user', filters={'id': rider_id, 'role': 'rider', 'status': 'active'})
            if not rider or len(rider) == 0:
                return jsonify({'error': 'rider_id is invalid'}), 400
            update_data_by_id('order', order_id, {'rider_id': rider_id})
            order['rider_id'] = rider_id

        now = datetime.utcnow()
        update_fields = {'status': new_status, 'updated_at': now.isoformat()}
        
        if new_status == 'picked_up':
            picked_up_by = request.current_user_id if actor_role == 'rider' else (order.get('picked_up_by') or order.get('rider_id'))
            update_fields['picked_up_by'] = picked_up_by
            update_fields['picked_up_at'] = now.isoformat()
            if actor_role == 'rider' and not order.get('rider_id'):
                update_fields['rider_id'] = request.current_user_id
        elif new_status == 'delivered':
            delivered_by = request.current_user_id if actor_role == 'rider' else (order.get('delivered_by') or order.get('rider_id'))
            update_fields['delivered_by'] = delivered_by
            update_fields['delivered_at'] = now.isoformat()
            if actor_role == 'rider' and not order.get('rider_id'):
                update_fields['rider_id'] = request.current_user_id

        updated_order = update_data_by_id('order', order_id, update_fields)

        try:
            order_orm = db.session.get(Order, order_id)
            if order_orm:
                if new_status == 'completed':
                    _release_commissions(order_orm)
                elif new_status == 'refunded':
                    _release_rider_earning(order_orm)
        except Exception as e:
            app.logger.error(f'Failed to release earnings for order {order_id}: {e}')
        
        # Use Shopee-style notifications based on status changes
        try:
            # Get order object for Shopee notification
            order_obj = db.session.get(Order, order_id) if USE_LOCAL_ORM_FALLBACK else None
            
            if order_obj:
                if new_status == 'processing' and actor_role == 'seller':
                    notify_order_processing(order_obj)
                elif new_status == 'ready_for_pickup' and actor_role == 'seller':
                    notify_order_ready_for_pickup(order_obj)
                elif new_status == 'picked_up' and actor_role == 'rider':
                    notify_order_accepted_by_rider(order_obj)
                elif new_status == 'delivered' and actor_role == 'rider':
                    notify_order_delivered(order_obj)
            else:
                # Fallback to push_notification for Supabase
                order_data = updated_order if isinstance(updated_order, dict) else order
                buyer_id = order_data.get('buyer_id')
                
                if new_status == 'processing' and actor_role == 'seller':
                    push_notification(
                        user_id=buyer_id,
                        message=f'Your order #{order_id} is now being processed.',
                        type='order_processing',
                        order_id=order_id
                    )
                elif new_status == 'ready_for_pickup' and actor_role == 'seller':
                    push_notification(
                        user_id=buyer_id,
                        message=f'Your order #{order_id} is out for delivery.',
                        type='out_for_delivery',
                        order_id=order_id
                    )
                    # Broadcast to available riders
                    try:
                        available_riders = get_data('user', filters={'role': 'rider', 'status': 'active'})
                        if available_riders:
                            for rider in available_riders:
                                socketio.emit('order_available', {'order_id': order_id}, room=f'user_{rider.get("id")}')
                    except Exception as e:
                        app.logger.error(f"Error broadcasting to riders: {e}")
                elif new_status == 'delivered' and actor_role == 'rider':
                    push_notification(
                        user_id=buyer_id,
                        message=f'Your order #{order_id} has been delivered! Please confirm receipt.',
                        type='order_delivered',
                        order_id=order_id
                    )
        except Exception as e:
            app.logger.error(f"Failed to send Shopee-style notification: {e}")
        
        return jsonify({'success': True, 'order': _serialize_order_api_dict(updated_order)})
    except Exception as e:
        app.logger.error(f'/api/v1/orders/status error: {e}')
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/v1/rider/complete-delivery', methods=['POST'])
@token_required
@role_required('rider')
def api_rider_complete_delivery():
    """Mark order as delivered with proof photo"""
    try:
        data = request.get_json(silent=True) or {}
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({
                'success': False,
                'error': 'order_id is required'
            }), 400
        
        order = db.session.get(Order, order_id)
        if not order:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        # Verify rider is assigned to this order
        if order.rider_id != request.current_user_id:
            return jsonify({
                'success': False,
                'error': 'You are not assigned to this order'
            }), 403
        
        # Update order status to delivered
        now = datetime.utcnow()
        order.status = 'delivered'
        order.delivered_by = request.current_user_id
        order.delivered_at = now.isoformat()
        order.updated_at = now
        
        db.session.commit()
        
        
        # Send notifications to buyer and seller with proof photo
        try:
            buyer = db.session.get(User, order.buyer_id)
            proof_photo_url = order.proof_photo_url if hasattr(order, 'proof_photo_url') else None
            rider = db.session.get(User, request.current_user_id)
            rider_name = f"{rider.first_name} {rider.last_name}".strip() if rider else 'Rider'
            
            # Notify buyer
            push_notification(
                user_id=order.buyer_id,
                message=f"📦 Order #{order_id} delivered by {rider_name}",
                image_url=proof_photo_url,
                type='order_delivered',
                order_id=order_id,
                actor_user_id=request.current_user_id
            )
            
            # Notify sellers (get from order items)
            try:
                order_items = db.session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
                seller_ids = set()
                for item in order_items:
                    product = db.session.get(Product, item.product_id)
                    if product and product.seller_id:
                        seller_ids.add(product.seller_id)
                
                for seller_id in seller_ids:
                    if seller_id != request.current_user_id:  # Don't send to rider if they're also seller
                        push_notification(
                            user_id=seller_id,
                            message=f"📦 Order #{order_id} delivered to {buyer.first_name if buyer else 'customer'}",
                            image_url=proof_photo_url,
                            type='order_delivered',
                            order_id=order_id,
                            actor_user_id=request.current_user_id
                        )
            except Exception as e:
                app.logger.error(f"Error notifying sellers: {e}")
        
        except Exception as e:
            app.logger.error(f"Error sending delivery notifications: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Order marked as delivered',
            'order': {
                'id': order.id,
                'status': order.status,
                'delivered_at': order.delivered_at
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error completing delivery: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to mark order as delivered'
        }), 500


@socketio.on('join')
def on_join(data):
    # Handle both old format {room: 'user_123'} and new format {user_id: 123}
    if 'room' in data:
        room = data['room']
    elif 'user_id' in data:
        room = f"user_{data['user_id']}"
    else:
        return
    join_room(room)

@socketio.on('join_seller_room')
def on_join_seller_room(data):
    seller_id = data.get('seller_id')
    if seller_id:
        join_room(f'user_{seller_id}')

@socketio.on('join_chat')
def on_join_chat(data=None):
    user_id = None
    if isinstance(data, dict):
        user_id = data.get('user_id')
    if user_id:
        room = f'user_{user_id}'
        join_room(room)
        emit('joined_chat', {'room': room})
    else:
        emit('joined_chat', {'room': None})

@socketio.on('typing')
def on_typing(data):
    if not isinstance(data, dict):
        return
    receiver_id = data.get('receiver_id')
    sender_id = data.get('sender_id')
    if receiver_id and sender_id:
        emit('user_typing', {'sender_id': sender_id}, room=f'user_{receiver_id}')

@socketio.on('stop_typing')
def on_stop_typing(data):
    if not isinstance(data, dict):
        return
    receiver_id = data.get('receiver_id')
    sender_id = data.get('sender_id')
    if receiver_id and sender_id:
        emit('user_stop_typing', {'sender_id': sender_id}, room=f'user_{receiver_id}')

# Mobile App SocketIO Events for Real-time Features
@socketio.on('rider_location_update')
def on_rider_location_update(data):
    """Handle real-time location updates from mobile rider app"""
    try:
        rider_id = data.get('rider_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        order_id = data.get('order_id')
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        
        if not all([rider_id, latitude, longitude]):
            emit('error', {'message': 'Missing required location data'})
            return
        
        # Validate rider exists and is active
        rider = User.query.filter_by(id=rider_id, role='rider', status='active').first()
        if not rider:
            emit('error', {'message': 'Invalid rider'})
            return
        
        # Join rider's personal room for tracking
        join_room(f'rider_{rider_id}')
        
        # Broadcast location to relevant parties
        location_data = {
            'rider_id': rider_id,
            'rider_name': f"{rider.first_name} {rider.last_name}",
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': timestamp,
            'order_id': order_id
        }
        
        # Send to admin room for tracking
        emit('rider_location_update', location_data, room='admin_tracking')
        
        # Send to specific order's buyer if order_id provided
        if order_id:
            order = Order.query.filter_by(id=order_id).first()
            if order and order.buyer_id:
                emit('rider_location_update', location_data, room=f'user_{order.buyer_id}')
        
        # Send confirmation to rider
        emit('location_update_confirmed', {'status': 'success', 'timestamp': timestamp})
        
    except Exception as e:
        app.logger.error(f"Rider location update error: {e}")
        emit('error', {'message': 'Location update failed'})

@socketio.on('order_status_update')
def on_order_status_update(data):
    """Handle order status updates from mobile apps"""
    try:
        user_id = data.get('user_id')
        order_id = data.get('order_id')
        status = data.get('status')
        notes = data.get('notes', '')
        user_role = data.get('user_role')  # rider, seller, admin
        
        if not all([user_id, order_id, status, user_role]):
            emit('error', {'message': 'Missing required data'})
            return
        
        # Validate user
        user = User.query.filter_by(id=user_id, status='active').first()
        if not user:
            emit('error', {'message': 'Invalid user'})
            return
        
        # Get order
        order = Order.query.filter_by(id=order_id).first()
        if not order:
            emit('error', {'message': 'Order not found'})
            return
        
        # Validate permissions based on role
        if user_role == 'rider' and order.rider_id != user_id:
            emit('error', {'message': 'Unauthorized action'})
            return
        
        if user_role == 'seller' and order.items[0].product.seller_id != user_id:
            emit('error', {'message': 'Unauthorized action'})
            return
        
        # Update order status
        old_status = order.status
        order.status = status
        order.updated_at = datetime.utcnow()
        
        # Add status-specific logic
        if status == 'picked_up' and user_role == 'rider':
            order.picked_up_by = user_id
            order.picked_up_at = datetime.utcnow()
        elif status == 'delivered' and user_role == 'rider':
            order.delivered_by = user_id
            order.delivered_at = datetime.utcnow()
        
        db.session.commit()
        
        # Prepare status update data
        status_data = {
            'order_id': order_id,
            'old_status': old_status,
            'new_status': status,
            'updated_by': user_role,
            'updated_by_name': f"{user.first_name} {user.last_name}",
            'notes': notes,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast to relevant parties
        # Send to buyer
        emit('order_status_update', status_data, room=f'user_{order.buyer_id}')
        
        # Send to seller
        if order.items and order.items[0].product.seller_id:
            emit('order_status_update', status_data, room=f'user_{order.items[0].product.seller_id}')
        
        # Send to rider if assigned
        if order.rider_id:
            emit('order_status_update', status_data, room=f'user_{order.rider_id}')
        
        # Send to admin room
        emit('order_status_update', status_data, room='admin_tracking')
        
        # Send confirmation
        emit('status_update_confirmed', {'order_id': order_id, 'status': status})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Order status update error: {e}")
        emit('error', {'message': 'Status update failed'})

@socketio.on('join_tracking_room')
def on_join_tracking_room(data):
    """Join tracking rooms for mobile apps"""
    try:
        user_id = data.get('user_id')
        user_role = data.get('user_role')
        
        if not user_id or not user_role:
            emit('error', {'message': 'Missing user information'})
            return
        
        # Validate user
        user = User.query.filter_by(id=user_id, status='active').first()
        if not user:
            emit('error', {'message': 'Invalid user'})
            return
        
        # Join user's personal room
        join_room(f'user_{user_id}')
        
        # Join role-specific rooms
        if user_role == 'rider':
            join_room('riders')
            # Join rider-specific tracking room
            join_room(f'rider_{user_id}')
        elif user_role == 'admin':
            join_room('admin_tracking')
        elif user_role == 'seller':
            join_room('sellers')
        
        # Send confirmation
        emit('room_joined', {
            'user_id': user_id,
            'user_role': user_role,
            'rooms': [f'user_{user_id}', f'{user_role}s']
        })
        
    except Exception as e:
        app.logger.error(f"Join tracking room error: {e}")
        emit('error', {'message': 'Failed to join room'})

@socketio.on('mobile_chat_message')
def on_mobile_chat_message(data):
    """Handle chat messages from mobile apps"""
    try:
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        message = data.get('message')
        chat_type = data.get('chat_type')  # 'buyer_seller' or 'buyer_rider'
        order_id = data.get('order_id')
        
        if not all([sender_id, receiver_id, message, chat_type]):
            emit('error', {'message': 'Missing required chat data'})
            return
        
        # Validate sender
        sender = User.query.filter_by(id=sender_id, status='active').first()
        if not sender:
            emit('error', {'message': 'Invalid sender'})
            return
        
        # Validate receiver
        receiver = User.query.filter_by(id=receiver_id, status='active').first()
        if not receiver:
            emit('error', {'message': 'Invalid receiver'})
            return
        
        # Create chat message record
        if chat_type == 'buyer_seller':
            chat_msg = StoreChatMessage(
                buyer_id=sender_id if sender.role == 'buyer' else receiver_id,
                seller_id=sender_id if sender.role == 'seller' else receiver_id,
                message=message,
                order_id=order_id
            )
        elif chat_type == 'buyer_rider':
            chat_msg = RiderChatMessage(
                buyer_id=sender_id if sender.role == 'buyer' else receiver_id,
                rider_id=sender_id if sender.role == 'rider' else receiver_id,
                message=message,
                order_id=order_id
            )
        else:
            emit('error', {'message': 'Invalid chat type'})
            return
        
        db.session.add(chat_msg)
        db.session.commit()
        
        # Prepare message data
        message_data = {
            'id': chat_msg.id,
            'sender_id': sender_id,
            'sender_name': f"{sender.first_name} {sender.last_name}",
            'sender_role': sender.role,
            'receiver_id': receiver_id,
            'message': message,
            'chat_type': chat_type,
            'order_id': order_id,
            'timestamp': chat_msg.created_at.isoformat()
        }
        
        # Send to receiver
        emit('new_chat_message', message_data, room=f'user_{receiver_id}')
        
        # Send confirmation to sender
        emit('message_sent', {
            'message_id': chat_msg.id,
            'timestamp': chat_msg.created_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Mobile chat message error: {e}")
        emit('error', {'message': 'Failed to send message'})

@socketio.on('get_active_orders')
def on_get_active_orders(data):
    """Get active orders for mobile user"""
    try:
        user_id = data.get('user_id')
        user_role = data.get('user_role')
        
        if not user_id or not user_role:
            emit('error', {'message': 'Missing user information'})
            return
        
        # Validate user
        user = User.query.filter_by(id=user_id, status='active').first()
        if not user:
            emit('error', {'message': 'Invalid user'})
            return
        
        # Get active orders based on role
        if user_role == 'buyer':
            orders = Order.query.filter_by(
                buyer_id=user_id
            ).filter(
                Order.status.in_(['pending', 'confirmed', 'preparing', 'ready_for_pickup', 'picked_up', 'out_for_delivery'])
            ).all()
        elif user_role == 'rider':
            orders = Order.query.filter_by(
                rider_id=user_id
            ).filter(
                Order.status.in_(['ready_for_pickup', 'picked_up', 'out_for_delivery'])
            ).all()
        elif user_role == 'seller':
            # Get orders containing seller's products
            orders = db.session.query(Order).join(OrderItem).join(Product).filter(
                Product.seller_id == user_id,
                Order.status.in_(['pending', 'confirmed', 'preparing', 'ready_for_pickup'])
            ).distinct().all()
        else:
            emit('error', {'message': 'Invalid role'})
            return
        
        # Format orders
        active_orders = []
        for order in orders:
            order_data = {
                'id': order.id,
                'status': order.status,
                'total_amount': float(order.total_amount),
                'delivery_address': order.delivery_address,
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat() if order.updated_at else None
            }
            
            # Add role-specific information
            if user_role == 'buyer':
                order_data['items_count'] = len(order.items)
                if order.rider_id:
                    rider = db.session.get(User, order.rider_id)
                    order_data['rider'] = {
                        'id': rider.id,
                        'name': f"{rider.first_name} {rider.last_name}",
                        'phone': rider.phone
                    }
            elif user_role == 'rider':
                order_data['buyer'] = {
                    'id': order.buyer_id,
                    'name': f"{order.buyer.first_name} {order.buyer.last_name}",
                    'phone': order.buyer.phone
                }
                order_data['pickup_address'] = order.items[0].product.seller.address if order.items and order.items[0].product.seller else None
            elif user_role == 'seller':
                order_data['buyer'] = {
                    'id': order.buyer_id,
                    'name': f"{order.buyer.first_name} {order.buyer.last_name}"
                }
            
            active_orders.append(order_data)
        
        emit('active_orders', {
            'orders': active_orders,
            'count': len(active_orders)
        })
        
    except Exception as e:
        app.logger.error(f"Get active orders error: {e}")
        emit('error', {'message': 'Failed to get active orders'})


# ============= BUYER API ENDPOINTS FOR MOBILE APP =============

@app.route('/api/v1/buyer/cart', methods=['GET', 'POST'])
@token_required
def buyer_get_cart():
    """Get current buyer's cart items or add item to cart (Supabase version)."""
    try:
        if request.method == 'GET':
            # Get user's cart - return in same format as /api/v1/cart
            cart_items = get_data('cart', filters={'user_id': request.current_user_id})
            if not cart_items:
                cart_items = []
            
            items = []
            total = 0
            
            for item in cart_items:
                product = get_data_by_id('product', item.get('product_id'))
                if product and product.get('status') == 'approved':
                    price = float(product.get('price', 0))
                    quantity = item.get('quantity', 0)
                    subtotal = price * quantity
                    total += subtotal
                    
                    items.append({
                        'id': item.get('id'),
                        'product_id': item.get('product_id'),
                        'product_name': product.get('name'),
                        'product_image': url_for('static', filename=f'uploads/{product.get("image_filename")}') if product.get('image_filename') else None,
                        'price': price,
                        'quantity': quantity,
                        'stock': product.get('stock', 0),
                        'subtotal': float(subtotal)
                    })
            
            return jsonify(items)  # Return as array for compatibility
        
        elif request.method == 'POST':
            # Add item to cart
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            
            if not product_id or quantity <= 0:
                return jsonify({'error': 'Invalid product or quantity'}), 400
            
            product = get_data_by_id('product', product_id)
            if not product or product.get('status') != 'approved':
                return jsonify({'error': 'Product not found'}), 404
            
            if product.get('stock', 0) < quantity:
                return jsonify({'error': 'Insufficient stock'}), 400
            
            # Check if item already in cart
            existing_items = get_data('cart', filters={'user_id': request.current_user_id, 'product_id': product_id})
            
            cart_item_id = None
            new_quantity = quantity
            
            if existing_items and len(existing_items) > 0:
                # Update existing cart item
                cart_item = existing_items[0]
                cart_item_id = cart_item.get('id')
                new_quantity = cart_item.get('quantity', 0) + quantity
                update_data_by_id('cart', cart_item_id, {'quantity': new_quantity})
            else:
                # Create new cart item
                new_cart_item = insert_data('cart', {
                    'user_id': request.current_user_id,
                    'product_id': product_id,
                    'quantity': quantity
                })
                if new_cart_item:
                    cart_item_id = new_cart_item.get('id')
                    new_quantity = quantity
            
            # Return the cart item that was created/updated
            price = float(product.get('price', 0))
            subtotal = price * new_quantity
            cart_item_response = {
                'id': cart_item_id,
                'product_id': product_id,
                'product_name': product.get('name'),
                'product_image': url_for('static', filename=f'uploads/{product.get("image_filename")}') if product.get('image_filename') else None,
                'price': price,
                'quantity': new_quantity,
                'stock': product.get('stock', 0),
                'subtotal': float(subtotal)
            }
            
            return jsonify({'success': True, 'message': 'Item added to cart', 'cart_item': cart_item_response}), 201
    except Exception as e:
        app.logger.error(f'buyer_get_cart error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/v1/buyer/cart/<int:item_id>', methods=['PUT'])
@token_required
def buyer_update_cart_item(item_id):
    """Update cart item quantity (Supabase version)."""
    try:
        cart_items = get_data('cart', filters={'id': item_id, 'user_id': request.current_user_id})
        if not cart_items or len(cart_items) == 0:
            return jsonify({'success': False, 'error': 'Cart item not found'}), 404
        
        cart_item = cart_items[0]
        
        data = request.get_json(silent=True) or {}
        quantity = data.get('quantity', 1)
        
        try:
            quantity = int(quantity)
        except:
            return jsonify({'success': False, 'error': 'Invalid quantity'}), 400
        
        if quantity < 1:
            return jsonify({'success': False, 'error': 'Quantity must be >= 1'}), 400
        
        product = get_data_by_id('product', cart_item.get('product_id'))
        if not product or product.get('status') != 'approved':
            return jsonify({'success': False, 'error': 'Product not available'}), 404
        
        if product.get('stock', 0) < quantity:
            return jsonify({'success': False, 'error': f'Only {product.get("stock")} in stock'}), 400
        
        updated_cart = update_data_by_id('cart', item_id, {'quantity': quantity})
        
        price = float(product.get('price', 0))
        return jsonify({
            'success': True,
            'item': {
                'id': item_id,
                'product_id': product.get('id'),
                'quantity': quantity,
                'subtotal': float(quantity * price),
            }
        })
    except Exception as e:
        app.logger.error(f'buyer_update_cart_item error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/v1/buyer/cart/<int:item_id>', methods=['DELETE'])
@token_required
def buyer_remove_from_cart(item_id):
    """Remove item from cart (Supabase version)."""
    try:
        cart_items = get_data('cart', filters={'id': item_id, 'user_id': request.current_user_id})
        if not cart_items or len(cart_items) == 0:
            return jsonify({'success': False, 'error': 'Cart item not found'}), 404
        
        delete_data_by_id('cart', item_id)
        
        return jsonify({'success': True, 'message': 'Item removed from cart'})
    except Exception as e:
        app.logger.error(f'buyer_remove_from_cart error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/v1/buyer/cart/clear', methods=['POST'])
@token_required
def buyer_clear_cart():
    """Clear all items from cart (Supabase version)."""
    try:
        cart_items = get_data('cart', filters={'user_id': request.current_user_id})
        if cart_items:
            for item in cart_items:
                delete_data_by_id('cart', item.get('id'))
        
        return jsonify({'success': True, 'message': 'Cart cleared'})
    except Exception as e:
        app.logger.error(f'buyer_clear_cart error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/v1/buyer/checkout', methods=['POST'])
@token_required
@active_user_required
def api_buyer_checkout():
    """Create order from cart - synchronized with web checkout logic."""
    try:
        data = request.get_json(silent=True) or {}
        
        recipient_name = str(data.get('recipient_name', '')).strip()
        recipient_phone = str(data.get('recipient_phone', '')).strip()
        shipping_address = str(data.get('shipping_address', '')).strip()
        payment_method = str(data.get('payment_method', 'cod')).strip()
        notes = str(data.get('notes', '')).strip()
        selected_items = data.get('selected_items', [])
        product_quantities = data.get('product_quantities', {})  # product_id -> quantity mapping
        coupon_id = data.get('coupon_id')  # Optional coupon
        shipping_fee = float(data.get('shipping_fee', 10.0))  # Shipping fee
        delivery_fee = float(data.get('delivery_fee', 0.0))  # Delivery fee based on province
        
        if not recipient_name or not recipient_phone or not shipping_address:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        active_address = Address.query.filter_by(
            user_id=request.current_user_id,
            is_default=True
        ).first()
        if not active_address:
            return jsonify({
                'success': False,
                'error': 'Shipping Address Required: Please add a delivery address in your profile before proceeding to checkout.'
            }), 400

        # Get cart items or direct product purchases
        if selected_items:
            # Check if these are cart item IDs or product IDs
            all_cart_items = get_data('cart', filters={'user_id': request.current_user_id})
            cart_items = [item for item in all_cart_items if item.get('id') in selected_items]
            
            # If no cart items found, treat as direct product purchases
            if not cart_items:
                cart_items = []
                for product_id in selected_items:
                    product = get_data_by_id('product', product_id)
                    if product and product.get('status') in ['approved', 'active']:
                        quantity = product_quantities.get(str(product_id), product_quantities.get(product_id, 1))
                        cart_items.append({
                            'id': None,
                            'product_id': product_id,
                            'quantity': quantity,
                        })
        else:
            cart_items = get_data('cart', filters={'user_id': request.current_user_id})
        
        if not cart_items:
            local = LOCAL_CARTS.get(request.current_user_id, [])
            if local:
                cart_items = [{
                    'id': it.get('id'),
                    'product_id': it.get('product_id'),
                    'quantity': it.get('quantity')
                } for it in local]
            else:
                return jsonify({'success': False, 'error': 'No items to checkout'}), 400
        
        # Validate product status and available stock (matching web logic)
        for cart_item in cart_items:
            product = get_data_by_id('product', cart_item.get('product_id'))
            if not product:
                orm_product = db.session.get(Product, cart_item.get('product_id'))
                if orm_product:
                    product = {
                        'id': orm_product.id,
                        'name': orm_product.name,
                        'price': orm_product.price,
                        'stock': orm_product.stock,
                        'seller_id': orm_product.seller_id,
                        'status': orm_product.status,
                    }
            if not product or product.get('status') != 'approved':
                return jsonify({'success': False, 'error': f'Product not available'}), 400
            
            available_stock = get_available_stock(cart_item.get('product_id'))
            if cart_item.get('quantity', 0) > available_stock:
                return jsonify({'success': False, 'error': f'Insufficient stock. Only {available_stock} items available'}), 400
        
        # Calculate totals
        total = 0
        for cart_item in cart_items:
            product = get_data_by_id('product', cart_item.get('product_id'))
            if product:
                total += float(product.get('price', 0)) * cart_item.get('quantity', 0)
        
        # Handle coupon discount
        discount_amount = 0.0
        applied_coupon = None
        if coupon_id:
            coupon = db.session.get(Coupon, coupon_id)
            if coupon and coupon.is_active:
                applied_coupon = coupon
                if coupon.discount_type == 'percentage':
                    discount_amount = total * (coupon.discount_value / 100)
                else:
                    discount_amount = coupon.discount_value
                if discount_amount > total:
                    discount_amount = total
                if coupon.discount_type == 'free_shipping' or discount_amount >= total:
                    shipping_fee = 0.0
        
        grand_total = max(0.0, total - discount_amount + shipping_fee + delivery_fee)
        
        # Create order with status='pending' (matching web logic)
        new_order = Order(
            buyer_id=request.current_user_id,
            total_amount=grand_total,
            payment_method=payment_method,
            shipping_address=shipping_address,
            status='pending',
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            notes=notes,
            coupon_id=coupon_id,
            discount_amount=discount_amount,
            delivery_fee=delivery_fee,
        )
        db.session.add(new_order)
        db.session.flush()
        
        # Generate order fulfillment data (matching web logic)
        qr_code = generate_qr_code(new_order.id)
        tracking_number = generate_tracking_number()
        batch_code = generate_batch_code()
        
        new_order.qr_code = qr_code
        new_order.tracking_number = tracking_number
        new_order.batch_code = batch_code
        new_order.label_generated_at = datetime.utcnow()
        
        try:
            # Immediately deduct stock for each item with row-level locking and transaction rollback on failure
            for cart_item in cart_items:
                product_id = cart_item.get('product_id')
                quantity = cart_item.get('quantity')
                
                # Get product with row-level lock to prevent race conditions
                product = db.session.query(Product).filter_by(id=product_id).with_for_update().first()
                if not product:
                    db.session.rollback()
                    return jsonify({'success': False, 'error': 'Product not found'}), 400
                
                # Check available stock
                if product.stock < quantity:
                    db.session.rollback()
                    return jsonify({'success': False, 'error': f'Insufficient stock for {product.name}. Only {product.stock} available'}), 400
                
                # Immediately deduct stock
                product.stock = product.stock - quantity
                
                db.session.add(OrderItem(
                    order_id=new_order.id,
                    product_id=product_id,
                    quantity=quantity,
                    price_at_time=float(product.price)
                ))
            
            new_order.stock_deducted = True
            
            # Create OrderLabel entry (matching web logic)
            db.session.add(OrderLabel(
                order_id=new_order.id,
                qr_code=qr_code,
                tracking_number=tracking_number,
                batch_code=batch_code,
                label_data=create_order_label_data(new_order),
                status='generated'
            ))
            
            # Increment coupon usage if applied
            if applied_coupon:
                applied_coupon.used_count = (applied_coupon.used_count or 0) + 1
            
            # Clear cart items (matching web logic)
            for cart_item in cart_items:
                if cart_item.get('id'):
                    delete_data_by_id('cart', cart_item.get('id'))
            
            # Clear in-memory carts
            try:
                if request.current_user_id in LOCAL_CARTS:
                    LOCAL_CARTS.pop(request.current_user_id, None)
            except Exception:
                pass
            
            db.session.commit()
            
            # Create notification for buyer and sellers
            try:
                notify_order_placed(new_order)
                app.logger.info(f'Notification created for order {new_order.id}')
            except Exception as e:
                app.logger.error(f'Failed to create notification for order {new_order.id}: {e}')
            
            # Broadcast real-time stock updates to all connected clients
            for cart_item in cart_items:
                try:
                    product_id = cart_item.get('product_id')
                    broadcast_stock_update(product_id)
                    app.logger.info(f'Broadcasted stock update for product {product_id}')
                except Exception as e:
                    app.logger.error(f'Failed to broadcast stock update: {e}')
            
            # Build order response
            order_dict = {
                'id': new_order.id,
                'buyer_id': new_order.buyer_id,
                'total_amount': float(new_order.total_amount),
                'subtotal': total,
                'discount': discount_amount,
                'delivery_fee': delivery_fee,
                'shipping_fee': shipping_fee,
                'status': new_order.status,
                'payment_method': new_order.payment_method,
                'shipping_address': new_order.shipping_address,
                'recipient_name': new_order.recipient_name,
                'recipient_phone': new_order.recipient_phone,
                'created_at': new_order.created_at.isoformat() if new_order.created_at else None,
                'items': []
            }
            for item in new_order.items:
                product = get_data_by_id('product', item.product_id)
                order_dict['items'].append({
                    'product_id': item.product_id,
                    'product_name': product.get('name') if product else 'Unknown',
                    'quantity': item.quantity,
                    'price': float(item.price_at_time)
                })
            
            return jsonify({
                'success': True,
                'order': order_dict,
                'message': 'Order placed successfully'
            })
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Checkout transaction failed: {e}')
            return jsonify({'success': False, 'error': f'Checkout failed: {str(e)}'}), 500
    except Exception as e:
        app.logger.error(f'buyer_checkout error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/v1/buyer/orders', methods=['GET'])
@token_required
def buyer_get_orders():
    """Get all orders for current buyer (Supabase version)."""
    try:
        status = request.args.get('status')
        
        # DEBUG: Log the user_id being used
        print(f"=== BUYER GET ORDERS DEBUG ===")
        print(f"User ID: {request.current_user_id}")
        print(f"User Role: {request.current_user_role}")
        
        filters = {'buyer_id': request.current_user_id}
        if status:
            filters['status'] = status
        
        print(f"Filters: {filters}")
        
        orders = get_data('order', filters=filters, order='created_at.desc')
        
        print(f"Orders fetched: {len(orders) if orders else 0}")
        if orders:
            print(f"First order: {orders[0]}")
        
        if not orders:
            orders = []
        
        return jsonify({
            'success': True,
            'orders': [_serialize_order_api_dict(order) for order in orders],
        })
    except Exception as e:
        app.logger.error(f'buyer_get_orders error: {e}')
        print(f"ERROR in buyer_get_orders: {e}")
        import traceback


@app.route('/api/v1/buyer/orders/<int:order_id>', methods=['GET'])
@token_required
def buyer_get_order(order_id):
    """Get specific order details (Supabase version)."""
    try:
        orders = get_data('order', filters={'id': order_id, 'buyer_id': request.current_user_id})
        if not orders or len(orders) == 0:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        order = orders[0]
        return jsonify({
            'success': True,
            'order': _serialize_order_api_dict(order),
        })
    except Exception as e:
        app.logger.error(f'buyer_get_order error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/v1/buyer/orders/by-status', methods=['GET'])
@token_required
def buyer_get_orders_by_status():
    """Get orders grouped by status - matches web my_orders logic (Supabase version)."""
    try:
        # Fetch all orders for buyer
        all_orders = get_data('order', filters={'buyer_id': request.current_user_id}, order='created_at.desc')
        if not all_orders:
            all_orders = []
        
        # Groupings for tabs - matching web implementation
        to_pay = [o for o in all_orders if o.get('status') in ['pending', 'to_pay']]
        to_ship = [o for o in all_orders if o.get('status') in ['processing', 'ready_for_pickup']]
        to_receive = [o for o in all_orders if o.get('status') in ['to_ship', 'in_transit', 'delivered']]
        completed = [o for o in all_orders if o.get('status') == 'completed']
        returns = [o for o in all_orders if o.get('status') in ['return_requested', 'returned', 'refunded']]
        cancelled = [o for o in all_orders if o.get('status') == 'cancelled']
        
        return jsonify({
            'success': True,
            'to_pay': [_serialize_order_api_dict(order) for order in to_pay],
            'to_ship': [_serialize_order_api_dict(order) for order in to_ship],
            'to_receive': [_serialize_order_api_dict(order) for order in to_receive],
            'completed': [_serialize_order_api_dict(order) for order in completed],
            'returns': [_serialize_order_api_dict(order) for order in returns],
            'cancelled': [_serialize_order_api_dict(order) for order in cancelled],
            'counts': {
                'to_pay': len(to_pay),
                'to_ship': len(to_ship),
                'to_receive': len(to_receive),
                'completed': len(completed),
                'returns': len(returns),
                'cancelled': len(cancelled)
            }
        })
    except Exception as e:
        app.logger.error(f'buyer_get_orders_by_status error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/v1/buyer/orders/<int:order_id>/cancel', methods=['POST'])
@token_required
def buyer_cancel_order(order_id):
    """Cancel an order - for mobile app with Shopee-style stock restoration."""
    try:
        # Get order using ORM for proper relationship access
        order = db.session.query(Order).filter_by(id=order_id, buyer_id=request.current_user_id).first()
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        # Only allow cancellation for certain statuses
        if order.status not in ['pending', 'to_pay', 'processing']:
            return jsonify({'success': False, 'error': 'Order cannot be cancelled in current status'}), 400
        
        # SHOPEE RULE: Restore stock only if order was pending/to_pay/processing (not shipped/completed)
        if order.status in ['pending', 'to_pay', 'processing']:
            for item in order.items:
                product = db.session.get(Product, item.product_id)
                if product:
                    product.stock += item.quantity
            db.session.flush()
            for item in order.items:
                broadcast_stock_update(item.product_id)
            app.logger.info(f'Mobile: Order {order.id} cancelled: restored stock for {len(order.items)} product(s)')
        
        # Update order status
        order.status = 'cancelled'
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        
        return jsonify({'success': True, 'message': 'Order cancelled successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'buyer_cancel_order error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/v1/buyer/orders/<int:order_id>/confirm-delivery', methods=['POST'])
@token_required
def buyer_confirm_delivery(order_id):
    """Confirm order delivery - for mobile app (Supabase version)."""
    try:
        orders = get_data('order', filters={'id': order_id, 'buyer_id': request.current_user_id})
        if not orders or len(orders) == 0:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        order = orders[0]
        
        # Allow confirmation for both in_transit and delivered orders
        if order.get('status') not in ['in_transit', 'delivered']:
            return jsonify({'success': False, 'error': 'Order must be in transit or delivered before confirming'}), 400
        
        # Update order status to completed
        update_result = update_data_by_id('order', order_id, {
            'status': 'completed',
            'delivered_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        })
        
        if not update_result:
            return jsonify({'success': False, 'error': 'Failed to update order'}), 500
        
        # Release commissions to rider and seller
        try:
            # Get order with ORM for commission calculation
            order_orm = db.session.get(Order, order_id)
            if order_orm:
                _release_commissions(order_orm)
        except Exception as e:
            app.logger.error(f'Failed to release commissions for order {order_id}: {e}')
        
        # Notify buyer
        try:
            push_notification(
                request.current_user_id,
                f'Thank you! Order #{order_id} marked as received and completed.',
                type='order',
                link=f'/buyer/order/{order_id}',
                order_id=order_id
            )
        except Exception as e:
            app.logger.error(f'Failed to notify buyer: {e}')
        
        # Notify rider
        try:
            rider_id = (
                order.get('rider_id')
                or order.get('picked_up_by')
                or order.get('delivered_by')
            )
            if rider_id:
                push_notification(
                    rider_id,
                    f'Order #{order_id} completed! Your commission has been released.',
                    type='order',
                    link=f'/rider/orders/{order_id}',
                    order_id=order_id
                )
        except Exception as e:
            app.logger.error(f'Failed to notify rider: {e}')
        
        # Notify seller(s)
        try:
            order_items = get_data('order_item', filters={'order_id': order_id})
            if order_items:
                seller_ids = set()
                for item in order_items:
                    product = get_data_by_id('product', item.get('product_id'))
                    if product and product.get('seller_id'):
                        seller_ids.add(product.get('seller_id'))
                
                for seller_id in seller_ids:
                    push_notification(
                        seller_id,
                        f'Order #{order_id} completed by buyer! Your commission has been released.',
                        type='order',
                        link=f'/seller/orders/{order_id}',
                        order_id=order_id
                    )
        except Exception as e:
            app.logger.error(f'Failed to notify sellers: {e}')
        
        return jsonify({
            'success': True,
            'message': 'Order confirmed as received and completed. Commissions released.'
        })
    except Exception as e:
        app.logger.error(f'buyer_confirm_delivery error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400




@app.route('/api/v1/buyer/orders/<int:order_id>/rating', methods=['POST'])
@token_required
def buyer_submit_rating(order_id):
    """Submit order rating with optional media files - for mobile app."""
    try:
        # Verify order belongs to user
        orders = get_data('order', filters={'id': order_id, 'buyer_id': request.current_user_id})
        if not orders or len(orders) == 0:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        order = orders[0]
        
        # Get rating and comment from form data (multipart)
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({'success': False, 'error': 'Invalid rating (must be 1-5)'}), 400
        
        # Handle media files
        media_urls = []
        if request.files:
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'reviews')
            os.makedirs(upload_dir, exist_ok=True)
            
            for key in request.files:
                file = request.files[key]
                if file and file.filename:
                    # Save file
                    filename = secure_filename(f"{order_id}_{int(time.time())}_{file.filename}")
                    filepath = os.path.join(upload_dir, filename)
                    file.save(filepath)
                    
                    # Determine media type
                    ext = filename.lower().split('.')[-1]
                    media_type = 'video' if ext in ['mp4', 'mov', 'avi', 'webm'] else 'image'
                    media_urls.append({
                        'type': media_type,
                        'path': f'/static/uploads/reviews/{filename}'
                    })
        
        # Update order rating
        update_data_by_id('order', order_id, {
            'rating': rating,
            'review': comment,
            'review_media': json.dumps(media_urls) if media_urls else None
        })
        
        # Get buyer info
        buyer = get_data_by_id('user', request.current_user_id)
        buyer_name = f"{buyer.get('first_name', '')} {buyer.get('last_name', '')}".strip() or 'Anonymous'
        buyer_avatar = buyer.get('profile_image')
        
        # Extract category ratings from comment
        category_ratings = ''
        if comment and ('Product Quality:' in comment or 'Delivery Speed:' in comment):
            lines = comment.split('\n')
            rating_lines = [line for line in lines if any(cat in line for cat in ['Product Quality:', 'Delivery Speed:', 'Packaging:', 'Rider Service:'])]
            if rating_lines:
                category_ratings = ', '.join(rating_lines)
        
        # Create product reviews for each item in the order
        order_items = get_data('order_item', filters={'order_id': order_id})
        if order_items:
            for item in order_items:
                product_id = item.get('product_id')
                if not product_id:
                    continue
                
                # Create review - only use fields that exist in Review model
                review_data = {
                    'product_id': product_id,
                    'user_id': request.current_user_id,
                    'rating': rating,
                    'title': '',  # Empty title, comment goes in content
                    'content': comment,  # Full comment with tags and category ratings
                    'media': json.dumps(media_urls) if media_urls else None,
                    'verified_purchase': True,
                    'order_id': order_id,
                    'status': 'published'
                    # Don't set created_at - let model default handle it
                }
                
                result = insert_data('review', review_data)
                if not result:
                    app.logger.error(f'Failed to create review for product {product_id}')
                
                # Update product rating
                reviews = get_data('review', filters={'product_id': product_id})
                if reviews:
                    avg_rating = sum(r.get('rating', 0) for r in reviews) / len(reviews)
                    review_count = len(reviews)
                    
                    update_data_by_id('product', product_id, {
                        'rating': round(avg_rating, 1),
                        'review_count': review_count
                    })
        
        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully'
        })
        
    except Exception as e:
        app.logger.error(f'buyer_submit_rating error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/v1/buyer/addresses', methods=['GET'])
@token_required
def buyer_get_addresses():
    """Get all addresses for current buyer - for mobile app."""
    try:
        addresses = get_data('address', filters={'user_id': request.current_user_id})
        if not addresses:
            addresses = []
        
        return jsonify({
            'success': True,
            'addresses': addresses
        })
    except Exception as e:
        app.logger.error(f'Error fetching addresses: {e}')
        return jsonify({'success': False, 'message': 'Failed to fetch addresses'}), 500


@app.route('/api/v1/buyer/addresses', methods=['POST'])
@token_required
def buyer_add_address():
    """Add a new address for current buyer - for mobile app."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('label') or not data.get('full_address'):
            return jsonify({'success': False, 'message': 'Label and full address are required'}), 400
        
        # If this is set as default, unset other default addresses
        if data.get('is_default'):
            existing_addresses = get_data('address', filters={'user_id': request.current_user_id})
            for addr in existing_addresses:
                if addr.get('is_default'):
                    update_data('address', {'id': addr['id']}, {'is_default': False})
        
        # Create new address
        address_data = {
            'user_id': request.current_user_id,
            'label': data.get('label'),
            'full_address': data.get('full_address'),
            'street_address': data.get('street_address', ''),
            'city': data.get('city', ''),
            'province': data.get('province', ''),
            'region': data.get('region', ''),
            'barangay': data.get('barangay', ''),
            'zip_code': data.get('zip_code', ''),
            'is_default': bool(data.get('is_default', False)),
        }
        
        new_address = insert_data('address', address_data)
        
        if new_address:
            return jsonify({
                'success': True,
                'message': 'Address added successfully',
                'address': new_address
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to add address'}), 500
            
    except Exception as e:
        app.logger.error(f'Error adding address: {e}')
        return jsonify({'success': False, 'message': f'Error adding address: {str(e)}'}), 500


@app.route('/api/v1/buyer/addresses/<int:address_id>', methods=['DELETE'])
@token_required
def buyer_delete_address(address_id):
    """Delete an address for current buyer - for mobile app."""
    try:
        # Verify the address belongs to the current user
        address = get_data_by_id('address', address_id)
        
        if not address:
            return jsonify({'success': False, 'message': 'Address not found'}), 404
        
        if address.get('user_id') != request.current_user_id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Delete the address
        success = delete_data_by_id('address', address_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Address deleted successfully'
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to delete address'}), 500
            
    except Exception as e:
        app.logger.error(f'Error deleting address: {e}')
        return jsonify({'success': False, 'message': f'Error deleting address: {str(e)}'}), 500

@app.route('/api/v1/buyer/profile', methods=['GET', 'PUT'])
@token_required
def buyer_profile_api():
    """Get or update buyer profile - syncs to database"""
    try:
        user = db.session.get(User, request.current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        if request.method == 'GET':
            profile_image = get_user_avatar_url(user.id, user.role)
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone': user.phone,
                    'address': user.address,
                    'role': user.role,
                    'status': user.status,
                    'email_verified': user.email_verified,
                    'profile_image': profile_image,
                    'profile_picture': profile_image,
                }
            })
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'phone' in data:
                user.phone = data['phone']
            if 'address' in data:
                user.address = data['address']
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Sync to Supabase
            try:
                supabase.table('users').update({
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'address': user.address,
                    'updated_at': user.updated_at.isoformat()
                }).eq('id', user.id).execute()
            except Exception as e:
                app.logger.warning(f'Supabase sync failed: {e}')
            
            profile_image = get_user_avatar_url(user.id, user.role)
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone': user.phone,
                    'address': user.address,
                    'role': user.role,
                    'status': user.status,
                    'profile_image': profile_image,
                    'profile_picture': profile_image,
                }
            })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'buyer_profile error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/v1/user/profile/picture', methods=['POST'])
@app.route('/api/v1/buyer/profile/picture', methods=['POST'])
@app.route('/api/v1/rider/profile/picture', methods=['POST'])
@token_required
def api_upload_profile_picture():
    """Upload profile photo for buyer, rider, or seller (mobile + API clients)."""
    try:
        user = db.session.get(User, request.current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        avatar_file = (
            request.files.get('avatar')
            or request.files.get('profile_picture')
            or request.files.get('image')
        )
        if not avatar_file or not avatar_file.filename:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400

        image_url = _save_user_profile_avatar(user, avatar_file)
        db.session.refresh(user)
        app.logger.info(
            'Profile picture saved for user %s: %s',
            user.id,
            user.profile_picture,
        )
        return jsonify({
            'success': True,
            'message': 'Profile picture updated successfully',
            'image_url': image_url,
            'profile_image': image_url,
            'profile_picture': image_url,
            'user': _serialize_user_api(user),
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'api_upload_profile_picture error: {e}')
        return jsonify({'success': False, 'error': 'Failed to upload profile picture'}), 500
        
# Optimized endpoints disabled - routes already exist in app.py
# register_optimized_endpoints(app, db, {
#     'Order': Order,
#     'OrderItem': OrderItem,
#     'Product': Product,
#     'User': User,
#     'Cart': Cart,
#     'Category': Category,
#     'Notification': Notification
# })

# Register mobile rating endpoints
register_mobile_rating_endpoints(app, db, Order, Review, token_required)
app.extensions['return_refund_deps'] = {
    'db': db,
    'Order': Order,
    'OrderItem': OrderItem,
    'ReturnRequest': ReturnRequest,
    'Product': Product,
    'push_notification': push_notification,
    '_emit_return_update': _emit_return_update,
    'force_fix_sequence_for_table': force_fix_sequence_for_table,
    'release_commissions': _release_commissions,
    'release_rider_earning': _release_rider_earning,
    'finalize_rider_earning_after_return': _finalize_rider_earning_after_return,
}
register_return_refund_api(app, db, token_required)

# Register unified chat (must run after get_user_avatar_url is defined)
register_unified_chat_api(app, socketio, db, get_avatar_url=get_user_avatar_url, token_required=token_required)

# Ensure notification table has all required columns for Shopee-style notifications
ensure_notification_table_on_startup()

# Rider mobile API endpoints are already defined in app.py
# Do not import rider_mobile_only_api to avoid duplicate endpoint registration

# Favicon handler - prevent 500 errors on missing favicon
@app.route('/favicon.ico')
def favicon():
    """Serve favicon or return 204 No Content if not found"""
    favicon_path = os.path.join(app.static_folder, 'favicon.ico')
    if os.path.exists(favicon_path):
        return app.send_static_file('favicon.ico')
    # Return 204 No Content instead of 404 or 500
    return '', 204

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)



@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    user_id = session.get('user_id')
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return jsonify([{
        'id': n.id,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat()
    } for n in notifications])

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    user_id = session.get('user_id')
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404




# ═══════════════════════════════════════════════════════════════════════════
# FORGOT PASSWORD & RESET PASSWORD API ENDPOINTS (Mobile)
# ═══════════════════════════════════════════════════════════════════════════
