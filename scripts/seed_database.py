import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, date
import random
from backend.app import create_app 
from backend.extensions import db
from backend.models import (
    User, Student, Faculty, Course, CourseOffering, 
    Enrollment, Attendance, Assessment, Prediction,
    AcademicTerm, AssessmentType, AssessmentSubmission
)
from backend.services.auth_service import register_user

app = create_app('development')

# Sample data
FIRST_NAMES = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'James', 'Emily', 'Robert', 'Lisa']
LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
DEPARTMENTS = ['Computer Science', 'Mathematics', 'Physics', 'Engineering', 'Data Science']
PROGRAMS = ['CS', 'DS', 'SE', 'IT', 'AI']

def create_academic_terms():
    """Create academic terms"""
    print("Creating academic terms...")
    
    # Create terms using the constructor from your model
    term1 = AcademicTerm(
        term_name='Fall 2024',
        term_code='FALL2024',
        start_date=date(2024, 9, 1),
        end_date=date(2024, 12, 20),
        is_current=False
    )
    db.session.add(term1)
    
    term2 = AcademicTerm(
        term_name='Spring 2025',
        term_code='SPRING2025',
        start_date=date(2025, 1, 15),
        end_date=date(2025, 5, 15),
        is_current=True
    )
    db.session.add(term2)
    
    db.session.commit()
    return AcademicTerm.query.filter_by(is_current=True).first()

def create_assessment_types():
    """Create assessment types"""
    print("Creating assessment types...")
    
    # Check if already exists
    if AssessmentType.query.first():
        print("  Assessment types already exist, skipping...")
        return
    
    assessment_types = [
        AssessmentType(type_name='Quiz', weight_percentage=20.0),
        AssessmentType(type_name='Assignment', weight_percentage=30.0),
        AssessmentType(type_name='Midterm Exam', weight_percentage=20.0),
        AssessmentType(type_name='Final Exam', weight_percentage=25.0),
        AssessmentType(type_name='Participation', weight_percentage=5.0)
    ]
    
    for assessment_type in assessment_types:
        db.session.add(assessment_type)
        print(f"  Created assessment type: {assessment_type.type_name}")
    
    db.session.commit()

def create_faculty_users(count=5):
    """Create faculty users"""
    print(f"Creating {count} faculty users...")
    faculty_list = []
    
    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        username = f"{first_name.lower()}.{last_name.lower()}{i}"
        email = f"{username}@university.edu"
        
        # Register faculty user
        user, error = register_user(
            username=username,
            email=email,
            password='password123',
            user_type='faculty',
            first_name=first_name,
            last_name=last_name,
            department=random.choice(DEPARTMENTS),
            position=random.choice(['Professor', 'Associate Professor', 'Assistant Professor'])
        )
        
        if user and user.faculty:
            faculty_list.append(user.faculty)
            print(f"  Created faculty: {username}")
        elif error:
            print(f"  Error creating faculty {username}: {error}")
    
    return faculty_list

def create_student_users(count=30):
    """Create student users"""
    print(f"Creating {count} student users...")
    student_list = []
    
    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        username = f"{first_name.lower()}.{last_name.lower()}{i}"
        email = f"{username}@student.university.edu"
        
        # Register student user
        user, error = register_user(
            username=username,
            email=email,
            password='password123',
            user_type='student',
            first_name=first_name,
            last_name=last_name,
            program_code=random.choice(PROGRAMS),
            year_of_study=random.randint(1, 4),
            date_of_birth=date(2000 + random.randint(0, 5), random.randint(1, 12), random.randint(1, 28)),
            gender=random.choice(['M', 'F', 'Other'])
        )
        
        if user and user.student:
            # Set a random GPA
            user.student.gpa = round(random.uniform(2.0, 4.0), 2)
            db.session.commit()
            student_list.append(user.student)
            print(f"  Created student: {username}")
        elif error:
            print(f"  Error creating student {username}: {error}")
    
    return student_list

