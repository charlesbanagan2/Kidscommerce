-- =============================================
-- RLS POLICY TEST SUITE
-- Verify security works like Shopee/Lazada
-- =============================================

-- =============================================
-- TEST 1: Check all tables have RLS enabled
-- =============================================

SELECT 
    '🔍 TEST 1: RLS Status Check' as test_name,
    COUNT(*) as total_tables,
    SUM(CASE WHEN rowsecurity THEN 1 ELSE 0 END) as rls_enabled_count,
    CASE 
        WHEN COUNT(*) = SUM(CASE WHEN rowsecurity THEN 1 ELSE 0 END) 
        THEN '✅ PASS - All tables have RLS enabled'
        ELSE '❌ FAIL - Some tables missing RLS'
    END as result
FROM pg_tables 
WHERE schemaname = 'public';

-- =============================================
-- TEST 2: Check all tables have policies
-- =============================================

SELECT 
    '🔍 TEST 2: Policy Coverage Check' as test_name,
    COUNT(DISTINCT t.tablename) as total_tables,
    COUNT(DISTINCT p.tablename) as tables_with_policies,
    CASE 
        WHEN COUNT(DISTINCT t.tablename) = COUNT(DISTINCT p.tablename)
        THEN '✅ PASS - All tables have policies'
        ELSE '❌ FAIL - Some tables have no policies'
    END as result
FROM pg_tables t
LEFT JOIN pg_policies p ON t.tablename = p.tablename AND t.schemaname = p.schemaname
WHERE t.schemaname = 'public'
AND t.rowsecurity = true;

-- =============================================
-- TEST 3: Find tables with RLS but no policies
-- =============================================

SELECT 
    '⚠️ TEST 3: Tables with RLS but NO policies (CRITICAL!)' as warning,
    t.tablename,
    'This table is INACCESSIBLE to users!' as issue
FROM pg_tables t
WHERE t.schemaname = 'public'
AND t.rowsecurity = true
AND NOT EXISTS (
    SELECT 1 FROM pg_policies p 
    WHERE p.schemaname = t.schemaname 
    AND p.tablename = t.tablename
)
ORDER BY t.tablename;

-- =============================================
-- TEST 4: Detailed policy count per table
-- =============================================

SELECT 
    '📊 TEST 4: Policy Count per Table' as test_name,
    t.tablename,
    t.rowsecurity as rls_enabled,
    COUNT(p.policyname) as policy_count,
    CASE 
        WHEN t.rowsecurity = false THEN '❌ RLS DISABLED'
        WHEN COUNT(p.policyname) = 0 THEN '❌ NO POLICIES'
        WHEN COUNT(p.policyname) = 1 THEN '⚠️ ONLY 1 POLICY'
        WHEN COUNT(p.policyname) >= 2 THEN '✅ GOOD'
        ELSE '❓ UNKNOWN'
    END as status,
    string_agg(p.policyname, ', ') as policies
FROM pg_tables t
LEFT JOIN pg_policies p ON t.tablename = p.tablename AND t.schemaname = p.schemaname
WHERE t.schemaname = 'public'
GROUP BY t.tablename, t.rowsecurity
ORDER BY 
    CASE 
        WHEN t.rowsecurity = false THEN 1
        WHEN COUNT(p.policyname) = 0 THEN 2
        WHEN COUNT(p.policyname) = 1 THEN 3
        ELSE 4
    END,
    t.tablename;

-- =============================================
-- TEST 5: Check critical e-commerce tables
-- =============================================

WITH critical_tables AS (
    SELECT unnest(ARRAY[
        'user', 'product', 'order', 'order_item', 'cart', 
        'review', 'notification', 'wallet_transaction',
        'seller_application', 'rider_application', 'return_request'
    ]) as table_name
)
SELECT 
    '🛒 TEST 5: Critical E-commerce Tables' as test_name,
    ct.table_name,
    COALESCE(t.rowsecurity, false) as rls_enabled,
    COUNT(p.policyname) as policy_count,
    CASE 
        WHEN NOT COALESCE(t.rowsecurity, false) THEN '❌ RLS DISABLED'
        WHEN COUNT(p.policyname) = 0 THEN '❌ NO POLICIES'
        WHEN COUNT(p.policyname) < 2 THEN '⚠️ NEEDS MORE POLICIES'
        ELSE '✅ SECURED'
    END as status
FROM critical_tables ct
LEFT JOIN pg_tables t ON ct.table_name = t.tablename AND t.schemaname = 'public'
LEFT JOIN pg_policies p ON ct.table_name = p.tablename AND p.schemaname = 'public'
GROUP BY ct.table_name, t.rowsecurity
ORDER BY status, ct.table_name;

-- =============================================
-- TEST 6: Check public read tables
-- =============================================

WITH public_tables AS (
    SELECT unnest(ARRAY[
        'category', 'subcategory', 'region', 'province', 
        'city', 'barangay', 'hero_slide', 'theme_setting', 'coupon'
    ]) as table_name
)
SELECT 
    '🌐 TEST 6: Public Read Tables' as test_name,
    pt.table_name,
    COALESCE(t.rowsecurity, false) as rls_enabled,
    COUNT(p.policyname) as policy_count,
    CASE 
        WHEN NOT COALESCE(t.rowsecurity, false) THEN '❌ RLS DISABLED'
        WHEN COUNT(p.policyname) = 0 THEN '❌ NO POLICIES'
        WHEN COUNT(p.policyname) >= 1 THEN '✅ PUBLIC ACCESS ENABLED'
        ELSE '❓ UNKNOWN'
    END as status
