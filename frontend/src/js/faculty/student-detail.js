// student-detail.js - Individual Student Detail Page
document.addEventListener('DOMContentLoaded', function() {
    // Initialize page
    initializePage();
    
    // Get student ID and offering ID from URL - FIXED PARAMETER NAMES
    const urlParams = new URLSearchParams(window.location.search);
    const studentId = urlParams.get('student_id');  // ✅ Fixed: was 'id'
    const offeringId = urlParams.get('offering_id'); // ✅ Added missing parameter
    
    console.log('URL Parameters:', { studentId, offeringId }); // Debug log
    
    if (studentId && offeringId) {
        loadStudentDetail(studentId, offeringId);
    } else {
        showError('Student ID or Offering ID not provided');
        hideLoading(); // ✅ Added: hide loading on error
    }
});

// Page Elements
let studentData = null;
let attendanceChart = null;
let gradeChart = null;

function initializePage() {
    // Initialize tabs
    initializeTabs();
    
    // Initialize logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
    
    // Initialize back button
    const backBtn = document.querySelector('.btn-secondary');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            window.history.back();
        });
    }
    
    // Initialize action buttons
    initializeActionButtons();
    
    // Check authentication - ADDED
    if (!authApi.isLoggedIn()) {
        window.location.href = '../login.html';
        return;
    }
    
    // Check user role - ADDED
    if (!authApi.hasRole('faculty')) {
        window.location.href = '../login.html';
        return;
    }
    
    // Display username - ADDED
    const user = authApi.getCurrentUser();
    if (user) {
        const usernameElement = document.getElementById('username');
        if (usernameElement) {
            usernameElement.textContent = user.username;
        }
    }
}

function initializeTabs() {
    const tabButtons = document.querySelectorAll('#attendanceTab, #assessmentsTab, #interventionsTab');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs
            tabButtons.forEach(btn => {
                btn.classList.remove('border-blue-500', 'text-blue-600');
                btn.classList.add('border-transparent', 'text-gray-500');
            });
            
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.add('hidden');
            });
            
            // Add active class to clicked tab
            this.classList.remove('border-transparent', 'text-gray-500');
            this.classList.add('border-blue-500', 'text-blue-600');
            
            // Show corresponding content
            const tabId = this.id.replace('Tab', 'TabContent');
            const targetContent = document.getElementById(tabId);
            if (targetContent) {
                targetContent.classList.remove('hidden');
            }
        });
    });
}

function initializeActionButtons() {
    // Send email button
    const sendEmailBtn = document.getElementById('sendEmailBtn');
    if (sendEmailBtn) {
        sendEmailBtn.addEventListener('click', () => {
            if (studentData && studentData.email) {
                window.location.href = `mailto:${studentData.email}`;
            } else {
                showError('Student email not available');
            }
        });
    }
    
    // Intervention button
    const interventionBtn = document.getElementById('interventionBtn');
    const addInterventionBtn = document.getElementById('addInterventionBtn');
    
    if (interventionBtn) {
        interventionBtn.addEventListener('click', showAddInterventionModal);
    }
    
    if (addInterventionBtn) {
        addInterventionBtn.addEventListener('click', showAddInterventionModal);
    }
    
    // Modal buttons
    const saveInterventionBtn = document.getElementById('saveInterventionBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    
    if (saveInterventionBtn) {
        saveInterventionBtn.addEventListener('click', addIntervention);
    }
    
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', hideAddInterventionModal);
    }
    
    // Close modal when clicking outside
    const interventionModal = document.getElementById('interventionModal');
    if (interventionModal) {
        interventionModal.addEventListener('click', function(e) {
            if (e.target === interventionModal) {
                hideAddInterventionModal();
            }
        });
    }
}