def create_courses():
    """Create courses"""
    print("Creating courses...")
    
    courses_data = [
        {'course_id': 'CS101', 'course_code': 'CS101', 'course_name': 'Introduction to Computer Science', 'credits': 3, 'department': 'Computer Science'},
        {'course_id': 'CS201', 'course_code': 'CS201', 'course_name': 'Data Structures and Algorithms', 'credits': 4, 'department': 'Computer Science'},
        {'course_id': 'CS301', 'course_code': 'CS301', 'course_name': 'Database Systems', 'credits': 3, 'department': 'Computer Science'},
        {'course_id': 'CS401', 'course_code': 'CS401', 'course_name': 'Machine Learning', 'credits': 4, 'department': 'Computer Science'},
        {'course_id': 'DS101', 'course_code': 'DS101', 'course_name': 'Introduction to Data Science', 'credits': 3, 'department': 'Data Science'},
        {'course_id': 'DS201', 'course_code': 'DS201', 'course_name': 'Statistical Analysis', 'credits': 3, 'department': 'Data Science'},
        {'course_id': 'MATH101', 'course_code': 'MATH101', 'course_name': 'Calculus I', 'credits': 4, 'department': 'Mathematics'},
        {'course_id': 'MATH201', 'course_code': 'MATH201', 'course_name': 'Linear Algebra', 'credits': 3, 'department': 'Mathematics'},
        {'course_id': 'ENG101', 'course_code': 'ENG101', 'course_name': 'Engineering Fundamentals', 'credits': 3, 'department': 'Engineering'},
        {'course_id': 'PHY101', 'course_code': 'PHY101', 'course_name': 'Physics I', 'credits': 4, 'department': 'Physics'}
    ]
    
    courses = []
    for course_data in courses_data:
        # Check if course already exists
        existing_course = Course.query.filter_by(course_id=course_data['course_id']).first()
        if existing_course:
            courses.append(existing_course)
            print(f"  Course already exists: {course_data['course_code']}")
        else:
            course = Course(
                course_id=course_data['course_id'],
                course_code=course_data['course_code'],
                course_name=course_data['course_name'],
                credits=course_data['credits'],
                department=course_data['department']
            )
            db.session.add(course)
            courses.append(course)
            print(f"  Created course: {course_data['course_code']} - {course_data['course_name']}")
    
    db.session.commit()
    return courses

def create_course_offerings(courses, faculty_list, current_term):
    """Create course offerings"""
    print("Creating course offerings...")
    offerings = []
    
    for course in courses:
        # Create 1-2 sections per course
        num_sections = random.randint(1, 2)
        for section in range(num_sections):
            faculty = random.choice(faculty_list)
            
            # Check if offering already exists
            existing = CourseOffering.query.filter_by(
                course_id=course.course_id,
                term_id=current_term.term_id,
                section_number=chr(65 + section)
            ).first()
            
            if existing:
                offerings.append(existing)
                continue
            
            offering = CourseOffering(
                course_id=course.course_id,
                term_id=current_term.term_id,
                faculty_id=faculty.faculty_id,
                section_number=chr(65 + section),
                capacity=random.randint(20, 40),
                enrolled_count=0,
                meeting_pattern=random.choice(['MWF 9:00-10:00', 'TTh 10:30-12:00', 'MWF 14:00-15:00']),
                location=f"Room {random.randint(100, 500)}"
            )
            db.session.add(offering)
            offerings.append(offering)
            print(f"  Created offering: {course.course_code} Section {offering.section_number}")
    
    db.session.commit()
    return offerings