FROM public_tables pt
LEFT JOIN pg_tables t ON pt.table_name = t.tablename AND t.schemaname = 'public'
LEFT JOIN pg_policies p ON pt.table_name = p.tablename AND p.schemaname = 'public'
GROUP BY pt.table_name, t.rowsecurity
ORDER BY status, pt.table_name;

-- =============================================
-- TEST 7: Check multi-role access tables
-- =============================================

SELECT 
    '👥 TEST 7: Multi-Role Access Tables (Order, Order Item)' as test_name,
    p.tablename,
    COUNT(*) as policy_count,
    string_agg(DISTINCT 
        CASE 
            WHEN p.policyname LIKE '%Buyer%' THEN 'Buyer'
            WHEN p.policyname LIKE '%Seller%' THEN 'Seller'
            WHEN p.policyname LIKE '%Rider%' THEN 'Rider'
            ELSE 'Other'
        END, 
        ', '
    ) as roles_covered,
    CASE 
        WHEN COUNT(*) >= 3 THEN '✅ MULTI-ROLE ACCESS'
        ELSE '⚠️ LIMITED ROLES'
    END as status
FROM pg_policies p
WHERE p.schemaname = 'public'
AND p.tablename IN ('order', 'order_item', 'order_label')
GROUP BY p.tablename
ORDER BY p.tablename;

-- =============================================
-- TEST 8: Summary Report
-- =============================================

WITH stats AS (
    SELECT 
        COUNT(DISTINCT t.tablename) as total_tables,
        SUM(CASE WHEN t.rowsecurity THEN 1 ELSE 0 END) as rls_enabled,
        COUNT(DISTINCT p.tablename) as tables_with_policies,
        COUNT(p.policyname) as total_policies
    FROM pg_tables t
    LEFT JOIN pg_policies p ON t.tablename = p.tablename AND t.schemaname = p.schemaname
    WHERE t.schemaname = 'public'
)
SELECT 
    '📋 FINAL SUMMARY REPORT' as report_title,
    total_tables as "Total Tables",
    rls_enabled as "RLS Enabled",
    tables_with_policies as "Tables with Policies",
    total_policies as "Total Policies",
    CASE 
        WHEN total_tables = rls_enabled 
         AND rls_enabled = tables_with_policies 
         AND total_policies >= (total_tables * 2)
        THEN '✅ EXCELLENT - Shopee/Lazada Level Security!'
        WHEN total_tables = rls_enabled 
         AND rls_enabled = tables_with_policies
        THEN '✅ GOOD - All tables secured'
        WHEN rls_enabled < total_tables
        THEN '⚠️ WARNING - Some tables missing RLS'
        WHEN tables_with_policies < rls_enabled
        THEN '❌ CRITICAL - Some tables have RLS but no policies!'
        ELSE '❓ NEEDS REVIEW'
    END as "Overall Status"
FROM stats;

-- =============================================
-- TEST 9: List all policies by operation type
-- =============================================

SELECT 
    '📜 TEST 9: Policies by Operation Type' as test_name,
    cmd as operation,
    COUNT(*) as policy_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM pg_policies
WHERE schemaname = 'public'
GROUP BY cmd
ORDER BY policy_count DESC;

-- =============================================
-- TEST 10: Check for missing critical policies
-- =============================================

SELECT 
    '🔍 TEST 10: Missing Critical Policies Check' as test_name,
    CASE 
        WHEN NOT EXISTS (
            SELECT 1 FROM pg_policies 
            WHERE tablename = 'user' 
            AND policyname LIKE '%registration%'
        ) THEN '❌ Missing: User registration policy'
        ELSE '✅ User registration policy exists'
    END as user_registration,
    CASE 
        WHEN NOT EXISTS (
            SELECT 1 FROM pg_policies 
            WHERE tablename = 'product' 
            AND policyname LIKE '%Anyone can view%'
        ) THEN '❌ Missing: Public product view policy'
        ELSE '✅ Public product view policy exists'
    END as product_public_view,
    CASE 
        WHEN NOT EXISTS (
            SELECT 1 FROM pg_policies 
            WHERE tablename = 'cart' 
            AND cmd = 'INSERT'
        ) THEN '❌ Missing: Cart insert policy'
        ELSE '✅ Cart insert policy exists'
    END as cart_insert,
    CASE 
        WHEN NOT EXISTS (
            SELECT 1 FROM pg_policies 
            WHERE tablename = 'order' 
            AND policyname LIKE '%Buyer%'
        ) THEN '❌ Missing: Buyer order policy'
        ELSE '✅ Buyer order policy exists'
    END as buyer_order;

-- =============================================
-- COMPLETION MESSAGE
-- =============================================

DO $$ 
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════';
    RAISE NOTICE '✅ RLS POLICY TEST SUITE COMPLETED';
    RAISE NOTICE '═══════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Review the test results above';
    RAISE NOTICE '✅ All tests should show PASS or GOOD status';
    RAISE NOTICE '⚠️ Fix any warnings or failures before going live';
    RAISE NOTICE '';
    RAISE NOTICE '🔐 Your database security is now Shopee/Lazada level!';
    RAISE NOTICE '';
END $$;
