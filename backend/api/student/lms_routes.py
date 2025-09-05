from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.auth_service import get_user_by_id
from backend.services.lms_activity_service import lms_activity_service
from backend.middleware.auth_middleware import student_required
from backend.utils.api import api_response, error_response
from backend.models import Enrollment, CourseOffering
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

lms_bp = Blueprint('lms', __name__, url_prefix='/api/student/lms')

@lms_bp.route('/track/page', methods=['POST'])
@jwt_required()
@student_required
def track_page_view():
    """Track a page view"""
    try:
        data = request.get_json()
        
        # Get user info
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        # Get required data
        page_url = data.get('page_url')
        page_title = data.get('page_title')
        course_id = data.get('course_id')
        
        if not page_url:
            return error_response('Page URL is required', 400)
        
        # Get user agent and IP
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')[:255]  # Limit to 255 chars
        
        # Get enrollment if course_id provided
        enrollment_id = None
        if course_id:
            enrollment = Enrollment.query.filter_by(
                student_id=user.student.student_id,
                enrollment_status='enrolled'
            ).join(
                CourseOffering
            ).filter(
                CourseOffering.course_id == course_id
            ).first()
            
            if enrollment:
                enrollment_id = enrollment.enrollment_id
        
        # If no specific enrollment, track for all active enrollments
        if not enrollment_id:
            # Get any active enrollment for general tracking
            enrollment = Enrollment.query.filter_by(
                student_id=user.student.student_id,
                enrollment_status='enrolled'
            ).first()
            
            if enrollment:
                enrollment_id = enrollment.enrollment_id
        
        if enrollment_id:
            # Track the activity
            activity = lms_activity_service.track_page_view(
                enrollment_id=enrollment_id,
                page_url=page_url,
                page_title=page_title,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            logger.info(f"Tracked page view for student {user.student.student_id}: {page_url}")
            
            return api_response({
                'activity_id': activity.activity_id,
                'tracked': True
            }, 'Page view tracked successfully')
        else:
            return api_response({
                'tracked': False,
                'message': 'No active enrollment found'
            }, 'No active enrollment to track')
        
    except Exception as e:
        logger.error(f"Error tracking page view: {str(e)}")
        return error_response('Failed to track page view', 500)

@lms_bp.route('/track/resource', methods=['POST'])
@jwt_required()
@student_required
def track_resource_view():
    """Track viewing of a resource"""
    try:
        data = request.get_json()
        
        # Get user info
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        # Get required data
        resource_id = data.get('resource_id')
        resource_name = data.get('resource_name')
        resource_type = data.get('resource_type', 'document')
        course_id = data.get('course_id')
        
        if not resource_id or not resource_name:
            return error_response('Resource ID and name are required', 400)
        
        # Get enrollment
        enrollment = None
        if course_id:
            enrollment = Enrollment.query.filter_by(
                student_id=user.student.student_id,
                enrollment_status='enrolled'
            ).join(
                CourseOffering
            ).filter(
                CourseOffering.course_id == course_id
            ).first()
        
        if not enrollment:
            # Get any active enrollment
            enrollment = Enrollment.query.filter_by(
                student_id=user.student.student_id,
                enrollment_status='enrolled'
            ).first()
        
        if not enrollment:
            return error_response('No active enrollment found', 404)
        
        # Track the activity
        activity = lms_activity_service.track_resource_view(
            enrollment_id=enrollment.enrollment_id,
            resource_id=str(resource_id),
            resource_name=resource_name,
            resource_type=resource_type,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:255]
        )
        
        return api_response({
            'activity_id': activity.activity_id,
            'tracked': True
        }, 'Resource view tracked successfully')
        
    except Exception as e:
        logger.error(f"Error tracking resource view: {str(e)}")
        return error_response('Failed to track resource view', 500)

@lms_bp.route('/track/assessment', methods=['POST'])
@jwt_required()
@student_required
def track_assessment_view():
    """Track viewing of an assessment"""
    try:
        data = request.get_json()
        
        # Get user info
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        # Get required data
        assessment_id = data.get('assessment_id')
        assessment_name = data.get('assessment_name')
        offering_id = data.get('offering_id')
        
        if not assessment_id or not assessment_name:
            return error_response('Assessment ID and name are required', 400)
        
        # Get enrollment
        enrollment = None
        if offering_id:
            enrollment = Enrollment.query.filter_by(
                student_id=user.student.student_id,
                offering_id=offering_id,
                enrollment_status='enrolled'
            ).first()
        
        if not enrollment:
            # Try to find by any active enrollment
            enrollment = Enrollment.query.filter_by(
                student_id=user.student.student_id,
                enrollment_status='enrolled'
            ).first()
        
        if not enrollment:
            return error_response('No active enrollment found', 404)
        
        # Track the activity
        activity = lms_activity_service.track_assessment_view(
            enrollment_id=enrollment.enrollment_id,
            assessment_id=assessment_id,
            assessment_name=assessment_name,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:255]
        )
        
        return api_response({
            'activity_id': activity.activity_id,
            'tracked': True
        }, 'Assessment view tracked successfully')
        
    except Exception as e:
        logger.error(f"Error tracking assessment view: {str(e)}")
        return error_response('Failed to track assessment view', 500)

@lms_bp.route('/session/end', methods=['POST'])
@jwt_required()
@student_required
def end_session():
    """End the current LMS session"""
    try:
        # Get user info
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        # End sessions for all active enrollments
        enrollments = Enrollment.query.filter_by(
            student_id=user.student.student_id,
            enrollment_status='enrolled'
        ).all()
        
        ended_count = 0
        for enrollment in enrollments:
            if lms_activity_service.end_session(enrollment.enrollment_id):
                ended_count += 1
        
        return api_response({
            'sessions_ended': ended_count
        }, f'Ended {ended_count} active sessions')
        
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        return error_response('Failed to end session', 500)

@lms_bp.route('/activities', methods=['GET'])
@jwt_required()
@student_required
def get_activities():
    """Get recent activities for the student"""
    try:
        # Get user info
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        # Get query parameters
        course_id = request.args.get('course_id')
        limit = request.args.get('limit', 50, type=int)
        
        # Get enrollment
        if course_id:
            enrollment = Enrollment.query.filter_by(
                student_id=user.student.student_id,
                enrollment_status='enrolled'
            ).join(
                CourseOffering
            ).filter(
                CourseOffering.course_id == course_id
            ).first()
            
            if enrollment:
                activities = lms_activity_service.get_enrollment_activities(
                    enrollment.enrollment_id, limit
                )
            else:
                activities = []
        else:
            # Get activities from all enrollments
            activities = []
            enrollments = Enrollment.query.filter_by(
                student_id=user.student.student_id,
                enrollment_status='enrolled'
            ).all()
            
            for enrollment in enrollments:
                enrollment_activities = lms_activity_service.get_enrollment_activities(
                    enrollment.enrollment_id, limit // len(enrollments) if enrollments else limit
                )
                activities.extend(enrollment_activities)
        
        return api_response({
            'activities': activities,
            'count': len(activities)
        }, 'Activities retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting activities: {str(e)}")
        return error_response('Failed to get activities', 500)