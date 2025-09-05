import jwt
from datetime import datetime, timedelta
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models import User, Student, Faculty
from backend.extensions import db
import logging
import uuid

logger = logging.getLogger('auth')

def register_user(username, email, password, user_type, **kwargs):
    """
    Register a new user
    
    Args:
        username: Username
        email: Email address
        password: Password
        user_type: Type of user (student, faculty, admin)
        **kwargs: Additional user details
    
    Returns:
        User object if registration successful, None otherwise
    """
    # Check if username or email already exists
    if User.query.filter_by(username=username).first():
        logger.warning(f"Registration failed: Username {username} already exists")
        return None, "Username already exists"
    
    if User.query.filter_by(email=email).first():
        logger.warning(f"Registration failed: Email {email} already exists")
        return None, "Email already exists"
    
    # Create user
    try:
        user = User(
            username=username,
            email=email,
            password=password,
            user_type=user_type
        )
        db.session.add(user)
        db.session.commit()
        
        # Create profile based on user type
        if user_type == 'student':
            student_id = kwargs.get('student_id', f'STU{str(uuid.uuid4())[:8].upper()}')
            student = Student(
                student_id=student_id,
                user_id=user.user_id,
                first_name=kwargs.get('first_name', ''),
                last_name=kwargs.get('last_name', ''),
                enrollment_date=kwargs.get('enrollment_date', datetime.utcnow().date())
            )
            db.session.add(student)
            db.session.commit()
            
        elif user_type == 'faculty':
            faculty_id = kwargs.get('faculty_id', f'FAC{str(uuid.uuid4())[:8].upper()}')
            faculty = Faculty(
                faculty_id=faculty_id,
                user_id=user.user_id,
                first_name=kwargs.get('first_name', ''),
                last_name=kwargs.get('last_name', ''),
                department=kwargs.get('department', '')
            )
            db.session.add(faculty)
            db.session.commit()
        
        logger.info(f"User {username} registered successfully as {user_type}")
        return user, None
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return None, f"Registration failed: {str(e)}"

def authenticate_user(username, password):
    """
    Authenticate a user by username and password
    
    Args:
        username: Username
        password: Password
    
    Returns:
        User object if authentication successful, None otherwise
    """
    user = User.query.filter_by(username=username).first()
    
    if not user:
        logger.warning(f"Authentication failed: User {username} not found")
        return None
    
    if not user.check_password(password):
        logger.warning(f"Authentication failed: Invalid password for user {username}")
        return None
    
    if not user.is_active:
        logger.warning(f"Authentication failed: User {username} is inactive")
        return None
    
    # Update last login time
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    logger.info(f"User {username} authenticated successfully")
    return user

def create_access_token(user_id, expires_delta=None):
    """
    Create an access token for a user
    
    Args:
        user_id: User ID
        expires_delta: Token expiration time
    
    Returns:
        Access token
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=1)
    
    expires_at = datetime.utcnow() + expires_delta
    
    payload = {
        'sub': str(user_id),
        'exp': expires_at,
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

def create_refresh_token(user_id, expires_delta=None):
    """
    Create a refresh token for a user
    
    Args:
        user_id: User ID
        expires_delta: Token expiration time
    
    Returns:
        Refresh token
    """
    if expires_delta is None:
        expires_delta = timedelta(days=30)
    
    expires_at = datetime.utcnow() + expires_delta
    
    payload = {
        'sub': str(user_id),
        'exp': expires_at,
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

def decode_token(token):
    """
    Decode a token
    
    Args:
        token: JWT token
    
    Returns:
        Decoded token payload
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None

def get_user_from_token(token):
    """
    Get user from token
    
    Args:
        token: JWT token
    
    Returns:
        User object
    """
    payload = decode_token(token)
    
    if not payload:
        return None
    
    user_id = payload.get('sub')
    
    if not user_id:
        return None
    
    return User.query.get(int(user_id))


def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        from backend.models import User
        user = User.query.get(int(user_id))
        return user
    except Exception as e:
        logger.error(f"Error getting user by ID: {str(e)}")
        return None