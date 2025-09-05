document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    const assessmentForm = document.getElementById('assessmentForm');
    const courseSelect = document.getElementById('courseSelect');
    const assessmentType = document.getElementById('assessmentType');
    const assessmentTitle = document.getElementById('assessmentTitle');
    const maxScore = document.getElementById('maxScore');
    const dueDate = document.getElementById('dueDate');
    const weight = document.getElementById('weight');
    const description = document.getElementById('description');
    const cancelBtn = document.getElementById('cancelBtn');
    const createBtn = document.getElementById('createBtn');
    
    // Modals
    const successModal = document.getElementById('successModal');
    const errorModal = document.getElementById('errorModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const errorMessage = document.getElementById('errorMessage');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const closeErrorBtn = document.getElementById('closeErrorBtn');
    
    // Initialize
    init();
    
    function init() {
        // Check authentication
        if (!authApi.isLoggedIn()) {
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
        loadAssessmentTypes();
        
        // Set up event listeners
        setupEventListeners();
        
        // Set default due date to tomorrow at 11:59 PM
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 7); // Default to 1 week from now
        tomorrow.setHours(23, 59, 0, 0);
        dueDate.value = tomorrow.toISOString().slice(0, 16);
    }
    
    function setupEventListeners() {
        // Logout
        logoutBtn.addEventListener('click', function() {
            authApi.logout();
        });
        
        // Cancel button
        cancelBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to cancel? Any unsaved changes will be lost.')) {
                window.location.href = 'assessments.html';
            }
        });
        
        // Form submission
        assessmentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            createAssessment();
        });
        
        // Modal close buttons
        closeModalBtn.addEventListener('click', function() {
            successModal.classList.add('hidden');
            // Redirect to assessments page
            window.location.href = 'assessments.html';
        });
        
        closeErrorBtn.addEventListener('click', function() {
            errorModal.classList.add('hidden');
        });
        
        // Assessment type change - update title placeholder
        assessmentType.addEventListener('change', function() {
            const selectedType = assessmentType.options[assessmentType.selectedIndex];
            if (selectedType.value) {
                const typeName = selectedType.text;
                assessmentTitle.placeholder = `e.g., ${typeName} 1, ${typeName} - Chapter 5`;
            }
        });
        
        // Real-time validation
        setupValidation();
    }
    
    function setupValidation() {
        // Title validation
        assessmentTitle.addEventListener('input', function() {
            if (this.value.length > 255) {
                this.setCustomValidity('Title must be 255 characters or less');
            } else {
                this.setCustomValidity('');
            }
        });
        
        // Max score validation
        maxScore.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value <= 0) {
                this.setCustomValidity('Maximum score must be greater than 0');
            } else if (value > 1000) {
                this.setCustomValidity('Maximum score cannot exceed 1000');
            } else {
                this.setCustomValidity('');
            }
        });
        
        // Weight validation
        weight.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value < 0) {
                this.setCustomValidity('Weight cannot be negative');
            } else if (value > 100) {
                this.setCustomValidity('Weight cannot exceed 100%');
            } else {
                this.setCustomValidity('');
            }
        });
    }
    
    async function loadFacultyCourses() {
        try {
            console.log('Loading faculty courses...');
            const response = await apiClient.get('faculty/courses');
            console.log('Courses response:', response);
            
            if (response.status === 'success' && response.data.courses) {
                populateCourseSelect(response.data.courses);
            } else {
                showError('Failed to load courses');
            }
        } catch (error) {
            console.error('Error loading courses:', error);
            showError('Failed to load courses. Please refresh the page.');
        }
    }
    
    async function loadAssessmentTypes() {
        try {
            console.log('Loading assessment types...');
            const response = await apiClient.get('faculty/assessment-types');
            console.log('Assessment types response:', response);
            
            if (response.status === 'success' && response.data.assessment_types) {
                populateAssessmentTypes(response.data.assessment_types);
            } else {
                showError('Failed to load assessment types');
            }
        } catch (error) {
            console.error('Error loading assessment types:', error);
            showError('Failed to load assessment types. Please refresh the page.');
        }
    }
    
    function populateCourseSelect(courses) {
        courseSelect.innerHTML = '<option value="">Select a course...</option>';
        
        if (!courses || courses.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No courses available';
            option.disabled = true;
            courseSelect.appendChild(option);
            return;
        }
        
        courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course.offering_id;
            option.textContent = `${course.course_code} - ${course.course_name} (Section ${course.section})`;
            courseSelect.appendChild(option);
        });
        
        console.log(`Loaded ${courses.length} courses`);
    }
    
    function populateAssessmentTypes(types) {
        assessmentType.innerHTML = '<option value="">Select type...</option>';
        
        if (!types || types.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No assessment types available';
            option.disabled = true;
            assessmentType.appendChild(option);
            return;
        }
        
        types.forEach(type => {
            const option = document.createElement('option');
            option.value = type.type_id;
            option.textContent = type.type_name;
            option.dataset.defaultWeight = type.weight_percentage;
            assessmentType.appendChild(option);
        });
        
        // Auto-fill weight when type is selected
        assessmentType.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            if (selectedOption.dataset.defaultWeight && !weight.value) {
                weight.value = selectedOption.dataset.defaultWeight;
            }
        });
        
        console.log(`Loaded ${types.length} assessment types`);
    }
    
    async function createAssessment() {
        // Validate form
        if (!assessmentForm.checkValidity()) {
            assessmentForm.reportValidity();
            return;
        }
        
        // Disable submit button
        createBtn.disabled = true;
        createBtn.textContent = 'Creating...';
        
        try {
            // Prepare data
            const formData = {
                offering_id: parseInt(courseSelect.value),
                type_id: parseInt(assessmentType.value),
                title: assessmentTitle.value.trim(),
                max_score: parseFloat(maxScore.value),
                due_date: dueDate.value || null,
                weight: weight.value ? parseFloat(weight.value) : null,
                description: description.value.trim() || null
            };
            
            console.log('Creating assessment with data:', formData);
            
            // Submit to API
            const response = await apiClient.post('faculty/assessments', formData);
            console.log('Create response:', response);
            
            if (response.status === 'success') {
                // Show success modal
                modalTitle.textContent = 'Assessment Created!';
                modalMessage.textContent = `"${formData.title}" has been created successfully. Students can now see this assessment in their course materials.`;
                successModal.classList.remove('hidden');
            } else {
                showError(response.message || 'Failed to create assessment');
            }
            
        } catch (error) {
            console.error('Error creating assessment:', error);
            
            if (error.response && error.response.data && error.response.data.message) {
                showError(error.response.data.message);
            } else if (error.response && error.response.status === 401) {
                showError('Session expired. Please log in again.');
                setTimeout(() => {
                    window.location.href = '../login.html';
                }, 2000);
            } else {
                showError('Failed to create assessment. Please try again.');
            }
        } finally {
            // Re-enable submit button
            createBtn.disabled = false;
            createBtn.textContent = 'Create Assessment';
        }
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorModal.classList.remove('hidden');
    }
    
    // URL parameter handling for pre-selected course
    function checkUrlParameters() {
        const urlParams = new URLSearchParams(window.location.search);
        const courseId = urlParams.get('course');
        
        if (courseId) {
            // Wait for courses to load, then select the specified course
            const checkAndSelect = () => {
                if (courseSelect.options.length > 1) {
                    courseSelect.value = courseId;
                } else {
                    setTimeout(checkAndSelect, 100);
                }
            };
            checkAndSelect();
        }
    }
    
    // Check for URL parameters after initialization
    setTimeout(checkUrlParameters, 500);
});