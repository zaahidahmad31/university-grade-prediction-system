document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    if (authApi.isLoggedIn()) {
        // Redirect to appropriate dashboard
        const userType = authApi.getUserRole();
        if (userType === 'student') {
            window.location.href = 'student/dashboard.html';
        } else if (userType === 'faculty') {
            window.location.href = 'faculty/dashboard.html';
        } else if (userType === 'admin') {
            window.location.href = 'admin/dashboard.html';
        }
        return;
    }
    
    // Check API status
    checkApiStatus();
});

async function checkApiStatus() {
    const statusElement = document.getElementById('apiStatus');
    if (!statusElement) return;
    
    try {
        const response = await apiClient.get('common/health');
        if (response.status === 'success') {
            statusElement.innerHTML = `
                <div class="flex items-center text-green-600">
                    <i class="fas fa-check-circle mr-2"></i>
                    <span>System is operational</span>
                </div>
            `;
        }
    } catch (error) {
        statusElement.innerHTML = `
            <div class="flex items-center text-red-600">
                <i class="fas fa-times-circle mr-2"></i>
                <span>System is currently offline</span>
            </div>
        `;
    }
}