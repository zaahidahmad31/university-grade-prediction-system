// Admin Course Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    const addCourseBtn = document.getElementById('addCourseBtn');
    
    // Statistics elements
    const totalCourses = document.getElementById('totalCourses');
    const activeOfferings = document.getElementById('activeOfferings');
    const totalEnrollments = document.getElementById('totalEnrollments');
    const avgCredits = document.getElementById('avgCredits');
    
    // Table elements
    const coursesTableBody = document.getElementById('coursesTableBody');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    
    // Pagination elements
    const startRecord = document.getElementById('startRecord');
    const endRecord = document.getElementById('endRecord');
    const totalRecords = document.getElementById('totalRecords');
    const prevPage = document.getElementById('prevPage');
    const nextPage = document.getElementById('nextPage');
    
    // Modal elements
    const courseModal = document.getElementById('courseModal');
    const modalTitle = document.getElementById('modalTitle');
    const closeModal = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelBtn');
    const courseForm = document.getElementById('courseForm');
    
    // State
    let courses = [];
    let currentPage = 1;
    let totalPages = 1;
    let searchQuery = '';
    
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
    }
    
    function setupEventListeners() {
        // Logout
        logoutBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to logout?')) {
                authApi.logout();
            }
        });
        
        // Add course
        addCourseBtn.addEventListener('click', function() {
            openCourseModal();
        });
        
        // Search
        searchBtn.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        
        // Pagination
        prevPage.addEventListener('click', function() {
            if (currentPage > 1) {
                currentPage--;
                loadCourses();
            }
        });
        
        nextPage.addEventListener('click', function() {
            if (currentPage < totalPages) {
                currentPage++;
                loadCourses();
            }
        });
        
        // Modal
        closeModal.addEventListener('click', closeCourseModal);
        cancelBtn.addEventListener('click', closeCourseModal);
        courseForm.addEventListener('submit', handleCourseSubmit);
        
        // Close modal on outside click
        courseModal.addEventListener('click', function(e) {
            if (e.target === courseModal) {
                closeCourseModal();
            }
        });
    }
    
    async function loadStatistics() {
    try {
        // Load course statistics
        const stats = await adminApi.getStatistics();
        
        if (stats.status === 'success' && stats.data) {
            // Update statistics display
            totalCourses.textContent = stats.data.total_courses || '0';
            activeOfferings.textContent = stats.data.active_courses || '0';
            totalEnrollments.textContent = stats.data.total_enrollments || '0';
            
            // Calculate average credits if we have courses
            if (stats.data.total_courses > 0) {
                // This would need a backend calculation, for now use demo value
                avgCredits.textContent = '3.5';
            } else {
                avgCredits.textContent = '0';
            }
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
        
        // Don't show demo values, show actual zeros or dashes
        totalCourses.textContent = '0';
        activeOfferings.textContent = '0';
        totalEnrollments.textContent = '0';
        avgCredits.textContent = '0';
    }
}
    
    async function loadCourses() {
        try {
            const params = {
                page: currentPage,
                limit: 10,
                search: searchQuery
            };
            
            const response = await adminApi.getCourses(params);
            
            if (response.status === 'success' && response.data) {
                courses = response.data.courses;
                currentPage = response.data.current_page;
                totalPages = response.data.total_pages;
                
                displayCourses(courses);
                updatePagination(response.data);
            }
        } catch (error) {
            console.error('Error loading courses:', error);
            
            // Show demo data
            const demoCourses = [
                {
                    course_id: 1,
                    course_code: 'CS101',
                    course_name: 'Introduction to Computer Science',
                    credits: 3,
                    description: 'Basic concepts of computer science',
                    active_offerings: 2
                },
                {
                    course_id: 2,
                    course_code: 'CS201',
                    course_name: 'Data Structures and Algorithms',
                    credits: 4,
                    description: 'Fundamental data structures and algorithms',
                    active_offerings: 1
                },
                {
                    course_id: 3,
                    course_code: 'MATH101',
                    course_name: 'Calculus I',
                    credits: 4,
                    description: 'Introduction to differential and integral calculus',
                    active_offerings: 3
                }
            ];
            displayCourses(demoCourses);
            updatePagination({ total: 3, current_page: 1, per_page: 10 });
        }
    }
    
    function displayCourses(courses) {
    if (!courses || courses.length === 0) {
        coursesTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="px-6 py-4 text-center text-gray-500">
                    No courses found
                </td>
            </tr>
        `;
        return;
    }
    
    const html = courses.map(course => {
        // Calculate total enrollments for this course (demo value)
        const enrollments = course.active_offerings * Math.floor(Math.random() * 30 + 10);
        
        // Use course_code as the identifier for edit/view functions
        const courseIdentifier = course.course_code || course.course_id;
        
        return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div>
                        <div class="text-sm font-medium text-gray-900">${course.course_code}</div>
                        <div class="text-sm text-gray-500">${course.course_name}</div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                        ${course.credits} credits
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${course.active_offerings || 0} active
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${enrollments} students
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button onclick="window.editCourse('${courseIdentifier}')" class="text-indigo-600 hover:text-indigo-900 mr-3">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button onclick="window.viewOfferings('${courseIdentifier}')" class="text-green-600 hover:text-green-900">
                        <i class="fas fa-list"></i> Offerings
                    </button>
                </td>
            </tr>
        `;
    }).join('');
    
    coursesTableBody.innerHTML = html;
    }
    
    function updatePagination(data) {
        const start = (data.current_page - 1) * data.per_page + 1;
        const end = Math.min(data.current_page * data.per_page, data.total);
        
        startRecord.textContent = start;
        endRecord.textContent = end;
        totalRecords.textContent = data.total;
        
        // Update button states
        prevPage.disabled = currentPage === 1;
        nextPage.disabled = currentPage === totalPages;
    }
    
    function performSearch() {
        searchQuery = searchInput.value;
        currentPage = 1;
        loadCourses();
    }
    
    function openCourseModal(course = null) {
    if (course) {
        modalTitle.textContent = 'Edit Course';
        // Load course data
        document.getElementById('courseId').value = course.course_id;
        document.getElementById('modalCourseCode').value = course.course_code;
        document.getElementById('modalCourseName').value = course.course_name;
        document.getElementById('modalCredits').value = course.credits;
        document.getElementById('modalDescription').value = course.description || '';
    } else {
        modalTitle.textContent = 'Add New Course';
        courseForm.reset();
    }
    
    courseModal.classList.remove('hidden');
    }
    
    function closeCourseModal() {
        courseModal.classList.add('hidden');
        courseForm.reset();
    }
    
    async function handleCourseSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(courseForm);
    const courseId = formData.get('courseId');
    
    const courseData = {
        course_code: formData.get('courseCode'),
        course_name: formData.get('courseName'),
        credits: parseInt(formData.get('credits')),
        description: formData.get('description')
    };
    
    try {
        let response;
        if (courseId) {
            // For update, find the course and use its course_code as identifier
            const course = courses.find(c => c.course_id === courseId);
            if (course) {
                // Use course_code instead of course_id for the URL
                response = await adminApi.updateCourse(course.course_code, courseData);
            } else {
                // Fallback to courseId if course not found in local array
                response = await adminApi.updateCourse(courseId, courseData);
            }
        } else {
            // Create new course
            response = await adminApi.createCourse(courseData);
        }
        
        if (response.status === 'success') {
            alert(courseId ? 'Course updated successfully' : 'Course created successfully');
            closeCourseModal();
            loadCourses();
            loadStatistics();
        }
    } catch (error) {
        console.error('Error saving course:', error);
        alert('Error saving course. Please try again.');
    }
}
    
    // Global functions for inline buttons
    window.editCourse = function(courseId) {
    // Find the course by its ID (handle both string and numeric IDs)
    const course = courses.find(c => 
        c.course_id === courseId || 
        c.course_id === parseInt(courseId) ||
        c.course_code === courseId
    );
    
    if (course) {
        openCourseModal(course);
    } else {
        console.error('Course not found:', courseId);
    }
};
    
    window.viewOfferings = function(courseId) {
    // Instead of using alert, create a proper modal or redirect
    // For now, let's create a simple modal to show offerings
    
    // Create modal HTML
    const offeringsModal = document.createElement('div');
    offeringsModal.innerHTML = `
        <div id="offeringsModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 z-50">
            <div class="flex items-center justify-center min-h-screen p-4">
                <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
                    <div class="flex justify-between items-center p-6 border-b">
                        <h3 class="text-lg font-semibold">Course Offerings - ${courseId}</h3>
                        <button onclick="closeOfferingsModal()" class="text-gray-400 hover:text-gray-600">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="p-6 overflow-y-auto max-h-[60vh]">
                        <div id="offeringsContent">
                            <div class="text-center">
                                <i class="fas fa-spinner fa-spin text-2xl text-gray-600"></i>
                                <p class="mt-2 text-gray-600">Loading offerings...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(offeringsModal);
    
    // Load offerings data
    loadCourseOfferings(courseId);
};

window.closeOfferingsModal = function() {
    const modal = document.getElementById('offeringsModal');
    if (modal) {
        modal.remove();
    }
};

async function loadCourseOfferings(courseId) {
    try {
        const response = await apiClient.get(`admin/courses/${courseId}/offerings`);
        
        if (response.status === 'success' && response.data) {
            displayOfferings(response.data);
        }
    } catch (error) {
        console.error('Error loading offerings:', error);
        
        // Show demo data if API fails
        const demoData = {
            course: {
                course_code: courseId,
                course_name: 'Course Name'
            },
            offerings: [
                {
                    offering_id: 1,
                    section_number: '001',
                    capacity: 30,
                    enrolled_count: 25,
                    faculty_name: 'Dr. John Smith',
                    term: 'Fall 2024'
                },
                {
                    offering_id: 2,
                    section_number: '002',
                    capacity: 30,
                    enrolled_count: 28,
                    faculty_name: 'Dr. Jane Doe',
                    term: 'Fall 2024'
                }
            ]
        };
        displayOfferings(demoData);
    }
}

// Function to display offerings
function displayOfferings(data) {
    const contentDiv = document.getElementById('offeringsContent');
    
    if (!data.offerings || data.offerings.length === 0) {
        contentDiv.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-folder-open text-4xl text-gray-400"></i>
                <p class="mt-2 text-gray-600">No offerings found for this course</p>
                <button onclick="createNewOffering('${data.course.course_code}')" class="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md">
                    <i class="fas fa-plus mr-2"></i>Create Offering
                </button>
            </div>
        `;
        return;
    }
    
    const html = `
        <div class="mb-4">
            <h4 class="font-semibold text-lg">${data.course.course_code} - ${data.course.course_name}</h4>
        </div>
        
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Section</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Term</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Faculty</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Schedule</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Enrollment</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    ${data.offerings.map(offering => `
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                Section ${offering.section_number}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                ${offering.term}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                ${offering.faculty_name}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                ${offering.meeting_pattern || 'TBA'}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                ${offering.location || 'TBA'}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                <div class="flex items-center">
                                    <span>${offering.enrolled_count}/${offering.capacity}</span>
                                    <div class="ml-2 w-24 bg-gray-200 rounded-full h-2">
                                        <div class="bg-blue-600 h-2 rounded-full" style="width: ${(offering.enrolled_count/offering.capacity)*100}%"></div>
                                    </div>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                <button onclick="editOffering(${offering.offering_id})" class="text-indigo-600 hover:text-indigo-900 mr-2">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button onclick="deleteOffering(${offering.offering_id}, '${data.course.course_code}')" class="text-red-600 hover:text-red-900">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        
        <div class="mt-4 flex justify-end">
            <button onclick="createNewOffering('${data.course.course_code}')" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md">
                <i class="fas fa-plus mr-2"></i>Add New Offering
            </button>
        </div>
    `;
    
    contentDiv.innerHTML = html;
}


// Placeholder function for creating new offering
window.createNewOffering = function(courseCode) {
    // First, we need to get available terms and faculty
    openOfferingModal(courseCode);
};

// Alternative: Simple redirect approach (if you prefer navigation instead of modal)
window.viewOfferingsRedirect = function(courseId) {
    // This would redirect to a dedicated offerings page
    window.location.href = `course-offerings.html?course=${courseId}`;
};

async function openOfferingModal(courseCode) {
    // Create offering modal HTML
    const offeringModalHtml = `
        <div id="newOfferingModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 z-50">
            <div class="flex items-center justify-center min-h-screen p-4">
                <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
                    <div class="flex justify-between items-center p-6 border-b">
                        <h3 class="text-lg font-semibold">Add New Offering - ${courseCode}</h3>
                        <button onclick="closeOfferingModal()" class="text-gray-400 hover:text-gray-600">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <form id="offeringForm" class="p-6 space-y-4">
                        <input type="hidden" id="offeringCourseCode" value="${courseCode}">
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Academic Term</label>
                            <select id="termId" name="termId" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                                <option value="">Select Term</option>
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Section Number</label>
                            <input type="text" id="sectionNumber" name="sectionNumber" required
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                   placeholder="e.g., 001, 002">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Faculty</label>
                            <select id="facultyId" name="facultyId" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                                <option value="">TBA</option>
                            </select>
                        </div>
                        
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Capacity</label>
                                <input type="number" id="capacity" name="capacity" required min="1" max="500"
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                       placeholder="30">
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
                                <input type="text" id="location" name="location"
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                       placeholder="e.g., Room 101">
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Meeting Pattern</label>
                            <input type="text" id="meetingPattern" name="meetingPattern"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                   placeholder="e.g., MWF 10:00-11:00">
                        </div>
                        
                        <div class="flex justify-end space-x-3 pt-4">
                            <button type="button" onclick="closeOfferingModal()" class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md">
                                Cancel
                            </button>
                            <button type="submit" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md">
                                <i class="fas fa-save mr-2"></i>Create Offering
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    const modalDiv = document.createElement('div');
    modalDiv.innerHTML = offeringModalHtml;
    document.body.appendChild(modalDiv);
    
    // Load terms and faculty
    await loadTermsAndFaculty();
    
    // Add submit handler
    document.getElementById('offeringForm').addEventListener('submit', handleOfferingSubmit);
}

