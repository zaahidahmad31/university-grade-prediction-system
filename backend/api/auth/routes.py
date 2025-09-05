from flask import Blueprint, request, jsonify, current_app
from backend.models import User
from backend.services.auth_service import (
    register_user, authenticate_user, 
    create_access_token, create_refresh_token,
    get_user_from_token
)
from backend.utils.api import api_response, error_response
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, 
    create_access_token as flask_create_access_token
)
import logging

logger = logging.getLogger('auth')

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data:
        return error_response('No data provided', 400)
    
    # Extract user data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('user_type', 'student')  # Default to student
    
    # Validate required fields
    if not all([username, email, password]):
        return error_response('Username, email, and password are required', 400)
    
    # Validate user type
    if user_type not in ['student', 'faculty', 'admin']:
        return error_response('Invalid user type', 400)
    
    # Register user
    user, error = register_user(
        username=username,
        email=email,
        password=password,
        user_type=user_type,
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        # Additional fields based on user type
        **{k: v for k, v in data.items() if k not in ['username', 'email', 'password', 'user_type', 'first_name', 'last_name']}
    )
    
    if error:
        return error_response(error, 400)
    
    # Create tokens
    access_token = create_access_token(user.user_id)
    refresh_token = create_refresh_token(user.user_id)
    
    return api_response({
        'message': 'User registered successfully',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.user_id,
            'username': user.username,
            'email': user.email,
            'user_type': user.user_type
        }
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user"""
    data = request.get_json()
    
    if not data:
        return error_response('No data provided', 400)
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return error_response('Username and password are required', 400)
    
    # Authenticate user
    user = authenticate_user(username, password)
    
    if not user:
        logger.warning(f"Failed login attempt for username: {username}")
        return error_response('Invalid username or password', 401)
    
    # Create tokens
    access_token = create_access_token(user.user_id)
    refresh_token = create_refresh_token(user.user_id)
    
    # Get profile data
    profile_data = None
    if user.user_type == 'student' and user.student:
        profile_data = user.student.to_dict()
        logger.info(f"Student logged in: {user.student.student_id}")
    elif user.user_type == 'faculty' and user.faculty:
        profile_data = user.faculty.to_dict()
        logger.info(f"Faculty logged in: {user.faculty.faculty_id}")
    
    logger.info(f"User {username} logged in successfully")
    
    return api_response({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.user_id,
            'username': user.username,
            'email': user.email,
            'user_type': user.user_type
        },
        'profile': profile_data
    }, 'Login successful')

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token"""
    data = request.get_json()
    
    if not data:
        return error_response('No data provided', 400)
    
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return error_response('Refresh token is required', 400)
    
    # Get user from token
    user = get_user_from_token(refresh_token)
    
    if not user:
        return error_response('Invalid or expired refresh token', 401)
    
    # Create new access token
    access_token = create_access_token(user.user_id)
    
    return api_response({
        'access_token': access_token
    }, 'Token refreshed successfully')

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get current user profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return error_response('User not found', 404)
    
    # Get detailed profile based on user type
    profile = None
    
    if user.user_type == 'student' and user.student:
        profile = user.student.to_dict()
    elif user.user_type == 'faculty' and user.faculty:
        profile = user.faculty.to_dict()
    
    return api_response({
        'user': {
            'id': user.user_id,
            'username': user.username,
            'email': user.email,
            'user_type': user.user_type,
            'profile': profile
        }
    }, 'User profile retrieved successfully')

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout a user"""
    # JWT is stateless, so we can't really "logout"
    # In a real app, you would implement token blacklisting
    # For now, we'll just return a success message
    
    return api_response(message='Logged out successfully')