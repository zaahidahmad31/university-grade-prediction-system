from datetime import datetime
from backend.extensions import db

class Attendance(db.Model):
    """Attendance record for a student in a course"""
    __tablename__ = 'attendance'
    
    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.enrollment_id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('present', 'absent', 'late', 'excused'), nullable=False)
    check_in_time = db.Column(db.Time, nullable=True)
    check_out_time = db.Column(db.Time, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    recorded_by = db.Column(db.String(50), nullable=True)  # 'system' or faculty_id
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, enrollment_id, attendance_date, status, **kwargs):
        self.enrollment_id = enrollment_id
        self.attendance_date = attendance_date
        self.status = status
        
        # Optional fields
        self.check_in_time = kwargs.get('check_in_time')
        self.check_out_time = kwargs.get('check_out_time')
        self.duration_minutes = kwargs.get('duration_minutes')
        self.recorded_by = kwargs.get('recorded_by')
        self.notes = kwargs.get('notes')
    
    def to_dict(self):
        """Convert attendance to dictionary for API responses"""
        return {
            'attendance_id': self.attendance_id,
            'enrollment_id': self.enrollment_id,
            'attendance_date': self.attendance_date.isoformat() if self.attendance_date else None,
            'status': self.status,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'duration_minutes': self.duration_minutes,
            'recorded_by': self.recorded_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<Attendance {self.enrollment_id} on {self.attendance_date}: {self.status}>"


class LMSSession(db.Model):
    """LMS session record for a student"""
    __tablename__ = 'lms_sessions'
    
    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.enrollment_id'), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False)
    logout_time = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Relationships
    activities = db.relationship('LMSActivity', backref='session', lazy=True)
    
    def __init__(self, enrollment_id, login_time, **kwargs):
        self.enrollment_id = enrollment_id
        self.login_time = login_time
        
        # Optional fields
        self.logout_time = kwargs.get('logout_time')
        self.duration_minutes = kwargs.get('duration_minutes')
        self.ip_address = kwargs.get('ip_address')
        self.user_agent = kwargs.get('user_agent')
    
    def end_session(self, logout_time=None):
        """End the session and calculate duration"""
        self.logout_time = logout_time or datetime.utcnow()
        delta = self.logout_time - self.login_time
        self.duration_minutes = int(delta.total_seconds() / 60)
        db.session.commit()
    
    def to_dict(self):
        """Convert session to dictionary for API responses"""
        return {
            'session_id': self.session_id,
            'enrollment_id': self.enrollment_id,
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'logout_time': self.logout_time.isoformat() if self.logout_time else None,
            'duration_minutes': self.duration_minutes,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }
    
    def __repr__(self):
        return f"<LMSSession {self.session_id} for {self.enrollment_id}>"


class LMSActivity(db.Model):
    """LMS activity record for a student"""
    __tablename__ = 'lms_activities'
    
    activity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey('lms_sessions.session_id'), nullable=False)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.enrollment_id'), nullable=False)
    activity_type = db.Column(db.Enum(
        'resource_view', 'forum_post', 'forum_reply', 'assignment_view',
        'quiz_attempt', 'video_watch', 'file_download', 'page_view'
    ), nullable=False)
    activity_timestamp = db.Column(db.DateTime, nullable=False)
    resource_id = db.Column(db.String(50), nullable=True)
    resource_name = db.Column(db.String(255), nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    details = db.Column(db.JSON, nullable=True)
    
    def __init__(self, session_id, enrollment_id, activity_type, activity_timestamp, **kwargs):
        self.session_id = session_id
        self.enrollment_id = enrollment_id
        self.activity_type = activity_type
        self.activity_timestamp = activity_timestamp
        
        # Optional fields
        self.resource_id = kwargs.get('resource_id')
        self.resource_name = kwargs.get('resource_name')
        self.duration_seconds = kwargs.get('duration_seconds')
        self.details = kwargs.get('details')
    
    def to_dict(self):
        """Convert activity to dictionary for API responses"""
        return {
            'activity_id': self.activity_id,
            'session_id': self.session_id,
            'enrollment_id': self.enrollment_id,
            'activity_type': self.activity_type,
            'activity_timestamp': self.activity_timestamp.isoformat() if self.activity_timestamp else None,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'duration_seconds': self.duration_seconds,
            'details': self.details
        }
    
    def __repr__(self):
        return f"<LMSActivity {self.activity_id}: {self.activity_type}>"


class LMSDailySummary(db.Model):
    """Daily summary of LMS activities for a student"""
    __tablename__ = 'lms_daily_summary'
    
    summary_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.enrollment_id'), nullable=False)
    summary_date = db.Column(db.Date, nullable=False)
    total_minutes = db.Column(db.Integer, default=0)
    login_count = db.Column(db.Integer, default=0)
    resource_views = db.Column(db.Integer, default=0)
    forum_posts = db.Column(db.Integer, default=0)
    forum_replies = db.Column(db.Integer, default=0)
    files_downloaded = db.Column(db.Integer, default=0)
    videos_watched = db.Column(db.Integer, default=0)
    pages_viewed = db.Column(db.Integer, default=0)
    
    __table_args__ = (
        db.UniqueConstraint('enrollment_id', 'summary_date', name='unique_daily'),
    )
    
    def __init__(self, enrollment_id, summary_date, **kwargs):
        self.enrollment_id = enrollment_id
        self.summary_date = summary_date
        
        # Activity counts
        self.total_minutes = kwargs.get('total_minutes', 0)
        self.login_count = kwargs.get('login_count', 0)
        self.resource_views = kwargs.get('resource_views', 0)
        self.forum_posts = kwargs.get('forum_posts', 0)
        self.forum_replies = kwargs.get('forum_replies', 0)
        self.files_downloaded = kwargs.get('files_downloaded', 0)
        self.videos_watched = kwargs.get('videos_watched', 0)
        self.pages_viewed = kwargs.get('pages_viewed', 0)
    
    def to_dict(self):
        """Convert summary to dictionary for API responses"""
        return {
            'summary_id': self.summary_id,
            'enrollment_id': self.enrollment_id,
            'summary_date': self.summary_date.isoformat() if self.summary_date else None,
            'total_minutes': self.total_minutes,
            'login_count': self.login_count,
            'resource_views': self.resource_views,
            'forum_posts': self.forum_posts,
            'forum_replies': self.forum_replies,
            'files_downloaded': self.files_downloaded,
            'videos_watched': self.videos_watched,
            'pages_viewed': self.pages_viewed
        }
    
    def __repr__(self):
        return f"<LMSDailySummary {self.enrollment_id} on {self.summary_date}>"