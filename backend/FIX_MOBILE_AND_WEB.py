"""
Fix for mobile app and website issues:
1. Website add to cart checking 'approved' instead of 'active'
2. Mobile API /api/products and /api/categories endpoints
"""

import re

# Read the app.py file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Change 'approved' to 'active' in add_to_cart
content = content.replace(
    "if product.status != 'approved':",
    "if product.status != 'active':"
)

# Fix 2: Add /api/categories endpoint if missing
if "@app.route('/api/categories')" not in content:
    # Find where to insert (after /api/products endpoint)
    insert_pos = content.find("@app.route('/api/products/<int:product_id>', methods=['PUT'])")
    if insert_pos > 0:
        categories_endpoint = '''
@app.route('/api/categories', methods=['GET'])
def api_categories():
    """Get all active categories with subcategories (Supabase version)."""
    try:
        categories = get_data('category', filters={'status': 'active'}, order='name.asc')
        if not categories:
            return jsonify([])
        
        result = []
        for category in categories:
            subcategories = get_data('subcategory', filters={'category_id': category.get('id'), 'status': 'active'}, order='name.asc')
            result.append({
                'id': category.get('id'),
                'name': category.get('name'),
                'description': category.get('description'),
                'cover_image': _safe_upload_url(category.get('cover_image_filename')) if category.get('cover_image_filename') else None,
                'subcategories': [
                    {
                        'id': sub.get('id'),
                        'name': sub.get('name'),
                        'description': sub.get('description')
                    } for sub in (subcategories or [])
                ]
            })
        
        return jsonify(result)
    except Exception as e:
        app.logger.error(f'/api/categories error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

'''
        content = content[:insert_pos] + categories_endpoint + content[insert_pos:]

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed:")
print("1. Changed add_to_cart to check for 'active' status")
print("2. Added /api/categories endpoint for mobile app")
print("")
print("Please restart the Flask server")
