from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy import and_
from backend.extensions import db
from backend.models import (
    Prediction, FeatureCache, Enrollment, Student, 
    CourseOffering, Alert, AlertType, ModelVersion
)
from backend.services.feature_calculator_service import FeatureCalculator
from backend.services.model_service import ModelService
import logging
import numpy as np

logger = logging.getLogger(__name__)

class PredictionService:
    """Service for managing grade predictions"""
    
    def __init__(self):
        self.feature_calculator = FeatureCalculator()
        self.model_service = ModelService()
    
    def generate_prediction(self, enrollment_id: int, 
                          save: bool = True) -> Dict:
        """
        Generate a prediction for a single student enrollment
        
        Args:
            enrollment_id: The enrollment to predict for
            save: Whether to save the prediction to database
            
        Returns:
            Dictionary with prediction details
        """
        try:
            logger.info(f"Generating prediction for enrollment {enrollment_id}")
            
            # Calculate features
            features = self.feature_calculator.calculate_features_for_enrollment(
                enrollment_id
            )
            
            # Make prediction
            predicted_grade, confidence, risk_level = self.model_service.predict(features)
            
            # Get model info
            model_info = self.model_service.get_model_info()
            
            # Create prediction record
            prediction_data = {
                'enrollment_id': enrollment_id,
                'prediction_date': datetime.now(),
                'predicted_grade': predicted_grade,
                'confidence_score': confidence,
                'risk_level': risk_level,
                'model_version': model_info['version'],
                'feature_snapshot': self._create_feature_snapshot(features)
            }
            
            if save:
                # Save to database
                prediction = Prediction(**prediction_data)
                
                # Add model accuracy if available
                model_version = ModelVersion.query.filter_by(is_active=True).first()
                if model_version and model_version.accuracy:
                    prediction.model_accuracy = model_version.accuracy
                
                db.session.add(prediction)
                
                # Check if alert needed
                if risk_level in ['medium', 'high']:
                    self._create_alert(enrollment_id, risk_level, predicted_grade)
                
                # Cache features for performance
                self._cache_features(enrollment_id, features)
                
                db.session.commit()
                prediction_data['prediction_id'] = prediction.prediction_id
            
            # Add explanation
            explanation = self.model_service.explain_prediction(
                features, predicted_grade, confidence
            )
            prediction_data['explanation'] = explanation
            
            logger.info(f"Prediction generated successfully: {predicted_grade} ({confidence:.2f})")
            return prediction_data
            
        except Exception as e:
            logger.error(f"Error generating prediction: {str(e)}")
            db.session.rollback()
            raise
    
    def batch_generate_predictions(self, offering_id: int) -> List[Dict]:
        """
        Generate predictions for all students in a course offering
        
        Args:
            offering_id: The course offering ID
            
        Returns:
            List of prediction results
        """
        try:
            # Get all active enrollments for the offering
            enrollments = Enrollment.query.filter(
                and_(
                    Enrollment.offering_id == offering_id,
                    Enrollment.enrollment_status == 'enrolled'
                )
            ).all()
            
            results = []
            success_count = 0
            
            for enrollment in enrollments:
                try:
                    result = self.generate_prediction(enrollment.enrollment_id)
                    results.append({
                        'enrollment_id': enrollment.enrollment_id,
                        'student_id': enrollment.student_id,
                        'status': 'success',
                        'prediction': result
                    })
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to predict for enrollment {enrollment.enrollment_id}: {str(e)}")
                    results.append({
                        'enrollment_id': enrollment.enrollment_id,
                        'student_id': enrollment.student_id,
                        'status': 'error',
                        'error': str(e)
                    })
            
            logger.info(f"Batch prediction complete: {success_count}/{len(enrollments)} successful")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch prediction: {str(e)}")
            raise
    
    def get_prediction_history(self, enrollment_id: int, 
                             limit: int = 10) -> List[Dict]:
        """
        Get prediction history for an enrollment
        
        Args:
            enrollment_id: The enrollment ID
            limit: Maximum number of predictions to return
            
        Returns:
            List of predictions ordered by date (newest first)
        """
        predictions = Prediction.query.filter_by(
            enrollment_id=enrollment_id
        ).order_by(
            Prediction.prediction_date.desc()
        ).limit(limit).all()
        
        return [p.to_dict() for p in predictions]
    
    def get_latest_prediction(self, enrollment_id: int) -> Optional[Dict]:
        """Get the most recent prediction for an enrollment"""
        prediction = Prediction.query.filter_by(
            enrollment_id=enrollment_id
        ).order_by(
            Prediction.prediction_date.desc()
        ).first()
        
        if prediction:
            return prediction.to_dict()
        return None
    
    def get_at_risk_students(self, offering_id: Optional[int] = None,
                           risk_levels: List[str] = ['high', 'medium']) -> List[Dict]:
        """
        Get students at risk across courses
        
        Args:
            offering_id: Optional course offering filter
            risk_levels: Risk levels to include
            
        Returns:
            List of at-risk students with their latest predictions
        """
        query = db.session.query(
            Prediction, Enrollment, Student
        ).join(
            Enrollment, Prediction.enrollment_id == Enrollment.enrollment_id
        ).join(
            Student, Enrollment.student_id == Student.student_id
        ).filter(
            Prediction.risk_level.in_(risk_levels)
        )
        
        if offering_id:
            query = query.filter(Enrollment.offering_id == offering_id)
        
        # Get only the latest prediction for each enrollment
        subquery = db.session.query(
            Prediction.enrollment_id,
            db.func.max(Prediction.prediction_date).label('max_date')
        ).group_by(Prediction.enrollment_id).subquery()
        
        query = query.join(
            subquery,
            and_(
                Prediction.enrollment_id == subquery.c.enrollment_id,
                Prediction.prediction_date == subquery.c.max_date
            )
        )
        
        results = []
        for prediction, enrollment, student in query.all():
            results.append({
                'student_id': student.student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'enrollment_id': enrollment.enrollment_id,
                'prediction': prediction.to_dict(),
                'course_info': self._get_course_info(enrollment.offering_id)
            })
        
        return results
    
    def compare_predictions(self, enrollment_id: int, 
                          date1: datetime, date2: datetime) -> Dict:
        """
        Compare predictions between two dates
        
        Args:
            enrollment_id: The enrollment ID
            date1: First date
            date2: Second date
            
        Returns:
            Comparison details
        """
        # Get predictions closest to each date
        pred1 = Prediction.query.filter(
            and_(
                Prediction.enrollment_id == enrollment_id,
                Prediction.prediction_date <= date1
            )
        ).order_by(Prediction.prediction_date.desc()).first()
        
        pred2 = Prediction.query.filter(
            and_(
                Prediction.enrollment_id == enrollment_id,
                Prediction.prediction_date <= date2
            )
        ).order_by(Prediction.prediction_date.desc()).first()
        
        if not pred1 or not pred2:
            return {'error': 'Predictions not found for specified dates'}
        
        return {
            'earlier_prediction': pred1.to_dict(),
            'later_prediction': pred2.to_dict(),
            'grade_changed': pred1.predicted_grade != pred2.predicted_grade,
            'confidence_change': float(pred2.confidence_score - pred1.confidence_score),
            'risk_change': self._compare_risk_levels(pred1.risk_level, pred2.risk_level)
        }
    
    def _create_feature_snapshot(self, features: np.ndarray) -> Dict:
        """Create a snapshot of features for storage"""
        feature_names = self.feature_calculator.get_feature_names()
        feature_values = features.flatten().tolist()
        
        return {
            name: float(value) 
            for name, value in zip(feature_names, feature_values)
        }
    
    def _create_alert(self, enrollment_id: int, risk_level: str, 
                     predicted_grade: str):
        """Create an alert for at-risk students"""
        # Get or create alert type
        alert_type = AlertType.query.filter_by(
            type_name='at_risk_prediction'
        ).first()
        
        if not alert_type:
            alert_type = AlertType(
                type_name='at_risk_prediction',
                severity='warning' if risk_level == 'medium' else 'critical',
                description='Student identified as at-risk by prediction model'
            )
            db.session.add(alert_type)
            db.session.flush()
        
        # Create alert
        alert = Alert(
            enrollment_id=enrollment_id,
            type_id=alert_type.type_id,
            triggered_date=datetime.now(),
            alert_message=f"Student predicted to {predicted_grade} with {risk_level} risk level",
            severity=alert_type.severity
        )
        db.session.add(alert)
    
    def _cache_features(self, enrollment_id: int, features: np.ndarray):
        """Cache calculated features for performance"""
        feature_names = self.feature_calculator.get_feature_names()
        feature_values = features.flatten()
        
        # Create feature cache entry
        cache_data = {
            'enrollment_id': enrollment_id,
            'feature_date': datetime.now().date()
        }
        
        # Map specific features to cache columns
        feature_mapping = {
            'attendance_rate': 'attendance_rate',
            'avg_session_duration': 'avg_session_duration',
            'login_frequency': 'login_frequency',
            'resource_access_rate': 'resource_access_rate',
            'assessment_submission_rate': 'assignment_submission_rate',
            'avg_assessment_score': 'avg_assignment_score',
            'forum_engagement_score': 'forum_engagement_score',
            'study_consistency': 'study_consistency_score',
            'days_since_last_login': 'last_login_days_ago',
            'total_online_minutes': 'total_study_minutes'
        }
        
        for feature_name, cache_column in feature_mapping.items():
            if feature_name in feature_names:
                idx = feature_names.index(feature_name)
                cache_data[cache_column] = feature_values[idx]
        
        # Check if cache exists for today
        existing_cache = FeatureCache.query.filter_by(
            enrollment_id=enrollment_id,
            feature_date=cache_data['feature_date']
        ).first()
        
        if existing_cache:
            # Update existing cache
            for key, value in cache_data.items():
                setattr(existing_cache, key, value)
        else:
            # Create new cache entry
            cache = FeatureCache(**cache_data)
            db.session.add(cache)
    
    def _get_course_info(self, offering_id: int) -> Dict:
        """Get course information for an offering"""
        offering = CourseOffering.query.get(offering_id)
        if offering:
            return {
                'course_code': offering.course.course_code,
                'course_name': offering.course.course_name,
                'section': offering.section_number
            }
        return {}
    
    def _compare_risk_levels(self, level1: str, level2: str) -> str:
        """Compare two risk levels and return the change"""
        risk_order = {'low': 0, 'medium': 1, 'high': 2}
        
        val1 = risk_order.get(level1, 0)
        val2 = risk_order.get(level2, 0)
        
        if val2 > val1:
            return 'increased'
        elif val2 < val1:
            return 'decreased'
        else:
            return 'unchanged'
        
    @staticmethod
    def update_feature_cache_for_all_students():
        """
        Update feature cache for all active students
        Run this as a scheduled job (e.g., every night)
        """
        try:
            # Get all active enrollments
            active_enrollments = db.session.query(Enrollment).filter(
                Enrollment.enrollment_status == 'enrolled'
            ).all()
            
            logger.info(f"Updating feature cache for {len(active_enrollments)} enrollments")
            
            feature_calculator = FeatureCalculator()
            
            for enrollment in active_enrollments:
                try:
                    # Calculate features
                    features = feature_calculator.calculate_features_for_enrollment(
                        enrollment.enrollment_id
                    )
                    
                    # Save to cache
                    prediction_service = PredictionService()
                    prediction_service._cache_features(enrollment.enrollment_id, features)
                    
                except Exception as e:
                    logger.error(f"Error caching features for enrollment {enrollment.enrollment_id}: {str(e)}")
            
            db.session.commit()
            logger.info("Feature cache update completed")
            
        except Exception as e:
            logger.error(f"Error updating feature cache: {str(e)}")
            db.session.rollback()