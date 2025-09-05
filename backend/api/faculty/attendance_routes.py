# backend/api/faculty/attendance_routes.py - FIXED VERSION
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.attendance_service import attendance_service
from backend.services.auth_service import get_user_by_id
from backend.middleware.auth_middleware import faculty_required
from backend.utils.api import api_response, error_response
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

# Create blueprint
faculty_attendance_bp = Blueprint('faculty_attendance', __name__, url_prefix='/api/faculty')

@faculty_attendance_bp.route('/attendance/roster/<int:offering_id>', methods=['GET'])
@jwt_required()
@faculty_required
def get_course_roster(offering_id):
    """Get course roster with attendance status for a specific date"""
    try:
        # Get date from query params
        date_str = request.args.get('date')
        if date_str:
            try:
                attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return error_response('Invalid date format. Use YYYY-MM-DD', 400)
        else:
            attendance_date = date.today()
        
        # Verify faculty has access to this course offering
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return error_response('Faculty profile not found', 404)
        
        # TODO: Add verification that faculty teaches this course
        
        # Get roster
        roster = attendance_service.get_course_roster(offering_id, attendance_date)
        
        return api_response({
            'roster': roster,
            'date': attendance_date.isoformat(),
            'offering_id': offering_id
        }, 'Roster retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting roster: {str(e)}")
        return error_response('Failed to get course roster', 500)

@faculty_attendance_bp.route('/attendance/mark', methods=['POST'])
@jwt_required()
@faculty_required
def mark_single_attendance():
    """Mark attendance for a single student"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['enrollment_id', 'attendance_date', 'status']
        for field in required_fields:
            if field not in data:
                return error_response(f'Missing required field: {field}', 400)
        
        # Validate status
        valid_statuses = ['present', 'absent', 'late', 'excused']
        if data['status'] not in valid_statuses:
            return error_response(f'Invalid status. Must be one of: {valid_statuses}', 400)
        
        # Parse date
        try:
            attendance_date = datetime.strptime(data['attendance_date'], '%Y-%m-%d').date()
        except ValueError:
            return error_response('Invalid date format. Use YYYY-MM-DD', 400)
        
        # Parse check-in time if provided
        check_in_time = None
        if data.get('check_in_time'):
            try:
                check_in_time = datetime.strptime(data['check_in_time'], '%H:%M').time()
            except ValueError:
                return error_response('Invalid time format. Use HH:MM', 400)
        
        # Get current user for recording
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        recorded_by = user.faculty.faculty_id if user and user.faculty else str(user_id)
        
        # Mark attendance
        attendance_record = attendance_service.mark_attendance(
            enrollment_id=data['enrollment_id'],
            attendance_date=attendance_date,
            status=data['status'],
            check_in_time=check_in_time,
            notes=data.get('notes'),
            recorded_by=recorded_by
        )
        
        if attendance_record:
            return api_response({
                'attendance_id': attendance_record.attendance_id,
                'status': attendance_record.status,
                'message': 'Attendance marked successfully'
            }, 'Attendance marked successfully')
        else:
            return error_response('Failed to mark attendance', 500)
        
    except Exception as e:
        logger.error(f"Error marking attendance: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response('Failed to mark attendance', 500)

@faculty_attendance_bp.route('/attendance/bulk-mark', methods=['POST'])
@jwt_required()
@faculty_required
def bulk_mark_attendance():
    """Mark attendance for multiple students"""
    try:
        data = request.get_json()
        
        # Validate request data
        if not data:
            return error_response('No data provided', 400)
        
        if 'attendance_records' not in data:
            return error_response('Missing attendance_records field', 400)
        
        attendance_data = data['attendance_records']
        
        if not isinstance(attendance_data, list):
            return error_response('attendance_records must be a list', 400)
        
        if len(attendance_data) == 0:
            return error_response('No attendance records provided', 400)
        
        # Validate each record
        valid_statuses = ['present', 'absent', 'late', 'excused']
        for i, record in enumerate(attendance_data):
            required_fields = ['enrollment_id', 'attendance_date', 'status']
            for field in required_fields:
                if field not in record:
                    return error_response(f'Missing required field: {field} in record {i+1}', 400)
            
            if record['status'] not in valid_statuses:
                return error_response(f'Invalid status in record {i+1}: {record["status"]}', 400)
        
        # Get current user for recording
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        recorded_by = user.faculty.faculty_id if user and user.faculty else str(user_id)
        
        # Process attendance data
        processed_data = []
        for record in attendance_data:
            try:
                # Parse date
                attendance_date = datetime.strptime(record['attendance_date'], '%Y-%m-%d').date()
                
                # Parse check-in time if provided
                check_in_time = None
                if record.get('check_in_time'):
                    check_in_time = datetime.strptime(record['check_in_time'], '%H:%M').time()
                
                processed_data.append({
                    'enrollment_id': record['enrollment_id'],
                    'attendance_date': attendance_date,
                    'status': record['status'],
                    'check_in_time': check_in_time,
                    'notes': record.get('notes')
                })
                
            except ValueError as e:
                logger.error(f"Error parsing record: {str(e)}")
                return error_response(f'Invalid date/time format in record: {str(e)}', 400)
        
        # Bulk mark attendance
        logger.info(f"Processing {len(processed_data)} attendance records")
        results = attendance_service.bulk_mark_attendance(processed_data, recorded_by)
        
        # Count successes and failures
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        
        # Log results
        logger.info(f"Bulk attendance completed: {successful} successful, {failed} failed")
        
        response_data = {
            'results': results,
            'summary': {
                'total': len(results),
                'successful': successful,
                'failed': failed
            }
        }
        
        if failed > 0:
            message = f'Bulk attendance partially completed: {successful} successful, {failed} failed'
            return api_response(response_data, message, status=206)  # Partial Content
        else:
            message = f'Bulk attendance completed successfully: {successful} records processed'
            return api_response(response_data, message)
        
    except Exception as e:
        logger.error(f"Error in bulk attendance marking: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response('Failed to process bulk attendance', 500)

@faculty_attendance_bp.route('/attendance/summary/<int:offering_id>', methods=['GET'])
@jwt_required()
@faculty_required
def get_attendance_summary(offering_id):
    """Get attendance summary for a course"""
    try:
        # Get date range from query params
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
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
        
        # Get summary
        summary = attendance_service.get_attendance_summary(
            offering_id, 
            start_date=start_date, 
            end_date=end_date
        )
        
        return api_response({
            'summary': summary,
            'offering_id': offering_id,
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None
        }, 'Attendance summary retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting attendance summary: {str(e)}")
        return error_response('Failed to get attendance summary', 500)

@faculty_attendance_bp.route('/attendance/<int:attendance_id>', methods=['DELETE'])
@jwt_required()
@faculty_required
def delete_attendance_record(attendance_id):
    """Delete an attendance record"""
    try:
        # TODO: Add verification that faculty has permission to delete this record
        
        success = attendance_service.delete_attendance(attendance_id)
        
        if success:
            return api_response({
                'attendance_id': attendance_id
            }, 'Attendance record deleted successfully')
        else:
            return error_response('Attendance record not found', 404)
        
    except Exception as e:
        logger.error(f"Error deleting attendance record: {str(e)}")
        return error_response('Failed to delete attendance record', 500)

@faculty_attendance_bp.route('/attendance/dates/<int:offering_id>', methods=['GET'])
@jwt_required()
@faculty_required
def get_attendance_dates(offering_id):
    """Get list of dates when attendance was taken for a course"""
    try:
        limit = request.args.get('limit', type=int, default=30)
        
        dates = attendance_service.get_course_attendance_dates(offering_id, limit)
        
        return api_response({
            'dates': [d.isoformat() for d in dates],
            'offering_id': offering_id
        }, 'Attendance dates retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting attendance dates: {str(e)}")
        return error_response('Failed to get attendance dates', 500)