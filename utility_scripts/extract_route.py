with open(r'C:\Users\mnban\Documents\kids\backend\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the function
start = content.find("@app.route('/product/<int:product_id>')")
if start == -1:
    print("Route not found!")
else:
    # Find the end (next @app.route or if __name__)
    end = content.find("\n@app.route", start + 50)
    if end == -1:
        end = content.find("\nif __name__", start)
    if end == -1:
        end = len(content)
    
    function_code = content[start:end]
    
    with open(r'C:\Users\mnban\Documents\kids\current_product_detail.txt', 'w', encoding='utf-8') as f:
        f.write(function_code)
    
    print(function_code)
    print(f"\n\nSaved to current_product_detail.txt ({len(function_code)} chars)")
