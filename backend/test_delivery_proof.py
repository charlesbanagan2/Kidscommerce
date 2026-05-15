"""
Test script to add delivery proof to an existing order
"""
from app import app, db
from models import Order
from datetime import datetime

def add_delivery_proof_to_order(order_id, proof_photo_filename):
    """Add delivery proof photo to an order"""
    with app.app_context():
        order = Order.query.get(order_id)
        
        if not order:
            print(f"❌ Order #{order_id} not found")
            return False
        
        # Update order with delivery proof
        order.proof_photo_url = proof_photo_filename
        order.status = 'completed'  # Set to completed since delivery proof is uploaded
        
        db.session.commit()
        
        print(f"✅ Added delivery proof to Order #{order_id}")
        print(f"   Photo: {proof_photo_filename}")
        print(f"   Status: {order.status}")
        return True

def list_recent_orders():
    """List recent orders to choose from"""
    with app.app_context():
        orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        
        print("\n📦 Recent Orders:")
        print("-" * 80)
        for order in orders:
            buyer_name = f"{order.buyer.first_name} {order.buyer.last_name}" if order.buyer else "Unknown"
            proof_status = "✅ Has proof" if order.proof_photo_url else "❌ No proof"
            print(f"Order #{order.id:3d} | {buyer_name:20s} | Status: {order.status:12s} | {proof_status}")
        print("-" * 80)

if __name__ == "__main__":
    print("🧪 Delivery Proof Test Script")
    print("=" * 80)
    
    # List recent orders
    list_recent_orders()
    
    # Example: Add delivery proof to order #1
    # You can use any image from static/uploads/delivery_proofs/
    # Or use a test image
    
    print("\n📝 To add delivery proof to an order:")
    print("   1. Upload a photo to: backend/static/uploads/delivery_proofs/")
    print("   2. Run: add_delivery_proof_to_order(ORDER_ID, 'delivery_proofs/photo.jpg')")
    print("\nExample:")
    print("   add_delivery_proof_to_order(1, 'delivery_proofs/test_delivery.jpg')")
    
    # Uncomment and modify this line to test:
    # add_delivery_proof_to_order(1, 'delivery_proofs/test_delivery.jpg')
