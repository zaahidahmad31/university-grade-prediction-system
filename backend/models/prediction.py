from datetime import datetime
from backend.extensions import db

class Prediction(db.Model):
    """Prediction model for grade predictions"""
    __tablename__ = 'predictions'
    
    prediction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.enrollment_id'), nullable=False)
    prediction_date = db.Column(db.DateTime, nullable=False)
    predicted_grade = db.Column(db.String(2), nullable=False)
    confidence_score = db.Column(db.Numeric(3, 2), nullable=False)
    risk_level = db.Column(db.Enum('low', 'medium', 'high'), nullable=False)
    model_version = db.Column(db.String(20), nullable=False)
    feature_snapshot = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    model_accuracy = db.Column(db.Numeric(5, 2), nullable=True)
    feature_version = db.Column(db.String(20), default='v1.0')
    
    def __init__(self, enrollment_id, prediction_date, predicted_grade, confidence_score, risk_level, model_version, feature_snapshot=None):
        self.enrollment_id = enrollment_id
        self.prediction_date = prediction_date
        self.predicted_grade = predicted_grade
        self.confidence_score = confidence_score
        self.risk_level = risk_level
        self.model_version = model_version
        self.feature_snapshot = feature_snapshot

        self.model_accuracy = None
        self.feature_version = 'v1.0'
    
    def to_dict(self):
        """Convert prediction to dictionary for API responses"""
        return {
            'prediction_id': self.prediction_id,
            'enrollment_id': self.enrollment_id,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'predicted_grade': self.predicted_grade,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'risk_level': self.risk_level,
            'model_version': self.model_version,
            'feature_snapshot': self.feature_snapshot,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'model_accuracy': float(self.model_accuracy) if self.model_accuracy else None,
            'feature_version': self.feature_version
        }
    
    def __repr__(self):
        return f"<Prediction {self.prediction_id} for {self.enrollment_id}: {self.predicted_grade}>"


class FeatureCache(db.Model):
    """Feature cache for performance optimization"""
    __tablename__ = 'feature_cache'
    
    cache_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.enrollment_id'), nullable=False)
    feature_date = db.Column(db.Date, nullable=False)
    attendance_rate = db.Column(db.Numeric(5, 2), nullable=True)
    avg_session_duration = db.Column(db.Numeric(8, 2), nullable=True)
    login_frequency = db.Column(db.Numeric(8, 2), nullable=True)
    resource_access_rate = db.Column(db.Numeric(5, 2), nullable=True)
    assignment_submission_rate = db.Column(db.Numeric(5, 2), nullable=True)
    avg_assignment_score = db.Column(db.Numeric(5, 2), nullable=True)
    forum_engagement_score = db.Column(db.Numeric(8, 2), nullable=True)
    study_consistency_score = db.Column(db.Numeric(5, 2), nullable=True)
    last_login_days_ago = db.Column(db.Integer, nullable=True)
    total_study_minutes = db.Column(db.Integer, nullable=True)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('enrollment_id', 'feature_date', name='unique_cache'),
    )
    
    def __init__(self, enrollment_id, feature_date, **kwargs):
        self.enrollment_id = enrollment_id
        self.feature_date = feature_date
        
        # Feature values
        self.attendance_rate = kwargs.get('attendance_rate')
        self.avg_session_duration = kwargs.get('avg_session_duration')
        self.login_frequency = kwargs.get('login_frequency')
        self.resource_access_rate = kwargs.get('resource_access_rate')
        self.assignment_submission_rate = kwargs.get('assignment_submission_rate')
        self.avg_assignment_score = kwargs.get('avg_assignment_score')
        self.forum_engagement_score = kwargs.get('forum_engagement_score')
        self.study_consistency_score = kwargs.get('study_consistency_score')
        self.last_login_days_ago = kwargs.get('last_login_days_ago')
        self.total_study_minutes = kwargs.get('total_study_minutes')
    
    def to_dict(self):
        """Convert feature cache to dictionary for API responses"""
        return {
            'cache_id': self.cache_id,
            'enrollment_id': self.enrollment_id,
            'feature_date': self.feature_date.isoformat() if self.feature_date else None,
            'attendance_rate': float(self.attendance_rate) if self.attendance_rate else None,
            'avg_session_duration': float(self.avg_session_duration) if self.avg_session_duration else None,
            'login_frequency': float(self.login_frequency) if self.login_frequency else None,
            'resource_access_rate': float(self.resource_access_rate) if self.resource_access_rate else None,
            'assignment_submission_rate': float(self.assignment_submission_rate) if self.assignment_submission_rate else None,
            'avg_assignment_score': float(self.avg_assignment_score) if self.avg_assignment_score else None,
            'forum_engagement_score': float(self.forum_engagement_score) if self.forum_engagement_score else None,
            'study_consistency_score': float(self.study_consistency_score) if self.study_consistency_score else None,
            'last_login_days_ago': self.last_login_days_ago,
            'total_study_minutes': self.total_study_minutes,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }
    
    def __repr__(self):
        return f"<FeatureCache {self.cache_id} for {self.enrollment_id} on {self.feature_date}>"
    
class MLFeatureStaging(db.Model):
    """ML Feature staging table for batch processing"""
    __tablename__ = 'ml_feature_staging'
    
    staging_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.enrollment_id'), nullable=False)
    calculation_date = db.Column(db.Date, nullable=False)
    feature_data = db.Column(db.JSON, nullable=False)
    is_processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, enrollment_id, calculation_date, feature_data):
        self.enrollment_id = enrollment_id
        self.calculation_date = calculation_date
        self.feature_data = feature_data
    
    def mark_processed(self):
        """Mark this staging record as processed"""
        self.is_processed = True
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'staging_id': self.staging_id,
            'enrollment_id': self.enrollment_id,
            'calculation_date': self.calculation_date.isoformat() if self.calculation_date else None,
            'feature_data': self.feature_data,
            'is_processed': self.is_processed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<MLFeatureStaging {self.staging_id} for enrollment {self.enrollment_id}>"