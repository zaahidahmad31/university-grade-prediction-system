// Admin Predictions API
const adminPredictionsApi = {
    // Get predictions summary
    async getPredictionsSummary() {
        try {
            const response = await apiClient.get('admin/predictions/summary');
            return response;
        } catch (error) {
            console.error('Error fetching predictions summary:', error);
            throw error;
        }
    },

    // Get predictions list with filters
    async getPredictions(params = {}) {
        try {
            const queryParams = new URLSearchParams();
            
            // Add parameters
            if (params.page) queryParams.append('page', params.page);
            if (params.per_page) queryParams.append('per_page', params.per_page);
            if (params.risk_level) queryParams.append('risk_level', params.risk_level);
            if (params.course_id) queryParams.append('course_id', params.course_id);
            if (params.grade) queryParams.append('grade', params.grade);
            if (params.search) queryParams.append('search', params.search);
            if (params.date_from) queryParams.append('date_from', params.date_from);
            if (params.date_to) queryParams.append('date_to', params.date_to);
            
            const url = `admin/predictions${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
            const response = await apiClient.get(url);
            return response;
        } catch (error) {
            console.error('Error fetching predictions:', error);
            throw error;
        }
    },

    // Get prediction details
    async getPredictionDetails(predictionId) {
        try {
            const response = await apiClient.get(`admin/predictions/${predictionId}`);
            return response;
        } catch (error) {
            console.error('Error fetching prediction details:', error);
            throw error;
        }
    },

    // Get course predictions
    async getCoursePredictions(courseId) {
        try {
            const response = await apiClient.get(`admin/predictions/course/${courseId}`);
            return response;
        } catch (error) {
            console.error('Error fetching course predictions:', error);
            throw error;
        }
    },

    // Get model performance
    async getModelPerformance() {
        try {
            const response = await apiClient.get('admin/predictions/model/performance');
            return response;
        } catch (error) {
            console.error('Error fetching model performance:', error);
            throw error;
        }
    },

    // Get prediction trends
    async getPredictionTrends(days = 30) {
        try {
            const response = await apiClient.get(`admin/predictions/trends?days=${days}`);
            return response;
        } catch (error) {
            console.error('Error fetching prediction trends:', error);
            throw error;
        }
    },

    // Export predictions
    exportPredictions(params = {}) {
        const queryParams = new URLSearchParams();
        
        if (params.risk_level) queryParams.append('risk_level', params.risk_level);
        if (params.course_id) queryParams.append('course_id', params.course_id);
        if (params.date_from) queryParams.append('date_from', params.date_from);
        if (params.date_to) queryParams.append('date_to', params.date_to);
        
        const url = `/api/admin/predictions/export${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
        
        // Get auth token
        const token = localStorage.getItem('access_token');
        
        // Create a hidden link and click it
        const link = document.createElement('a');
        link.href = `${window.location.origin}${url}`;
        link.download = `predictions_${new Date().toISOString().split('T')[0]}.csv`;
        
        // Add auth header using fetch
        fetch(link.href, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = link.download;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Error exporting predictions:', error);
            alert('Failed to export predictions');
        });
    }
};