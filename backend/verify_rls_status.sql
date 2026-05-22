-- =============================================
-- VERIFY RLS STATUS AND FIND MISSING POLICIES
-- =============================================
-- Run this in Supabase SQL Editor to check your setup

-- 1. Check which tables have RLS enabled
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled,
    CASE 
        WHEN rowsecurity THEN '✅ Enabled'
        ELSE '❌ DISABLED'
    END as status
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY rowsecurity DESC, tablename;

-- 2. Count policies per table
SELECT 
    schemaname,
    tablename,
    COUNT(*) as policy_count
FROM pg_policies
WHERE schemaname = 'public'
GROUP BY schemaname, tablename
ORDER BY policy_count DESC, tablename;

-- 3. Find tables with RLS enabled but NO policies (SECURITY RISK!)
SELECT 
    t.tablename,
    '⚠️ RLS ENABLED BUT NO POLICIES - TABLE IS INACCESSIBLE!' as warning
FROM pg_tables t
WHERE t.schemaname = 'public'
AND t.rowsecurity = true
AND NOT EXISTS (
    SELECT 1 FROM pg_policies p 
    WHERE p.schemaname = t.schemaname 
    AND p.tablename = t.tablename
)
ORDER BY t.tablename;

-- 4. List all existing policies
SELECT 
    schemaname,
    tablename,
    policyname,
    cmd as operation,
    CASE 
        WHEN roles = '{public}' THEN 'Public'
        WHEN roles = '{authenticated}' THEN 'Authenticated'
        ELSE array_to_string(roles, ', ')
    END as applies_to
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
