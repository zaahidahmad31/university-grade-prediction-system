from flask import Blueprint, jsonify, current_app
from backend.extensions import db
from backend.utils.api import api_response
from sqlalchemy import inspect
from sqlalchemy import text

common_bp = Blueprint('common', __name__)

@common_bp.route('/')
def index():
    """API root endpoint"""
    return api_response({
        'name': 'University Grade Prediction System API',
        'version': '1.0',
        'endpoints': {
            'auth': '/api/auth',
            'student': '/api/student',
            'faculty': '/api/faculty',
            'admin': '/api/admin',
            'prediction': '/api/prediction'
        }
    }, 'Welcome to the University Grade Prediction System API')

@common_bp.route('/health')
def health_check():
    """Health check endpoint"""
    # Check database connection
    try:
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        current_app.logger.error(f"Database connection error: {e}")
        db_status = 'disconnected'
    
    return api_response({
        'api': 'ok',
        'database': db_status,
        'environment': current_app.config['ENV']
    }, 'Service is running')

@common_bp.route('/tables')
def list_tables():
    """List all database tables"""
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    return api_response({
        'tables': tables,
        'count': len(tables)
    }, 'Database tables retrieved successfully')