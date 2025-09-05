import logging
from datetime import datetime
from flask import request, g
from backend.models.tracking import LMSSession, LMSActivity
from backend.models import Enrollment
from backend.extensions import db

logger = logging.getLogger(__name__)

class ActivityTracker:
    """Middleware to track user activities in the system"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the activity tracker with the Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        self.excluded_paths = app.config.get('ACTIVITY_TRACKER_EXCLUDED_PATHS', [
            '/api/auth/login',
            '/api/auth/logout', 
            '/api/auth/refresh',
            '/static'
        ])
    
    def before_request(self):
        """Called before each request"""
        # Store request start time
        g.request_start_time = datetime.utcnow()
        
        # Skip tracking for excluded paths
        if self._should_skip_tracking():
            return
        
        # Track session if user is authenticated
        if hasattr(g, 'current_user') and g.current_user:
            self._ensure_session()
    
    def after_request(self, response):
        """Called after each request"""
        # Skip tracking for excluded paths
        if self._should_skip_tracking():
            return response
        
        # Track activity if user is authenticated
        if hasattr(g, 'current_user') and g.current_user and hasattr(g, 'current_session'):
            self._track_activity()
        
        return response
    
    def _should_skip_tracking(self):
        """Check if current path should be excluded from tracking"""
        for path in self.excluded_paths:
            if request.path.startswith(path):
                return True
        return False
    
    def _ensure_session(self):
        """Ensure user has an active session"""
        if not hasattr(g, 'current_session'):
            # Get all active enrollments for the user
            enrollments = self._get_user_enrollments()
            
            if enrollments:
                # For now, we'll use the first enrollment
                # In a real scenario, you might want to determine which course 
                # the activity is related to based on the URL or request data
                enrollment = enrollments[0]
                
                # Look for active session
                session = LMSSession.query.filter_by(
                    enrollment_id=enrollment.enrollment_id,
                    logout_time=None
                ).order_by(LMSSession.login_time.desc()).first()
                
                # Create new session if none exists or last one is too old
                if not session or (datetime.utcnow() - session.login_time).seconds > 3600:
                    session = LMSSession(
                        enrollment_id=enrollment.enrollment_id,
                        login_time=datetime.utcnow(),
                        ip_address=request.remote_addr,
                        user_agent=request.user_agent.string[:255] if request.user_agent else None
                    )
                    db.session.add(session)
                    db.session.commit()
                
                g.current_session = session
                g.current_enrollment_id = enrollment.enrollment_id
    
    def _get_user_enrollments(self):
        """Get active enrollments for current user"""
        if not g.current_user:
            return []
        
        # Check if user is a student
        if hasattr(g.current_user, 'student'):
            enrollments = Enrollment.query.filter_by(
                student_id=g.current_user.student.student_id,
                enrollment_status='enrolled'
            ).all()
            return enrollments
        
        return []
    
    def _track_activity(self):
        """Track the current activity"""
        if not hasattr(g, 'current_session') or not hasattr(g, 'current_enrollment_id'):
            return
        
        # Determine activity type based on request
        activity_type = self._determine_activity_type()
        if not activity_type:
            return
        
        try:
            # Calculate duration
            duration = None
            if hasattr(g, 'request_start_time'):
                duration = int((datetime.utcnow() - g.request_start_time).total_seconds())
            
            # Create activity record with both session_id and enrollment_id
            activity = LMSActivity(
                session_id=g.current_session.session_id,
                enrollment_id=g.current_enrollment_id,  # Now we're passing this required parameter
                activity_type=activity_type,
                activity_timestamp=datetime.utcnow(),
                resource_id=self._get_resource_id(),
                resource_name=self._get_resource_name(),
                duration_seconds=duration
            )
            
            db.session.add(activity)
            db.session.commit()
            
            logger.debug(f"Tracked activity: {activity_type} for enrollment {g.current_enrollment_id}")
            
        except Exception as e:
            logger.error(f"Error tracking activity: {str(e)}")
            db.session.rollback()
    
    def _determine_activity_type(self):
        """Determine activity type based on request"""
        path = request.path.lower()
        
        # Map paths to activity types
        
        if '/api/student/dashboard' in path or '/dashboard' in path:
            return 'page_view'
        elif '/api/student/courses' in path or '/courses' in path:
            return 'resource_view'
        elif '/api/student/assessments' in path or '/assessments' in path:
            return 'assignment_view'
        elif '/quiz' in path:
            return 'quiz_attempt'
        elif '/forum' in path:
            if request.method == 'POST':
                return 'forum_post'
            return 'page_view'
        elif '/video' in path:
            return 'video_watch'
        elif '/download' in path:
            return 'file_download'
        elif '/predictions' in path:
            return 'page_view'
        else:
            # Default to page_view for GET requests
            if request.method == 'GET':
                return 'page_view'
        
        return None
    
    def _get_resource_id(self):
        """Extract resource ID from request"""
        # Try to get ID from various sources
        if 'id' in request.view_args:
            return str(request.view_args['id'])
        elif 'course_id' in request.view_args:
            return str(request.view_args['course_id'])
        elif 'assessment_id' in request.view_args:
            return str(request.view_args['assessment_id'])
        return None
    
    def _get_resource_name(self):
        """Get a descriptive name for the resource"""
        # This is simplified - in production you'd look up actual names
        endpoint = request.endpoint or ''
        return endpoint.replace('_', ' ').title()

def track_activity(activity_type, resource_id=None, resource_name=None, **kwargs):
    """Manual activity tracking function"""
    try:
        if hasattr(g, 'current_session') and hasattr(g, 'current_enrollment_id'):
            activity = LMSActivity(
                session_id=g.current_session.session_id,
                enrollment_id=g.current_enrollment_id,
                activity_type=activity_type,
                activity_timestamp=datetime.utcnow(),
                resource_id=resource_id,
                resource_name=resource_name,
                **kwargs
            )
            db.session.add(activity)
            db.session.commit()
            logger.debug(f"Manually tracked activity: {activity_type}")
    except Exception as e:
        logger.error(f"Error in manual activity tracking: {str(e)}")
        db.session.rollback()

