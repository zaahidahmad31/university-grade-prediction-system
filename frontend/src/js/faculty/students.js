// students.js - Complete Fixed Version
document.addEventListener('DOMContentLoaded', function() {
    // Initialize page
    initializePage();
});

// Global variables
let allStudents = [];
let filteredStudents = [];
let coursesList = [];

// Page elements
const usernameElement = document.getElementById('username');
const logoutBtn = document.getElementById('logoutBtn');
const courseFilter = document.getElementById('courseFilter');
const riskFilter = document.getElementById('riskFilter');
const statusFilter = document.getElementById('statusFilter');
const searchInput = document.getElementById('searchInput');
const clearFiltersBtn = document.getElementById('clearFiltersBtn');
const exportBtn = document.getElementById('exportBtn');

function initializePage() {
    // Check authentication
    if (!authApi.isLoggedIn() || !authApi.hasRole('faculty')) {
        window.location.href = '../login.html';
        return;
    }
    
    // Display username
    const user = authApi.getCurrentUser();
    if (user && usernameElement) {
        usernameElement.textContent = user.username;
    }
    
    // Load data
    loadFacultyCourses();
    loadAllStudents();
    
    // Set up event listeners
    setupEventListeners();
}

function setupEventListeners() {
    // Logout
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            authApi.logout();
        });
    }
    
    // Filters
    if (courseFilter) courseFilter.addEventListener('change', filterStudents);
    if (riskFilter) riskFilter.addEventListener('change', filterStudents);
    if (statusFilter) statusFilter.addEventListener('change', filterStudents);
    if (searchInput) searchInput.addEventListener('input', debounce(filterStudents, 300));
    
    // Clear filters
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            if (courseFilter) courseFilter.value = '';
            if (riskFilter) riskFilter.value = '';
            if (statusFilter) statusFilter.value = '';
            if (searchInput) searchInput.value = '';
            filterStudents();
        });
    }
    
    // Export
    if (exportBtn) {
        exportBtn.addEventListener('click', exportToCSV);
    }
}

async function loadFacultyCourses() {
    try {
        const response = await apiClient.get('faculty/courses');
        if (response.status === 'success' && response.data.courses) {
            coursesList = response.data.courses;
            populateCourseFilter();
        }
    } catch (error) {
        console.error('Error loading courses:', error);
    }
}

async function loadAllStudents() {
    try {
        showLoading(true);
        
        // Show the students container, hide loading
        const studentsContainer = document.getElementById('studentsContainer');
        if (studentsContainer) {
            studentsContainer.classList.remove('hidden');
        }
        
        // Get all students from the new endpoint
        const response = await apiClient.get('faculty/all-students');
        console.log('All students response:', response);
        
        if (response.status === 'success' && response.data.students) {
            allStudents = response.data.students;
            
            // Update summary statistics
            if (response.data.summary) {
                updateSummaryStats(response.data.summary);
            }
            
            // Filter and display students
            filterStudents();
        } else {
            allStudents = [];
            updateSummaryStats({
                total_students: 0,
                active_students: 0,
                at_risk_students: 0,
                average_attendance: 0
            });
            showNoStudents();
        }
        
    } catch (error) {
        console.error('Error loading all students:', error);
        showError('Failed to load student information. Please refresh the page.');
    } finally {
        showLoading(false);
    }
}

function populateCourseFilter() {
    if (!courseFilter) return;
    
    courseFilter.innerHTML = '<option value="">All Courses</option>';
    
    coursesList.forEach(course => {
        const option = document.createElement('option');
        option.value = course.offering_id;
        option.textContent = `${course.course_code} - ${course.course_name}`;
        courseFilter.appendChild(option);
    });
}

