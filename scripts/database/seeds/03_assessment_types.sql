-- Insert assessment types
INSERT INTO assessment_types (type_name, weight_percentage) 
VALUES
('Quiz', 20.00),
('Assignment', 30.00),
('Midterm Exam', 20.00),
('Final Exam', 25.00),
('Participation', 5.00)
ON DUPLICATE KEY UPDATE type_name = VALUES(type_name);

-- Insert alert types
INSERT INTO alert_types (type_name, severity, description) 
VALUES
('Low Attendance', 'warning', 'Attendance rate below 70%'),
('Missing Assignments', 'warning', 'More than 2 assignments missing'),
('Failing Grade Risk', 'critical', 'Predicted grade is F'),
('Low Engagement', 'info', 'LMS activity below average'),
('Improvement Needed', 'warning', 'Grade declining over time')
ON DUPLICATE KEY UPDATE type_name = VALUES(type_name);

-- Insert system configuration
INSERT INTO system_config (config_key, config_value, description) 
VALUES
('attendance_threshold', '70', 'Minimum attendance percentage'),
('prediction_frequency', 'daily', 'How often to run predictions'),
('alert_email_enabled', 'true', 'Send email alerts'),
('model_version', 'v1.0', 'Current active model version')
ON DUPLICATE KEY UPDATE config_key = VALUES(config_key);