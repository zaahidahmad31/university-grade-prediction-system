document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    const courseFilter = document.getElementById('courseFilter');
    const statusFilter = document.getElementById('statusFilter');
    const refreshBtn = document.getElementById('refreshBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const assessmentsList = document.getElementById('assessmentsList');
    const noAssessments = document.getElementById('noAssessments');
    
    // State
    let allAssessments = [];
    let coursesList = [];
    
    // Initialize
    init();
    
    function init() {
        // Check authentication
        if (!authApi.isLoggedIn()) {
            window.location.href = '../login.html';
            return;
        }
        
        // Check user role
        if (!authApi.hasRole('faculty')) {
            window.location.href = '../login.html';
            return;
        }
        
        // Display username
        const user = authApi.getCurrentUser();
        if (user) {
            usernameElement.textContent = user.username;
        }
        
        // Load data
        loadFacultyCourses();
        loadAllAssessments();
        
        // Set up event listeners
        setupEventListeners();
    }
    
    function setupEventListeners() {
        // Logout
        logoutBtn.addEventListener('click', function() {
            authApi.logout();
        });
        
        // Refresh button
        refreshBtn.addEventListener('click', function() {
            loadAllAssessments();
        });
        
        // Filter changes
        courseFilter.addEventListener('change', filterAssessments);
        statusFilter.addEventListener('change', filterAssessments);
    }
    
    async function loadFacultyCourses() {
        try {
            console.log('Loading faculty courses...');
            const response = await apiClient.get('faculty/courses');
            console.log('Courses response:', response);
            
            if (response.status === 'success' && response.data.courses) {
                coursesList = response.data.courses;
                populateCourseFilter();
            }
        } catch (error) {
            console.error('Error loading courses:', error);
        }
    }
    
    // Find the loadAllAssessments function and update the API call
    async function loadAllAssessments() {
        try {
            showLoading(true);
            console.log('Loading all assessments...');
            allAssessments = [];
            
            for (const course of coursesList) {
                try {
                    // CHANGE THIS LINE - Update the URL pattern
                    const response = await apiClient.get(`faculty/courses/${course.offering_id}/assessments`);
                    
                    if (response.status === 'success' && response.data.assessments) {
                        const courseAssessments = response.data.assessments.map(assessment => ({
                            ...assessment,
                            course_code: course.course_code,
                            course_name: course.course_name,
                            offering_id: course.offering_id
                        }));
                        allAssessments = [...allAssessments, ...courseAssessments];
                    }
                } catch (error) {
                    console.error(`Error loading assessments for course ${course.course_code}:`, error);
                }
            }
            
            filterAssessments();
            showLoading(false);
            
        } catch (error) {
            console.error('Error loading assessments:', error);
            showError('Failed to load assessments');
            showLoading(false);
        }
    }
    
    function populateCourseFilter() {
        courseFilter.innerHTML = '<option value="">All Courses</option>';
        
        coursesList.forEach(course => {
            const option = document.createElement('option');
            option.value = course.offering_id;
            option.textContent = `${course.course_code} - ${course.course_name}`;
            courseFilter.appendChild(option);
        });
    }
    
    function filterAssessments() {
        const courseFilterValue = courseFilter.value;
        const statusFilterValue = statusFilter.value;
        
        let filteredAssessments = allAssessments.filter(assessment => {
            // Course filter
            if (courseFilterValue && assessment.offering_id != courseFilterValue) {
                return false;
            }
            
            // Status filter
            if (statusFilterValue) {
                if (statusFilterValue === 'published' && !assessment.is_published) {
                    return false;
                }
                if (statusFilterValue === 'draft' && assessment.is_published) {
                    return false;
                }
            }
            
            return true;
        });
        
        displayAssessments(filteredAssessments);
    }
    
    function displayAssessments(assessments) {
        if (!assessments.length) {
            showNoAssessments();
            return;
        }
        
        // Group assessments by course
        const assessmentsByCourse = {};
        assessments.forEach(assessment => {
            const courseKey = `${assessment.course_code} - ${assessment.course_name}`;
            if (!assessmentsByCourse[courseKey]) {
                assessmentsByCourse[courseKey] = [];
            }
            assessmentsByCourse[courseKey].push(assessment);
        });
        
        assessmentsList.innerHTML = '';
        
        Object.keys(assessmentsByCourse).forEach(courseKey => {
            const courseAssessments = assessmentsByCourse[courseKey];
            const courseSection = createCourseAssessmentSection(courseKey, courseAssessments);
            assessmentsList.appendChild(courseSection);
        });
        
        assessmentsList.classList.remove('hidden');
        noAssessments.classList.add('hidden');
    }
    
    function createCourseAssessmentSection(courseKey, assessments) {
        const section = document.createElement('div');
        section.className = 'bg-white rounded-lg shadow-md overflow-hidden';
        
        section.innerHTML = `
            <div class="bg-gray-50 px-6 py-4 border-b">
                <h3 class="text-lg font-semibold text-gray-900">${courseKey}</h3>
                <p class="text-sm text-gray-600">${assessments.length} assessment(s)</p>
            </div>
            <div class="divide-y divide-gray-200">
                ${assessments.map(assessment => createAssessmentCard(assessment)).join('')}
            </div>
        `;
        
        return section;
    }
    
    function createAssessmentCard(assessment) {
        const dueDate = assessment.due_date ? new Date(assessment.due_date) : null;
        const statusBadge = assessment.is_published ? 
            '<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Published</span>' :
            '<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">Draft</span>';
        
        return `
            <div class="p-6 hover:bg-gray-50">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <div class="flex items-center space-x-3 mb-2">
                            <h4 class="text-lg font-medium text-gray-900">${assessment.title}</h4>
                            ${statusBadge}
                        </div>
                        <div class="flex items-center space-x-4 text-sm text-gray-500 mb-2">
                            <span class="flex items-center">
                                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                                </svg>
                                ${assessment.type_name}
                            </span>
                            <span>Max Score: ${assessment.max_score}</span>
                            ${assessment.weight ? `<span>Weight: ${assessment.weight}%</span>` : ''}
                            ${dueDate ? `
                                <span class="flex items-center">
                                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                    </svg>
                                    Due: ${dueDate.toLocaleDateString()} ${dueDate.toLocaleTimeString()}
                                </span>
                            ` : ''}
                        </div>
                        
                        <!-- Assessment Statistics -->
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3 text-sm">
                            <div class="text-center p-2 bg-blue-50 rounded">
                                <div class="font-semibold text-blue-600">${assessment.statistics.total_students}</div>
                                <div class="text-gray-600">Students</div>
                            </div>
                            <div class="text-center p-2 bg-green-50 rounded">
                                <div class="font-semibold text-green-600">${assessment.statistics.submitted_count}</div>
                                <div class="text-gray-600">Submitted</div>
                            </div>
                            <div class="text-center p-2 bg-yellow-50 rounded">
                                <div class="font-semibold text-yellow-600">${assessment.statistics.graded_count}</div>
                                <div class="text-gray-600">Graded</div>
                            </div>
                            <div class="text-center p-2 bg-purple-50 rounded">
                                <div class="font-semibold text-purple-600">${assessment.statistics.average_score || '-'}</div>
                                <div class="text-gray-600">Avg Score</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="flex flex-col space-y-2 ml-4">
                        
                        <a href="assessment-grade.html?assessment_id=${assessment.assessment_id}" 
                           class="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 text-center flex items-center justify-center">
                            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
                            </svg>
                            Grade
                        </a>
                        <button onclick="editAssessment(${assessment.assessment_id})" 
                                class="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 flex items-center justify-center">
                            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                            Edit
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    function showLoading(show) {
        if (show) {
            loadingIndicator.classList.remove('hidden');
            assessmentsList.classList.add('hidden');
            noAssessments.classList.add('hidden');
        } else {
            loadingIndicator.classList.add('hidden');
        }
    }
    
    function showNoAssessments() {
        assessmentsList.classList.add('hidden');
        noAssessments.classList.remove('hidden');
    }
    
    function showError(message) {
        console.error(message);
        alert(message);
    }
    
    // Global functions for buttons
    window.editAssessment = function(assessmentId) {
        window.location.href = `assessment-edit.html?assessment_id=${assessmentId}`;
    };
});