function updateSummaryStats(summaryData = null) {
    if (summaryData) {
        // Use provided summary data from API
        const totalElement = document.getElementById('totalStudents');
        const activeElement = document.getElementById('activeStudents');
        const atRiskElement = document.getElementById('atRiskStudents');
        const avgAttendanceElement = document.getElementById('avgAttendance');
        
        if (totalElement) totalElement.textContent = summaryData.total_students;
        if (activeElement) activeElement.textContent = summaryData.active_students;
        if (atRiskElement) atRiskElement.textContent = summaryData.at_risk_students;
        if (avgAttendanceElement) avgAttendanceElement.textContent = `${summaryData.average_attendance}%`;
    } else {
        // Calculate from loaded student data (legacy method)
        const totalStudents = allStudents.length;
        const activeStudents = allStudents.filter(s => s.current_grade !== 'W').length;
        const atRiskStudents = allStudents.filter(s => s.risk_level === 'high' || s.risk_level === 'medium').length;
        
        const attendanceRates = allStudents
            .filter(s => s.attendance_rate !== undefined && s.attendance_rate !== null)
            .map(s => s.attendance_rate);
        const avgAttendance = attendanceRates.length > 0 
            ? attendanceRates.reduce((sum, rate) => sum + rate, 0) / attendanceRates.length 
            : 0;
        
        const totalElement = document.getElementById('totalStudents');
        const activeElement = document.getElementById('activeStudents');
        const atRiskElement = document.getElementById('atRiskStudents');
        const avgAttendanceElement = document.getElementById('avgAttendance');
        
        if (totalElement) totalElement.textContent = totalStudents;
        if (activeElement) activeElement.textContent = activeStudents;
        if (atRiskElement) atRiskElement.textContent = atRiskStudents;
        if (avgAttendanceElement) avgAttendanceElement.textContent = `${avgAttendance.toFixed(1)}%`;
    }
}

function filterStudents() {
    const courseFilterValue = courseFilter ? courseFilter.value : '';
    const riskFilterValue = riskFilter ? riskFilter.value : '';
    const statusFilterValue = statusFilter ? statusFilter.value : '';
    const searchValue = searchInput ? searchInput.value.toLowerCase() : '';
    
    filteredStudents = allStudents.filter(student => {
        // Course filter
        if (courseFilterValue && student.offering_id != courseFilterValue) {
            return false;
        }
        
        // Risk filter
        if (riskFilterValue && student.risk_level !== riskFilterValue) {
            return false;
        }
        
        // Status filter (based on current grade or attendance)
        if (statusFilterValue) {
            if (statusFilterValue === 'active' && student.current_grade === 'W') {
                return false;
            }
            if (statusFilterValue === 'withdrawn' && student.current_grade !== 'W') {
                return false;
            }
        }
        
        // Search filter
        if (searchValue) {
            const searchableText = `${student.name} ${student.student_id} ${student.email || ''} ${student.course_code}`.toLowerCase();
            if (!searchableText.includes(searchValue)) {
                return false;
            }
        }
        
        return true;
    });
    
    displayStudents();
}

function displayStudents() {
    const tbody = document.querySelector('#studentsTableBody');
    const noStudentsDiv = document.getElementById('noStudents');
    const studentsTable = document.querySelector('.overflow-x-auto');
    
    if (!tbody) return;
    
    if (filteredStudents.length === 0) {
        showNoStudents();
        return;
    }
    
    // Show table, hide no students message
    if (studentsTable) studentsTable.style.display = 'block';
    if (noStudentsDiv) noStudentsDiv.classList.add('hidden');
    
    tbody.innerHTML = filteredStudents.map(student => createStudentRow(student)).join('');
}

