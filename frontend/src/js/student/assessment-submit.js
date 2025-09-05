document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    if (!authApi.isLoggedIn() || !authApi.hasRole('student')) {
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
    const assessmentTitle = document.getElementById('assessmentTitle');
    const courseName = document.getElementById('courseName');
    const assessmentType = document.getElementById('assessmentType');
    const dueDate = document.getElementById('dueDate');
    const maxScore = document.getElementById('maxScore');
    const weight = document.getElementById('weight');
    const status = document.getElementById('status');
    const description = document.getElementById('description');
    const descriptionSection = document.getElementById('descriptionSection');
    
    // Submission elements
    const submissionStatus = document.getElementById('submissionStatus');
    const submissionForm = document.getElementById('submissionForm');
    const assessmentSubmitForm = document.getElementById('assessmentSubmitForm');
    const submissionText = document.getElementById('submissionText');
    const submitBtn = document.getElementById('submitBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    
    // Previous submission elements
    const previousSubmission = document.getElementById('previousSubmission');
    const previousSubmissionContent = document.getElementById('previousSubmissionContent');
    const feedbackSection = document.getElementById('feedbackSection');
    const feedback = document.getElementById('feedback');
    
    // Modal elements
    const successModal = document.getElementById('successModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    
    // State
    let assessmentData = null;
    let isSubmitted = false;
    let selectedFile = null;
    
    // Create file input element
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.pdf,.doc,.docx,.txt,.zip,.jpg,.jpeg,.png';
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);
    
    // Initialize
    initialize();
    
    async function initialize() {
        try {
            await loadAssessmentDetails();
            setupEventListeners();
            setupFileUpload();
            updateFileUploadSection();
        } catch (error) {
            console.error('Initialization error:', error);
            showError('Failed to initialize page');
        }
    }
    
    async function loadAssessmentDetails() {
    try {
        showLoading(true);
        
        console.log('Loading assessment with ID:', assessmentId);
        const response = await apiClient.get(`student/assessments/${assessmentId}`);
        console.log('API Response:', response);
        
        if (response.status === 'success' && response.data) {
            assessmentData = response.data;
            console.log('Assessment Data:', assessmentData);
            
            // Track assessment view AFTER data is loaded
            if (typeof activityTracker !== 'undefined' && assessmentData) {
                activityTracker.trackAssessmentView(assessmentId, assessmentData.title);
            }
            
            displayAssessmentInfo();
            checkSubmissionStatus();
            showLoading(false);
        } else {
            console.log('No data in response');
            throw new Error('Failed to load assessment details');
        }
    } catch (error) {
        console.error('Error loading assessment:', error);
        showError('Failed to load assessment. Redirecting...');
        setTimeout(() => {
            window.location.href = 'assessments.html';
        }, 2000);
    }
}
    
    function displayAssessmentInfo() {
        assessmentTitle.textContent = assessmentData.title;
        courseName.textContent = `${assessmentData.course_code} - ${assessmentData.course_name}`;
        assessmentType.textContent = assessmentData.type_name;
        maxScore.textContent = `${assessmentData.max_score} points`;
        weight.textContent = assessmentData.weight ? `${assessmentData.weight}%` : 'Not specified';
        
        // Format due date
        if (assessmentData.due_date) {
            const date = new Date(assessmentData.due_date);
            dueDate.textContent = `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
            
            // Check if overdue
            if (new Date() > date && assessmentData.status !== 'graded') {
                dueDate.classList.add('text-red-600', 'font-semibold');
                dueDate.innerHTML += ' <span class="text-xs">(Overdue)</span>';
            }
        } else {
            dueDate.textContent = 'No due date';
        }
        
        // Display description if exists
        if (assessmentData.description) {
            description.textContent = assessmentData.description;
            descriptionSection.classList.remove('hidden');
        }
        
        // Display status
        updateStatus();
    }
    
    function updateStatus() {
        status.textContent = assessmentData.status === 'graded' ? 'Graded' : 
                           assessmentData.submission_date ? 'Submitted' : 'Not Submitted';
        
        if (assessmentData.status === 'graded') {
            status.className = 'font-medium text-green-600';
        } else if (assessmentData.submission_date) {
            status.className = 'font-medium text-blue-600';
        } else {
            status.className = 'font-medium text-yellow-600';
        }
    }
    
    function checkSubmissionStatus() {
        isSubmitted = !!assessmentData.submission_date;
        
        if (isSubmitted) {
            // Show submission status
            submissionStatus.classList.remove('hidden');
            document.getElementById('submissionDate').textContent = 
                new Date(assessmentData.submission_date).toLocaleString();
            
            // Show grade if available
            if (assessmentData.score !== null) {
                document.getElementById('gradeInfo').classList.remove('hidden');
                document.getElementById('grade').textContent = 
                    `${assessmentData.score}/${assessmentData.max_score} (${assessmentData.percentage.toFixed(1)}%)`;
            }
            
            // Show previous submission
            if (assessmentData.submission_text) {
                previousSubmission.classList.remove('hidden');
                previousSubmissionContent.innerHTML = `
                    <div class="bg-gray-50 p-4 rounded-md">
                        <pre class="whitespace-pre-wrap text-sm">${escapeHtml(assessmentData.submission_text)}</pre>
                    </div>
                `;
            }
            
            // Show submitted file info if exists
            if (assessmentData.file_name) {
                const fileInfoHtml = `
                    <div class="mt-3 p-3 bg-blue-50 rounded-md">
                        <p class="text-sm font-medium text-blue-900">Attached File:</p>
                        <div class="flex items-center mt-2">
                            <svg class="h-5 w-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z" clip-rule="evenodd"></path>
                            </svg>
                            <span class="text-sm text-blue-800">${assessmentData.file_name}</span>
                            <a href="#" onclick="downloadSubmittedFile(event)" class="ml-3 text-xs text-blue-600 hover:text-blue-800 underline">Download</a>
                        </div>
                    </div>
                `;
                previousSubmissionContent.innerHTML += fileInfoHtml;
            }
            
            // Show feedback if available
            if (assessmentData.feedback) {
                feedbackSection.classList.remove('hidden');
                feedback.textContent = assessmentData.feedback;
            }
            
            // Disable form if already graded
            if (assessmentData.status === 'graded') {
                submissionForm.classList.add('opacity-50');
                submissionText.disabled = true;
                submitBtn.disabled = true;
                submitBtn.textContent = 'Already Graded';
                // Disable file upload
                const fileUploadArea = document.getElementById('fileUploadArea');
                if (fileUploadArea) {
                    fileUploadArea.classList.add('cursor-not-allowed', 'opacity-50');
                    fileUploadArea.onclick = null;
                }
            } else {
                // Allow resubmission if not graded
                submitBtn.textContent = 'Resubmit Assessment';
            }
        }
    }
    
    function updateFileUploadSection() {
        // Find the existing file upload div
        const fileUploadDiv = document.querySelector('.border-2.border-dashed');
        if (fileUploadDiv && fileUploadDiv.parentElement) {
            fileUploadDiv.parentElement.innerHTML = `
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    File Upload (Optional)
                </label>
                <div id="fileUploadArea" class="border-2 border-dashed border-gray-300 rounded-md p-6 text-center cursor-pointer hover:border-gray-400 transition-colors">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                    </svg>
                    <p class="mt-2 text-sm text-gray-600">Click to upload or drag and drop</p>
                    <p class="text-xs text-gray-500">PDF, DOC, DOCX, TXT, ZIP, JPG, PNG (Max 10MB)</p>
                </div>
                <div id="selectedFileInfo" class="hidden mt-3 p-3 bg-gray-50 rounded-md flex items-center justify-between">
                    <div class="flex items-center">
                        <svg class="h-5 w-5 text-gray-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z" clip-rule="evenodd"></path>
                        </svg>
                        <span id="selectedFileName" class="text-sm text-gray-700"></span>
                        <span id="selectedFileSize" class="text-xs text-gray-500 ml-2"></span>
                    </div>
                    <button type="button" id="removeFileBtn" class="text-red-600 hover:text-red-800">
                        <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                        </svg>
                    </button>
                </div>
            `;
        }
    }
    
    function setupEventListeners() {
        // Form submission
        assessmentSubmitForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitAssessment();
        });
        
        // Cancel button
        cancelBtn.addEventListener('click', function() {
            const hasChanges = submissionText.value.trim() || selectedFile;
            if (hasChanges && !confirm('You have unsaved changes. Are you sure you want to cancel?')) {
                return;
            }
            window.location.href = 'assessments.html';
        });
        
        // Modal close
        closeModalBtn.addEventListener('click', function() {
            window.location.href = 'assessments.html';
        });
    }
    
    function setupFileUpload() {
        const fileUploadArea = document.getElementById('fileUploadArea');
        const selectedFileInfo = document.getElementById('selectedFileInfo');
        const selectedFileName = document.getElementById('selectedFileName');
        const selectedFileSize = document.getElementById('selectedFileSize');
        const removeFileBtn = document.getElementById('removeFileBtn');
        
        if (!fileUploadArea) return;
        
        // Only setup if not already graded
        if (assessmentData && assessmentData.status === 'graded') {
            return;
        }
        
        // Click to upload
        fileUploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Drag and drop
        fileUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUploadArea.classList.add('border-blue-500', 'bg-blue-50');
        });
        
        fileUploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            fileUploadArea.classList.remove('border-blue-500', 'bg-blue-50');
        });
        
        fileUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUploadArea.classList.remove('border-blue-500', 'bg-blue-50');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });
        
        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
        
        // Remove file
        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', () => {
                selectedFile = null;
                fileInput.value = '';
                selectedFileInfo.classList.add('hidden');
                fileUploadArea.classList.remove('hidden');
            });
        }
    }
    
    function handleFileSelect(file) {
        // Validate file
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedExtensions = ['pdf', 'doc', 'docx', 'txt', 'zip', 'jpg', 'jpeg', 'png'];
        const fileExtension = file.name.split('.').pop().toLowerCase();
        
        if (file.size > maxSize) {
            alert('File is too large. Maximum size is 10MB.');
            return;
        }
        
        if (!allowedExtensions.includes(fileExtension)) {
            alert('Invalid file type. Please upload PDF, DOC, DOCX, TXT, ZIP, JPG, or PNG files.');
            return;
        }
        
        selectedFile = file;
        document.getElementById('selectedFileName').textContent = file.name;
        document.getElementById('selectedFileSize').textContent = `(${formatFileSize(file.size)})`;
        document.getElementById('selectedFileInfo').classList.remove('hidden');
        document.getElementById('fileUploadArea').classList.add('hidden');
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async function submitAssessment() {
        const text = submissionText.value.trim();
        
        if (!text && !selectedFile) {
            alert('Please enter submission text or upload a file');
            return;
        }
        
        // Confirm submission
        const confirmMsg = isSubmitted ? 
            'Are you sure you want to resubmit? This will replace your previous submission.' :
            'Are you sure you want to submit? You may not be able to change it after grading.';
            
        if (!confirm(confirmMsg)) {
            return;
        }
        
        try {
            // Disable submit button
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
            
            let response;
            
            if (selectedFile) {
                // Use FormData for file upload
                const formData = new FormData();
                if (text) {
                    formData.append('submission_text', text);
                }
                formData.append('file', selectedFile);
                
                // Check if apiClient has postFormData method, if not, use axios directly
                if (typeof apiClient.postFormData === 'function') {
                    response = await apiClient.postFormData(`student/assessments/${assessmentId}/submit`, formData);
                } else {
                    // Fallback to direct axios call
                    const token = authApi.getToken();
                    const axiosResponse = await axios.post(
                        `${apiClient.baseURL}/student/assessments/${assessmentId}/submit`,
                        formData,
                        {
                            headers: {
                                'Authorization': `Bearer ${token}`,
                                'Content-Type': 'multipart/form-data'
                            }
                        }
                    );
                    response = axiosResponse.data;
                }
            } else {
                // JSON submission for text only
                response = await apiClient.post(`student/assessments/${assessmentId}/submit`, {
                    submission_text: text
                });
            }
            
            if (response.status === 'success') {
                // Show success modal
                successModal.classList.remove('hidden');
            } else {
                showError(response.message || 'Failed to submit assessment');
            }
            
        } catch (error) {
            console.error('Error submitting assessment:', error);
            
            if (error.response && error.response.status === 401) {
                showError('Session expired. Please log in again.');
                setTimeout(() => {
                    authApi.logout();
                }, 2000);
            } else {
                showError('Failed to submit assessment. Please try again.');
            }
        } finally {
            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.textContent = isSubmitted ? 'Resubmit Assessment' : 'Submit Assessment';
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
        console.error(message);
        alert(message);
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Make downloadSubmittedFile available globally
    window.downloadSubmittedFile = async function(event) {
        event.preventDefault();
        try {
            window.location.href = `${apiClient.baseURL}/student/assessments/${assessmentId}/download`;
        } catch (error) {
            console.error('Error downloading file:', error);
            showError('Failed to download file');
        }
    };
});