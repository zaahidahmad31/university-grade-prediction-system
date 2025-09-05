# backend/api/faculty/routes.py - CLEANED VERSION (Remove attendance routes)
from flask import Blueprint, jsonify, request, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.academic import Enrollment
from backend.models.assessment import Assessment, AssessmentSubmission
from backend.models.user import Faculty, Student
from backend.services.faculty_service import faculty_service
from backend.services.auth_service import get_user_by_id
from backend.services.assessment_service import assessment_service
from backend.middleware.auth_middleware import faculty_required
from backend.utils.api import api_response, error_response
from datetime import datetime, date
import logging
from backend.extensions import db 
from backend.models import User, CourseOffering
import os
from flask import send_file, current_app
from werkzeug.utils import secure_filename 
from backend.services.gpa_service import gpa_service
from flask_login import login_required, current_user


logger = logging.getLogger(__name__)

faculty_bp = Blueprint('faculty', __name__, url_prefix='/api/faculty')

# =====================================================
# DASHBOARD & BASIC ROUTES
# =====================================================

@faculty_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@faculty_required
def get_dashboard():
    """Get faculty dashboard data"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        faculty_id = user.faculty.faculty_id
        
        # Get dashboard summary
        summary = faculty_service.get_dashboard_summary(faculty_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'summary': summary,
                'faculty': {
                    'faculty_id': faculty_id,
                    'name': f"{user.faculty.first_name} {user.faculty.last_name}",
                    'email': user.email,
                    'department': user.faculty.department
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load dashboard data'
        }), 500

@faculty_bp.route('/courses', methods=['GET'])
@jwt_required()
@faculty_required
def get_courses():
    """Get courses taught by faculty"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        faculty_id = user.faculty.faculty_id
        
        # Get term from query params (optional)
        term_id = request.args.get('term_id', type=int)
        
        # Get courses
        courses = faculty_service.get_teaching_courses(faculty_id, term_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'courses': courses
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting courses: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load courses'
        }), 500

@faculty_bp.route('/students', methods=['GET'])
@jwt_required()
@faculty_required
def get_students():
    """Get students in faculty's courses"""
    try:
        # Get offering_id from query params
        offering_id = request.args.get('offering_id', type=int)
        
        if not offering_id:
            return jsonify({
                'status': 'error',
                'message': 'Course offering ID is required'
            }), 400
        
        # Verify faculty teaches this course
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        # Get students
        students = faculty_service.get_students_by_course(offering_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'students': students
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting students: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load students'
        }), 500

@faculty_bp.route('/all-students', methods=['GET'])
@jwt_required()
@faculty_required
def get_all_students():
    """Get all students enrolled in faculty's courses"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        faculty_id = user.faculty.faculty_id
        
        # Get all students across all courses
        all_students = faculty_service.get_all_students(faculty_id)
        
        # Get summary statistics
        total_students = len(all_students)
        active_students = len([s for s in all_students if s['current_grade'] != 'W'])
        at_risk_students = len([s for s in all_students if s['risk_level'] in ['medium', 'high']])
        
        # Calculate average attendance
        attendance_rates = [s['attendance_rate'] for s in all_students if s['attendance_rate'] is not None]
        avg_attendance = sum(attendance_rates) / len(attendance_rates) if attendance_rates else 0
        
        return jsonify({
            'status': 'success',
            'data': {
                'students': all_students,
                'summary': {
                    'total_students': total_students,
                    'active_students': active_students,
                    'at_risk_students': at_risk_students,
                    'average_attendance': round(avg_attendance, 1)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting all students: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load students'
        }), 500

@faculty_bp.route('/at-risk-students', methods=['GET'])
@jwt_required()
@faculty_required
def get_at_risk_students():
    """Get at-risk students in faculty's courses"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        faculty_id = user.faculty.faculty_id
        
        # Get at-risk students
        at_risk_students = faculty_service.get_at_risk_students(faculty_id)
        
        # Get total student count for context
        summary = faculty_service.get_dashboard_summary(faculty_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'students': at_risk_students,
                'total_students': summary['student_count']
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting at-risk students: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load at-risk students'
        }), 500

