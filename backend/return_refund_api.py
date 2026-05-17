# Return & Refund Mobile API Endpoints
from flask import request, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import json
import traceback
from sqlalchemy import text as sa_text
from sqlalchemy.exc import IntegrityError

def register_return_refund_api(app, db, token_required):
    """Register return and refund API endpoints for mobile app"""

    deps = app.extensions.get('return_refund_deps', {})
    active_db = deps.get('db', db)
    Order = deps.get('Order')
    OrderItem = deps.get('OrderItem')
    ReturnRequest = deps.get('ReturnRequest')
    Product = deps.get('Product')
    push_notification_fn = deps.get('push_notification')
    emit_return_update_fn = deps.get('_emit_return_update')
    force_fix_sequence_fn = deps.get('force_fix_sequence_for_table')
    release_commissions_fn = deps.get('release_commissions')
    release_rider_earning_fn = deps.get('release_rider_earning')
    finalize_rider_earning_after_return_fn = deps.get('finalize_rider_earning_after_return')

    if not all([Order, OrderItem, ReturnRequest, Product]):
        raise RuntimeError(
            'Missing return_refund_deps in app.extensions. '
            'Ensure app.py sets model dependencies before register_return_refund_api().'
        )

    def _parse_media_list(value):
        """Normalize media fields that may be list/json-string/string into a clean list."""
        if not value:
            return []
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            if raw.startswith('['):
                try:
                    decoded = json.loads(raw)
                    if isinstance(decoded, list):
                        return [str(v).strip() for v in decoded if str(v).strip()]
                except Exception:
                    pass
            return [raw]
        return []

    def _safe_video_value(videos):
        """Store video reference in a String(255) column safely."""
        if not videos:
            return None

        cleaned = [str(v).strip() for v in videos if str(v).strip()]
        if not cleaned:
            return None

        # Single URL is preferred and avoids overfilling String(255).
        if len(cleaned) == 1:
            return cleaned[0][:255]

        encoded = json.dumps(cleaned)
        if len(encoded) <= 255:
            return encoded

        # Fallback: keep first URL only when payload is too long.
        return cleaned[0][:255]

    def _sync_return_request_sequence():
        """Repair the return_request id sequence after manual imports or Supabase drift."""
        try:
            if force_fix_sequence_fn:
                return bool(force_fix_sequence_fn('return_request'))

            if 'postgresql' not in str(active_db.engine.url).lower():
                return False

            active_db.session.execute(
                sa_text(
                    "SELECT setval(pg_get_serial_sequence('return_request', 'id'), "
                    "(SELECT COALESCE(MAX(id), 0) FROM return_request) + 1, false)"
                )
            )
            active_db.session.commit()
            return True
        except Exception:
            active_db.session.rollback()
            app.logger.exception("Failed to sync return_request id sequence")
            return False

    def _is_return_request_pk_conflict(error):
        if not isinstance(error, IntegrityError):
            return False

        original = getattr(error, 'orig', None)
        pgcode = getattr(original, 'pgcode', None)
        message = str(original or error).lower()
        return (
            pgcode == '23505'
            and 'return_request_pkey' in message
            and 'duplicate key value' in message
        )

    def _flush_return_request(return_request):
        with active_db.session.begin_nested():
            active_db.session.add(return_request)
            active_db.session.flush()
    
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
            data = request.get_json(silent=True) or {}
            
            # Get order
            order = active_db.session.get(Order, order_id)
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
            images = data.get('images', [])  # List of image URLs
            videos = data.get('videos', [])  # List of video URLs

            if isinstance(images, str):
                images = [images]
            if isinstance(videos, str):
                videos = [videos]

            images = [img for img in images if img]
            videos = [vid for vid in videos if vid]
            
            if not items:
                return jsonify({'success': False, 'error': 'No items selected'}), 400
            
            if not reason:
                return jsonify({'success': False, 'error': 'Reason is required'}), 400

            _sync_return_request_sequence()
            
            # Create return requests for each item
            created_requests = []
            skipped_items = 0
            for item_data in items:
                try:
                    order_item_id = item_data.get('order_item_id')
                    try:
                        order_item_id = int(order_item_id)
                    except (TypeError, ValueError):
                        skipped_items += 1
                        continue

                    try:
                        quantity = int(item_data.get('quantity', 1) or 1)
                    except (TypeError, ValueError):
                        quantity = 1
                    
                    order_item = active_db.session.get(OrderItem, order_item_id)
                    if not order_item or order_item.order_id != order_id:
                        skipped_items += 1
                        continue

                    if quantity < 1:
                        quantity = 1
                    if order_item.quantity and quantity > order_item.quantity:
                        quantity = order_item.quantity

                    product = order_item.product or active_db.session.get(Product, order_item.product_id)
                    if not product:
                        skipped_items += 1
                        continue
                    
                    # Get seller from product
                    seller_id = product.seller_id
                    if not seller_id:
                        skipped_items += 1
                        continue

                    unit_price = float(order_item.price_at_time or 0)
                    
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
                        refund_amount=unit_price * quantity,
                        images=images if images else None,
                        video_filename=_safe_video_value(videos)
                    )

                    _flush_return_request(return_request)
                    created_requests.append(return_request)
                except IntegrityError as item_error:
                    if _is_return_request_pk_conflict(item_error) and not created_requests:
                        active_db.session.rollback()
                        _sync_return_request_sequence()
                        app.logger.warning(
                            "Recovered stale return_request id sequence for order %s; retrying item %s",
                            order_id,
                            item_data,
                        )

                        retry_request = ReturnRequest(
                            order_id=order_id,
                            order_item_id=order_item_id,
                            buyer_id=request.current_user_id,
                            seller_id=seller_id,
                            reason=reason,
                            description=additional_details,
                            quantity=quantity,
                            request_type='return',
                            status='submitted',
                            refund_amount=unit_price * quantity,
                            images=images if images else None,
                            video_filename=_safe_video_value(videos)
                        )
                        try:
                            _flush_return_request(retry_request)
                            created_requests.append(retry_request)
                            continue
                        except Exception as retry_error:
                            item_error = retry_error

                    skipped_items += 1
                    app.logger.exception(
                        "Return request item failed for order %s item payload %s: %s",
                        order_id,
                        item_data,
                        item_error,
                    )
                    continue
                except Exception as item_error:
                    skipped_items += 1
                    app.logger.exception(
                        "Return request item failed for order %s item payload %s: %s",
                        order_id,
                        item_data,
                        item_error,
                    )
                    continue
            
            if not created_requests:
                active_db.session.rollback()
                return jsonify({
                    'success': False,
                    'error': 'No valid order items were found for this return request',
                    'skipped_items': skipped_items,
                }), 400

            order.status = 'return_requested'
            order.updated_at = datetime.utcnow()
            active_db.session.commit()
            
            # Notify sellers
            for rr in created_requests:
                try:
                    if push_notification_fn:
                        push_notification_fn(
                            rr.seller_id,
                            f'New return request for Order #{order_id}',
                            type='return_request',
                            link=f'/seller/returns/{rr.id}'
                        )
                    if emit_return_update_fn:
                        emit_return_update_fn(rr)
                except Exception as e:
                    print(f'Notification error: {e}')
            
            return jsonify({
                'success': True,
                'message': 'Return request submitted successfully',
                'order_status': order.status,
                'return_requests': [{
                    'id': rr.id,
                    'status': rr.status,
                    'created_at': rr.created_at.isoformat()
                } for rr in created_requests]
            })
            
        except Exception as e:
            active_db.session.rollback()
            print(f'Error creating return request: {e}')
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/buyer/return-requests', methods=['GET'])
    @token_required
    def api_get_buyer_return_requests():
        """Get all return requests for buyer"""
        try:
            requests_query = active_db.session.query(ReturnRequest).filter_by(
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
                    'product_name': (
                        rr.order_item.product.name
                        if rr.order_item and rr.order_item.product
                        else (
                            (active_db.session.get(Product, rr.order_item.product_id).name if rr.order_item and active_db.session.get(Product, rr.order_item.product_id) else None)
                        )
                    ),
                    'product_image': (
                        rr.order_item.product.image_filename
                        if rr.order_item and rr.order_item.product
                        else (
                            (active_db.session.get(Product, rr.order_item.product_id).image_filename if rr.order_item and active_db.session.get(Product, rr.order_item.product_id) else None)
                        )
                    ),
                    'images': _parse_media_list(rr.images),
                    'videos': _parse_media_list(rr.video_filename),
                    'seller_response_reason': rr.seller_response_reason,
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
            requests_query = active_db.session.query(ReturnRequest).filter_by(
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
                    'product_name': (
                        rr.order_item.product.name
                        if rr.order_item and rr.order_item.product
                        else (
                            (active_db.session.get(Product, rr.order_item.product_id).name if rr.order_item and active_db.session.get(Product, rr.order_item.product_id) else None)
                        )
                    ),
                    'product_image': (
                        rr.order_item.product.image_filename
                        if rr.order_item and rr.order_item.product
                        else (
                            (active_db.session.get(Product, rr.order_item.product_id).image_filename if rr.order_item and active_db.session.get(Product, rr.order_item.product_id) else None)
                        )
                    ),
                    'images': _parse_media_list(rr.images),
                    'videos': _parse_media_list(rr.video_filename),
                    'seller_response_reason': rr.seller_response_reason
                } for rr in requests_query]
            })
        except Exception as e:
            print(f'Error fetching seller return requests: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/seller/return-requests/<int:return_id>/approve', methods=['POST'])
    @token_required
    def api_seller_approve_return(return_id):
        """Seller approves a return request - item becomes refunded and moves to returns tab."""
        try:
            rr = active_db.session.get(ReturnRequest, return_id)
            if not rr:
                return jsonify({'success': False, 'error': 'Return request not found'}), 404
            
            if rr.seller_id != request.current_user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            if rr.status not in ['submitted', 'seller_reviewing', 'waiting_seller_approval']:
                return jsonify({'success': False, 'error': 'Invalid status'}), 400
            
            # Update return request status and order status per business rule
            rr.status = 'refunded'
            rr.processed_at = datetime.utcnow()
            rr.processed_by = request.current_user_id
            
            # Update order status to refunded
            order = active_db.session.get(Order, rr.order_id)
            if order:
                order.status = 'refunded'
                order.payment_status = 'refunded'
                order.updated_at = datetime.utcnow()
            
            active_db.session.commit()
            rider_earning_released = False
            if order:
                try:
                    if finalize_rider_earning_after_return_fn:
                        rider_earning_released = bool(
                            finalize_rider_earning_after_return_fn(order, True)
                        )
                    elif release_rider_earning_fn:
                        rider_earning_released = bool(release_rider_earning_fn(order))
                except Exception:
                    app.logger.exception(
                        "Failed to release rider earnings for approved return %s",
                        rr.id,
                    )
            
            # Notify buyer
            if push_notification_fn:
                push_notification_fn(
                    rr.buyer_id,
                    f'Your return request for Order #{rr.order_id} has been approved. The item is now refunded.',
                    type='return_approved',
                    link=f'/buyer/orders/{rr.order_id}'
                )
                rider_id = (
                    getattr(order, 'picked_up_by', None)
                    or getattr(order, 'delivered_by', None)
                    or getattr(order, 'rider_id', None)
                )
                if rider_id and rider_earning_released:
                    push_notification_fn(
                        rider_id,
                        f'Order #{rr.order_id} delivery earnings have been released.',
                        type='order',
                        link=f'/rider/orders/{rr.order_id}'
                    )

            if emit_return_update_fn:
                emit_return_update_fn(rr)
            
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
            active_db.session.rollback()
            print(f'Error approving return: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/seller/return-requests/<int:return_id>/reject', methods=['POST'])
    @token_required
    def api_seller_reject_return(return_id):
        """Seller rejects a return request"""
        try:
            data = request.get_json(silent=True) or {}
            rejection_reason = data.get('reason', '').strip()
            
            rr = active_db.session.get(ReturnRequest, return_id)
            if not rr:
                return jsonify({'success': False, 'error': 'Return request not found'}), 404
            
            if rr.seller_id != request.current_user_id:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            if rr.status not in ['submitted', 'seller_reviewing', 'waiting_seller_approval']:
                return jsonify({'success': False, 'error': 'Invalid status'}), 400
            
            # Update status
            rr.status = 'rejected'
            rr.seller_response_reason = rejection_reason
            rr.processed_at = datetime.utcnow()
            rr.processed_by = request.current_user_id

            # Keep order closed as completed on rejection.
            order = active_db.session.get(Order, rr.order_id)
            if order and order.status != 'completed':
                order.status = 'completed'
                order.updated_at = datetime.utcnow()

            active_db.session.commit()
            if order:
                try:
                    if finalize_rider_earning_after_return_fn:
                        finalize_rider_earning_after_return_fn(order, False)
                    elif release_commissions_fn:
                        release_commissions_fn(order)
                except Exception:
                    app.logger.exception(
                        "Failed to release commissions for rejected return %s",
                        rr.id,
                    )
            
            # Notify buyer
            if push_notification_fn:
                push_notification_fn(
                    rr.buyer_id,
                    f'Your return request for Order #{rr.order_id} was rejected',
                    type='return_rejected',
                    link=f'/buyer/orders/{rr.order_id}'
                )
                rider_id = (
                    getattr(order, 'picked_up_by', None)
                    or getattr(order, 'delivered_by', None)
                    or getattr(order, 'rider_id', None)
                )
                if rider_id:
                    push_notification_fn(
                        rider_id,
                        f'Order #{rr.order_id} completed. Your delivery earnings have been released.',
                        type='order',
                        link=f'/rider/orders/{rr.order_id}'
                    )

            if emit_return_update_fn:
                emit_return_update_fn(rr)
            
            return jsonify({
                'success': True,
                'message': 'Return request rejected',
                'return_request': {
                    'id': rr.id,
                    'status': rr.status
                }
            })
        except Exception as e:
            active_db.session.rollback()
            print(f'Error rejecting return: {e}')
            return jsonify({'success': False, 'error': str(e)}), 500
    
    print("[OK] Return & Refund API registered")
