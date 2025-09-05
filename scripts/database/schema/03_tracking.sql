-- Attendance records
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    enrollment_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('present', 'absent', 'late', 'excused') NOT NULL,
    check_in_time TIME NULL,
    check_out_time TIME NULL,
    duration_minutes INT NULL,
    recorded_by VARCHAR(50), -- 'system' or faculty_id
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id),
    INDEX idx_enrollment_date (enrollment_id, attendance_date),
    INDEX idx_date (attendance_date),
    INDEX idx_status (status)
);

-- LMS sessions
CREATE TABLE IF NOT EXISTS lms_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    enrollment_id INT NOT NULL,
    login_time TIMESTAMP NOT NULL,
    logout_time TIMESTAMP NULL,
    duration_minutes INT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id),
    INDEX idx_enrollment (enrollment_id),
    INDEX idx_login_time (login_time)
);

-- LMS activities (granular tracking)
CREATE TABLE IF NOT EXISTS lms_activities (
    activity_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT NOT NULL,
    enrollment_id INT NOT NULL,
    activity_type ENUM('resource_view', 'forum_post', 'forum_reply', 'assignment_view', 
                       'quiz_attempt', 'video_watch', 'file_download', 'page_view') NOT NULL,
    activity_timestamp TIMESTAMP NOT NULL,
    resource_id VARCHAR(50) NULL,
    resource_name VARCHAR(255) NULL,
    duration_seconds INT NULL,
    details JSON NULL, -- Store additional activity-specific data
    FOREIGN KEY (session_id) REFERENCES lms_sessions(session_id),
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id),
    INDEX idx_enrollment_timestamp (enrollment_id, activity_timestamp),
    INDEX idx_type (activity_type)
);

-- Daily LMS activity summary (for performance)
CREATE TABLE IF NOT EXISTS lms_daily_summary (
    summary_id INT PRIMARY KEY AUTO_INCREMENT,
    enrollment_id INT NOT NULL,
    summary_date DATE NOT NULL,
    total_minutes INT DEFAULT 0,
    login_count INT DEFAULT 0,
    resource_views INT DEFAULT 0,
    forum_posts INT DEFAULT 0,
    forum_replies INT DEFAULT 0,
    files_downloaded INT DEFAULT 0,
    videos_watched INT DEFAULT 0,
    pages_viewed INT DEFAULT 0,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id),
    UNIQUE KEY unique_daily (enrollment_id, summary_date),
    INDEX idx_date (summary_date)
);