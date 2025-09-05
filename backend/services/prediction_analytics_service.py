from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import and_, or_, func, desc
from backend.extensions import db
from backend.models import (
    Prediction, ModelVersion, Enrollment, Student, Faculty,
    CourseOffering, Course, User, Assessment, AssessmentSubmission,
    Attendance, LMSDailySummary, FeatureCache
)
import logging
import json

logger = logging.getLogger(__name__)

class PredictionAnalyticsService:
    """Service for prediction analytics and reporting (Admin panel)"""
    
    def get_prediction_summary(self, faculty_id: int = None) -> Dict:
        """Get summary statistics for predictions"""
        try:
            # Base query
            query = db.session.query(Prediction)
            
            if faculty_id:
                # Filter by faculty's courses
                query = query.join(Enrollment)\
                    .join(CourseOffering)\
                    .filter(CourseOffering.faculty_id == faculty_id)
            
            # Get total predictions
            total_predictions = query.count()
            
            # Get predictions by risk level
            risk_distribution = {}
            risk_counts = query.with_entities(
                Prediction.risk_level,
                func.count(Prediction.prediction_id)
            ).group_by(Prediction.risk_level).all()
            
            for risk, count in risk_counts:
                risk_distribution[risk] = count
            
            # Get recent predictions (last 7 days)
            recent_predictions = query.filter(
                Prediction.prediction_date >= datetime.now() - timedelta(days=7)
            ).count()
            
            # Get accuracy metrics
            # Get predictions with high confidence (>= 0.7)
            accurate_predictions = query.filter(
                Prediction.confidence_score >= 0.7
            ).count()
            
            accuracy_rate = (accurate_predictions / total_predictions * 100) if total_predictions > 0 else 0
            
            # Get predictions by grade
            grade_distribution = {}
            grade_counts = query.with_entities(
                Prediction.predicted_grade,
                func.count(Prediction.prediction_id)
            ).group_by(Prediction.predicted_grade).all()
            
            for grade, count in grade_counts:
                grade_distribution[grade] = count
            
            # Get model performance stats
            model_stats = self._get_model_performance_stats()
            
            return {
                'total_predictions': total_predictions,
                'recent_predictions': recent_predictions,
                'risk_distribution': risk_distribution,
                'grade_distribution': grade_distribution,
                'accuracy_rate': accuracy_rate,
                'high_risk_count': risk_distribution.get('high', 0),
                'medium_risk_count': risk_distribution.get('medium', 0),
                'low_risk_count': risk_distribution.get('low', 0),
                'model_stats': model_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting prediction summary: {str(e)}")
            return {
                'total_predictions': 0,
                'recent_predictions': 0,
                'risk_distribution': {},
                'grade_distribution': {},
                'accuracy_rate': 0,
                'high_risk_count': 0,
                'medium_risk_count': 0,
                'low_risk_count': 0,
                'model_stats': {}
            }
    
    def get_predictions_list(self, page: int = 1, per_page: int = 10, 
                            filters: Dict = None) -> Dict:
        """Get paginated predictions list with filters"""
        try:
            # Build query with joins
            query = db.session.query(
                Prediction, Enrollment, Student, User, CourseOffering, Course
            ).join(
                Enrollment, Prediction.enrollment_id == Enrollment.enrollment_id
            ).join(
                Student, Enrollment.student_id == Student.student_id
            ).join(
                User, Student.user_id == User.user_id
            ).join(
                CourseOffering, Enrollment.offering_id == CourseOffering.offering_id
            ).join(
                Course, CourseOffering.course_id == Course.course_id
            )
            
            # Apply filters
            if filters:
                if filters.get('risk_level'):
                    query = query.filter(Prediction.risk_level == filters['risk_level'])
                
                if filters.get('course_id'):
                    query = query.filter(Course.course_id == filters['course_id'])
                
                if filters.get('grade'):
                    query = query.filter(Prediction.predicted_grade == filters['grade'])
                
                if filters.get('date_from'):
                    query = query.filter(Prediction.prediction_date >= filters['date_from'])
                
                if filters.get('date_to'):
                    query = query.filter(Prediction.prediction_date <= filters['date_to'])
                
                if filters.get('search'):
                    search_term = f"%{filters['search']}%"
                    query = query.filter(or_(
                        Student.student_id.ilike(search_term),
                        Student.first_name.ilike(search_term),
                        Student.last_name.ilike(search_term)
                    ))
            
            # Order by date (newest first)
            query = query.order_by(desc(Prediction.prediction_date))
            
            # Paginate
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            # Format results
            predictions = []
            for pred, enrollment, student, user, offering, course in pagination.items:
                # Get current grade from feature cache if available
                current_grade = self._get_current_grade(enrollment.enrollment_id)
                
                predictions.append({
                    'prediction_id': pred.prediction_id,
                    'student': {
                        'student_id': student.student_id,
                        'name': f"{student.first_name} {student.last_name}",
                        'email': user.email
                    },
                    'course': {
                        'course_id': course.course_id,
                        'course_code': course.course_code,
                        'course_name': course.course_name
                    },
                    'predicted_grade': pred.predicted_grade,
                    'current_grade': current_grade,
                    'risk_level': pred.risk_level,
                    'confidence_score': float(pred.confidence_score),
                    'prediction_date': pred.prediction_date.isoformat(),
                    'model_version': pred.model_version,
                    'factors': self._get_factors_from_snapshot(pred),
                    'recommendations': self._generate_recommendations(pred, enrollment.enrollment_id)
                })
            
            return {
                'predictions': predictions,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page
            }
            
        except Exception as e:
            logger.error(f"Error getting predictions list: {str(e)}")
            return {
                'predictions': [],
                'total': 0,
                'pages': 0,
                'current_page': page,
                'per_page': per_page
            }
    
    def get_prediction_details(self, prediction_id: int) -> Optional[Dict]:
        """Get detailed prediction information"""
        try:
            # Get prediction with all related data
            result = db.session.query(
                Prediction, Enrollment, Student, User, CourseOffering, Course
            ).join(
                Enrollment, Prediction.enrollment_id == Enrollment.enrollment_id
            ).join(
                Student, Enrollment.student_id == Student.student_id
            ).join(
                User, Student.user_id == User.user_id
            ).join(
                CourseOffering, Enrollment.offering_id == CourseOffering.offering_id
            ).join(
                Course, CourseOffering.course_id == Course.course_id
            ).filter(
                Prediction.prediction_id == prediction_id
            ).first()
            
            if not result:
                return None
            
            pred, enrollment, student, user, offering, course = result
            
            # Get student's performance data
            performance_data = self._get_student_performance(enrollment.enrollment_id)
            
            # Get historical predictions
            historical = self._get_historical_predictions(enrollment.enrollment_id)
            
            # Get feature details from cache
            feature_details = self._get_feature_details(enrollment.enrollment_id)
            
            return {
                'prediction': {
                    'prediction_id': pred.prediction_id,
                    'predicted_grade': pred.predicted_grade,
                    'current_grade': self._get_current_grade(enrollment.enrollment_id),
                    'risk_level': pred.risk_level,
                    'confidence_score': float(pred.confidence_score),
                    'prediction_date': pred.prediction_date.isoformat(),
                    'model_version': pred.model_version,
                    'model_accuracy': float(pred.model_accuracy) if pred.model_accuracy else None,
                    'factors': self._get_factors_from_snapshot(pred),
                    'recommendations': self._generate_recommendations(pred, enrollment.enrollment_id)
                },
                'student': {
                    'student_id': student.student_id,
                    'name': f"{student.first_name} {student.last_name}",
                    'email': user.email,
                    'program': getattr(student, 'program_code', 'N/A'),
                    'year': getattr(student, 'year_of_study', 'N/A')
                },
                'course': {
                    'course_code': course.course_code,
                    'course_name': course.course_name,
                    'section': offering.section_number,
                    'term': offering.term.term_name if offering.term else 'N/A',
                    'faculty': f"{offering.faculty.first_name} {offering.faculty.last_name}" if offering.faculty else 'N/A'
                },
                'performance': performance_data,
                'features': feature_details,
                'historical_predictions': historical
            }
            
        except Exception as e:
            logger.error(f"Error getting prediction details: {str(e)}")
            return None
    
    def get_course_predictions(self, course_id: int) -> Dict:
        """Get prediction analytics for a specific course"""
        try:
            # Get all predictions for the course
            query = db.session.query(Prediction).join(
                Enrollment
            ).join(
                CourseOffering
            ).filter(
                CourseOffering.course_id == course_id
            )
            
            total = query.count()
            
            # Risk distribution
            risk_dist = {}
            risk_counts = query.with_entities(
                Prediction.risk_level,
                func.count(Prediction.prediction_id)
            ).group_by(Prediction.risk_level).all()
            
            for risk, count in risk_counts:
                risk_dist[risk] = {
                    'count': count,
                    'percentage': (count / total * 100) if total > 0 else 0
                }
            
            # Grade distribution
            grade_dist = {}
            grade_counts = query.with_entities(
                Prediction.predicted_grade,
                func.count(Prediction.prediction_id)
            ).group_by(Prediction.predicted_grade).all()
            
            for grade, count in grade_counts:
                grade_dist[grade] = {
                    'count': count,
                    'percentage': (count / total * 100) if total > 0 else 0
                }
            
            # Average confidence
            avg_confidence = query.with_entities(
                func.avg(Prediction.confidence_score)
            ).scalar() or 0
            
            return {
                'total_predictions': total,
                'risk_distribution': risk_dist,
                'grade_distribution': grade_dist,
                'average_confidence': float(avg_confidence),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting course predictions: {str(e)}")
            return {
                'total_predictions': 0,
                'risk_distribution': {},
                'grade_distribution': {},
                'average_confidence': 0,
                'last_updated': datetime.now().isoformat()
            }
    
    def get_model_performance(self) -> Dict:
        """Get performance metrics for prediction models"""
        try:
            # Get latest active model
            latest_model = ModelVersion.query.filter_by(
                is_active=True
            ).order_by(
                desc(ModelVersion.created_at)
            ).first()
            
            if not latest_model:
                return {
                    'model_version': 'N/A',
                    'model_name': 'N/A',
                    'accuracy': 0,
                    'precision': 0,
                    'recall': 0,
                    'f1_score': 0,
                    'total_predictions': 0,
                    'last_trained': None
                }
            
            # Get prediction count for this model
            total_predictions = Prediction.query.filter(
                Prediction.model_version == latest_model.version
            ).count()
            
            return {
                'model_version': latest_model.version,
                'model_name': latest_model.model_type,
                'accuracy': float(latest_model.accuracy) * 100 if latest_model.accuracy else 0,
                'precision': float(latest_model.precision) * 100 if latest_model.precision else 0,
                'recall': float(latest_model.recall) * 100 if latest_model.recall else 0,
                'f1_score': float(latest_model.f1_score) * 100 if latest_model.f1_score else 0,
                'total_predictions': total_predictions,
                'last_trained': latest_model.created_at.isoformat() if latest_model.created_at else None,
                'metrics': {
                    'feature_importance': latest_model.feature_importance,
                    'training_samples': latest_model.training_samples,
                    'validation_samples': latest_model.validation_samples
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting model performance: {str(e)}")
            return {
                'model_version': 'N/A',
                'accuracy': 0,
                'precision': 0,
                'recall': 0,
                'f1_score': 0,
                'total_predictions': 0,
                'last_trained': None
            }
    
    def _get_student_performance(self, enrollment_id: int) -> Dict:
        """Get student's current performance metrics from feature cache"""
        try:
            # Get latest feature cache entry
            cache = FeatureCache.query.filter_by(
                enrollment_id=enrollment_id
            ).order_by(
                desc(FeatureCache.feature_date)
            ).first()
            
            if cache:
                return {
                    'attendance_rate': float(cache.attendance_rate) if cache.attendance_rate else 0,
                    'assessment_average': float(cache.avg_assignment_score) if cache.avg_assignment_score else 0,
                    'lms_engagement': self._calculate_engagement_score(cache),
                    'submission_rate': float(cache.assignment_submission_rate) if cache.assignment_submission_rate else 0
                }
            
            # Fallback to calculating directly
            return self._calculate_performance_metrics(enrollment_id)
            
        except Exception as e:
            logger.error(f"Error getting student performance: {str(e)}")
            return {
                'attendance_rate': 0,
                'assessment_average': 0,
                'lms_engagement': 0,
                'submission_rate': 0
            }
    
    def _calculate_engagement_score(self, cache: FeatureCache) -> float:
        """Calculate LMS engagement score from cache data"""
        try:
            factors = [
                cache.login_frequency or 0,
                cache.resource_access_rate or 0,
                cache.forum_engagement_score or 0,
                cache.study_consistency_score or 0
            ]
            
            # Average of available factors, normalized to 0-100
            return sum(factors) / len([f for f in factors if f > 0]) if any(factors) else 0
            
        except:
            return 0
    
    def _calculate_performance_metrics(self, enrollment_id: int) -> Dict:
        """Calculate performance metrics directly from data"""
        # This is a fallback when cache is not available
        # Implementation would depend on your specific data structure
        return {
            'attendance_rate': 0,
            'assessment_average': 0,
            'lms_engagement': 0,
            'submission_rate': 0
        }
    
    def _get_current_grade(self, enrollment_id: int) -> str:
        """Get current grade calculation"""
        try:
            # Get average of graded assessments
            avg_score = db.session.query(
                func.avg(AssessmentSubmission.score)
            ).join(
                Assessment
            ).filter(
                AssessmentSubmission.enrollment_id == enrollment_id,
                AssessmentSubmission.is_graded == True
            ).scalar()
            
            if avg_score:
                # Convert to letter grade
                score = float(avg_score)
                if score >= 90:
                    return 'A'
                elif score >= 80:
                    return 'B'
                elif score >= 70:
                    return 'C'
                elif score >= 60:
                    return 'D'
                else:
                    return 'F'
            
            return '-'
            
        except:
            return '-'
    
    def _get_historical_predictions(self, enrollment_id: int, limit: int = 10) -> List[Dict]:
        """Get historical predictions for an enrollment"""
        try:
            predictions = Prediction.query.filter_by(
                enrollment_id=enrollment_id
            ).order_by(
                desc(Prediction.prediction_date)
            ).limit(limit).all()
            
            return [
                {
                    'date': p.prediction_date.isoformat(),
                    'grade': p.predicted_grade,
                    'risk_level': p.risk_level,
                    'confidence': float(p.confidence_score)
                }
                for p in predictions
            ]
            
        except:
            return []
    
    def _get_feature_details(self, enrollment_id: int) -> Dict:
        """Get detailed feature information from cache"""
        try:
            cache = FeatureCache.query.filter_by(
                enrollment_id=enrollment_id
            ).order_by(
                desc(FeatureCache.feature_date)
            ).first()
            
            if cache:
                return {
                    'attendance_rate': float(cache.attendance_rate) if cache.attendance_rate else 0,
                    'avg_session_duration': float(cache.avg_session_duration) if cache.avg_session_duration else 0,
                    'login_frequency': float(cache.login_frequency) if cache.login_frequency else 0,
                    'resource_access_rate': float(cache.resource_access_rate) if cache.resource_access_rate else 0,
                    'assignment_submission_rate': float(cache.assignment_submission_rate) if cache.assignment_submission_rate else 0,
                    'avg_assignment_score': float(cache.avg_assignment_score) if cache.avg_assignment_score else 0,
                    'forum_engagement_score': float(cache.forum_engagement_score) if cache.forum_engagement_score else 0,
                    'study_consistency_score': float(cache.study_consistency_score) if cache.study_consistency_score else 0,
                    'last_login_days_ago': int(cache.last_login_days_ago) if cache.last_login_days_ago else 0,
                    'total_study_minutes': int(cache.total_study_minutes) if cache.total_study_minutes else 0,
                    'feature_date': cache.feature_date.isoformat() if cache.feature_date else None
                }
            
            return {}
            
        except:
            return {}
    
    def _get_factors_from_snapshot(self, prediction: Prediction) -> Dict:
        """Extract factors from prediction snapshot"""
        try:
            if prediction.feature_snapshot:
                # Parse JSON if it's a string
                if isinstance(prediction.feature_snapshot, str):
                    return json.loads(prediction.feature_snapshot)
                return prediction.feature_snapshot
            return {}
        except:
            return {}
    
    def _generate_recommendations(self, prediction: Prediction, enrollment_id: int) -> List[str]:
        """Generate recommendations based on prediction and features"""
        recommendations = []
        
        try:
            # Get feature cache
            cache = FeatureCache.query.filter_by(
                enrollment_id=enrollment_id
            ).order_by(
                desc(FeatureCache.feature_date)
            ).first()
            
            if not cache:
                return ["Unable to generate specific recommendations due to missing data"]
            
            # Attendance-based recommendations
            if cache.attendance_rate and cache.attendance_rate < 70:
                recommendations.append("Improve attendance rate - currently below 70%")
            
            # Engagement-based recommendations
            if cache.login_frequency and cache.login_frequency < 3:
                recommendations.append("Increase LMS engagement - log in more frequently")
            
            # Assignment-based recommendations
            if cache.assignment_submission_rate and cache.assignment_submission_rate < 80:
                recommendations.append("Submit all assignments on time")
            
            if cache.avg_assignment_score and cache.avg_assignment_score < 60:
                recommendations.append("Seek help to improve assignment scores")
            
            # Risk-based recommendations
            if prediction.risk_level == 'high':
                recommendations.append("Schedule a meeting with instructor immediately")
                recommendations.append("Consider tutoring or study group participation")
            elif prediction.risk_level == 'medium':
                recommendations.append("Review course materials and seek clarification on difficult topics")
            
            # Study consistency
            if cache.study_consistency_score and cache.study_consistency_score < 50:
                recommendations.append("Establish a regular study schedule")
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Review course progress with instructor"]
    
    def _get_model_performance_stats(self) -> Dict:
        """Get model performance statistics"""
        try:
            latest_model = ModelVersion.query.filter_by(
                is_active=True
            ).first()
            
            if not latest_model:
                return {
                    'accuracy': 0,
                    'precision': 0,
                    'recall': 0,
                    'f1_score': 0
                }
            
            return {
                'accuracy': float(latest_model.accuracy) * 100 if latest_model.accuracy else 0,
                'precision': float(latest_model.precision) * 100 if latest_model.precision else 0,
                'recall': float(latest_model.recall) * 100 if latest_model.recall else 0,
                'f1_score': float(latest_model.f1_score) * 100 if latest_model.f1_score else 0
            }
            
        except:
            return {
                'accuracy': 0,
                'precision': 0,
                'recall': 0,
                'f1_score': 0
            }