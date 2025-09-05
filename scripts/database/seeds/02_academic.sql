-- Academic terms
INSERT INTO academic_terms (term_name, term_code, start_date, end_date, is_current)
VALUES
('Fall 2023', 'FALL2023', '2023-09-01', '2023-12-15', 0),
('Spring 2024', 'SPRING2024', '2024-01-15', '2024-05-10', 0),
('Fall 2024', 'FALL2024', '2024-09-01', '2024-12-15', 0),
('Spring 2025', 'SPRING2025', '2025-01-15', '2025-05-10', 1)
ON DUPLICATE KEY UPDATE term_code = VALUES(term_code);

-- Courses
INSERT INTO courses (course_id, course_code, course_name, credits, department, description, is_active)
VALUES
('CS101', 'CS101', 'Introduction to Computer Science', 3, 'Computer Science', 'Foundational course covering basic concepts in computer science', 1),
('CS201', 'CS201', 'Data Structures and Algorithms', 4, 'Computer Science', 'Study of common data structures and algorithms', 1),
('DS101', 'DS101', 'Introduction to Data Science', 3, 'Data Science', 'Overview of data science concepts and techniques', 1),
('DS201', 'DS201', 'Machine Learning Fundamentals', 4, 'Data Science', 'Introduction to machine learning algorithms and applications', 1)
ON DUPLICATE KEY UPDATE course_code = VALUES(course_code);

-- Course offerings for the current term
INSERT INTO course_offerings (course_id, term_id, faculty_id, section_number, capacity, enrolled_count, meeting_pattern, location)
VALUES
('CS101', (SELECT term_id FROM academic_terms WHERE is_current = 1), 'FAC00001', 'A', 30, 2, 'MWF 10:00-11:00', 'Room 101'),
('CS201', (SELECT term_id FROM academic_terms WHERE is_current = 1), 'FAC00001', 'A', 25, 1, 'TTh 13:00-14:30', 'Room 102'),
('DS101', (SELECT term_id FROM academic_terms WHERE is_current = 1), 'FAC00002', 'A', 30, 1, 'MWF 13:00-14:00', 'Room 201'),
('DS201', (SELECT term_id FROM academic_terms WHERE is_current = 1), 'FAC00002', 'A', 25, 2, 'TTh 15:00-16:30', 'Room 202')
ON DUPLICATE KEY UPDATE section_number = VALUES(section_number);

-- Enrollments for the current term
INSERT INTO enrollments (student_id, offering_id, enrollment_date, enrollment_status)
VALUES
('STU00001', (SELECT offering_id FROM course_offerings WHERE course_id = 'CS101' AND term_id = (SELECT term_id FROM academic_terms WHERE is_current = 1)), '2025-01-10', 'enrolled'),
('STU00001', (SELECT offering_id FROM course_offerings WHERE course_id = 'CS201' AND term_id = (SELECT term_id FROM academic_terms WHERE is_current = 1)), '2025-01-10', 'enrolled'),
('STU00002', (SELECT offering_id FROM course_offerings WHERE course_id = 'DS101' AND term_id = (SELECT term_id FROM academic_terms WHERE is_current = 1)), '2025-01-12', 'enrolled'),
('STU00003', (SELECT offering_id FROM course_offerings WHERE course_id = 'CS201' AND term_id = (SELECT term_id FROM academic_terms WHERE is_current = 1)), '2025-01-08', 'enrolled'),
('STU00003', (SELECT offering_id FROM course_offerings WHERE course_id = 'DS201' AND term_id = (SELECT term_id FROM academic_terms WHERE is_current = 1)), '2025-01-08', 'enrolled')
ON DUPLICATE KEY UPDATE enrollment_date = VALUES(enrollment_date);