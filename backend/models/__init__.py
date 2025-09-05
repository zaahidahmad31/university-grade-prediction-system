# Python package initialization
"""
Models package for the university grade prediction system.
All SQLAlchemy models are imported here for easy access.
"""

# Import all models to make them available
from .user import User, Student, Faculty
from .academic import AcademicTerm, Course, CourseOffering, Enrollment
from .tracking import Attendance, LMSSession, LMSActivity, LMSDailySummary
from .assessment import AssessmentType, Assessment, AssessmentSubmission
from .prediction import Prediction, FeatureCache,MLFeatureStaging
from .alert import AlertType, Alert, Intervention
from .system import SystemConfig, AuditLog, ModelVersion

# This is done for easier importing of models in other modules
__all__ = [
    'User', 'Student', 'Faculty',
    'AcademicTerm', 'Course', 'CourseOffering', 'Enrollment',
    'Attendance', 'LMSSession', 'LMSActivity', 'LMSDailySummary',
    'AssessmentType', 'Assessment', 'AssessmentSubmission',
    'Prediction', 'FeatureCache',
    'AlertType', 'Alert', 'Intervention',
    'SystemConfig', 'AuditLog', 'ModelVersion','MLFeatureStaging'
]