// ✅ FIXED: Updated function to accept both parameters
async function loadStudentDetail(studentId, offeringId) {
    try {
        showLoading();
        
        console.log(`Loading student ${studentId} for offering ${offeringId}`);
        
        // ✅ FIXED: Updated API call to include both parameters
        const response = await apiClient.get(`faculty/students/${studentId}?offering_id=${offeringId}`);
        
        if (response.status === 'success') {
            studentData = response.data.student;
            console.log('Student data loaded:', studentData);
            
            populateStudentInfo(studentData);
            loadAttendanceData(studentId, offeringId);
            loadGradeData(studentId, offeringId);
            loadInterventions(studentId, offeringId);
            
            // ✅ FIXED: Show main content after loading
            const mainContent = document.getElementById('mainContent');
            if (mainContent) {
                mainContent.classList.remove('hidden');
            }
        } else {
            throw new Error(response.message || 'Failed to load student data');
        }
        
    } catch (error) {
        console.error('Error loading student detail:', error);
        
        // ✅ IMPROVED: Better error handling
        if (error.response && error.response.status === 401) {
            showError('Session expired. Please log in again.');
            setTimeout(() => {
                window.location.href = '../login.html';
            }, 2000);
        } else if (error.response && error.response.status === 404) {
            showError('Student not found or access denied.');
        } else {
            showError('Failed to load student information');
        }
    } finally {
        hideLoading();
    }
}

