# backend/services/course_service.py

from backend.models import (
    Course, CourseOffering, Enrollment, Student, Faculty,
    AcademicTerm
)
from backend.extensions import db
from sqlalchemy import and_, or_
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CourseService:
    """Service class for course-related operations"""
    
    @staticmethod
    def get_available_courses(student_id, term_id=None):
        """Get all courses available for enrollment"""
        try:
            # Get current term if not specified
            if not term_id:
                current_term = AcademicTerm.query.filter_by(is_current=True).first()
                if not current_term:
                    logger.warning("No current term found")
                    return []
                term_id = current_term.term_id
            
            # Get courses the student is already enrolled in
            enrolled_offerings = db.session.query(Enrollment.offering_id).filter(
                Enrollment.student_id == student_id,
                Enrollment.enrollment_status.in_(['enrolled', 'completed'])
            ).subquery()
            
            # Get available courses
            available = db.session.query(
                CourseOffering.offering_id,
                Course.course_id,
                Course.course_code,
                Course.course_name,
                Course.credits,
                CourseOffering.section_number,
                CourseOffering.capacity,
                CourseOffering.enrolled_count,
                CourseOffering.meeting_pattern,
                CourseOffering.location,
                Faculty.first_name.label('faculty_first_name'),
                Faculty.last_name.label('faculty_last_name')
            ).join(
                Course, Course.course_id == CourseOffering.course_id
            ).outerjoin(
                Faculty, Faculty.faculty_id == CourseOffering.faculty_id
            ).filter(
                CourseOffering.term_id == term_id,
                CourseOffering.offering_id.notin_(enrolled_offerings),
                CourseOffering.enrolled_count < CourseOffering.capacity
            ).all()
            
            # Format results
            courses = []
            for course in available:
                courses.append({
                    'offering_id': course.offering_id,
                    'course_id': course.course_id,
                    'course_code': course.course_code,
                    'course_name': course.course_name,
                    'credits': course.credits,
                    'section_number': course.section_number,
                    'available_seats': course.capacity - course.enrolled_count,
                    'meeting_pattern': course.meeting_pattern,
                    'location': course.location,
                    'instructor': f"{course.faculty_first_name} {course.faculty_last_name}" if course.faculty_first_name else "TBA"
                })
            
            return courses
            
        except Exception as e:
            logger.error(f"Error getting available courses: {str(e)}")
            return []
    
    @staticmethod
    def enroll_student(student_id, offering_id):
        """Enroll a student in a course"""
        try:
            # Check if offering exists and has space
            offering = CourseOffering.query.get(offering_id)
            if not offering:
                return None, "Course offering not found"
            
            if offering.enrolled_count >= offering.capacity:
                return None, "Course is full"
            
            # Check if already enrolled
            existing = Enrollment.query.filter_by(
                student_id=student_id,
                offering_id=offering_id
            ).first()
            
            if existing:
                if existing.enrollment_status == 'enrolled':
                    return None, "Already enrolled in this course"
                elif existing.enrollment_status == 'dropped':
                    # Re-enroll
                    existing.enrollment_status = 'enrolled'
                    existing.enrollment_date = datetime.utcnow().date()
                    offering.enrolled_count += 1
                    db.session.commit()
                    
                    # Return successful enrollment data
                    return {
                        'enrollment_id': existing.enrollment_id,
                        'message': 'Successfully re-enrolled in course'
                    }, None
            
            # Create new enrollment
            enrollment = Enrollment(
                student_id=student_id,
                offering_id=offering_id,
                enrollment_date=datetime.utcnow().date(),
                enrollment_status='enrolled'
            )
            
            # Update enrolled count
            offering.enrolled_count += 1
            
            db.session.add(enrollment)
            db.session.commit()
            
            # Return successful enrollment data
            return {
                'enrollment_id': enrollment.enrollment_id,
                'message': 'Successfully enrolled in course'
            }, None
            
        except Exception as e:
            logger.error(f"Error enrolling student: {str(e)}")
            db.session.rollback()
            return None, "Failed to enroll in course"
    
    @staticmethod
    def drop_course(student_id, offering_id):
        """Drop a course for a student"""
        try:
            # Find enrollment
            enrollment = Enrollment.query.filter_by(
                student_id=student_id,
                offering_id=offering_id,
                enrollment_status='enrolled'
            ).first()
            
            if not enrollment:
                return False, "Enrollment not found"
            
            # Update enrollment status
            enrollment.enrollment_status = 'dropped'
            
            # Update enrolled count
            offering = CourseOffering.query.get(offering_id)
            if offering:
                offering.enrolled_count = max(0, offering.enrolled_count - 1)
            
            db.session.commit()
            return True, "Course dropped successfully"
            
        except Exception as e:
            logger.error(f"Error dropping course: {str(e)}")
            db.session.rollback()
            return False, "Failed to drop course"
    
    @staticmethod
    def get_course_details(offering_id):
        """Get detailed information about a course offering"""
        try:
            course_data = db.session.query(
                CourseOffering.offering_id,
                Course.course_id,
                Course.course_code,
                Course.course_name,
                Course.credits,
                Course.description,
                CourseOffering.section_number,
                CourseOffering.capacity,
                CourseOffering.enrolled_count,
                CourseOffering.meeting_pattern,
                CourseOffering.location,
                Faculty.first_name.label('faculty_first_name'),
                Faculty.last_name.label('faculty_last_name'),
                Faculty.email.label('faculty_email'),
                AcademicTerm.term_name
            ).join(
                Course, Course.course_id == CourseOffering.course_id
            ).outerjoin(
                Faculty, Faculty.faculty_id == CourseOffering.faculty_id
            ).join(
                AcademicTerm, AcademicTerm.term_id == CourseOffering.term_id
            ).filter(
                CourseOffering.offering_id == offering_id
            ).first()
            
            if not course_data:
                return None
            
            return {
                'offering_id': course_data.offering_id,
                'course_id': course_data.course_id,
                'course_code': course_data.course_code,
                'course_name': course_data.course_name,
                'credits': course_data.credits,
                'description': course_data.description,
                'section_number': course_data.section_number,
                'capacity': course_data.capacity,
                'enrolled_count': course_data.enrolled_count,
                'available_seats': course_data.capacity - course_data.enrolled_count,
                'meeting_pattern': course_data.meeting_pattern,
                'location': course_data.location,
                'instructor': {
                    'name': f"{course_data.faculty_first_name} {course_data.faculty_last_name}" if course_data.faculty_first_name else "TBA",
                    'email': course_data.faculty_email
                },
                'term': course_data.term_name
            }
            
        except Exception as e:
            logger.error(f"Error getting course details: {str(e)}")
            return None

# Instantiate service
course_service = CourseService()