def create_enrollments(students, offerings):
    """Create student enrollments"""
    print("Creating enrollments...")
    enrollments = []
    
    for student in students:
        # Each student enrolls in 3-5 courses
        num_courses = random.randint(3, 5)
        selected_offerings = random.sample(offerings, min(num_courses, len(offerings)))
        
        for offering in selected_offerings:
            # Check if already enrolled
            existing = Enrollment.query.filter_by(
                student_id=student.student_id,
                offering_id=offering.offering_id
            ).first()
            
            if existing:
                enrollments.append(existing)
                continue
            
            # Check capacity
            if offering.enrolled_count < offering.capacity:
                enrollment = Enrollment(
                    student_id=student.student_id,
                    offering_id=offering.offering_id,
                    enrollment_date=date.today() - timedelta(days=random.randint(30, 60)),
                    enrollment_status='enrolled'
                )
                db.session.add(enrollment)
                enrollments.append(enrollment)
                
                # Update enrolled count
                offering.enrolled_count += 1
                
                print(f"  Enrolled {student.first_name} {student.last_name} in {offering.course.course_code}")
    
    db.session.commit()
    return enrollments

def create_attendance_records(enrollments):
    """Create attendance records"""
    print("Creating attendance records...")
    
    for enrollment in enrollments:
        # Check if attendance already exists
        existing_attendance = Attendance.query.filter_by(enrollment_id=enrollment.enrollment_id).first()
        if existing_attendance:
            continue
        
        # Create attendance for past 30 days (excluding weekends)
        for days_ago in range(30):
            date_to_check = date.today() - timedelta(days=days_ago)
            
            # Skip weekends
            if date_to_check.weekday() in [5, 6]:  # Saturday, Sunday
                continue
            
            # Random attendance with 80% probability of being present
            status = random.choices(
                ['present', 'absent', 'late'],
                weights=[0.8, 0.15, 0.05]
            )[0]
            
            attendance = Attendance(
                enrollment_id=enrollment.enrollment_id,
                attendance_date=date_to_check,
                status=status,
                check_in_time=datetime.combine(date_to_check, 
                    datetime.strptime(f"{random.randint(8,10)}:{random.randint(0,59)}", "%H:%M").time()
                ) if status != 'absent' else None
            )
            db.session.add(attendance)
    
    db.session.commit()
    print("  Created attendance records")

def create_assessments(offerings):
    """Create assessments for courses"""
    print("Creating assessments...")
    
    assessment_types = AssessmentType.query.all()
    
    for offering in offerings:
        # Create assessments for each type
        for i, assessment_type in enumerate(assessment_types):
            # Check if assessment already exists
            existing = Assessment.query.filter_by(
                offering_id=offering.offering_id,
                type_id=assessment_type.type_id,
                title=f"{assessment_type.type_name} {i+1}"
            ).first()
            
            if existing:
                continue
            
            assessment = Assessment(
                offering_id=offering.offering_id,
                type_id=assessment_type.type_id,
                title=f"{assessment_type.type_name} {i+1}",
                max_score=100.0,
                due_date=datetime.now() + timedelta(days=random.randint(-30, 30)),
                weight=assessment_type.weight_percentage,
                description=f"{assessment_type.type_name} for {offering.course.course_name}",
                is_published=True
            )
            db.session.add(assessment)
            print(f"  Created assessment: {assessment.title} for {offering.course.course_code}")
    
    db.session.commit()

def create_assessment_submissions(enrollments):
    """Create some assessment submissions"""
    print("Creating assessment submissions...")
    
    for enrollment in enrollments:
        # Get assessments for this enrollment's offering
        assessments = Assessment.query.filter_by(offering_id=enrollment.offering_id).all()
        
        # Submit some assessments (70% chance for each)
        for assessment in assessments:
            if random.random() < 0.7:  # 70% submission rate
                # Check if already submitted
                existing = AssessmentSubmission.query.filter_by(
                    enrollment_id=enrollment.enrollment_id,
                    assessment_id=assessment.assessment_id
                ).first()
                
                if existing:
                    continue
                
                # Create submission
                is_late = random.random() < 0.1  # 10% late submissions
                score = random.uniform(60, 100) if not is_late else random.uniform(50, 90)
                
                # Fix: Convert max_score to float
                max_score_float = float(assessment.max_score) if assessment.max_score else 100.0
                
                submission = AssessmentSubmission(
                    enrollment_id=enrollment.enrollment_id,
                    assessment_id=assessment.assessment_id,
                    submission_date=assessment.due_date - timedelta(hours=random.randint(1, 48)) if not is_late else 
                                   assessment.due_date + timedelta(hours=random.randint(1, 24)),
                    score=score,
                    percentage=(score / max_score_float) * 100,  # Fixed line
                    is_late=is_late,
                    late_penalty=10 if is_late else 0,
                    graded_date=datetime.now(),
                    graded_by='SYSTEM'
                )
                db.session.add(submission)
    
    db.session.commit()
    print("  Created assessment submissions")

