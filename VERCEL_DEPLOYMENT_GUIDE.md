# Vercel Deployment Guide for Kids Commerce

## 🚀 Quick Deployment Steps

### 1. Prepare Your Repository
Your project is already on GitHub at: `https://github.com/charlesbanagan2/Kidscommerce`

### 2. Deploy to Vercel

#### Option A: Using the Vercel Link (Recommended)
1. Click your deployment link: https://vercel.com/new/import?framework=other&hasTrialAvailable=1&id=1239304379&name=Kidscommerce&owner=charlesbanagan2&project-name=kidscommerce&provider=github&remainingProjects=1&s=https%3A%2F%2Fgithub.com%2Fcharlesbanagan2%2FKidscommerce&totalProjects=1&teamSlug=kids-kingdom-s-projects&deploymentIds=dpl_5Ku55M8tHohHJVnTzZ8mYtDs67MJ

2. Vercel will automatically detect your repository

#### Option B: Manual Deployment
1. Go to https://vercel.com/new
2. Import your GitHub repository: `charlesbanagan2/Kidscommerce`
3. Vercel will auto-detect the configuration from `vercel.json`

### 3. Configure Environment Variables in Vercel

In your Vercel project dashboard, go to **Settings → Environment Variables** and add these:

#### Required Environment Variables:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=43948051603-4urea9cbk1n1ppbk8ehnkepssi2vkmfv.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

# Supabase Configuration
SUPABASE_URL=https://qkdacoawexaxejljfihh.supabase.co
SUPABASE_KEY=sb_publishable_PcSjw7T6f7D4tj3s8SxZKg_IqTuUhWM
SUPABASE_SERVICE_KEY=sb_secret_Kxo54KzgPd8haK3Za_-VkQ_AoTWJUhX
SUPABASE_DB_URL=postgresql+psycopg2://postgres.qkdacoawexaxejljfihh:Kidscommerce%401234@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres

# Email Configuration
MAIL_SENDER=charlesgabrielle.banagan@lspu.edu.ph
MAIL_APP_PASSWORD=uadirdemyawgaemu
MAIL_SENDER_NAME=Kids Kingdom
EMAILLISTVERIFY_API_KEY=WCoX3dgyRS7WsEVopg7afzNIfsQAfXVH

# Security Keys
SECRET_KEY=KidsKingdom_SuperSecure_FlaskSession_Key_2026!#
JWT_SECRET_KEY=KidsKingdom_Mobile_Authentication_JWT_Secret_Token_072223

# Flask Configuration
FLASK_ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=10000

# CORS - Update this after deployment with your Vercel URL
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

### 4. Update ALLOWED_ORIGINS After First Deploy

After your first deployment:
1. Copy your Vercel deployment URL (e.g., `https://kidscommerce.vercel.app`)
2. Go to **Settings → Environment Variables**
3. Update `ALLOWED_ORIGINS` to include your Vercel URL:
   ```
   ALLOWED_ORIGINS=https://kidscommerce.vercel.app,http://localhost:3000
   ```
4. Redeploy the project

### 5. Update Supabase CORS Settings

1. Go to your Supabase Dashboard: https://app.supabase.com/project/qkdacoawexaxejljfihh
2. Navigate to **Settings → API**
3. Add your Vercel URL to the allowed origins:
   - `https://kidscommerce.vercel.app` (or your actual Vercel URL)

### 6. Update Google OAuth Redirect URIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services → Credentials**
3. Find your OAuth 2.0 Client ID
4. Add these Authorized redirect URIs:
   - `https://kidscommerce.vercel.app/login/google/authorized`
   - `https://kidscommerce.vercel.app/auth/google/callback`
   (Replace with your actual Vercel URL)

## 📋 Deployment Checklist

- [ ] Push latest code to GitHub
- [ ] Create `vercel.json` configuration (already created)
- [ ] Deploy to Vercel using the link or manually
- [ ] Add all environment variables in Vercel dashboard
- [ ] Update `ALLOWED_ORIGINS` with Vercel URL
- [ ] Update Supabase CORS settings
- [ ] Update Google OAuth redirect URIs
- [ ] Test the deployment

## 🔧 Troubleshooting

### Issue: 500 Internal Server Error
**Solution:** Check Vercel logs in the dashboard. Usually caused by missing environment variables.

### Issue: Database Connection Failed
**Solution:** Verify `SUPABASE_DB_URL` is correctly set in Vercel environment variables.

### Issue: CORS Errors
**Solution:** 
1. Update `ALLOWED_ORIGINS` in Vercel
2. Update CORS settings in Supabase dashboard

### Issue: Google Login Not Working
**Solution:** Add Vercel URL to Google OAuth authorized redirect URIs

## 📱 Mobile App Configuration

After deploying to Vercel, update your Flutter mobile app's API endpoint:

1. Open `mobile_app/lib/kids_commercedb/supabase.env`
2. Add your Vercel backend URL:
   ```
   BACKEND_URL=https://kidscommerce.vercel.app
   ```

## 🎯 Testing Your Deployment

1. Visit your Vercel URL
2. Test user registration
3. Test login (both email and Google)
4. Test product browsing
5. Test cart functionality
6. Test checkout process

## 📊 Monitoring

- **Vercel Dashboard**: Monitor deployments, logs, and analytics
- **Supabase Dashboard**: Monitor database queries and performance
- **Vercel Logs**: Real-time logs available in the dashboard

## 🔄 Continuous Deployment

Vercel automatically deploys when you push to your GitHub repository:
- Push to `main` branch → Production deployment
- Push to other branches → Preview deployments

## 💡 Tips

1. **Use Environment Variables**: Never commit sensitive keys to GitHub
2. **Monitor Logs**: Check Vercel logs regularly for errors
3. **Database Pooling**: Supabase pooler is already configured for serverless
4. **Cold Starts**: First request may be slow (Vercel serverless limitation)
5. **Function Timeout**: Vercel has a 10-second timeout for Hobby plan

## 🆘 Need Help?

- Vercel Documentation: https://vercel.com/docs
- Supabase Documentation: https://supabase.com/docs
- Check deployment logs in Vercel dashboard

---

**Ready to deploy?** Click your deployment link and follow the steps above! 🚀
