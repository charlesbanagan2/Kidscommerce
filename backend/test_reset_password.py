#!/usr/bin/env python3
"""
Reset Password Error Handling Test Script
Tests all scenarios to verify proper error messages
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://192.168.1.20:5000"
TEST_EMAIL = "test@gmail.com"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_test(test_name):
    print(f"{Colors.BOLD}🧪 Test: {test_name}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.END}")

def request_reset_code(email):
    """Request a password reset code"""
    print_info(f"Requesting reset code for: {email}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/forgot-password",
        json={"email": email},
        timeout=10
    )
    
    print_info(f"Status Code: {response.status_code}")
    print_info(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def reset_password(email, code, new_password):
    """Attempt to reset password with given code"""
    print_info(f"Attempting reset with code: {code}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/reset-password",
        json={
            "email": email,
            "code": code,
            "new_password": new_password
        },
        timeout=10
    )
    
    print_info(f"Status Code: {response.status_code}")
    result = response.json()
    print_info(f"Response: {json.dumps(result, indent=2)}")
    
    return result

def test_wrong_code_first_attempt():
    """Test 1: Wrong code on first attempt"""
    print_test("Wrong Code - 1st Attempt")
    
    # Request code first
    request_reset_code(TEST_EMAIL)
    time.sleep(1)
    
    # Try wrong code
    result = reset_password(TEST_EMAIL, "111111", "NewPass123!")
    
    # Verify response
    if result.get('success') == False:
        error = result.get('error', '')
        error_type = result.get('error_type', '')
        remaining = result.get('remaining_attempts', 0)
        
        if error_type == 'invalid_code' and remaining == 2:
            print_success(f"Correct error type: {error_type}")
            print_success(f"Correct remaining attempts: {remaining}")
            print_success(f"Error message: {error}")
            return True
        else:
            print_error(f"Wrong error type or attempts: {error_type}, remaining: {remaining}")
            return False
    else:
        print_error("Should have failed but succeeded!")
        return False

def test_wrong_code_second_attempt():
    """Test 2: Wrong code on second attempt"""
    print_test("Wrong Code - 2nd Attempt")
    
    # Request code first
    request_reset_code(TEST_EMAIL)
    time.sleep(1)
    
    # First wrong attempt
    reset_password(TEST_EMAIL, "111111", "NewPass123!")
    time.sleep(0.5)
    
    # Second wrong attempt
    result = reset_password(TEST_EMAIL, "222222", "NewPass123!")
    
    # Verify response
    if result.get('success') == False:
        error_type = result.get('error_type', '')
        remaining = result.get('remaining_attempts', 0)
        
        if error_type == 'invalid_code' and remaining == 1:
            print_success(f"Correct error type: {error_type}")
            print_success(f"Correct remaining attempts: {remaining}")
            return True
        else:
            print_error(f"Wrong error type or attempts: {error_type}, remaining: {remaining}")
            return False
    else:
        print_error("Should have failed but succeeded!")
        return False

def test_wrong_code_third_attempt():
    """Test 3: Wrong code on third attempt (too many attempts)"""
    print_test("Wrong Code - 3rd Attempt (Too Many)")
    
    # Request code first
    request_reset_code(TEST_EMAIL)
    time.sleep(1)
    
    # Three wrong attempts
    reset_password(TEST_EMAIL, "111111", "NewPass123!")
    time.sleep(0.5)
    reset_password(TEST_EMAIL, "222222", "NewPass123!")
    time.sleep(0.5)
    result = reset_password(TEST_EMAIL, "333333", "NewPass123!")
    
    # Verify response
    if result.get('success') == False:
        error_type = result.get('error_type', '')
        
        if error_type == 'too_many_attempts':
            print_success(f"Correct error type: {error_type}")
            print_success("Code should be invalidated now")
            return True
        else:
            print_error(f"Wrong error type: {error_type}")
            return False
    else:
        print_error("Should have failed but succeeded!")
        return False

def test_correct_code():
    """Test 4: Correct code"""
    print_test("Correct Code")
    
    # Request code first
    result = request_reset_code(TEST_EMAIL)
    
    if not result.get('success'):
        print_error("Failed to request reset code")
        return False
    
    # Get the code from backend logs or use a known test code
    print_info("⚠️  Check backend logs for the actual code")
    print_info("Enter the code from email/logs:")
    actual_code = input("Code: ").strip()
    
    if not actual_code:
        print_error("No code provided, skipping test")
        return False
    
    time.sleep(1)
    
    # Try correct code
    result = reset_password(TEST_EMAIL, actual_code, "NewPass123!")
    
    # Verify response
    if result.get('success') == True:
        print_success("Password reset successful!")
        return True
    else:
        print_error(f"Failed: {result.get('error')}")
        return False

def test_expired_code():
    """Test 5: Expired code (would need to wait 5 minutes)"""
    print_test("Expired Code")
    print_info("⚠️  This test requires waiting 5+ minutes")
    print_info("Skipping for now - test manually if needed")
    return None

def test_no_internet():
    """Test 6: No internet connection"""
    print_test("No Internet Connection")
    print_info("⚠️  This test requires manually turning off internet")
    print_info("Test manually in the app")
    return None

def run_all_tests():
    """Run all automated tests"""
    print_header("🧪 RESET PASSWORD ERROR HANDLING TESTS")
    
    results = []
    
    # Test 1: Wrong code - 1st attempt
    try:
        result = test_wrong_code_first_attempt()
        results.append(("Wrong Code - 1st Attempt", result))
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        results.append(("Wrong Code - 1st Attempt", False))
    
    time.sleep(2)
    
    # Test 2: Wrong code - 2nd attempt
    try:
        result = test_wrong_code_second_attempt()
        results.append(("Wrong Code - 2nd Attempt", result))
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        results.append(("Wrong Code - 2nd Attempt", False))
    
    time.sleep(2)
    
    # Test 3: Wrong code - 3rd attempt
    try:
        result = test_wrong_code_third_attempt()
        results.append(("Wrong Code - 3rd Attempt", result))
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        results.append(("Wrong Code - 3rd Attempt", False))
    
    time.sleep(2)
    
    # Test 4: Correct code (interactive)
    try:
        result = test_correct_code()
        results.append(("Correct Code", result))
    except Exception as e:
        print_error(f"Test failed with exception: {e}")
        results.append(("Correct Code", False))
    
    # Print summary
    print_header("📊 TEST SUMMARY")
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in results:
        if result is True:
            print_success(f"{test_name}: PASSED")
            passed += 1
        elif result is False:
            print_error(f"{test_name}: FAILED")
            failed += 1
        else:
            print_info(f"{test_name}: SKIPPED")
            skipped += 1
    
    print(f"\n{Colors.BOLD}Total: {len(results)} tests{Colors.END}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {failed}{Colors.END}")
    print(f"{Colors.YELLOW}Skipped: {skipped}{Colors.END}")
    
    if failed == 0 and passed > 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.END}")
    elif failed > 0:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ SOME TESTS FAILED{Colors.END}")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n\n{Colors.RED}Fatal error: {e}{Colors.END}")
