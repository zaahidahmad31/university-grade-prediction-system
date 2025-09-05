-- Alert types
CREATE TABLE IF NOT EXISTS alert_types (
    type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(50) NOT NULL,
    severity ENUM('info', 'warning', 'critical') NOT NULL,
    description TEXT
);

-- Alerts
CREATE TABLE IF NOT EXISTS alerts (
    alert_id INT PRIMARY KEY AUTO_INCREMENT,
    enrollment_id INT NOT NULL,
    type_id INT NOT NULL,
    triggered_date DATETIME NOT NULL,
    alert_message TEXT NOT NULL,
    severity ENUM('info', 'warning', 'critical') NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    read_date DATETIME NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_date DATETIME NULL,
    resolved_by VARCHAR(20) NULL,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id),
    FOREIGN KEY (type_id) REFERENCES alert_types(type_id),
    INDEX idx_enrollment (enrollment_id),
    INDEX idx_unread (is_read, enrollment_id),
    INDEX idx_severity (severity)
);

-- Interventions
CREATE TABLE IF NOT EXISTS interventions (
    intervention_id INT PRIMARY KEY AUTO_INCREMENT,
    enrollment_id INT NOT NULL,
    alert_id INT NULL,
    faculty_id VARCHAR(20) NOT NULL,
    intervention_date DATETIME NOT NULL,
    intervention_type VARCHAR(50),
    description TEXT,
    outcome TEXT,
    follow_up_date DATE NULL,
    is_successful BOOLEAN NULL,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id),
    FOREIGN KEY (alert_id) REFERENCES alerts(alert_id),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id),
    INDEX idx_enrollment (enrollment_id)
);