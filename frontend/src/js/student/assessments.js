document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    if (!authApi.isLoggedIn() || !authApi.hasRole('student')) {
        window.location.href = '../login.html';
        return;
    }

    // DOM elements
    const courseFilter = document.getElementById('courseFilter');
    const typeFilter = document.getElementById('typeFilter');
    const statusFilter = document.getElementById('statusFilter');
    const applyFilters = document.getElementById('applyFilters');
    const assessmentsList = document.getElementById('assessmentsList');
    const loadingState = document.getElementById('loadingState');
    const assessmentsTable = document.getElementById('assessmentsTable');
    const noDataState = document.getElementById('noDataState');
    const logoutBtn = document.getElementById('logoutBtn');

    // Summary counts
    const totalCount = document.getElementById('totalCount');
    const pendingCount = document.getElementById('pendingCount');
    const submittedCount = document.getElementById('submittedCount');
    const gradedCount = document.getElementById('gradedCount');

    // State
    let allAssessments = [];
    let courses = new Set();

    // Initialize
    initialize();

    async function initialize() {
        setupEventListeners();
        await loadAssessments();
        populateCourseFilter();
        applyCurrentFilters();
    }

    function setupEventListeners() {
        applyFilters.addEventListener('click', applyCurrentFilters);
        logoutBtn.addEventListener('click', () => authApi.logout());
        
        // Enter key on filters
        [courseFilter, typeFilter, statusFilter].forEach(filter => {
            filter.addEventListener('change', applyCurrentFilters);
        });
    }

    async function loadAssessments() {
        try {
            showLoading(true);
            
            const response = await apiClient.get('student/assessments/all');
            console.log('Response from API:', response);
            
            if (response.status === 'success') {
                // Flatten the course structure into assessment list
                allAssessments = [];
                response.data.courses.forEach(course => {
                    course.assessments.forEach(assessment => {
                        console.log('Assessment:', assessment); // ADD THIS
                        allAssessments.push({
                            ...assessment,
                            course_code: course.course_code,
                            course_name: course.course_name
                        });
                        courses.add(`${course.course_code}|${course.course_name}`);
                    });
                });
                
                showLoading(false);
            } else {
                throw new Error('Failed to load assessments');
            }
        } catch (error) {
            console.error('Error loading assessments:', error);
            showLoading(false);
            showNoData();
        }
    }

    function populateCourseFilter() {
        courseFilter.innerHTML = '<option value="">All Courses</option>';
        
        Array.from(courses).sort().forEach(courseStr => {
            const [code, name] = courseStr.split('|');
            const option = document.createElement('option');
            option.value = code;
            option.textContent = `${code} - ${name}`;
            courseFilter.appendChild(option);
        });
    }

    function applyCurrentFilters() {
        const courseValue = courseFilter.value;
        const typeValue = typeFilter.value;
        const statusValue = statusFilter.value;

        let filtered = allAssessments;

        // Apply course filter
        if (courseValue) {
            filtered = filtered.filter(a => a.course_code === courseValue);
        }

        // Apply type filter
        if (typeValue) {
            filtered = filtered.filter(a => a.type_name === typeValue);
        }

        // Apply status filter
        if (statusValue) {
            filtered = filtered.filter(a => {
                const status = getAssessmentStatus(a);
                return status === statusValue;
            });
        }

        displayAssessments(filtered);
        updateCounts(filtered);
    }

    function getAssessmentStatus(assessment) {
        if (assessment.score !== null) {
            return 'graded';
        } else if (assessment.submission_date) {
            return 'submitted';
        } else if (assessment.due_date && new Date(assessment.due_date) < new Date()) {
            return 'overdue';
        } else {
            return 'not_submitted';
        }
    }

    function displayAssessments(assessments) {
        if (assessments.length === 0) {
            showNoData();
            return;
        }

        assessmentsList.innerHTML = assessments.map(assessment => {
            const status = getAssessmentStatus(assessment);
            const statusBadge = getStatusBadge(status);
            const actionButton = getActionButton(assessment, status);
            const dueDate = assessment.due_date ? new Date(assessment.due_date) : null;
            
            return `
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm font-medium text-gray-900">${assessment.course_code}</div>
                        <div class="text-sm text-gray-500">${assessment.course_name}</div>
                    </td>
                    <td class="px-6 py-4">
                        <div class="text-sm font-medium text-gray-900">${assessment.title}</div>
                        ${assessment.description ? `<div class="text-xs text-gray-500 mt-1">${assessment.description.substring(0, 50)}...</div>` : ''}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="text-sm text-gray-900">${assessment.type_name}</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">
                            ${dueDate ? dueDate.toLocaleDateString() : 'No due date'}
                        </div>
                        ${dueDate ? `<div class="text-xs text-gray-500">${dueDate.toLocaleTimeString()}</div>` : ''}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        ${statusBadge}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        ${assessment.score !== null ? 
                            `<div class="text-sm font-medium">${assessment.score}/${assessment.max_score}</div>
                             <div class="text-xs text-gray-500">${assessment.percentage.toFixed(1)}%</div>` : 
                            '<span class="text-sm text-gray-500">-</span>'}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        ${actionButton}
                    </td>
                </tr>
            `;
        }).join('');

        assessmentsTable.classList.remove('hidden');
        noDataState.classList.add('hidden');
    }

    function getStatusBadge(status) {
        const badges = {
            'not_submitted': '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Pending</span>',
            'overdue': '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Overdue</span>',
            'submitted': '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">Submitted</span>',
            'graded': '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Graded</span>'
        };
        return badges[status] || '';
    }

    function getActionButton(assessment, status) {
        if (status === 'graded') {
            return `<a href="assessment-submit.html?assessment_id=${assessment.assessment_id}" 
                       class="text-gray-600 hover:text-gray-900">View Grade</a>`;
        } else if (status === 'submitted') {
            return `<a href="assessment-submit.html?assessment_id=${assessment.assessment_id}" 
                       class="text-blue-600 hover:text-blue-900">View/Edit</a>`;
        } else {
            return `<a href="assessment-submit.html?assessment_id=${assessment.assessment_id}" 
                       class="bg-blue-600 text-white px-3 py-1 rounded-md text-xs hover:bg-blue-700">Submit</a>`;
        }
    }

    function updateCounts(assessments) {
        const counts = {
            total: assessments.length,
            pending: 0,
            submitted: 0,
            graded: 0
        };

        assessments.forEach(assessment => {
            const status = getAssessmentStatus(assessment);
            if (status === 'graded') {
                counts.graded++;
            } else if (status === 'submitted') {
                counts.submitted++;
            } else {
                counts.pending++;
            }
        });

        totalCount.textContent = counts.total;
        pendingCount.textContent = counts.pending;
        submittedCount.textContent = counts.submitted;
        gradedCount.textContent = counts.graded;
    }

    function showLoading(show) {
        if (show) {
            loadingState.classList.remove('hidden');
            assessmentsTable.classList.add('hidden');
            noDataState.classList.add('hidden');
        } else {
            loadingState.classList.add('hidden');
        }
    }

    function showNoData() {
        loadingState.classList.add('hidden');
        assessmentsTable.classList.add('hidden');
        noDataState.classList.remove('hidden');
    }
});