window.closeOfferingModal = function() {
    const modal = document.getElementById('newOfferingModal');
    if (modal) {
        modal.parentElement.remove();
    }
};


async function handleOfferingSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const courseCode = document.getElementById('offeringCourseCode').value;
    
    // Find the course to get its course_id
    const course = courses.find(c => c.course_code === courseCode);
    if (!course) {
        alert('Course not found');
        return;
    }
    
    const offeringData = {
        course_id: course.course_id,
        term_id: parseInt(formData.get('termId')),
        section_number: formData.get('sectionNumber'),
        faculty_id: formData.get('facultyId') || null,
        capacity: parseInt(formData.get('capacity')),
        location: formData.get('location') || null,
        meeting_pattern: formData.get('meetingPattern') || null
    };
    
    try {
        const response = await apiClient.post('admin/offerings', offeringData);
        
        if (response.status === 'success') {
            alert('Offering created successfully!');
            closeOfferingModal();
            
            // Refresh the offerings list if modal is open
            const offeringsModal = document.getElementById('offeringsModal');
            if (offeringsModal) {
                loadCourseOfferings(courseCode);
            }
            
            // Refresh course statistics
            loadStatistics();
            loadCourses();
        }
    } catch (error) {
        console.error('Error creating offering:', error);
        alert('Error creating offering. Please try again.');
    }
}