def create_predictions(enrollments):
    """Create grade predictions"""
    print("Creating grade predictions...")
    
    for enrollment in enrollments:
        # Check if prediction already exists
        existing = Prediction.query.filter_by(enrollment_id=enrollment.enrollment_id).first()
        if existing:
            continue
        
        # Calculate attendance rate
        attendance_records = Attendance.query.filter_by(enrollment_id=enrollment.enrollment_id).all()
        if attendance_records:
            present_count = sum(1 for a in attendance_records if a.status in ['present', 'late'])
            attendance_rate = present_count / len(attendance_records)
        else:
            attendance_rate = 0.8
        
        # Get assessment average
        submissions = AssessmentSubmission.query.filter_by(enrollment_id=enrollment.enrollment_id).all()
        if submissions:
            # Convert percentage to float if it's a decimal
            percentages = [float(s.percentage) if s.percentage else 0 for s in submissions]
            avg_score = sum(percentages) / len(percentages) if percentages else 75
        else:
            avg_score = 75
        
        # Convert to float to ensure proper arithmetic
        attendance_rate = float(attendance_rate)
        avg_score = float(avg_score)
        
        # Predict grade based on attendance and assessment scores
        combined_score = (attendance_rate * 40) + (avg_score * 0.6)
        
        if combined_score >= 90:
            predicted_grade = 'A'
            risk_level = 'low'
        elif combined_score >= 80:
            predicted_grade = 'B'
            risk_level = 'low'
        elif combined_score >= 70:
            predicted_grade = 'C'
            risk_level = 'medium'
        elif combined_score >= 60:
            predicted_grade = 'D'
            risk_level = 'high'
        else:
            predicted_grade = 'F'
            risk_level = 'high'
        
        prediction = Prediction(
            enrollment_id=enrollment.enrollment_id,
            prediction_date=datetime.now(),
            predicted_grade=predicted_grade,
            confidence_score=round(random.uniform(0.65, 0.95), 2),
            risk_level=risk_level,
            model_version='v1.0',
            feature_snapshot={
                'attendance_rate': round(attendance_rate, 2),
                'assessment_average': round(avg_score, 2),
                'combined_score': round(combined_score, 2)
            }
        )
        db.session.add(prediction)
    
    db.session.commit()
    print("  Created predictions")

def seed_database():
    """Main function to seed the database"""
    with app.app_context():
        print("Starting database seeding...")
        
        # Check if data already exists
        if User.query.count() > 0:
            response = input("Database already contains data. Do you want to continue? (y/n): ")
            if response.lower() != 'y':
                print("Seeding cancelled.")
                return
        
        try:
            # Create basic data
            current_term = create_academic_terms()
            create_assessment_types()
            
            # Create users
            faculty_list = create_faculty_users(5)
            student_list = create_student_users(30)
            
            # Create courses and offerings
            courses = create_courses()
            offerings = create_course_offerings(courses, faculty_list, current_term)
            
            # Create enrollments
            enrollments = create_enrollments(student_list, offerings)
            
            # Create attendance
            create_attendance_records(enrollments)
            
            # Create assessments
            create_assessments(offerings)
            
            # Create assessment submissions
            create_assessment_submissions(enrollments)
            
            # Create predictions
            create_predictions(enrollments)
            
            print("\n✅ Database seeding completed successfully!")
            print("\nSample login credentials:")
            print("  Faculty: john.smith0 / password123")
            print("  Student: jane.johnson0 / password123")
            print("\nAll users have the password: password123")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    seed_database()