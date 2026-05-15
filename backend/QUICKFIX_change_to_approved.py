"""
QUICKEST FIX: Change all 'active' products to 'approved' status
This makes them visible to buyers without changing any code
"""
from app import app, db, Product

with app.app_context():
    # Find all active products
    active_products = Product.query.filter_by(status='active').all()
    
    if not active_products:
        print("No products with 'active' status found.")
        
        # Show current status distribution
        all_products = Product.query.all()
        if all_products:
            statuses = {}
            for p in all_products:
                statuses[p.status] = statuses.get(p.status, 0) + 1
            print(f"\nCurrent product status distribution:")
            for status, count in statuses.items():
                print(f"  {status}: {count}")
    else:
        print(f"Found {len(active_products)} products with 'active' status.")
        print("Changing to 'approved' status...\n")
        
        for product in active_products:
            product.status = 'approved'
            print(f"  ✓ {product.name} -> approved")
        
        db.session.commit()
        print(f"\n✅ Successfully changed {len(active_products)} products to 'approved' status!")
        print("✅ Products are now visible to buyers on the homepage!")
        print("\nRefresh your browser (Ctrl+Shift+R) to see them.")
