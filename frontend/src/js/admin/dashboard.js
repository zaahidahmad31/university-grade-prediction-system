// Admin Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    
    // Statistics elements
    const totalUsers = document.getElementById('totalUsers');
    const activeStudents = document.getElementById('activeStudents');
    const facultyCount = document.getElementById('facultyCount');
    const activeCourses = document.getElementById('activeCourses');
    
    // Content elements
    const recentActivities = document.getElementById('recentActivities');
    const lastChecked = document.getElementById('lastChecked');
    
    // Initialize
    init();
    
    function init() {
        // Check authentication
        if (!authApi.isLoggedIn()) {
            window.location.href = '../login.html';
            return;
        }
        
        // Check if user is admin
        const user = authApi.getCurrentUser();
        if (user.user_type !== 'admin') {
            alert('Access denied. Admin privileges required.');
            window.location.href = '../login.html';
            return;
        }
        
        // Display username
        if (user) {
            usernameElement.textContent = user.username;
        }
        
        // Set up logout
        logoutBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to logout?')) {
                authApi.logout();
            }
        });
        
        // Load dashboard data
        loadDashboardData();
        
        // Set up auto-refresh
        setInterval(updateSystemStatus, 60000); // Update every minute
    }
    
    async function loadDashboardData() {
        try {
            // Load statistics
            await loadStatistics();
            
            // Load recent activities
            await loadRecentActivities();
            
            // Update system status
            updateSystemStatus();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }
    
    async function loadStatistics() {
        try {
            const response = await apiClient.get('admin/statistics');
            
            if (response.status === 'success' && response.data) {
                const stats = response.data;
                
                // Update statistics
                totalUsers.textContent = stats.total_users || 0;
                activeStudents.textContent = stats.active_students || 0;
                facultyCount.textContent = stats.faculty_count || 0;
                activeCourses.textContent = stats.active_courses || 0;
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
            
            // Show placeholder data for demo
            totalUsers.textContent = '156';
            activeStudents.textContent = '128';
            facultyCount.textContent = '24';
            activeCourses.textContent = '18';
        }
    }
    
    async function loadRecentActivities() {
        try {
            const response = await apiClient.get('admin/activities/recent');
            
            if (response.status === 'success' && response.data) {
                displayActivities(response.data.activities);
            }
        } catch (error) {
            console.error('Error loading activities:', error);
            
            // Show demo activities
            const demoActivities = [
                {
                    icon: 'fa-user-plus',
                    color: 'text-blue-600',
                    message: 'New student registered: John Doe',
                    time: '5 minutes ago'
                },
                {
                    icon: 'fa-bell',
                    color: 'text-yellow-600',
                    message: '15 new alerts generated',
                    time: '1 hour ago'
                },
                {
                    icon: 'fa-chart-line',
                    color: 'text-green-600',
                    message: 'Predictions updated for CS301',
                    time: '2 hours ago'
                },
                {
                    icon: 'fa-user-times',
                    color: 'text-red-600',
                    message: 'User account deactivated: test_user',
                    time: '3 hours ago'
                }
            ];
            displayActivities(demoActivities);
        }
    }
    
    function displayActivities(activities) {
        if (!activities || activities.length === 0) {
            recentActivities.innerHTML = '<p class="text-gray-500">No recent activities</p>';
            return;
        }
        
        const html = activities.map(activity => `
            <div class="flex items-start space-x-3">
                <div class="flex-shrink-0">
                    <i class="fas ${activity.icon} ${activity.color}"></i>
                </div>
                <div class="flex-1">
                    <p class="text-sm text-gray-800">${activity.message}</p>
                    <p class="text-xs text-gray-500">${activity.time}</p>
                </div>
            </div>
        `).join('');
        
        recentActivities.innerHTML = html;
    }
    
    function updateSystemStatus() {
        const now = new Date();
        lastChecked.textContent = now.toLocaleTimeString();
    }
    
    // Sidebar active state
    function setActiveSidebarItem() {
        const currentPage = window.location.pathname.split('/').pop();
        const sidebarLinks = document.querySelectorAll('aside a');
        
        sidebarLinks.forEach(link => {
            if (link.getAttribute('href') === currentPage) {
                link.classList.add('bg-gray-100');
            } else {
                link.classList.remove('bg-gray-100');
            }
        });
    }
    
    setActiveSidebarItem();
});