function populateStudentInfo(student) {
    console.log('Populating student info:', student);
    
    // ✅ FIXED: Handle both data structures
    let firstName, lastName, fullName;
    
    if (student.first_name && student.last_name) {
        // If we have separate first_name and last_name
        firstName = student.first_name;
        lastName = student.last_name;
        fullName = `${firstName} ${lastName}`;
    } else if (student.name) {
        // If we have a single name field, split it
        const nameParts = student.name.split(' ');
        firstName = nameParts[0] || '';
        lastName = nameParts.slice(1).join(' ') || '';
        fullName = student.name;
    } else {
        // Fallback
        firstName = 'Unknown';
        lastName = 'Student';
        fullName = 'Unknown Student';
    }
    
    // Update page title
    document.title = `${fullName} - Student Detail`;
    
    // Update breadcrumb
    const breadcrumbName = document.getElementById('breadcrumbName');
    if (breadcrumbName) {
        breadcrumbName.textContent = fullName;
    }
    
    // Student header info
    const studentName = document.getElementById('studentName');
    const studentId = document.getElementById('studentId');
    const courseInfo = document.getElementById('courseInfo');
    const studentInitials = document.getElementById('studentInitials');
    
    // ✅ FIXED: Use the processed names
    if (studentName) studentName.textContent = fullName;
    if (studentId) studentId.textContent = `ID: ${student.student_id}`;
    if (courseInfo) courseInfo.textContent = student.course_name || 'Course Information';
    if (studentInitials) {
        // ✅ FIXED: Safe initial generation
        const initials = `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
        studentInitials.textContent = initials;
    }
    
    // Risk badge
    const riskContainer = document.getElementById('riskBadgeContainer');
    if (riskContainer && student.risk_level) {
        const riskColor = getRiskColor(student.risk_level);
        riskContainer.innerHTML = `
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${riskColor}-100 text-${riskColor}-800">
                ${capitalizeFirst(student.risk_level)} Risk
            </span>
        `;
    }
    
    // Performance cards
    const currentGPA = document.getElementById('currentGPA');
    const attendanceRate = document.getElementById('attendanceRate');
    const predictedGrade = document.getElementById('predictedGrade');
    const riskLevel = document.getElementById('riskLevel');
    
    if (currentGPA) currentGPA.textContent = student.overall_gpa || student.gpa || 'N/A';
    if (attendanceRate) attendanceRate.textContent = `${student.attendance_rate || 0}%`;
    if (predictedGrade) predictedGrade.textContent = student.predicted_grade || student.current_grade || 'N/A';
    if (riskLevel) riskLevel.textContent = capitalizeFirst(student.risk_level || 'Unknown');
}

function getInitials(name) {
    if (!name) return 'XX';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
}

function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// ✅ FIXED: Updated to include offeringId parameter
async function loadAttendanceData(studentId, offeringId) {
    try {
        const response = await apiClient.get(`faculty/students/${studentId}/attendance?offering_id=${offeringId}`);
        
        // ✅ DEBUG: Log the actual response
        console.log('Attendance API Response:', response);
        
        if (response.status === 'success') {
            console.log('Attendance data:', response.data);
            createAttendanceChart(response.data.attendance_history || []);
            populateAttendanceTable(response.data.attendance_records || response.data.records || []);
        } else {
            console.warn('Attendance API returned non-success status:', response.status);
        }
        
    } catch (error) {
        console.error('Error loading attendance data:', error);
        const chartElement = document.getElementById('attendanceChart');
        if (chartElement) {
            chartElement.innerHTML = '<p class="text-gray-500 text-center">Failed to load attendance data</p>';
        }
    }
}

// ✅ FIXED: Updated to include offeringId parameter
async function loadGradeData(studentId, offeringId) {
    try {
        const response = await apiClient.get(`faculty/students/${studentId}/grades?offering_id=${offeringId}`);
        
        // ✅ DEBUG: Log the actual response
        console.log('Grades API Response:', response);
        
        if (response.status === 'success') {
            console.log('Grade data:', response.data);
            console.log('Assessments array:', response.data.assessments);
            
            createGradeChart(response.data.assessments || []);
            populateAssessmentsList(response.data.assessments || []);
        } else {
            console.warn('Grades API returned non-success status:', response.status);
        }
        
    } catch (error) {
        console.error('Error loading grade data:', error);
        const chartElement = document.getElementById('gradesChart');
        if (chartElement) {
            chartElement.innerHTML = '<p class="text-gray-500 text-center">Failed to load grade data</p>';
        }
    }
}

// ✅ FIXED: Updated to include offeringId parameter
async function loadInterventions(studentId, offeringId) {
    try {
        const response = await apiClient.get(`faculty/students/${studentId}/interventions?offering_id=${offeringId}`);
        
        // ✅ DEBUG: Log the actual response
        console.log('Interventions API Response:', response);
        
        if (response.status === 'success') {
            console.log('Interventions data:', response.data);
            populateInterventions(response.data.interventions || []);
        } else {
            console.warn('Interventions API returned non-success status:', response.status);
        }
        
    } catch (error) {
        console.error('Error loading interventions:', error);
        const interventionsElement = document.getElementById('interventionsList');
        if (interventionsElement) {
            interventionsElement.innerHTML = '<p class="text-gray-500">Failed to load intervention history</p>';
        }
    }
}

function createAttendanceChart(attendanceHistory) {
    const ctx = document.getElementById('attendanceChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (attendanceChart) {
        attendanceChart.destroy();
    }
    
    if (!attendanceHistory || attendanceHistory.length === 0) {
        ctx.innerHTML = '<p class="text-gray-500 text-center">No attendance data available</p>';
        return;
    }
    
    const labels = attendanceHistory.map(item => item.date);
    const data = attendanceHistory.map(item => item.attendance_rate);
    
    attendanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Attendance Rate',
                data: data,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.1
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
                title: {
                    display: true,
                    text: 'Attendance Trend'
                },
                legend: {
                    display: false
                }
            }
        }
    });
}

function createGradeChart(assessments) {
    const ctx = document.getElementById('gradesChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (gradeChart) {
        gradeChart.destroy();
    }
    
    if (!assessments || assessments.length === 0) {
        ctx.innerHTML = '<p class="text-gray-500 text-center">No assessment data available</p>';
        return;
    }
    
    const labels = assessments.map(item => item.title || item.assessment_name);
    const data = assessments.map(item => item.score || item.percentage);
    
    gradeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Score',
                data: data,
                backgroundColor: data.map(score => {
                    if (score >= 90) return 'rgba(40, 167, 69, 0.8)';
                    if (score >= 80) return 'rgba(23, 162, 184, 0.8)';
                    if (score >= 70) return 'rgba(255, 193, 7, 0.8)';
                    return 'rgba(220, 53, 69, 0.8)';
                }),
                borderColor: data.map(score => {
                    if (score >= 90) return 'rgba(40, 167, 69, 1)';
                    if (score >= 80) return 'rgba(23, 162, 184, 1)';
                    if (score >= 70) return 'rgba(255, 193, 7, 1)';
                    return 'rgba(220, 53, 69, 1)';
                }),
                borderWidth: 1
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
                title: {
                    display: true,
                    text: 'Assessment Scores'
                },
                legend: {
                    display: false
                }
            }
        }
    });
}

function populateAttendanceTable(attendanceRecords) {
    const tbody = document.getElementById('attendanceTableBody');
    if (!tbody) return;
    
    if (!attendanceRecords || attendanceRecords.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-gray-500 py-4">No attendance records found</td></tr>';
        return;
    }
    
    tbody.innerHTML = attendanceRecords.map(record => `
        <tr class="border-b">
            <td class="py-2">${formatDate(record.date)}</td>
            <td class="py-2">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${getAttendanceColor(record.status)}-100 text-${getAttendanceColor(record.status)}-800">
                    ${record.status}
                </span>
            </td>
            <td class="py-2">${record.check_in_time || '-'}</td>
            <td class="py-2">${record.notes || '-'}</td>
        </tr>
    `).join('');
}

function populateAssessmentsList(assessments) {
    const container = document.getElementById('assessmentsList');
    if (!container) return;
    
    if (!assessments || assessments.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No assessments found</p>';
        return;
    }
    
    container.innerHTML = assessments.map(assessment => `
        <div class="border rounded-lg p-4">
            <div class="flex justify-between items-start">
                <div>
                    <h4 class="font-medium">${assessment.title}</h4>
                    <p class="text-sm text-gray-500">${assessment.type}</p>
                </div>
                <div class="text-right">
                    <span class="text-lg font-semibold">${assessment.score || 'N/A'}%</span>
                    <p class="text-sm text-gray-500">${formatDate(assessment.due_date)}</p>
                </div>
            </div>
        </div>
    `).join('');
}

function populateInterventions(interventions) {
    const container = document.getElementById('interventionsList');
    if (!container) return;
    
    if (!interventions || interventions.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No interventions recorded</p>';
        return;
    }
    
    container.innerHTML = interventions.map(intervention => `
        <div class="border rounded-lg p-4">
            <div class="flex justify-between items-start mb-2">
                <h4 class="font-medium">${intervention.type}</h4>
                <span class="text-sm text-gray-500">${formatDate(intervention.created_at)}</span>
            </div>
            <p class="text-gray-700">${intervention.notes}</p>
        </div>
    `).join('');
}

// Modal functions
function showAddInterventionModal() {
    const modal = document.getElementById('interventionModal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function hideAddInterventionModal() {
    const modal = document.getElementById('interventionModal');
    if (modal) {
        modal.classList.add('hidden');
    }
    
    // Clear form
    const typeSelect = document.getElementById('interventionType');
    const notesTextarea = document.getElementById('interventionNotes');
    if (typeSelect) typeSelect.value = '';
    if (notesTextarea) notesTextarea.value = '';
}

async function addIntervention() {
    const typeSelect = document.getElementById('interventionType');
    const notesTextarea = document.getElementById('interventionNotes');
    
    if (!typeSelect || !notesTextarea) return;
    
    const type = typeSelect.value;
    const notes = notesTextarea.value.trim();
    
    if (!type || !notes) {
        showError('Please fill in all fields');
        return;
    }
    
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const studentId = urlParams.get('student_id');
        const offeringId = urlParams.get('offering_id');
        
        const response = await apiClient.post(`faculty/interventions`, {
            student_id: studentId,
            offering_id: offeringId,
            type: type,
            notes: notes
        });
        
        if (response.status === 'success') {
            showSuccess('Intervention added successfully');
            hideAddInterventionModal();
            // Reload interventions
            loadInterventions(studentId, offeringId);
        } else {
            throw new Error(response.message);
        }
        
    } catch (error) {
        console.error('Error adding intervention:', error);
        showError('Failed to add intervention');
    }
}

// Utility functions
function getRiskColor(riskLevel) {
    switch(riskLevel?.toLowerCase()) {
        case 'high': return 'red';
        case 'medium': return 'yellow';
        case 'low': return 'green';
        default: return 'gray';
    }
}

function getAttendanceColor(status) {
    switch(status?.toLowerCase()) {
        case 'present': return 'green';
        case 'late': return 'yellow';
        case 'absent': return 'red';
        case 'excused': return 'blue';
        default: return 'gray';
    }
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showLoading() {
    const loadingDiv = document.getElementById('loadingIndicator');
    if (loadingDiv) {
        loadingDiv.classList.remove('hidden');
    }
    
    const mainContent = document.getElementById('mainContent');
    if (mainContent) {
        mainContent.classList.add('hidden');
    }
}

function hideLoading() {
    const loadingDiv = document.getElementById('loadingIndicator');
    if (loadingDiv) {
        loadingDiv.classList.add('hidden');
    }
}

function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'fixed top-4 right-4 bg-green-500 text-white p-4 rounded-md shadow-lg z-50';
    alert.textContent = message;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 3000);
}

function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'fixed top-4 right-4 bg-red-500 text-white p-4 rounded-md shadow-lg z-50';
    alert.textContent = message;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 5000);
}

function logout() {
    authApi.logout();
}