filepath = r'C:\Users\mnban\Documents\kids\backend\app.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find product_detail function
start = content.find("@app.route('/product/<int:product_id>')")
if start == -1:
    print("Route not found!")
    exit(1)

# Find the return render_template line
render_pos = content.find("return render_template('product_detail.html',", start)
if render_pos == -1:
    print("render_template not found!")
    exit(1)

# Find the closing parenthesis of render_template
paren_count = 1
i = render_pos + len("return render_template('product_detail.html',")
while i < len(content) and paren_count > 0:
    if content[i] == '(':
        paren_count += 1
    elif content[i] == ')':
        paren_count -= 1
    i += 1

# Extract current parameters
param_start = render_pos + len("return render_template('product_detail.html',")
param_end = i - 1
current_params = content[param_start:param_end]

# Check what's missing
missing = []
if 'available_stock' not in current_params:
    missing.append('available_stock')
if 'media_items' not in current_params:
    missing.append('media_items')

if not missing:
    print("All required variables already present")
else:
    print(f"Adding missing variables: {missing}")
    
    # Build new parameters
    new_params = current_params.rstrip().rstrip(',')
    
    if 'available_stock' in missing:
        new_params += ',\n                         available_stock=get_available_stock(product.id)'
    
    if 'media_items' in missing:
        new_params += ',\n                         media_items=[]'
    
    # Replace in content
    new_content = content[:param_start] + new_params + content[param_end:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("DONE! Missing variables added")
    print("Restart Flask server now")
