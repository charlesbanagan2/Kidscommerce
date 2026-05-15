"""
RIDER SYSTEM - AUTOMATED SETUP SCRIPT
Run this script to automatically set up the complete rider system
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(text)
    print("="*60)

def print_step(step_num, text):
    print(f"\n[{step_num}/5] {text}")

def run_command(cmd, description):
    print(f"   Running: {description}...")
    result = os.system(cmd)
    if result == 0:
        print(f"   ✅ {description} completed")
        return True
    else:
        print(f"   ❌ {description} failed")
        return False

def setup_database():
    """Step 1: Setup database"""
    print_step(1, "Setting up database")
    
    try:
        from app import app, db
        from sqlalchemy import text
        
        with app.app_context():
            # Check if columns exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('order')]
            
            required_columns = [
                'rider_id', 'picked_up_at', 'picked_up_by',
                'delivered_at', 'delivered_by', 'rider_earnings'
            ]
            
            missing = [col for col in required_columns if col not in columns]
            
            if missing:
                print(f"   Adding missing columns: {missing}")
                
                migrations = {
                    'rider_id': "ALTER TABLE `order` ADD COLUMN rider_id INTEGER NULL",
                    'picked_up_at': "ALTER TABLE `order` ADD COLUMN picked_up_at DATETIME NULL",
                    'picked_up_by': "ALTER TABLE `order` ADD COLUMN picked_up_by INTEGER NULL",
                    'delivered_at': "ALTER TABLE `order` ADD COLUMN delivered_at DATETIME NULL",
                    'delivered_by': "ALTER TABLE `order` ADD COLUMN delivered_by INTEGER NULL",
                    'rider_earnings': "ALTER TABLE `order` ADD COLUMN rider_earnings FLOAT DEFAULT 0.0"
                }
                
                for col in missing:
                    if col in migrations:
                        try:
                            db.session.execute(text(migrations[col]))
                            print(f"   ✅ Added column: {col}")
                        except Exception as e:
                            print(f"   ⚠️  Column {col}: {str(e)}")
                
                db.session.commit()
                print("   ✅ Database migration completed")
            else:
                print("   ✅ All columns already exist")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database setup failed: {str(e)}")
        return False

def integrate_backend():
    """Step 2: Integrate backend API"""
    print_step(2, "Integrating backend API")
    
    try:
        app_py_path = Path('app.py')
        
        if not app_py_path.exists():
            print("   ❌ app.py not found")
            return False
        
        # Read app.py
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already integrated
        if 'rider_complete_api' in content or 'api/rider/available-orders' in content:
            print("   ✅ Rider API already integrated")
            return True
        
        # Find insertion point (before if __name__ == '__main__')
        if "if __name__ == '__main__':" in content:
            parts = content.split("if __name__ == '__main__':")
            
            integration_code = """

# ============================================
# RIDER API INTEGRATION
# ============================================
try:
    exec(open('rider_complete_api.py').read())
    print("✅ Rider API loaded successfully")
except Exception as e:
    print(f"⚠️  Rider API load error: {e}")

