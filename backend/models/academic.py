from datetime import datetime
from backend.extensions import db

class AcademicTerm(db.Model):
    """Academic term/semester model"""
    __tablename__ = 'academic_terms'
    
    term_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    term_name = db.Column(db.String(50), nullable=False)
    term_code = db.Column(db.String(20), unique=True, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    
    # Relationships
    course_offerings = db.relationship('CourseOffering', backref='term', lazy=True)
    
    def __init__(self, term_name, term_code, start_date, end_date, is_current=False):
        self.term_name = term_name
        self.term_code = term_code
        self.start_date = start_date
        self.end_date = end_date
        self.is_current = is_current
    
    def to_dict(self):
        """Convert term to dictionary for API responses"""
        return {
            'term_id': self.term_id,
            'term_name': self.term_name,
            'term_code': self.term_code,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_current': self.is_current
        }
    
    def __repr__(self):
        return f"<Term {self.term_code}: {self.term_name}>"


class Course(db.Model):
    """Course model"""
    __tablename__ = 'courses'
    
    course_id = db.Column(db.String(20), primary_key=True)
    course_code = db.Column(db.String(20), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    offerings = db.relationship('CourseOffering', backref='course', lazy=True)
    
    def __init__(self, course_id, course_code, course_name, credits, **kwargs):
        self.course_id = course_id
        self.course_code = course_code
        self.course_name = course_name
        self.credits = credits
        
        # Optional fields
        self.department = kwargs.get('department')
        self.description = kwargs.get('description')
        self.is_active = kwargs.get('is_active', True)
    
    def to_dict(self):
        """Convert course to dictionary for API responses"""
        return {
            'course_id': self.course_id,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'credits': self.credits,
            'department': self.department,
            'description': self.description,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f"<Course {self.course_code}: {self.course_name}>"


class CourseOffering(db.Model):
    """Course offering model (instance of a course in a specific term)"""
    __tablename__ = 'course_offerings'
    
    offering_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.String(20), db.ForeignKey('courses.course_id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('academic_terms.term_id'), nullable=False)
    faculty_id = db.Column(db.String(20), db.ForeignKey('faculty.faculty_id'), nullable=True)
    section_number = db.Column(db.String(10), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)
    enrolled_count = db.Column(db.Integer, default=0)
    meeting_pattern = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(50), nullable=True)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='offering', lazy=True)
    assessments = db.relationship('Assessment', backref='offering', lazy=True)
    
    __table_args__ = (
        db.UniqueConstraint('course_id', 'term_id', 'section_number', name='unique_offering'),
    )
    
    def __init__(self, course_id, term_id, **kwargs):
        self.course_id = course_id
        self.term_id = term_id
        
        # Optional fields
        self.faculty_id = kwargs.get('faculty_id')
        self.section_number = kwargs.get('section_number')
        self.capacity = kwargs.get('capacity')
        self.enrolled_count = kwargs.get('enrolled_count', 0)
        self.meeting_pattern = kwargs.get('meeting_pattern')
        self.location = kwargs.get('location')
    
    def to_dict(self):
        """Convert offering to dictionary for API responses"""
        return {
            'offering_id': self.offering_id,
            'course_id': self.course_id,
            'term_id': self.term_id,
            'faculty_id': self.faculty_id,
            'section_number': self.section_number,
            'capacity': self.capacity,
            'enrolled_count': self.enrolled_count,
            'meeting_pattern': self.meeting_pattern,
            'location': self.location,
            'course': self.course.to_dict() if self.course else None,
            'term': self.term.to_dict() if self.term else None,
            'faculty': self.faculty.to_dict() if self.faculty else None
        }
    
    def __repr__(self):
        return f"<Offering {self.course_id}-{self.section_number} ({self.term.term_code})>"


class Enrollment(db.Model):
    """Student enrollment in a course offering"""
    __tablename__ = 'enrollments'
    
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'), nullable=False)
    offering_id = db.Column(db.Integer, db.ForeignKey('course_offerings.offering_id'), nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False)
    enrollment_status = db.Column(db.Enum('enrolled', 'dropped', 'completed', 'withdrawn'), default='enrolled')
    final_grade = db.Column(db.String(2), nullable=True)
    grade_points = db.Column(db.Numeric(3, 2), nullable=True)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='enrollment', lazy=True)
    lms_sessions = db.relationship('LMSSession', backref='enrollment', lazy=True)
    assessment_submissions = db.relationship('AssessmentSubmission', backref='enrollment', lazy=True)
    predictions = db.relationship('Prediction', backref='enrollment', lazy=True)
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'offering_id', name='unique_enrollment'),
    )
    
    def __init__(self, student_id, offering_id, enrollment_date, **kwargs):
        self.student_id = student_id
        self.offering_id = offering_id
        self.enrollment_date = enrollment_date
        
        # Optional fields
        self.enrollment_status = kwargs.get('enrollment_status', 'enrolled')
        self.final_grade = kwargs.get('final_grade')
        self.grade_points = kwargs.get('grade_points')
    
    def to_dict(self):
        """Convert enrollment to dictionary for API responses"""
        return {
            'enrollment_id': self.enrollment_id,
            'student_id': self.student_id,
            'offering_id': self.offering_id,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'enrollment_status': self.enrollment_status,
            'final_grade': self.final_grade,
            'grade_points': float(self.grade_points) if self.grade_points else None,
            'student': self.student.to_dict() if self.student else None,
            'offering': self.offering.to_dict() if self.offering else None
        }
    
    def __repr__(self):
        return f"<Enrollment {self.student_id} in {self.offering.course.course_code}>"