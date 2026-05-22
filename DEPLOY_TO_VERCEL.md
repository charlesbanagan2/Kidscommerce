# 🚀 Deploy Kids Commerce to Vercel - Quick Start

## ⚡ Fast Track Deployment (5 Minutes)

### Step 1: Click Your Deployment Link
👉 **[CLICK HERE TO DEPLOY](https://vercel.com/new/import?framework=other&hasTrialAvailable=1&id=1239304379&name=Kidscommerce&owner=charlesbanagan2&project-name=kidscommerce&provider=github&remainingProjects=1&s=https%3A%2F%2Fgithub.com%2Fcharlesbanagan2%2FKidscommerce&totalProjects=1&teamSlug=kids-kingdom-s-projects&deploymentIds=dpl_5Ku55M8tHohHJVnTzZ8mYtDs67MJ)**

### Step 2: Import Your Repository
1. Vercel will detect your GitHub repository
2. Click **"Import"**
3. Vercel will automatically detect the configuration from `vercel.json`

### Step 3: Configure Environment Variables
Click **"Environment Variables"** and paste this entire block:

```env
GOOGLE_CLIENT_ID=43948051603-4urea9cbk1n1ppbk8ehnkepssi2vkmfv.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
SUPABASE_URL=https://qkdacoawexaxejljfihh.supabase.co
SUPABASE_KEY=sb_publishable_PcSjw7T6f7D4tj3s8SxZKg_IqTuUhWM
SUPABASE_SERVICE_KEY=sb_secret_Kxo54KzgPd8haK3Za_-VkQ_AoTWJUhX
SUPABASE_DB_URL=postgresql+psycopg2://postgres.qkdacoawexaxejljfihh:Kidscommerce%401234@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres
MAIL_SENDER=charlesgabrielle.banagan@lspu.edu.ph
MAIL_APP_PASSWORD=uadirdemyawgaemu
MAIL_SENDER_NAME=Kids Kingdom
EMAILLISTVERIFY_API_KEY=WCoX3dgyRS7WsEVopg7afzNIfsQAfXVH
SECRET_KEY=KidsKingdom_SuperSecure_FlaskSession_Key_2026!#
JWT_SECRET_KEY=KidsKingdom_Mobile_Authentication_JWT_Secret_Token_072223
FLASK_ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=10000
USE_LOCAL_ORM_FALLBACK=0
ALLOWED_ORIGINS=https://kidscommerce.vercel.app,http://localhost:3000
```

**Note:** You can paste this as bulk import or add them one by one.

### Step 4: Deploy!
1. Click **"Deploy"**
2. Wait 2-3 minutes for the build to complete
3. You'll get a URL like: `https://kidscommerce.vercel.app`

### Step 5: Update ALLOWED_ORIGINS (Important!)
After deployment:
1. Copy your Vercel URL
2. Go to **Settings → Environment Variables**
3. Edit `ALLOWED_ORIGINS` and replace with your actual URL:
   ```
   ALLOWED_ORIGINS=https://your-actual-url.vercel.app,http://localhost:3000
   ```
4. Click **"Redeploy"** in the Deployments tab

## ✅ Post-Deployment Checklist

### 1. Update Supabase CORS
- [ ] Go to [Supabase Dashboard](https://app.supabase.com/project/qkdacoawexaxejljfihh/settings/api)
- [ ] Add your Vercel URL to allowed origins
- [ ] Save changes

### 2. Update Google OAuth
- [ ] Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- [ ] Add redirect URI: `https://your-vercel-url.vercel.app/login/google/authorized`
- [ ] Add redirect URI: `https://your-vercel-url.vercel.app/auth/google/callback`
- [ ] Save changes

### 3. Test Your Deployment
- [ ] Visit your Vercel URL
- [ ] Test user registration
- [ ] Test login
- [ ] Test product browsing
- [ ] Check Vercel logs for errors

### 4. Update Mobile App
- [ ] Open `mobile_app/lib/kids_commercedb/supabase.env`
- [ ] Add: `BACKEND_URL=https://your-vercel-url.vercel.app`
- [ ] Rebuild your mobile app

## 🐛 Common Issues & Quick Fixes

### ❌ "Build Failed"
**Fix:** Check Vercel build logs. Usually missing dependencies.
```bash
# Make sure requirements.txt is in the root directory
# Vercel looks for it there
```

### ❌ "500 Internal Server Error"
**Fix:** Check environment variables are set correctly
1. Go to Settings → Environment Variables
2. Verify all variables are present
3. Redeploy

### ❌ "Database Connection Failed"
**Fix:** Verify `SUPABASE_DB_URL` is correct
```
postgresql+psycopg2://postgres.qkdacoawexaxejljfihh:Kidscommerce%401234@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres
```
Note the `%40` (URL-encoded `@` symbol)

### ❌ "CORS Error"
**Fix:** 
1. Update `ALLOWED_ORIGINS` in Vercel
2. Add Vercel URL to Supabase CORS settings

### ❌ "Google Login Not Working"
**Fix:** Add Vercel URL to Google OAuth redirect URIs

## 📱 Mobile App Integration

After deploying, update your Flutter app:

1. **Update API Endpoint:**
   ```dart
   // In your API service file
   static const String baseUrl = 'https://your-vercel-url.vercel.app';
   ```

2. **Test Mobile App:**
   ```bash
   cd mobile_app
   flutter run
   ```

## 📊 Monitor Your Deployment

### Vercel Dashboard
- **Deployments**: View deployment history
- **Logs**: Real-time application logs
- **Analytics**: Traffic and performance metrics

### Supabase Dashboard
- **Database**: Monitor queries and connections
- **API Logs**: View API request logs
- **Auth**: Monitor user authentication

## 🎯 What's Deployed?

Your Vercel deployment includes:
- ✅ Flask backend API
- ✅ Supabase database connection
- ✅ Google OAuth authentication
- ✅ Email verification system
- ✅ Product management
- ✅ Cart and checkout
- ✅ Order management
- ✅ Notification system
- ✅ Chat functionality
- ✅ Review system

## 🔄 Continuous Deployment

Vercel automatically deploys when you push to GitHub:
- **Main branch** → Production deployment
- **Other branches** → Preview deployments

To deploy changes:
```bash
git add .
git commit -m "Your changes"
git push origin main
```

Vercel will automatically build and deploy!

## 💡 Pro Tips

1. **Use Preview Deployments**: Test changes on preview URLs before merging to main
2. **Monitor Logs**: Check logs regularly for errors
3. **Set Up Alerts**: Configure Vercel to notify you of deployment failures
4. **Use Environment Variables**: Never commit secrets to GitHub
5. **Enable Analytics**: Track your app's performance

## 🆘 Need Help?

- **Vercel Docs**: https://vercel.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Check Logs**: Vercel Dashboard → Your Project → Logs

## 📞 Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check Supabase logs
3. Verify all environment variables
4. Test API endpoints with curl or Postman

---

## 🎉 You're Ready!

Click the deployment link above and follow the steps. Your Kids Commerce app will be live in minutes!

**Deployment Link:** https://vercel.com/new/import?framework=other&hasTrialAvailable=1&id=1239304379&name=Kidscommerce&owner=charlesbanagan2&project-name=kidscommerce&provider=github&remainingProjects=1&s=https%3A%2F%2Fgithub.com%2Fcharlesbanagan2%2FKidscommerce&totalProjects=1&teamSlug=kids-kingdom-s-projects&deploymentIds=dpl_5Ku55M8tHohHJVnTzZ8mYtDs67MJ

Good luck! 🚀
