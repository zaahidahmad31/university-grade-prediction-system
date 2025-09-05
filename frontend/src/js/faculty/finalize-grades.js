document.addEventListener('DOMContentLoaded', function() {
    // Get URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const offeringId = urlParams.get('offering_id');
    
    if (!offeringId) {
        alert('No course selected');
        window.location.href = 'dashboard.html';
        return;
    }
    
    // Elements
    const courseTitle = document.getElementById('courseTitle');
    const courseDetails = document.getElementById('courseDetails');
    const gradeTableBody = document.getElementById('gradeTableBody');
    const totalStudents = document.getElementById('totalStudents');
    const finalizedCount = document.getElementById('finalizedCount');
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const selectAllBtn = document.getElementById('selectAllBtn');
    const finalizeSelectedBtn = document.getElementById('finalizeSelectedBtn');
    const overrideModal = document.getElementById('overrideModal');
    const suggestedGradeText = document.getElementById('suggestedGradeText');
    const overrideGradeText = document.getElementById('overrideGradeText');
    const overrideReason = document.getElementById('overrideReason');
    const cancelOverride = document.getElementById('cancelOverride');
    const confirmOverride = document.getElementById('confirmOverride');
    
    // State
    let gradeData = [];
    let selectedGrades = new Set();
    let pendingOverride = null;
    
    // Load grade summary
    loadGradeSummary();
    
    async function loadGradeSummary() {
        try {
            const response = await apiClient.get(`faculty/courses/${offeringId}/grade-summary`);
            
            if (response.status === 'success') {
                const data = response.data;
                
                // Display course info
                courseTitle.textContent = `${data.course.course_code} - ${data.course.course_name}`;
                courseDetails.textContent = `Section ${data.course.section} | ${data.course.term}`;
                
                // Store grade data
                gradeData = data.students;
                
                // Update counts
                totalStudents.textContent = gradeData.length;
                finalizedCount.textContent = gradeData.filter(s => s.is_finalized).length;
                
                // Display students
                displayGrades();
            }
        } catch (error) {
            console.error('Error loading grade summary:', error);
            alert('Failed to load grade summary');
        }
    }
    
    function displayGrades() {
        gradeTableBody.innerHTML = '';
        
        gradeData.forEach((student, index) => {
            const row = createGradeRow(student, index);
            gradeTableBody.appendChild(row);
        });
    }
    
    function createGradeRow(student, index) {
        const row = document.createElement('tr');
        row.className = student.is_finalized ? 'bg-gray-50' : '';
        
        // Get assessment scores
        const quizScore = getAssessmentScore(student.assessments, 'Quiz');
        const assignmentScore = getAssessmentScore(student.assessments, 'Assignment');
        const midtermScore = getAssessmentScore(student.assessments, 'Midterm Exam');
        const finalScore = getAssessmentScore(student.assessments, 'Final Exam');
        
        // Check if grade was overridden
        const isOverridden = student.suggested_grade && 
                           student.final_grade && 
                           student.suggested_grade !== student.final_grade;
        
        row.innerHTML = `
            <td class="px-4 py-4">
                <input type="checkbox" 
                       class="student-checkbox rounded" 
                       data-index="${index}"
                       ${student.is_finalized ? 'disabled' : ''}>
            </td>
            <td class="px-4 py-4">
                <div class="text-sm font-medium text-gray-900">${student.student_name}</div>
                <div class="text-sm text-gray-500">ID: ${student.student_id}</div>
            </td>
            <td class="px-4 py-4 text-sm">${quizScore}</td>
            <td class="px-4 py-4 text-sm">${assignmentScore}</td>
            <td class="px-4 py-4 text-sm">${midtermScore}</td>
            <td class="px-4 py-4 text-sm">${finalScore}</td>
            <td class="px-4 py-4">
                <span class="text-sm font-semibold ${student.total_percentage ? 'text-gray-900' : 'text-gray-400'}">
                    ${student.total_percentage ? student.total_percentage + '%' : '-'}
                </span>
            </td>
            <td class="px-4 py-4">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getGradeBadgeClass(student.suggested_grade)}">
                    ${student.suggested_grade || '-'}
                </span>
            </td>
            <td class="px-4 py-4">
                ${student.is_finalized ? 
                    `<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getGradeBadgeClass(student.final_grade)}">
                        ${student.final_grade}
                        ${isOverridden ? '<span class="ml-1 text-yellow-600">*</span>' : ''}
                    </span>` :
                    `<select class="grade-select text-sm border rounded px-2 py-1" data-index="${index}">
                        <option value="">Select</option>
                        <option value="A" ${student.suggested_grade === 'A' ? 'selected' : ''}>A</option>
                        <option value="B" ${student.suggested_grade === 'B' ? 'selected' : ''}>B</option>
                        <option value="C" ${student.suggested_grade === 'C' ? 'selected' : ''}>C</option>
                        <option value="D" ${student.suggested_grade === 'D' ? 'selected' : ''}>D</option>
                        <option value="F" ${student.suggested_grade === 'F' ? 'selected' : ''}>F</option>
                    </select>`
                }
            </td>
            <td class="px-4 py-4">
                ${student.is_finalized ? 
                    '<span class="text-xs text-green-600 font-medium">Finalized</span>' :
                    '<span class="text-xs text-gray-500">Pending</span>'
                }
            </td>
        `;
        
        // Add event listeners
        const checkbox = row.querySelector('.student-checkbox');
        if (checkbox && !student.is_finalized) {
            checkbox.addEventListener('change', handleCheckboxChange);
        }
        
        const gradeSelect = row.querySelector('.grade-select');
        if (gradeSelect) {
            gradeSelect.addEventListener('change', handleGradeChange);
        }
        
        return row;
    }
    
    function getAssessmentScore(assessments, type) {
        const assessment = assessments.find(a => a.type === type);
        if (!assessment || assessment.average === null) return '-';
        return assessment.average + '%';
    }
    
    function getGradeBadgeClass(grade) {
        const classes = {
            'A': 'bg-green-100 text-green-800',
            'B': 'bg-blue-100 text-blue-800',
            'C': 'bg-yellow-100 text-yellow-800',
            'D': 'bg-orange-100 text-orange-800',
            'F': 'bg-red-100 text-red-800'
        };
        return classes[grade] || 'bg-gray-100 text-gray-800';
    }
    
    function handleCheckboxChange(event) {
        const index = parseInt(event.target.dataset.index);
        
        if (event.target.checked) {
            selectedGrades.add(index);
        } else {
            selectedGrades.delete(index);
        }
        
        updateSelectionState();
    }
    
    function handleGradeChange(event) {
        const index = parseInt(event.target.dataset.index);
        const student = gradeData[index];
        const newGrade = event.target.value;
        
        // Check if this is an override
        if (newGrade && student.suggested_grade && newGrade !== student.suggested_grade) {
            // Show override modal
            pendingOverride = {
                index: index,
                suggestedGrade: student.suggested_grade,
                newGrade: newGrade,
                element: event.target
            };
            
            suggestedGradeText.textContent = student.suggested_grade;
            overrideGradeText.textContent = newGrade;
            overrideReason.value = '';
            overrideModal.classList.remove('hidden');
        }
    }
    
    function updateSelectionState() {
        finalizeSelectedBtn.disabled = selectedGrades.size === 0;
        selectAllCheckbox.checked = selectedGrades.size === gradeData.filter(s => !s.is_finalized).length;
    }
    
    // Select all functionality
    selectAllCheckbox.addEventListener('change', function() {
        const checkboxes = document.querySelectorAll('.student-checkbox:not(:disabled)');
        checkboxes.forEach((checkbox, index) => {
            checkbox.checked = this.checked;
            const studentIndex = parseInt(checkbox.dataset.index);
            if (this.checked) {
                selectedGrades.add(studentIndex);
            } else {
                selectedGrades.delete(studentIndex);
            }
        });
        updateSelectionState();
    });
    
    selectAllBtn.addEventListener('click', function() {
        selectAllCheckbox.checked = true;
        selectAllCheckbox.dispatchEvent(new Event('change'));
    });
    
    // Override modal handlers
    cancelOverride.addEventListener('click', function() {
        if (pendingOverride) {
            pendingOverride.element.value = pendingOverride.suggestedGrade || '';
            pendingOverride = null;
        }
        overrideModal.classList.add('hidden');
    });
    
    confirmOverride.addEventListener('click', function() {
        if (pendingOverride) {
            const student = gradeData[pendingOverride.index];
            student.override_reason = overrideReason.value;
            pendingOverride = null;
        }
        overrideModal.classList.add('hidden');
    });
    
    // Finalize grades
    finalizeSelectedBtn.addEventListener('click', async function() {
        const gradesToFinalize = [];
        
        selectedGrades.forEach(index => {
            const student = gradeData[index];
            const gradeSelect = document.querySelector(`.grade-select[data-index="${index}"]`);
            const finalGrade = gradeSelect ? gradeSelect.value : student.suggested_grade;
            
            if (finalGrade) {
                gradesToFinalize.push({
                    enrollment_id: student.enrollment_id,
                    final_grade: finalGrade,
                    override_reason: student.override_reason || null
                });
            }
        });
        
        if (gradesToFinalize.length === 0) {
            alert('Please select grades for all selected students');
            return;
        }
        
        if (!confirm(`Are you sure you want to finalize grades for ${gradesToFinalize.length} students? This will calculate and update their GPAs.`)) {
            return;
        }
        
        try {
            this.disabled = true;
            this.textContent = 'Finalizing...';
            
            const response = await apiClient.post('faculty/grades/finalize', {
                grades: gradesToFinalize
            });
            
            if (response.status === 'success') {
                alert(`Successfully finalized ${response.data.success_count} grades`);
                
                // Reload to show updated status
                await loadGradeSummary();
                selectedGrades.clear();
                updateSelectionState();
            } else {
                alert('Failed to finalize grades');
            }
        } catch (error) {
            console.error('Error finalizing grades:', error);
            alert('Failed to finalize grades');
        } finally {
            this.disabled = false;
            this.textContent = 'Finalize Selected';
        }
    });
    
    // Back button
    document.getElementById('backBtn').addEventListener('click', function() {
        window.location.href = 'dashboard.html';
    });
    
    // Display username
    const user = authApi.getCurrentUser();
    if (user) {
        document.getElementById('username').textContent = user.username;
    }
});