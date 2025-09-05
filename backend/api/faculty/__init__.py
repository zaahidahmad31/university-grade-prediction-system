# backend/api/faculty/__init__.py
# Python package initialization
from .routes import faculty_bp
from .attendance_routes import faculty_attendance_bp

# Export both blueprints
__all__ = ['faculty_bp', 'faculty_attendance_bp']