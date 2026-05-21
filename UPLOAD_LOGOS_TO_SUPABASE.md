# UPLOAD KIDS KINGDOM LOGOS TO SUPABASE STORAGE

## PROBLEMA
Ang Kids Kingdom logo at iba pang static images ay hindi lumalabas sa Render server.

## DAHILAN
Ang logo files ay naka-store locally sa `backend/static/uploads/` pero hindi kasama sa Render server.

## LOGO FILES NA KAILANGAN I-UPLOAD
- `kklogo_black.png` - Main logo (black version)
- `logo_ulit.png` - Alternative logo
- `logo_white.png` - White version
- `logo_150x40.png` - Small logo
- `logo1.png` - Logo variant 1
- `logo_2.png` - Logo variant 2
- `default-store-logo.png` - Default store logo
- `hero_slide_1.png` - Hero slide image
- `hero_slide_4_new_arrival.png` - Hero slide image

## SOLUSYON: 2 OPTIONS

### ⭐ OPTION 1: UPLOAD VIA SUPABASE DASHBOARD (RECOMMENDED)

**STEP 1: Go to Supabase Storage**
1. Open: https://supabase.com/dashboard/project/qkdacoawexaxejljfihh/storage/buckets/product-images
2. Click **Upload files** button

**STEP 2: Upload Logo Files**
1. Navigate to: `c:\Users\mnban\OneDrive\Desktop\kids\backend\static\uploads\`
2. Select these files:
   - `kklogo_black.png`
   - `logo_ulit.png`
   - `logo_white.png`
   - `logo_150x40.png`
   - `logo1.png`
   - `logo_2.png`
   - `default-store-logo.png`
   - `hero_slide_1.png`
   - `hero_slide_4_new_arrival.png`
3. Click **Upload**
4. Wait for upload to complete

**STEP 3: Update Backend Code**
Update `base.html` to use Supabase Storage URL:

```html
<!-- BEFORE -->
<img src="{{ url_for('static', filename='uploads/' ~ theme_logo) }}" alt="Site Logo" class="navbar-brand-logo">

<!-- AFTER -->
<img src="https://qkdacoawexaxejljfihh.supabase.co/storage/v1/object/public/product-images/{{ theme_logo }}" alt="Site Logo" class="navbar-brand-logo">
```

---

### OPTION 2: COMMIT LOGOS TO GIT (QUICK FIX)

**STEP 1: Create .gitignore Exception**
Add this to `.gitignore`:

```
# Allow logo files
!backend/static/uploads/kklogo_black.png
!backend/static/uploads/logo_ulit.png
!backend/static/uploads/logo_white.png
!backend/static/uploads/logo_150x40.png
!backend/static/uploads/logo1.png
!backend/static/uploads/logo_2.png
!backend/static/uploads/default-store-logo.png
!backend/static/uploads/hero_slide_1.png
!backend/static/uploads/hero_slide_4_new_arrival.png
```

**STEP 2: Commit and Push**
```bash
git add backend/static/uploads/kklogo_black.png
git add backend/static/uploads/logo_ulit.png
git add backend/static/uploads/logo_white.png
git add backend/static/uploads/logo_150x40.png
git add backend/static/uploads/logo1.png
git add backend/static/uploads/logo_2.png
git add backend/static/uploads/default-store-logo.png
git add backend/static/uploads/hero_slide_1.png
git add backend/static/uploads/hero_slide_4_new_arrival.png
git commit -m "add: Kids Kingdom logos and hero slides"
git push origin main
```

**STEP 3: Redeploy Render**

**PROS:**
- ✅ Quick and simple
- ✅ No code changes needed

**CONS:**
- ⚠️ Increases Git repo size (~2MB)
- ⚠️ Not scalable for many images

---

## ⭐ RECOMMENDED: OPTION 2 (COMMIT TO GIT)

Para sa logo files lang, okay lang i-commit sa Git kasi:
- Small files lang (total ~2MB)
- Static assets na hindi nagbabago
- Kailangan available sa lahat ng deployments

Para sa product images at store logos, use Supabase Storage (already done).

---

## CURRENT STATUS
- ✅ Product images uploaded to Supabase Storage (25 products)
- ✅ Store logos uploaded to Supabase Storage (6 stores)
- ✅ Database URLs updated
- ❌ Kids Kingdom logo files NOT uploaded yet
- ❌ Hero slide images NOT uploaded yet

## NEXT STEPS
1. **Upload logo files** (Option 1 or 2)
2. **Redeploy Render**
3. **Test website** - check if logo appears
