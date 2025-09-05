const studentApi = {
    // Profile Management
    async getProfile() {
        try {
            const response = await apiClient.get('student/profile');
            return response;
        } catch (error) {
            console.error('Error fetching profile:', error);
            throw error;
        }
    },

    async updateProfile(profileData) {
        try {
            const response = await apiClient.put('student/profile', profileData);
            return response;
        } catch (error) {
            console.error('Error updating profile:', error);
            throw error;
        }
    },

    // Course Management
    async getEnrolledCourses(termId = null) {
        try {
            const params = termId ? `?term_id=${termId}` : '';
            const response = await apiClient.get(`student/courses${params}`);
            return response;
        } catch (error) {
            console.error('Error fetching enrolled courses:', error);
            throw error;
        }
    },

    async getAvailableCourses(termId = null) {
        try {
            const params = termId ? `?term_id=${termId}` : '';
            const response = await apiClient.get(`student/courses/available${params}`);
            return response;
        } catch (error) {
            console.error('Error fetching available courses:', error);
            throw error;
        }
    },

    async enrollInCourse(offeringId) {
        try {
            const response = await apiClient.post('student/courses/enroll', {
                offering_id: offeringId
            });
            return response;
        } catch (error) {
            console.error('Error enrolling in course:', error);
            throw error;
        }
    },

    async dropCourse(offeringId) {
        try {
            const response = await apiClient.post('student/courses/drop', {
                offering_id: offeringId
            });
            return response;
        } catch (error) {
            console.error('Error dropping course:', error);
            throw error;
        }
    },

    // Dashboard
    async getDashboard() {
        try {
            const response = await apiClient.get('student/dashboard');
            return response;
        } catch (error) {
            console.error('Error fetching dashboard:', error);
            throw error;
        }
    },

    async getCourses(termId = null) {
        try {
            let endpoint = 'student/courses';
            if (termId) {
                endpoint += `?term_id=${termId}`;
            }
            const response = await apiClient.get(endpoint);
            return response;
        } catch (error) {
            console.error('Error fetching courses:', error);
            throw error;
        }
    },
    
    // Get attendance data
    async getAttendance(courseId = null) {
        try {
            let endpoint = 'student/attendance';
            if (courseId) {
                endpoint += `?course_id=${courseId}`;
            }
            const response = await apiClient.get(endpoint);
            return response;
        } catch (error) {
            console.error('Error fetching attendance:', error);
            throw error;
        }
    },
    
    // Get assessments
    async getAssessments(courseId = null) {
        try {
            let endpoint = 'student/assessments';
            if (courseId) {
                endpoint += `?course_id=${courseId}`;
            }
            const response = await apiClient.get(endpoint);
            return response;
        } catch (error) {
            console.error('Error fetching assessments:', error);
            throw error;
        }
    },
    
    // Get grade predictions
    async getPredictions() {
        try {
            const response = await apiClient.get('student/predictions');
            return response;
        } catch (error) {
            console.error('Error fetching predictions:', error);
            throw error;
        }
    }

};