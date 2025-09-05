document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    const reportContent = document.getElementById('reportContent');
    const reportTitle = document.getElementById('reportTitle');
    const reportBody = document.getElementById('reportBody');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    // State
    let currentReport = null;
    let currentReportType = null;
    
    // Initialize
    init();
    
    function init() {
        // Check authentication
        if (!authApi.isLoggedIn()) {
            window.location.href = '../login.html';
            return;
        }
        
        // Check admin role
        if (!authApi.hasRole('admin')) {
            window.location.href = '../login.html';
            return;
        }
        
        // Display username
        const user = authApi.getCurrentUser();
        if (user) {
            usernameElement.textContent = user.username;
        }
        
        // Set up event listeners
        setupEventListeners();
    }
    
    function setupEventListeners() {
        // Logout
        logoutBtn.addEventListener('click', function() {
            authApi.logout();
        });
    }
    
    // Report loading functions
    window.loadExecutiveSummary = async function() {
        showLoading(true);
        currentReportType = 'executive-summary';
        
        try {
            const response = await apiClient.get('admin/reports/executive-summary');
            
            if (response.status === 'success' && response.data) {
                displayExecutiveSummary(response.data);
            }
        } catch (error) {
            console.error('Error loading executive summary:', error);
            showError('Failed to load executive summary');
        } finally {
            showLoading(false);
        }
    };
    
    window.loadStudentPerformance = async function() {
        showLoading(true);
        currentReportType = 'student-performance';
        
        try {
            const response = await apiClient.get('admin/reports/student-performance');
            
            if (response.status === 'success' && response.data) {
                displayStudentPerformance(response.data);
            }
        } catch (error) {
            console.error('Error loading student performance:', error);
            showError('Failed to load student performance report');
        } finally {
            showLoading(false);
        }
    };
    
    window.loadCourseAnalytics = async function() {
        showLoading(true);
        currentReportType = 'course-analytics';
        
        try {
            const response = await apiClient.get('admin/reports/course-analytics');
            
            if (response.status === 'success' && response.data) {
                displayCourseAnalytics(response.data);
            }
        } catch (error) {
            console.error('Error loading course analytics:', error);
            showError('Failed to load course analytics report');
        } finally {
            showLoading(false);
        }
    };
    
    window.loadAttendanceTrends = async function() {
        showLoading(true);
        currentReportType = 'attendance-trends';
        
        try {
            const response = await apiClient.get('admin/reports/attendance-trends?days=30');
            
            if (response.status === 'success' && response.data) {
                displayAttendanceTrends(response.data);
            }
        } catch (error) {
            console.error('Error loading attendance trends:', error);
            showError('Failed to load attendance trends report');
        } finally {
            showLoading(false);
        }
    };
    
    window.loadSystemUsage = async function() {
        showLoading(true);
        currentReportType = 'system-usage';
        
        try {
            const response = await apiClient.get('admin/reports/system-usage');
            
            if (response.status === 'success' && response.data) {
                displaySystemUsage(response.data);
            }
        } catch (error) {
            console.error('Error loading system usage:', error);
            showError('Failed to load system usage report');
        } finally {
            showLoading(false);
        }
    };
    
    // Display functions
    function displayExecutiveSummary(data) {
        reportTitle.textContent = 'Executive Summary Report';
        currentReport = data;
        
        // Handle empty or invalid data
        if (!data || !data.period) {
            showError('No data available for executive summary');
            return;
        }
        
        const period = data.period;
        const startDate = new Date(period.start_date).toLocaleDateString();
        const endDate = new Date(period.end_date).toLocaleDateString();
        
        // Use default values if data is missing
        const users = data.users || {};
        const courses = data.courses || {};
        const predictions = data.predictions || {};
        const alerts = data.alerts || {};
        const performance = data.performance || {};
        
        reportBody.innerHTML = `
            <div class="mb-6">
                <p class="text-gray-600">Report Period: ${startDate} - ${endDate}</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div class="bg-blue-50 p-4 rounded">
                    <h4 class="font-semibold text-blue-800 mb-2">Users</h4>
                    <p class="text-2xl font-bold text-blue-600">${users.total_students || 0}</p>
                    <p class="text-sm text-gray-600">Total Students</p>
                    <p class="text-lg font-semibold text-blue-600 mt-2">${users.active_students || 0}</p>
                    <p class="text-sm text-gray-600">Active Students</p>
                    <p class="text-lg font-semibold text-blue-600 mt-2">${users.total_faculty || 0}</p>
                    <p class="text-sm text-gray-600">Faculty Members</p>
                </div>
                
                <div class="bg-green-50 p-4 rounded">
                    <h4 class="font-semibold text-green-800 mb-2">Courses</h4>
                    <p class="text-2xl font-bold text-green-600">${courses.total_courses || 0}</p>
                    <p class="text-sm text-gray-600">Total Courses</p>
                    <p class="text-lg font-semibold text-green-600 mt-2">${courses.active_courses || 0}</p>
                    <p class="text-sm text-gray-600">Active Courses</p>
                </div>
                
                <div class="bg-purple-50 p-4 rounded">
                    <h4 class="font-semibold text-purple-800 mb-2">Predictions & Alerts</h4>
                    <p class="text-2xl font-bold text-purple-600">${predictions.total_predictions || 0}</p>
                    <p class="text-sm text-gray-600">Predictions Generated</p>
                    <p class="text-lg font-semibold text-red-600 mt-2">${predictions.high_risk_students || 0}</p>
                    <p class="text-sm text-gray-600">High Risk Students</p>
                    <p class="text-lg font-semibold text-yellow-600 mt-2">${alerts.unresolved_alerts || 0}</p>
                    <p class="text-sm text-gray-600">Unresolved Alerts</p>
                </div>
            </div>
            
            <div class="mt-6">
                <h4 class="font-semibold mb-2">Key Metrics</h4>
                <div class="bg-gray-50 p-4 rounded">
                    <div class="flex justify-between items-center">
                        <span>Average Attendance Rate</span>
                        <span class="font-semibold">${(performance.average_attendance || 0).toFixed(1)}%</span>
                    </div>
                </div>
            </div>
        `;
        
        reportContent.classList.remove('hidden');
    }
    
    function displayStudentPerformance(data) {
        reportTitle.textContent = 'Student Performance Report';
        currentReport = data;
        
        const summary = data.summary;
        
        reportBody.innerHTML = `
            <div class="mb-6">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="bg-blue-50 p-3 rounded text-center">
                        <p class="text-sm text-gray-600">Total Students</p>
                        <p class="text-xl font-semibold text-blue-600">${summary.total_students}</p>
                    </div>
                    <div class="bg-green-50 p-3 rounded text-center">
                        <p class="text-sm text-gray-600">Average Score</p>
                        <p class="text-xl font-semibold text-green-600">${summary.average_score.toFixed(1)}%</p>
                    </div>
                    <div class="bg-purple-50 p-3 rounded text-center">
                        <p class="text-sm text-gray-600">Average Attendance</p>
                        <p class="text-xl font-semibold text-purple-600">${summary.average_attendance.toFixed(1)}%</p>
                    </div>
                    <div class="bg-red-50 p-3 rounded text-center">
                        <p class="text-sm text-gray-600">At-Risk Students</p>
                        <p class="text-xl font-semibold text-red-600">${summary.at_risk_students}</p>
                    </div>
                </div>
            </div>
            
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Student</th>
                            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Average Score</th>
                            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Attendance</th>
                            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Predicted Grade</th>
                            <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Risk Level</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        ${data.students.map(student => `
                            <tr>
                                <td class="px-4 py-2">
                                    <div>
                                        <div class="text-sm font-medium">${student.name}</div>
                                        <div class="text-xs text-gray-500">${student.student_id}</div>
                                    </div>
                                </td>
                                <td class="px-4 py-2 text-sm">${student.average_score.toFixed(1)}%</td>
                                <td class="px-4 py-2 text-sm">${student.attendance_rate.toFixed(1)}%</td>
                                <td class="px-4 py-2">
                                    <span class="px-2 py-1 text-xs font-semibold rounded-full ${getGradeClass(student.predicted_grade)}">
                                        ${student.predicted_grade}
                                    </span>
                                </td>
                                <td class="px-4 py-2">
                                    <span class="px-2 py-1 text-xs font-semibold rounded-full ${getRiskClass(student.risk_level)}">
                                        ${student.risk_level}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        reportContent.classList.remove('hidden');
    }
    
    function displayCourseAnalytics(data) {
        reportTitle.textContent = 'Course Analytics Report';
        currentReport = data;
        
        reportBody.innerHTML = `
            <div class="mb-6">
                <p class="text-gray-600">Total Courses: ${data.total_courses}</p>
            </div>
            
            <div class="space-y-4">
                ${data.courses.map(course => `
                    <div class="bg-white border rounded-lg p-4">
                        <div class="flex justify-between items-start mb-2">
                            <div>
                                <h4 class="font-semibold">${course.course_code} - ${course.course_name}</h4>
                                <p class="text-sm text-gray-600">Faculty: ${course.faculty}</p>
                            </div>
                            <div class="text-right">
                                <p class="text-lg font-semibold">${course.enrolled_students}</p>
                                <p class="text-xs text-gray-500">Students</p>
                            </div>
                        </div>
                        
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                            <div>
                                <p class="text-sm text-gray-600">Average Score</p>
                                <p class="font-semibold">${course.average_score.toFixed(1)}%</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">High Risk</p>
                                <p class="font-semibold text-red-600">${course.risk_distribution.high || 0}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">Medium Risk</p>
                                <p class="font-semibold text-yellow-600">${course.risk_distribution.medium || 0}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">Low Risk</p>
                                <p class="font-semibold text-green-600">${course.risk_distribution.low || 0}</p>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        reportContent.classList.remove('hidden');
    }
    
    function displayAttendanceTrends(data) {
        reportTitle.textContent = 'Attendance Trends Report';
        currentReport = data;
        
        reportBody.innerHTML = `
            <div class="mb-6">
                <p class="text-gray-600">Period: Last ${data.summary.period_days} days</p>
                <p class="text-gray-600">Average Attendance Rate: <span class="font-semibold">${data.summary.average_attendance_rate.toFixed(1)}%</span></p>
            </div>
            
            <div class="mb-6" style="height: 400px;">
                <canvas id="attendanceChart"></canvas>
            </div>
        `;
        
        reportContent.classList.remove('hidden');
        
        // Create attendance chart
        const ctx = document.getElementById('attendanceChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.trends.map(t => new Date(t.date).toLocaleDateString()),
                datasets: [{
                    label: 'Attendance Rate (%)',
                    data: data.trends.map(t => t.attendance_rate),
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    function displaySystemUsage(data) {
        reportTitle.textContent = 'System Usage Report';
        currentReport = data;
        
        reportBody.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bg-blue-50 p-4 rounded">
                    <h4 class="font-semibold text-blue-800 mb-3">User Activity</h4>
                    <div class="space-y-2">
                        <div>
                            <p class="text-2xl font-bold text-blue-600">${data.user_activity.active_users_today}</p>
                            <p class="text-sm text-gray-600">Active Users Today</p>
                        </div>
                        <div class="mt-3">
                            <p class="text-xl font-semibold text-blue-600">${data.user_activity.active_users_week}</p>
                            <p class="text-sm text-gray-600">Active Users This Week</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-green-50 p-4 rounded">
                    <h4 class="font-semibold text-green-800 mb-3">LMS Usage</h4>
                    <div class="space-y-2">
                        <div>
                            <p class="text-2xl font-bold text-green-600">${data.lms_usage.total_activities_week}</p>
                            <p class="text-sm text-gray-600">Total Activities (Week)</p>
                        </div>
                        <div class="mt-3">
                            <p class="text-xl font-semibold text-green-600">${data.lms_usage.average_minutes_per_day.toFixed(0)} min</p>
                            <p class="text-sm text-gray-600">Average Daily Usage</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-purple-50 p-4 rounded">
                    <h4 class="font-semibold text-purple-800 mb-3">Predictions</h4>
                    <div class="space-y-2">
                        <div>
                            <p class="text-2xl font-bold text-purple-600">${data.predictions.generated_today}</p>
                            <p class="text-sm text-gray-600">Generated Today</p>
                        </div>
                        <div class="mt-3">
                            <p class="text-xl font-semibold text-purple-600">${data.predictions.generated_week}</p>
                            <p class="text-sm text-gray-600">Generated This Week</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        reportContent.classList.remove('hidden');
    }
    
    // Export and print functions
    window.printReport = function() {
        window.print();
    };
    
    window.exportReport = function() {
        if (!currentReport) return;
        
        // Convert report data to CSV or JSON
        const dataStr = JSON.stringify(currentReport, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `${currentReportType}_${new Date().toISOString().split('T')[0]}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    };
    
    // Helper functions
    function showLoading(show) {
        if (show) {
            loadingIndicator.classList.remove('hidden');
        } else {
            loadingIndicator.classList.add('hidden');
        }
    }
    
    function showError(message) {
        reportTitle.textContent = 'Error';
        reportBody.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-exclamation-circle text-red-500 text-4xl mb-4"></i>
                <p class="text-gray-600">${message}</p>
            </div>
        `;
        reportContent.classList.remove('hidden');
    }
    
    function getGradeClass(grade) {
        const classes = {
            'A': 'bg-green-100 text-green-800',
            'B': 'bg-blue-100 text-blue-800',
            'C': 'bg-yellow-100 text-yellow-800',
            'D': 'bg-orange-100 text-orange-800',
            'F': 'bg-red-100 text-red-800'
        };
        return classes[grade] || 'bg-gray-100 text-gray-800';
    }
    
    function getRiskClass(risk) {
        const classes = {
            'high': 'bg-red-100 text-red-800',
            'medium': 'bg-yellow-100 text-yellow-800',
            'low': 'bg-green-100 text-green-800'
        };
        return classes[risk] || 'bg-gray-100 text-gray-800';
    }
});