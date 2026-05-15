# PASTE THIS INTO app.py - REPLACE EXISTING ROUTES

# ============================================================================
# OPTIMIZED HOMEPAGE - FAST LOADING WITH EAGER LOADING
# ============================================================================
@app.route('/')
def index():
    """Homepage - Optimized with eager loading to prevent N+1 queries"""
    from sqlalchemy.orm import joinedload
    
    # Single query with eager loading - loads products, sellers, and categories in ONE query
    products = Product.query.options(
        joinedload(Product.seller).joinedload(User.seller_applications),
        joinedload(Product.category)
    ).filter_by(status='active').order_by(Product.created_at.desc()).limit(24).all()
    
    # Get hero slides
    hero_slides = HeroSlide.query.filter_by(is_active=True).order_by(HeroSlide.created_at.asc()).limit(6).all()
    
    # Get categories
    categories = Category.query.filter_by(status='active').order_by(Category.name).all()
    
    return render_template('buyer_home.html',
        products=products,
        hero_slides=hero_slides,
        categories=categories
    )


# ============================================================================
# PRODUCT DETAIL PAGE - FIXED AND OPTIMIZED
# ============================================================================
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page with reviews and related products"""
    from sqlalchemy.orm import joinedload
    
    # Load product with all related data in one query
    product = Product.query.options(
        joinedload(Product.seller).joinedload(User.seller_applications),
        joinedload(Product.category),
        joinedload(Product.reviews).joinedload(Review.user)
    ).filter_by(id=product_id).first_or_404()
    
    # Get seller info
    seller = product.seller
    seller_app = seller.seller_applications[0] if seller and seller.seller_applications else None
    
    # Get related products (same category, exclude current)
    related_products = Product.query.options(
        joinedload(Product.seller),
        joinedload(Product.category)
    ).filter(
        Product.category_id == product.category_id,
        Product.id != product_id,
        Product.status == 'active'
    ).limit(4).all()
    
    # Calculate average rating
    reviews = product.reviews
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    
    # Check if user can review
    can_review = False
    if 'user_id' in session:
        can_review, _, _ = can_user_review_product(session['user_id'], product_id)
    
    return render_template('product_detail.html',
        product=product,
        seller=seller,
        seller_app=seller_app,
        related_products=related_products,
        reviews=reviews,
        avg_rating=avg_rating,
        can_review=can_review
    )


# ============================================================================
# SHOP PAGE - OPTIMIZED WITH EAGER LOADING
# ============================================================================
@app.route('/shop')
def shop():
    """Shop page with filtering and search - optimized"""
    from sqlalchemy.orm import joinedload
    
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '').strip()
    sort = request.args.get('sort', 'newest')
    
    # Base query with eager loading
    query = Product.query.options(
        joinedload(Product.seller).joinedload(User.seller_applications),
        joinedload(Product.category)
    ).filter_by(status='active')
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )
    
    # Apply sorting
    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort == 'name':
        query = query.order_by(Product.name.asc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())
    
    # Execute query
    products = query.all()
    
    # Get categories for filter
    categories = Category.query.filter_by(status='active').order_by(Category.name).all()
    
    return render_template('shop.html',
        products=products,
        categories=categories,
        selected_category=category_id,
        search_query=search,
        sort=sort
    )


# ============================================================================
# CATEGORY PAGE - OPTIMIZED
# ============================================================================
@app.route('/category/<int:category_id>')
def category_products(category_id):
    """Category page - optimized"""
    from sqlalchemy.orm import joinedload
    
    category = Category.query.get_or_404(category_id)
    
    products = Product.query.options(
        joinedload(Product.seller).joinedload(User.seller_applications),
        joinedload(Product.category)
    ).filter_by(
        category_id=category_id,
        status='active'
    ).order_by(Product.created_at.desc()).all()
    
    categories = Category.query.filter_by(status='active').order_by(Category.name).all()
    
    return render_template('shop.html',
        products=products,
        categories=categories,
        selected_category=category_id,
        current_category=category
    )
