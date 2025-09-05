let assessmentId;
let currentSubmission;
let assessmentData;

document.addEventListener('DOMContentLoaded', function() {
    assessmentId = getUrlParameter('id');
    if (!assessmentId) {
        window.location.href = 'assessments.html';
        return;
    }
    
    loadSubmissions();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('logoutBtn').addEventListener('click', logout);
}

async function loadSubmissions() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/api/faculty/assessments/${assessmentId}/submissions`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            assessmentData = data.data.assessment;
            displayAssessmentInfo(assessmentData);
            displaySubmissions(data.data.submissions);
            updateStats(data.data.submissions);
        } else {
            showError('Failed to load submissions');
        }
    } catch (error) {
        console.error('Error loading submissions:', error);
        showError('Error loading submissions');
    }
}

function displayAssessmentInfo(assessment) {
    const info = `${assessment.assessment_type.type_name}: ${assessment.title} (Max Score: ${assessment.max_score})`;
    document.getElementById('assessmentInfo').textContent = info;
}

function updateStats(submissions) {
    const total = submissions.length;
    const graded = submissions.filter(s => s.score !== null).length;
    const pending = total - graded;
    
    document.getElementById('totalStudents').textContent = total;
    document.getElementById('submittedCount').textContent = total;
    document.getElementById('gradedCount').textContent = graded;
    document.getElementById('pendingCount').textContent = pending;
}

function displaySubmissions(submissions) {
    const tbody = document.getElementById('submissionsTableBody');
    tbody.innerHTML = '';
    
    if (submissions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                    No submissions yet
                </td>
            </tr>
        `;
        return;
    }
    
    submissions.forEach(submission => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">${submission.student_name}</div>
                <div class="text-sm text-gray-500">${submission.student_id}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatDateTime(submission.submission_date)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${getSubmissionTypeBadge(submission)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${getStatusBadge(submission)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${submission.score !== null ? `${submission.score}/${submission.max_score}` : '-'}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button onclick="viewSubmission(${submission.submission_id})" 
                        class="text-blue-600 hover:text-blue-900 mr-3">
                    View
                </button>
                ${submission.has_file ? `
                    <button onclick="downloadSubmission(${submission.submission_id})" 
                            class="text-green-600 hover:text-green-900 mr-3">
                        Download
                    </button>
                ` : ''}
            </td>
        `;
        tbody.appendChild(row);
    });
}

function getSubmissionTypeBadge(submission) {
    const badges = {
        'both': '<span class="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800">File + Text</span>',
        'file': '<span class="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">File</span>',
        'text': '<span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">Text</span>'
    };
    return badges[submission.submission_type] || '<span class="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">Unknown</span>';
}

function getStatusBadge(submission) {
    if (submission.score !== null) {
        return '<span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">Graded</span>';
    } else if (submission.is_late) {
        return '<span class="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">Late</span>';
    } else {
        return '<span class="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">Pending</span>';
    }
}

async function viewSubmission(submissionId) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/api/faculty/submissions/${submissionId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            currentSubmission = data.data;
            showSubmissionModal(currentSubmission);
        } else {
            showError('Failed to load submission details');
        }
    } catch (error) {
        console.error('Error loading submission:', error);
        showError('Error loading submission details');
    }
}

function showSubmissionModal(submission) {
    const content = document.getElementById('submissionContent');
    content.innerHTML = `
        <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <p class="text-sm font-medium text-gray-500">Student</p>
                    <p class="mt-1 text-sm text-gray-900">${submission.student_name} (${submission.student_id})</p>
                </div>
                <div>
                    <p class="text-sm font-medium text-gray-500">Submitted</p>
                    <p class="mt-1 text-sm text-gray-900">${formatDateTime(submission.submission_date)}</p>
                </div>
            </div>
            
            ${submission.submission_text ? `
                <div>
                    <p class="text-sm font-medium text-gray-500 mb-2">Text Submission</p>
                    <div class="p-4 bg-gray-50 rounded-md max-h-96 overflow-y-auto">
                        <pre class="whitespace-pre-wrap text-sm">${escapeHtml(submission.submission_text)}</pre>
                    </div>
                </div>
            ` : ''}
            
            ${submission.has_file ? `
                <div>
                    <p class="text-sm font-medium text-gray-500 mb-2">File Attachment</p>
                    <div class="flex items-center justify-between p-4 bg-gray-50 rounded-md">
                        <div>
                            <p class="text-sm font-medium text-gray-900">${submission.file_name}</p>
                            <p class="text-xs text-gray-500">Size: ${formatFileSize(submission.file_size)} | Type: ${submission.mime_type}</p>
                        </div>
                        <button onclick="downloadSubmission(${submission.submission_id})" 
                                class="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 text-sm">
                            Download
                        </button>
                    </div>
                </div>
            ` : ''}
            
            ${submission.score !== null ? `
                <div>
                    <p class="text-sm font-medium text-gray-500 mb-2">Current Grade</p>
                    <div class="p-4 bg-green-50 rounded-md">
                        <p class="text-lg font-bold text-green-800">${submission.score} / ${submission.max_score} (${submission.percentage.toFixed(1)}%)</p>
                        ${submission.feedback ? `
                            <div class="mt-2">
                                <p class="text-sm font-medium text-gray-700">Feedback:</p>
                                <p class="text-sm text-gray-700">${submission.feedback}</p>
                            </div>
                        ` : ''}
                        <p class="text-xs text-gray-500 mt-2">Graded by: ${submission.graded_by} on ${formatDateTime(submission.graded_date)}</p>
                    </div>
                </div>
            ` : ''}
        </div>
    `;
    
    // Update grade button
    const gradeBtn = document.getElementById('gradeSubmissionBtn');
    gradeBtn.style.display = submission.enrollment_id ? 'block' : 'none';
    gradeBtn.onclick = () => {
        window.location.href = `assessment-grade.html?id=${assessmentId}&highlight=${submission.enrollment_id}`;
    };
    
    document.getElementById('submissionModal').classList.remove('hidden');
}

function closeSubmissionModal() {
    document.getElementById('submissionModal').classList.add('hidden');
}

async function downloadSubmission(submissionId) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/api/faculty/submissions/${submissionId}/download`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const contentDisposition = response.headers.get('content-disposition');
            const fileName = contentDisposition
                ? contentDisposition.split('filename=')[1].replace(/['"]/g, '')
                : 'submission';
            
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            showError('Failed to download submission');
        }
    } catch (error) {
        console.error('Error downloading submission:', error);
        showError('Error downloading submission');
    }
}

// Utility functions
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

function formatFileSize(bytes) {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function showError(message) {
    alert(message); // Replace with your error display method
}

function logout() {
    localStorage.clear();
    window.location.href = '../login.html';
}