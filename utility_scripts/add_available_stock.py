filepath = r'C:\Users\mnban\Documents\kids\backend\app.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the return render_template line in product_detail
search_str = "return render_template('product_detail.html',"
pos = content.find(search_str)

if pos == -1:
    print("Could not find render_template for product_detail")
else:
    # Find the closing parenthesis
    paren_count = 0
    start = pos + len("return render_template(")
    i = start
    while i < len(content):
        if content[i] == '(':
            paren_count += 1
        elif content[i] == ')':
            if paren_count == 0:
                break
            paren_count -= 1
        i += 1
    
    # Extract current parameters
    current_params = content[start:i]
    
    # Check if available_stock already exists
    if 'available_stock' in current_params:
        print("available_stock already in template parameters")
    else:
        print("Adding available_stock to template parameters")
        
        # Add available_stock before the closing paren
        new_params = current_params.rstrip().rstrip(',') + ',\n                         available_stock=get_available_stock(product.id)'
        
        new_content = content[:start] + new_params + content[i:]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("DONE! available_stock added to product_detail route")