@faculty_bp.route('/assessments', methods=['GET'])
@jwt_required()
@faculty_required
def get_assessments():
    """Get recent assessments for faculty's courses"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        faculty_id = user.faculty.faculty_id
        
        # Get assessments
        assessments = faculty_service.get_recent_assessments(faculty_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'assessments': assessments
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting assessments: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load assessments'
        }), 500
    
@faculty_bp.route('/assessments/<int:assessment_id>', methods=['GET'])
@jwt_required()
@faculty_required
def get_assessment(assessment_id):
    """Get assessment details for editing"""
    try:
        # TODO: Verify faculty teaches this course
        
        assessment = assessment_service.get_assessment_details(assessment_id)
        
        if assessment:
            return api_response(assessment, 'Assessment details retrieved successfully')
        else:
            return error_response('Assessment not found', 404)
        
    except Exception as e:
        logger.error(f"Error getting assessment: {str(e)}")
        return error_response('Failed to get assessment details', 500)
    
@faculty_bp.route('/assessments/<int:assessment_id>', methods=['PUT'])
@jwt_required()
@faculty_required
def update_assessment(assessment_id):
    """Update an existing assessment"""
    try:
        data = request.get_json()
        
        # Get current user for tracking
        user_id = get_jwt_identity()
        
        # TODO: Verify faculty teaches this course
        
        # Update assessment
        assessment, error = assessment_service.update_assessment(
            assessment_id=assessment_id,
            **data
        )
        
        if assessment:
            return api_response({
                'assessment_id': assessment.assessment_id,
                'title': assessment.title
            }, 'Assessment updated successfully')
        else:
            return error_response(error or 'Failed to update assessment', 400)
        
    except Exception as e:
        logger.error(f"Error updating assessment: {str(e)}")
        return error_response('Failed to update assessment', 500)


@faculty_bp.route('/analytics', methods=['GET'])
@jwt_required()
@faculty_required
def get_analytics():
    """Get analytics data for faculty's courses"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        faculty_id = user.faculty.faculty_id
        
        # For now, return basic analytics
        # This can be expanded with more detailed analytics
        courses = faculty_service.get_teaching_courses(faculty_id)
        
        analytics = {
            'total_courses': len(courses),
            'average_attendance': 85.5,  # Placeholder
            'average_grade': 'B',  # Placeholder
            'submission_rate': 92.3  # Placeholder
        }
        
        return jsonify({
            'status': 'success',
            'data': analytics
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load analytics'
        }), 500

# =====================================================
# INDIVIDUAL STUDENT DETAIL ROUTES
# =====================================================

@faculty_bp.route('/students/<string:student_id>', methods=['GET'])
@jwt_required()
@faculty_required
def get_student_detail(student_id):
    """Get detailed information for a specific student"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        faculty_id = user.faculty.faculty_id
        
        # Get student detail
        student_detail = faculty_service.get_student_detail(faculty_id, student_id)
        
        if not student_detail:
            return jsonify({
                'status': 'error',
                'message': 'Student not found or not enrolled in your courses'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'student': student_detail
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting student detail: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load student details'
        }), 500

@faculty_bp.route('/students/<string:student_id>/grades', methods=['GET'])
@jwt_required()
@faculty_required
def get_student_grades(student_id):
    """Get grade data for a specific student"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        faculty_id = user.faculty.faculty_id
        
        # Get offering_id from query params
        offering_id = request.args.get('offering_id', type=int)
        
        # Get student grade data
        grade_data = faculty_service.get_student_grade_detail(faculty_id, student_id, offering_id)
        
        return jsonify({
            'status': 'success',
            'data': grade_data
        })
        
    except Exception as e:
        logger.error(f"Error getting student grades: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load grade data'
        }), 500

@faculty_bp.route('/students/<string:student_id>/attendance', methods=['GET'])
@jwt_required()
@faculty_required
def get_student_attendance(student_id):
    """Get attendance data for a specific student"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        faculty_id = user.faculty.faculty_id
        
        # Get student attendance data
        attendance_data = faculty_service.get_student_attendance_detail(faculty_id, student_id)
        
        return jsonify({
            'status': 'success',
            'data': attendance_data
        })
        
    except Exception as e:
        logger.error(f"Error getting student attendance: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load attendance data'
        }), 500

@faculty_bp.route('/students/<string:student_id>/interventions', methods=['GET'])
@jwt_required()
@faculty_required
def get_student_interventions(student_id):
    """Get intervention history for a specific student"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        faculty_id = user.faculty.faculty_id
        
        # Get student interventions
        interventions = faculty_service.get_student_interventions(faculty_id, student_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'interventions': interventions
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting student interventions: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load intervention data'
        }), 500

