#!/usr/bin/env python
"""
Script to populate test data for prediction testing
"""
import sys
import os
from datetime import datetime, timedelta, date
import random

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.extensions import db
from backend.models import *

def populate_test_data():
    """Populate test data for predictions"""
    app = create_app()
    
    with app.app_context():
        # Get the first enrollment (created by init script)
        enrollment = Enrollment.query.first()
        if not enrollment:
            print("No enrollment found! Run init_database.py first")
            return
        
        print(f"Populating data for enrollment {enrollment.enrollment_id}")
        
        # Create attendance records for the past 30 days
        create_attendance_records(enrollment.enrollment_id, days=30)
        
        # Create LMS activity data
        create_lms_activity(enrollment.enrollment_id, days=30)
        
        # Create assessment submissions
        create_assessment_submissions(enrollment.enrollment_id)
        
        print("Test data populated successfully!")

def create_attendance_records(enrollment_id, days=30):
    """Create attendance records"""
    print("Creating attendance records...")
    
    # Start from 30 days ago
    start_date = date.today() - timedelta(days=days)
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # Skip weekends
        if current_date.weekday() in [5, 6]:
            continue
        
        # 85% attendance rate with some randomness
        if random.random() < 0.85:
            status = 'present' if random.random() < 0.9 else 'late'
        else:
            status = 'absent'
        
        attendance = Attendance(
            enrollment_id=enrollment_id,
            attendance_date=current_date,
            status=status,
            recorded_by='system'
        )
        
        if status in ['present', 'late']:
            attendance.check_in_time = datetime.combine(
                current_date, 
                datetime.strptime("09:00", "%H:%M").time()
            ).time()
            attendance.duration_minutes = random.randint(45, 60)
        
        db.session.add(attendance)
    
    db.session.commit()
    print(f"Created {days} attendance records")

def create_lms_activity(enrollment_id, days=30):
    """Create LMS activity data"""
    print("Creating LMS activity...")
    
    start_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # Create 0-3 sessions per day
        num_sessions = random.randint(0, 3)
        
        for _ in range(num_sessions):
            # Random login time during the day
            login_hour = random.randint(8, 22)
            login_minute = random.randint(0, 59)
            login_time = current_date.replace(
                hour=login_hour, 
                minute=login_minute, 
                second=0, 
                microsecond=0
            )
            
            # Session duration between 10-120 minutes
            duration = random.randint(10, 120)
            logout_time = login_time + timedelta(minutes=duration)
            
            session = LMSSession(
                enrollment_id=enrollment_id,
                login_time=login_time,
                logout_time=logout_time,
                duration_minutes=duration
            )
            db.session.add(session)
            db.session.flush()  # Get session ID
            
            # Create activities within the session
            num_activities = random.randint(3, 15)
            activity_types = [
                'resource_view', 'page_view', 'forum_post', 
                'forum_reply', 'video_watch', 'file_download'
            ]
            
            for j in range(num_activities):
                activity_time = login_time + timedelta(
                    minutes=random.randint(0, duration)
                )
                
                activity = LMSActivity(
                    session_id=session.session_id,
                    enrollment_id=enrollment_id,
                    activity_type=random.choice(activity_types),
                    activity_timestamp=activity_time,
                    resource_id=f'RES{random.randint(100, 999)}',
                    resource_name=f'Resource {random.randint(1, 50)}'
                )
                
                if activity.activity_type == 'video_watch':
                    activity.duration_seconds = random.randint(60, 1800)
                
                db.session.add(activity)
            
            # Create daily summary
            summary_date = current_date.date()
            existing_summary = LMSDailySummary.query.filter_by(
                enrollment_id=enrollment_id,
                summary_date=summary_date
            ).first()
            
            if not existing_summary:
                summary = LMSDailySummary(
                    enrollment_id=enrollment_id,
                    summary_date=summary_date,
                    total_minutes=duration,
                    login_count=1,
                    resource_views=random.randint(5, 20),
                    forum_posts=random.randint(0, 2),
                    forum_replies=random.randint(0, 3),
                    files_downloaded=random.randint(0, 5),
                    videos_watched=random.randint(0, 3),
                    pages_viewed=random.randint(10, 30)
                )
                db.session.add(summary)
            else:
                existing_summary.total_minutes += duration
                existing_summary.login_count += 1
    
    db.session.commit()
    print("Created LMS activity data")

