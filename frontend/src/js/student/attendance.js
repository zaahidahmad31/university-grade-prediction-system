// frontend/src/js/student/attendance.js
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    const courseFilter = document.getElementById('courseFilter');
    const statusFilter = document.getElementById('statusFilter');
    const dateFilter = document.getElementById('dateFilter');
    const downloadBtn = document.getElementById('downloadBtn');
    
    // Summary elements
    const overallRate = document.getElementById('overallRate');
    const classesAttended = document.getElementById('classesAttended');
    const lateCount = document.getElementById('lateCount');
    const absenceCount = document.getElementById('absenceCount');
    
    // Content elements
    const courseBreakdown = document.getElementById('courseBreakdown');
    const attendanceTableBody = document.getElementById('attendanceTableBody');
    const attendanceInsights = document.getElementById('attendanceInsights');
    const emptyState = document.getElementById('emptyState');
    const loadingState = document.getElementById('loadingState');
    
    // State
    let allAttendanceRecords = [];
    let filteredRecords = [];
    let attendanceStats = {};
    let courseStats = [];
    let trendChart = null;
    
    // Initialize
    init();
    
    function init() {
        // Check authentication
        if (!authApi.isLoggedIn()) {
            window.location.href = '../login.html';
            return;
        }
        
        if (!authApi.hasRole('student')) {
            window.location.href = '../login.html';
            return;
        }
        
        // Display username
        const user = authApi.getCurrentUser();
        if (user) {
            usernameElement.textContent = user.username;
        }
        
        // Setup event listeners
        setupEventListeners();
        
        // Load data
        loadAttendanceData();
    }
    
    function setupEventListeners() {
        // Logout
        logoutBtn?.addEventListener('click', function() {
            authApi.logout();
            window.location.href = '../login.html';
        });
        
        // Filters
        courseFilter?.addEventListener('change', applyFilters);
        statusFilter?.addEventListener('change', applyFilters);
        dateFilter?.addEventListener('change', applyFilters);
        
        // Download
        downloadBtn?.addEventListener('click', downloadAttendanceReport);
    }
    
    async function loadAttendanceData() {
        try {
            showLoading();
            
            // Load attendance records and stats in parallel
            const [recordsResult, statsResult] = await Promise.allSettled([
                loadAttendanceRecords(),
                loadAttendanceStats()
            ]);
            
            if (recordsResult.status === 'fulfilled') {
                allAttendanceRecords = recordsResult.value || [];
                filteredRecords = [...allAttendanceRecords];
                displayAttendanceRecords();
                populateCourseFilter();
            }
            
            if (statsResult.status === 'fulfilled') {
                attendanceStats = statsResult.value || {};
                updateSummaryCards();
                generateInsights();
            }
            
            // Update charts
            updateAttendanceTrendChart();
            updateCourseBreakdown();
            
            hideLoading();
            
        } catch (error) {
            console.error('Error loading attendance data:', error);
            showError('Failed to load attendance data');
            hideLoading();
        }
    }
    
    async function loadAttendanceRecords() {
        try {
            const response = await apiClient.get('student/attendance');
            
            if (response.status === 'success' && response.data) {
                return response.data.attendance || [];
            } else {
                return [];
            }
        } catch (error) {
            console.error('Error loading attendance records:', error);
            return [];
        }
    }
    
    async function loadAttendanceStats() {
        try {
            const response = await apiClient.get('student/attendance/stats');
            
            if (response.status === 'success' && response.data) {
                return response.data.stats || {};
            } else {
                return {};
            }
        } catch (error) {
            console.error('Error loading attendance stats:', error);
            return {};
        }
    }
    
    function updateSummaryCards() {
        if (overallRate) overallRate.textContent = `${attendanceStats.attendance_rate || 0}%`;
        if (classesAttended) classesAttended.textContent = attendanceStats.present_count || 0;
        if (lateCount) lateCount.textContent = attendanceStats.late_count || 0;
        if (absenceCount) absenceCount.textContent = attendanceStats.absent_count || 0;
    }
    
    function populateCourseFilter() {
        if (!courseFilter) return;
        
        // Get unique courses from records
        const courses = [...new Set(allAttendanceRecords.map(record => 
            `${record.course_code} - ${record.course_name}`
        ))];
        
        // Clear existing options (except "All Courses")
        courseFilter.innerHTML = '<option value="">All Courses</option>';
        
        courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course;
            option.textContent = course;
            courseFilter.appendChild(option);
        });
    }
    
    function displayAttendanceRecords() {
        if (!attendanceTableBody) return;
        
        if (filteredRecords.length === 0) {
            showEmptyState();
            return;
        }
        
        hideEmptyState();
        
        const rows = filteredRecords.map(record => createAttendanceRow(record)).join('');
        attendanceTableBody.innerHTML = rows;
    }
    
    function createAttendanceRow(record) {
        const statusClass = getStatusClass(record.status);
        const statusIcon = getStatusIcon(record.status);
        const formattedDate = new Date(record.date).toLocaleDateString();
        
        return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${formattedDate}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">${record.course_code}</div>
                    <div class="text-sm text-gray-500">${record.course_name}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusClass}">
                        <i class="fas ${statusIcon} mr-1"></i>
                        ${record.status.charAt(0).toUpperCase() + record.status.slice(1)}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${record.check_in_time || '-'}
                </td>
                <td class="px-6 py-4 text-sm text-gray-900">
                    ${record.notes || '-'}
                </td>
            </tr>
        `;
    }
    
    function getStatusClass(status) {
        switch (status) {
            case 'present': return 'bg-green-100 text-green-800';
            case 'absent': return 'bg-red-100 text-red-800';
            case 'late': return 'bg-yellow-100 text-yellow-800';
            case 'excused': return 'bg-blue-100 text-blue-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    }
    
    function getStatusIcon(status) {
        switch (status) {
            case 'present': return 'fa-check-circle';
            case 'absent': return 'fa-times-circle';
            case 'late': return 'fa-clock';
            case 'excused': return 'fa-info-circle';
            default: return 'fa-question-circle';
        }
    }
    
    function applyFilters() {
        const courseValue = courseFilter?.value || '';
        const statusValue = statusFilter?.value || '';
        const dateValue = dateFilter?.value || '';
        
        filteredRecords = allAttendanceRecords.filter(record => {
            const matchesCourse = !courseValue || 
                `${record.course_code} - ${record.course_name}` === courseValue;
            
            const matchesStatus = !statusValue || record.status === statusValue;
            
            const matchesDate = !dateValue || record.date === dateValue;
            
            return matchesCourse && matchesStatus && matchesDate;
        });
        
        displayAttendanceRecords();
    }
    
    function updateCourseBreakdown() {
        if (!courseBreakdown) return;
        
        // Calculate course-wise stats
        const courseMap = new Map();
        
        allAttendanceRecords.forEach(record => {
            const key = `${record.course_code} - ${record.course_name}`;
            if (!courseMap.has(key)) {
                courseMap.set(key, {
                    course: key,
                    total: 0,
                    present: 0,
                    absent: 0,
                    late: 0,
                    excused: 0
                });
            }
            
            const stats = courseMap.get(key);
            stats.total++;
            stats[record.status]++;
        });
        
        courseStats = Array.from(courseMap.values());
        
        if (courseStats.length === 0) {
            courseBreakdown.innerHTML = '<p class="text-gray-500 text-center">No course data available</p>';
            return;
        }
        
        const html = courseStats.map(course => {
            const attendanceRate = course.total > 0 ? 
                Math.round((course.present / course.total) * 100) : 0;
            
            const rateColor = attendanceRate >= 80 ? 'text-green-600' :
                             attendanceRate >= 60 ? 'text-yellow-600' : 'text-red-600';
            
            return `
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div class="flex-1">
                        <div class="font-medium text-gray-900">${course.course}</div>
                        <div class="text-sm text-gray-500">
                            ${course.present}/${course.total} classes attended
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-lg font-bold ${rateColor}">${attendanceRate}%</div>
                        <div class="w-20 h-2 bg-gray-200 rounded-full mt-1">
                            <div class="h-2 rounded-full ${attendanceRate >= 80 ? 'bg-green-500' : 
                                                        attendanceRate >= 60 ? 'bg-yellow-500' : 'bg-red-500'}" 
                                 style="width: ${attendanceRate}%"></div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        courseBreakdown.innerHTML = html;
    }
    
    function updateAttendanceTrendChart() {
        const ctx = document.getElementById('attendanceTrendChart');
        if (!ctx || !Chart) return;
        
        try {
            // Destroy existing chart
            if (trendChart) {
                trendChart.destroy();
                trendChart = null;
            }
            
            // Prepare data for trend chart
            const last30Days = [];
            const today = new Date();
            
            for (let i = 29; i >= 0; i--) {
                const date = new Date(today);
                date.setDate(date.getDate() - i);
                last30Days.push(date.toISOString().split('T')[0]);
            }
            
            const trendData = last30Days.map(date => {
                const dayRecords = allAttendanceRecords.filter(record => record.date === date);
                const presentCount = dayRecords.filter(record => record.status === 'present').length;
                const totalCount = dayRecords.length;
                
                return {
                    date: date,
                    rate: totalCount > 0 ? (presentCount / totalCount) * 100 : null
                };
            });
            
            trendChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: trendData.map(d => new Date(d.date).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric' 
                    })),
                    datasets: [{
                        label: 'Attendance Rate (%)',
                        data: trendData.map(d => d.rate),
                        borderColor: '#3B82F6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.1,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
            
        } catch (error) {
            console.error('Error creating trend chart:', error);
        }
    }
    
    function generateInsights() {
        if (!attendanceInsights) return;
        
        const insights = [];
        const rate = attendanceStats.attendance_rate || 0;
        
        // Attendance rate insight
        if (rate >= 90) {
            insights.push({
                icon: 'fa-trophy',
                color: 'text-green-600',
                text: 'Excellent attendance! Keep up the great work.',
                type: 'success'
            });
        } else if (rate >= 75) {
            insights.push({
                icon: 'fa-thumbs-up',
                color: 'text-blue-600',
                text: 'Good attendance rate. Try to maintain consistency.',
                type: 'info'
            });
        } else if (rate >= 60) {
            insights.push({
                icon: 'fa-exclamation-triangle',
                color: 'text-yellow-600',
                text: 'Your attendance needs improvement. Consider setting goals.',
                type: 'warning'
            });
        } else {
            insights.push({
                icon: 'fa-warning',
                color: 'text-red-600',
                text: 'Critical: Low attendance may affect your academic performance.',
                type: 'danger'
            });
        }
        
        // Late arrivals insight
        if (attendanceStats.late_count > 5) {
            insights.push({
                icon: 'fa-clock',
                color: 'text-orange-600',
                text: 'You have frequent late arrivals. Try to arrive on time.',
                type: 'warning'
            });
        }
        
        // Course-specific insights
        const lowAttendanceCourses = courseStats.filter(course => {
            const rate = course.total > 0 ? (course.present / course.total) * 100 : 0;
            return rate < 75;
        });
        
        if (lowAttendanceCourses.length > 0) {
            insights.push({
                icon: 'fa-book',
                color: 'text-purple-600',
                text: `Focus on improving attendance in ${lowAttendanceCourses.length} course(s).`,
                type: 'info'
            });
        }
        
        const html = insights.map(insight => `
            <div class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                <div class="flex-shrink-0">
                    <i class="fas ${insight.icon} ${insight.color} text-lg"></i>
                </div>
                <div class="flex-1">
                    <p class="text-sm text-gray-700">${insight.text}</p>
                </div>
            </div>
        `).join('');
        
        attendanceInsights.innerHTML = html || '<p class="text-gray-500 text-center">No insights available</p>';
    }
    
    function downloadAttendanceReport() {
        try {
            // Create CSV content
            const headers = ['Date', 'Course', 'Status', 'Check-in Time', 'Notes'];
            const csvRows = [headers.join(',')];
            
            filteredRecords.forEach(record => {
                const row = [
                    record.date,
                    `"${record.course_code} - ${record.course_name}"`,
                    record.status,
                    record.check_in_time || '',
                    `"${record.notes || ''}"`
                ];
                csvRows.push(row.join(','));
            });
            
            const csvContent = csvRows.join('\n');
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `attendance-report-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showNotification('Attendance report downloaded successfully!', 'success');
            
        } catch (error) {
            console.error('Error downloading report:', error);
            showNotification('Failed to download report', 'error');
        }
    }
    
    function showLoading() {
        if (loadingState) loadingState.classList.remove('hidden');
        if (emptyState) emptyState.classList.add('hidden');
    }
    
    function hideLoading() {
        if (loadingState) loadingState.classList.add('hidden');
    }
    
    function showEmptyState() {
        if (attendanceTableBody) attendanceTableBody.innerHTML = '';
        if (emptyState) emptyState.classList.remove('hidden');
    }
    
    function hideEmptyState() {
        if (emptyState) emptyState.classList.add('hidden');
    }
    
    function showError(message) {
        showNotification(message, 'error');
    }
    
    function showNotification(message, type = 'info') {
        const bgColor = type === 'error' ? 'bg-red-500' : 
                       type === 'success' ? 'bg-green-500' : 'bg-blue-500';
        
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 ${bgColor} text-white px-4 py-2 rounded shadow-lg z-50 transition-opacity duration-300`;
        toast.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'} mr-2"></i>
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 4000);
    }
});

// Global functions for quick actions
function generateAttendanceReport() {
    alert('Advanced reporting feature coming soon!');
}

function viewAttendanceGoals() {
    alert('Goal setting feature coming soon!');
}

function contactAcademicAdvisor() {
    window.location.href = 'mailto:advisor@university.edu?subject=Attendance Inquiry';
}