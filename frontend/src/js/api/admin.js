// Admin API Client
const adminApi = {
    // Get dashboard statistics
    async getStatistics() {
        try {
            const response = await apiClient.get('admin/statistics');
            return response;
        } catch (error) {
            console.error('Error fetching statistics:', error);
            throw error;
        }
    },

    // Get recent activities
    async getRecentActivities() {
        try {
            const response = await apiClient.get('admin/activities/recent');
            return response;
        } catch (error) {
            console.error('Error fetching activities:', error);
            throw error;
        }
    },

    // User management
    async getUsers(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const response = await apiClient.get(`admin/users${queryString ? '?' + queryString : ''}`);
            return response;
        } catch (error) {
            console.error('Error fetching users:', error);
            throw error;
        }
    },

    async getUser(userId) {
        try {
            const response = await apiClient.get(`admin/users/${userId}`);
            return response;
        } catch (error) {
            console.error('Error fetching user:', error);
            throw error;
        }
    },

    async createUser(userData) {
        try {
            const response = await apiClient.post('admin/users', userData);
            return response;
        } catch (error) {
            console.error('Error creating user:', error);
            throw error;
        }
    },

    async updateUser(userId, userData) {
        try {
            const response = await apiClient.put(`admin/users/${userId}`, userData);
            return response;
        } catch (error) {
            console.error('Error updating user:', error);
            throw error;
        }
    },

    async updateUserStatus(userId, isActive) {
        try {
            const response = await apiClient.put(`admin/users/${userId}/status`, { is_active: isActive });
            return response;
        } catch (error) {
            console.error('Error updating user status:', error);
            throw error;
        }
    },

    // Course management
    async getCourses(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const response = await apiClient.get(`admin/courses${queryString ? '?' + queryString : ''}`);
            return response;
        } catch (error) {
            console.error('Error fetching courses:', error);
            throw error;
        }
    },

    async createCourse(courseData) {
        try {
            const response = await apiClient.post('admin/courses', courseData);
            return response;
        } catch (error) {
            console.error('Error creating course:', error);
            throw error;
        }
    },

    async updateCourse(courseId, courseData) {
        try {
            const response = await apiClient.put(`admin/courses/${courseId}`, courseData);
            return response;
        } catch (error) {
            console.error('Error updating course:', error);
            throw error;
        }
    },

    // System configuration
    async getSystemConfig() {
        try {
            const response = await apiClient.get('admin/system/config');
            return response;
        } catch (error) {
            console.error('Error fetching system config:', error);
            throw error;
        }
    },

    async updateSystemConfig(config) {
        try {
            const response = await apiClient.put('admin/system/config', config);
            return response;
        } catch (error) {
            console.error('Error updating system config:', error);
            throw error;
        }
    },

    // Reports
    async generateReport(reportType, params = {}) {
        try {
            const response = await apiClient.post('admin/reports/generate', {
                report_type: reportType,
                parameters: params
            });
            return response;
        } catch (error) {
            console.error('Error generating report:', error);
            throw error;
        }
    },

    // Alerts overview
    async getSystemAlerts(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const response = await apiClient.get(`admin/alerts${queryString ? '?' + queryString : ''}`);
            return response;
        } catch (error) {
            console.error('Error fetching system alerts:', error);
            throw error;
        }
    },

    // Predictions overview
    async getPredictionsOverview() {
        try {
            const response = await apiClient.get('admin/predictions/overview');
            return response;
        } catch (error) {
            console.error('Error fetching predictions overview:', error);
            throw error;
        }
    },

    // Model management
    async getModelInfo() {
        try {
            const response = await apiClient.get('admin/model/info');
            return response;
        } catch (error) {
            console.error('Error fetching model info:', error);
            throw error;
        }
    },

    async retrainModel() {
        try {
            const response = await apiClient.post('admin/model/retrain');
            return response;
        } catch (error) {
            console.error('Error retraining model:', error);
            throw error;
        }
    },

    async getSystemAlerts(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const response = await apiClient.get(`admin/alerts${queryString ? '?' + queryString : ''}`);
            return response;
        } catch (error) {
            console.error('Error fetching system alerts:', error);
            throw error;
        }
    },

    async getSystemAlertStats() {
        try {
            const response = await apiClient.get('admin/alerts/stats');
            return response;
        } catch (error) {
            console.error('Error fetching alert statistics:', error);
            throw error;
        }
    },

    async resolveAlert(alertId) {
        try {
            const response = await apiClient.put(`admin/alerts/${alertId}/resolve`);
            return response;
        } catch (error) {
            console.error('Error resolving alert:', error);
            throw error;
        }
    },

    async bulkResolveAlerts(alertIds) {
        try {
            const response = await apiClient.post('admin/alerts/bulk-resolve', { alert_ids: alertIds });
            return response;
        } catch (error) {
            console.error('Error bulk resolving alerts:', error);
            throw error;
        }
    },
    async getCourseOfferings(courseId) {
    try {
        const response = await apiClient.get(`admin/courses/${courseId}/offerings`);
        return response;
    } catch (error) {
        console.error('Error fetching course offerings:', error);
        throw error;
    }
},

// Also add these offering-related functions:
async createCourseOffering(courseId, offeringData) {
    try {
        const response = await apiClient.post(`admin/courses/${courseId}/offerings`, offeringData);
        return response;
    } catch (error) {
        console.error('Error creating course offering:', error);
        throw error;
    }
},

async updateCourseOffering(courseId, offeringId, offeringData) {
    try {
        const response = await apiClient.put(`admin/courses/${courseId}/offerings/${offeringId}`, offeringData);
        return response;
    } catch (error) {
        console.error('Error updating course offering:', error);
        throw error;
    }
},

async deleteCourseOffering(courseId, offeringId) {
    try {
        const response = await apiClient.delete(`admin/courses/${courseId}/offerings/${offeringId}`);
        return response;
    } catch (error) {
        console.error('Error deleting course offering:', error);
        throw error;
    }
}
};

// Make it available globally
window.adminApi = adminApi;