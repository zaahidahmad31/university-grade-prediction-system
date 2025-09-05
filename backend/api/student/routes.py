# backend/api/student/routes.py - CLEANED VERSION (Remove attendance routes)
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import current_user, jwt_required, get_jwt_identity
from flask_login import login_required, current_user
from backend.models.user import Student
from backend.services.student_service import student_service
from backend.services.assessment_service import assessment_service
from backend.services.auth_service import get_user_by_id
from backend.middleware.auth_middleware import student_required
from backend.services.course_service import course_service
from backend.models import Course, CourseOffering, Enrollment, Faculty, AcademicTerm, Prediction, Assessment, AssessmentSubmission
from sqlalchemy import func, desc
from backend.utils.api import api_response, error_response
from backend.models import User
from datetime import datetime
import logging
from backend.extensions import db 
import os
from werkzeug.utils import secure_filename
from backend.services.prediction_service import PredictionService
from backend.services.gpa_service import gpa_service 

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

logger = logging.getLogger(__name__)
# Initialize the prediction service
prediction_service = PredictionService()

student_bp = Blueprint('student', __name__, url_prefix='/api/student')

@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@student_required
def get_dashboard():
    """Get comprehensive student dashboard data"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return jsonify({
                'status': 'error',
                'message': 'Student profile not found'
            }), 404
        
        student_id = user.student.student_id
        
        # Get dashboard summary
        summary = student_service.get_dashboard_summary(student_id)
        
        # Get recent courses (for dashboard display)
        recent_courses = student_service.get_enrolled_courses(student_id)[:3]  # Limit to 3
        
        return jsonify({
            'status': 'success',
            'data': {
                'summary': summary,
                'recent_courses': recent_courses,
                'student': {
                    'student_id': student_id,
                    'name': f"{user.student.first_name} {user.student.last_name}",
                    'email': user.email,
                    'program_code': user.student.program_code,
                    'year_of_study': user.student.year_of_study
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load dashboard data'
        }), 500

@student_bp.route('/courses', methods=['GET'])
@jwt_required()
@student_required
def get_courses():
    """Get enrolled courses for the student with detailed information"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return jsonify({
                'status': 'error',
                'message': 'Student profile not found'
            }), 404
        
        student_id = user.student.student_id
        
        # Get term from query params (optional)
        term_id = request.args.get('term_id', type=int)
        
        # Get courses using the enhanced service method
        courses = student_service.get_enrolled_courses(student_id, term_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'courses': courses,
                'student_info': {
                    'student_id': student_id,
                    'name': f"{user.student.first_name} {user.student.last_name}",
                    'email': user.email
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting courses: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load courses'
        }), 500

# REMOVED ATTENDANCE ROUTE - Now handled by attendance_routes.py

@student_bp.route('/assessments', methods=['GET'])
@jwt_required()
@student_required
def get_assessments():
    """Get assessments for the student"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return jsonify({
                'status': 'error',
                'message': 'Student profile not found'
            }), 404
        
        student_id = user.student.student_id
        
        # Get course_id from query params (optional)
        course_id = request.args.get('course_id')
        
        # Get assessments
        assessments = student_service.get_assessments(student_id, course_id)
        
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

@student_bp.route('/predictions', methods=['GET'])
@jwt_required()
@student_required
def get_predictions():
    """Get grade predictions for the student"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return jsonify({
                'status': 'error',
                'message': 'Student profile not found'
            }), 404
        
        student_id = user.student.student_id
        
        # Get predictions
        predictions = student_service.get_grade_predictions(student_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'predictions': predictions
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting predictions: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load predictions'
        }), 500

