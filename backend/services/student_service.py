from backend.models import (
    Student, Enrollment, Course, Assessment, Attendance, 
    CourseOffering, Prediction, AssessmentSubmission,Faculty, AcademicTerm, User
)
from backend.extensions import db
from sqlalchemy import func, and_, desc 
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StudentService:
    """Service class for student-related operations"""
    
    @staticmethod
    def get_student_by_user_id(user_id):
        """Get student record by user ID"""
        try:
            student = Student.query.filter_by(user_id=user_id).first()
            return student
        except Exception as e:
            logger.error(f"Error getting student: {str(e)}")
            return None
        
    @staticmethod
    def update_student_profile(student_id, profile_data):
        """Update student profile"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return None, "Student not found"
            
            # Update allowed fields
            allowed_fields = [
                'first_name', 'last_name', 'date_of_birth', 
                'gender', 'program_code', 'year_of_study'
            ]
            
            for field in allowed_fields:
                if field in profile_data:
                    setattr(student, field, profile_data[field])
            
            db.session.commit()
            return student, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating student profile: {str(e)}")
            return None, str(e)
    
    
    @staticmethod
    def get_enrolled_courses(student_id, term_id=None):
        """Get all courses enrolled by a student"""
        try:
            # ✅ FIX: First, let's check what fields Faculty actually has
            # Get faculty email from User table instead of Faculty table
            query = db.session.query(
                Course.course_id,
                Course.course_code,
                Course.course_name,
                Course.credits,
                CourseOffering.offering_id,
                CourseOffering.section_number,
                CourseOffering.meeting_pattern,
                CourseOffering.location,
                Enrollment.enrollment_id,
                Enrollment.enrollment_status,
                Enrollment.final_grade,
                Faculty.first_name.label('instructor_first_name'),
                Faculty.last_name.label('instructor_last_name'),
                # ✅ FIX: Get email from User table via faculty relationship
                User.email.label('instructor_email')
            ).select_from(Course).join(
                CourseOffering, CourseOffering.course_id == Course.course_id
            ).join(
                Enrollment, Enrollment.offering_id == CourseOffering.offering_id
            ).outerjoin(
                Faculty, Faculty.faculty_id == CourseOffering.faculty_id
            ).outerjoin(
                # ✅ FIX: Join with User table to get email
                User, User.user_id == Faculty.user_id
            ).filter(
                Enrollment.student_id == student_id
            )
            
            # Filter by term if provided
            if term_id:
                query = query.filter(CourseOffering.term_id == term_id)
            else:
                # Get current term courses if no term specified
                current_term = AcademicTerm.query.filter_by(is_current=True).first()
                if current_term:
                    query = query.filter(CourseOffering.term_id == current_term.term_id)
            
            courses = query.all()
            
            result = []
            for course in courses:
                # Calculate attendance rate for this course
                attendance_rate = StudentService._calculate_course_attendance_rate(
                    course.enrollment_id
                )
                
                # Get latest prediction for this enrollment
                latest_prediction = Prediction.query.filter_by(
                    enrollment_id=course.enrollment_id
                ).order_by(desc(Prediction.prediction_date)).first()
                
                # Get next upcoming assessment
                next_assessment = StudentService._get_next_assessment(course.offering_id)
                
                course_data = {
                    'course_id': course.course_id,
                    'course_code': course.course_code,
                    'course_name': course.course_name,
                    'credits': course.credits,
                    'offering_id': course.offering_id,
                    'section': course.section_number,
                    'meeting_pattern': course.meeting_pattern,
                    'location': course.location,
                    'enrollment_id': course.enrollment_id,
                    'enrollment_status': course.enrollment_status,
                    'current_grade': course.final_grade,
                    'attendance_rate': attendance_rate,
                    'instructor_name': f"{course.instructor_first_name} {course.instructor_last_name}" if course.instructor_first_name else 'TBA',
                    'instructor_email': course.instructor_email,  # Now safely from User table
                    'predicted_grade': latest_prediction.predicted_grade if latest_prediction else None,
                    'risk_level': latest_prediction.risk_level if latest_prediction else None,
                    'confidence_score': float(latest_prediction.confidence_score) if latest_prediction else None,
                    'next_assessment': next_assessment
                }
                
                result.append(course_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting enrolled courses: {str(e)}")
            import traceback
            traceback.print_exc()  # This will help us debug further if needed
            return []
    
    @staticmethod
    def get_attendance_summary(student_id, course_id=None):
        """Get attendance summary for student"""
        try:
            # Base query for enrollments
            query = db.session.query(
                Enrollment.enrollment_id,
                Course.course_code,
                Course.course_name,
                CourseOffering.offering_id
            ).join(
                CourseOffering, CourseOffering.offering_id == Enrollment.offering_id
            ).join(
                Course, Course.course_id == CourseOffering.course_id
            ).filter(
                Enrollment.student_id == student_id,
                Enrollment.enrollment_status == 'enrolled'
            )
            
            # Filter by specific course if provided
            if course_id:
                query = query.filter(Course.course_id == course_id)
            
            enrollments = query.all()
            
            attendance_data = []
            for enrollment in enrollments:
                # Get attendance records for this enrollment
                attendance_records = Attendance.query.filter_by(
                    enrollment_id=enrollment.enrollment_id
                ).all()
                
                total_classes = len(attendance_records)
                present_count = len([a for a in attendance_records if a.status == 'present'])
                absent_count = len([a for a in attendance_records if a.status == 'absent'])
                late_count = len([a for a in attendance_records if a.status == 'late'])
                
                attendance_rate = (present_count / total_classes * 100) if total_classes > 0 else 0
                
                attendance_data.append({
                    'enrollment_id': enrollment.enrollment_id,
                    'course_code': enrollment.course_code,
                    'course_name': enrollment.course_name,
                    'offering_id': enrollment.offering_id,
                    'total_classes': total_classes,
                    'present_count': present_count,
                    'absent_count': absent_count,
                    'late_count': late_count,
                    'attendance_rate': round(attendance_rate, 2)
                })
            
            return attendance_data
            
        except Exception as e:
            logger.error(f"Error getting attendance summary: {str(e)}")
            return []
    
    @staticmethod
    def get_assessments(student_id, course_id=None):
        """Get assessments for a student"""
        try:
            # Fixed query with proper joins
            query = db.session.query(
                Assessment.assessment_id,
                Assessment.title,
                Assessment.max_score,
                Assessment.due_date,
                Course.course_name,
                Course.course_code,
                AssessmentSubmission.score
            ).select_from(Assessment).join(
                CourseOffering, Assessment.offering_id == CourseOffering.offering_id
            ).join(
                Course, CourseOffering.course_id == Course.course_id
            ).join(
                Enrollment, Enrollment.offering_id == CourseOffering.offering_id
            ).outerjoin(
                AssessmentSubmission, 
                and_(
                    AssessmentSubmission.assessment_id == Assessment.assessment_id,
                    AssessmentSubmission.enrollment_id == Enrollment.enrollment_id
                )
            ).filter(
                Enrollment.student_id == student_id,
                Enrollment.enrollment_status == 'enrolled'
            )
            
            if course_id:
                query = query.filter(CourseOffering.course_id == course_id)
            
            assessments = query.all()
            
            # Format results
            result = []
            for assessment in assessments:
                result.append({
                    'assessment_id': assessment.assessment_id,
                    'title': assessment.title,
                    'max_score': float(assessment.max_score) if assessment.max_score else 0,
                    'due_date': assessment.due_date.isoformat() if assessment.due_date else None,
                    'course_name': assessment.course_name,
                    'course_code': assessment.course_code,
                    'score': float(assessment.score) if assessment.score else None,
                    'percentage': round((float(assessment.score) / float(assessment.max_score)) * 100, 2) if assessment.score and assessment.max_score else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting assessments: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_grade_predictions(student_id):
        """Get grade predictions for a student"""
        try:
            predictions = db.session.query(
                Prediction.prediction_id,
                Prediction.predicted_grade,
                Prediction.confidence_score,
                Prediction.prediction_date,
                CourseOffering.course_id,
                Course.course_code,
                Course.course_name
            ).select_from(Prediction).join(
                Enrollment, Enrollment.enrollment_id == Prediction.enrollment_id
            ).join(
                CourseOffering, Enrollment.offering_id == CourseOffering.offering_id
            ).join(
                Course, CourseOffering.course_id == Course.course_id
            ).filter(
                Enrollment.student_id == student_id,
                Enrollment.enrollment_status == 'enrolled'
            ).order_by(
                Prediction.prediction_date.desc()
            ).all()
            
            # Get only the latest prediction for each course
            latest_predictions = {}
            for pred in predictions:
                if pred.course_id not in latest_predictions:
                    latest_predictions[pred.course_id] = {
                        'prediction_id': pred.prediction_id,
                        'course_id': pred.course_id,
                        'course_code': pred.course_code,
                        'course_name': pred.course_name,
                        'predicted_grade': pred.predicted_grade,
                        'confidence_score': float(pred.confidence_score),
                        'prediction_date': pred.prediction_date.isoformat()
                    }
            
            return list(latest_predictions.values())
            
        except Exception as e:
            logger.error(f"Error getting grade predictions: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_dashboard_summary(student_id):
        """Get dashboard summary for student"""
        try:
            # Get current term enrollments
            current_term = AcademicTerm.query.filter_by(is_current=True).first()
            if not current_term:
                return StudentService._get_default_summary()
            
            enrollments = db.session.query(Enrollment).join(
                CourseOffering, CourseOffering.offering_id == Enrollment.offering_id
            ).filter(
                Enrollment.student_id == student_id,
                CourseOffering.term_id == current_term.term_id,
                Enrollment.enrollment_status == 'enrolled'
            ).all()
            
            if not enrollments:
                return StudentService._get_default_summary()
            
            # Calculate total credits
            total_credits = db.session.query(
                func.sum(Course.credits)
            ).join(
                CourseOffering, CourseOffering.course_id == Course.course_id
            ).join(
                Enrollment, Enrollment.offering_id == CourseOffering.offering_id
            ).filter(
                Enrollment.student_id == student_id,
                CourseOffering.term_id == current_term.term_id,
                Enrollment.enrollment_status == 'enrolled'
            ).scalar() or 0
            
            # Calculate overall attendance rate
            total_attendance_records = 0
            total_present = 0
            
            for enrollment in enrollments:
                attendance_records = Attendance.query.filter_by(
                    enrollment_id=enrollment.enrollment_id
                ).all()
                
                total_attendance_records += len(attendance_records)
                total_present += len([a for a in attendance_records if a.status == 'present'])
            
            overall_attendance_rate = (total_present / total_attendance_records * 100) if total_attendance_records > 0 else 0
            
            # Calculate GPA from current grades
            grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
            total_grade_points = 0
            total_credits_with_grades = 0
            
            for enrollment in enrollments:
                if enrollment.final_grade and enrollment.final_grade in grade_points:
                    course_credits = db.session.query(Course.credits).join(
                        CourseOffering, CourseOffering.course_id == Course.course_id
                    ).filter(
                        CourseOffering.offering_id == enrollment.offering_id
                    ).scalar() or 0
                    
                    total_grade_points += grade_points[enrollment.final_grade] * course_credits
                    total_credits_with_grades += course_credits
            
            current_gpa = total_grade_points / total_credits_with_grades if total_credits_with_grades > 0 else 0
            
            # Count upcoming assessments
            upcoming_assessments = db.session.query(Assessment).join(
                CourseOffering, CourseOffering.offering_id == Assessment.offering_id
            ).join(
                Enrollment, Enrollment.offering_id == CourseOffering.offering_id
            ).filter(
                Enrollment.student_id == student_id,
                Assessment.due_date >= datetime.now(),
                Enrollment.enrollment_status == 'enrolled'
            ).count()
            
            # Count at-risk courses
            at_risk_courses = 0
            for enrollment in enrollments:
                latest_prediction = Prediction.query.filter_by(
                    enrollment_id=enrollment.enrollment_id
                ).order_by(desc(Prediction.prediction_date)).first()
                
                if latest_prediction and latest_prediction.risk_level in ['high', 'very_high']:
                    at_risk_courses += 1
            
            return {
                'course_count': len(enrollments),
                'total_credits': total_credits,
                'gpa': round(current_gpa, 2),
                'attendance_rate': round(overall_attendance_rate, 1),
                'upcoming_assessments': upcoming_assessments,
                'at_risk_courses': at_risk_courses
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {str(e)}")
            return StudentService._get_default_summary()
        
    @staticmethod
    def _calculate_course_attendance_rate(enrollment_id):
        """Calculate attendance rate for a specific enrollment"""
        try:
            attendance_records = Attendance.query.filter_by(
                enrollment_id=enrollment_id
            ).all()
            
            if not attendance_records:
                return 0
            
            present_count = len([a for a in attendance_records if a.status == 'present'])
            total_count = len(attendance_records)
            
            return round((present_count / total_count) * 100, 2)
            
        except Exception as e:
            logger.error(f"Error calculating attendance rate: {str(e)}")
            return 0

    @staticmethod
    def _get_next_assessment(offering_id):
        """Get the next upcoming assessment for a course offering"""
        try:
            next_assessment = Assessment.query.filter(
                Assessment.offering_id == offering_id,
                Assessment.due_date >= datetime.now()
            ).order_by(Assessment.due_date).first()
            
            if next_assessment:
                return f"{next_assessment.title} (Due: {next_assessment.due_date.strftime('%m/%d/%Y')})"
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting next assessment: {str(e)}")
            return None
        
    @staticmethod
    def _get_default_summary():
        """Return default summary when no data is available"""
        return {
            'course_count': 0,
            'total_credits': 0,
            'gpa': 0,
            'attendance_rate': 0,
            'upcoming_assessments': 0,
            'at_risk_courses': 0
        }

# Create service instance
student_service = StudentService()