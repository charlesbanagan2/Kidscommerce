-- QUICK RLS SETUP - Run this first in Supabase SQL Editor
-- This enables RLS on all tables immediately for security

-- Enable RLS on all tables
DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
    LOOP
        EXECUTE 'ALTER TABLE ' || quote_ident(r.tablename) || ' ENABLE ROW LEVEL SECURITY';
    END LOOP;
END $$;

-- Create a temporary permissive policy for service_role to allow backend operations
-- This allows your Flask app (using service key) to bypass RLS
DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
    LOOP
        -- Drop existing policies if any
        EXECUTE 'DROP POLICY IF EXISTS "Service role bypass" ON ' || quote_ident(r.tablename);
        
        -- Create permissive policy for service role
        EXECUTE 'CREATE POLICY "Service role bypass" ON ' || quote_ident(r.tablename) || 
                ' FOR ALL USING (true) WITH CHECK (true)';
    END LOOP;
END $$;

-- Verify RLS is enabled
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;
