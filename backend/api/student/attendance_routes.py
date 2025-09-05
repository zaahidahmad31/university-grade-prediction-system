# backend/api/student/attendance_routes.py - FIXED VERSION
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.attendance_service import attendance_service
from backend.services.auth_service import get_user_by_id
from backend.middleware.auth_middleware import student_required
from backend.utils.api import api_response, error_response
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)

# Create blueprint
student_attendance_bp = Blueprint('student_attendance', __name__, url_prefix='/api/student')

@student_attendance_bp.route('/attendance', methods=['GET'])
@jwt_required()
@student_required
def get_student_attendance():
    """Get attendance records for the current student"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        student_id = user.student.student_id
        
        # Get query parameters
        course_offering_id = request.args.get('course_id', type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Parse dates
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return error_response('Invalid start_date format. Use YYYY-MM-DD', 400)
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return error_response('Invalid end_date format. Use YYYY-MM-DD', 400)
        
        # Get attendance records
        attendance_records = attendance_service.get_student_attendance(
            student_id=student_id,
            course_offering_id=course_offering_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return api_response({
            'attendance': attendance_records
        }, 'Attendance records retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting student attendance: {str(e)}")
        return error_response('Failed to load attendance data', 500)

@student_attendance_bp.route('/attendance/stats', methods=['GET'])
@jwt_required()
@student_required
def get_student_attendance_stats():
    """Get attendance statistics for the current student"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        student_id = user.student.student_id
        
        # Get query parameters
        course_offering_id = request.args.get('course_id', type=int)
        
        # Get attendance statistics
        stats = attendance_service.get_student_attendance_stats(
            student_id=student_id,
            course_offering_id=course_offering_id
        )
        
        return api_response({
            'stats': stats
        }, 'Attendance statistics retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting student attendance stats: {str(e)}")
        return error_response('Failed to load attendance statistics', 500)

@student_attendance_bp.route('/attendance/summary', methods=['GET'])
@jwt_required()
@student_required
def get_student_attendance_summary():
    """Get attendance summary for all courses"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        student_id = user.student.student_id
        
        # Get attendance summary by course
        from backend.models.academic import Enrollment, CourseOffering, Course
        from backend.models.tracking import Attendance
        from backend.extensions import db
        from sqlalchemy import func, case
        
        # FIXED: Query to get course-wise attendance summary with corrected case() syntax
        summary_query = db.session.query(
            CourseOffering.offering_id,
            Course.course_code,
            Course.course_name,
            CourseOffering.section_number,
            func.count(Attendance.attendance_id).label('total_classes'),
            func.sum(case((Attendance.status == 'present', 1), else_=0)).label('present_count'),
            func.sum(case((Attendance.status == 'absent', 1), else_=0)).label('absent_count'),
            func.sum(case((Attendance.status == 'late', 1), else_=0)).label('late_count'),
            func.sum(case((Attendance.status == 'excused', 1), else_=0)).label('excused_count')
        ).select_from(Enrollment).join(
            CourseOffering, Enrollment.offering_id == CourseOffering.offering_id
        ).join(
            Course, CourseOffering.course_id == Course.course_id
        ).join(
            Attendance, Attendance.enrollment_id == Enrollment.enrollment_id
        ).filter(
            Enrollment.student_id == student_id
        ).group_by(
            CourseOffering.offering_id,
            Course.course_code,
            Course.course_name,
            CourseOffering.section_number
        ).all()
        
        # Format summary data
        summary = []
        for record in summary_query:
            total = record.total_classes or 0
            present = record.present_count or 0
            attendance_rate = (present / total * 100) if total > 0 else 0
            
            summary.append({
                'offering_id': record.offering_id,
                'course_code': record.course_code,
                'course_name': record.course_name,
                'section': record.section_number,
                'total_classes': total,
                'present_count': present,
                'absent_count': record.absent_count or 0,
                'late_count': record.late_count or 0,
                'excused_count': record.excused_count or 0,
                'attendance_rate': round(attendance_rate, 2)
            })
        
        return api_response({
            'summary': summary
        }, 'Attendance summary retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting student attendance summary: {str(e)}")
        return error_response('Failed to load attendance summary', 500)

@student_attendance_bp.route('/attendance/calendar', methods=['GET'])
@jwt_required()
@student_required
def get_student_attendance_calendar():
    """Get attendance data formatted for calendar view"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        student_id = user.student.student_id
        
        # Get query parameters
        year = request.args.get('year', type=int, default=date.today().year)
        month = request.args.get('month', type=int, default=date.today().month)
        
        # Calculate date range for the month
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Get attendance records for the month
        attendance_records = attendance_service.get_student_attendance(
            student_id=student_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Format for calendar
        calendar_data = {}
        for record in attendance_records:
            date_key = record['date']
            if date_key not in calendar_data:
                calendar_data[date_key] = []
            
            calendar_data[date_key].append({
                'course_code': record['course_code'],
                'course_name': record['course_name'],
                'status': record['status'],
                'check_in_time': record['check_in_time']
            })
        
        return api_response({
            'calendar': calendar_data,
            'year': year,
            'month': month
        }, 'Calendar data retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting student attendance calendar: {str(e)}")
        return error_response('Failed to load calendar data', 500)

# Export the blueprint for import
__all__ = ['student_attendance_bp']