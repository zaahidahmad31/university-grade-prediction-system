import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration"""
    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_timeout': 20,
        'pool_size': 10,
        'max_overflow': 5
    }
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
      # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@university.edu')
    MAIL_ENABLED = os.environ.get('MAIL_ENABLED', 'false').lower() == 'true'
    
    # ML Model
    MODEL_PATH = os.path.join(basedir, 'ml_models')
    
    # Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'txt', 'pdf', 'doc', 'docx',  'zip', 'jpg', 'jpeg', 'png'}
    
    
    # API
    API_TITLE = 'University Grade Prediction System API'
    API_VERSION = '1.0'
    
    # CORS
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000']

class DevelopmentConfig(Config):
    """Development configuration"""
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')
    
    # Shorter token expiry for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    
    # Enable all CORS origins in development
    CORS_ORIGINS = '*'

class TestingConfig(Config):
    """Testing configuration"""
    ENV = 'testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
    # Use faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 4
    
    # No email in testing
    MAIL_SUPPRESS_SEND = True

class ProductionConfig(Config):
    """Production configuration"""
    ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # HTTPS settings
    PREFERRED_URL_SCHEME = 'https'
    
    # Stricter CORS in production
    CORS_ORIGINS = [
        'https://university-grade-prediction.com',
        'https://www.university-grade-prediction.com'
    ]
    
    # Log to file in production
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'false').lower() in ['true', 'on', '1']

# Configure based on environment variable
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}