// Authentication API
const authApi = {
    // Register
    async register(userData) {
        try {
            const response = await apiClient.post('auth/register', userData);
            
            // Store tokens and user info in localStorage
            if (response.status === 'success' && response.data) {
                localStorage.setItem('access_token', response.data.access_token);
                localStorage.setItem('refresh_token', response.data.refresh_token);
                localStorage.setItem('user', JSON.stringify(response.data.user));
            }
            
            return response;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    },
    
    // Login
    async login(username, password) {
        try {
            const response = await apiClient.post('auth/login', { username, password });
            
            // Store tokens and user info in localStorage
            if (response.status === 'success' && response.data) {
                localStorage.setItem('access_token', response.data.access_token);
                localStorage.setItem('refresh_token', response.data.refresh_token);
                localStorage.setItem('user', JSON.stringify(response.data.user));
            }
            
            return response;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },
    
    // Refresh token
    async refreshToken() {
        try {
            const refreshToken = localStorage.getItem('refresh_token');
            
            if (!refreshToken) {
                throw new Error('No refresh token available');
            }
            
            const response = await apiClient.post('auth/refresh', { refresh_token: refreshToken });
            
            // Update access token in localStorage
            if (response.status === 'success' && response.data) {
                localStorage.setItem('access_token', response.data.access_token);
            }
            
            return response;
        } catch (error) {
            console.error('Token refresh error:', error);
            this.logout();
            throw error;
        }
    },
    
    // Get user profile
    async getProfile() {
        try {
            const response = await apiClient.get('auth/me');
            
            // Update user info in localStorage
            if (response.status === 'success' && response.data) {
                localStorage.setItem('user', JSON.stringify(response.data.user));
            }
            
            return response;
        } catch (error) {
            console.error('Get profile error:', error);
            throw error;
        }
    },
    
    // Logout
    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        
        // Redirect to login page
        window.location.href = '/';
    },
    
    // Check if user is logged in
    isLoggedIn() {
        return !!localStorage.getItem('access_token');
    },
    
    // Get current user
    getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },
    
    // Get user role
    getUserRole() {
        const user = this.getCurrentUser();
        return user ? user.user_type : null;
    },
    
    // Check if user has role
    hasRole(role) {
        const userRole = this.getUserRole();
        return userRole === role;
    }
};