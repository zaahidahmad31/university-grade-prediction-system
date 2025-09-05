// Mock data for development
const mockData = {
    // Student dashboard mock data
    courses: [
        {
            course_id: 'CS101',
            course_code: 'CS101',
            course_name: 'Introduction to Computer Science',
            instructor: 'John Smith',
            section: 'A'
        },
        {
            course_id: 'CS201',
            course_code: 'CS201',
            course_name: 'Data Structures and Algorithms',
            instructor: 'Jane Doe',
            section: 'A'
        },
        {
            course_id: 'DS101',
            course_code: 'DS101',
            course_name: 'Introduction to Data Science',
            instructor: 'John Smith',
            section: 'A'
        }
    ],
    predictions: [
        {
            course_id: 'CS101',
            course_name: 'Introduction to Computer Science',
            predicted_grade: 'A',
            confidence_score: 0.85
        },
        {
            course_id: 'CS201',
            course_name: 'Data Structures and Algorithms',
            predicted_grade: 'B',
            confidence_score: 0.75
        },
        {
            course_id: 'DS101',
            course_name: 'Introduction to Data Science',
            predicted_grade: 'C',
            confidence_score: 0.65
        }
    ],
    
    // Faculty dashboard mock data
    facultyCourses: [
        {
            course_id: 'CS101',
            course_code: 'CS101',
            course_name: 'Introduction to Computer Science',
            section: 'A',
            student_count: 28
        },
        {
            course_id: 'CS201',
            course_code: 'CS201',
            course_name: 'Data Structures and Algorithms',
            section: 'A',
            student_count: 24
        },
        {
            course_id: 'CS301',
            course_code: 'CS301',
            course_name: 'Algorithms and Complexity',
            section: 'B',
            student_count: 18
        }
    ],
    facultyAssessments: [
        {
            assessment_id: 1,
            title: 'Midterm Exam',
            course_id: 'CS101',
            course_name: 'Introduction to Computer Science',
            due_date: '2025-07-15T00:00:00',
            submission_count: 25,
            total_students: 28
        },
        {
            assessment_id: 2,
            title: 'Assignment 3: Sorting Algorithms',
            course_id: 'CS201',
            course_name: 'Data Structures and Algorithms',
            due_date: '2025-07-10T00:00:00',
            submission_count: 20,
            total_students: 24
        },
        {
            assessment_id: 3,
            title: 'Quiz 2: Graph Algorithms',
            course_id: 'CS301',
            course_name: 'Algorithms and Complexity',
            due_date: '2025-07-08T00:00:00',
            submission_count: 15,
            total_students: 18
        }
    ],
    atRiskStudents: [
        {
            student_id: 'STU00001',
            name: 'Alice Johnson',
            course_id: 'CS101',
            course_name: 'Introduction to Computer Science',
            predicted_grade: 'D',
            risk_level: 'medium',
            risk_factors: ['Low attendance (65%)', 'Missing assignments (2)']
        },
        {
            student_id: 'STU00012',
            name: 'Bob Williams',
            course_id: 'CS201',
            course_name: 'Data Structures and Algorithms',
            predicted_grade: 'F',
            risk_level: 'high',
            risk_factors: ['Low attendance (40%)', 'Missing assignments (3)', 'Failed quiz (2)']
        },
        {
            student_id: 'STU00023',
            name: 'Charlie Brown',
            course_id: 'CS301',
            course_name: 'Algorithms and Complexity',
            predicted_grade: 'C',
            risk_level: 'low',
            risk_factors: ['Low engagement in class', 'Declining performance']
        },
        {
            student_id: 'STU00008',
            name: 'David Miller',
            course_id: 'CS101',
            course_name: 'Introduction to Computer Science',
            predicted_grade: 'F',
            risk_level: 'high',
            risk_factors: ['Low attendance (30%)', 'No assignments submitted', 'No logins to LMS']
        }
    ]
};