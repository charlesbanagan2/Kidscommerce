import sys
sys.path.insert(0, r'C:\Users\mnban\Documents\kids\backend')

from app import app, get_data, update_data

with app.app_context():
    print("Checking for pending restock requests...\n")
    
    # Get all pending restock requests
    pending = get_data('restock_request', filters={'status': 'pending'})
    
    if not pending or len(pending) == 0:
        print("No pending restock requests found. Stock should display correctly.")
    else:
        print(f"Found {len(pending)} pending restock requests:")
        for req in pending:
            print(f"  ID: {req.get('id')} - Product: {req.get('product_id')} - Qty: {req.get('quantity')}")
        
        print("\nThese pending requests cause products to show 0 stock.")
        print("\nOptions:")
        print("1. Approve them (change status to 'approved')")
        print("2. Reject them (change status to 'rejected')")
        print("3. Delete them")
        print("\nType 'approve', 'reject', or 'delete' to fix:")
        
        choice = input().strip().lower()
        
        if choice in ['approve', 'reject', 'delete']:
            for req in pending:
                req_id = req.get('id')
                if choice == 'delete':
                    from app import delete_data_by_id
                    delete_data_by_id('restock_request', req_id)
                    print(f"  Deleted request {req_id}")
                else:
                    new_status = 'approved' if choice == 'approve' else 'rejected'
                    update_data('restock_request', {'id': req_id}, {'status': new_status})
                    print(f"  Updated request {req_id} to {new_status}")
            
            print(f"\nDone! Stock should now display correctly.")
        else:
            print("No action taken.")
