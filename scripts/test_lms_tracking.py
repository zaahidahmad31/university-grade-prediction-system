"""
Script to test if LMS tracking is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.extensions import db
from backend.models import User, Student, Enrollment, LMSSession, LMSActivity
from flask import g
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app('development')

def test_activity_tracking():
    """Test if activity tracking is working"""
    with app.app_context():
        print("\n=== Testing LMS Activity Tracking ===\n")
        
        # 1. Check if any students exist
        students = Student.query.all()
        print(f"Found {len(students)} students")
        
        if not students:
            print("❌ No students found. Please create at least one student first.")
            return
        
        # 2. Check enrollments
        enrollments = Enrollment.query.filter_by(enrollment_status='enrolled').all()
        print(f"Found {len(enrollments)} active enrollments")
        
        if not enrollments:
            print("❌ No active enrollments found. Please enroll a student first.")
            return
        
        # 3. Check if ActivityTracker is registered
        print(f"\nActivityTracker registered: {hasattr(app, 'before_request_funcs')}")
        print(f"Before request handlers: {len(app.before_request_funcs.get(None, []))}")
        
        # 4. Simulate a request with user context
        enrollment = enrollments[0]
        user = User.query.filter_by(user_id=enrollment.student.user_id).first()
        
        print(f"\nSimulating request for user: {user.username}")
        
        with app.test_request_context('/api/student/dashboard'):
            # Manually set g.current_user (simulating JWT middleware)
            g.current_user = user
            
            # The ActivityTracker should handle this automatically
            # Let's check if it creates a session
            print(f"g.current_user is set: {hasattr(g, 'current_user') and g.current_user is not None}")
            
            if hasattr(g, 'current_user') and g.current_user:
                print(f"Current user: {g.current_user.username}")
                
                # Check for student attribute
                if hasattr(g.current_user, 'student'):
                    print(f"✅ User has student profile: {g.current_user.student.student_id}")
                else:
                    print("❌ User has no student profile")
                    
            # Manually trigger the activity tracker's before_request
            from backend.middleware.activity_tracker import ActivityTracker
            # Get the app's activity tracker instance
            if hasattr(app, 'before_request_funcs'):
                print("\nManually triggering before_request handlers...")
                for handler in app.before_request_funcs.get(None, []):
                    try:
                        handler()
                    except Exception as e:
                        print(f"Handler error: {e}")
                
                # Check if session was created
                if hasattr(g, 'current_session'):
                    print(f"✅ Session created: {g.current_session.session_id}")
                else:
                    print("❌ No session created")
        
        # 5. Check database for sessions and activities
        print(f"\nDatabase check:")
        print(f"Total LMS sessions: {LMSSession.query.count()}")
        print(f"Total LMS activities: {LMSActivity.query.count()}")
        
        # 6. Show recent sessions
        recent_sessions = LMSSession.query.order_by(LMSSession.login_time.desc()).limit(5).all()
        if recent_sessions:
            print(f"\nRecent sessions:")
            for session in recent_sessions:
                print(f"  - Session {session.session_id}: Enrollment {session.enrollment_id}, "
                      f"Login: {session.login_time}, Duration: {session.duration_minutes} min")

if __name__ == '__main__':
    test_activity_tracking()