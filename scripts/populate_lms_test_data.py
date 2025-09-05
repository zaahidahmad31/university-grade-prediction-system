"""
Script to populate test LMS data for all enrolled students
This will help the ML model make better predictions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.extensions import db
from backend.models import (
    Student, Enrollment, LMSSession, LMSActivity, 
    LMSDailySummary, Attendance
)
from datetime import datetime, timedelta
import random

app = create_app('development')

def populate_lms_data():
    """Populate realistic LMS data for testing"""
    with app.app_context():
        print("\n=== Populating LMS Test Data ===\n")
        
        # Get all active enrollments
        enrollments = Enrollment.query.filter_by(enrollment_status='enrolled').all()
        print(f"Found {len(enrollments)} active enrollments")
        
        if not enrollments:
            print("No active enrollments found. Please enroll students first.")
            return
        
        # Activity patterns for different student types
        patterns = {
            'excellent': {
                'sessions_per_week': 5,
                'activities_per_session': 15,
                'attendance_rate': 0.95
            },
            'good': {
                'sessions_per_week': 3,
                'activities_per_session': 10,
                'attendance_rate': 0.80
            },
            'average': {
                'sessions_per_week': 2,
                'activities_per_session': 5,
                'attendance_rate': 0.70
            },
            'poor': {
                'sessions_per_week': 1,
                'activities_per_session': 3,
                'attendance_rate': 0.50
            }
        }
        
        activity_types = [
            ('page_view', 0.4),
            ('resource_view', 0.3),
            ('assignment_view', 0.1),
            ('video_watch', 0.1),
            ('forum_post', 0.05),
            ('file_download', 0.05)
        ]
        
        for i, enrollment in enumerate(enrollments):
            # Assign a pattern to each student
            pattern_name = list(patterns.keys())[i % len(patterns)]
            pattern = patterns[pattern_name]
            
            print(f"\nProcessing enrollment {enrollment.enrollment_id} "
                  f"(Student: {enrollment.student.student_id}) - Pattern: {pattern_name}")
            
            # Generate data for the past 30 days
            start_date = datetime.now() - timedelta(days=30)
            
            sessions_created = 0
            activities_created = 0
            
            # Create attendance records
            for day in range(30):
                current_date = start_date + timedelta(days=day)
                
                # Skip weekends
                if current_date.weekday() in [5, 6]:
                    continue
                
                # Create attendance based on pattern
                if random.random() < pattern['attendance_rate']:
                    attendance = Attendance(
                        enrollment_id=enrollment.enrollment_id,
                        attendance_date=current_date.date(),
                        status='present' if random.random() > 0.1 else 'late',
                        check_in_time=current_date.replace(hour=9, minute=0).time(),
                        check_out_time=current_date.replace(hour=17, minute=0).time(),
                        duration_minutes=480,
                        recorded_by='system'
                    )
                    db.session.add(attendance)
            
            # Create LMS sessions
            for week in range(4):
                week_start = start_date + timedelta(weeks=week)
                
                # Create sessions for this week
                for _ in range(pattern['sessions_per_week']):
                    # Random day and time
                    day_offset = random.randint(0, 6)
                    hour = random.randint(8, 20)
                    
                    session_start = week_start + timedelta(days=day_offset, hours=hour)
                    session_duration = random.randint(30, 120)  # 30-120 minutes
                    
                    # Create session
                    session = LMSSession(
                        enrollment_id=enrollment.enrollment_id,
                        login_time=session_start,
                        logout_time=session_start + timedelta(minutes=session_duration),
                        duration_minutes=session_duration,
                        ip_address=f"192.168.1.{random.randint(1, 255)}",
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0"
                    )
                    db.session.add(session)
                    db.session.flush()
                    
                    sessions_created += 1
                    
                    # Create activities for this session
                    activity_time = session_start
                    for _ in range(pattern['activities_per_session']):
                        # Select activity type based on weights
                        activity_type = random.choices(
                            [t[0] for t in activity_types],
                            weights=[t[1] for t in activity_types]
                        )[0]
                        
                        # Create activity
                        activity = LMSActivity(
                            session_id=session.session_id,
                            enrollment_id=enrollment.enrollment_id,
                            activity_type=activity_type,
                            activity_timestamp=activity_time,
                            resource_id=f"{activity_type}_{random.randint(1, 100)}",
                            resource_name=f"{activity_type.replace('_', ' ').title()} {random.randint(1, 20)}",
                            duration_seconds=random.randint(30, 300) if 'video' in activity_type else None
                        )
                        db.session.add(activity)
                        
                        activities_created += 1
                        activity_time += timedelta(minutes=random.randint(1, 10))
            
            print(f"  Created {sessions_created} sessions and {activities_created} activities")
        
        # Commit all changes
        db.session.commit()
        print("\n✅ LMS test data populated successfully!")
        
        # Generate daily summaries
        print("\nGenerating daily summaries...")
        from backend.services.lms_summary_service import LMSSummaryService
        
        for day in range(30):
            summary_date = (datetime.now() - timedelta(days=day)).date()
            LMSSummaryService.generate_daily_summary(summary_date)
        
        print("✅ Daily summaries generated!")
        
        # Show summary statistics
        print("\n=== Summary Statistics ===")
        print(f"Total LMS Sessions: {LMSSession.query.count()}")
        print(f"Total LMS Activities: {LMSActivity.query.count()}")
        print(f"Total Daily Summaries: {LMSDailySummary.query.count()}")
        print(f"Total Attendance Records: {Attendance.query.count()}")

if __name__ == '__main__':
    populate_lms_data()