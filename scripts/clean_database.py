# scripts/clean_database.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.extensions import db
from backend.models import *

app = create_app('development')

def clean_database():
    """Clean all data from database (BE CAREFUL!)"""
    with app.app_context():
        response = input("⚠️  This will DELETE ALL DATA. Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
        
        print("Cleaning database...")
        
        # Delete in reverse order of dependencies
        db.session.query(Prediction).delete()
        db.session.query(AssessmentSubmission).delete()
        db.session.query(Assessment).delete()
        db.session.query(Attendance).delete()
        db.session.query(Enrollment).delete()
        db.session.query(CourseOffering).delete()
        db.session.query(Course).delete()
        db.session.query(Student).delete()
        db.session.query(Faculty).delete()
        db.session.query(User).delete()
        db.session.query(AssessmentType).delete()
        db.session.query(AcademicTerm).delete()
        
        db.session.commit()
        print("✅ Database cleaned successfully!")

if __name__ == '__main__':
    clean_database()