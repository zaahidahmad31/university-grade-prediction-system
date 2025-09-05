document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    const registerForm = document.getElementById('registerForm');
    const userTypeSelect = document.getElementById('userType');
    const studentFields = document.getElementById('studentFields');
    const facultyFields = document.getElementById('facultyFields');
    const registerError = document.getElementById('registerError');
    
    // Show/hide fields based on user type
    userTypeSelect.addEventListener('change', function() {
        if (this.value === 'student') {
            studentFields.classList.remove('hidden');
            facultyFields.classList.add('hidden');
        } else if (this.value === 'faculty') {
            studentFields.classList.add('hidden');
            facultyFields.classList.remove('hidden');
        }
    });
    
    // Handle form submission
    registerForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        // Get form values
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const userType = userTypeSelect.value;
        
        // Validate passwords match
        if (password !== confirmPassword) {
            showError('Passwords do not match');
            return;
        }
        
        // Create user data object
        let userData = {
            username,
            email,
            password,
            user_type: userType
        };
        
        // Add user type specific fields
        if (userType === 'student') {
            userData.first_name = document.getElementById('firstName').value;
            userData.last_name = document.getElementById('lastName').value;
            userData.program_code = document.getElementById('programCode').value;
            userData.year_of_study = document.getElementById('yearOfStudy').value;
        } else if (userType === 'faculty') {
            userData.first_name = document.getElementById('facultyFirstName').value;
            userData.last_name = document.getElementById('facultyLastName').value;
            userData.department = document.getElementById('department').value;
            userData.position = document.getElementById('position').value;
        }
        
        try {
            // Register user
            const response = await authApi.register(userData);
            
            // Redirect to dashboard
            if (userType === 'student') {
                window.location.href = '/student/dashboard.html';
            } else if (userType === 'faculty') {
                window.location.href = '/faculty/dashboard.html';
            }
        } catch (error) {
            showError(error.response?.data?.message || 'Registration failed');
        }
    });
    
    // Show error message
    function showError(message) {
        registerError.textContent = message;
        registerError.classList.remove('hidden');
    }
});