// frontend/src/js/api/faculty.js

const facultyApi = {
    // Profile Management
    async getProfile() {
        try {
            const response = await apiClient.get('faculty/profile');
            return response;
        } catch (error) {
            console.error('Error fetching profile:', error);
            throw error;
        }
    },

    async updateProfile(profileData) {
        try {
            const response = await apiClient.put('faculty/profile', profileData);
            return response;
        } catch (error) {
            console.error('Error updating profile:', error);
            throw error;
        }
    },

    // Dashboard
    async getDashboard() {
        try {
            const response = await apiClient.get('faculty/dashboard');
            return response;
        } catch (error) {
            console.error('Error fetching dashboard:', error);
            throw error;
        }
    },

    // Course Management
    async getCourses() {
        try {
            const response = await apiClient.get('faculty/courses');
            return response;
        } catch (error) {
            console.error('Error fetching courses:', error);
            throw error;
        }
    },

    async getCourseStudents(offeringId) {
        try {
            const response = await apiClient.get(`faculty/courses/${offeringId}/students`);
            return response;
        } catch (error) {
            console.error('Error fetching course students:', error);
            throw error;
        }
    },

    // Assessment Management
    async getAssessments(offeringId = null) {
        try {
            let endpoint = 'faculty/assessments';
            if (offeringId) {
                endpoint += `?offering_id=${offeringId}`;
            }
            const response = await apiClient.get(endpoint);
            return response;
        } catch (error) {
            console.error('Error fetching assessments:', error);
            throw error;
        }
    },

    async createAssessment(assessmentData) {
        try {
            const response = await apiClient.post('faculty/assessments', assessmentData);
            return response;
        } catch (error) {
            console.error('Error creating assessment:', error);
            throw error;
        }
    },

    async updateAssessment(assessmentId, assessmentData) {
        try {
            const response = await apiClient.put(`faculty/assessments/${assessmentId}`, assessmentData);
            return response;
        } catch (error) {
            console.error('Error updating assessment:', error);
            throw error;
        }
    },

    async deleteAssessment(assessmentId) {
        try {
            const response = await apiClient.delete(`faculty/assessments/${assessmentId}`);
            return response;
        } catch (error) {
            console.error('Error deleting assessment:', error);
            throw error;
        }
    },

    // Grade Management
    async getAssessmentRoster(assessmentId) {
        try {
            const response = await apiClient.get(`faculty/assessments/${assessmentId}/roster`);
            return response;
        } catch (error) {
            console.error('Error fetching assessment roster:', error);
            throw error;
        }
    },

    async gradeAssessment(gradeData) {
        try {
            const response = await apiClient.post('faculty/assessments/grade', gradeData);
            return response;
        } catch (error) {
            console.error('Error grading assessment:', error);
            throw error;
        }
    },

    async bulkGradeAssessments(grades) {
        try {
            const response = await apiClient.post('faculty/assessments/bulk-grade', { grades });
            return response;
        } catch (error) {
            console.error('Error bulk grading assessments:', error);
            throw error;
        }
    },

    // Attendance Management
    async getAttendance(offeringId, date = null) {
        try {
            let endpoint = `faculty/attendance/${offeringId}`;
            if (date) {
                endpoint += `?date=${date}`;
            }
            const response = await apiClient.get(endpoint);
            return response;
        } catch (error) {
            console.error('Error fetching attendance:', error);
            throw error;
        }
    },

    async markAttendance(attendanceData) {
        try {
            const response = await apiClient.post('faculty/attendance', attendanceData);
            return response;
        } catch (error) {
            console.error('Error marking attendance:', error);
            throw error;
        }
    },

    async bulkMarkAttendance(attendanceRecords) {
        try {
            const response = await apiClient.post('faculty/attendance/bulk', { attendance: attendanceRecords });
            return response;
        } catch (error) {
            console.error('Error bulk marking attendance:', error);
            throw error;
        }
    },

    // Student Management
    async getStudents(filters = {}) {
        try {
            const queryParams = new URLSearchParams(filters).toString();
            const endpoint = queryParams ? `faculty/students?${queryParams}` : 'faculty/students';
            const response = await apiClient.get(endpoint);
            return response;
        } catch (error) {
            console.error('Error fetching students:', error);
            throw error;
        }
    },

    async getStudentDetails(studentId) {
        try {
            const response = await apiClient.get(`faculty/students/${studentId}`);
            return response;
        } catch (error) {
            console.error('Error fetching student details:', error);
            throw error;
        }
    },

    // At-Risk Students
    async getAtRiskStudents() {
        try {
            const response = await apiClient.get('faculty/at-risk-students');
            return response;
        } catch (error) {
            console.error('Error fetching at-risk students:', error);
            throw error;
        }
    }
};