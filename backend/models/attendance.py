# backend/models/attendance.py - FIXED VERSION
from backend.extensions import db
from datetime import datetime
from sqlalchemy.dialects.mysql import ENUM

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    attendance_id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.enrollment_id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(
        ENUM('present', 'absent', 'late', 'excused', name='attendance_status'),
        nullable=False
    )
    check_in_time = db.Column(db.Time, nullable=True)
    check_out_time = db.Column(db.Time, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    recorded_by = db.Column(db.String(50), nullable=True)  # faculty_id or 'system'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    enrollment = db.relationship('Enrollment', backref='attendance_records')
    
    # Indexes - FIXED: Added extend_existing=True
    __table_args__ = (
        db.Index('idx_enrollment_date', 'enrollment_id', 'attendance_date'),
        db.Index('idx_date', 'attendance_date'),
        db.Index('idx_status', 'status'),
        db.UniqueConstraint('enrollment_id', 'attendance_date', name='unique_enrollment_date'),
        {'extend_existing': True}  # THIS IS THE KEY FIX
    )
    
    def __repr__(self):
        return f'<Attendance {self.attendance_id}: {self.status} on {self.attendance_date}>'
    
    def to_dict(self):
        return {
            'attendance_id': self.attendance_id,
            'enrollment_id': self.enrollment_id,
            'attendance_date': self.attendance_date.isoformat() if self.attendance_date else None,
            'status': self.status,
            'check_in_time': self.check_in_time.strftime('%H:%M') if self.check_in_time else None,
            'check_out_time': self.check_out_time.strftime('%H:%M') if self.check_out_time else None,
            'duration_minutes': self.duration_minutes,
            'recorded_by': self.recorded_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_student_attendance_rate(cls, student_id, course_offering_id=None):
        """Calculate attendance rate for a student"""
        from backend.models.academic import Enrollment  # Import here to avoid circular imports
        
        query = cls.query.join(Enrollment).filter(Enrollment.student_id == student_id)
        
        if course_offering_id:
            query = query.filter(Enrollment.course_offering_id == course_offering_id)
        
        total_records = query.count()
        if total_records == 0:
            return 0
        
        present_records = query.filter(cls.status.in_(['present', 'late'])).count()
        return round((present_records / total_records) * 100, 2)
    
    @classmethod
    def get_course_attendance_summary(cls, course_offering_id):
        """Get attendance summary for a course"""
        from sqlalchemy import func
        from backend.models.academic import Enrollment  # Import here to avoid circular imports
        
        summary = db.session.query(
            func.count(cls.attendance_id).label('total_classes'),
            func.sum(db.case([(cls.status == 'present', 1)], else_=0)).label('present_count'),
            func.sum(db.case([(cls.status == 'absent', 1)], else_=0)).label('absent_count'),
            func.sum(db.case([(cls.status == 'late', 1)], else_=0)).label('late_count'),
            func.sum(db.case([(cls.status == 'excused', 1)], else_=0)).label('excused_count')
        ).join(Enrollment).filter(
            Enrollment.course_offering_id == course_offering_id
        ).first()
        
        return summary