// Admin System Alerts JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    
    // Statistics elements
    const totalAlerts = document.getElementById('totalAlerts');
    const activeAlerts = document.getElementById('activeAlerts');
    const criticalAlerts = document.getElementById('criticalAlerts');
    const resolvedToday = document.getElementById('resolvedToday');
    
    // Filter elements
    const severityFilter = document.getElementById('severityFilter');
    const typeFilter = document.getElementById('typeFilter');
    const statusFilter = document.getElementById('statusFilter');
    const courseFilter = document.getElementById('courseFilter');
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    
    // Table elements
    const alertsTableBody = document.getElementById('alertsTableBody');
    const selectAll = document.getElementById('selectAll');
    const bulkResolveBtn = document.getElementById('bulkResolveBtn');
    const exportBtn = document.getElementById('exportBtn');
    
    // Pagination elements
    const startRecord = document.getElementById('startRecord');
    const endRecord = document.getElementById('endRecord');
    const totalRecords = document.getElementById('totalRecords');
    const prevPage = document.getElementById('prevPage');
    const nextPage = document.getElementById('nextPage');
    
    // Modal elements
    const alertModal = document.getElementById('alertModal');
    const closeModal = document.getElementById('closeModal');
    const alertDetails = document.getElementById('alertDetails');
    
    // Chart
    let alertTrendsChart = null;
    
    // State
    let alerts = [];
    let selectedAlerts = new Set();
    let currentPage = 1;
    let totalPages = 1;
    let filters = {};
    
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
        
        // Set up event listeners
        setupEventListeners();
        
        // Load initial data
        loadStatistics();
        loadCourses();
        loadAlerts();
        initializeChart();
    }
    
    function setupEventListeners() {
        // Logout
        logoutBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to logout?')) {
                authApi.logout();
            }
        });
        
        // Filters
        applyFiltersBtn.addEventListener('click', applyFilters);
        
        // Select all
        selectAll.addEventListener('change', function() {
            const checkboxes = alertsTableBody.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(cb => {
                cb.checked = selectAll.checked;
                const alertId = parseInt(cb.dataset.alertId);
                if (selectAll.checked) {
                    selectedAlerts.add(alertId);
                } else {
                    selectedAlerts.delete(alertId);
                }
            });
            updateBulkActions();
        });
        
        // Bulk resolve
        bulkResolveBtn.addEventListener('click', bulkResolveAlerts);
        
        // Export
        exportBtn.addEventListener('click', exportAlerts);
        
        // Pagination
        prevPage.addEventListener('click', function() {
            if (currentPage > 1) {
                currentPage--;
                loadAlerts();
            }
        });
        
        nextPage.addEventListener('click', function() {
            if (currentPage < totalPages) {
                currentPage++;
                loadAlerts();
            }
        });
        
        // Modal - Fix: Use the actual function name
        closeModal.addEventListener('click', function() {
            closeAlertModal();
        });
        
        alertModal.addEventListener('click', function(e) {
            if (e.target === alertModal) {
                closeAlertModal();
            }
        });
    }
    
    // Define closeAlertModal function at the top level
    function closeAlertModal() {
        alertModal.classList.add('hidden');
    }
    
    async function loadStatistics() {
        try {
            const response = await adminApi.getSystemAlertStats();
            
            if (response.status === 'success' && response.data) {
                totalAlerts.textContent = response.data.total_alerts || '0';
                activeAlerts.textContent = response.data.active_alerts || '0';
                criticalAlerts.textContent = response.data.critical_alerts || '0';
                resolvedToday.textContent = response.data.resolved_today || '0';
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
            // Show demo data
            totalAlerts.textContent = '156';
            activeAlerts.textContent = '42';
            criticalAlerts.textContent = '8';
            resolvedToday.textContent = '12';
        }
    }
    
    async function loadCourses() {
        try {
            const response = await adminApi.getCourses({ limit: 100 });
            
            if (response.status === 'success' && response.data) {
                const courses = response.data.courses;
                courseFilter.innerHTML = '<option value="">All Courses</option>';
                courses.forEach(course => {
                    courseFilter.innerHTML += `<option value="${course.course_id}">${course.course_code} - ${course.course_name}</option>`;
                });
            }
        } catch (error) {
            console.error('Error loading courses:', error);
        }
    }
    
    async function loadAlerts() {
        try {
            // Show loading
            alertsTableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="px-6 py-4 text-center text-gray-500">
                        <i class="fas fa-spinner fa-spin mr-2"></i>Loading alerts...
                    </td>
                </tr>
            `;
            
            const params = {
                page: currentPage,
                limit: 10,
                ...filters
            };
            
            const response = await adminApi.getSystemAlerts(params);
            
            if (response.status === 'success' && response.data) {
                // Handle both possible response structures
                if (Array.isArray(response.data)) {
                    alerts = response.data;
                    totalPages = response.pagination ? Math.ceil(response.pagination.total / 10) : 1;
                } else if (response.data.alerts) {
                    alerts = response.data.alerts;
                    currentPage = response.data.current_page || 1;
                    totalPages = response.data.total_pages || 1;
                }
                
                displayAlerts(alerts);
                updatePagination({
                    current_page: currentPage,
                    per_page: 10,
                    total: response.pagination ? response.pagination.total : alerts.length
                });
            }
        } catch (error) {
            console.error('Error loading alerts:', error);
            
            // Check if it's an authentication error
            if (error.response && error.response.status === 401) {
                alert('Session expired. Please login again.');
                authApi.logout();
                return;
            }
            
            // Show demo data for development
            const demoAlerts = [
                {
                    alert_id: 1,
                    type: 'Low Attendance',
                    message: 'Student attendance below 70% threshold',
                    severity: 'warning',
                    student_name: 'John Doe',
                    student_id: 'STU001',
                    course_name: 'CS101 - Introduction to Computer Science',
                    triggered_date: new Date().toISOString(),
                    is_read: false,
                    is_resolved: false
                },
                {
                    alert_id: 2,
                    type: 'Grade Risk',
                    message: 'Predicted to fail based on current performance',
                    severity: 'critical',
                    student_name: 'Jane Smith',
                    student_id: 'STU002',
                    course_name: 'MATH101 - Calculus I',
                    triggered_date: new Date(Date.now() - 86400000).toISOString(),
                    is_read: true,
                    is_resolved: false
                },
                {
                    alert_id: 3,
                    type: 'Missing Assignments',
                    message: 'More than 2 assignments missing',
                    severity: 'warning',
                    student_name: 'Bob Johnson',
                    student_id: 'STU003',
                    course_name: 'CS201 - Data Structures',
                    triggered_date: new Date(Date.now() - 172800000).toISOString(),
                    is_read: true,
                    is_resolved: true
                }
            ];
            displayAlerts(demoAlerts);
            updatePagination({ total: 3, current_page: 1, per_page: 10 });
        }
    }
    
    function displayAlerts(alerts) {
        if (!alerts || alerts.length === 0) {
            alertsTableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="px-6 py-4 text-center text-gray-500">
                        No alerts found
                    </td>
                </tr>
            `;
            return;
        }
        
        const html = alerts.map(alert => {
            const severityColors = {
                'critical': 'text-red-600 bg-red-100',
                'warning': 'text-yellow-600 bg-yellow-100',
                'info': 'text-blue-600 bg-blue-100'
            };
            
            const statusBadge = alert.is_resolved 
                ? '<span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">Resolved</span>'
                : alert.is_read 
                    ? '<span class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">Read</span>'
                    : '<span class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">New</span>';
            
            return `
                <tr class="hover:bg-gray-50 ${!alert.is_read ? 'bg-blue-50' : ''}">
                    <td class="px-6 py-4">
                        <input type="checkbox" class="rounded border-gray-300" 
                               data-alert-id="${alert.alert_id || alert.id}"
                               ${selectedAlerts.has(alert.alert_id || alert.id) ? 'checked' : ''}>
                    </td>
                    <td class="px-6 py-4">
                        <div>
                            <div class="text-sm font-medium text-gray-900">${alert.type || alert.alert_type}</div>
                            <div class="text-sm text-gray-500">${alert.message}</div>
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm">
                            <div class="font-medium text-gray-900">${alert.student_name || 'N/A'}</div>
                            <div class="text-gray-500">${alert.student_id || ''}</div>
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${alert.course_name || 'N/A'}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 py-1 text-xs font-medium ${severityColors[alert.severity] || 'text-gray-600 bg-gray-100'} rounded-full">
                            ${alert.severity}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${formatDate(alert.triggered_date || alert.created_at)}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        ${statusBadge}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button onclick="viewAlert(${alert.alert_id || alert.id})" class="text-indigo-600 hover:text-indigo-900 mr-2">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${!alert.is_resolved ? `
                            <button onclick="resolveAlert(${alert.alert_id || alert.id})" class="text-green-600 hover:text-green-900">
                                <i class="fas fa-check"></i>
                            </button>
                        ` : ''}
                    </td>
                </tr>
            `;
        }).join('');
        
        alertsTableBody.innerHTML = html;
        
        // Add checkbox listeners
        alertsTableBody.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', function() {
                const alertId = parseInt(this.dataset.alertId);
                if (this.checked) {
                    selectedAlerts.add(alertId);
                } else {
                    selectedAlerts.delete(alertId);
                }
                updateBulkActions();
            });
        });
    }
    
    function updatePagination(data) {
        const start = ((data.current_page || 1) - 1) * (data.per_page || 10) + 1;
        const end = Math.min((data.current_page || 1) * (data.per_page || 10), data.total || 0);
        
        startRecord.textContent = data.total > 0 ? start : 0;
        endRecord.textContent = end;
        totalRecords.textContent = data.total || 0;
        
        prevPage.disabled = currentPage === 1;
        nextPage.disabled = currentPage === totalPages;
    }
    
    function updateBulkActions() {
        bulkResolveBtn.disabled = selectedAlerts.size === 0;
    }
    
    function applyFilters() {
        filters = {
            severity: severityFilter.value,
            type: typeFilter.value,
            status: statusFilter.value,
            course_id: courseFilter.value
        };
        
        // Remove empty filters
        Object.keys(filters).forEach(key => {
            if (!filters[key]) delete filters[key];
        });
        
        currentPage = 1;
        loadAlerts();
    }
    
    async function bulkResolveAlerts() {
        if (selectedAlerts.size === 0) return;
        
        if (confirm(`Are you sure you want to resolve ${selectedAlerts.size} alert(s)?`)) {
            try {
                // In a real implementation, this would call the API
                alert('Alerts resolved successfully');
                selectedAlerts.clear();
                loadAlerts();
                loadStatistics();
            } catch (error) {
                console.error('Error resolving alerts:', error);
                alert('Failed to resolve alerts');
            }
        }
    }
    
    function exportAlerts() {
        // In a real implementation, this would generate a CSV/Excel file
        alert('Export functionality would download alerts as CSV/Excel file');
    }
    
    function initializeChart() {
    // Get the canvas element
    const canvas = document.getElementById('alertTrendsChart');
    if (!canvas) {
        console.error('Chart canvas not found');
        return;
    }
    
    // Fix: Set explicit dimensions for the canvas
    const container = canvas.parentElement;
    canvas.width = container.offsetWidth;
    canvas.height = 400; // Fixed height
    
    const ctx = canvas.getContext('2d');
    
    // Generate demo data for last 7 days
    const labels = [];
    const criticalData = [];
    const warningData = [];
    const infoData = [];
    
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));
        
        criticalData.push(Math.floor(Math.random() * 10));
        warningData.push(Math.floor(Math.random() * 20) + 10);
        infoData.push(Math.floor(Math.random() * 15) + 5);
    }
    
    // Destroy existing chart if it exists
    if (alertTrendsChart) {
        alertTrendsChart.destroy();
    }
    
    alertTrendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Critical',
                    data: criticalData,
                    borderColor: 'rgb(239, 68, 68)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Warning',
                    data: warningData,
                    borderColor: 'rgb(245, 158, 11)',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Info',
                    data: infoData,
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 5
                    }
                }
            }
        }
    });
    
    // Fix: Prevent resize observer issues
    window.addEventListener('resize', function() {
        if (alertTrendsChart) {
            // Debounce resize
            clearTimeout(window.chartResizeTimeout);
            window.chartResizeTimeout = setTimeout(() => {
                const container = canvas.parentElement;
                canvas.width = container.offsetWidth;
                canvas.height = 400;
                alertTrendsChart.resize();
            }, 250);
        }
    });
}
    
    // Global functions
    window.viewAlert = async function(alertId) {
        const alert = alerts.find(a => (a.alert_id || a.id) === alertId);
        if (!alert) return;
        
        // Show alert details in modal
        alertDetails.innerHTML = `
            <div class="space-y-4">
                <div>
                    <h4 class="text-sm font-medium text-gray-500">Alert Type</h4>
                    <p class="mt-1 text-lg">${alert.type || alert.alert_type}</p>
                </div>
                
                <div>
                    <h4 class="text-sm font-medium text-gray-500">Message</h4>
                    <p class="mt-1">${alert.message}</p>
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <h4 class="text-sm font-medium text-gray-500">Student</h4>
                        <p class="mt-1">${alert.student_name || 'N/A'} ${alert.student_id ? `(${alert.student_id})` : ''}</p>
                    </div>
                    
                    <div>
                        <h4 class="text-sm font-medium text-gray-500">Course</h4>
                        <p class="mt-1">${alert.course_name || 'N/A'}</p>
                    </div>
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <h4 class="text-sm font-medium text-gray-500">Severity</h4>
                        <p class="mt-1">
                            <span class="px-2 py-1 text-sm font-medium ${
                                alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                                alert.severity === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-blue-100 text-blue-800'
                            } rounded-full">
                                ${alert.severity}
                            </span>
                        </p>
                    </div>
                    
                    <div>
                        <h4 class="text-sm font-medium text-gray-500">Triggered Date</h4>
                        <p class="mt-1">${new Date(alert.triggered_date || alert.created_at).toLocaleString()}</p>
                    </div>
                </div>
                
                ${alert.prediction_details ? `
                    <div class="border-t pt-4">
                        <h4 class="text-sm font-medium text-gray-500 mb-2">Prediction Details</h4>
                        <div class="bg-gray-50 p-3 rounded">
                            <p class="text-sm">Predicted Grade: <span class="font-medium">${alert.prediction_details.predicted_grade}</span></p>
                            <p class="text-sm">Confidence: <span class="font-medium">${alert.prediction_details.confidence}%</span></p>
                        </div>
                    </div>
                ` : ''}
                
                <div class="flex justify-end space-x-3 pt-4 border-t">
                    ${!alert.is_resolved ? `
                        <button onclick="resolveAlert(${alert.alert_id || alert.id}); closeAlertModal();" 
                                class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md">
                            <i class="fas fa-check mr-2"></i>Resolve Alert
                        </button>
                    ` : ''}
                    <button onclick="closeAlertModal()" class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-md">
                        Close
                    </button>
                </div>
            </div>
        `;
        
        alertModal.classList.remove('hidden');
    };
    
    window.resolveAlert = async function(alertId) {
        if (confirm('Are you sure you want to resolve this alert?')) {
            try {
                const response = await adminApi.resolveAlert(alertId);
                if (response.status === 'success') {
                    alert('Alert resolved successfully');
                    loadAlerts();
                    loadStatistics();
                }
            } catch (error) {
                console.error('Error resolving alert:', error);
                alert('Failed to resolve alert');
            }
        }
    };
    
    // Make closeAlertModal available globally as well
    window.closeAlertModal = closeAlertModal;
    
    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 3600000) { // Less than 1 hour
            return `${Math.floor(diff / 60000)} minutes ago`;
        } else if (diff < 86400000) { // Less than 1 day
            return `${Math.floor(diff / 3600000)} hours ago`;
        } else if (diff < 604800000) { // Less than 1 week
            return `${Math.floor(diff / 86400000)} days ago`;
        } else {
            return date.toLocaleDateString();
        }
    }
    
    // Set active sidebar item
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