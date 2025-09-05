#!/usr/bin/env python
"""
Script to initialize the database and create an admin user.
Run this script after setting up the database to create the
initial tables and insert the admin user.
"""

import os
import sys
from pathlib import Path
from werkzeug.security import generate_password_hash
from flask import Flask

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

# Import the app and database
from config import config
from backend.extensions import db
from backend.models import User, Student, Faculty, AcademicTerm, Course, CourseOffering, \
    Enrollment, AssessmentType, AlertType, SystemConfig

def init_db(drop=False, admin_username='admin', admin_email='admin@university.edu', admin_password='admin123'):
    """Initialize the database."""
    if drop:
        print('Dropping all tables...')
        db.drop_all()
    
    print('Creating tables...')
    db.create_all()
    
    # Check if admin user already exists
    if User.query.filter_by(username=admin_username).first() is None:
        print('Creating admin user...')
        admin = User(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            user_type='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print(f'Admin user created: {admin_username}')
    else:
        print('Admin user already exists')
    
    # Create initial data if needed
    create_initial_data()
    
    print('Database initialized!')

def create_initial_data():
    """Create initial data for the application"""
    
    # Check if we have already created initial data
    if AcademicTerm.query.first() is not None:
        print('Initial data already exists')
        return
    
    print('Creating initial data...')
    
    # Create assessment types
    assessment_types = [
        AssessmentType('Quiz', 20.00),
        AssessmentType('Assignment', 30.00),
        AssessmentType('Midterm Exam', 20.00),
        AssessmentType('Final Exam', 25.00),
        AssessmentType('Participation', 5.00)
    ]
    db.session.bulk_save_objects(assessment_types)
    
    # Create alert types
    alert_types = [
        AlertType('Low Attendance', 'warning', 'Attendance rate below 70%'),
        AlertType('Missing Assignments', 'warning', 'More than 2 assignments missing'),
        AlertType('Failing Grade Risk', 'critical', 'Predicted grade is F'),
        AlertType('Low Engagement', 'info', 'LMS activity below average'),
        AlertType('Improvement Needed', 'warning', 'Grade declining over time')
    ]
    db.session.bulk_save_objects(alert_types)
    
    # Create system configuration
    system_configs = [
        SystemConfig('attendance_threshold', '70', 'Minimum attendance percentage'),
        SystemConfig('prediction_frequency', 'daily', 'How often to run predictions'),
        SystemConfig('alert_email_enabled', 'true', 'Send email alerts'),
        SystemConfig('model_version', 'v1.0', 'Current active model version')
    ]
    db.session.bulk_save_objects(system_configs)
    
    # Commit changes
    db.session.commit()
    print('Initial data created!')

if __name__ == '__main__':
    # Create a minimal app to run the command
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    
    with app.app_context():
        init_db(drop=False, admin_username='admin', admin_email='admin@university.edu', admin_password='admin123')