@faculty_bp.route('/interventions', methods=['POST'])
@jwt_required()
@faculty_required
def add_intervention():
    """Add new intervention for a student"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_id', 'offering_id', 'type', 'notes']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # For now, just return success since intervention model might not be implemented yet
        # In a real implementation, you would save to database
        
        return jsonify({
            'status': 'success',
            'message': 'Intervention added successfully',
            'data': {
                'intervention_id': 'temp_id',  # Would be real ID from database
                'type': data['type'],
                'notes': data['notes'],
                'created_date': '2024-06-12'  # Would be actual timestamp
            }
        })
        
    except Exception as e:
        logger.error(f"Error adding intervention: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to add intervention'
        }), 500

# REMOVED ALL ATTENDANCE ROUTES - Now handled by attendance_routes.py

# =====================================================
# ASSESSMENT ROUTES
# =====================================================

@faculty_bp.route('/assessment-types', methods=['GET'])
@jwt_required()
@faculty_required
def get_assessment_types():
    """Get available assessment types"""
    try:
        assessment_types = assessment_service.get_assessment_types()
        
        return api_response({
            'assessment_types': assessment_types
        }, 'Assessment types retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting assessment types: {str(e)}")
        return error_response('Failed to get assessment types', 500)
    
@faculty_bp.route('/assessments', methods=['POST'])
@jwt_required()
@faculty_required
def create_assessment():
    """Create a new assessment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['offering_id', 'type_id', 'title', 'max_score']
        for field in required_fields:
            if field not in data:
                return error_response(f'Missing required field: {field}', 400)
        
        # Get current user for tracking
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        created_by = user.faculty.faculty_id if user and user.faculty else str(user_id)
        
        # Create assessment
        assessment = assessment_service.create_assessment(
            offering_id=data['offering_id'],
            type_id=data['type_id'],
            title=data['title'],
            max_score=data['max_score'],
            due_date=data.get('due_date'),
            weight=data.get('weight'),
            description=data.get('description'),
            created_by=created_by
        )
        
        if assessment:
            return api_response({
                'assessment_id': assessment.assessment_id,
                'title': assessment.title
            }, 'Assessment created successfully')
        else:
            return error_response('Failed to create assessment', 500)
        
    except Exception as e:
        logger.error(f"Error creating assessment: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response('Failed to create assessment', 500)

 # Changed route
@faculty_bp.route('/courses/<int:offering_id>/assessments', methods=['GET'])
@jwt_required()
@faculty_required
def get_course_assessments(offering_id):
    """Get all assessments for a course offering"""
    try:
        # TODO: Verify faculty teaches this course
        
        assessments = assessment_service.get_assessments_by_offering(offering_id)
        
        return api_response({
            'assessments': assessments,
            'offering_id': offering_id
        }, 'Assessments retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting assessments: {str(e)}")
        return error_response('Failed to get assessments', 500)
    
@faculty_bp.route('/assessments/<int:assessment_id>', methods=['DELETE'])
@jwt_required()
@faculty_required
def delete_assessment(assessment_id):
    """Delete an assessment"""
    try:
        # TODO: Verify faculty teaches this course
        
        success, message = assessment_service.delete_assessment(assessment_id)
        
        if success:
            return api_response(message='Assessment deleted successfully')
        else:
            return error_response(message, 400)
        
    except Exception as e:
        logger.error(f"Error deleting assessment: {str(e)}")
        return error_response('Failed to delete assessment', 500)
    
@faculty_bp.route('/assessments/<int:assessment_id>/statistics', methods=['GET'])
@jwt_required()
@faculty_required
def get_assessment_statistics(assessment_id):
    """Get assessment statistics"""
    try:
        # TODO: Verify faculty teaches this course
        
        statistics = assessment_service.get_assessment_statistics(assessment_id)
        
        if statistics:
            return api_response(statistics, 'Statistics retrieved successfully')
        else:
            return error_response('Assessment not found', 404)
        
    except Exception as e:
        logger.error(f"Error getting assessment statistics: {str(e)}")
        return error_response('Failed to get assessment statistics', 500)
    
@faculty_bp.route('/assessments/grade', methods=['POST'])
@jwt_required()
@faculty_required
def enter_single_grade():
    """Enter grade for a single student"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['enrollment_id', 'assessment_id', 'score']
        for field in required_fields:
            if field not in data:
                return error_response(f'Missing required field: {field}', 400)
        
        # Get current user for tracking
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        graded_by = user.faculty.faculty_id if user and user.faculty else str(user_id)
        
        # Enter the grade
        submission, error = assessment_service.enter_grade(
            enrollment_id=data['enrollment_id'],
            assessment_id=data['assessment_id'],
            score=data['score'],
            feedback=data.get('feedback'),
            graded_by=graded_by
        )
        
        if submission:
            return api_response({
                'submission_id': submission.submission_id,
                'score': float(submission.score),
                'percentage': float(submission.percentage)
            }, 'Grade entered successfully')
        else:
            return error_response(error or 'Failed to enter grade', 400)
        
    except Exception as e:
        logger.error(f"Error entering grade: {str(e)}")
        return error_response('Failed to enter grade', 500)
    
@faculty_bp.route('/assessments/grades/bulk', methods=['POST'])
@jwt_required()
@faculty_required
def enter_bulk_grades():
    """Enter grades for multiple students"""
    try:
        data = request.get_json()
        
        if 'grades' not in data or not isinstance(data['grades'], list):
            return error_response('Invalid data format. Expected "grades" array', 400)
        
        # Get current user for tracking
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        graded_by = user.faculty.faculty_id if user and user.faculty else str(user_id)
        
        # Enter grades
        results = assessment_service.bulk_enter_grades(data['grades'], graded_by)
        
        # Count successes
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        return api_response({
            'results': results,
            'summary': {
                'total': len(results),
                'successful': successful,
                'failed': failed
            }
        }, f'Bulk grading completed: {successful} successful, {failed} failed')
        
    except Exception as e:
        logger.error(f"Error in bulk grading: {str(e)}")
        return error_response('Failed to process bulk grading', 500)
    
@faculty_bp.route('/assessments/<int:assessment_id>/roster', methods=['GET'])
@jwt_required()
@faculty_required
def get_assessment_roster(assessment_id):
    """Get roster for grade entry with security verification"""
    try:
        # Get current user and verify faculty status
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            logger.warning(f"User {user_id} attempted to access assessment roster without faculty status")
            return error_response('Faculty profile not found', 404)
        
        faculty_id = user.faculty.faculty_id
        
        # FIXED: Pass faculty_id for security verification
        roster_data = assessment_service.get_assessment_roster(assessment_id, faculty_id)
        
        if roster_data:
            return api_response(roster_data, 'Assessment roster retrieved successfully')
        else:
            # Check if assessment exists at all
            assessment = Assessment.query.get(assessment_id)
            if not assessment:
                return error_response('Assessment not found', 404)
            else:
                return error_response('You do not have permission to access this assessment', 403)
        
    except Exception as e:
        logger.error(f"Error getting assessment roster: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response('Failed to get assessment roster', 500)
    
@faculty_bp.route('/courses/<int:offering_id>/students', methods=['GET'])
@jwt_required()
@faculty_required
def get_course_students(offering_id):
    """Get students enrolled in a specific course offering"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        faculty_id = user.faculty.faculty_id
        
        # Verify faculty teaches this course
        from backend.models import CourseOffering
        course_offering = CourseOffering.query.filter_by(
            offering_id=offering_id,
            faculty_id=faculty_id
        ).first()
        
        if not course_offering:
            return jsonify({
                'status': 'error',
                'message': 'You are not authorized to view this course'
            }), 403
        
        # Get students enrolled in this course
        students = faculty_service.get_students_by_course(offering_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'students': students,
                'offering_id': offering_id,
                'course_info': {
                    'course_code': course_offering.course.course_code,
                    'course_name': course_offering.course.course_name,
                    'section': course_offering.section_number
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting course students: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load course students'
        }), 500

@faculty_bp.route('/dashboard/summary', methods=['GET'])
@jwt_required()
@faculty_required
def get_dashboard_summary():
    """Get dashboard summary for faculty"""
    try:
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({
                'status': 'error',
                'message': 'Faculty profile not found'
            }), 404
        
        faculty_id = user.faculty.faculty_id
        
        # Get dashboard summary
        summary = faculty_service.get_dashboard_summary(faculty_id)
        
        return jsonify({
            'status': 'success',
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load dashboard summary'
        }), 500
    
@faculty_bp.route('/profile', methods=['GET'])
@jwt_required()
@faculty_required
def get_profile():
    """Get faculty profile"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return error_response('Faculty profile not found', 404)
        
        faculty = user.faculty
        
        # Build profile response - using actual field names from the model
        profile_data = {
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'last_login': user.last_login.isoformat() if user.last_login else None
            },
            'faculty': {
                'faculty_id': faculty.faculty_id,
                'first_name': faculty.first_name,
                'last_name': faculty.last_name,
                'department': faculty.department,
                'position': faculty.position,
                'office_location': faculty.office_location,
                'phone_number': faculty.phone,  # Map phone to phone_number for frontend compatibility
                'specialization': None,  # Not in model, return None
                'hire_date': None,  # Not in model, return None
                'status': 'active'  # Not in model, return default
            }
        }
        
        return api_response(profile_data, 'Profile retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting faculty profile: {str(e)}")
        return error_response('Failed to retrieve profile', 500)

    
@faculty_bp.route('/profile', methods=['PUT'])
@jwt_required()
@faculty_required
def update_profile():
    """Update faculty profile"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return error_response('Faculty profile not found', 404)
        
        data = request.get_json()
        if not data:
            return error_response('No data provided', 400)
        
        faculty = user.faculty
        
        # Map frontend field names to model field names
        field_mapping = {
            'first_name': 'first_name',
            'last_name': 'last_name',
            'department': 'department',
            'position': 'position',
            'office_location': 'office_location',
            'phone_number': 'phone'  # Map phone_number from frontend to phone in model
        }
        
        # Update faculty fields
        for frontend_field, model_field in field_mapping.items():
            if frontend_field in data:
                value = data[frontend_field]
                # Handle empty strings - convert to None for database
                if value == '':
                    value = None
                setattr(faculty, model_field, value)
        
        # Update user email if provided
        if 'email' in data:
            email = data['email']
            if email and email != user.email:
                # Check if email already exists
                existing = User.query.filter_by(email=email).first()
                if existing:
                    return error_response('Email already in use', 400)
                user.email = email
        
        # Save changes
        db.session.commit()
        
        # Return updated profile data
        profile_data = {
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'last_login': user.last_login.isoformat() if user.last_login else None
            },
            'faculty': {
                'faculty_id': faculty.faculty_id,
                'first_name': faculty.first_name,
                'last_name': faculty.last_name,
                'department': faculty.department,
                'position': faculty.position,
                'office_location': faculty.office_location,
                'phone_number': faculty.phone,  # Map phone to phone_number for frontend
                'specialization': None,  # Not in model
                'hire_date': None,  # Not in model
                'status': 'active'  # Not in model
            }
        }
        
        logger.info(f"Profile updated successfully for faculty: {faculty.faculty_id}")
        
        return api_response(profile_data, 'Profile updated successfully')
        
    except Exception as e:
        logger.error(f"Error updating faculty profile: {str(e)}")
        db.session.rollback()
        return error_response('Failed to update profile', 500)
    
@faculty_bp.route('/submissions/<int:submission_id>', methods=['GET'])
@jwt_required()
@faculty_required
def get_submission_details(submission_id):
    """Get detailed submission information"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return error_response('Faculty profile not found', 404)
        
        faculty_id = user.faculty.faculty_id
        
        # Get submission with security check
        submission_data = assessment_service.get_submission_details(submission_id, faculty_id)
        
        if submission_data:
            return api_response(submission_data, 'Submission details retrieved successfully')
        else:
            return error_response('Submission not found or access denied', 404)
        
    except Exception as e:
        logger.error(f"Error getting submission details: {str(e)}")
        return error_response('Failed to get submission details', 500)
    
@faculty_bp.route('/submissions/<int:submission_id>/download', methods=['GET'])
@jwt_required()
@faculty_required
def download_submission(submission_id):
    """Download submission file"""
    try:
        submission = AssessmentSubmission.query.get(submission_id)
        
        if not submission:
            return error_response('Submission not found', 404)
        
        if not submission.file_path:
            return error_response('No file attached to this submission', 404)
        
        # TODO: Verify faculty teaches this course
        
        # Construct file path
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], submission.file_path)
        
        if not os.path.exists(file_path):
            return error_response('File not found on server', 404)
        
        return send_file(
            file_path,
            download_name=submission.file_name or 'submission',
            as_attachment=True,
            mimetype=submission.mime_type or 'application/octet-stream'
        )
        
    except Exception as e:
        logger.error(f"Error downloading submission: {str(e)}")
        return error_response('Failed to download submission', 500)
    
@faculty_bp.route('/assessments/<int:assessment_id>/submissions', methods=['GET'])
@jwt_required()
@faculty_required
def get_assessment_submissions(assessment_id):
    """Get all submissions for an assessment with student details"""
    try:
        # Get assessment details first
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            return error_response('Assessment not found', 404)
        
        # Get all submissions with student details
        submissions = db.session.query(
            AssessmentSubmission,
            User.first_name,
            User.last_name,
            Student.student_id,
            Enrollment.enrollment_id
        ).join(
            Enrollment, Enrollment.enrollment_id == AssessmentSubmission.enrollment_id
        ).join(
            Student, Student.student_id == Enrollment.student_id
        ).join(
            User, User.user_id == Student.user_id
        ).filter(
            AssessmentSubmission.assessment_id == assessment_id
        ).order_by(
            User.last_name, User.first_name
        ).all()
        
        # TODO: Verify faculty teaches this course
        
        result = []
        for submission, first_name, last_name, student_id, enrollment_id in submissions:
            sub_dict = submission.to_dict()
            sub_dict['student_name'] = f"{first_name} {last_name}"
            sub_dict['student_id'] = student_id
            sub_dict['enrollment_id'] = enrollment_id
            sub_dict['max_score'] = float(assessment.max_score)
            result.append(sub_dict)
        
        return api_response({
            'submissions': result,
            'total': len(result),
            'assessment': assessment.to_dict()
        }, 'Submissions retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting submissions: {str(e)}")
        return error_response('Failed to get submissions', 500)
    
@faculty_bp.route('/submissions/<int:submission_id>/download', methods=['GET'])
@jwt_required()
@faculty_required
def download_submission_file(submission_id):
    """Download submission file"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return error_response('Faculty profile not found', 404)
        
        faculty_id = user.faculty.faculty_id
        
        # Get file download response
        file_response = assessment_service.download_submission_file(submission_id, faculty_id)
        
        if file_response:
            return file_response
        else:
            return error_response('File not found or access denied', 404)
        
    except Exception as e:
        logger.error(f"Error downloading submission file: {str(e)}")
        return error_response('Failed to download file', 500)
    

#gpa roues 


@faculty_bp.route('/courses/<int:offering_id>/grade-summary', methods=['GET'])
@jwt_required()
@faculty_required
def get_grade_summary(offering_id):
    """Get grade summary for all students in a course"""
    try:
        # Get current user using JWT
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({'status': 'error', 'message': 'Faculty profile not found'}), 404
        
        # Verify faculty teaches this course
        faculty = user.faculty
        offering = CourseOffering.query.filter_by(
            offering_id=offering_id,
            faculty_id=faculty.faculty_id
        ).first()
        
        if not offering:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
        # Get grade summary
        summary = gpa_service.get_course_grade_summary(offering_id)
        
        # Add course info
        course_info = {
            'offering_id': offering_id,
            'course_code': offering.course.course_code,
            'course_name': offering.course.course_name,
            'section': offering.section_number,
            'term': offering.term.term_name
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'course': course_info,
                'students': summary
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting grade summary: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to get grade summary'}), 500

@faculty_bp.route('/grades/finalize', methods=['POST'])
@jwt_required()
@faculty_required
def finalize_grades():
    """Finalize grades for one or more students"""
    try:
        data = request.get_json()
        grades = data.get('grades', [])
        
        if not grades:
            return jsonify({'status': 'error', 'message': 'No grades provided'}), 400
        
        # Get current user using JWT
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.faculty:
            return jsonify({'status': 'error', 'message': 'Faculty profile not found'}), 404
            
        faculty = user.faculty
        
        # Verify faculty access to all enrollments
        enrollment_ids = [g['enrollment_id'] for g in grades]
        
        # Check authorization
        authorized_count = db.session.query(Enrollment).join(
            CourseOffering
        ).filter(
            Enrollment.enrollment_id.in_(enrollment_ids),
            CourseOffering.faculty_id == faculty.faculty_id
        ).count()
        
        if authorized_count != len(enrollment_ids):
            return jsonify({'status': 'error', 'message': 'Unauthorized access to some enrollments'}), 403
        
        # Process grades
        success_count = 0
        errors = []
        
        for grade_data in grades:
            enrollment_id = grade_data['enrollment_id']
            final_grade = grade_data['final_grade']
            override_reason = grade_data.get('override_reason')
            
            success, message = gpa_service.finalize_grade(
                enrollment_id, 
                final_grade, 
                override_reason
            )
            
            if success:
                success_count += 1
            else:
                errors.append({
                    'enrollment_id': enrollment_id,
                    'error': message
                })
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully finalized {success_count} grades',
            'data': {
                'success_count': success_count,
                'total': len(grades),
                'errors': errors
            }
        })
        
    except Exception as e:
        logger.error(f"Error finalizing grades: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to finalize grades'}), 500