@student_bp.route('/course/<int:offering_id>/assessments', methods=['GET'])
@jwt_required()
@student_required
def get_student_course_assessments(offering_id):
    """Get assessments for a specific course"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return jsonify({
                'status': 'error',
                'message': 'Student profile not found'
            }), 404
        
        student_id = user.student.student_id
        
        # Get assessments for this course
        assessments = assessment_service.get_student_assessments(student_id, offering_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'assessments': assessments,
                'offering_id': offering_id
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting student assessments: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load assessments'
        }), 500

@student_bp.route('/assessments/all', methods=['GET'])
@jwt_required()
@student_required
def get_all_student_assessments():
    """Get all assessments for a student across all courses"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return jsonify({
                'status': 'error',
                'message': 'Student profile not found'
            }), 404
        
        student_id = user.student.student_id
        
        # Get all assessments
        assessments = assessment_service.get_student_assessments(student_id)
        
        # Group by course for better organization
        courses = {}
        for assessment in assessments:
            course_key = f"{assessment['course_code']}"
            if course_key not in courses:
                courses[course_key] = {
                    'course_code': assessment['course_code'],
                    'course_name': assessment['course_name'],
                    'assessments': []
                }
            courses[course_key]['assessments'].append(assessment)
        
        return jsonify({
            'status': 'success',
            'data': {
                'courses': list(courses.values()),
                'total_assessments': len(assessments)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting all student assessments: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load assessments'
        }), 500

@student_bp.route('/api/student/grades/summary', methods=['GET'])
@login_required
@student_required
def get_grade_summary():
    """Get student's grade summary including GPA"""
    try:
        user_id = current_user.user_id
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            return jsonify({'status': 'error', 'message': 'Student not found'}), 404
        
        # Get current GPA
        current_gpa = float(student.gpa) if student.gpa else 0.0
        
        # Get grade summary data
        summary = {
            'current_gpa': current_gpa,
            'grade_distribution': [],  # You can implement this later
            'term_history': []  # You can implement this later
        }
        
        return jsonify({
            'status': 'success',
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting grade summary: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Failed to get grade summary'}), 500
    
@student_bp.route('/courses/<string:course_id>', methods=['GET'])
@jwt_required()
@student_required
def get_course_details(course_id):
    """Get detailed information for a specific course"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return jsonify({
                'status': 'error',
                'message': 'Student profile not found'
            }), 404
        
        student_id = user.student.student_id
        
        # Get the specific course enrollment
        enrollment = db.session.query(
            Enrollment, Course, CourseOffering, Faculty
        ).join(
            CourseOffering, CourseOffering.offering_id == Enrollment.offering_id
        ).join(
            Course, Course.course_id == CourseOffering.course_id
        ).outerjoin(
            Faculty, Faculty.faculty_id == CourseOffering.faculty_id
        ).filter(
            Enrollment.student_id == student_id,
            Course.course_id == course_id,
            Enrollment.enrollment_status == 'enrolled'
        ).first()
        
        if not enrollment:
            return jsonify({
                'status': 'error',
                'message': 'Course not found or not enrolled'
            }), 404
        
        enrollment_obj, course, offering, faculty = enrollment
        
        # Get detailed course information
        course_details = {
            'course_id': course.course_id,
            'course_code': course.course_code,
            'course_name': course.course_name,
            'credits': course.credits,
            'description': course.description,
            'section': offering.section_number,
            'meeting_pattern': offering.meeting_pattern,
            'location': offering.location,
            'instructor_name': f"{faculty.first_name} {faculty.last_name}" if faculty else 'TBA',
            'instructor_email': faculty.email if faculty else None,
            'enrollment_status': enrollment_obj.enrollment_status,
            'current_grade': enrollment_obj.final_grade
        }
        
        # Get attendance data
        attendance_summary = student_service.get_attendance_summary(student_id, course_id)
        
        # Get assessments for this course
        assessments = db.session.query(Assessment).join(
            CourseOffering, CourseOffering.offering_id == Assessment.offering_id
        ).join(
            Enrollment, Enrollment.offering_id == CourseOffering.offering_id
        ).filter(
            Enrollment.student_id == student_id,
            CourseOffering.course_id == course_id
        ).all()
        
        assessment_data = []
        for assessment in assessments:
            # Get submission if exists
            submission = AssessmentSubmission.query.filter_by(
                assessment_id=assessment.assessment_id,
                student_id=student_id
            ).first()
            
            assessment_data.append({
                'assessment_id': assessment.assessment_id,
                'title': assessment.title,
                'type': assessment.type_id,  # You may want to join with AssessmentType
                'max_score': assessment.max_score,
                'due_date': assessment.due_date.isoformat() if assessment.due_date else None,
                'weight': float(assessment.weight),
                'submission_score': submission.score if submission else None,
                'submitted_at': submission.submitted_at.isoformat() if submission and submission.submitted_at else None
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'course': course_details,
                'attendance': attendance_summary,
                'assessments': assessment_data
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting course details: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load course details'
        }), 500
    
@student_bp.route('/profile', methods=['GET'])
@jwt_required()
@student_required
def get_profile():
    """Get student profile"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        student = user.student
        
        # Build profile response
        profile_data = {
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'last_login': user.last_login.isoformat() if user.last_login else None
            },
            'student': {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'date_of_birth': student.date_of_birth.isoformat() if student.date_of_birth else None,
                'gender': student.gender,
                'program_code': student.program_code,
                'year_of_study': student.year_of_study,
                'enrollment_date': student.enrollment_date.isoformat() if student.enrollment_date else None,
                'expected_graduation': student.expected_graduation.isoformat() if student.expected_graduation else None,
                'gpa': float(student.gpa) if student.gpa else None,
                'status': student.status
            }
        }
        
        return api_response(profile_data, 'Profile retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        return error_response('Failed to retrieve profile', 500)

@student_bp.route('/profile', methods=['PUT'])
@jwt_required()
@student_required
def update_profile():
    """Update student profile"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        data = request.get_json()
        if not data:
            return error_response('No data provided', 400)
        
        student = user.student
        
        # Update allowed fields only
        allowed_student_fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 
                                  'program_code', 'year_of_study']
        allowed_user_fields = ['email']
        
        # Update student fields
        for field in allowed_student_fields:
            if field in data:
                value = data[field]
                
                # Handle empty strings - convert to None for database
                if value == '':
                    value = None
                
                if field == 'date_of_birth' and value:
                    # Parse date string to date object
                    try:
                        date_obj = datetime.strptime(value, '%Y-%m-%d').date()
                        setattr(student, field, date_obj)
                    except ValueError:
                        return error_response('Invalid date format. Use YYYY-MM-DD', 400)
                elif field == 'year_of_study' and value is not None:
                    # Ensure year_of_study is an integer
                    try:
                        setattr(student, field, int(value))
                    except ValueError:
                        return error_response('Year of study must be a number', 400)
                else:
                    setattr(student, field, value)
        
        # Update user fields
        for field in allowed_user_fields:
            if field in data:
                value = data[field]
                
                # Don't update email if it's empty
                if field == 'email' and not value:
                    continue
                    
                # Check if email already exists
                if field == 'email' and value != user.email:
                    existing = User.query.filter_by(email=value).first()
                    if existing:
                        return error_response('Email already in use', 400)
                setattr(user, field, value)
        
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
            'student': {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'date_of_birth': student.date_of_birth.isoformat() if student.date_of_birth else None,
                'gender': student.gender,
                'program_code': student.program_code,
                'year_of_study': student.year_of_study,
                'enrollment_date': student.enrollment_date.isoformat() if student.enrollment_date else None,
                'expected_graduation': student.expected_graduation.isoformat() if student.expected_graduation else None,
                'gpa': float(student.gpa) if student.gpa else None,
                'status': student.status
            }
        }
        
        logger.info(f"Profile updated successfully for student: {student.student_id}")
        
        return api_response(profile_data, 'Profile updated successfully')
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        db.session.rollback()
        return error_response('Failed to update profile', 500)
    
@student_bp.route('/courses/available', methods=['GET'])
@jwt_required()
@student_required
def get_available_courses():
    """Get courses available for enrollment"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        student_id = user.student.student_id
        
        # Get term from query params
        term_id = request.args.get('term_id', type=int)
        
        # Get available courses
        courses = course_service.get_available_courses(student_id, term_id)
        
        return api_response({
            'courses': courses,
            'count': len(courses)
        }, 'Available courses retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting available courses: {str(e)}")
        return error_response('Failed to retrieve available courses', 500)

@student_bp.route('/courses/enroll', methods=['POST'])
@jwt_required()
@student_required
def enroll_in_course():
    """Enroll in a course"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        data = request.get_json()
        if not data or 'offering_id' not in data:
            return error_response('Course offering ID is required', 400)
        
        student_id = user.student.student_id
        offering_id = data['offering_id']
        
        # Log the enrollment attempt
        logger.info(f"Student {student_id} attempting to enroll in offering {offering_id}")
        
        # Enroll student
        result, error = course_service.enroll_student(student_id, offering_id)
        
        if error:
            logger.warning(f"Enrollment failed for student {student_id}: {error}")
            return error_response(error, 400)
        
        logger.info(f"Student {student_id} successfully enrolled in offering {offering_id}")
        
        return api_response({
            'enrollment_id': result['enrollment_id'],
            'message': result['message']
        }, 'Successfully enrolled in course')
        
    except Exception as e:
        logger.error(f"Error enrolling in course: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response('Failed to enroll in course', 500)

@student_bp.route('/courses/drop', methods=['POST'])
@jwt_required()
@student_required
def drop_course():
    """Drop a course"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        data = request.get_json()
        if not data or 'offering_id' not in data:
            return error_response('Course offering ID is required', 400)
        
        student_id = user.student.student_id
        offering_id = data['offering_id']
        
        # Log the drop attempt
        logger.info(f"Student {student_id} attempting to drop offering {offering_id}")
        
        # Drop course
        success, message = course_service.drop_course(student_id, offering_id)
        
        if not success:
            logger.warning(f"Drop failed for student {student_id}: {message}")
            return error_response(message, 400)
        
        logger.info(f"Student {student_id} successfully dropped offering {offering_id}")
        
        return api_response({'message': message}, 'Course dropped successfully')
        
    except Exception as e:
        logger.error(f"Error dropping course: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response('Failed to drop course', 500)
    
@student_bp.route('/upload-photo', methods=['POST'])
@jwt_required()
@student_required
def upload_profile_photo():
        """Upload profile photo"""
        try:
            user_id = get_jwt_identity()
            user = get_user_by_id(user_id)
            
            if not user or not user.student:
                return error_response('Student profile not found', 404)
            
            if 'photo' not in request.files:
                return error_response('No photo file provided', 400)
            
            file = request.files['photo']
            
            if file.filename == '':
                return error_response('No file selected', 400)
            
            if file and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(f"student_{user.student.student_id}_{file.filename}")
                
                # Create upload directory if it doesn't exist
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                
                # Update student profile with photo path
                user.student.profile_photo = f"profiles/{filename}"
                db.session.commit()
                
                return api_response({
                    'photo_url': f"/uploads/profiles/{filename}"
                }, 'Photo uploaded successfully')
            
            return error_response('Invalid file type', 400)
            
        except Exception as e:
            logger.error(f"Error uploading photo: {str(e)}")
            return error_response('Failed to upload photo', 500)
        
@student_bp.route('/assessments/<int:assessment_id>', methods=['GET'])
@jwt_required()
@student_required
def get_assessment_detail(assessment_id):
    """Get detailed assessment information for submission"""
    try:
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        student_id = user.student.student_id
        
        # Get assessment details with submission status
        assessment = assessment_service.get_student_assessment_detail(student_id, assessment_id)
        
        if assessment:
            return api_response(assessment, 'Assessment details retrieved successfully')
        else:
            return error_response('Assessment not found or not available to you', 404)
            
    except Exception as e:
        logger.error(f"Error getting assessment detail: {str(e)}")
        return error_response('Failed to get assessment details', 500)
    
@student_bp.route('/assessments/<int:assessment_id>/submit', methods=['POST'])
@jwt_required()
@student_required
def submit_assessment(assessment_id):
    """Submit an assessment with text and/or file"""
    try:
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        student_id = user.student.student_id
        
        # Get enrollment for this assessment
        enrollment = db.session.query(Enrollment).join(
            CourseOffering, Enrollment.offering_id == CourseOffering.offering_id
        ).join(
            Assessment, Assessment.offering_id == CourseOffering.offering_id
        ).filter(
            Assessment.assessment_id == assessment_id,
            Enrollment.student_id == student_id
        ).first()
        
        if not enrollment:
            return error_response('You are not enrolled in this course', 403)
        
        # Handle both JSON and form data
        submission_text = None
        file_info = None
        submission_type = 'text'
        
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle file upload
            submission_text = request.form.get('submission_text')
            
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename:
                    # Save file
                    file_result, error = file_service.save_submission_file(
                        file, student_id, assessment_id
                    )
                    
                    if error:
                        return error_response(error, 400)
                    
                    file_info = file_result
                    submission_type = 'both' if submission_text else 'file'
        else:
            # Handle JSON data
            data = request.get_json()
            submission_text = data.get('submission_text')
            submission_type = 'text'
        
        # Validate that at least one type of submission is provided
        if not submission_text and not file_info:
            return error_response('Please provide either text or file submission', 400)
        
        # Create submission
        submission, error = assessment_service.create_submission(
            enrollment_id=enrollment.enrollment_id,
            assessment_id=assessment_id,
            submission_text=submission_text,
            file_info=file_info,
            submission_type=submission_type
        )
        
        if error:
            # Clean up uploaded file if submission failed
            if file_info:
                file_service.delete_file(file_info['file_path'])
            return error_response(error, 500)
        
        return api_response({
            'submission_id': submission.submission_id,
            'submitted_at': submission.submission_date.isoformat(),
            'is_late': submission.is_late,
            'submission_type': submission.submission_type
        }, 'Assessment submitted successfully')
        
    except Exception as e:
        logger.error(f"Error submitting assessment: {str(e)}")
        return error_response('Failed to submit assessment', 500)
    
@student_bp.route('/assessments/<int:assessment_id>/download', methods=['GET'])
@jwt_required()
@student_required
def download_submission(assessment_id):
    """Download submitted file"""
    try:
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        # Get submission
        submission = db.session.query(AssessmentSubmission).join(
            Enrollment, AssessmentSubmission.enrollment_id == Enrollment.enrollment_id
        ).filter(
            AssessmentSubmission.assessment_id == assessment_id,
            Enrollment.student_id == user.student.student_id
        ).first()
        
        if not submission or not submission.file_path:
            return error_response('No file found', 404)
        
        # Send file
        from flask import send_file
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        file_path = os.path.join(upload_folder, submission.file_path)
        
        if not os.path.exists(file_path):
            return error_response('File not found on server', 404)
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=submission.file_name,
            mimetype=submission.mime_type
        )
        
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return error_response('Failed to download file', 500)


@student_bp.route('/grades/summary', methods=['GET'])
@jwt_required()
@student_required
def get_grades_summary():
    """Get overall grades summary for the student"""
    try:
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return error_response('Student profile not found', 404)
        
        student_id = user.student.student_id
        
        # Get all assessments with grades using the assessment service
        assessments = assessment_service.get_student_assessments(student_id)
        
        # Calculate summary statistics
        graded_assessments = [a for a in assessments if a['score'] is not None]
        
        if graded_assessments:
            total_points = sum(a['score'] for a in graded_assessments)
            total_possible = sum(a['max_score'] for a in graded_assessments)
            overall_percentage = (total_points / total_possible * 100) if total_possible > 0 else 0
            
            # Count by grade
            grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
            for assessment in graded_assessments:
                percentage = assessment['percentage']
                if percentage >= 90:
                    grade_counts['A'] += 1
                elif percentage >= 80:
                    grade_counts['B'] += 1
                elif percentage >= 70:
                    grade_counts['C'] += 1
                elif percentage >= 60:
                    grade_counts['D'] += 1
                else:
                    grade_counts['F'] += 1
        else:
            overall_percentage = 0
            grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        
        summary = {
            'total_assessments': len(assessments),
            'graded_assessments': len(graded_assessments),
            'pending_assessments': len(assessments) - len(graded_assessments),
            'overall_percentage': round(overall_percentage, 2),
            'grade_distribution': grade_counts
        }
        
        return api_response(summary, 'Grades summary retrieved successfully')
        
    except Exception as e:
        logger.error(f"Error getting grades summary: {str(e)}")
        return error_response('Failed to get grades summary', 500)
    

    
@student_bp.route('/predictions', methods=['GET'])
@jwt_required()
def get_student_predictions():
    """Get all predictions for the current student"""
    try:
        user_id = get_jwt_identity()
        
        # Get student from user
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return error_response('Student profile not found', 404)
        
        # Get all enrollments for this student
        enrollments = Enrollment.query.filter_by(
            student_id=student.student_id,
            enrollment_status='enrolled'
        ).all()
        
        predictions_data = []
        
        for enrollment in enrollments:
            # Get latest prediction for each enrollment
            latest_prediction = prediction_service.get_latest_prediction(enrollment.enrollment_id)
            
            predictions_data.append({
                'enrollment_id': enrollment.enrollment_id,
                'course': {
                    'course_code': enrollment.offering.course.course_code,
                    'course_name': enrollment.offering.course.course_name,
                    'offering_id': enrollment.offering_id
                },
                'prediction': latest_prediction if latest_prediction else None
            })
        
        return api_response({
            'student': {
                'id': student.student_id,
                'name': f"{student.first_name} {student.last_name}"
            },
            'predictions': predictions_data
        })
        
    except Exception as e:
        logger.error(f"Error getting student predictions: {str(e)}")
        return error_response(f"Error retrieving predictions: {str(e)}")
    
@student_bp.route('/enrollments', methods=['GET'])
@jwt_required()
def get_student_enrollments():
    """Get all enrollments for the current student"""
    try:
        user_id = get_jwt_identity()
        
        # Get student from user
        student = Student.query.filter_by(user_id=user_id).first()
        if not student:
            return error_response('Student profile not found', 404)
        
        # Get enrollments
        enrollments = Enrollment.query.filter_by(
            student_id=student.student_id,
            enrollment_status='enrolled'
        ).all()
        
        enrollments_data = []
        for e in enrollments:
            enrollments_data.append({
                'enrollment_id': e.enrollment_id,
                'course_name': f"{e.offering.course.course_code} - {e.offering.course.course_name}",
                'course_code': e.offering.course.course_code,
                'offering_id': e.offering_id
            })
        
        return api_response(enrollments_data)
        
    except Exception as e:
        logger.error(f"Error getting enrollments: {str(e)}")
        return error_response(f"Error retrieving enrollments: {str(e)}")
    
@student_bp.route('/predictions/generate', methods=['POST'])
@jwt_required()
@student_required
def generate_student_predictions():
    """Generate new predictions for the current student"""
    try:
        # Get current user
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user or not user.student:
            return jsonify({
                'status': 'error',
                'message': 'Student profile not found'
            }), 404
        
        student_id = user.student.student_id
        
        # Import prediction service
        from backend.services.prediction_service import PredictionService
        prediction_service = PredictionService()
        
        # Get all active enrollments
        enrollments = Enrollment.query.filter(
            Enrollment.student_id == student_id,
            Enrollment.enrollment_status == 'enrolled'
        ).all()
        
        if not enrollments:
            return jsonify({
                'status': 'error',
                'message': 'No active enrollments found'
            }), 404
        
        results = []
        success_count = 0
        
        for enrollment in enrollments:
            try:
                # Generate prediction for this enrollment
                prediction = prediction_service.generate_prediction(
                    enrollment.enrollment_id,
                    save=True
                )
                
                # Add course info
                prediction['course_code'] = enrollment.offering.course.course_code
                prediction['course_name'] = enrollment.offering.course.course_name
                
                results.append({
                    'enrollment_id': enrollment.enrollment_id,
                    'course_code': enrollment.offering.course.course_code,
                    'status': 'success',
                    'prediction': prediction
                })
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to generate prediction for enrollment {enrollment.enrollment_id}: {str(e)}")
                results.append({
                    'enrollment_id': enrollment.enrollment_id,
                    'course_code': enrollment.offering.course.course_code,
                    'status': 'error',
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'message': f'Generated {success_count} predictions successfully',
            'data': {
                'results': results,
                'total_processed': len(results),
                'success_count': success_count,
                'error_count': len(results) - success_count
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating predictions: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate predictions: {str(e)}'
        }), 500

    
