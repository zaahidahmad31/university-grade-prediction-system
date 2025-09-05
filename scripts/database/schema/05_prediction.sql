-- Predictions
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INT PRIMARY KEY AUTO_INCREMENT,
    enrollment_id INT NOT NULL,
    prediction_date DATETIME NOT NULL,
    predicted_grade VARCHAR(2) NOT NULL,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    risk_level ENUM('low', 'medium', 'high') NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    feature_snapshot JSON NULL, -- Store features used for prediction
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id),
    INDEX idx_enrollment_date (enrollment_id, prediction_date),
    INDEX idx_risk_level (risk_level)
);

-- Feature cache (for performance)
CREATE TABLE IF NOT EXISTS feature_cache (
    cache_id INT PRIMARY KEY AUTO_INCREMENT,
    enrollment_id INT NOT NULL,
    feature_date DATE NOT NULL,
    attendance_rate DECIMAL(5,2),
    avg_session_duration DECIMAL(8,2),
    login_frequency DECIMAL(8,2),
    resource_access_rate DECIMAL(5,2),
    assignment_submission_rate DECIMAL(5,2),
    avg_assignment_score DECIMAL(5,2),
    forum_engagement_score DECIMAL(8,2),
    study_consistency_score DECIMAL(5,2),
    last_login_days_ago INT,
    total_study_minutes INT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id),
    UNIQUE KEY unique_cache (enrollment_id, feature_date),
    INDEX idx_date (feature_date)
);