# Return & Refund Mobile API Endpoints
from flask import request, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import json

def register_return_refund_api(app, db, token_required):
    """Register return and refund API endpoints for mobile app"""
    
    from app import (
        Order, OrderItem, ReturnRequest, User, Product, 
        push_notification, socketio, _emit_return_update
    )
    
    @app.route('/api/return-evidence/upload', methods=['POST'])
    @token_required
    def api_upload_return_evidence():
        """Upload return evidence (images/videos)"""
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            
            if file_ext not in allowed_extensions:
                return jsonify({'success': False, 'error': 'Invalid file type'}), 400
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            unique_filename = timestamp + filename
            
            # Create upload directory if not exists
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'returns')
            os.makedirs(upload_path, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            # Return URL
            file_url = f'/static/uploads/returns/{unique_filename}'
            
            return jsonify({
                'success': True,
                'url': file_url,
                'filename': unique_filename
            })
            
        except Exception as e:
            print(f'Error uploading return evidence: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/buyer/orders/<int:order_id>/return-request', methods=['POST'])
    @token_required
    def api_create_return_request(order_id):
        """Buyer creates a return/refund request"""
        try:
            data = request.get_json() or {}
            
            # Get order
            order = Order.query.get(order_id)
            if not order:
                return jsonify({'success': False, 'error': 'Order not found'}), 404
            
            # Verify buyer owns this order
            if order.buyer_id != request.current_user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            # Check if order is eligible for return (delivered or completed)
            if order.status not in ['delivered', 'completed']:
                return jsonify({
                    'success': False, 
                    'error': 'Only delivered or completed orders can be returned'
                }), 400
            
            # Get request data
            items = data.get('items', [])  # [{order_item_id, quantity, reason}]
            reason = data.get('reason', '').strip()
            additional_details = data.get('additional_details', '').strip()
            refund_method = data.get('refund_method', 'original')
            images = data.get('images', [])  # List of image URLs
            
            if not items:
                return jsonify({'success': False, 'error': 'No items selected'}), 400
            
            if not reason:
                return jsonify({'success': False, 'error': 'Reason is required'}), 400
            
            # Create return requests for each item
            created_requests = []
            for item_data in items:
                order_item_id = item_data.get('order_item_id')
                quantity = item_data.get('quantity', 1)
                
                order_item = OrderItem.query.get(order_item_id)
                if not order_item or order_item.order_id != order_id:
                    continue
                
                # Get seller from product
                seller_id = order_item.product.seller_id
                
                # Create return request
                return_request = ReturnRequest(
                    order_id=order_id,
                    order_item_id=order_item_id,
                    buyer_id=request.current_user_id,
                    seller_id=seller_id,
                    reason=reason,
                    description=additional_details,
                    quantity=quantity,
                    request_type='return',
                    status='submitted',
                    refund_amount=order_item.price_at_time * quantity,
                    images=json.dumps(images) if images else None
                )
                
                db.session.add(return_request)
                created_requests.append(return_request)
            
            db.session.commit()
            
            # Notify sellers
            for rr in created_requests:
                try:
                    push_notification(
                        rr.seller_id,
                        f'New return request for Order #{order_id}',
                        type='return_request',
                        link=f'/seller/returns/{rr.id}'
                    )
                    _emit_return_update(rr)
                except Exception as e:
                    print(f'Notification error: {e}')
            
            return jsonify({
                'success': True,
                'message': 'Return request submitted successfully',
                'return_requests': [{
                    'id': rr.id,
                    'status': rr.status,
                    'created_at': rr.created_at.isoformat()
                } for rr in created_requests]
            })
            
        except Exception as e:
            db.session.rollback()
            print(f'Error creating return request: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/buyer/return-requests', methods=['GET'])
    @token_required
    def api_get_buyer_return_requests():
        """Get all return requests for buyer"""
        try:
            requests_query = ReturnRequest.query.filter_by(
                buyer_id=request.current_user_id
            ).order_by(ReturnRequest.created_at.desc()).all()
            
            return jsonify({
                'success': True,
                'return_requests': [{
                    'id': rr.id,
                    'order_id': rr.order_id,
                    'reason': rr.reason,
                    'description': rr.description,
                    'quantity': rr.quantity,
                    'status': rr.status,
                    'refund_amount': float(rr.refund_amount) if rr.refund_amount else 0,
                    'created_at': rr.created_at.isoformat(),
                    'product_name': rr.order_item.product.name if rr.order_item else None,
                    'product_image': rr.order_item.product.image_filename if rr.order_item else None,
                    'images': json.loads(rr.images) if rr.images else []
                } for rr in requests_query]
            })
        except Exception as e:
            print(f'Error fetching return requests: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/seller/return-requests', methods=['GET'])
    @token_required
    def api_get_seller_return_requests():
        """Get all return requests for seller"""
        try:
            requests_query = ReturnRequest.query.filter_by(
                seller_id=request.current_user_id
            ).order_by(ReturnRequest.created_at.desc()).all()
            
            return jsonify({
                'success': True,
                'return_requests': [{
                    'id': rr.id,
                    'order_id': rr.order_id,
                    'buyer_name': f"{rr.buyer.first_name} {rr.buyer.last_name}",
                    'reason': rr.reason,
                    'description': rr.description,
                    'quantity': rr.quantity,
                    'status': rr.status,
                    'refund_amount': float(rr.refund_amount) if rr.refund_amount else 0,
                    'created_at': rr.created_at.isoformat(),
                    'product_name': rr.order_item.product.name if rr.order_item else None,
                    'product_image': rr.order_item.product.image_filename if rr.order_item else None,
                    'images': json.loads(rr.images) if rr.images else [],
                    'seller_response_reason': rr.seller_response_reason
                } for rr in requests_query]
            })
        except Exception as e:
            print(f'Error fetching seller return requests: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/seller/return-requests/<int:return_id>/approve', methods=['POST'])
    @token_required
    def api_seller_approve_return(return_id):
        """Seller approves a return request - item becomes refunded and moves to returns tab"""
        try:
            rr = ReturnRequest.query.get(return_id)
            if not rr:
                return jsonify({'success': False, 'error': 'Return request not found'}), 404
            
            if rr.seller_id != request.current_user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            if rr.status != 'submitted':
                return jsonify({'success': False, 'error': 'Invalid status'}), 400
            
            # Update return request status to approved
            rr.status = 'approved'
            rr.processed_at = datetime.utcnow()
            rr.processed_by = request.current_user_id
            
            # Update order status to refunded
            order = Order.query.get(rr.order_id)
            if order:
                order.status = 'refunded'
                order.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # Notify buyer
            push_notification(
                rr.buyer_id,
                f'Your return request for Order #{rr.order_id} has been approved. The item is now refunded.',
                type='return_approved',
                link=f'/buyer/orders/{rr.order_id}'
            )
            
            _emit_return_update(rr)
            
            return jsonify({
                'success': True,
                'message': 'Return request approved. Item is now refunded.',
                'return_request': {
                    'id': rr.id,
                    'status': rr.status,
                    'order_status': 'refunded'
                }
            })
        except Exception as e:
            db.session.rollback()
            print(f'Error approving return: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/seller/return-requests/<int:return_id>/reject', methods=['POST'])
    @token_required
    def api_seller_reject_return(return_id):
        """Seller rejects a return request"""
        try:
            data = request.get_json() or {}
            rejection_reason = data.get('reason', '').strip()
            
            rr = ReturnRequest.query.get(return_id)
            if not rr:
                return jsonify({'success': False, 'error': 'Return request not found'}), 404
            
            if rr.seller_id != request.current_user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            if rr.status != 'submitted':
                return jsonify({'success': False, 'error': 'Invalid status'}), 400
            
            # Update status
            rr.status = 'rejected'
            rr.seller_response_reason = rejection_reason
            rr.processed_at = datetime.utcnow()
            rr.processed_by = request.current_user_id
            db.session.commit()
            
            # Notify buyer
            push_notification(
                rr.buyer_id,
                f'Your return request for Order #{rr.order_id} was rejected',
                type='return_rejected',
                link=f'/buyer/orders/{rr.order_id}'
            )
            
            _emit_return_update(rr)
            
            return jsonify({
                'success': True,
                'message': 'Return request rejected',
                'return_request': {
                    'id': rr.id,
                    'status': rr.status
                }
            })
        except Exception as e:
            db.session.rollback()
            print(f'Error rejecting return: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500
    
    print("[OK] Return & Refund API registered")
