import sys
sys.path.insert(0, r'C:\Users\mnban\Documents\kids\backend')

from app import app, Product, get_available_stock

with app.app_context():
    print("Testing get_available_stock function...\n")
    
    products = Product.query.filter_by(status='active').limit(5).all()
    
    for p in products:
        print(f"Product ID: {p.id} - {p.name}")
        print(f"  Stock in DB: {p.stock}")
        
        try:
            available = get_available_stock(p.id)
            print(f"  get_available_stock() returned: {available}")
            
            if available == 0 and p.stock > 0:
                print(f"  ERROR: Function returns 0 but DB has {p.stock}!")
        except Exception as e:
            print(f"  ERROR calling get_available_stock: {e}")
        
        print()
