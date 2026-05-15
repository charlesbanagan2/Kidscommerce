filepath = r'C:\Users\mnban\Documents\kids\backend\app.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if route exists
if "@app.route('/product/<int:product_id>')" in content:
    print("Route exists")
    
    # Check for required variables in the route
    start = content.find("@app.route('/product/<int:product_id>')")
    end = content.find("\n@app.route", start + 100)
    if end == -1:
        end = content.find("\nif __name__", start)
    
    route_code = content[start:end]
    
    required = ['available_stock', 'media_items', 'avg_rating', 'reviews']
    missing = []
    
    for var in required:
        if var not in route_code:
            missing.append(var)
    
    if missing:
        print(f"MISSING variables: {missing}")
        print("\nRoute needs to be fixed!")
    else:
        print("All required variables present:")
        for var in required:
            print(f"  - {var}")
        print("\nRoute is COMPLETE! Restart Flask server now.")
else:
    print("ERROR: Route not found!")
