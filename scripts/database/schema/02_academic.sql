-- Academic terms/semesters
CREATE TABLE IF NOT EXISTS academic_terms (
    term_id INT PRIMARY KEY AUTO_INCREMENT,
    term_name VARCHAR(50) NOT NULL,
    term_code VARCHAR(20) UNIQUE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT FALSE,
    INDEX idx_dates (start_date, end_date)
);

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    course_id VARCHAR(20) PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    credits INT NOT NULL CHECK (credits > 0),
    department VARCHAR(100),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_course_code (course_code),
    INDEX idx_department (department)
);

-- Course offerings (instances of courses in specific terms)
CREATE TABLE IF NOT EXISTS course_offerings (
    offering_id INT PRIMARY KEY AUTO_INCREMENT,
    course_id VARCHAR(20) NOT NULL,
    term_id INT NOT NULL,
    faculty_id VARCHAR(20),
    section_number VARCHAR(10),
    capacity INT CHECK (capacity > 0),
    enrolled_count INT DEFAULT 0,
    meeting_pattern VARCHAR(50), -- e.g., "MWF 10:00-11:00"
    location VARCHAR(50),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (term_id) REFERENCES academic_terms(term_id),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id),
    UNIQUE KEY unique_offering (course_id, term_id, section_number),
    INDEX idx_term_course (term_id, course_id)
);

-- Student enrollments
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(20) NOT NULL,
    offering_id INT NOT NULL,
    enrollment_date DATE NOT NULL,
    enrollment_status ENUM('enrolled', 'dropped', 'completed', 'withdrawn') DEFAULT 'enrolled',
    final_grade VARCHAR(2) NULL, -- A, B, C, D, F
    grade_points DECIMAL(3,2) NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (offering_id) REFERENCES course_offerings(offering_id),
    UNIQUE KEY unique_enrollment (student_id, offering_id),
    INDEX idx_student_offering (student_id, offering_id),
    INDEX idx_status (enrollment_status)
);