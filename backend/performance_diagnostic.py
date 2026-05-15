#!/usr/bin/env python3
"""
Performance Diagnostic Tool
Analyzes app.py to identify slow query patterns and missing optimizations
"""

import re

def analyze_performance_issues():
    """Scan app.py for common performance anti-patterns"""
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        recommendations = []
        
        print("=" * 70)
        print("PERFORMANCE DIAGNOSTIC REPORT")
        print("=" * 70)
        
        # Check 1: N+1 queries (queries without joinedload/selectinload)
        query_patterns = re.findall(r'(\w+)\.query\.filter[^.]*\.all\(\)', content)
        queries_without_eager = []
        for match in query_patterns:
            # Check if this query has joinedload nearby
            pattern = f"{match}.query.options"
            if pattern not in content:
                queries_without_eager.append(match)
        
        if queries_without_eager:
            issues.append(f"⚠️  Found {len(set(queries_without_eager))} queries without eager loading")
            recommendations.append("Add .options(joinedload(...)) to prevent N+1 queries")
        
        # Check 2: .count() usage (slow for large tables)
        count_queries = len(re.findall(r'\.count\(\)', content))
        if count_queries > 10:
            issues.append(f"⚠️  Found {count_queries} .count() calls (potentially slow)")
            recommendations.append("Replace .count() with scalar subqueries using func.count()")
        
        # Check 3: Missing pagination
        all_queries = re.findall(r'\.all\(\)', content)
        limited_queries = re.findall(r'\.limit\(\d+\)\.all\(\)', content)
        unlimited = len(all_queries) - len(limited_queries)
        if unlimited > 20:
            issues.append(f"⚠️  Found {unlimited} queries without .limit() (memory risk)")
            recommendations.append("Add .limit() to queries that return multiple rows")
        
        # Check 4: Session operations in loops
        if re.search(r'for .+ in .+:\s+db\.session', content, re.MULTILINE):
            issues.append("⚠️  Found db.session operations inside loops")
            recommendations.append("Batch database operations outside loops")
        
        # Check 5: Missing indexes (check if get_admin_badge_counts exists)
        if 'get_admin_badge_counts' in content:
            badge_func = re.search(r'def get_admin_badge_counts\(\):.*?(?=\ndef |\Z)', content, re.DOTALL)
            if badge_func and '.join(' in badge_func.group(0):
                issues.append("⚠️  get_admin_badge_counts() uses complex joins")
                recommendations.append("Split into separate scalar queries with indexed columns")
        
        # Check 6: Connection pool settings
        if 'pool_size' in content:
            pool_match = re.search(r"'pool_size':\s*(\d+)", content)
            if pool_match:
                pool_size = int(pool_match.group(1))
                if pool_size < 10:
                    issues.append(f"⚠️  Connection pool size is {pool_size} (may be too small)")
                    recommendations.append("Increase pool_size to 20+ for better concurrency")
        
        # Check 7: Static file caching
        if 'SEND_FILE_MAX_AGE_DEFAULT' not in content:
            issues.append("⚠️  Static file caching not configured")
            recommendations.append("Add SEND_FILE_MAX_AGE_DEFAULT to Flask config")
        
        # Print results
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"   Total lines of code: {len(content.splitlines())}")
        print(f"   Database queries found: {len(all_queries)}")
        print(f"   Queries with pagination: {len(limited_queries)}")
        print(f"   .count() operations: {count_queries}")
        
        if issues:
            print(f"\n🔴 ISSUES FOUND ({len(issues)}):")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
            
            print(f"\n💡 RECOMMENDATIONS ({len(recommendations)}):")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("\n✅ No major performance issues detected!")
        
        # Specific route analysis
        print("\n" + "=" * 70)
        print("ROUTE-SPECIFIC ANALYSIS")
        print("=" * 70)
        
        routes_to_check = [
            (r"@app\.route\('/'\)", "Homepage (/)"),
            (r"@app\.route\('/admin/profile'\)", "Admin Profile"),
            (r"@app\.route\('/admin/pending-registrations'\)", "Pending Registrations"),
            (r"@app\.route\('/login'", "Login"),
            (r"@app\.route\('/logout'\)", "Logout"),
        ]
        
        for pattern, name in routes_to_check:
            match = re.search(pattern + r'.*?(?=@app\.route|\Z)', content, re.DOTALL)
            if match:
                route_code = match.group(0)
                queries = len(re.findall(r'\.query\.', route_code))
                has_eager = 'joinedload' in route_code or 'selectinload' in route_code
                has_limit = '.limit(' in route_code
                
                status = "✅" if (has_eager or queries <= 2) and (has_limit or queries <= 1) else "⚠️"
                print(f"\n{status} {name}")
                print(f"   Queries: {queries}")
                print(f"   Eager loading: {'Yes' if has_eager else 'No'}")
                print(f"   Pagination: {'Yes' if has_limit else 'No'}")
        
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("\n1. Run: python comprehensive_performance_fix.py")
        print("2. Verify database indexes are applied (database_indexes.sql)")
        print("3. Restart Flask server and test")
        print("4. Monitor [SLOW] warnings in server logs")
        
        return len(issues)
        
    except FileNotFoundError:
        print("❌ Error: app.py not found")
        return -1
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return -1

if __name__ == '__main__':
    issue_count = analyze_performance_issues()
    exit(0 if issue_count == 0 else 1)
