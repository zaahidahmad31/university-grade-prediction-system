// API Client
const API_URL = 'http://localhost:5000/api';

const apiClient = {
    // Get request
    async get(endpoint) {
        try {
            const headers = this._getHeaders();
            const response = await axios.get(`${API_URL}/${endpoint}`, { headers });
            return response.data;
        } catch (error) {
            if (error.response && error.response.status === 401) {
                // Token expired, try to refresh
                await this._handleTokenExpiration();
                // Retry request with new token
                const headers = this._getHeaders();
                const response = await axios.get(`${API_URL}/${endpoint}`, { headers });
                return response.data;
            }
            console.error('API Error:', error);
            throw error;
        }
    },
    
    // Post request
    async post(endpoint, data) {
        try {
            const headers = this._getHeaders();
            const response = await axios.post(`${API_URL}/${endpoint}`, data, { headers });
            return response.data;
        } catch (error) {
            if (error.response && error.response.status === 401) {
                // Token expired, try to refresh
                await this._handleTokenExpiration();
                // Retry request with new token
                const headers = this._getHeaders();
                const response = await axios.post(`${API_URL}/${endpoint}`, data, { headers });
                return response.data;
            }
            console.error('API Error:', error);
            throw error;
        }
    },
    
    // Put request
    async put(endpoint, data) {
        try {
            const headers = this._getHeaders();
            const response = await axios.put(`${API_URL}/${endpoint}`, data, { headers });
            return response.data;
        } catch (error) {
            if (error.response && error.response.status === 401) {
                // Token expired, try to refresh
                await this._handleTokenExpiration();
                // Retry request with new token
                const headers = this._getHeaders();
                const response = await axios.put(`${API_URL}/${endpoint}`, data, { headers });
                return response.data;
            }
            console.error('API Error:', error);
            throw error;
        }
    },
    
    // Delete request
    async delete(endpoint) {
        try {
            const headers = this._getHeaders();
            const response = await axios.delete(`${API_URL}/${endpoint}`, { headers });
            return response.data;
        } catch (error) {
            if (error.response && error.response.status === 401) {
                // Token expired, try to refresh
                await this._handleTokenExpiration();
                // Retry request with new token
                const headers = this._getHeaders();
                const response = await axios.delete(`${API_URL}/${endpoint}`, { headers });
                return response.data;
            }
            console.error('API Error:', error);
            throw error;
        }
    },
    
    // Get headers with authorization token
    _getHeaders() {
        const token = localStorage.getItem('access_token');
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    },
    
    // Handle token expiration
    async _handleTokenExpiration() {
        try {
            // Try to refresh token
            await authApi.refreshToken();
        } catch (error) {
            // If refresh fails, logout
            authApi.logout();
            throw new Error('Session expired. Please log in again.');
        }
    },

    // Add this method to your apiClient:
    async postFormData(endpoint, formData) {
        const token = authApi.getToken();
        if (!token) {
            throw new Error('No authentication token');
        }
        
        try {
            const response = await axios.post(`${this.baseURL}/${endpoint}`, formData, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });
            return response.data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
};

window.apiClient = apiClient;


const academicApi = {
    async getTerms() {
        try {
            const response = await apiClient.get('admin/terms');
            return response;
        } catch (error) {
            console.error('Error fetching terms:', error);
            throw error;
        }
    },
    
    async createTerm(termData) {
        try {
            const response = await apiClient.post('admin/terms', termData);
            return response;
        } catch (error) {
            console.error('Error creating term:', error);
            throw error;
        }
    }
};

// Faculty endpoints
const facultyApi = {
    async getList() {
        try {
            const response = await apiClient.get('admin/faculty/list');
            return response;
        } catch (error) {
            console.error('Error fetching faculty list:', error);
            throw error;
        }
    }
};

// Make sure these are available globally or export them
window.academicApi = academicApi;
window.facultyApi = facultyApi;
