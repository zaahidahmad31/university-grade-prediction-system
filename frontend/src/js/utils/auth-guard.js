(function() {
    'use strict';
    
    // Configuration
    const AUTH_CONFIG = {
        loginPage: '../login.html',  // Updated to work from subdirectories
        indexPage: '../index.html',
        dashboards: {
            student: '../student/dashboard.html',
            faculty: '../faculty/dashboard.html',
            admin: '../admin/dashboard.html'
        }
    };
    
    // Main auth guard function
    function initAuthGuard() {
        // Check if user is logged in
        if (!authApi.isLoggedIn()) {
            redirectToLogin();
            return false;
        }
        
        // Get current page info
        const currentPath = window.location.pathname;
        const userRole = authApi.getUserRole();
        
        // Check role-based access
        if (!checkRoleAccess(currentPath, userRole)) {
            redirectToDashboard(userRole);
            return false;
        }
        
        // User is authorized
        console.log('User authorized:', userRole);
        setupLogoutHandlers();
        updateUserDisplay();
        
        return true;
    }
    
    // Check if user has access to current path
    function checkRoleAccess(path, userRole) {
        // Define role access patterns
        const rolePatterns = {
            student: /\/student\//i,
            faculty: /\/faculty\//i,
            admin: /\/admin\//i
        };
        
        // Check each role pattern
        for (const [role, pattern] of Object.entries(rolePatterns)) {
            if (pattern.test(path) && userRole !== role) {
                console.warn(`Access denied: ${userRole} trying to access ${role} area`);
                return false;
            }
        }
        
        return true;
    }
    
    // Redirect to login page
    function redirectToLogin() {
        console.log('Redirecting to login...');
        // Store the intended destination
        sessionStorage.setItem('redirectUrl', window.location.href);
        window.location.href = AUTH_CONFIG.loginPage;
    }
    
    // Redirect to appropriate dashboard
    function redirectToDashboard(userRole) {
        const dashboardUrl = AUTH_CONFIG.dashboards[userRole];
        
        if (dashboardUrl) {
            console.log(`Redirecting ${userRole} to dashboard...`);
            window.location.href = dashboardUrl;
        } else {
            console.error('Unknown user role:', userRole);
            window.location.href = AUTH_CONFIG.indexPage;
        }
    }
    
    // Setup logout handlers for all logout buttons
    function setupLogoutHandlers() {
        // Handle multiple logout buttons
        const logoutButtons = document.querySelectorAll('#logoutBtn, .logout-btn');
        
        logoutButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                handleLogout();
            });
        });
    }
    
    // Handle logout
    function handleLogout() {
        authApi.logout();
        window.location.href = AUTH_CONFIG.loginPage;
    }
    
    // Update user display elements
    function updateUserDisplay() {
        const user = authApi.getCurrentUser();
        if (!user) return;
        
        // Update all username displays
        const usernameElements = document.querySelectorAll('#username, .username-display');
        usernameElements.forEach(el => {
            el.textContent = user.username || 'User';
        });
        
        // Update any user info displays
        const userInfoElements = document.querySelectorAll('.user-info');
        userInfoElements.forEach(el => {
            el.innerHTML = `
                <span class="font-medium">${user.username}</span>
                <span class="text-sm text-gray-500">${user.user_type}</span>
            `;
        });
    }
    
    // Public API
    window.authGuard = {
        init: initAuthGuard,
        checkAccess: checkRoleAccess,
        redirectToLogin: redirectToLogin,
        redirectToDashboard: redirectToDashboard,
        handleLogout: handleLogout
    };
    
    // Auto-initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAuthGuard);
    } else {
        initAuthGuard();
    }
})();