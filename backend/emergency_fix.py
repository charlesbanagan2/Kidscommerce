"""
EMERGENCY FIX - Restore Homepage and Fix Performance Issues
Run this immediately to fix the broken homepage
"""

import re

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_homepage(content):
    """Fix the broken homepage - restore full Product objects"""
    print("🔧 Fixing homepage route...")
    
    # Find and replace the broken index route
    old_pattern = r'''@app\.route\('/'\)\s+def index\(\):.*?return render_template\('buyer_home\.html',\s+products=featured_products,\s+hero_slides=hero_slides,\s+categories=categories\)'''
    
    new_route = '''@app.route('/')
def index():
    """
    Homepage showing all approved products with hero slides.
    Optimized with eager loading to prevent N+1 queries.
    """
    from sqlalchemy.orm import joinedload
    
    # Get all active products with eager loading - ONE query instead of many
    products = Product.query.options(
        joinedload(Product.seller),
        joinedload(Product.category)
    ).filter_by(status='active').order_by(Product.created_at.desc()).limit(24).all()
    
    # Get hero slides for homepage banner
    hero_slides = HeroSlide.query.filter_by(is_active=True).order_by(HeroSlide.created_at.asc()).limit(6).all()
    
    # Get unique categories
    all_categories = Category.query.filter_by(status='active').order_by(Category.name).all()
    seen_names = set()
    categories = []
    for cat in all_categories:
        if cat.name not in seen_names:
            seen_names.add(cat.name)
            categories.append(cat)
    
    return render_template('buyer_home.html',
        products=products,
        hero_slides=hero_slides,
        categories=categories
    )'''
    
    if re.search(old_pattern, content, re.DOTALL):
        content = re.sub(old_pattern, new_route, content, flags=re.DOTALL)
        print("   ✅ Fixed homepage route")
    else:
        print("   ⚠️  Could not find exact pattern, trying alternative...")
        # Try to find just the function definition
        alt_pattern = r'@app\.route\(\'/\'\)\s+def index\(\):[^@]+'
        if re.search(alt_pattern, content, re.DOTALL):
            # Find the end of the function (next @app.route or next def at same level)
            content = re.sub(
                r'(@app\.route\(\'/\'\)\s+def index\(\):).*?(?=\n@app\.route|\nclass |\ndef [a-z_]+\(\):)',
                r'\1\n' + new_route.split('def index():')[1] + '\n\n',
                content,
                flags=re.DOTALL
            )
            print("   ✅ Fixed homepage route (alternative method)")
    
    return content

def main():
    print("=" * 70)
    print("🚨 EMERGENCY FIX - Restoring Homepage")
    print("=" * 70)
    print()
    
    app_file = 'app.py'
    
    print("📖 Reading app.py...")
    content = read_file(app_file)
    
    print("🔧 Applying emergency fix...")
    content = fix_homepage(content)
    
    print("💾 Writing fixed file...")
    write_file(app_file, content)
    
    print()
    print("=" * 70)
    print("✅ EMERGENCY FIX COMPLETE!")
    print("=" * 70)
    print()
    print("🔄 Next Steps:")
    print("   1. Restart your Flask server")
    print("   2. Test the homepage - products should now appear")
    print("   3. Check terminal for [SLOW] messages")
    print()

if __name__ == '__main__':
    main()
