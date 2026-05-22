-- =============================================
-- MISSING RLS POLICIES - ADD THESE
-- =============================================
-- These tables were missing from your original RLS script

-- =============================================
-- ENABLE RLS ON MISSING TABLES
-- =============================================

ALTER TABLE "region" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "province" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "city" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "barangay" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "city_municipality" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "order_label" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "seller_order_seen" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "restock_request" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "qr_scan_log" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "delivery_personnel" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "oauth" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "admin_profile" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "admin_security_log" ENABLE ROW LEVEL SECURITY;

-- =============================================
-- REGION/PROVINCE/CITY/BARANGAY POLICIES (PUBLIC READ)
-- =============================================

-- Everyone can read Philippine address data
CREATE POLICY "Anyone can view regions" ON "region"
  FOR SELECT USING (true);

CREATE POLICY "Anyone can view provinces" ON "province"
  FOR SELECT USING (true);

CREATE POLICY "Anyone can view cities" ON "city"
  FOR SELECT USING (true);

CREATE POLICY "Anyone can view barangays" ON "barangay"
  FOR SELECT USING (true);

CREATE POLICY "Anyone can view city_municipality" ON "city_municipality"
  FOR SELECT USING (true);

-- =============================================
-- ORDER LABEL POLICIES
-- =============================================

-- Buyers can view labels for their orders
CREATE POLICY "Buyers can view own order labels" ON "order_label"
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_label.order_id
      AND "order".buyer_id = current_setting('app.user_id', true)::bigint
    )
  );

-- Riders can view labels for assigned orders
CREATE POLICY "Riders can view assigned order labels" ON "order_label"
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = order_label.order_id
      AND (
        "order".rider_id = current_setting('app.user_id', true)::bigint
        OR "order".picked_up_by = current_setting('app.user_id', true)::bigint
      )
    )
  );

-- Sellers can view labels for orders containing their products
CREATE POLICY "Sellers can view order labels for their products" ON "order_label"
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM order_item oi
      JOIN product p ON oi.product_id = p.id
      WHERE oi.order_id = order_label.order_id
      AND p.seller_id = current_setting('app.user_id', true)::bigint
    )
  );

-- =============================================
-- SELLER ORDER SEEN POLICIES
-- =============================================

CREATE POLICY "Sellers can view own order seen records" ON "seller_order_seen"
  FOR SELECT
  USING (seller_id = current_setting('app.user_id', true)::bigint);

CREATE POLICY "Sellers can manage own order seen records" ON "seller_order_seen"
  FOR ALL
  USING (seller_id = current_setting('app.user_id', true)::bigint);

-- =============================================
-- RESTOCK REQUEST POLICIES
-- =============================================

CREATE POLICY "Sellers can view own restock requests" ON "restock_request"
  FOR SELECT
  USING (seller_id = current_setting('app.user_id', true)::bigint);

CREATE POLICY "Sellers can create restock requests" ON "restock_request"
  FOR INSERT
  WITH CHECK (seller_id = current_setting('app.user_id', true)::bigint);

-- =============================================
-- QR SCAN LOG POLICIES
-- =============================================

-- Users can view scan logs for their orders
CREATE POLICY "Users can view own order scan logs" ON "qr_scan_log"
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM "order"
      WHERE "order".id = qr_scan_log.order_id
      AND (
        "order".buyer_id = current_setting('app.user_id', true)::bigint
        OR "order".rider_id = current_setting('app.user_id', true)::bigint
      )
    )
  );

-- Riders can create scan logs
CREATE POLICY "Riders can create scan logs" ON "qr_scan_log"
  FOR INSERT
  WITH CHECK (scanned_by = current_setting('app.user_id', true)::bigint);

-- =============================================
-- DELIVERY PERSONNEL POLICIES
-- =============================================

CREATE POLICY "Riders can view own delivery personnel record" ON "delivery_personnel"
  FOR SELECT
  USING (user_id = current_setting('app.user_id', true)::bigint);

CREATE POLICY "Riders can update own delivery personnel record" ON "delivery_personnel"
  FOR UPDATE
  USING (user_id = current_setting('app.user_id', true)::bigint);

-- =============================================
-- OAUTH POLICIES
-- =============================================

CREATE POLICY "Users can view own oauth records" ON "oauth"
  FOR SELECT
  USING (user_id = current_setting('app.user_id', true)::bigint);

-- =============================================
-- ADMIN PROFILE POLICIES
-- =============================================

CREATE POLICY "Admins can view own profile" ON "admin_profile"
  FOR SELECT
  USING (user_id = current_setting('app.user_id', true)::bigint);

CREATE POLICY "Admins can update own profile" ON "admin_profile"
  FOR UPDATE
  USING (user_id = current_setting('app.user_id', true)::bigint);

-- =============================================
-- ADMIN SECURITY LOG POLICIES
-- =============================================

CREATE POLICY "Admins can view own security logs" ON "admin_security_log"
  FOR SELECT
  USING (user_id = current_setting('app.user_id', true)::bigint);

-- =============================================
-- GRANT ADDITIONAL PERMISSIONS
-- =============================================

-- Grant select on address tables
GRANT SELECT ON region TO anon, authenticated;
GRANT SELECT ON province TO anon, authenticated;
GRANT SELECT ON city TO anon, authenticated;
GRANT SELECT ON barangay TO anon, authenticated;
GRANT SELECT ON city_municipality TO anon, authenticated;

-- Grant permissions for order labels
GRANT SELECT ON order_label TO authenticated;

-- Grant permissions for seller operations
GRANT SELECT, INSERT, UPDATE ON seller_order_seen TO authenticated;
GRANT SELECT, INSERT ON restock_request TO authenticated;

-- Grant permissions for rider operations
GRANT SELECT, INSERT ON qr_scan_log TO authenticated;
GRANT SELECT, UPDATE ON delivery_personnel TO authenticated;

-- Grant permissions for admin operations
GRANT SELECT, UPDATE ON admin_profile TO authenticated;
GRANT SELECT ON admin_security_log TO authenticated;

-- Grant permissions for oauth
GRANT SELECT ON oauth TO authenticated;

-- =============================================
-- VERIFICATION QUERY
-- =============================================

-- Run this to verify all tables now have RLS and policies
SELECT 
    t.tablename,
    t.rowsecurity as rls_enabled,
    COUNT(p.policyname) as policy_count,
    CASE 
        WHEN t.rowsecurity = false THEN '❌ RLS DISABLED'
        WHEN COUNT(p.policyname) = 0 THEN '⚠️ NO POLICIES'
        ELSE '✅ SECURED'
    END as status
FROM pg_tables t
LEFT JOIN pg_policies p ON t.tablename = p.tablename AND t.schemaname = p.schemaname
WHERE t.schemaname = 'public'
GROUP BY t.tablename, t.rowsecurity
ORDER BY status, t.tablename;
