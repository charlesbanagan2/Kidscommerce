# PRODUCT IMAGES FIX

## CURRENT STATUS
- ✅ Kids Kingdom logo - VISIBLE
- ✅ Hero slides - VISIBLE
- ❌ Product images - NOT VISIBLE

## PROBLEM
Ang database URLs ay naka-point pa rin sa Supabase Storage:
```
https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/xxx.png
```

Pero ang product images ay WALA sa Supabase Storage. Ang images ay naka-upload sa **Git/Render** na lang.

## SOLUTION

### Run SQL Script to Revert URLs
1. Go to: https://supabase.com/dashboard/project/qkdacoawexaxejljfihh/sql/new
2. Copy-paste ang SQL from `REVERT_PRODUCT_IMAGES_TO_LOCAL.sql`
3. Click **RUN**

This will change:
- **FROM**: `https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/20251124_133613_Screenshot_2025-11-24_213535.png`
- **TO**: `20251124_133613_Screenshot_2025-11-24_213535.png`

Then the backend will serve from: `https://kids-kingdom.onrender.com/static/uploads/20251124_133613_Screenshot_2025-11-24_213535.png`

## EXPECTED RESULT
After running the SQL:
- ✅ Product images should appear on website
- ✅ Store logos should remain visible
- ✅ All images served from Render

## VERIFICATION
1. Run the SQL script
2. Refresh website: https://kids-kingdom.onrender.com
3. Check homepage - product images should appear
4. Check product detail pages
5. Check mobile app

## FILES
- `REVERT_PRODUCT_IMAGES_TO_LOCAL.sql` - SQL script to run
