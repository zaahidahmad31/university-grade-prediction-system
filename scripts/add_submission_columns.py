import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.extensions import db
from backend.app import create_app
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_submission_columns():
    """Add new submission columns to assessment_submissions table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'assessment_submissions' 
                AND TABLE_SCHEMA = DATABASE()
                AND COLUMN_NAME IN ('submission_text', 'file_path', 'file_name', 
                                   'file_size', 'mime_type', 'submission_type')
            """))
            existing_columns = [row[0] for row in result]
            
            if len(existing_columns) == 6:
                logger.info("All columns already exist. No migration needed.")
                return
            
            # Add missing columns
            logger.info("Adding new columns to assessment_submissions table...")
            
            if 'submission_text' not in existing_columns:
                db.session.execute(text("ALTER TABLE assessment_submissions ADD COLUMN submission_text TEXT"))
                logger.info("Added submission_text column")
            
            if 'file_path' not in existing_columns:
                db.session.execute(text("ALTER TABLE assessment_submissions ADD COLUMN file_path VARCHAR(500)"))
                logger.info("Added file_path column")
            
            if 'file_name' not in existing_columns:
                db.session.execute(text("ALTER TABLE assessment_submissions ADD COLUMN file_name VARCHAR(255)"))
                logger.info("Added file_name column")
            
            if 'file_size' not in existing_columns:
                db.session.execute(text("ALTER TABLE assessment_submissions ADD COLUMN file_size INTEGER"))
                logger.info("Added file_size column")
            
            if 'mime_type' not in existing_columns:
                db.session.execute(text("ALTER TABLE assessment_submissions ADD COLUMN mime_type VARCHAR(100)"))
                logger.info("Added mime_type column")
            
            if 'submission_type' not in existing_columns:
                db.session.execute(text("ALTER TABLE assessment_submissions ADD COLUMN submission_type VARCHAR(50) DEFAULT 'text'"))
                logger.info("Added submission_type column")
            
            db.session.commit()
            logger.info("Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    add_submission_columns()