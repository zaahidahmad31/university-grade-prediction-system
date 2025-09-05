from datetime import datetime, timedelta
from sqlalchemy import func
from backend.models import LMSSession, LMSActivity, LMSDailySummary, Enrollment
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

class LMSSummaryService:
    """Service to aggregate daily LMS activity summaries"""
    
    @staticmethod
    def generate_daily_summary(date=None):
        """
        Generate daily summary for all students
        Run this as a scheduled job (e.g., every night at midnight)
        """
        if not date:
            date = datetime.now().date() - timedelta(days=1)  # Yesterday
        
        logger.info(f"Generating LMS daily summary for {date}")
        
        try:
            # Get all enrollments with activity on this date
            enrollments_with_activity = db.session.query(
                LMSSession.enrollment_id
            ).filter(
                func.date(LMSSession.login_time) == date
            ).distinct().all()
            
            for (enrollment_id,) in enrollments_with_activity:
                LMSSummaryService._generate_summary_for_enrollment(enrollment_id, date)
            
            db.session.commit()
            logger.info(f"Generated daily summaries for {len(enrollments_with_activity)} enrollments")
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {str(e)}")
            db.session.rollback()
    
    @staticmethod
    def _generate_summary_for_enrollment(enrollment_id, date):
        """Generate summary for a specific enrollment and date"""
        
        # Get all sessions for this date
        sessions = LMSSession.query.filter(
            LMSSession.enrollment_id == enrollment_id,
            func.date(LMSSession.login_time) == date
        ).all()
        
        if not sessions:
            return
        
        # Calculate metrics
        total_minutes = 0
        login_count = len(sessions)
        
        # Activity counts
        activity_counts = {
            'resource_views': 0,
            'forum_posts': 0,
            'forum_replies': 0,
            'assessment_views': 0,
            'page_views': 0
        }
        
        for session in sessions:
            # Calculate session duration
            if session.logout_time:
                duration = (session.logout_time - session.login_time).seconds / 60
                total_minutes += duration
            
            # Count activities
            activities = LMSActivity.query.filter_by(session_id=session.session_id).all()
            
            for activity in activities:
                if activity.activity_type == 'resource_view':
                    activity_counts['resource_views'] += 1
                elif activity.activity_type == 'forum_post':
                    activity_counts['forum_posts'] += 1
                elif activity.activity_type == 'forum_reply':
                    activity_counts['forum_replies'] += 1
                elif activity.activity_type in ['assessment_view', 'assessment_submit']:
                    activity_counts['assessment_views'] += 1
                else:
                    activity_counts['page_views'] += 1
        
        # Check if summary exists
        summary = LMSDailySummary.query.filter_by(
            enrollment_id=enrollment_id,
            summary_date=date
        ).first()
        
        if summary:
            # Update existing
            summary.total_minutes = int(total_minutes)
            summary.login_count = login_count
            summary.resource_views = activity_counts['resource_views']
            summary.forum_posts = activity_counts['forum_posts']
            summary.forum_replies = activity_counts['forum_replies']
            summary.pages_viewed = activity_counts['page_views']
        else:
            # Create new
            summary = LMSDailySummary(
                enrollment_id=enrollment_id,
                summary_date=date,
                total_minutes=int(total_minutes),
                login_count=login_count,
                resource_views=activity_counts['resource_views'],
                forum_posts=activity_counts['forum_posts'],
                forum_replies=activity_counts['forum_replies'],
                pages_viewed=activity_counts['page_views']
            )
            db.session.add(summary)