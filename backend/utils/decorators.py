from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role', 'student')
            
            if user_role not in allowed_roles:
                return jsonify({'msg': 'Access forbidden: insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def student_required(f):
    """Decorator to ensure user is a student"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        user_role = claims.get('role', 'student')
        
        if user_role != 'student':
            return jsonify({'msg': 'Student access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function