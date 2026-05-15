# Notification API Endpoints

from flask import Blueprint, request, jsonify, session, current_app
from functools import wraps
import logging

logger = logging.getLogger(__name__)

notification_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@notification_bp.route('/', methods=['GET'])
@login_required
def get_notifications():
    """Get all notifications for current user"""
    from extensions import db
    from notification_service import Notification
    
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    active_role = session.get('active_role')
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    with current_app.app_context():
        if user_role:
            query = Notification.query.filter_by(user_id=user_id, user_role=user_role)
        elif active_role:
            query = Notification.query.filter_by(user_id=user_id, user_role=active_role)
        else:
            query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        query = query.order_by(Notification.created_at.desc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        unread = Notification.query.filter_by(user_id=user_id, is_read=False).count()
        
        return jsonify({
            'notifications': [n.to_dict() for n in paginated.items],
            'total': paginated.total,
            'page': page,
            'per_page': per_page,
            'pages': paginated.pages,
            'unread_count': unread
        })

@notification_bp.route('/unread-count', methods=['GET'])
@login_required
def get_unread_count():
    """Get unread notification count"""
    from extensions import db
    from notification_service import Notification
    
    user_id = session.get('user_id')
    with current_app.app_context():
        count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    return jsonify({'unread_count': count})

@notification_bp.route('/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark single notification as read"""
    from extensions import db
    from notification_service import Notification
    
    user_id = session.get('user_id')
    with current_app.app_context():
        notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notif:
            notif.is_read = True
            db.session.commit()
            return jsonify({'success': True, 'message': 'Notification marked as read'})
    return jsonify({'success': False, 'error': 'Notification not found'}), 404

@notification_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Mark all notifications as read"""
    from extensions import db
    from notification_service import Notification
    
    user_id = session.get('user_id')
    with current_app.app_context():
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
    return jsonify({'success': True, 'message': 'All notifications marked as read'})

@notification_bp.route('/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    """Delete a notification"""
    from extensions import db
    from notification_service import Notification
    
    user_id = session.get('user_id')
    with current_app.app_context():
        notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notif:
            db.session.delete(notif)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Notification deleted'})
    return jsonify({'success': False, 'error': 'Notification not found'}), 404

@notification_bp.route('/mobile', methods=['GET'])
def get_mobile_notifications():
    """Get notifications for mobile app (JWT auth)"""
    from flask import g
    from extensions import db
    from notification_service import Notification
    
    if not hasattr(g, 'current_user'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = g.current_user['id']
    user_role = g.current_user['role']
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    with current_app.app_context():
        query = Notification.query.filter_by(user_id=user_id, user_role=user_role)
        query = query.order_by(Notification.created_at.desc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        unread = Notification.query.filter_by(user_id=user_id, is_read=False).count()
        
        return jsonify({
            'success': True,
            'notifications': [n.to_dict() for n in paginated.items],
            'total': paginated.total,
            'unread_count': unread
        })

@notification_bp.route('/mobile/<int:notification_id>/read', methods=['POST'])
def mark_mobile_notification_read(notification_id):
    """Mark notification as read (mobile)"""
    from flask import g
    from extensions import db
    from notification_service import Notification
    
    if not hasattr(g, 'current_user'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = g.current_user['id']
    with current_app.app_context():
        notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notif:
            notif.is_read = True
            db.session.commit()
            return jsonify({'success': True})
    return jsonify({'success': False}), 404
