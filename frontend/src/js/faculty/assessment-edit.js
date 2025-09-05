document.addEventListener('DOMContentLoaded', function() {
    console.log('Assessment Edit page loaded');
    
   if (!authApi.isLoggedIn()) {
        window.location.href = '../login.html';
        return;
    }
    
    // Check user role
    if (!authApi.hasRole('faculty')) {
        window.location.href = '../login.html';
        return;
    }
    
    // Get assessment ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const assessmentId = urlParams.get('assessment_id');
    
    if (!assessmentId) {
        alert('No assessment ID provided');
        window.location.href = 'assessments.html';
        return;
    }
    
    // DOM elements
    const loadingIndicator = document.getElementById('loadingIndicator');
    const mainContent = document.getElementById('mainContent');
    const assessmentForm = document.getElementById('assessmentForm');
    
    // Form fields
    const courseDisplay = document.getElementById('courseDisplay');
    const assessmentType = document.getElementById('assessmentType');
    const assessmentTitle = document.getElementById('assessmentTitle');
    const maxScore = document.getElementById('maxScore');
    const dueDate = document.getElementById('dueDate');
    const weight = document.getElementById('weight');
    const description = document.getElementById('description');
    const isPublished = document.getElementById('isPublished');
    
    // Buttons
    const updateBtn = document.getElementById('updateBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const deleteBtn = document.getElementById('deleteBtn');
    
    // Modals
    const successModal = document.getElementById('successModal');
    const errorModal = document.getElementById('errorModal');
    const deleteModal = document.getElementById('deleteModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const errorMessage = document.getElementById('errorMessage');
    const deleteMessage = document.getElementById('deleteMessage');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const closeErrorBtn = document.getElementById('closeErrorBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    
    // Warnings
    const gradedWarning = document.getElementById('gradedWarning');
    const scoreWarning = document.getElementById('scoreWarning');
    
    // Track original data
    let originalAssessmentData = null;
    let hasGradedSubmissions = false;
    
    // Initialize page
    initialize();
    
    async function initialize() {
        try {
            // Load user name
            const userName = localStorage.getItem('userName') || 'Faculty Member';
            document.getElementById('userName').textContent = userName;
            
            // Setup logout
            document.getElementById('logoutBtn').addEventListener('click', function() {
                localStorage.clear();
                window.location.href = '../login.html';
            });
            
            // Load assessment types first
            await loadAssessmentTypes();
            
            // Load assessment data
            await loadAssessmentData();
            
            // Setup event listeners
            setupEventListeners();
            
        } catch (error) {
            console.error('Initialization error:', error);
            showError('Failed to initialize page. Please try again.');
        }
    }
    
    async function loadAssessmentTypes() {
        try {
            const response = await apiClient.get('faculty/assessment-types');
            
            if (response.status === 'success' && response.data.assessment_types) {
                populateAssessmentTypes(response.data.assessment_types);
            } else {
                showError('Failed to load assessment types');
            }
        } catch (error) {
            console.error('Error loading assessment types:', error);
            showError('Failed to load assessment types');
        }
    }
    
    function populateAssessmentTypes(types) {
        assessmentType.innerHTML = '<option value="">Select type...</option>';
        
        types.forEach(type => {
            const option = document.createElement('option');
            option.value = type.type_id;
            option.textContent = type.type_name;
            assessmentType.appendChild(option);
        });
    }
    
    async function loadAssessmentData() {
        try {
            showLoading(true);
            
            const response = await apiClient.get(`faculty/assessments/${assessmentId}`);
            
            if (response.status === 'success' && response.data) {
                originalAssessmentData = response.data;
                populateForm(response.data);
                
                // Check if assessment has graded submissions
                await checkGradedStatus();
                
                showLoading(false);
            } else {
                throw new Error('Failed to load assessment data');
            }
        } catch (error) {
            console.error('Error loading assessment:', error);
            showError('Failed to load assessment. Redirecting...');
            setTimeout(() => {
                window.location.href = 'assessments.html';
            }, 2000);
        }
    }
    
    function populateForm(data) {
        // Display course information
        courseDisplay.textContent = `${data.course_code} - ${data.course_name}`;
        
        // Set form values
        assessmentType.value = data.type_id || '';
        assessmentTitle.value = data.title || '';
        maxScore.value = data.max_score || '';
        weight.value = data.weight || '';
        description.value = data.description || '';
        isPublished.checked = data.is_published || false;
        
        // Handle due date
        if (data.due_date) {
            // Convert ISO string to datetime-local format
            const date = new Date(data.due_date);
            const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
            dueDate.value = localDate.toISOString().slice(0, 16);
        }
    }
    
    async function checkGradedStatus() {
        try {
            // Get assessment statistics to check if it has been graded
            const response = await apiClient.get(`faculty/assessments/${assessmentId}/statistics`);
            
            if (response.status === 'success' && response.data && response.data.statistics) {
                hasGradedSubmissions = response.data.statistics.graded_count > 0;
                
                if (hasGradedSubmissions) {
                    gradedWarning.classList.remove('hidden');
                    // Show warning when max score is changed
                    maxScore.addEventListener('input', () => {
                        if (parseFloat(maxScore.value) !== originalAssessmentData.max_score) {
                            scoreWarning.classList.remove('hidden');
                        } else {
                            scoreWarning.classList.add('hidden');
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error checking graded status:', error);
            // Continue without showing warning
        }
    }
    
    function setupEventListeners() {
        // Form submission
        assessmentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            updateAssessment();
        });
        
        // Cancel button
        cancelBtn.addEventListener('click', function() {
            if (hasUnsavedChanges() && !confirm('You have unsaved changes. Are you sure you want to cancel?')) {
                return;
            }
            window.location.href = 'assessments.html';
        });
        
        // Delete button
        deleteBtn.addEventListener('click', function() {
            if (hasGradedSubmissions) {
                deleteMessage.textContent = 'This assessment has graded submissions and cannot be deleted.';
                confirmDeleteBtn.style.display = 'none';
            } else {
                deleteMessage.textContent = 'This action cannot be undone. Are you sure you want to delete this assessment?';
                confirmDeleteBtn.style.display = 'inline-block';
            }
            deleteModal.classList.remove('hidden');
        });
        
        // Modal close buttons
        closeModalBtn.addEventListener('click', function() {
            successModal.classList.add('hidden');
            window.location.href = 'assessments.html';
        });
        
        closeErrorBtn.addEventListener('click', function() {
            errorModal.classList.add('hidden');
        });
        
        cancelDeleteBtn.addEventListener('click', function() {
            deleteModal.classList.add('hidden');
        });
        
        confirmDeleteBtn.addEventListener('click', function() {
            deleteAssessment();
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
    
    function hasUnsavedChanges() {
        if (!originalAssessmentData) return false;
        
        const currentData = getFormData();
        
        // Compare each field
        return currentData.type_id !== originalAssessmentData.type_id ||
               currentData.title !== originalAssessmentData.title ||
               currentData.max_score !== originalAssessmentData.max_score ||
               currentData.weight !== (originalAssessmentData.weight || null) ||
               currentData.description !== (originalAssessmentData.description || null) ||
               currentData.due_date !== formatDueDate(originalAssessmentData.due_date) ||
               currentData.is_published !== originalAssessmentData.is_published;
    }
    
    function getFormData() {
        const dueDateValue = dueDate.value;
        const formattedDueDate = dueDateValue ? new Date(dueDateValue).toISOString() : null;
        
        return {
            type_id: parseInt(assessmentType.value),
            title: assessmentTitle.value.trim(),
            max_score: parseFloat(maxScore.value),
            due_date: formattedDueDate,
            weight: weight.value ? parseFloat(weight.value) : null,
            description: description.value.trim() || null,
            is_published: isPublished.checked
        };
    }
    
    function formatDueDate(dateString) {
        if (!dateString) return null;
        return new Date(dateString).toISOString();
    }
    
    async function updateAssessment() {
        try {
            // Validate form
            if (!assessmentForm.checkValidity()) {
                assessmentForm.reportValidity();
                return;
            }
            
            // Disable submit button
            updateBtn.disabled = true;
            updateBtn.textContent = 'Updating...';
            
            // Get form data
            const formData = getFormData();
            
            // Warn about max score change if needed
            if (hasGradedSubmissions && formData.max_score !== originalAssessmentData.max_score) {
                if (!confirm('Changing the maximum score will recalculate all existing grade percentages. Are you sure you want to continue?')) {
                    updateBtn.disabled = false;
                    updateBtn.textContent = 'Update Assessment';
                    return;
                }
            }
            
            console.log('Updating assessment with data:', formData);
            
            // Submit to API
            const response = await apiClient.put(`faculty/assessments/${assessmentId}`, formData);
            console.log('Update response:', response);
            
            if (response.status === 'success') {
                // Show success modal
                modalTitle.textContent = 'Assessment Updated!';
                modalMessage.textContent = `"${formData.title}" has been updated successfully.`;
                successModal.classList.remove('hidden');
            } else {
                showError(response.message || 'Failed to update assessment');
            }
            
        } catch (error) {
            console.error('Error updating assessment:', error);
            
            if (error.response && error.response.data && error.response.data.message) {
                showError(error.response.data.message);
            } else if (error.response && error.response.status === 401) {
                showError('Session expired. Please log in again.');
                setTimeout(() => {
                    window.location.href = '../login.html';
                }, 2000);
            } else {
                showError('Failed to update assessment. Please try again.');
            }
        } finally {
            // Re-enable submit button
            updateBtn.disabled = false;
            updateBtn.textContent = 'Update Assessment';
        }
    }
    
    async function deleteAssessment() {
        try {
            deleteModal.classList.add('hidden');
            
            const response = await apiClient.delete(`faculty/assessments/${assessmentId}`);
            
            if (response.status === 'success') {
                modalTitle.textContent = 'Assessment Deleted';
                modalMessage.textContent = 'The assessment has been deleted successfully.';
                successModal.classList.remove('hidden');
            } else {
                showError(response.message || 'Failed to delete assessment');
            }
            
        } catch (error) {
            console.error('Error deleting assessment:', error);
            showError('Failed to delete assessment. It may have submissions.');
        }
    }
    
    function showLoading(show) {
        if (show) {
            loadingIndicator.classList.remove('hidden');
            mainContent.classList.add('hidden');
        } else {
            loadingIndicator.classList.add('hidden');
            mainContent.classList.remove('hidden');
        }
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorModal.classList.remove('hidden');
    }
});