"""
            
            new_content = parts[0] + integration_code + "if __name__ == '__main__':" + parts[1]
            
            # Backup original
            backup_path = app_py_path.with_suffix('.py.backup_rider')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ Backup created: {backup_path}")
            
            # Write new content
            with open(app_py_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("   ✅ Rider API integrated into app.py")
            return True
        else:
            print("   ⚠️  Could not find insertion point in app.py")
            print("   Please manually add: exec(open('rider_complete_api.py').read())")
            return False
        
    except Exception as e:
        print(f"   ❌ Backend integration failed: {str(e)}")
        return False

def create_test_data():
    """Step 3: Create test data"""
    print_step(3, "Creating test data")
    
    try:
        from app import app, db, User, Order, OrderItem, Product
        from datetime import datetime
        
        with app.app_context():
            # Create test rider
            rider = User.query.filter_by(email='test.rider@example.com').first()
            if not rider:
                rider = User(
                    email='test.rider@example.com',
                    password='password123',
                    first_name='Test',
                    last_name='Rider',
                    role='rider',
                    status='approved',
                    phone='09123456789'
                )
                db.session.add(rider)
                db.session.commit()
                print(f"   ✅ Test rider created (ID: {rider.id})")
                print(f"      Email: test.rider@example.com")
                print(f"      Password: password123")
            else:
                print(f"   ✅ Test rider exists (ID: {rider.id})")
            
            # Create test buyer
            buyer = User.query.filter_by(email='test.buyer@example.com').first()
            if not buyer:
                buyer = User(
                    email='test.buyer@example.com',
                    password='password123',
                    first_name='Test',
                    last_name='Buyer',
                    role='buyer',
                    status='approved',
                    phone='09987654321'
                )
                db.session.add(buyer)
                db.session.commit()
                print(f"   ✅ Test buyer created (ID: {buyer.id})")
            else:
                print(f"   ✅ Test buyer exists (ID: {buyer.id})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test data creation failed: {str(e)}")
        return False

def run_tests():
    """Step 4: Run tests"""
    print_step(4, "Running tests")
    
    return run_command(
        'python test_rider_system.py',
        'Rider system tests'
    )

def print_summary():
    """Step 5: Print summary"""
    print_step(5, "Setup Complete!")
    
    print("\n" + "="*60)
    print("🎉 RIDER SYSTEM SETUP COMPLETED!")
    print("="*60)
    
    print("\n📋 NEXT STEPS:")
    print("\n1. Start the backend server:")
    print("   python app.py")
    
    print("\n2. Test the API endpoints:")
    print("   curl http://localhost:5000/api/health")
    
    print("\n3. Login credentials:")
    print("   Email: test.rider@example.com")
    print("   Password: password123")
    
    print("\n4. Mobile app setup:")
    print("   cd mobile_app")
    print("   flutter pub get")
    print("   flutter run")
    
    print("\n5. Test FCFS order acceptance:")
    print("   - Create order as buyer")
    print("   - Seller marks as ready_for_pickup")
    print("   - Rider accepts order")
    print("   - Try accepting with another rider (should fail)")
    
    print("\n📚 Documentation:")
    print("   - RIDER_COMPLETE_INTEGRATION.md - Full integration guide")
    print("   - RIDER_COMPLETE_SUMMARY.md - Feature summary")
    print("   - test_rider_system.py - Test script")
    
    print("\n✅ All features implemented:")
    print("   ✓ Real-time order notifications")
    print("   ✓ FCFS order acceptance")
    print("   ✓ Earnings tracking")
    print("   ✓ Database integration")
    print("   ✓ QR code verification")
    print("   ✓ Socket.IO real-time updates")
    
    print("\n" + "="*60)

def main():
    print_header("RIDER SYSTEM - AUTOMATED SETUP")
    print("This script will set up the complete rider system")
    print("Estimated time: 5 minutes")
    
    # Change to backend directory
    if not os.path.exists('app.py'):
        print("\n❌ Error: app.py not found")
        print("Please run this script from the backend directory")
        sys.exit(1)
    
    # Run setup steps
    steps = [
        ("Database Setup", setup_database),
        ("Backend Integration", integrate_backend),
        ("Test Data Creation", create_test_data),
        ("Run Tests", run_tests),
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"\n❌ Error in {step_name}: {str(e)}")
            results.append((step_name, False))
    
    # Print results
    print("\n" + "="*60)
    print("SETUP RESULTS")
    print("="*60)
    
    for step_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {step_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print_summary()
    else:
        print("\n❌ Some steps failed. Please check the errors above.")
        print("You can run individual steps manually:")
        print("  1. python add_rider_columns.py")
        print("  2. Manually integrate rider_complete_api.py")
        print("  3. python test_rider_system.py")

if __name__ == '__main__':
    main()
