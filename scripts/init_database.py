#!/usr/bin/env python
"""
Script to initialize the database with all tables
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.extensions import db
from backend.models import *  # This imports all models including MLFeatureStaging

def init_database():
    """Initialize the database with all tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Create default data
        create_default_data()
        
        print("Database initialization complete!")

def create_default_data():
    """Create default data for the system"""
    
    # Check if data already exists
    if User.query.count() > 0:
        print("Data already exists, skipping initialization")
        return
    
    # Create assessment types (including OULAD types)
    assessment_types = [
        AssessmentType('Quiz', 10),
        AssessmentType('Assignment', 30),
        AssessmentType('Midterm Exam', 30),
        AssessmentType('Final Exam', 30),
        # Add OULAD-specific types
        AssessmentType('CMA', 30),  # Computer Marked Assessment
        AssessmentType('TMA', 50),  # Tutor Marked Assessment
        AssessmentType('Exam', 20)
    ]
    
    for at in assessment_types:
        db.session.add(at)
    
    # Create alert types
    alert_types = [
        AlertType('low_attendance', 'warning', 'Student attendance below 75%'),
        AlertType('missing_assignments', 'warning', 'Student has missing assignments'),
        AlertType('at_risk_prediction', 'critical', 'Student predicted to be at risk'),
        AlertType('low_engagement', 'info', 'Student LMS engagement is low'),
        AlertType('grade_drop', 'warning', 'Student grades dropping significantly')
    ]
    
    for alert_type in alert_types:
        db.session.add(alert_type)
    
    # Create system configuration
    configs = [
        SystemConfig('model_version', 'v1.0', 'Current ML model version'),
        SystemConfig('attendance_threshold', '75', 'Minimum attendance percentage'),
        SystemConfig('prediction_frequency', 'weekly', 'How often to run predictions'),
        SystemConfig('alert_email_enabled', 'true', 'Enable email alerts'),
        SystemConfig('maintenance_mode', 'false', 'System maintenance mode')
    ]
    
    for config in configs:
        db.session.add(config)
    
    # Create an academic term
    from datetime import date
    term = AcademicTerm(
        term_name='Fall 2024',
        term_code='F2024',
        start_date=date(2024, 9, 1),
        end_date=date(2024, 12, 20),
        is_current=True
    )
    db.session.add(term)
    
    # Create sample users (admin, faculty, student)
    admin_user = User('admin', 'admin@university.edu', 'admin123', 'admin')
    faculty_user = User('john.smith', 'john.smith@university.edu', 'faculty123', 'faculty')
    student_user = User('jane.doe', 'jane.doe@university.edu', 'student123', 'student')
    
    db.session.add(admin_user)
    db.session.add(faculty_user)
    db.session.add(student_user)
    db.session.flush()  # Get user IDs
    
    # Create faculty profile
    faculty = Faculty(
        faculty_id='FAC001',
        user_id=faculty_user.user_id,
        first_name='John',
        last_name='Smith',
        department='Computer Science',
        position='Assistant Professor',
        office_location='Building A, Room 301'
    )
    db.session.add(faculty)
    
    # Create student profile with demographic data
    student = Student(
        student_id='STU001',
        user_id=student_user.user_id,
        first_name='Jane',
        last_name='Doe',
        enrollment_date=date(2023, 9, 1),
        program_code='CS',
        year_of_study=2,
        expected_graduation=date(2026, 5, 15),
        # Add demographic fields
        age_band='0-35',
        highest_education='A Level or Equivalent',
        num_of_prev_attempts=0,
        studied_credits=60,
        has_disability=False
    )
    db.session.add(student)
    
    # Create a sample course
    course = Course(
        course_id='CS101',
        course_code='CS101',
        course_name='Introduction to Computer Science',
        credits=3,
        department='Computer Science',
        description='Fundamental concepts of computer science'
    )
    db.session.add(course)
    db.session.flush()
    
    # Create course offering
    offering = CourseOffering(
        course_id=course.course_id,
        term_id=term.term_id,
        faculty_id=faculty.faculty_id,
        section_number='001',
        capacity=30,
        meeting_pattern='MWF 10:00-11:00',
        location='Room 101'
    )
    db.session.add(offering)
    db.session.flush()
    
    # Enroll student
    enrollment = Enrollment(
        student_id=student.student_id,
        offering_id=offering.offering_id,
        enrollment_date=date.today()
    )
    db.session.add(enrollment)
    
    # Create sample assessments
    db.session.flush()  # Get offering ID
    
    quiz = Assessment(
        offering_id=offering.offering_id,
        type_id=1,  # Quiz
        title='Quiz 1: Introduction',
        max_score=100,
        weight=5,
        is_published=True,
        assessment_type_mapped='Quiz'  # Add this
    )
    db.session.add(quiz)
    
    assignment = Assessment(
        offering_id=offering.offering_id,
        type_id=2,  # Assignment
        title='Assignment 1: Hello World',
        max_score=100,
        weight=10,
        is_published=True,
        assessment_type_mapped='Assignment'  # Add this
    )
    db.session.add(assignment)
    
    # Record initial model version
    model_version = ModelVersion(
        version_name='grade_predictor_v1',
        model_file_path='ml_models/grade_predictor.pkl',
        accuracy=85.5,
        precision_score=83.2,
        recall_score=87.1,
        f1_score=85.1,
        training_date=date.today(),
        is_active=True,
        notes='Initial model deployment'
    )
    db.session.add(model_version)
    
    # Commit all changes
    db.session.commit()
    
    print("Default data created successfully!")
    print("\nTest Accounts Created:")
    print("Admin: username='admin', password='admin123'")
    print("Faculty: username='john.smith', password='faculty123'")
    print("Student: username='jane.doe', password='student123'")

if __name__ == '__main__':
    init_database()