# backend/services/assessment_service.py - FIXED VERSION
from backend.models import (
    Assessment, AssessmentType, AssessmentSubmission, Enrollment, 
    Student, CourseOffering, Course,User 
)
from backend.extensions import db
from datetime import datetime, date
from sqlalchemy import func, and_, desc
import logging
import os
from flask import send_file, current_app
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

class AssessmentService:
    """Service class for assessment-related operations"""
    
    @staticmethod
    def get_assessment_types():
        """Get all available assessment types"""
        try:
            assessment_types = AssessmentType.query.all()
            return [at.to_dict() for at in assessment_types]
        except Exception as e:
            logger.error(f"Error getting assessment types: {str(e)}")
            return []
    
    @staticmethod
    def create_assessment(offering_id, type_id, title, max_score, due_date=None, weight=None, description=None, created_by=None):
        """Create a new assessment"""
        try:
            # ✅ FIXED: Handle multiple date formats from frontend
            if isinstance(due_date, str) and due_date:
                try:
                    # Try ISO format first (what frontend sends): 2025-06-20T18:29
                    if 'T' in due_date:
                        due_date = datetime.fromisoformat(due_date)
                    else:
                        # Fallback to space format: 2025-06-20 18:29
                        due_date = datetime.strptime(due_date, '%Y-%m-%d %H:%M')
                except ValueError as e:
                    logger.error(f"Error parsing due_date '{due_date}': {str(e)}")
                    # If parsing fails, set to None (optional field)
                    due_date = None
            
            assessment = Assessment(
                offering_id=offering_id,
                type_id=type_id,
                title=title,
                max_score=max_score,
                due_date=due_date,
                weight=weight,
                description=description,
                is_published=True
            )
            
            db.session.add(assessment)
            db.session.commit()
            
            logger.info(f"Assessment created: {title} for offering {offering_id}")
            return assessment
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating assessment: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def get_assessments_by_offering(offering_id, include_unpublished=False):
        """Get all assessments for a course offering"""
        try:
            query = db.session.query(
                Assessment.assessment_id,
                Assessment.title,
                Assessment.max_score,
                Assessment.due_date,
                Assessment.weight,
                Assessment.description,
                Assessment.is_published,
                Assessment.created_at,
                AssessmentType.type_name,
                AssessmentType.type_id
            ).join(
                AssessmentType, AssessmentType.type_id == Assessment.type_id
            ).filter(
                Assessment.offering_id == offering_id
            )
            
            if not include_unpublished:
                query = query.filter(Assessment.is_published == True)
            
            assessments = query.order_by(Assessment.due_date.asc()).all()
            
            result = []
            for assessment in assessments:
                # Get submission statistics
                total_students = Enrollment.query.filter_by(
                    offering_id=offering_id,
                    enrollment_status='enrolled'
                ).count()
                
                submitted_count = AssessmentSubmission.query.filter_by(
                    assessment_id=assessment.assessment_id
                ).count()
                
                graded_count = AssessmentSubmission.query.filter_by(
                    assessment_id=assessment.assessment_id
                ).filter(
                    AssessmentSubmission.score.isnot(None)
                ).count()
                
                # Calculate average score
                avg_score = db.session.query(
                    func.avg(AssessmentSubmission.score)
                ).filter_by(
                    assessment_id=assessment.assessment_id
                ).filter(
                    AssessmentSubmission.score.isnot(None)
                ).scalar()
                
                result.append({
                    'assessment_id': assessment.assessment_id,
                    'title': assessment.title,
                    'type_name': assessment.type_name,
                    'type_id': assessment.type_id,
                    'max_score': float(assessment.max_score),
                    'due_date': assessment.due_date.isoformat() if assessment.due_date else None,
                    'weight': float(assessment.weight) if assessment.weight else None,
                    'description': assessment.description,
                    'is_published': assessment.is_published,
                    'created_at': assessment.created_at.isoformat() if assessment.created_at else None,
                    'statistics': {
                        'total_students': total_students,
                        'submitted_count': submitted_count,
                        'graded_count': graded_count,
                        'submission_rate': round((submitted_count / total_students * 100) if total_students > 0 else 0, 2),
                        'grading_progress': round((graded_count / total_students * 100) if total_students > 0 else 0, 2),
                        'average_score': round(float(avg_score), 2) if avg_score else None
                    }
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting assessments: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_assessment_roster(assessment_id, faculty_id=None):
        """Get roster of students for grade entry with submission information"""
        try:
            # Get the assessment and course info
            assessment = Assessment.query.get(assessment_id)
            if not assessment:
                logger.warning(f"Assessment {assessment_id} not found")
                return None
            
            # SECURITY CHECK: Verify faculty teaches this course
            if faculty_id:
                offering = CourseOffering.query.get(assessment.offering_id)
                if not offering or offering.faculty_id != faculty_id:
                    logger.warning(f"Faculty {faculty_id} attempted to access assessment {assessment_id} they don't teach")
                    return None
            
            # IMPROVED QUERY: Include submission information
            students = db.session.query(
                Student.student_id,
                Student.first_name,
                Student.last_name,
                Enrollment.enrollment_id,
                AssessmentSubmission.submission_id,
                AssessmentSubmission.score,
                AssessmentSubmission.percentage,
                AssessmentSubmission.submission_date,
                AssessmentSubmission.is_late,
                AssessmentSubmission.feedback,
                # NEW: Include submission content info
                AssessmentSubmission.submission_text,
                AssessmentSubmission.file_path,
                AssessmentSubmission.file_name
            ).select_from(Enrollment)\
            .join(Student, Student.student_id == Enrollment.student_id)\
            .outerjoin(
                AssessmentSubmission,
                db.and_(
                    AssessmentSubmission.enrollment_id == Enrollment.enrollment_id,
                    AssessmentSubmission.assessment_id == assessment_id
                )
            ).filter(
                Enrollment.offering_id == assessment.offering_id,
                Enrollment.enrollment_status == 'enrolled'
            ).order_by(Student.last_name, Student.first_name).all()
            
            # Process results with enhanced submission info
            roster = []
            for student in students:
                try:
                    # Safe type conversion with validation
                    score_val = None
                    percentage_val = None
                    
                    if student.score is not None:
                        try:
                            score_val = float(student.score)
                        except (ValueError, TypeError) as e:
                            logger.error(f"Invalid score value for student {student.student_id}: {student.score}")
                            score_val = None
                    
                    if student.percentage is not None:
                        try:
                            percentage_val = float(student.percentage)
                        except (ValueError, TypeError) as e:
                            logger.error(f"Invalid percentage value for student {student.student_id}: {student.percentage}")
                            percentage_val = None
                    
                    # Safe date conversion
                    submission_date_str = None
                    if student.submission_date:
                        try:
                            submission_date_str = student.submission_date.isoformat()
                        except AttributeError:
                            logger.error(f"Invalid submission_date for student {student.student_id}")
                    
                    # NEW: Determine submission content availability
                    has_text = bool(student.submission_text)
                    has_file = bool(student.file_path)
                    
                    roster.append({
                        'student_id': student.student_id,
                        'enrollment_id': student.enrollment_id,
                        'name': f"{student.first_name} {student.last_name}",
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                        'submission_id': student.submission_id,
                        'score': score_val,
                        'percentage': percentage_val,
                        'submission_date': submission_date_str,
                        'is_late': bool(student.is_late) if student.is_late is not None else False,
                        'feedback': student.feedback,
                        # NEW: Include submission content info
                        'submission_text': student.submission_text,
                        'has_file': has_file,
                        'file_name': student.file_name,
                        'status': 'graded' if score_val is not None else ('submitted' if student.submission_id else 'not_submitted')
                    })
                    
                except Exception as student_error:
                    logger.error(f"Error processing student {student.student_id}: {str(student_error)}")
                    continue
            
            # Safe assessment data conversion
            assessment_data = {
                'assessment_id': assessment.assessment_id,
                'title': assessment.title,
                'max_score': float(assessment.max_score) if assessment.max_score else 0.0,
                'due_date': assessment.due_date.isoformat() if assessment.due_date else None
            }
            
            return {
                'assessment': assessment_data,
                'roster': roster
            }
            
        except Exception as e:
            logger.error(f"Error getting assessment roster: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def enter_grade(enrollment_id, assessment_id, score, feedback=None, graded_by=None):
        """Enter or update a grade for a student"""
        try:
            # Get the assessment to validate score
            assessment = Assessment.query.get(assessment_id)
            if not assessment:
                return None, "Assessment not found"
            
            # Validate score
            if score < 0 or score > float(assessment.max_score):
                return None, f"Score must be between 0 and {assessment.max_score}"
            
            # Check if submission already exists
            existing_submission = AssessmentSubmission.query.filter_by(
                enrollment_id=enrollment_id,
                assessment_id=assessment_id
            ).first()
            
            if existing_submission:
                # Update existing submission
                existing_submission.score = score
                existing_submission.percentage = (score / float(assessment.max_score)) * 100
                existing_submission.feedback = feedback
                existing_submission.graded_date = datetime.utcnow()
                existing_submission.graded_by = graded_by
                submission = existing_submission
            else:
                # Create new submission
                submission = AssessmentSubmission(
                    enrollment_id=enrollment_id,
                    assessment_id=assessment_id,
                    submission_date=datetime.utcnow(),  # Auto-submit when graded
                    score=score,
                    percentage=(score / float(assessment.max_score)) * 100,
                    feedback=feedback,
                    graded_date=datetime.utcnow(),
                    graded_by=graded_by
                )
                db.session.add(submission)
            
            db.session.commit()
            return submission, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error entering grade: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, str(e)
    
    @staticmethod
    def bulk_enter_grades(grades_data, graded_by=None):
        """Enter grades for multiple students"""
        try:
            results = []
            
            for grade_data in grades_data:
                submission, error = AssessmentService.enter_grade(
                    enrollment_id=grade_data['enrollment_id'],
                    assessment_id=grade_data['assessment_id'],
                    score=grade_data['score'],
                    feedback=grade_data.get('feedback'),
                    graded_by=graded_by
                )
                
                if submission:
                    results.append({
                        'enrollment_id': grade_data['enrollment_id'],
                        'success': True,
                        'submission_id': submission.submission_id
                    })
                else:
                    results.append({
                        'enrollment_id': grade_data['enrollment_id'],
                        'success': False,
                        'error': error
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk grade entry: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_student_assessments(student_id, offering_id=None):
        """Get all assessments for a student"""
        try:
            query = db.session.query(
                Assessment,  # Get the full Assessment object
                AssessmentType,
                Course,
                CourseOffering,
                AssessmentSubmission
            ).join(
                CourseOffering, CourseOffering.offering_id == Assessment.offering_id
            ).join(
                Course, Course.course_id == CourseOffering.course_id
            ).join(
                AssessmentType, AssessmentType.type_id == Assessment.type_id
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
                Enrollment.enrollment_status == 'enrolled',
                Assessment.is_published == True
            )
            
            if offering_id:
                query = query.filter(Assessment.offering_id == offering_id)
            
            assessments = query.order_by(Assessment.due_date.desc()).all()
            
            result = []
            for assessment, assessment_type, course, offering, submission in assessments:
                result.append({
                    'assessment_id': assessment.assessment_id,  # Make sure this is included
                    'title': assessment.title,
                    'type_name': assessment_type.type_name,
                    'course_code': course.course_code,
                    'course_name': course.course_name,
                    'max_score': float(assessment.max_score),
                    'due_date': assessment.due_date.isoformat() if assessment.due_date else None,
                    'weight': float(assessment.weight) if assessment.weight else None,
                    'description': assessment.description,
                    'score': float(submission.score) if submission and submission.score is not None else None,
                    'percentage': float(submission.percentage) if submission and submission.percentage is not None else None,
                    'submission_date': submission.submission_date.isoformat() if submission and submission.submission_date else None,
                    'feedback': submission.feedback if submission else None,
                    'is_late': submission.is_late if submission else False,
                    'status': 'graded' if submission and submission.score is not None else ('submitted' if submission else 'pending')
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting student assessments: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_assessment_statistics(assessment_id):
        """Get detailed statistics for an assessment"""
        try:
            assessment = Assessment.query.get(assessment_id)
            if not assessment:
                return None
            
            # Get all submissions with scores
            submissions = AssessmentSubmission.query.filter_by(
                assessment_id=assessment_id
            ).filter(
                AssessmentSubmission.score.isnot(None)
            ).all()
            
            if not submissions:
                return {
                    'assessment_id': assessment_id,
                    'title': assessment.title,
                    'total_submissions': 0,
                    'statistics': None
                }
            
            scores = [float(s.score) for s in submissions]
            max_score = float(assessment.max_score)
            
            # Calculate statistics
            stats = {
                'total_submissions': len(scores),
                'average_score': round(sum(scores) / len(scores), 2),
                'average_percentage': round((sum(scores) / len(scores)) / max_score * 100, 2),
                'highest_score': max(scores),
                'lowest_score': min(scores),
                'median_score': round(sorted(scores)[len(scores) // 2], 2),
                'grade_distribution': {}
            }
            
            # Calculate grade distribution
            for score in scores:
                percentage = (score / max_score) * 100
                if percentage >= 90:
                    grade = 'A'
                elif percentage >= 80:
                    grade = 'B'
                elif percentage >= 70:
                    grade = 'C'
                elif percentage >= 60:
                    grade = 'D'
                else:
                    grade = 'F'
                
                stats['grade_distribution'][grade] = stats['grade_distribution'].get(grade, 0) + 1
            
            return {
                'assessment_id': assessment_id,
                'title': assessment.title,
                'max_score': max_score,
                'statistics': stats
            }
            
        except Exception as e:
            logger.error(f"Error getting assessment statistics: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def update_assessment(assessment_id, **update_data):
        """Update an existing assessment"""
        try:
            assessment = Assessment.query.get(assessment_id)
            if not assessment:
                return None, "Assessment not found"
            
            # Update allowed fields
            allowed_fields = ['title', 'max_score', 'due_date', 'weight', 'description', 'type_id']
            
            for field in allowed_fields:
                if field in update_data:
                    if field == 'due_date' and isinstance(update_data[field], str) and update_data[field]:
                        try:
                            # Try ISO format first (what frontend sends)
                            if 'T' in update_data[field]:
                                update_data[field] = datetime.fromisoformat(update_data[field].replace('Z', '+00:00'))
                            else:
                                # Fallback to simple format
                                update_data[field] = datetime.strptime(update_data[field], '%Y-%m-%d %H:%M')
                        except ValueError as e:
                            logger.error(f"Error parsing due_date '{update_data[field]}': {str(e)}")
                            # If parsing fails, skip updating this field
                            continue
                            
                    setattr(assessment, field, update_data[field])
            
            db.session.commit()
            logger.info(f"Assessment updated: {assessment.title} (ID: {assessment_id})")
            return assessment, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating assessment: {str(e)}")
            return None, str(e)
        
    @staticmethod
    def get_assessment_details(assessment_id):
        """Get detailed assessment information for editing"""
        try:
            assessment = db.session.query(
                Assessment.assessment_id,
                Assessment.offering_id,
                Assessment.type_id,
                Assessment.title,
                Assessment.max_score,
                Assessment.due_date,
                Assessment.weight,
                Assessment.description,
                Assessment.is_published,
                CourseOffering.course_id,
                Course.course_code,
                Course.course_name
            ).join(
                CourseOffering, Assessment.offering_id == CourseOffering.offering_id
            ).join(
                Course, CourseOffering.course_id == Course.course_id
            ).filter(
                Assessment.assessment_id == assessment_id
            ).first()
            
            if assessment:
                return {
                    'assessment_id': assessment.assessment_id,
                    'offering_id': assessment.offering_id,
                    'course_id': assessment.course_id,
                    'course_code': assessment.course_code,
                    'course_name': assessment.course_name,
                    'type_id': assessment.type_id,
                    'title': assessment.title,
                    'max_score': float(assessment.max_score),
                    'due_date': assessment.due_date.isoformat() if assessment.due_date else None,
                    'weight': float(assessment.weight) if assessment.weight else None,
                    'description': assessment.description,
                    'is_published': assessment.is_published
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting assessment details: {str(e)}")
            return None
    
    @staticmethod
    def get_assessment_by_id(assessment_id):
        """Get a single assessment by ID"""
        try:
            assessment = db.session.query(
                Assessment.assessment_id,
                Assessment.offering_id,
                Assessment.type_id,
                Assessment.title,
                Assessment.max_score,
                Assessment.due_date,
                Assessment.weight,
                Assessment.description,
                Assessment.is_published,
                Assessment.created_at,
                AssessmentType.type_name,
                AssessmentType.type_id.label('type_id_check')
            ).join(
                AssessmentType, AssessmentType.type_id == Assessment.type_id
            ).filter(
                Assessment.assessment_id == assessment_id
            ).first()
            
            if not assessment:
                return None
            
            return {
                'assessment_id': assessment.assessment_id,
                'offering_id': assessment.offering_id,
                'type_id': assessment.type_id,
                'title': assessment.title,
                'type_name': assessment.type_name,
                'max_score': float(assessment.max_score),
                'due_date': assessment.due_date.isoformat() if assessment.due_date else None,
                'weight': float(assessment.weight) if assessment.weight else None,
                'description': assessment.description,
                'is_published': assessment.is_published,
                'created_at': assessment.created_at.isoformat() if assessment.created_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting assessment: {str(e)}")
            return None
    
    @staticmethod
    def delete_assessment(assessment_id):
        """Delete an assessment (if no submissions exist)"""
        try:
            assessment = Assessment.query.get(assessment_id)
            if not assessment:
                return False, "Assessment not found"
            
            # Check if there are any submissions
            submission_count = AssessmentSubmission.query.filter_by(
                assessment_id=assessment_id
            ).count()
            
            if submission_count > 0:
                return False, "Cannot delete assessment with existing submissions"
            
            db.session.delete(assessment)
            db.session.commit()
            return True, "Assessment deleted successfully"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting assessment: {str(e)}")
            return False, str(e)
        

    @staticmethod
    def get_student_assessment_detail(student_id, assessment_id):
        """Get detailed assessment information for a student"""
        try:
            # Get enrollment for the student
            result = db.session.query(
                Assessment,
                AssessmentType,
                Course,
                CourseOffering,
                Enrollment,
                AssessmentSubmission
            ).join(
                AssessmentType, Assessment.type_id == AssessmentType.type_id
            ).join(
                CourseOffering, Assessment.offering_id == CourseOffering.offering_id
            ).join(
                Course, CourseOffering.course_id == Course.course_id
            ).join(
                Enrollment, Enrollment.offering_id == CourseOffering.offering_id
            ).outerjoin(
                AssessmentSubmission, 
                db.and_(
                    AssessmentSubmission.assessment_id == Assessment.assessment_id,
                    AssessmentSubmission.enrollment_id == Enrollment.enrollment_id
                )
            ).filter(
                Assessment.assessment_id == assessment_id,
                Enrollment.student_id == student_id,
                Assessment.is_published == True,
                Enrollment.enrollment_status == 'enrolled'  # Add this check
            ).first()
            
            if not result:
                logger.warning(f"No assessment found for student {student_id} and assessment {assessment_id}")
                return None
            
            assessment, assessment_type, course, offering, enrollment, submission = result
            
            # Build response with all necessary fields
            data = {
                'assessment_id': assessment.assessment_id,
                'title': assessment.title,
                'description': assessment.description,
                'type_id': assessment.type_id,
                'type_name': assessment_type.type_name,
                'course_id': course.course_id,
                'course_code': course.course_code,
                'course_name': course.course_name,
                'max_score': float(assessment.max_score) if assessment.max_score else 0,
                'due_date': assessment.due_date.isoformat() if assessment.due_date else None,
                'weight': float(assessment.weight) if assessment.weight else None,
                'is_late': datetime.utcnow() > assessment.due_date if assessment.due_date else False,
                'status': 'not_submitted'
            }
            
            # Add submission info if exists
            if submission:
                data.update({
                    'submission_id': submission.submission_id,
                    'submission_date': submission.submission_date.isoformat() if submission.submission_date else None,
                    'submission_text': submission.submission_text,
                    'file_name': submission.file_name,
                    'has_file': bool(submission.file_path),
                    'submission_type': submission.submission_type,
                    'score': float(submission.score) if submission.score is not None else None,
                    'percentage': float(submission.percentage) if submission.percentage is not None else None,
                    'feedback': submission.feedback,
                    'status': 'graded' if submission.score is not None else 'submitted',
                    'is_late': submission.is_late if hasattr(submission, 'is_late') else False
                })
            
            logger.info(f"Returning assessment data: {data}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting assessment detail: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
    @staticmethod
    def create_submission(enrollment_id, assessment_id, submission_text=None, 
                     file_info=None, submission_type='text'):
        """Create or update a student submission"""
        try:
            # Get assessment to check due date
            assessment = Assessment.query.get(assessment_id)
            if not assessment:
                return None, "Assessment not found"
            
            # Check if late
            is_late = False
            if assessment.due_date and datetime.utcnow() > assessment.due_date:
                is_late = True
            
            # Check for existing submission
            existing = AssessmentSubmission.query.filter_by(
                enrollment_id=enrollment_id,
                assessment_id=assessment_id
            ).first()
            
            if existing:
                # Update existing submission
                existing.submission_date = datetime.utcnow()
                existing.submission_text = submission_text
                existing.is_late = is_late
                existing.submission_type = submission_type
                
                # Update file info if provided
                if file_info:
                    existing.file_path = file_info.get('file_path')
                    existing.file_name = file_info.get('file_name')
                    existing.file_size = file_info.get('file_size')
                    existing.mime_type = file_info.get('mime_type')
                
                submission = existing
            else:
                # Create new submission
                submission = AssessmentSubmission(
                    enrollment_id=enrollment_id,
                    assessment_id=assessment_id,
                    submission_date=datetime.utcnow(),
                    submission_text=submission_text,
                    is_late=is_late,
                    submission_type=submission_type
                )
                
                # Add file info if provided
                if file_info:
                    submission.file_path = file_info.get('file_path')
                    submission.file_name = file_info.get('file_name')
                    submission.file_size = file_info.get('file_size')
                    submission.mime_type = file_info.get('mime_type')
                
                db.session.add(submission)
            
            db.session.commit()
            return submission, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating submission: {str(e)}")
            return None, str(e)
        

    @staticmethod
    def get_submission_details(submission_id, faculty_id=None):
        """Get detailed submission information with security check"""
        try:
            # Get submission with related data
            submission = db.session.query(
                AssessmentSubmission.submission_id,
                AssessmentSubmission.submission_date,
                AssessmentSubmission.submission_text,
                AssessmentSubmission.file_path,
                AssessmentSubmission.file_name,
                AssessmentSubmission.file_size,
                AssessmentSubmission.mime_type,
                AssessmentSubmission.score,
                AssessmentSubmission.percentage,
                AssessmentSubmission.feedback,
                AssessmentSubmission.is_late,
                Assessment.assessment_id,
                Assessment.title.label('assessment_title'),
                Assessment.max_score,
                CourseOffering.faculty_id
            ).join(
                Assessment, Assessment.assessment_id == AssessmentSubmission.assessment_id
            ).join(
                CourseOffering, CourseOffering.offering_id == Assessment.offering_id
            ).filter(
                AssessmentSubmission.submission_id == submission_id
            ).first()
            
            if not submission:
                logger.warning(f"Submission {submission_id} not found")
                return None
            
            # Security check: Verify faculty teaches this course
            if faculty_id and submission.faculty_id != faculty_id:
                logger.warning(f"Faculty {faculty_id} attempted to access submission {submission_id} they don't teach")
                return None
            
            # Determine submission type
            has_text = bool(submission.submission_text)
            has_file = bool(submission.file_path)
            
            if has_text and has_file:
                submission_type = 'both'
            elif has_file:
                submission_type = 'file'
            elif has_text:
                submission_type = 'text'
            else:
                submission_type = 'none'
            
            return {
                'submission_id': submission.submission_id,
                'submission_date': submission.submission_date.isoformat() if submission.submission_date else None,
                'submission_text': submission.submission_text,
                'submission_type': submission_type,
                'has_file': has_file,
                'file_name': submission.file_name,
                'file_size': submission.file_size,
                'mime_type': submission.mime_type,
                'score': float(submission.score) if submission.score is not None else None,
                'percentage': float(submission.percentage) if submission.percentage is not None else None,
                'feedback': submission.feedback,
                'is_late': bool(submission.is_late),
                'assessment': {
                    'assessment_id': submission.assessment_id,
                    'title': submission.assessment_title,
                    'max_score': float(submission.max_score)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting submission details: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        
    @staticmethod
    def download_submission_file(submission_id, faculty_id=None):
        """Download submission file with security check"""
        try:
            # Get submission with security check
            submission = db.session.query(
                AssessmentSubmission.file_path,
                AssessmentSubmission.file_name,
                AssessmentSubmission.mime_type,
                CourseOffering.faculty_id
            ).join(
                Assessment, Assessment.assessment_id == AssessmentSubmission.assessment_id
            ).join(
                CourseOffering, CourseOffering.offering_id == Assessment.offering_id
            ).filter(
                AssessmentSubmission.submission_id == submission_id
            ).first()
            
            if not submission:
                logger.warning(f"Submission {submission_id} not found")
                return None
            
            # Security check: Verify faculty teaches this course
            if faculty_id and submission.faculty_id != faculty_id:
                logger.warning(f"Faculty {faculty_id} attempted to download submission {submission_id} they don't teach")
                return None
            
            if not submission.file_path:
                logger.warning(f"No file attached to submission {submission_id}")
                return None
            
            # Construct full file path
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            full_path = os.path.join(upload_folder, submission.file_path)
            
            # Check if file exists
            if not os.path.exists(full_path):
                logger.error(f"File not found on disk: {full_path}")
                return None
            
            # Send file
            return send_file(
                full_path,
                as_attachment=True,
                download_name=submission.file_name,
                mimetype=submission.mime_type
            )
            
        except Exception as e:
            logger.error(f"Error downloading submission file: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


# Create service instance
assessment_service = AssessmentService()