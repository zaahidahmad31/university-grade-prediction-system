from datetime import datetime
from backend.models import LMSSession, LMSActivity, Enrollment
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

class LMSActivityService:
    
    @staticmethod
    def track_page_view(enrollment_id, page_url, page_title=None, ip_address=None, user_agent=None):
        """Track a page view"""
        try:
            # Get or create session
            session = LMSActivityService._get_or_create_session(enrollment_id, ip_address, user_agent)
            
            # Create activity
            activity = LMSActivity(
                session_id=session.session_id,
                enrollment_id=enrollment_id,
                activity_type='page_view',
                activity_timestamp=datetime.utcnow(),
                resource_id=page_url,
                resource_name=page_title or page_url
            )
            
            db.session.add(activity)
            db.session.commit()
            
            return activity
            
        except Exception as e:
            logger.error(f"Error tracking page view: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def track_resource_view(enrollment_id, resource_id, resource_name, resource_type='document', 
                           ip_address=None, user_agent=None):
        """Track viewing of a resource"""
        try:
            session = LMSActivityService._get_or_create_session(enrollment_id, ip_address, user_agent)
            
            activity = LMSActivity(
                session_id=session.session_id,
                enrollment_id=enrollment_id,
                activity_type='resource_view',
                activity_timestamp=datetime.utcnow(),
                resource_id=str(resource_id),
                resource_name=resource_name,
                details={'resource_type': resource_type}
            )
            
            db.session.add(activity)
            db.session.commit()
            
            return activity
            
        except Exception as e:
            logger.error(f"Error tracking resource view: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def track_assessment_view(enrollment_id, assessment_id, assessment_name, ip_address=None, user_agent=None):
        """Track viewing of an assessment"""
        try:
            session = LMSActivityService._get_or_create_session(enrollment_id, ip_address, user_agent)
            
            activity = LMSActivity(
                session_id=session.session_id,
                enrollment_id=enrollment_id,
                activity_type='assignment_view',
                activity_timestamp=datetime.utcnow(),
                resource_id=f"assessment_{assessment_id}",
                resource_name=assessment_name
            )
            
            db.session.add(activity)
            db.session.commit()
            
            return activity
            
        except Exception as e:
            logger.error(f"Error tracking assessment view: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def _get_or_create_session(enrollment_id, ip_address=None, user_agent=None):
        """Get active session or create new one"""
        # Look for active session (within last hour)
        session = LMSSession.query.filter_by(
            enrollment_id=enrollment_id,
            logout_time=None
        ).order_by(LMSSession.login_time.desc()).first()
        
        if not session or (datetime.utcnow() - session.login_time).seconds > 3600:
            # Create new session
            session = LMSSession(
                enrollment_id=enrollment_id,
                login_time=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent[:255] if user_agent else None
            )
            db.session.add(session)
            db.session.flush()  # Get session_id without committing
        
        return session
    
    @staticmethod
    def end_session(enrollment_id):
        """End active session"""
        try:
            session = LMSSession.query.filter_by(
                enrollment_id=enrollment_id,
                logout_time=None
            ).order_by(LMSSession.login_time.desc()).first()
            
            if session:
                session.logout_time = datetime.utcnow()
                session.duration_minutes = int((session.logout_time - session.login_time).seconds / 60)
                db.session.commit()
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_enrollment_activities(enrollment_id, limit=50):
        """Get recent activities for an enrollment"""
        try:
            activities = LMSActivity.query.filter_by(
                enrollment_id=enrollment_id
            ).order_by(LMSActivity.activity_timestamp.desc()).limit(limit).all()
            
            return [activity.to_dict() for activity in activities]
            
        except Exception as e:
            logger.error(f"Error getting activities: {str(e)}")
            return []

# Create service instance
lms_activity_service = LMSActivityService()