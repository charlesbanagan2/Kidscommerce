"""
Add delivery_fee column to Order table
Rider earnings = delivery_fee (based on province)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Order
from sqlalchemy import text

def add_delivery_fee_column():
    """Add delivery_fee column to order table"""
    print("\n" + "="*70)
    print("  ADDING DELIVERY_FEE COLUMN TO ORDER TABLE")
    print("="*70)
    
    with app.app_context():
        try:
            # Check if column exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('order')]
            
            if 'delivery_fee' in columns:
                print("\n(!) delivery_fee column already exists")
                return True
            
            print("\n(+) Adding delivery_fee column...")
            
            # Add column using raw SQL
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE "order" ADD COLUMN delivery_fee FLOAT DEFAULT 36.0'))
                conn.commit()
            
            print("(+) delivery_fee column added successfully!")
            print("    Default value: 36.0 (Laguna base rate)")
            
            return True
            
        except Exception as e:
            print(f"\n(-) Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def update_existing_orders():
    """Update existing orders with delivery_fee based on shipping_address"""
    print("\n" + "="*70)
    print("  UPDATING EXISTING ORDERS WITH DELIVERY FEE")
    print("="*70)
    
    with app.app_context():
        try:
            from province_delivery_fees import calculate_delivery_fee, PROVINCE_RANKS
            
            orders = Order.query.all()
            print(f"\n(+) Found {len(orders)} orders to update")
            
            updated_count = 0
            for order in orders:
                # Extract province from shipping address
                province = None
                if order.shipping_address:
                    address_lower = order.shipping_address.lower()
                    for prov in PROVINCE_RANKS.keys():
                        if prov.lower() in address_lower:
                            province = prov
                            break
                
                # Calculate delivery fee
                if province:
                    delivery_fee = calculate_delivery_fee(province)
                else:
                    delivery_fee = 36.0  # Default to Laguna
                
                # Update order
                order.delivery_fee = delivery_fee
                
                # Update rider_earnings to match delivery_fee
                if order.picked_up_by:
                    order.rider_earnings = delivery_fee
                
                updated_count += 1
                
                if updated_count % 10 == 0:
                    print(f"  Updated {updated_count} orders...")
            
            db.session.commit()
            print(f"\n(+) Successfully updated {updated_count} orders!")
            
            # Show sample
            print("\nSample Updated Orders:")
            sample_orders = Order.query.limit(5).all()
            for order in sample_orders:
                print(f"  Order #{order.id}: delivery_fee=P{order.delivery_fee:.2f}, rider_earnings=P{order.rider_earnings:.2f}")
            
            return True
            
        except Exception as e:
            print(f"\n(-) Error: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

def main():
    print("\n" + "="*70)
    print("  DELIVERY FEE MIGRATION")
    print("="*70)
    
    # Step 1: Add column
    if not add_delivery_fee_column():
        print("\n(-) Failed to add delivery_fee column")
        return
    
    # Step 2: Update existing orders
    if not update_existing_orders():
        print("\n(-) Failed to update existing orders")
        return
    
    print("\n" + "="*70)
    print("  MIGRATION COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nNext steps:")
    print("1. Update app.py to use delivery_fee instead of RIDER_EARNING_RATE")
    print("2. Rider earnings = delivery_fee (province-based)")
    print("3. Test the new earnings calculation")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
