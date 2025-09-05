import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.extensions import db

app = create_app('development')

def add_profile_fields():
    """Add profile fields to students table"""
    with app.app_context():
        try:
            # Add profile_photo column
            db.session.execute("""
                ALTER TABLE students 
                ADD COLUMN profile_photo VARCHAR(255) NULL
            """)
            print("✓ Added profile_photo column")
        except Exception as e:
            print(f"profile_photo column might already exist: {e}")
        
        try:
            # Add phone_number column
            db.session.execute("""
                ALTER TABLE students 
                ADD COLUMN phone_number VARCHAR(20) NULL
            """)
            print("✓ Added phone_number column")
        except Exception as e:
            print(f"phone_number column might already exist: {e}")
        
        try:
            # Add address column
            db.session.execute("""
                ALTER TABLE students 
                ADD COLUMN address TEXT NULL
            """)
            print("✓ Added address column")
        except Exception as e:
            print(f"address column might already exist: {e}")
        
        try:
            db.session.commit()
            print("\n✅ All profile fields added successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing changes: {e}")

if __name__ == '__main__':
    add_profile_fields()