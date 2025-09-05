 document.addEventListener('DOMContentLoaded', function() {
        // Elements
        const usernameElement = document.getElementById('username');
        const logoutBtn = document.getElementById('logoutBtn');
        const courseFilter = document.getElementById('courseFilter');
        const riskFilter = document.getElementById('riskFilter');
        const searchInput = document.getElementById('searchInput');
        const clearFiltersBtn = document.getElementById('clearFiltersBtn');
        const exportBtn = document.getElementById('exportBtn');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const studentsContainer = document.getElementById('studentsContainer');
        const noStudents = document.getElementById('noStudents');
        
        // Summary elements
        const highRiskCount = document.getElementById('highRiskCount');
        const mediumRiskCount = document.getElementById('mediumRiskCount');
        const totalAtRisk = document.getElementById('totalAtRisk');
        
        // Modal elements
        const interventionModal = document.getElementById('interventionModal');
        const modalTitle = document.getElementById('modalTitle');
        const interventionNotes = document.getElementById('interventionNotes');
        const saveInterventionBtn = document.getElementById('saveInterventionBtn');
        const closeModalBtn = document.getElementById('closeModalBtn');
        
        // State
        let allAtRiskStudents = [];
        let filteredStudents = [];
        let coursesList = [];
        let currentStudentId = null;
        
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
            loadAtRiskStudents();
            
            // Set up event listeners
            setupEventListeners();
        }
        
        function setupEventListeners() {
            // Logout
            logoutBtn.addEventListener('click', function() {
                authApi.logout();
            });
            
            // Filters
            courseFilter.addEventListener('change', filterStudents);
            riskFilter.addEventListener('change', filterStudents);
            searchInput.addEventListener('input', debounce(filterStudents, 300));
            
            // Clear filters
            clearFiltersBtn.addEventListener('click', function() {
                courseFilter.value = '';
                riskFilter.value = '';
                searchInput.value = '';
                filterStudents();
            });
            
            // Export
            exportBtn.addEventListener('click', exportToCSV);
            
            // Modal events
            closeModalBtn.addEventListener('click', function() {
                interventionModal.classList.add('hidden');
            });
            
            saveInterventionBtn.addEventListener('click', saveIntervention);
        }
        
        async function loadFacultyCourses() {
            try {
                const response = await apiClient.get('faculty/courses');
                if (response.status === 'success' && response.data.courses) {
                    coursesList = response.data.courses;
                    populateCourseFilter();
                }
            } catch (error) {
                console.error('Error loading courses:', error);
            }
        }
        
        async function loadAtRiskStudents() {
            try {
                showLoading(true);
                
                // Get at-risk students from API
                const response = await apiClient.get('faculty/at-risk-students');
                console.log('At-risk students response:', response);
                
                if (response.status === 'success' && response.data.students) {
                    allAtRiskStudents = response.data.students;
                    
                    // Enrich with additional data from all students
                    await enrichStudentData();
                    
                    updateSummaryStats();
                    filterStudents();
                } else {
                    allAtRiskStudents = [];
                    updateSummaryStats();
                    showNoStudents();
                }
            } catch (error) {
                console.error('Error loading at-risk students:', error);
                showError('Failed to load at-risk students. Please refresh the page.');
            } finally {
                showLoading(false);
            }
        }
        
        async function enrichStudentData() {
            // If API provided basic data, enrich with attendance information
            for (let i = 0; i < allAtRiskStudents.length; i++) {
                const student = allAtRiskStudents[i];
                
                try {
                    // Get attendance data if not already present
                    if (!student.attendance_rate && student.offering_id) {
                        const attendanceResponse = await apiClient.get(`faculty/attendance/summary/${student.offering_id}`);
                        if (attendanceResponse.status === 'success' && attendanceResponse.data.summary) {
                            const studentAttendance = attendanceResponse.data.summary.find(
                                record => record.student_id === student.student_id
                            );
                            
                            if (studentAttendance) {
                                student.attendance_rate = studentAttendance.attendance_rate;
                                student.present_count = studentAttendance.present_count;
                                student.total_classes = studentAttendance.total_classes;
                            }
                        }
                    }
                    
                    // Add risk factors if not already present
                    if (!student.risk_factors) {
                        student.risk_factors = identifyRiskFactors(student.attendance_rate || 0, student.gpa);
                    }
                    
                } catch (error) {
                    console.error(`Error enriching data for student ${student.student_id}:`, error);
                }
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
        
        function filterStudents() {
            const courseFilterValue = courseFilter.value;
            const riskFilterValue = riskFilter.value;
            const searchValue = searchInput.value.toLowerCase();
            
            filteredStudents = allAtRiskStudents.filter(student => {
                // Course filter
                if (courseFilterValue && student.offering_id != courseFilterValue) {
                    return false;
                }
                
                // Risk filter
                if (riskFilterValue && student.risk_level !== riskFilterValue) {
                    return false;
                }
                
                // Search filter - FIXED: Use correct field name
                if (searchValue) {
                    const studentName = student.name || 'Unknown';
                    const searchText = `${studentName} ${student.student_id}`.toLowerCase();
                    if (!searchText.includes(searchValue)) {
                        return false;
                    }
                }
                
                return true;
            });
            
            displayStudents(filteredStudents);
        }
        
        function displayStudents(students) {
            if (!students.length) {
                showNoStudents();
                return;
            }
            
            studentsContainer.innerHTML = '';
            
            students.forEach(student => {
                const studentCard = createStudentCard(student);
                studentsContainer.appendChild(studentCard);
            });
            
            studentsContainer.classList.remove('hidden');
            noStudents.classList.add('hidden');
        }
        
        function createStudentCard(student) {
            const card = document.createElement('div');
            card.className = 'bg-white rounded-lg shadow-md border-l-4 ' + 
                            (student.risk_level === 'high' ? 'border-red-500' : 'border-yellow-500');
            
            const riskBadge = getRiskBadge(student.risk_level);
            const attendanceBadge = getAttendanceBadge(student.attendance_rate || 0);
            const riskFactors = student.risk_factors || [];
            
            // FIXED: Use correct field name from API response
            const studentName = student.name || 'Unknown Student';
            const nameInitials = getNameInitials(studentName);
            
            card.innerHTML = `
                <div class="p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div class="flex items-center">
                            <div class="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center text-gray-600 font-medium text-lg">
                                ${nameInitials}
                            </div>
                            <div class="ml-4">
                                <h3 class="text-lg font-semibold text-gray-900">
                                    ${studentName}
                                </h3>
                                <p class="text-sm text-gray-500">ID: ${student.student_id}</p>
                                <p class="text-sm text-gray-500">
                                    ${student.course_code || 'Unknown Course'} - Section ${student.section || 'N/A'}
                                </p>
                            </div>
                        </div>
                        <div class="flex flex-col items-end space-y-2">
                            ${riskBadge}
                            <div class="text-right">
                                <div class="text-sm font-medium">Predicted: ${student.predicted_grade || 'N/A'}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Risk Metrics -->
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div class="text-center p-3 bg-gray-50 rounded-lg">
                            <div class="text-lg font-bold ${(student.attendance_rate || 0) < 70 ? 'text-red-600' : 'text-yellow-600'}">
                                ${(student.attendance_rate || 0).toFixed(1)}%
                            </div>
                            <div class="text-xs text-gray-500">Attendance</div>
                            ${attendanceBadge}
                        </div>
                        <div class="text-center p-3 bg-gray-50 rounded-lg">
                            <div class="text-lg font-bold text-gray-700">${student.gpa || 'N/A'}</div>
                            <div class="text-xs text-gray-500">Current GPA</div>
                        </div>
                        <div class="text-center p-3 bg-gray-50 rounded-lg">
                            <div class="text-lg font-bold text-gray-700">${student.present_count || 0}/${student.total_classes || 0}</div>
                            <div class="text-xs text-gray-500">Classes Attended</div>
                        </div>
                        <div class="text-center p-3 bg-gray-50 rounded-lg">
                            <div class="text-lg font-bold ${student.risk_level === 'high' ? 'text-red-600' : 'text-yellow-600'}">
                                ${riskFactors.length}
                            </div>
                            <div class="text-xs text-gray-500">Risk Factors</div>
                        </div>
                    </div>
                    
                    <!-- Risk Factors -->
                    ${riskFactors.length > 0 ? `
                        <div class="mb-4">
                            <h4 class="text-sm font-medium text-gray-700 mb-2">Risk Factors:</h4>
                            <div class="flex flex-wrap gap-2">
                                ${riskFactors.map(factor => `
                                    <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                                        ${factor}
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    <!-- Action Buttons -->
                    <div class="flex flex-wrap gap-2">
                        <a href="student-detail.html?student_id=${student.student_id}&offering_id=${student.offering_id}" 
                           class="bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 flex items-center">
                            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                            </svg>
                            View Details
                        </a>
                        <button onclick="recordIntervention('${student.student_id}', '${studentName}')" 
                                class="bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700 flex items-center">
                            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                            Add Note
                        </button>
                        <a href="attendance.html?course=${student.offering_id}" 
                           class="bg-yellow-600 text-white px-3 py-2 rounded text-sm hover:bg-yellow-700 flex items-center">
                            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                            </svg>
                            Attendance
                        </a>
                        <a href="assessments.html?course=${student.offering_id}" 
                           class="bg-purple-600 text-white px-3 py-2 rounded text-sm hover:bg-purple-700 flex items-center">
                            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                            Assessments
                        </a>
                    </div>
                </div>
            `;
            
            return card;
        }
        
        function getNameInitials(name) {
            if (!name || name === 'Unknown Student') return 'UN';
            
            const parts = name.trim().split(' ');
            if (parts.length === 1) {
                return parts[0].charAt(0).toUpperCase();
            }
            return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
        }
        
        function updateSummaryStats() {
            const high = allAtRiskStudents.filter(s => s.risk_level === 'high').length;
            const medium = allAtRiskStudents.filter(s => s.risk_level === 'medium').length;
            const total = high + medium;
            
            highRiskCount.textContent = high;
            mediumRiskCount.textContent = medium;
            totalAtRisk.textContent = total;
        }
        
        function calculateRiskLevel(attendanceRate, gpa) {
            const gpaScore = gpa ? parseFloat(gpa) : 2.0;
            
            if (attendanceRate < 70 || gpaScore < 2.0) return 'high';
            if (attendanceRate < 85 || gpaScore < 3.0) return 'medium';
            return 'low';
        }
        
        function calculatePredictedGrade(attendanceRate, gpa) {
            const gpaScore = gpa ? parseFloat(gpa) : 2.0;
            const combined = (attendanceRate / 100 * 0.3) + (gpaScore / 4.0 * 0.7);
            
            if (combined >= 0.9) return 'A';
            if (combined >= 0.8) return 'B';
            if (combined >= 0.7) return 'C';
            if (combined >= 0.6) return 'D';
            return 'F';
        }
        
        function identifyRiskFactors(attendanceRate, gpa) {
            const factors = [];
            
            if (attendanceRate < 60) factors.push('Very Low Attendance');
            else if (attendanceRate < 70) factors.push('Low Attendance');
            else if (attendanceRate < 80) factors.push('Below Average Attendance');
            
            const gpaScore = gpa ? parseFloat(gpa) : 2.0;
            if (gpaScore < 2.0) factors.push('Below 2.0 GPA');
            else if (gpaScore < 2.5) factors.push('Low GPA');
            
            // Add more sophisticated risk factors based on your data
            if (attendanceRate < 70 && gpaScore < 2.5) factors.push('Multiple Risk Indicators');
            
            return factors;
        }
        
        function getRiskBadge(riskLevel) {
            const badges = {
                'high': '<span class="inline-flex px-3 py-1 text-sm font-semibold rounded-full bg-red-100 text-red-800">🔴 High Risk</span>',
                'medium': '<span class="inline-flex px-3 py-1 text-sm font-semibold rounded-full bg-yellow-100 text-yellow-800">🟡 Medium Risk</span>'
            };
            return badges[riskLevel] || '';
        }
        
        function getAttendanceBadge(rate) {
            if (rate >= 80) return '<div class="text-xs text-blue-600 mt-1">Good</div>';
            if (rate >= 70) return '<div class="text-xs text-yellow-600 mt-1">Warning</div>';
            return '<div class="text-xs text-red-600 mt-1">Critical</div>';
        }
        
        function exportToCSV() {
            let csv = 'Student ID,Name,Course,Risk Level,Attendance Rate,GPA,Predicted Grade,Risk Factors\n';
            
            filteredStudents.forEach(student => {
                const riskFactors = (student.risk_factors || []).join('; ');
                const studentName = student.name || 'Unknown Student';
                csv += `"${student.student_id}","${studentName}","${student.course_code}","${student.risk_level}","${(student.attendance_rate || 0).toFixed(1)}%","${student.gpa || 'N/A'}","${student.predicted_grade}","${riskFactors}"\n`;
            });
            
            // Download CSV
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `at_risk_students_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
        }
        
        // Global function for intervention modal
        window.recordIntervention = function(studentId, studentName) {
            currentStudentId = studentId;
            modalTitle.textContent = `Record Intervention - ${studentName}`;
            interventionNotes.value = '';
            interventionModal.classList.remove('hidden');
        };
        
        async function saveIntervention() {
            const notes = interventionNotes.value.trim();
            if (!notes) {
                alert('Please enter intervention notes');
                return;
            }
            
            try {
                // Here you would save to your backend
                // For now, we'll just show success and close modal
                console.log(`Saving intervention for ${currentStudentId}: ${notes}`);
                
                alert('Intervention notes saved successfully');
                interventionModal.classList.add('hidden');
                
            } catch (error) {
                console.error('Error saving intervention:', error);
                alert('Failed to save intervention notes');
            }
        }
        
        function showLoading(show) {
            if (show) {
                loadingIndicator.classList.remove('hidden');
                studentsContainer.classList.add('hidden');
                noStudents.classList.add('hidden');
            } else {
                loadingIndicator.classList.add('hidden');
            }
        }
        
        function showNoStudents() {
            studentsContainer.classList.add('hidden');
            noStudents.classList.remove('hidden');
        }
        
        function showError(message) {
            console.error(message);
            alert(message);
        }
        
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
    });