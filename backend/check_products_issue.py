"""
Diagnostic script to check why products aren't showing on homepage
"""
from app import app, db, Product, User, Category

with app.app_context():
    print("=" * 60)
    print("PRODUCT DATABASE DIAGNOSTIC")
    print("=" * 60)
    
    # Check total products
    total_products = Product.query.count()
    print(f"\n1. Total products in database: {total_products}")
    
    # Check products by status
    print("\n2. Products by status:")
    for status in ['pending', 'approved', 'rejected', 'active']:
        count = Product.query.filter_by(status=status).count()
        if count > 0:
            print(f"   - {status}: {count}")
    
    # Check approved products
    approved_products = Product.query.filter_by(status='approved').all()
    print(f"\n3. Approved products: {len(approved_products)}")
    
    if approved_products:
        print("\n4. Sample approved products:")
        for p in approved_products[:5]:
            print(f"   - ID: {p.id}, Name: {p.name}, Stock: {p.stock}, Status: {p.status}")
    else:
        print("\n4. No approved products found!")
        
        # Check if there are ANY products
        all_products = Product.query.limit(10).all()
        if all_products:
            print("\n5. Sample products (any status):")
            for p in all_products:
                print(f"   - ID: {p.id}, Name: {p.name}, Stock: {p.stock}, Status: {p.status}")
        else:
            print("\n5. Database is completely empty - no products at all!")
    
    # Check sellers
    sellers = User.query.filter_by(role='seller').count()
    print(f"\n6. Total sellers: {sellers}")
    
    # Check categories
    categories = Category.query.count()
    print(f"\n7. Total categories: {categories}")
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS COMPLETE")
    print("=" * 60)
    
    # Provide recommendations
    print("\nRECOMMENDATIONS:")
    if total_products == 0:
        print("❌ No products in database. You need to:")
        print("   1. Login as a seller")
        print("   2. Add products via seller dashboard")
        print("   3. Admin must approve the products")
    elif len(approved_products) == 0:
        print("❌ Products exist but none are approved. You need to:")
        print("   1. Login as admin")
        print("   2. Go to Products section")
        print("   3. Approve pending products")
    else:
        print("✅ Products are approved and should be visible!")
        print("   If they're not showing, check:")
        print("   1. Browser cache (Ctrl+Shift+R)")
        print("   2. Flask server is running")
        print("   3. Template rendering correctly")