def create_assessment_submissions(enrollment_id):
    """Create assessment submissions"""
    print("Creating assessment submissions...")
    
    # Get assessments for the enrollment's course
    enrollment = Enrollment.query.get(enrollment_id)
    assessments = Assessment.query.filter_by(
        offering_id=enrollment.offering_id
    ).all()
    
    for assessment in assessments:
        # Submit with 90% probability
        if random.random() < 0.9:
            # Score between 65-95
            score = random.uniform(65, 95)
            
            submission = AssessmentSubmission(
                enrollment_id=enrollment_id,
                assessment_id=assessment.assessment_id,
                submission_date=datetime.now() - timedelta(days=random.randint(1, 10)),
                score=score,
                percentage=score,
                is_late=random.random() < 0.1,  # 10% late submissions
                graded_date=datetime.now() - timedelta(days=random.randint(0, 5)),
                graded_by='FAC001'
            )
            
            db.session.add(submission)
    
    db.session.commit()
    print("Created assessment submissions")

def create_multiple_students(count=10):
    """Create multiple students with data for testing"""
    app = create_app()
    
    with app.app_context():
        # Get current term and offering
        term = AcademicTerm.query.filter_by(is_current=True).first()
        offering = CourseOffering.query.first()
        
        if not term or not offering:
            print("No term or offering found! Run init_database.py first")
            return
        
        print(f"Creating {count} additional students...")
        
        for i in range(2, count + 2):  # Start from 2 since we already have STU001
            # Create user
            user = User(
                username=f'student{i}',
                email=f'student{i}@university.edu',
                password='student123',
                user_type='student'
            )
            db.session.add(user)
            db.session.flush()
            
            # Create student profile with demographic data
            age_bands = ['0-35', '35-55', '55+']
            education_levels = [
                'No Formal quals', 
                'Lower Than A Level', 
                'A Level or Equivalent', 
                'HE Qualification', 
                'Post Graduate Qualification'
            ]
            
            student = Student(
                student_id=f'STU{i:03d}',
                user_id=user.user_id,
                first_name=f'Student',
                last_name=f'{i}',
                enrollment_date=date(2023, 9, 1),
                program_code='CS',
                year_of_study=random.randint(1, 4),
                age_band=random.choice(age_bands),
                highest_education=random.choice(education_levels),
                num_of_prev_attempts=random.randint(0, 2),
                studied_credits=random.choice([30, 60, 90, 120]),
                has_disability=random.random() < 0.1  # 10% have disability
            )
            db.session.add(student)
            db.session.flush()
            
            # Enroll in course
            enrollment = Enrollment(
                student_id=student.student_id,
                offering_id=offering.offering_id,
                enrollment_date=date.today() - timedelta(days=30)
            )
            db.session.add(enrollment)
            db.session.flush()
            
            # Create data with varying patterns
            # Some students with poor attendance/performance
            if i % 3 == 0:
                # Poor performer
                create_attendance_records(enrollment.enrollment_id, days=30)
                create_lms_activity(enrollment.enrollment_id, days=30)
            else:
                # Good performer
                create_attendance_records(enrollment.enrollment_id, days=30)
                create_lms_activity(enrollment.enrollment_id, days=30)
            
            create_assessment_submissions(enrollment.enrollment_id)
            
            print(f"Created student {i}/{count}")
        
        db.session.commit()
        print(f"Created {count} students with data")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Populate test data')
    parser.add_argument('--students', type=int, default=0, 
                       help='Number of additional students to create')
    
    args = parser.parse_args()
    
    if args.students > 0:
        create_multiple_students(args.students)
    else:
        populate_test_data()