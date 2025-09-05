-- Assessment types
CREATE TABLE IF NOT EXISTS assessment_types (
    type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(50) NOT NULL,
    weight_percentage DECIMAL(5,2) CHECK (weight_percentage >= 0 AND weight_percentage <= 100)
);

-- Assessments
CREATE TABLE IF NOT EXISTS assessments (
    assessment_id INT PRIMARY KEY AUTO_INCREMENT,
    offering_id INT NOT NULL,
    type_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    max_score DECIMAL(6,2) NOT NULL,
    due_date DATETIME NULL,
    weight DECIMAL(5,2) CHECK (weight >= 0 AND weight <= 100),
    description TEXT,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (offering_id) REFERENCES course_offerings(offering_id),
    FOREIGN KEY (type_id) REFERENCES assessment_types(type_id),
    INDEX idx_offering (offering_id),
    INDEX idx_due_date (due_date)
);

-- Student assessment submissions
CREATE TABLE IF NOT EXISTS assessment_submissions (
    submission_id INT PRIMARY KEY AUTO_INCREMENT,
    enrollment_id INT NOT NULL,
    assessment_id INT NOT NULL,
    submission_date DATETIME NOT NULL,
    score DECIMAL(6,2) NULL,
    percentage DECIMAL(5,2) NULL,
    is_late BOOLEAN DEFAULT FALSE,
    late_penalty DECIMAL(5,2) DEFAULT 0,
    graded_date DATETIME NULL,
    graded_by VARCHAR(20) NULL,
    feedback TEXT NULL,
    attempt_number INT DEFAULT 1,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id),
    FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id),
    UNIQUE KEY unique_submission (enrollment_id, assessment_id, attempt_number),
    INDEX idx_enrollment (enrollment_id),
    INDEX idx_assessment (assessment_id)
);