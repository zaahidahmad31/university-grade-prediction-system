from datetime import datetime, timedelta
from backend.services.lms_summary_service import LMSSummaryService
from backend.services.prediction_service import PredictionService
from backend.services.alert_service import AlertService
import logging

logger = logging.getLogger(__name__)

def run_daily_tasks():
    """
    Run all daily tasks
    Schedule this to run every night at midnight
    """
    logger.info("Starting daily tasks...")
    
    try:
        # 1. Generate LMS daily summaries for yesterday
        yesterday = datetime.now().date() - timedelta(days=1)
        LMSSummaryService.generate_daily_summary(yesterday)
        
        # 2. Update feature cache for all students
        PredictionService.update_feature_cache_for_all_students()
        
        # 3. Check and create alerts for all students
        alert_service = AlertService()
        alert_service.check_and_create_alerts()
        logger.info("Alert checking completed")
        
        # 4. Generate predictions for at-risk detection (optional)
        # generate_weekly_predictions()
        
        logger.info("Daily tasks completed successfully")
        
    except Exception as e:
        logger.error(f"Error in daily tasks: {str(e)}")

def run_hourly_tasks():
    """
    Run tasks that need more frequent updates
    Schedule this to run every hour
    """
    logger.info("Starting hourly tasks...")
    
    try:
        # Check alerts for critical conditions
        alert_service = AlertService()
        alert_service.check_and_create_alerts()
        
        logger.info("Hourly tasks completed successfully")
        
    except Exception as e:
        logger.error(f"Error in hourly tasks: {str(e)}")

def generate_weekly_predictions():
    """
    Generate predictions for all active students
    Run this weekly
    """
    from backend.models import Enrollment
    
    active_enrollments = Enrollment.query.filter(
        Enrollment.enrollment_status == 'enrolled'
    ).all()
    
    prediction_service = PredictionService()
    
    for enrollment in active_enrollments:
        try:
            prediction_service.generate_prediction(
                enrollment.enrollment_id,
                save=True
            )
        except Exception as e:
            logger.error(f"Error generating prediction for {enrollment.enrollment_id}: {str(e)}")

def send_weekly_summaries():
    """
    Send weekly performance summaries to students
    Run this every Sunday evening
    """
    from backend.models import Student
    from backend.services.email_service import EmailService
    
    logger.info("Sending weekly summaries...")
    
    try:
        email_service = EmailService()
        students = Student.query.filter_by(is_active=True).all()
        
        for student in students:
            # Get student's weekly data
            # This is simplified - you'd need to implement the data gathering
            summary_data = {
                'courses': [],  # Populate with actual data
                'total_study_time': 0,
                'resources_accessed': 0,
                'assignments_submitted': 0
            }
            
            email_service.send_weekly_summary(
                to_email=student.user.email,
                name=f"{student.first_name} {student.last_name}",
                summary_data=summary_data
            )
        
        logger.info("Weekly summaries sent successfully")
        
    except Exception as e:
        logger.error(f"Error sending weekly summaries: {str(e)}")

# Command to run manually
if __name__ == "__main__":
    run_daily_tasks()