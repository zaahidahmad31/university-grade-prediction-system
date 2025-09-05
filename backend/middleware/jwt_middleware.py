from flask import g
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt_identity
from jwt.exceptions import DecodeError
from backend.models import User
import logging

logger = logging.getLogger(__name__)

def load_logged_in_user():
    """
    Load the logged-in user into g.current_user for each request
    This should be called in app.before_request
    """
    g.current_user = None
    
    try:
        # In Flask-JWT-Extended 4.x, use verify_jwt_in_request with optional=True
        verify_jwt_in_request(optional=True)
        
        # Get user ID from JWT if available
        user_id = get_jwt_identity()
        
        if user_id:
            # Load user and set in g
            user = User.query.get(user_id)
            if user:
                g.current_user = user
                logger.debug(f"Loaded user {user.username} into g.current_user")
                
    except Exception as e:
        # No valid JWT or other error - that's okay for public routes
        logger.debug(f"No JWT found or invalid: {str(e)}")
        pass