import bcrypt
import re
from passlib.hash import pbkdf2_sha256

def hash_password(password):
    """Hash a password using pbkdf2_sha256"""
    return pbkdf2_sha256.hash(password)

def verify_password(password, password_hash):
    """Verify a password against a hash"""
    return pbkdf2_sha256.verify(password, password_hash)

def password_strength(password):
    """Check password strength"""
    # Check length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check for uppercase
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password meets strength requirements"