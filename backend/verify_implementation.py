import sys
import os

# Check if app.py exists and has the new endpoints
app_py_path = r'c:\Users\mnban\OneDrive\Desktop\kids\backend\app.py'

print("Verifying Backend Implementation...")
print("=" * 50)

if not os.path.exists(app_py_path):
    print("ERROR: app.py not found!")
    sys.exit(1)

with open(app_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check for new endpoints
checks = {
    "Forgot Password Endpoint": "@app.route('/api/v1/auth/forgot-password', methods=['POST'])",
    "Forgot Password Function": "def api_v1_forgot_password():",
    "FIXED VERSION Comment (Forgot)": "Send password reset code to user's email (Mobile API) - FIXED VERSION",
    "ORM Usage (Forgot)": "user = User.query.filter_by(email=email).first()",
    "Reset Password Endpoint": "@app.route('/api/v1/auth/reset-password', methods=['POST'])",
    "Reset Password Function": "def api_v1_reset_password():",
    "FIXED VERSION Comment (Reset)": "Reset user password with verification code (Mobile API) - FIXED VERSION",
    "ORM Usage (Reset)": "user.password = new_password",
    "Error Type Field": "'error_type':",
    "Database Rollback": "db.session.rollback()",
}

all_passed = True
for check_name, check_string in checks.items():
    count = content.count(check_string)
    if count > 0:
        print(f"[PASS] {check_name}: Found ({count} occurrence(s))")
    else:
        print(f"[FAIL] {check_name}: NOT FOUND")
        all_passed = False

print("=" * 50)

# Count endpoint occurrences
forgot_count = content.count("@app.route('/api/v1/auth/forgot-password'")
reset_count = content.count("@app.route('/api/v1/auth/reset-password'")

print(f"\nEndpoint Count:")
print(f"   Forgot Password: {forgot_count} (should be 1)")
print(f"   Reset Password: {reset_count} (should be 1)")

if forgot_count == 1 and reset_count == 1:
    print("[PASS] No duplicate endpoints found!")
else:
    print("[WARN] Duplicate endpoints detected!")
    all_passed = False

print("\n" + "=" * 50)
if all_passed:
    print("[SUCCESS] ALL CHECKS PASSED!")
    print("\nReady to restart backend:")
    print("   cd c:\\Users\\mnban\\OneDrive\\Desktop\\kids\\backend")
    print("   python app.py")
else:
    print("[ERROR] SOME CHECKS FAILED - Please review")

print("=" * 50)
