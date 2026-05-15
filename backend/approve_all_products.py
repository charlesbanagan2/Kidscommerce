"""
Quick fix: Approve all pending products
Run this if you have products but they're all pending approval
"""
from app import app, db, Product

with app.app_context():
    # Find all pending products
    pending_products = Product.query.filter_by(status='pending').all()
    
    if not pending_products:
        print("No pending products found.")
        
        # Check for other statuses
        all_products = Product.query.all()
        if all_products:
            print(f"\nFound {len(all_products)} products with these statuses:")
            for p in all_products[:10]:
                print(f"  - {p.name}: {p.status}")
        else:
            print("\nNo products in database at all!")
    else:
        print(f"Found {len(pending_products)} pending products. Approving...")
        
        for product in pending_products:
            product.status = 'approved'
            print(f"  ✓ Approved: {product.name}")
        
        db.session.commit()
        print(f"\n✅ Successfully approved {len(pending_products)} products!")
        print("Refresh your homepage to see them.")
