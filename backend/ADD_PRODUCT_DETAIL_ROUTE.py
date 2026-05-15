# ADD THIS ROUTE AFTER THE index() ROUTE IN app.py
# Search for the index() route and add this right after it

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page - optimized with eager loading"""
    from sqlalchemy.orm import joinedload
    
    # Load product with all related data in ONE query
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
        joinedload(Product.seller).joinedload(User.seller_applications),
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
    
    # Check if in wishlist
    in_wishlist = False
    if 'user_id' in session:
        in_wishlist = Wishlist.query.filter_by(
            user_id=session['user_id'],
            product_id=product_id
        ).first() is not None
    
    return render_template('product_detail.html',
        product=product,
        seller=seller,
        seller_app=seller_app,
        related_products=related_products,
        reviews=reviews,
        avg_rating=avg_rating,
        can_review=can_review,
        in_wishlist=in_wishlist
    )
