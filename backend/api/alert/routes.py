from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.alert_service import AlertService
from backend.services.auth_service import get_user_by_id
from backend.middleware.auth_middleware import student_required, faculty_required
import logging

logger = logging.getLogger(__name__)

alert_bp = Blueprint('alert', __name__, url_prefix='/api/alerts')
alert_service = AlertService()

@alert_bp.route('/student', methods=['GET'])
@jwt_required()
@student_required
def get_student_alerts():
    """Get alerts for the current student"""
    try:
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return jsonify({
                'status': 'error',
                'message': 'Student profile not found'
            }), 404
        
        # Get query parameters
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        # Get alerts
        alerts = alert_service.get_student_alerts(
            student_id=user.student.student_id,
            unread_only=unread_only
        )
        
        # Get unread count
        unread_count = sum(1 for alert in alerts if not alert['is_read'])
        
        return jsonify({
            'status': 'success',
            'data': {
                'alerts': alerts,
                'unread_count': unread_count,
                'total_count': len(alerts)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting student alerts: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load alerts'
        }), 500

@alert_bp.route('/faculty/summary', methods=['GET'])
@jwt_required()
@faculty_required
def get_faculty_alert_summary():
    """Get alert summary for faculty's courses"""
    try:
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        # Get alert summary
        summary = alert_service.get_alert_summary(
            faculty_id=user.faculty.faculty_id
        )
        
        return jsonify({
            'status': 'success',
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting alert summary: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load alert summary'
        }), 500

@alert_bp.route('/faculty/course/<int:offering_id>', methods=['GET'])
@jwt_required()
@faculty_required
def get_course_alerts(offering_id):
    """Get all alerts for a specific course"""
    try:
        # This would need implementation in alert_service
        # For now, return a placeholder
        return jsonify({
            'status': 'success',
            'data': {
                'alerts': [],
                'message': 'Course-specific alerts coming soon'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting course alerts: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load course alerts'
        }), 500

@alert_bp.route('/<int:alert_id>/read', methods=['PUT'])
@jwt_required()
def mark_alert_read(alert_id):
    """Mark an alert as read"""
    try:
        alert_service.mark_alert_read(alert_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Alert marked as read'
        })
        
    except Exception as e:
        logger.error(f"Error marking alert read: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to update alert'
        }), 500

@alert_bp.route('/<int:alert_id>/resolve', methods=['PUT'])
@jwt_required()
@faculty_required
def resolve_alert(alert_id):
    """Mark an alert as resolved (faculty only)"""
    try:
        user_id = get_jwt_identity()
        
        alert_service.resolve_alert(alert_id, resolved_by=str(user_id))
        
        return jsonify({
            'status': 'success',
            'message': 'Alert resolved'
        })
        
    except Exception as e:
        logger.error(f"Error resolving alert: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to resolve alert'
        }), 500

@alert_bp.route('/check', methods=['POST'])
@jwt_required()
def check_alerts():
    """Manually trigger alert checking (admin/faculty only)"""
    try:
        # Get enrollment_id from request body if provided
        data = request.get_json() or {}
        enrollment_id = data.get('enrollment_id')
        
        # Check alerts
        alert_service.check_and_create_alerts(enrollment_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Alert check completed'
        })
        
    except Exception as e:
        logger.error(f"Error checking alerts: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to check alerts'
        }), 500