function createStudentRow(student) {
    const attendanceColor = getAttendanceColor(student.attendance_rate);
    const riskColor = getRiskColor(student.risk_level);
    const gradeColor = getGradeColor(student.current_grade);
    
    return `
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                        <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                            <span class="text-sm font-medium text-gray-700">
                                ${getInitials(student.name)}
                            </span>
                        </div>
                    </div>
                    <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">${student.name}</div>
                        <div class="text-sm text-gray-500">${student.student_id}</div>
                        <div class="text-sm text-gray-500">${student.email || 'N/A'}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">${student.course_code}</div>
                <div class="text-sm text-gray-500">${student.course_name}</div>
                ${student.section ? `<div class="text-xs text-gray-400">Section ${student.section}</div>` : ''}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${attendanceColor}-100 text-${attendanceColor}-800">
                    ${student.attendance_rate}%
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${gradeColor}-100 text-${gradeColor}-800">
                    ${student.current_grade || student.predicted_grade || 'N/A'}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${riskColor}-100 text-${riskColor}-800">
                    ${capitalizeFirst(student.risk_level)} Risk
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <a href="student-detail.html?student_id=${student.student_id}&offering_id=${student.offering_id}" 
                    class="text-blue-600 hover:text-blue-900 mr-3">View</a>
                <button onclick="sendAlert('${student.student_id}')" 
                        class="text-yellow-600 hover:text-yellow-900 mr-3">Alert</button>
                <button onclick="scheduleIntervention('${student.student_id}')" 
                        class="text-green-600 hover:text-green-900">Intervene</button>
            </td>
        </tr>
    `;
}

function showNoStudents() {
    const tbody = document.querySelector('#studentsTableBody');
    const noStudentsDiv = document.getElementById('noStudents');
    const studentsTable = document.querySelector('.overflow-x-auto');
    
    if (tbody) tbody.innerHTML = '';
    if (studentsTable) studentsTable.style.display = 'none';
    if (noStudentsDiv) noStudentsDiv.classList.remove('hidden');
}

function showLoading(show) {
    const loadingDiv = document.getElementById('loadingIndicator');
    if (loadingDiv) {
        loadingDiv.style.display = show ? 'block' : 'none';
    }
}

// Utility functions
function getInitials(name) {
    if (!name) return '??';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
}

function getAttendanceColor(rate) {
    if (rate >= 90) return 'green';
    if (rate >= 75) return 'yellow';
    if (rate >= 60) return 'orange';
    return 'red';
}

function getRiskColor(level) {
    switch(level?.toLowerCase()) {
        case 'high': return 'red';
        case 'medium': return 'yellow';
        case 'low': return 'green';
        default: return 'gray';
    }
}

function getGradeColor(grade) {
    if (!grade) return 'gray';
    switch(grade.toUpperCase()) {
        case 'A': case 'A+': case 'A-': return 'green';
        case 'B': case 'B+': case 'B-': return 'blue';
        case 'C': case 'C+': case 'C-': return 'yellow';
        case 'D': case 'D+': case 'D-': return 'orange';
        case 'F': return 'red';
        default: return 'gray';
    }
}

function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Action functions
function sendAlert(studentId) {
    console.log('Sending alert to student:', studentId);
    // Implement alert functionality
}

function scheduleIntervention(studentId) {
    console.log('Scheduling intervention for student:', studentId);
    // Implement intervention scheduling
}

function exportToCSV() {
    if (filteredStudents.length === 0) {
        showError('No students to export');
        return;
    }
    
    const headers = ['Student ID', 'Name', 'Email', 'Course', 'Attendance Rate', 'Current Grade', 'Risk Level'];
    const csvData = [headers];
    
    filteredStudents.forEach(student => {
        csvData.push([
            student.student_id,
            student.name,
            student.email || '',
            `${student.course_code} - ${student.course_name}`,
            `${student.attendance_rate}%`,
            student.current_grade || student.predicted_grade || 'N/A',
            capitalizeFirst(student.risk_level)
        ]);
    });
    
    const csvContent = csvData.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `students_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    
    window.URL.revokeObjectURL(url);
}

function showError(message) {
    // Create and show error alert
    const alert = document.createElement('div');
    alert.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    alert.textContent = message;
    document.body.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 5000);
}

function showSuccess(message) {
    // Create and show success alert
    const alert = document.createElement('div');
    alert.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    alert.textContent = message;
    document.body.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 5000);
}