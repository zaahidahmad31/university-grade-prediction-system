document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded fired');
    
    // Elements
    const elements = {
        searchInput: document.getElementById('searchInput'),
        departmentFilter: document.getElementById('departmentFilter'),
        creditsFilter: document.getElementById('creditsFilter'),
        dayFilter: document.getElementById('dayFilter'),
        availableCoursesList: document.getElementById('availableCoursesList'),
        enrolledCount: document.getElementById('enrolledCount'),
        totalCredits: document.getElementById('totalCredits'),
        availableCount: document.getElementById('availableCount'),
        maxCredits: document.getElementById('maxCredits'),
        enrollmentModal: document.getElementById('enrollmentModal'),
        enrollmentDetails: document.getElementById('enrollmentDetails'),
        cancelEnrollment: document.getElementById('cancelEnrollment'),
        confirmEnrollment: document.getElementById('confirmEnrollment')
    };
    
    // State
    let state = {
        availableCourses: [],
        filteredCourses: [],
        enrolledCourses: [],
        selectedCourse: null,
        totalEnrolledCredits: 0,
        maxCreditsAllowed: 18
    };
    
    // Initialize
    init();
    
    function init() {
        console.log('init() called');
        // Auth guard will handle authentication
        if (!authApi.hasRole('student')) {
            return;
        }
        
        setupEventListeners();
        loadData();
    }
    
    function setupEventListeners() {
        console.log('setupEventListeners() called');
        
        // Search and filters
        elements.searchInput?.addEventListener('input', debounce(filterCourses, 300));
        elements.departmentFilter?.addEventListener('change', filterCourses);
        elements.creditsFilter?.addEventListener('change', filterCourses);
        elements.dayFilter?.addEventListener('change', filterCourses);
        
        // Modal controls - Add debug wrapper
        elements.cancelEnrollment?.addEventListener('click', closeEnrollmentModal);
        
        // Debug wrapper for confirmEnrollment
        if (elements.confirmEnrollment) {
            console.log('Adding click listener to confirmEnrollment button');
            elements.confirmEnrollment.addEventListener('click', function(e) {
                console.log('Confirm button clicked');
                console.log('Current state.selectedCourse:', state.selectedCourse);
                confirmEnrollment();
            });
        }
        
        // Close modal on backdrop click
        elements.enrollmentModal?.addEventListener('click', function(e) {
            if (e.target === this) closeEnrollmentModal();
        });
    }
    
    async function loadData() {
        showLoading();
        
        try {
            // Load enrolled courses and available courses in parallel
            const [enrolledResponse, availableResponse] = await Promise.all([
                studentApi.getEnrolledCourses(),
                studentApi.getAvailableCourses()
            ]);
            
            console.log('Enrolled courses response:', enrolledResponse);
            console.log('Available courses response:', availableResponse);
            
            // Process enrolled courses
            if (enrolledResponse && enrolledResponse.status === 'success' && enrolledResponse.data) {
                state.enrolledCourses = enrolledResponse.data.courses || [];
                updateEnrollmentStats();
            }
            
            // Process available courses
            if (availableResponse && availableResponse.status === 'success' && availableResponse.data) {
                state.availableCourses = availableResponse.data.courses || [];
                state.filteredCourses = [...state.availableCourses];
                displayAvailableCourses();
            }
            
        } catch (error) {
            console.error('Error loading data:', error);
            showError('Failed to load course data');
        } finally {
            hideLoading();
        }
    }
    
    function updateEnrollmentStats() {
        // Calculate total credits
        state.totalEnrolledCredits = state.enrolledCourses.reduce((sum, course) => {
            return sum + (course.credits || 0);
        }, 0);
        
        // Update display
        if (elements.enrolledCount) {
            elements.enrolledCount.textContent = state.enrolledCourses.length;
        }
        if (elements.totalCredits) {
            elements.totalCredits.textContent = state.totalEnrolledCredits;
        }
        if (elements.availableCount) {
            elements.availableCount.textContent = state.availableCourses.length;
        }
    }
    
    function filterCourses() {
        const searchTerm = elements.searchInput?.value.toLowerCase() || '';
        const department = elements.departmentFilter?.value || '';
        const credits = elements.creditsFilter?.value || '';
        const day = elements.dayFilter?.value || '';
        
        state.filteredCourses = state.availableCourses.filter(course => {
            // Search filter
            const matchesSearch = !searchTerm || 
                course.course_code?.toLowerCase().includes(searchTerm) ||
                course.course_name?.toLowerCase().includes(searchTerm);
            
            // Department filter
            const matchesDepartment = !department || 
                course.course_code?.startsWith(department);
            
            // Credits filter
            const matchesCredits = !credits || 
                course.credits === parseInt(credits);
            
            // Day filter
            const matchesDay = !day || 
                course.meeting_pattern?.includes(day);
            
            return matchesSearch && matchesDepartment && matchesCredits && matchesDay;
        });
        
        displayAvailableCourses();
    }
    
    function displayAvailableCourses() {
        if (!elements.availableCoursesList) return;
        
        if (state.filteredCourses.length === 0) {
            elements.availableCoursesList.innerHTML = `
                <p class="text-gray-500 text-center py-8">No courses found matching your criteria.</p>
            `;
            return;
        }
        
        elements.availableCoursesList.innerHTML = state.filteredCourses.map(course => `
            <div class="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h4 class="font-semibold text-lg">${course.course_code} - ${course.course_name}</h4>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2 text-sm text-gray-600">
                            <p><i class="fas fa-user-tie mr-2"></i>Instructor: ${course.instructor || 'TBA'}</p>
                            <p><i class="fas fa-clock mr-2"></i>Schedule: ${course.meeting_pattern || 'TBA'}</p>
                            <p><i class="fas fa-map-marker-alt mr-2"></i>Location: ${course.location || 'TBA'}</p>
                            <p><i class="fas fa-users mr-2"></i>Available: ${course.available_seats} seats</p>
                        </div>
                        <div class="mt-2">
                            <span class="inline-block px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">
                                ${course.credits} Credits
                            </span>
                            <span class="inline-block px-2 py-1 text-xs rounded bg-gray-100 text-gray-800 ml-2">
                                Section ${course.section_number}
                            </span>
                        </div>
                    </div>
                    <div class="ml-4">
                        ${renderEnrollButton(course)}
                    </div>
                </div>
            </div>
        `).join('');
        
        // Attach event listeners to enroll buttons
        document.querySelectorAll('.enroll-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                console.log('Enroll button clicked for course:', this.dataset.courseId);
                const courseId = parseInt(this.dataset.courseId);
                const course = state.availableCourses.find(c => c.offering_id === courseId);
                if (course) {
                    console.log('Found course:', course);
                    showEnrollmentModal(course);
                }
            });
        });
    }
    
    function renderEnrollButton(course) {
        const canEnroll = checkEnrollmentEligibility(course);
        
        if (!canEnroll.eligible) {
            return `
                <button class="px-4 py-2 bg-gray-300 text-gray-600 rounded cursor-not-allowed" disabled>
                    ${canEnroll.reason}
                </button>
            `;
        }
        
        return `
            <button class="enroll-btn px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    data-course-id="${course.offering_id}">
                <i class="fas fa-plus mr-2"></i>Enroll
            </button>
        `;
    }
    
    function checkEnrollmentEligibility(course) {
        // Check if seats available
        if (course.available_seats === 0) {
            return { eligible: false, reason: 'Full' };
        }
        
        // Check credit limit
        const newTotalCredits = state.totalEnrolledCredits + (course.credits || 0);
        if (newTotalCredits > state.maxCreditsAllowed) {
            return { eligible: false, reason: 'Credit Limit' };
        }
        
        // Check time conflicts (simplified - in real app, would check actual times)
        const hasConflict = state.enrolledCourses.some(enrolled => {
            return enrolled.meeting_pattern === course.meeting_pattern;
        });
        
        if (hasConflict) {
            return { eligible: false, reason: 'Time Conflict' };
        }
        
        return { eligible: true };
    }
    
    function showEnrollmentModal(course) {
        console.log('showEnrollmentModal called with course:', course);
        state.selectedCourse = course;
        
        const newTotalCredits = state.totalEnrolledCredits + (course.credits || 0);
        
        elements.enrollmentDetails.innerHTML = `
            <div class="space-y-3">
                <h4 class="font-semibold">${course.course_code} - ${course.course_name}</h4>
                
                <div class="bg-gray-50 p-3 rounded space-y-2 text-sm">
                    <p><strong>Credits:</strong> ${course.credits}</p>
                    <p><strong>Section:</strong> ${course.section_number}</p>
                    <p><strong>Instructor:</strong> ${course.instructor || 'TBA'}</p>
                    <p><strong>Schedule:</strong> ${course.meeting_pattern || 'TBA'}</p>
                    <p><strong>Location:</strong> ${course.location || 'TBA'}</p>
                </div>
                
                <div class="bg-blue-50 p-3 rounded">
                    <p class="text-sm"><strong>Current Credits:</strong> ${state.totalEnrolledCredits}</p>
                    <p class="text-sm"><strong>After Enrollment:</strong> ${newTotalCredits}</p>
                    <p class="text-sm text-gray-600 mt-1">Maximum allowed: ${state.maxCreditsAllowed} credits</p>
                </div>
                
                <p class="text-sm text-gray-600">
                    By enrolling, you confirm that you have checked for schedule conflicts and meet all prerequisites.
                </p>
            </div>
        `;
        
        elements.enrollmentModal.classList.remove('hidden');
        console.log('Modal shown, state.selectedCourse is now:', state.selectedCourse);
    }
    
    function closeEnrollmentModal() {
        console.log('closeEnrollmentModal called');
        elements.enrollmentModal.classList.add('hidden');
        state.selectedCourse = null;
    }
    
    async function confirmEnrollment() {
    if (!state.selectedCourse) {
        console.error('No course selected for enrollment');
        showError('Please select a course first');
        return;
    }
    
    // Store the course info before closing modal
    const courseToEnroll = state.selectedCourse;
    
    try {
        showLoading();
        closeEnrollmentModal(); // This sets state.selectedCourse to null
        
        console.log('Enrolling in course:', courseToEnroll.offering_id);
        
        // Use courseToEnroll instead of state.selectedCourse
        const response = await studentApi.enrollInCourse(courseToEnroll.offering_id);
        
        console.log('Enrollment response:', response);
        
        if (response && response.status === 'success') {
            showSuccess('Successfully enrolled in ' + courseToEnroll.course_code);
            // Reload data to update lists
            await loadData();
        } else {
            console.error('Enrollment failed with response:', response);
            showError(response?.message || 'Failed to enroll in course');
        }
    } catch (error) {
        console.error('Enrollment error caught:', error);
        console.error('Error response:', error.response);
        console.error('Error response data:', error.response?.data);
        
        // Check different error response structures
        let errorMessage = 'Failed to enroll in course';
        
        if (error.response?.data?.message) {
            errorMessage = error.response.data.message;
        } else if (error.response?.data?.error) {
            errorMessage = error.response.data.error;
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        showError(errorMessage);
    } finally {
        hideLoading();
    }
}
    
    // Utility functions
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
    
    function showLoading() {
        const loader = document.getElementById('loader');
        if (loader) loader.style.display = 'flex';
    }
    
    function hideLoading() {
        const loader = document.getElementById('loader');
        if (loader) loader.style.display = 'none';
    }
    
    function showSuccess(message) {
        showNotification(message, 'success');
    }
    
    function showError(message) {
        showNotification(message, 'error');
    }
    
    function showNotification(message, type = 'info') {
        const bgColor = type === 'error' ? 'bg-red-500' : 
                       type === 'success' ? 'bg-green-500' : 'bg-blue-500';
        
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded shadow-lg z-50`;
        toast.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 
                                  type === 'success' ? 'check-circle' : 
                                  'info-circle'} mr-2"></i>
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
    
    // Log when script loads
    console.log('course-enrollment.js loaded');
});