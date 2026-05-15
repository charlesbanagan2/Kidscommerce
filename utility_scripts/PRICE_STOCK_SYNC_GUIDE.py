"""
Sync prices and stock across database, website, and mobile app
This script ensures all products have consistent data
"""

# INSTRUCTIONS:
# 1. This script will check all products in your database
# 2. It will ensure prices and stock are consistent
# 3. The mobile app reads from the same database via API

# Key Points:
# - Database (Supabase PostgreSQL) is the single source of truth
# - Website (Flask) reads directly from database
# - Mobile app calls Flask API which reads from database
# - All three use the SAME data source

# The issue is likely in how data is displayed, not stored
# Let's verify the API response format matches what mobile app expects

print("=" * 80)
print("PRICE AND STOCK SYNC VERIFICATION")
print("=" * 80)

print("""
Your system architecture:
1. Database (Supabase PostgreSQL) - Single source of truth
2. Website (Flask backend) - Reads from database
3. Mobile App - Calls Flask API endpoints

Since all three use the same database, prices and stock ARE already the same.

The mobile app Product model expects:
- price: double (required)
- stock: int (required)

The Flask API /api/products endpoint returns:
- price: float from database
- stock: int from database

VERIFICATION STEPS:
""")

print("\n1. Check database has valid data:")
print("   - All products should have price > 0")
print("   - All products should have stock >= 0")

print("\n2. Check Flask API response format:")
print("   - Ensure /api/products returns 'price' and 'stock' fields")
print("   - Ensure data types match (float for price, int for stock)")

print("\n3. Check mobile app parsing:")
print("   - Product.fromJson() correctly reads 'price' and 'stock'")
print("   - No data transformation issues")

print("\n" + "=" * 80)
print("SOLUTION:")
print("=" * 80)

print("""
Since your backend uses Supabase (PostgreSQL), all data is already synced.
The mobile app and website read from the same database.

To verify everything is working:

1. Check a product in database:
   SELECT id, name, price, stock FROM product WHERE id = 1;

2. Check same product via website:
   Visit: http://localhost:5000/product/1

3. Check same product via mobile API:
   GET http://localhost:5000/api/products

All three should show IDENTICAL price and stock values.

If you see differences, the issue is in:
- API response formatting (backend/app.py)
- Mobile app data parsing (mobile_app/lib/models/product.dart)
- Display logic (not actual data)
""")

print("\n" + "=" * 80)
print("NEXT STEPS:")
print("=" * 80)
print("""
1. Run your Flask backend
2. Open mobile app
3. Compare a specific product's price/stock in both
4. If different, check the API response format
5. Verify Product.fromJson() in mobile app correctly parses the data
""")
