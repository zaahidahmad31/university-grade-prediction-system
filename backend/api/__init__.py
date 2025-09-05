# Python package initialization
# Import blueprints
from backend.api.auth.routes import auth_bp
from backend.api.student.routes import student_bp
from backend.api.faculty.routes import faculty_bp
from backend.api.admin.routes import admin_bp
from backend.api.prediction.routes import prediction_bp
from backend.api.common.routes import common_bp

# Export blueprints
__all__ = [
    'auth_bp',
    'student_bp',
    'faculty_bp',
    'admin_bp',
    'prediction_bp',
    'common_bp'
]