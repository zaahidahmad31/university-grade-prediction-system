-- System configuration
CREATE TABLE IF NOT EXISTS system_config (
    config_id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(50) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Audit log
CREATE TABLE IF NOT EXISTS audit_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50),
    record_id INT NULL,
    old_values JSON NULL,
    new_values JSON NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_created (created_at),
    INDEX idx_user (user_id),
    INDEX idx_action (action)
);

-- Model versions
CREATE TABLE IF NOT EXISTS model_versions (
    version_id INT PRIMARY KEY AUTO_INCREMENT,
    version_name VARCHAR(50) UNIQUE NOT NULL,
    model_file_path VARCHAR(255),
    accuracy DECIMAL(5,2),
    precision_score DECIMAL(5,2),
    recall_score DECIMAL(5,2),
    f1_score DECIMAL(5,2),
    training_date DATE,
    is_active BOOLEAN DEFAULT FALSE,
    feature_list JSON,
    hyperparameters JSON,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Views for common queries
CREATE OR REPLACE VIEW v_current_enrollments AS
SELECT 
    e.enrollment_id,
    e.student_id,
    s.first_name,
    s.last_name,
    c.course_code,
    c.course_name,
    co.section_number,
    f.first_name AS instructor_first,
    f.last_name AS instructor_last,
    at.term_name
FROM enrollments e
JOIN students s ON e.student_id = s.student_id
JOIN course_offerings co ON e.offering_id = co.offering_id
JOIN courses c ON co.course_id = c.course_id
LEFT JOIN faculty f ON co.faculty_id = f.faculty_id
JOIN academic_terms at ON co.term_id = at.term_id
WHERE e.enrollment_status = 'enrolled'
AND at.is_current = TRUE;

-- At-risk students view
CREATE OR REPLACE VIEW v_at_risk_students AS
SELECT 
    p.enrollment_id,
    e.student_id,
    s.first_name,
    s.last_name,
    c.course_code,
    c.course_name,
    p.predicted_grade,
    p.confidence_score,
    p.risk_level,
    p.prediction_date
FROM predictions p
JOIN enrollments e ON p.enrollment_id = e.enrollment_id
JOIN students s ON e.student_id = s.student_id
JOIN course_offerings co ON e.offering_id = co.offering_id
JOIN courses c ON co.course_id = c.course_id
WHERE p.risk_level IN ('medium', 'high')
AND p.prediction_id IN (
    SELECT MAX(prediction_id)
    FROM predictions
    GROUP BY enrollment_id
);