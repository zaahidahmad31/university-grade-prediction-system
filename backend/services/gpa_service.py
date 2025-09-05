from backend.extensions import db
from backend.models.user import Student
from backend.models.academic import Enrollment, Course, CourseOffering
from backend.models.assessment import Assessment, AssessmentSubmission, AssessmentType
from sqlalchemy import func, and_
import logging

logger = logging.getLogger(__name__)

class GPAService:
    
    # Grade point mapping
    GRADE_POINTS = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'D-': 0.7,
        'F': 0.0
    }
    
    @staticmethod
    def calculate_letter_grade(percentage):
        """Convert percentage to letter grade"""
        if percentage >= 93: return 'A'
        elif percentage >= 90: return 'A-'
        elif percentage >= 87: return 'B+'
        elif percentage >= 83: return 'B'
        elif percentage >= 80: return 'B-'
        elif percentage >= 77: return 'C+'
        elif percentage >= 73: return 'C'
        elif percentage >= 70: return 'C-'
        elif percentage >= 67: return 'D+'
        elif percentage >= 63: return 'D'
        elif percentage >= 60: return 'D-'
        else: return 'F'
    
    @staticmethod
    def calculate_gpa(student_id, term_id=None):
        """Calculate GPA for a student"""
        try:
            # Build query for enrollments
            query = db.session.query(
                Enrollment.enrollment_id,
                Enrollment.final_grade,
                Enrollment.grade_points,
                Course.credits
            ).join(
                CourseOffering,
                Enrollment.offering_id == CourseOffering.offering_id
            ).join(
                Course,
                CourseOffering.course_id == Course.course_id
            ).filter(
                Enrollment.student_id == student_id,
                Enrollment.enrollment_status.in_(['enrolled', 'completed']),
                Enrollment.grade_points.isnot(None)
            )
            
            # Filter by term if specified
            if term_id:
                query = query.filter(CourseOffering.term_id == term_id)
            
            enrollments = query.all()
            
            if not enrollments:
                return 0.0
            
            # Calculate GPA
            total_grade_points = 0
            total_credit_hours = 0
            
            for enrollment in enrollments:
                credit_hours = enrollment.credits or 3  # Default 3 credits
                grade_points = float(enrollment.grade_points) if enrollment.grade_points else 0
                
                total_grade_points += grade_points * credit_hours
                total_credit_hours += credit_hours
            
            if total_credit_hours == 0:
                return 0.0
            
            gpa = total_grade_points / total_credit_hours
            return round(gpa, 2)
            
        except Exception as e:
            logger.error(f"Error calculating GPA: {str(e)}")
            return 0.0
    
    @staticmethod
    def update_student_gpa(student_id, term_id=None):
        """Update student's GPA in the database"""
        try:
            # Calculate GPA
            gpa = GPAService.calculate_gpa(student_id, term_id)
            
            # Update student record
            student = Student.query.get(student_id)
            if student:
                student.gpa = gpa
                db.session.commit()
            
            return gpa
            
        except Exception as e:
            logger.error(f"Error updating student GPA: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def get_course_grade_summary(offering_id):
        """Get grade summary for all students in a course"""
        try:
            # Get all enrollments with assessment details
            enrollments = db.session.query(
                Enrollment.enrollment_id,
                Enrollment.student_id,
                Student.first_name,
                Student.last_name,
                Enrollment.final_grade,
                Enrollment.grade_points
            ).join(
                Student,
                Enrollment.student_id == Student.student_id
            ).filter(
                Enrollment.offering_id == offering_id,
                Enrollment.enrollment_status == 'enrolled'
            ).all()
            
            results = []
            
            for enrollment in enrollments:
                # Get assessment summary
                assessment_summary = GPAService._get_assessment_summary(enrollment.enrollment_id)
                
                # Calculate suggested grade
                if assessment_summary['total_percentage'] is not None:
                    suggested_grade = GPAService.calculate_letter_grade(
                        assessment_summary['total_percentage']
                    )
                    suggested_points = GPAService.GRADE_POINTS.get(suggested_grade, 0)
                else:
                    suggested_grade = None
                    suggested_points = None
                
                results.append({
                    'enrollment_id': enrollment.enrollment_id,
                    'student_id': enrollment.student_id,
                    'student_name': f"{enrollment.first_name} {enrollment.last_name}",
                    'assessments': assessment_summary['breakdown'],
                    'total_percentage': assessment_summary['total_percentage'],
                    'suggested_grade': suggested_grade,
                    'suggested_points': suggested_points,
                    'final_grade': enrollment.final_grade,
                    'grade_points': float(enrollment.grade_points) if enrollment.grade_points else None,
                    'is_finalized': enrollment.final_grade is not None
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting course grade summary: {str(e)}")
            return []

    @staticmethod
    def _get_assessment_summary(enrollment_id):
        """Get assessment breakdown for an enrollment (simplified version)"""
        try:
            # Get all assessments for this enrollment
            assessments = db.session.query(
                Assessment.assessment_id,
                Assessment.title,
                Assessment.weight,
                Assessment.max_score,
                AssessmentSubmission.score,
                AssessmentSubmission.percentage
            ).outerjoin(
                AssessmentSubmission,
                and_(
                    Assessment.assessment_id == AssessmentSubmission.assessment_id,
                    AssessmentSubmission.enrollment_id == enrollment_id
                )
            ).filter(
                Assessment.offering_id == db.session.query(Enrollment.offering_id)
                    .filter(Enrollment.enrollment_id == enrollment_id).scalar_subquery()
            ).all()
            
            breakdown = []
            total_weighted = 0
            total_weight = 0
            
            # Group by assessment type (you can customize this)
            assessment_types = {}
            
            for assessment in assessments:
                # Simple type detection based on title
                if 'quiz' in assessment.title.lower():
                    type_name = 'Quiz'
                elif 'assignment' in assessment.title.lower():
                    type_name = 'Assignment'
                elif 'midterm' in assessment.title.lower():
                    type_name = 'Midterm Exam'
                elif 'final' in assessment.title.lower():
                    type_name = 'Final Exam'
                else:
                    type_name = 'Other'
                
                if type_name not in assessment_types:
                    assessment_types[type_name] = {
                        'scores': [],
                        'weight': 0
                    }
                
                if assessment.percentage is not None:
                    assessment_types[type_name]['scores'].append(float(assessment.percentage))
                    if assessment.weight:
                        assessment_types[type_name]['weight'] += float(assessment.weight)
            
            # Calculate averages
            for type_name, data in assessment_types.items():
                if data['scores']:
                    avg_score = sum(data['scores']) / len(data['scores'])
                    weight = data['weight'] / len(data['scores']) if data['weight'] else 25  # Default 25%
                    
                    breakdown.append({
                        'type': type_name,
                        'weight': weight,
                        'average': round(avg_score, 2)
                    })
                    
                    total_weighted += avg_score * weight
                    total_weight += weight
                else:
                    breakdown.append({
                        'type': type_name,
                        'weight': 25,  # Default weight
                        'average': None
                    })
            
            # Default breakdown if no assessments
            if not breakdown:
                breakdown = [
                    {'type': 'Quiz', 'weight': 20, 'average': None},
                    {'type': 'Assignment', 'weight': 30, 'average': None},
                    {'type': 'Midterm Exam', 'weight': 25, 'average': None},
                    {'type': 'Final Exam', 'weight': 25, 'average': None}
                ]
            
            total_percentage = (total_weighted / total_weight) if total_weight > 0 else None
            
            return {
                'breakdown': breakdown,
                'total_percentage': round(total_percentage, 2) if total_percentage else None
            }
            
        except Exception as e:
            logger.error(f"Error getting assessment summary: {str(e)}")
            return {'breakdown': [], 'total_percentage': None}

    @staticmethod
    def finalize_grade(enrollment_id, final_grade, override_reason=None):
        """Finalize a single student's grade"""
        try:
            enrollment = Enrollment.query.get(enrollment_id)
            if not enrollment:
                return False, "Enrollment not found"
            
            # Validate grade
            if final_grade not in GPAService.GRADE_POINTS:
                return False, "Invalid grade"
            
            # Get assessment summary to check if override
            summary = GPAService._get_assessment_summary(enrollment_id)
            suggested_grade = None
            
            if summary['total_percentage'] is not None:
                suggested_grade = GPAService.calculate_letter_grade(summary['total_percentage'])
            
            # Store the grade
            enrollment.final_grade = final_grade
            enrollment.grade_points = GPAService.GRADE_POINTS[final_grade]
            
            # If grade was overridden, log it
            if suggested_grade and suggested_grade != final_grade:
                logger.info(f"Grade override for enrollment {enrollment_id}: "
                           f"Suggested: {suggested_grade}, Final: {final_grade}, "
                           f"Reason: {override_reason}")
            
            db.session.commit()
            
            # Update student's GPA
            GPAService.update_student_gpa(enrollment.student_id)
            
            return True, "Grade finalized successfully"
            
        except Exception as e:
            logger.error(f"Error finalizing grade: {str(e)}")
            db.session.rollback()
            return False, "Failed to finalize grade"

# Create service instance
gpa_service = GPAService()