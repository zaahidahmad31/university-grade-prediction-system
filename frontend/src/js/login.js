document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    if (authApi.isLoggedIn()) {
        // Redirect to appropriate dashboard
        const userType = authApi.getUserRole();
        redirectToDashboard(userType);
        return;
    }
    
    // Get form elements
    const loginForm = document.getElementById('loginForm');
    const loginError = document.getElementById('loginError');
    
    // Handle form submission
    loginForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        // Hide any previous errors
        loginError.classList.add('hidden');
        
        // Get form values
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        // Disable submit button
        const submitButton = event.target.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Logging in...';
        
        try {
            // Login user
            const response = await authApi.login(username, password);
            
            // Get user type
            const userType = authApi.getUserRole();
            
            // Redirect to appropriate dashboard
            redirectToDashboard(userType);
            
        } catch (error) {
            // Show error message
            const errorMessage = error.response?.data?.message || 'Invalid username or password';
            showError(errorMessage);
            
            // Re-enable submit button
            submitButton.disabled = false;
            submitButton.textContent = 'Login';
        }
    });
    
    // Show error message
    function showError(message) {
        loginError.textContent = message;
        loginError.classList.remove('hidden');
    }
    
    // Redirect to dashboard based on user type
    function redirectToDashboard(userType) {
        if (userType === 'student') {
            window.location.href = 'student/dashboard.html';
        } else if (userType === 'faculty') {
            window.location.href = 'faculty/dashboard.html';
        } else if (userType === 'admin') {
            window.location.href = 'admin/dashboard.html';
        } else {
            window.location.href = 'index.html';
        }
    }
});