import sys
sys.path.insert(0, 'backend')
try:
    from app import app, db, Product
    with app.app_context():
        products = Product.query.filter_by(status='active').limit(3).all()
        print(f"Found {len(products)} products\n")
        for p in products:
            print(f"Product: {p.name}")
            print(f"  Main image: {p.image_filename}")
            print(f"  Gallery type: {type(p.gallery)}")
            print(f"  Gallery data: {p.gallery}")
            print()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
