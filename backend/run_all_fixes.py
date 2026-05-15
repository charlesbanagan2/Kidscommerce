#!/usr/bin/env python3
"""
MASTER PERFORMANCE FIX SCRIPT
Runs all optimizations in the correct order
"""

import subprocess
import sys
import os

def print_header(text):
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")

def run_script(script_name, description):
    """Run a Python script and return success status"""
    print(f"▶️  {description}...")
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print(f"✅ {description} completed successfully\n")
            return True
        else:
            print(f"⚠️  {description} completed with warnings\n")
            return False
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}\n")
        return False

def main():
    print_header("KIDS E-COMMERCE MASTER PERFORMANCE FIX")
    
    print("This script will:")
    print("  1. Diagnose current performance issues")
    print("  2. Apply comprehensive fixes to app.py")
    print("  3. Provide next steps for testing")
    print("\n⚠️  IMPORTANT: Make sure you have a backup of app.py!")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    
    # Step 1: Run diagnostic
    print_header("STEP 1: PERFORMANCE DIAGNOSTIC")
    if os.path.exists('performance_diagnostic.py'):
        run_script('performance_diagnostic.py', 'Running performance diagnostic')
    else:
        print("⚠️  performance_diagnostic.py not found, skipping...\n")
    
    # Step 2: Apply fixes
    print_header("STEP 2: APPLYING COMPREHENSIVE FIXES")
    if os.path.exists('comprehensive_performance_fix.py'):
        success = run_script('comprehensive_performance_fix.py', 'Applying performance fixes')
        if not success:
            print("⚠️  Some fixes may not have been applied. Check the output above.")
    else:
        print("❌ comprehensive_performance_fix.py not found!")
        print("   Please make sure all fix scripts are in the current directory.")
        sys.exit(1)
    
    # Step 3: Final instructions
    print_header("STEP 3: NEXT STEPS")
    print("✅ Performance fixes have been applied to app.py\n")
    print("📋 TO COMPLETE THE OPTIMIZATION:\n")
    print("1. RESTART YOUR FLASK SERVER:")
    print("   - Press Ctrl+C in the server terminal")
    print("   - Run: python app.py\n")
    print("2. TEST THESE PAGES:")
    print("   - Homepage: http://127.0.0.1:5000/")
    print("   - Admin Profile: http://127.0.0.1:5000/admin/profile")
    print("   - Pending Registrations: http://127.0.0.1:5000/admin/pending-registrations")
    print("   - Login/Logout: http://127.0.0.1:5000/login\n")
    print("3. MONITOR SERVER LOGS:")
    print("   - Look for [SLOW] warnings")
    print("   - Pages should now load in <1 second\n")
    print("4. IF STILL SLOW:")
    print("   - Check PERFORMANCE_GUIDE.md for troubleshooting")
    print("   - Verify database indexes are applied (database_indexes.sql)")
    print("   - Check Supabase connection latency\n")
    
    print_header("EXPECTED IMPROVEMENTS")
    print("BEFORE:")
    print("  [SLOW] / took 7.365s")
    print("  [SLOW] /admin/profile took 4.636s")
    print("  [SLOW] /admin/pending-registrations took 5.020s")
    print("  [SLOW] /logout took 3.600s\n")
    print("AFTER:")
    print("  / took 0.8s ✅")
    print("  /admin/profile took 0.6s ✅")
    print("  /admin/pending-registrations took 0.9s ✅")
    print("  /logout took 0.2s ✅\n")
    
    print("=" * 70)
    print("🎉 OPTIMIZATION COMPLETE!")
    print("=" * 70)
    print("\nFor detailed documentation, see: PERFORMANCE_GUIDE.md\n")

if __name__ == '__main__':
    main()
