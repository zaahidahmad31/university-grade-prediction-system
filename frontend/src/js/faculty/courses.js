// Faculty Courses Management
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    
    // Stats elements
    const totalCoursesCount = document.getElementById('totalCoursesCount');
    const totalStudentsCount = document.getElementById('totalStudentsCount');
    const atRiskStudentsCount = document.getElementById('atRiskStudentsCount');
    const totalAssessmentsCount = document.getElementById('totalAssessmentsCount');
    
    // Content elements
    const coursesContainer = document.getElementById('coursesContainer');
    const emptyState = document.getElementById('emptyState');
    const searchInput = document.getElementById('searchCourses');
    const statusFilter = document.getElementById('statusFilter');
    
    // Modal elements
    const courseModal = document.getElementById('courseModal');
    const modalCourseTitle = document.getElementById('modalCourseTitle');
    const modalContent = document.getElementById('modalContent');
    const closeModal = document.getElementById('closeModal');
    
    // State
    let allCourses = [];
    let filteredCourses = [];
    
    // Initialize
    init();
    
    function init() {
        // Check authentication
        if (!authApi.isLoggedIn()) {
            window.location.href = '../login.html';
            return;
        }
        
        if (!authApi.hasRole('faculty')) {
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
        loadAllData();
    }
    
    function setupEventListeners() {
        // Logout
        logoutBtn?.addEventListener('click', function() {
            authApi.logout();
            window.location.href = '../login.html';
        });
        
        // Refresh
        refreshBtn?.addEventListener('click', function() {
            loadAllData();
        });
        
        // Search
        searchInput?.addEventListener('input', function() {
            filterCourses();
        });
        
        // Status filter
        statusFilter?.addEventListener('change', function() {
            filterCourses();
        });
        
        // Close modal
        closeModal?.addEventListener('click', function() {
            courseModal.classList.add('hidden');
        });
        
        // Close modal on backdrop click
        courseModal?.addEventListener('click', function(e) {
            if (e.target === courseModal) {
                courseModal.classList.add('hidden');
            }
        });
    }
    
    async function loadAllData() {
        try {
            showLoading();
            await Promise.all([
                loadCourses(),
                loadDashboardStats()
            ]);
        } catch (error) {
            console.error('Error loading data:', error);
            showError('Failed to load course data');
        }
    }
    
    async function loadCourses() {
        try {
            console.log('Loading faculty courses...');
            const response = await apiClient.get('faculty/courses');
            console.log('Courses response:', response);
            
            if (response.status === 'success' && response.data.courses) {
                allCourses = response.data.courses;
                filteredCourses = [...allCourses];
                displayCourses();
                updateStats();
            } else {
                throw new Error('Failed to load courses');
            }
        } catch (error) {
            console.error('Error loading courses:', error);
            showError('Failed to load courses');
        }
    }
    
    async function loadDashboardStats() {
        try {
            // Load additional stats like at-risk students
            const atRiskResponse = await apiClient.get('faculty/at-risk-students');
            if (atRiskResponse.status === 'success' && atRiskResponse.data) {
                updateAtRiskStats(atRiskResponse.data.students || []);
            }
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    }
    
    function displayCourses() {
        if (!filteredCourses || filteredCourses.length === 0) {
            showEmptyState();
            return;
        }
        
        hideEmptyState();
        const html = filteredCourses.map(course => createCourseCard(course)).join('');
        coursesContainer.innerHTML = html;
        
        // Add click listeners to course cards
        attachCourseCardListeners();
    }
    
    function createCourseCard(course) {
        const enrollmentRate = course.capacity > 0 ? 
            Math.round((course.enrolled_count / course.capacity) * 100) : 0;
        
        const statusColor = getStatusColor(course.enrollment_status);
        const capacityColor = enrollmentRate >= 90 ? 'text-red-600' : 
                            enrollmentRate >= 70 ? 'text-orange-600' : 'text-green-600';
        
        return `
            <div class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 cursor-pointer course-card" 
                 data-offering-id="${course.offering_id}">
                <div class="p-6">
                    <!-- Course Header -->
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <h3 class="text-lg font-semibold text-gray-900 mb-1">
                                ${course.course_name}
                            </h3>
                            <p class="text-sm text-gray-600">
                                ${course.course_code} • Section ${course.section} • ${course.credits} Credits
                            </p>
                        </div>
                        <span class="px-2 py-1 text-xs font-medium rounded-full ${statusColor.bg} ${statusColor.text}">
                            Active
                        </span>
                    </div>
                    
                    <!-- Course Stats -->
                    <div class="grid grid-cols-2 gap-4 mb-4">
                        <div class="text-center p-3 bg-gray-50 rounded-lg">
                            <div class="text-2xl font-bold text-blue-600">${course.enrolled_count || 0}</div>
                            <div class="text-xs text-gray-600">Students</div>
                        </div>
                        <div class="text-center p-3 bg-gray-50 rounded-lg">
                            <div class="text-2xl font-bold ${capacityColor}">${enrollmentRate}%</div>
                            <div class="text-xs text-gray-600">Enrolled</div>
                        </div>
                    </div>
                    
                    <!-- Course Details -->
                    <div class="space-y-2 mb-4">
                        <div class="flex items-center text-sm text-gray-600">
                            <i class="fas fa-clock w-4 mr-2"></i>
                            <span>${course.meeting_pattern || 'TBA'}</span>
                        </div>
                        <div class="flex items-center text-sm text-gray-600">
                            <i class="fas fa-map-marker-alt w-4 mr-2"></i>
                            <span>${course.location || 'TBA'}</span>
                        </div>
                        <div class="flex items-center text-sm text-gray-600">
                            <i class="fas fa-users w-4 mr-2"></i>
                            <span>${course.enrolled_count}/${course.capacity} enrolled</span>
                        </div>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="flex space-x-2">
                        <button class="flex-1 bg-blue-600 text-white py-2 px-3 rounded text-sm hover:bg-blue-700 view-students-btn"
                                data-offering-id="${course.offering_id}">
                            <i class="fas fa-users mr-1"></i> Students
                        </button>
                        <button class="flex-1 bg-gray-600 text-white py-2 px-3 rounded text-sm hover:bg-gray-700 view-details-btn"
                                data-offering-id="${course.offering_id}">
                            <i class="fas fa-eye mr-1"></i> Details
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    function attachCourseCardListeners() {
        // View students buttons
        document.querySelectorAll('.view-students-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const offeringId = this.dataset.offeringId;
                viewCourseStudents(offeringId);
            });
        });
        
        // View details buttons
        document.querySelectorAll('.view-details-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const offeringId = this.dataset.offeringId;
                viewCourseDetails(offeringId);
            });
        });
        
        // Course card clicks
        document.querySelectorAll('.course-card').forEach(card => {
            card.addEventListener('click', function() {
                const offeringId = this.dataset.offeringId;
                viewCourseDetails(offeringId);
            });
        });
    }
    
    function filterCourses() {
        const searchTerm = searchInput.value.toLowerCase();
        const statusFilterValue = statusFilter.value;
        
        filteredCourses = allCourses.filter(course => {
            const matchesSearch = !searchTerm || 
                course.course_name.toLowerCase().includes(searchTerm) ||
                course.course_code.toLowerCase().includes(searchTerm);
            
            const matchesStatus = !statusFilterValue || 
                course.enrollment_status === statusFilterValue;
            
            return matchesSearch && matchesStatus;
        });
        
        displayCourses();
    }
    
    function updateStats() {
        // Calculate totals
        const totalCourses = allCourses.length;
        const totalStudents = allCourses.reduce((sum, course) => sum + (course.enrolled_count || 0), 0);
        
        // Update display
        if (totalCoursesCount) totalCoursesCount.textContent = totalCourses;
        if (totalStudentsCount) totalStudentsCount.textContent = totalStudents;
    }
    
    function updateAtRiskStats(atRiskStudents) {
        if (atRiskStudentsCount) {
            atRiskStudentsCount.textContent = atRiskStudents.length;
        }
    }
    
    async function viewCourseStudents(offeringId) {
        // Navigate to students page with course filter
        window.location.href = `students.html?course=${offeringId}`;
    }
    
    async function viewCourseDetails(offeringId) {
    try {
        showModal('Loading course details...');
        
        const course = allCourses.find(c => c.offering_id == offeringId);
        if (!course) {
            throw new Error('Course not found');
        }
        
        // Use existing data and make simpler API calls
        let students = [];
        let attendanceSummary = {};
        
        try {
            // Try to get students - this should work with your existing backend
            const studentsResponse = await apiClient.get(`faculty/students?offering_id=${offeringId}`);
            if (studentsResponse.status === 'success' && studentsResponse.data.students) {
                students = studentsResponse.data.students;
            }
        } catch (error) {
            console.warn('Could not load students:', error);
            // Continue without students data
        }
        
        // Calculate basic statistics from available data
        const totalStudents = students.length || course.enrolled_count || 0;
        const averageAttendance = students.length > 0 ? 
            students.reduce((sum, s) => sum + (s.attendance_rate || 0), 0) / students.length : 0;
        const atRiskCount = students.filter(s => s.predicted_grade && ['D', 'F'].includes(s.predicted_grade)).length;
        
        displayCourseDetailsModal(course, students, { average_attendance_rate: averageAttendance });
        
    } catch (error) {
        console.error('Error loading course details:', error);
        showModal(`
            <div class="text-center py-8">
                <i class="fas fa-exclamation-circle text-red-500 text-4xl mb-4"></i>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">Unable to Load Details</h3>
                <p class="text-gray-600 mb-4">Some course details are currently unavailable.</p>
                <div class="space-y-3">
                    <button onclick="window.location.href='students.html?course=${offeringId}'" 
                            class="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
                        <i class="fas fa-users mr-2"></i>View Students Instead
                    </button>
                    <button onclick="document.getElementById('courseModal').classList.add('hidden')" 
                            class="w-full bg-gray-600 text-white py-2 px-4 rounded hover:bg-gray-700">
                        Close
                    </button>
                </div>
            </div>
        `);
    }
}
    
    function displayCourseDetailsModal(course, students, attendanceSummary) {
    modalCourseTitle.textContent = `${course.course_code} - ${course.course_name}`;
    
    const averageAttendance = attendanceSummary.average_attendance_rate || 0;
    const atRiskCount = students.filter(s => s.predicted_grade && ['D', 'F'].includes(s.predicted_grade)).length;
    const highPerformers = students.filter(s => s.predicted_grade && ['A', 'B'].includes(s.predicted_grade)).length;
    
    modalContent.innerHTML = `
        <div class="space-y-6">
            <!-- Course Info -->
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">Course Information</h4>
                    <div class="space-y-1 text-sm">
                        <p><strong>Code:</strong> ${course.course_code}</p>
                        <p><strong>Section:</strong> ${course.section || 'N/A'}</p>
                        <p><strong>Credits:</strong> ${course.credits}</p>
                        <p><strong>Meeting:</strong> ${course.meeting_pattern || 'TBA'}</p>
                        <p><strong>Location:</strong> ${course.location || 'TBA'}</p>
                    </div>
                </div>
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">Enrollment Stats</h4>
                    <div class="space-y-1 text-sm">
                        <p><strong>Capacity:</strong> ${course.capacity || 'N/A'}</p>
                        <p><strong>Enrolled:</strong> ${course.enrolled_count || students.length}</p>
                        <p><strong>Available:</strong> ${course.capacity ? (course.capacity - (course.enrolled_count || students.length)) : 'N/A'}</p>
                        <p><strong>Utilization:</strong> ${course.capacity ? Math.round(((course.enrolled_count || students.length) / course.capacity) * 100) : 'N/A'}%</p>
                    </div>
                </div>
            </div>
            
            <!-- Performance Overview -->
            <div>
                <h4 class="font-semibold text-gray-900 mb-3">Performance Overview</h4>
                <div class="grid grid-cols-4 gap-4">
                    <div class="bg-blue-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-blue-600">${students.length}</div>
                        <div class="text-sm text-gray-600">Total Students</div>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-green-600">${Math.round(averageAttendance)}%</div>
                        <div class="text-sm text-gray-600">Avg Attendance</div>
                    </div>
                    <div class="bg-red-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-red-600">${atRiskCount}</div>
                        <div class="text-sm text-gray-600">At Risk</div>
                    </div>
                    <div class="bg-purple-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-purple-600">${highPerformers}</div>
                        <div class="text-sm text-gray-600">High Performers</div>
                    </div>
                </div>
            </div>
            
            <!-- Recent Students -->
            <div>
                <h4 class="font-semibold text-gray-900 mb-3">Students Preview (${students.length})</h4>
                <div class="max-h-60 overflow-y-auto">
                    ${students.length > 0 ? students.slice(0, 5).map(student => `
                        <div class="flex justify-between items-center py-2 border-b">
                            <div>
                                <div class="font-medium">${student.name}</div>
                                <div class="text-sm text-gray-600">${student.program_code || 'Unknown Program'} • Year ${student.year_of_study || 'N/A'}</div>
                            </div>
                            <div class="text-right text-sm">
                                <div class="font-medium">${student.predicted_grade || 'N/A'}</div>
                                <div class="text-gray-600">${Math.round(student.attendance_rate || 0)}% attendance</div>
                            </div>
                        </div>
                    `).join('') : '<p class="text-gray-500 text-center py-4">No student data available</p>'}
                </div>
                ${students.length > 5 ? `<p class="text-sm text-gray-600 mt-2">Showing 5 of ${students.length} students</p>` : ''}
            </div>
            
            <!-- Action Buttons -->
            <div class="flex space-x-3 pt-4 border-t">
                <button onclick="window.location.href='students.html?course=${course.offering_id}'" 
                        class="flex-1 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
                    <i class="fas fa-users mr-2"></i>Manage Students
                </button>
                <button onclick="window.location.href='attendance.html?course=${course.offering_id}'" 
                        class="flex-1 bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700">
                    <i class="fas fa-calendar-check mr-2"></i>Take Attendance
                </button>
                <button onclick="window.location.href='assessments.html?course=${course.offering_id}'" 
                        class="flex-1 bg-purple-600 text-white py-2 px-4 rounded hover:bg-purple-700">
                    <i class="fas fa-clipboard-check mr-2"></i>Assessments
                </button>
            </div>
        </div>
    `;
}
    
    function showModal(content) {
        modalContent.innerHTML = typeof content === 'string' ? `<p>${content}</p>` : content;
        courseModal.classList.remove('hidden');
    }
    
    function showLoading() {
        coursesContainer.innerHTML = `
            <div class="col-span-full text-center py-8">
                <div class="inline-flex items-center px-4 py-2 text-gray-600">
                    <i class="fas fa-spinner fa-spin mr-2"></i>
                    Loading courses...
                </div>
            </div>
        `;
    }
    
    function showEmptyState() {
        coursesContainer.innerHTML = '';
        emptyState.classList.remove('hidden');
    }
    
    function hideEmptyState() {
        emptyState.classList.add('hidden');
    }
    
    function showError(message) {
        coursesContainer.innerHTML = `
            <div class="col-span-full text-center py-8">
                <div class="text-red-600">
                    <i class="fas fa-exclamation-circle mr-2"></i>
                    ${message}
                </div>
            </div>
        `;
    }
    
    function getStatusColor(status) {
        switch(status) {
            case 'completed':
                return { bg: 'bg-gray-100', text: 'text-gray-800' };
            case 'active':
            default:
                return { bg: 'bg-green-100', text: 'text-green-800' };
        }
    }
});