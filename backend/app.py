import os
from flask import Flask
from config import config
from backend.extensions import db, login_manager, jwt, cors, mail, migrate
from backend.utils.cors import configure_cors
from flask_jwt_extended import JWTManager
from flask import send_from_directory
from backend.middleware.activity_tracker import ActivityTracker


def create_app(config_name=None):
    """Create and configure the Flask application"""
    
    # Set default config if not provided
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Set up logging
    from backend.utils.logger import setup_app_logging
    app = setup_app_logging(app)
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Configure CORS properly with our utility
    app = configure_cors(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register shell context
    register_shell_context(app)
    
    # Register commands
    register_commands(app)
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        from flask import send_from_directory
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    app.logger.info(f"Application started in {config_name} mode")
    
    return app


def initialize_extensions(app):
    """Initialize Flask extensions"""
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Initialize activity tracker
    activity_tracker = ActivityTracker(app)
    app.logger.info("Activity tracker initialized")
    
    # Set up JWT user loading for activity tracker
    from backend.middleware.jwt_middleware import load_logged_in_user
    app.before_request(load_logged_in_user)
    app.logger.info("JWT user loading middleware registered")
    
    # Configure login manager
    from backend.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page'
    login_manager.login_message_category = 'info'
    
    # Configure JWT callbacks
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.user_id if hasattr(user, 'user_id') else user
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(user_id=identity).one_or_none()


def register_blueprints(app):
    """Register Flask blueprints"""
    try:
        # Import blueprints INSIDE the function to avoid circular imports
        from backend.api.auth import auth_bp
        from backend.api.student import student_bp
        from backend.api.student.attendance_routes import student_attendance_bp
        from backend.api.faculty import faculty_bp
        from backend.api.faculty.attendance_routes import faculty_attendance_bp
        from backend.api.admin import admin_bp
        from backend.api.prediction import prediction_bp
        from backend.api.common import common_bp
        from backend.api.alert import alert_bp
        from backend.api.student.lms_routes import lms_bp
        
        # Register blueprints with URL prefixes
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(student_bp, url_prefix='/api/student')
        app.register_blueprint(student_attendance_bp)  # already has prefix
        app.register_blueprint(faculty_bp, url_prefix='/api/faculty')
        app.register_blueprint(faculty_attendance_bp)  # already has prefix
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        app.register_blueprint(prediction_bp, url_prefix='/api/prediction')
        app.register_blueprint(common_bp, url_prefix='/api/common')
        app.register_blueprint(alert_bp)
        app.register_blueprint(lms_bp)
        
        app.logger.info("All blueprints registered successfully")
        
    except ImportError as e:
        app.logger.error(f"Error importing blueprints: {str(e)}")
        # Continue anyway to get partial functionality


def register_error_handlers(app):
    """Register error handlers"""
    try:
        from backend.middleware.error_handler import register_error_handlers as register
        register(app)
        app.logger.info("Error handlers registered")
    except ImportError as e:
        app.logger.warning(f"Error handlers not available: {str(e)}")


def register_shell_context(app):
    """Register shell context objects"""
    def shell_context():
        """Shell context objects"""
        # Import models inside the function to avoid circular imports
        try:
            from backend.models import (
                User, Student, Faculty, Course, CourseOffering, 
                Enrollment, Prediction
            )
            return {
                'db': db,
                'User': User,
                'Student': Student,
                'Faculty': Faculty,
                'Course': Course,
                'CourseOffering': CourseOffering,
                'Enrollment': Enrollment,
                'Prediction': Prediction
            }
        except ImportError as e:
            app.logger.warning(f"Some models not available for shell context: {str(e)}")
            return {'db': db}
    
    app.shell_context_processor(shell_context)
    app.logger.info("Shell context registered")

    
def register_commands(app):
    """Register custom commands"""
    try:
        # Import and register commands from separate file
        from backend.commands import register_commands as register_cmds
        register_cmds(app)
        app.logger.info("Commands registered successfully")
    except ImportError as e:
        app.logger.error(f"Error importing commands: {str(e)}")
        # Fallback - register at least a test command
        @app.cli.command()
        def test_commands():
            """Test if commands are working"""
            print("Basic commands are working!")
            print("But main commands file not found: backend/commands.py")