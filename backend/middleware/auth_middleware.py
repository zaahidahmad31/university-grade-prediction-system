from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from backend.models import User
import logging

logger = logging.getLogger('auth')

def role_required(role):
    """Decorator to check user role"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Verify JWT is valid
            verify_jwt_in_request()
            
            # Get identity from JWT
            user_id = get_jwt_identity()
            
            # Get user from database
            user = User.query.get(user_id)
            
            # Check if user exists and has required role
            if not user or user.user_type != role:
                logger.warning(f"Role access denied: User {user_id} tried to access {role} resource")
                return jsonify({
                    'status': 'error',
                    'message': 'You do not have permission to access this resource'
                }), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# Specific role decorators
admin_required = role_required('admin')
faculty_required = role_required('faculty')
student_required = role_required('student')

def get_current_user():
    """Get current user from JWT identity"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def auth_required(fn):
    """Decorator to check if user is authenticated"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Verify JWT
        verify_jwt_in_request()
        
        # Get user ID from JWT
        user_id = get_jwt_identity()
        
        # Get user
        user = User.query.get(user_id)
        
        # Check if user exists
        if not user:
            logger.warning(f"Access denied: User {user_id} not found")
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        return fn(*args, **kwargs)
    
    return wrapper

def admin_required(fn):
    """Decorator to require admin role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        # Get user from database
        user = User.query.filter_by(user_id=current_user_id).first()
        
        if not user or user.user_type != 'admin':
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        return fn(*args, **kwargs)
    
    return wrapper