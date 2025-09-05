import os
import threading
import time
import logging
from datetime import datetime, timedelta
from backend.app import create_app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = create_app(os.environ.get('FLASK_CONFIG', 'development'))

def run_background_tasks():
    """Run background tasks in a separate thread"""
    logger.info("Background task thread started")
    
    # Wait a bit for app to fully initialize
    time.sleep(10)
    
    while True:
        try:
            with app.app_context():
                # Import here to avoid circular imports
                from backend.services.lms_summary_service import LMSSummaryService
                from backend.tasks.scheduled_tasks import run_daily_tasks
                
                # Generate daily summary
                logger.info("Running LMS daily summary generation...")
                yesterday = datetime.now().date() - timedelta(days=1)
                LMSSummaryService.generate_daily_summary(yesterday)
                logger.info(f"Generated daily summary for {yesterday}")
                
                # Run other daily tasks
                logger.info("Running other daily tasks...")
                run_daily_tasks()
                logger.info("Daily tasks completed")
                
        except Exception as e:
            logger.error(f"Error in background task: {e}")
            import traceback
            traceback.print_exc()
        
        # Run every 5 minutes for testing (change to 86400 for daily in production)
        logger.info("Background task sleeping for 5 minutes...")
        time.sleep(300)  # 5 minutes for testing

def run_hourly_tasks():
    """Run hourly tasks in a separate thread"""
    logger.info("Hourly task thread started")
    
    # Wait a bit for app to fully initialize
    time.sleep(15)
    
    while True:
        try:
            with app.app_context():
                from backend.services.alert_service import AlertService
                
                logger.info("Running hourly alert checks...")
                alert_service = AlertService()
                alert_service.check_and_create_alerts()
                logger.info("Hourly alert check completed")
                
        except Exception as e:
            logger.error(f"Error in hourly task: {e}")
            import traceback
            traceback.print_exc()
        
        # Run every hour
        time.sleep(3600)  # 1 hour

# Start background threads only in main process
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    # Daily/5-minute tasks thread
    daily_thread = threading.Thread(target=run_background_tasks, daemon=True)
    daily_thread.start()
    logger.info("Daily background tasks thread started")
    
    # Hourly tasks thread
    hourly_thread = threading.Thread(target=run_hourly_tasks, daemon=True)
    hourly_thread.start()
    logger.info("Hourly background tasks thread started")

# For development server
if __name__ == '__main__':
    logger.info("Starting Flask development server with background tasks...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Important: prevents duplicate threads
    )