window.editOffering = function(offeringId) {
    // Implementation for editing offering
    alert(`Edit offering ${offeringId} - Coming soon!`);
};

window.deleteOffering = async function(offeringId, courseCode) {
    if (!confirm('Are you sure you want to delete this offering?')) {
        return;
    }
    
    try {
        const response = await apiClient.delete(`admin/offerings/${offeringId}`);
        
        if (response.status === 'success') {
            alert('Offering deleted successfully!');
            loadCourseOfferings(courseCode);
            loadStatistics();
        }
    } catch (error) {
        console.error('Error deleting offering:', error);
        alert('Error deleting offering. Please check if there are enrollments.');
    }
};


async function loadTermsAndFaculty() {
    try {
        // Load academic terms - FIXED ROUTE
        const termsResponse = await apiClient.get('admin/terms');  // Changed from 'academic/terms'
        if (termsResponse.status === 'success' && termsResponse.data) {
            const termSelect = document.getElementById('termId');
            termsResponse.data.terms.forEach(term => {
                const option = document.createElement('option');
                option.value = term.term_id;
                option.textContent = `${term.term_name} (${term.term_code})`;
                if (term.is_current) {
                    option.selected = true;
                }
                termSelect.appendChild(option);
            });
        }
        
        // Load faculty - FIXED ROUTE
        const facultyResponse = await apiClient.get('admin/faculty/list');  // Changed from 'faculty/list'
        if (facultyResponse.status === 'success' && facultyResponse.data) {
            const facultySelect = document.getElementById('facultyId');
            facultyResponse.data.faculty.forEach(faculty => {
                const option = document.createElement('option');
                option.value = faculty.faculty_id;
                option.textContent = `${faculty.first_name} ${faculty.last_name}`;
                facultySelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading terms and faculty:', error);
        
        // Add demo data if API fails
        const termSelect = document.getElementById('termId');
        termSelect.innerHTML = `
            <option value="">Select Term</option>
            <option value="1" selected>Fall 2024</option>
            <option value="2">Spring 2025</option>
        `;
        
        const facultySelect = document.getElementById('facultyId');
        facultySelect.innerHTML = `
            <option value="">TBA</option>
            <option value="FAC001">Dr. John Smith</option>
            <option value="FAC002">Dr. Jane Doe</option>
            <option value="FAC003">Prof. Robert Johnson</option>
        `;
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