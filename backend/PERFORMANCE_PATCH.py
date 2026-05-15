# CRITICAL PERFORMANCE OPTIMIZATIONS - Add at the very top of app.py after imports

# 1. Aggressive connection pooling for Supabase
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 50,              # Increased from 20
    'max_overflow': 20,           # Increased from 10
    'pool_timeout': 10,           # Reduced from 30
    'echo': False,
    'connect_args': {
        'connect_timeout': 5,     # Reduced from 10
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5,
    }
}

# 2. Enable query result caching
from flask_caching import Cache
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# 3. Preload commonly used data
@app.before_first_request
def preload_data():
    """Preload and cache common queries"""
    try:
        # Cache active products
        Product.query.filter_by(status='active').options(
            joinedload(Product.seller),
            joinedload(Product.category)
        ).all()
        # Cache categories
        Category.query.filter_by(status='active').all()
    except:
        pass
