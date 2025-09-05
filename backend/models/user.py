from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from backend.extensions import db

class User(db.Model, UserMixin):
    """User model for authentication"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.Enum('student', 'faculty', 'admin'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    student = db.relationship('Student', backref='user', uselist=False, lazy=True)
    faculty = db.relationship('Faculty', backref='user', uselist=False, lazy=True)
    
    def __init__(self, username, email, password, user_type):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.user_type = user_type
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Required for Flask-Login"""
        return str(self.user_id)
    
    def update_last_login(self):
        """Update last login time"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'user_type': self.user_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f"<User {self.username}>"


class Student(db.Model):
    """Student model for extended student information"""
    __tablename__ = 'students'
    
    student_id = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.Enum('M', 'F', 'Other'), nullable=True)
    program_code = db.Column(db.String(20), nullable=True)
    year_of_study = db.Column(db.Integer, nullable=True)
    enrollment_date = db.Column(db.Date, nullable=False)
    expected_graduation = db.Column(db.Date, nullable=True)
    gpa = db.Column(db.Numeric(3, 2), nullable=True)
    status = db.Column(db.Enum('active', 'inactive', 'graduated', 'withdrawn'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    profile_photo = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    age_band = db.Column(db.Enum('0-35', '35-55', '55+'), default='0-35')
    highest_education = db.Column(db.Enum(
        'No Formal quals', 
        'Lower Than A Level', 
        'A Level or Equivalent', 
        'HE Qualification', 
        'Post Graduate Qualification'
    ), default='A Level or Equivalent')
    num_of_prev_attempts = db.Column(db.Integer, default=0)
    studied_credits = db.Column(db.Integer, default=60)
    has_disability = db.Column(db.Boolean, default=False)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    
    def __init__(self, student_id, user_id, first_name, last_name, enrollment_date, **kwargs):
        self.student_id = student_id
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.enrollment_date = enrollment_date
        
        # Optional fields
        self.date_of_birth = kwargs.get('date_of_birth')
        self.gender = kwargs.get('gender')
        self.program_code = kwargs.get('program_code')
        self.year_of_study = kwargs.get('year_of_study')
        self.expected_graduation = kwargs.get('expected_graduation')
        self.gpa = kwargs.get('gpa')
        self.status = kwargs.get('status', 'active')

        # ADD THESE NEW FIELDS:
        self.age_band = kwargs.get('age_band', '0-35')
        self.highest_education = kwargs.get('highest_education', 'A Level or Equivalent')
        self.num_of_prev_attempts = kwargs.get('num_of_prev_attempts', 0)
        self.studied_credits = kwargs.get('studied_credits', 60)
        self.has_disability = kwargs.get('has_disability', False)
    
    @property
    def full_name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert student to dictionary for API responses"""
        return {
            'student_id': self.student_id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'program_code': self.program_code,
            'year_of_study': self.year_of_study,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'expected_graduation': self.expected_graduation.isoformat() if self.expected_graduation else None,
            'gpa': float(self.gpa) if self.gpa else None,
            'status': self.status,
            'age_band': self.age_band,
            'highest_education': self.highest_education,
            'num_of_prev_attempts': self.num_of_prev_attempts,
            'studied_credits': self.studied_credits,
            'has_disability': self.has_disability

        }
    
    def __repr__(self):
        return f"<Student {self.student_id}: {self.full_name}>"


class Faculty(db.Model):
    """Faculty model for faculty information"""
    __tablename__ = 'faculty'
    
    faculty_id = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(50), nullable=True)
    office_location = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    course_offerings = db.relationship('CourseOffering', backref='faculty', lazy=True)
    
    def __init__(self, faculty_id, user_id, first_name, last_name, **kwargs):
        self.faculty_id = faculty_id
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        
        # Optional fields
        self.department = kwargs.get('department')
        self.position = kwargs.get('position')
        self.office_location = kwargs.get('office_location')
        self.phone = kwargs.get('phone')
    
    @property
    def full_name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert faculty to dictionary for API responses"""
        return {
            'faculty_id': self.faculty_id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'department': self.department,
            'position': self.position,
            'office_location': self.office_location,
            'phone': self.phone
        }
    
    def __repr__(self):
        return f"<Faculty {self.faculty_id}: {self.full_name}>"