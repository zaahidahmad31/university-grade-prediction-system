import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.extensions import db
from sqlalchemy import text

app = create_app('development')

def add_profile_columns():
    """Add profile columns to students table"""
    with app.app_context():
        print("Adding profile columns to students table...")
        
        # Check current columns first
        try:
            result = db.session.execute(text("SHOW COLUMNS FROM students"))
            existing_columns = [row[0] for row in result]
            print(f"Existing columns: {existing_columns}")
        except Exception as e:
            print(f"Error checking columns: {e}")
            return
        
        # Add each column if it doesn't exist
        columns_to_add = [
            ("profile_photo", "VARCHAR(255)"),
            ("phone_number", "VARCHAR(20)"),
            ("address", "TEXT")
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                try:
                    query = text(f"ALTER TABLE students ADD COLUMN {column_name} {column_type} NULL")
                    db.session.execute(query)
                    db.session.commit()
                    print(f"✓ Added {column_name} column")
                except Exception as e:
                    db.session.rollback()
                    print(f"✗ Error adding {column_name}: {e}")
            else:
                print(f"→ Column {column_name} already exists")
        
        print("\nDone! Now you can uncomment the fields in your Student model.")

if __name__ == '__main__':
    add_profile_columns()