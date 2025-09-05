-- Admin user (password: admin123)
INSERT INTO users (username, email, password_hash, user_type, is_active)
VALUES
('admin', 'admin@university.edu', '$2b$12$tGp9pzhWMQyQb.fbwgz22.QKT0d9P0hgpiVQSHyKQ7HrQcJVwS5m6', 'admin', 1)
ON DUPLICATE KEY UPDATE username = 'admin';

-- Sample faculty users (password: faculty123)
INSERT INTO users (username, email, password_hash, user_type, is_active)
VALUES
('faculty1', 'faculty1@university.edu', '$2b$12$5KP/JZ0zzYL8BEP9rt0zfeCVOZXOmraPLziYUcGBRuLCIZ5d3UuIe', 'faculty', 1),
('faculty2', 'faculty2@university.edu', '$2b$12$5KP/JZ0zzYL8BEP9rt0zfeCVOZXOmraPLziYUcGBRuLCIZ5d3UuIe', 'faculty', 1)
ON DUPLICATE KEY UPDATE username = VALUES(username);

-- Sample student users (password: student123)
INSERT INTO users (username, email, password_hash, user_type, is_active)
VALUES
('student1', 'student1@university.edu', '$2b$12$C3OWXS2Mgzw5.IRzpQPZIOmqwaF/L0aCtKLbGQwx8WPWdQp7yRqhy', 'student', 1),
('student2', 'student2@university.edu', '$2b$12$C3OWXS2Mgzw5.IRzpQPZIOmqwaF/L0aCtKLbGQwx8WPWdQp7yRqhy', 'student', 1),
('student3', 'student3@university.edu', '$2b$12$C3OWXS2Mgzw5.IRzpQPZIOmqwaF/L0aCtKLbGQwx8WPWdQp7yRqhy', 'student', 1)
ON DUPLICATE KEY UPDATE username = VALUES(username);

-- Add faculty records
INSERT INTO faculty (faculty_id, user_id, first_name, last_name, department, position)
VALUES
('FAC00001', (SELECT user_id FROM users WHERE username = 'faculty1'), 'John', 'Smith', 'Computer Science', 'Associate Professor'),
('FAC00002', (SELECT user_id FROM users WHERE username = 'faculty2'), 'Jane', 'Doe', 'Data Science', 'Assistant Professor')
ON DUPLICATE KEY UPDATE faculty_id = VALUES(faculty_id);

-- Add student records
INSERT INTO students (student_id, user_id, first_name, last_name, date_of_birth, gender, program_code, year_of_study, enrollment_date)
VALUES
('STU00001', (SELECT user_id FROM users WHERE username = 'student1'), 'Alice', 'Johnson', '2000-05-15', 'F', 'CS', 2, '2022-09-01'),
('STU00002', (SELECT user_id FROM users WHERE username = 'student2'), 'Bob', 'Williams', '2001-02-28', 'M', 'DS', 1, '2023-09-01'),
('STU00003', (SELECT user_id FROM users WHERE username = 'student3'), 'Charlie', 'Brown', '1999-11-10', 'M', 'CS', 3, '2021-09-01')
ON DUPLICATE KEY UPDATE student_id = VALUES(student_id);