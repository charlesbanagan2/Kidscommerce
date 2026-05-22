# Supabase + Vercel Integration Guide

## 🎯 Overview
This guide helps you connect your Vercel-deployed Flask backend with your Supabase database.

## 📋 Prerequisites
- Supabase project: `qkdacoawexaxejljfihh`
- Supabase URL: `https://qkdacoawexaxejljfihh.supabase.co`
- Vercel account with deployed project

## 🔧 Step 1: Configure Supabase for Vercel

### 1.1 Update Supabase CORS Settings
1. Go to [Supabase Dashboard](https://app.supabase.com/project/qkdacoawexaxejljfihh)
2. Navigate to **Settings → API**
3. Scroll to **CORS Configuration**
4. Add your Vercel URLs:
   ```
   https://kidscommerce.vercel.app
   https://*.vercel.app
   ```

### 1.2 Verify Database Connection String
Your connection string is already configured:
```
postgresql+psycopg2://postgres.qkdacoawexaxejljfihh:Kidscommerce%401234@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres
```

This uses Supabase's **Transaction Pooler** which is perfect for serverless deployments like Vercel.

### 1.3 Check Row Level Security (RLS)
1. Go to **Authentication → Policies**
2. Ensure RLS policies are properly configured for:
   - `user` table
   - `product` table
   - `cart` table
   - `order` table
   - `order_item` table
   - `review` table
   - `notification` table

## 🚀 Step 2: Configure Vercel Environment Variables

In your Vercel project dashboard (**Settings → Environment Variables**), add:

### Database Configuration
```bash
SUPABASE_URL=https://qkdacoawexaxejljfihh.supabase.co
SUPABASE_KEY=sb_publishable_PcSjw7T6f7D4tj3s8SxZKg_IqTuUhWM
SUPABASE_SERVICE_KEY=sb_secret_Kxo54KzgPd8haK3Za_-VkQ_AoTWJUhX
SUPABASE_DB_URL=postgresql+psycopg2://postgres.qkdacoawexaxejljfihh:Kidscommerce%401234@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres
```

### Security Keys
```bash
SECRET_KEY=KidsKingdom_SuperSecure_FlaskSession_Key_2026!#
JWT_SECRET_KEY=KidsKingdom_Mobile_Authentication_JWT_Secret_Token_072223
```

### Email Configuration
```bash
MAIL_SENDER=charlesgabrielle.banagan@lspu.edu.ph
MAIL_APP_PASSWORD=uadirdemyawgaemu
MAIL_SENDER_NAME=Kids Kingdom
EMAILLISTVERIFY_API_KEY=WCoX3dgyRS7WsEVopg7afzNIfsQAfXVH
```

### Google OAuth
```bash
GOOGLE_CLIENT_ID=43948051603-4urea9cbk1n1ppbk8ehnkepssi2vkmfv.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
```

### Flask Configuration
```bash
FLASK_ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=10000
USE_LOCAL_ORM_FALLBACK=0
```

**Important:** Set `USE_LOCAL_ORM_FALLBACK=0` for Vercel deployment to ensure it uses Supabase REST API.

## 🔐 Step 3: Supabase Security Best Practices

### 3.1 API Keys
- **Anon Key** (`SUPABASE_KEY`): Used for client-side requests with RLS
- **Service Key** (`SUPABASE_SERVICE_KEY`): Used for admin operations, bypasses RLS

### 3.2 Connection Pooling
Your app uses Supabase's Transaction Pooler (port 6543) which is optimized for:
- Serverless environments
- Short-lived connections
- High concurrency

### 3.3 RLS Policies
Ensure these policies are active:

#### User Table
```sql
-- Users can read their own data
CREATE POLICY "Users can view own data" ON user
  FOR SELECT USING (auth.uid() = id::text);

-- Users can update their own data
CREATE POLICY "Users can update own data" ON user
  FOR UPDATE USING (auth.uid() = id::text);
```

#### Product Table
```sql
-- Anyone can view approved products
CREATE POLICY "Anyone can view approved products" ON product
  FOR SELECT USING (status = 'approved');

-- Sellers can manage their own products
CREATE POLICY "Sellers can manage own products" ON product
  FOR ALL USING (seller_id = auth.uid()::integer);
```

#### Cart Table
```sql
-- Users can manage their own cart
CREATE POLICY "Users can manage own cart" ON cart
  FOR ALL USING (user_id = auth.uid()::integer);
```

## 🧪 Step 4: Test the Connection

### 4.1 Test Database Connection
After deploying to Vercel, check the logs:
```
[OK] Direct PostgreSQL connection successful
```

### 4.2 Test API Endpoints
Test these endpoints with your Vercel URL:

```bash
# Health check
curl https://kidscommerce.vercel.app/

# Get products
curl https://kidscommerce.vercel.app/api/products

# User registration
curl -X POST https://kidscommerce.vercel.app/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

## 🐛 Troubleshooting

### Issue: "Database connection failed"
**Cause:** Incorrect connection string or Supabase project paused

**Solution:**
1. Verify `SUPABASE_DB_URL` in Vercel environment variables
2. Check if Supabase project is active (not paused)
3. Verify password is URL-encoded: `Kidscommerce%401234`

### Issue: "RLS policy violation"
**Cause:** Row Level Security blocking requests

**Solution:**
1. Use `SUPABASE_SERVICE_KEY` for admin operations
2. Verify RLS policies in Supabase dashboard
3. Check if user is authenticated properly

### Issue: "Connection timeout"
**Cause:** Using wrong pooler or connection limit reached

**Solution:**
1. Ensure using Transaction Pooler (port 6543)
2. Check Supabase connection limits in dashboard
3. Implement connection pooling in app

### Issue: "CORS error"
**Cause:** Vercel URL not in Supabase allowed origins

**Solution:**
1. Add Vercel URL to Supabase CORS settings
2. Update `ALLOWED_ORIGINS` in Vercel environment variables

## 📊 Monitoring

### Supabase Dashboard
- **Database → Query Performance**: Monitor slow queries
- **Database → Connections**: Check active connections
- **API → Logs**: View API request logs

### Vercel Dashboard
- **Deployments → Logs**: Real-time application logs
- **Analytics**: Monitor traffic and performance
- **Functions**: Check serverless function execution

## 🔄 Database Migrations

If you need to run migrations:

1. **Local Development:**
   ```bash
   cd backend
   flask db upgrade
   ```

2. **Production (Supabase SQL Editor):**
   - Go to Supabase Dashboard → SQL Editor
   - Run migration SQL directly

## 💡 Performance Tips

1. **Use Connection Pooling**: Already configured with Supabase pooler
2. **Enable Caching**: Flask-Caching is installed
3. **Optimize Queries**: Use `selectinload()` for relationships
4. **Index Database**: Add indexes for frequently queried columns
5. **Monitor Logs**: Check Vercel logs for slow requests

## 🎯 Next Steps

1. ✅ Deploy to Vercel
2. ✅ Configure environment variables
3. ✅ Test database connection
4. ✅ Update CORS settings
5. ✅ Test API endpoints
6. ✅ Monitor logs and performance

---

**Your Supabase + Vercel setup is ready!** 🎉

For issues, check:
- Vercel logs: https://vercel.com/dashboard
- Supabase logs: https://app.supabase.com/project/qkdacoawexaxejljfihh
