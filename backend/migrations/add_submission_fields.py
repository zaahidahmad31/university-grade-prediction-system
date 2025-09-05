# Create file: backend/migrations/add_submission_fields.py
from backend.extensions import db

def upgrade():
    """Add submission fields to assessment_submissions table"""
    with db.engine.connect() as conn:
        conn.execute("""
            ALTER TABLE assessment_submissions 
            ADD COLUMN submission_text TEXT,
            ADD COLUMN file_path VARCHAR(500),
            ADD COLUMN file_name VARCHAR(255),
            ADD COLUMN file_size INTEGER,
            ADD COLUMN mime_type VARCHAR(100),
            ADD COLUMN submission_type VARCHAR(50) DEFAULT 'text'
        """)

def downgrade():
    """Remove submission fields"""
    with db.engine.connect() as conn:
        conn.execute("""
            ALTER TABLE assessment_submissions 
            DROP COLUMN submission_text,
            DROP COLUMN file_path,
            DROP COLUMN file_name,
            DROP COLUMN file_size,
            DROP COLUMN mime_type,
            DROP COLUMN submission_type
        """)