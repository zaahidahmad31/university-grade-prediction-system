document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const elements = {
        username: document.getElementById('username'),
        logoutBtn: document.getElementById('logoutBtn'),
        refreshBtn: document.getElementById('refreshBtn'),
        enrollBtn: document.getElementById('enrollBtn'),
        termFilter: document.getElementById('termFilter'),
        searchCourses: document.getElementById('searchCourses'),
        statusFilter: document.getElementById('statusFilter'),
        totalCoursesCount: document.getElementById('totalCoursesCount'),
        currentGPA: document.getElementById('currentGPA'),
        overallAttendance: document.getElementById('overallAttendance'),
        atRiskCoursesCount: document.getElementById('atRiskCoursesCount'),
        coursesContainer: document.getElementById('coursesContainer'),
        emptyState: document.getElementById('emptyState'),
        attendanceTrend: document.getElementById('attendanceTrend'),
        courseModal: document.getElementById('courseModal'),
        modalCourseTitle: document.getElementById('modalCourseTitle'),
        courseModalContent: document.getElementById('courseModalContent'),
        closeCourseModal: document.getElementById('closeCourseModal'),
        quickActionsModal: document.getElementById('quickActionsModal'),
        quickActionsContent: document.getElementById('quickActionsContent'),
        closeQuickActionsModal: document.getElementById('closeQuickActionsModal')
    };
    
    // State
    let state = {
        allCourses: [],
        filteredCourses: [],
        dashboardSummary: {},
        gradeChart: null,
        isLoading: false,
        isInitialized: false,
        gradeChartRendered: false
    };
    
    // Initialize
    init();
    
    function init() {
        if (state.isInitialized) return;
        
        // Auth check is now handled by auth-guard.js
        // Just verify we're a student
        if (!authApi.hasRole('student')) {
            console.error('Not authorized as student');
            return;
        }
        
        // Setup event listeners
        setupEventListeners();
        
        state.isInitialized = true;
        
        // Load data
        loadAllData();
    }
    
    function setupEventListeners() {
        // Basic actions
        elements.refreshBtn?.addEventListener('click', () => !state.isLoading && loadAllData());
        
        // Search with debounce
        let searchTimeout;
        elements.searchCourses?.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(filterCourses, 300);
        });
        
        // Filters
        elements.termFilter?.addEventListener('change', () => !state.isLoading && loadCourses());
        elements.statusFilter?.addEventListener('change', filterCourses);
        
        // Modal controls
        setupModalListeners();
    }
    
    function setupModalListeners() {
        // Close buttons
        elements.closeCourseModal?.addEventListener('click', () => {
            elements.courseModal?.classList.add('hidden');
        });
        
        elements.closeQuickActionsModal?.addEventListener('click', () => {
            elements.quickActionsModal?.classList.add('hidden');
        });
        
        // Backdrop clicks
        elements.courseModal?.addEventListener('click', function(e) {
            if (e.target === this) this.classList.add('hidden');
        });
        
        elements.quickActionsModal?.addEventListener('click', function(e) {
            if (e.target === this) this.classList.add('hidden');
        });
    }
    
    async function loadAllData() {
        if (state.isLoading) return;
        
        try {
            state.isLoading = true;
            showLoading();
            
            // Load dashboard and courses in parallel
            const [dashboardResult, coursesResult] = await Promise.allSettled([
                loadDashboardSummary(),
                loadCourses()
            ]);
            
            // Handle results
            if (dashboardResult.status === 'fulfilled') {
                updateDashboardStats();
            }
            
            if (coursesResult.status === 'fulfilled') {
                // Update charts only once after DOM is ready
                requestAnimationFrame(() => {
                    updateProgressCharts();
                });
            }
            
        } catch (error) {
            console.error('Error loading data:', error);
            showError('Failed to load course data');
        } finally {
            state.isLoading = false;
        }
    }
    
    async function loadDashboardSummary() {
        try {
            const response = await studentApi.getDashboard();
            
            if (response.status === 'success' && response.data) {
                state.dashboardSummary = response.data.summary || {};
                return state.dashboardSummary;
            }
        } catch (error) {
            console.warn('Dashboard summary not available:', error);
            state.dashboardSummary = { gpa: 0, attendance_rate: 0, upcoming_assessments: 0 };
        }
    }
    
    async function loadCourses() {
        showLoading();
        
        try {
            const response = await studentApi.getCourses();
            
            if (response.status === 'success' && response.data) {
                state.allCourses = response.data.courses || [];
                state.filteredCourses = [...state.allCourses];
                updateStats();
                displayCourses();
            }
        } catch (error) {
            console.error('Error loading courses:', error);
            showError('Failed to load courses');
        } finally {
            hideLoading();
        }
    }
    
    function displayCourses() {
        if (!elements.coursesContainer) return;
        
        const coursesToDisplay = state.filteredCourses.length > 0 ? state.filteredCourses : state.allCourses;
        
        if (coursesToDisplay.length === 0) {
            showEmptyState();
            return;
        }
        
        hideEmptyState();
        
        elements.coursesContainer.innerHTML = coursesToDisplay.map(course => createCourseCard(course)).join('');
        
        // Attach event listeners after creating cards
        attachCourseCardListeners();
    }
    
    function createCourseCard(course) {
        const attendanceRate = course.attendance_rate || 0;
        const predictedGrade = course.predicted_grade || 'N/A';
        const currentGrade = course.current_grade || 'N/A';
        
        const attendanceColor = attendanceRate >= 80 ? 'text-green-600' :
                               attendanceRate >= 60 ? 'text-yellow-600' : 'text-red-600';
        
        const gradeColor = getGradeColor(predictedGrade);
        const isAtRisk = isStudentAtRisk(course);
        
        return `
            <div class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 course-card cursor-pointer" 
                 data-course-id="${course.course_id || ''}" 
                 data-offering-id="${course.offering_id || ''}">
                <div class="p-6">
                    <!-- Course Header -->
                    <div class="flex justify-between items-start mb-4">
                        <div class="flex-1">
                            <h3 class="text-lg font-semibold text-gray-900 mb-1">
                                ${course.course_name || 'Course Name'}
                            </h3>
                            <p class="text-sm text-gray-600">
                                ${course.course_code || 'N/A'} • ${course.credits || 0} Credits
                            </p>
                        </div>
                        <div class="flex flex-col items-end space-y-1">
                            <span class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                                ${course.enrollment_status || 'Enrolled'}
                            </span>
                            ${isAtRisk ? '<span class="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">At Risk</span>' : ''}
                        </div>
                    </div>
                    
                    <!-- Progress Stats -->
                    <div class="grid grid-cols-3 gap-3 mb-4">
                        <div class="text-center p-3 bg-gray-50 rounded-lg">
                            <div class="text-lg font-bold ${attendanceColor}">${Math.round(attendanceRate)}%</div>
                            <div class="text-xs text-gray-600">Attendance</div>
                        </div>
                        <div class="text-center p-3 bg-gray-50 rounded-lg">
                            <div class="text-lg font-bold text-blue-600">${currentGrade}</div>
                            <div class="text-xs text-gray-600">Current</div>
                        </div>
                        <div class="text-center p-3 bg-gray-50 rounded-lg">
                            <div class="text-lg font-bold ${gradeColor}">${predictedGrade}</div>
                            <div class="text-xs text-gray-600">Predicted</div>
                        </div>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="flex space-x-2">
                        <button class="flex-1 bg-blue-600 text-white py-2 px-3 rounded text-sm hover:bg-blue-700 view-details-btn"
                                data-course-id="${course.course_id || ''}">
                            <i class="fas fa-eye mr-1"></i> Details
                        </button>
                        <button class="flex-1 bg-green-600 text-white py-2 px-3 rounded text-sm hover:bg-green-700 quick-actions-btn"
                                data-course-id="${course.course_id || ''}">
                            <i class="fas fa-bolt mr-1"></i> Actions
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Helper functions
    function getGradeColor(grade) {
    if (['A', 'A-', 'B+', 'B'].includes(grade)) return 'text-green-600';
    if (['B-', 'C+', 'C'].includes(grade)) return 'text-yellow-600';
    if (['C-', 'D+', 'D', 'D-', 'F', 'Fail'].includes(grade) || grade?.toLowerCase() === 'fail') return 'text-red-600';
    return 'text-gray-600';
}
    
    function isStudentAtRisk(course) {
    const grade = course.predicted_grade;
    return ['C-', 'D+', 'D', 'D-', 'F', 'Fail'].includes(grade) || 
           grade?.toLowerCase() === 'fail' ||
           (course.attendance_rate && course.attendance_rate < 60);
}
    
    function attachCourseCardListeners() {
        // Use event delegation for better performance
        document.querySelectorAll('.view-details-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const courseId = this.dataset.courseId;
                if (courseId) viewCourseDetails(courseId);
            });
        });
        
        document.querySelectorAll('.quick-actions-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const courseId = this.dataset.courseId;
                if (courseId) showQuickActions(courseId);
            });
        });
        
        document.querySelectorAll('.course-card').forEach(card => {
            card.addEventListener('click', function() {
                const courseId = this.dataset.courseId;
                if (courseId) viewCourseDetails(courseId);
            });
        });
    }
    
    function filterCourses() {
        const searchTerm = elements.searchCourses?.value?.toLowerCase() || '';
        const selectedStatus = elements.statusFilter?.value || '';
        
        state.filteredCourses = state.allCourses.filter(course => {
            const matchesSearch = !searchTerm || 
                course.course_name?.toLowerCase().includes(searchTerm) ||
                course.course_code?.toLowerCase().includes(searchTerm);
            
            const matchesStatus = !selectedStatus || 
                course.enrollment_status === selectedStatus;
            
            return matchesSearch && matchesStatus;
        });
        
        displayCourses();
        updateStats();
    }
    
    function updateStats() {
        // Count total courses
        const totalCourses = state.allCourses.length;
        
        // Count at-risk courses
        const atRiskCount = state.allCourses.filter(course => isStudentAtRisk(course)).length;
        
        // Update display
        if (elements.totalCoursesCount) {
            elements.totalCoursesCount.textContent = totalCourses;
        }
        if (elements.atRiskCoursesCount) {
            elements.atRiskCoursesCount.textContent = atRiskCount;
        }
    }
    
    function updateDashboardStats() {
        if (elements.currentGPA) {
            elements.currentGPA.textContent = state.dashboardSummary.gpa || '-';
        }
        if (elements.overallAttendance) {
            elements.overallAttendance.textContent = `${Math.round(state.dashboardSummary.attendance_rate || 0)}%`;
        }
    }
    
function updateProgressCharts() {
    // Update attendance trend
    updateAttendanceTrend();
    
    // Update grade summary directly
    updateGradeSummary();
}
    
function updateGradeSummary() {
    console.log('updateGradeSummary called'); // Debug log
    
    // Look for the correct element
    const gradeChart = document.getElementById('gradeChart');
    if (!gradeChart) {
        console.error('Grade chart element not found');
        return;
    }
    
    console.log('Courses data:', state.allCourses); // Debug log
    
    // Calculate grade distribution
    const gradeDistribution = {
        'A': 0,
        'B': 0,
        'C': 0,
        'D': 0,
        'F': 0
    };
    
    let total = 0;
    state.allCourses.forEach(course => {
        const grade = course.predicted_grade || course.current_grade;
        console.log(`Course ${course.course_code}: grade = ${grade}`); // Debug log
        
        if (!grade || grade === 'N/A') return;
        
        // Handle both letter grades and "Fail"
        if (['A+', 'A', 'A-'].includes(grade)) gradeDistribution['A']++;
        else if (['B+', 'B', 'B-'].includes(grade)) gradeDistribution['B']++;
        else if (['C+', 'C', 'C-'].includes(grade)) gradeDistribution['C']++;
        else if (['D+', 'D', 'D-'].includes(grade)) gradeDistribution['D']++;
        else if (grade === 'F' || grade === 'Fail' || grade.toLowerCase() === 'fail') gradeDistribution['F']++;
        
        total++;
    });
    
    console.log('Grade distribution:', gradeDistribution, 'Total:', total); // Debug log
    
    // Create the chart HTML
    const pieChartHTML = createStaticPieChart(gradeDistribution, total);
    
    // Simply replace the content of the gradeChart div
    gradeChart.innerHTML = pieChartHTML;
    
    console.log('Chart rendered'); // Debug log
}
    
    function createStaticPieChart(data, total) {
        if (total === 0) {
            return '<p class="text-gray-500 text-center">No grade data available</p>';
        }
        
        const width = 250;
        const height = 250;
        const radius = 100;
        const centerX = width / 2;
        const centerY = height / 2;
        
        const colors = {
            'A': '#10B981', // Green
            'B': '#3B82F6', // Blue
            'C': '#F59E0B', // Yellow
            'D': '#EF4444', // Orange
            'F': '#DC2626'  // Red
        };
        
        // Calculate angles for each segment
        let currentAngle = -90; // Start at top
        const segments = [];
        
        Object.entries(data).forEach(([grade, count]) => {
            if (count > 0) {
                const percentage = (count / total) * 100;
                const angle = (count / total) * 360;
                
                segments.push({
                    grade,
                    count,
                    percentage,
                    startAngle: currentAngle,
                    endAngle: currentAngle + angle,
                    color: colors[grade]
                });
                
                currentAngle += angle;
            }
        });
        
        // Create SVG paths for pie segments
        const svgPaths = segments.map(segment => {
            const startAngleRad = (segment.startAngle * Math.PI) / 180;
            const endAngleRad = (segment.endAngle * Math.PI) / 180;
            
            const x1 = centerX + radius * Math.cos(startAngleRad);
            const y1 = centerY + radius * Math.sin(startAngleRad);
            const x2 = centerX + radius * Math.cos(endAngleRad);
            const y2 = centerY + radius * Math.sin(endAngleRad);
            
            const largeArcFlag = segment.endAngle - segment.startAngle > 180 ? 1 : 0;
            
            const pathData = [
                `M ${centerX} ${centerY}`,
                `L ${x1} ${y1}`,
                `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
                'Z'
            ].join(' ');
            
            return `<path d="${pathData}" fill="${segment.color}" stroke="white" stroke-width="2"/>`;
        }).join('');
        
        // Create legend
        const legend = segments.map(segment => `
            <div class="flex items-center space-x-2">
                <div class="w-4 h-4 rounded" style="background-color: ${segment.color}"></div>
                <span class="text-sm">Grade ${segment.grade}: ${segment.count} (${segment.percentage.toFixed(1)}%)</span>
            </div>
        `).join('');
        
        return `
            <div class="text-center">
                <svg width="${width}" height="${height}" class="mx-auto">
                    ${svgPaths}
                </svg>
                <div class="mt-4 space-y-1 text-left inline-block">
                    ${legend}
                </div>
                <div class="mt-2 text-sm text-gray-600">
                    Total Courses: ${total}
                </div>
            </div>
        `;
    }
    
    function updateAttendanceTrend() {
        if (!elements.attendanceTrend) return;
        
        if (state.allCourses.length === 0) {
            elements.attendanceTrend.innerHTML = '<p class="text-gray-500 text-sm">No attendance data available</p>';
            return;
        }
        
        const html = state.allCourses.map(course => {
            const rate = course.attendance_rate || 0;
            const color = rate >= 80 ? 'bg-green-500' :
                         rate >= 60 ? 'bg-yellow-500' : 'bg-red-500';
            
            return `
                <div class="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span class="text-sm font-medium">${course.course_code || 'N/A'}</span>
                    <div class="flex items-center space-x-2">
                        <div class="w-24 h-2 bg-gray-200 rounded-full">
                            <div class="${color} h-2 rounded-full transition-all duration-300" style="width: ${rate}%"></div>
                        </div>
                        <span class="text-sm text-gray-600 w-12 text-right">${Math.round(rate)}%</span>
                    </div>
                </div>
            `;
        }).join('');
        
        elements.attendanceTrend.innerHTML = html;
    }
    
    async function viewCourseDetails(courseId) {
        const course = state.allCourses.find(c => c.course_id == courseId);
        if (!course) {
            showError('Course not found');
            return;
        }
        
        // Update modal title
        if (elements.modalCourseTitle) {
            elements.modalCourseTitle.textContent = `${course.course_code || 'N/A'} - ${course.course_name || 'Course'}`;
        }
        
        // Update modal content
        if (elements.courseModalContent) {
            elements.courseModalContent.innerHTML = `
                <div class="space-y-6">
                    <!-- Course Overview -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h4 class="font-semibold text-gray-900 mb-3">Course Information</h4>
                            <div class="space-y-2 text-sm">
                                <p><strong>Course Code:</strong> ${course.course_code || 'N/A'}</p>
                                <p><strong>Course Name:</strong> ${course.course_name || 'N/A'}</p>
                                <p><strong>Credits:</strong> ${course.credits || 'N/A'}</p>
                                <p><strong>Status:</strong> <span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">${course.enrollment_status || 'Enrolled'}</span></p>
                            </div>
                        </div>
                        <div>
                            <h4 class="font-semibold text-gray-900 mb-3">Academic Performance</h4>
                            <div class="space-y-2 text-sm">
                                <p><strong>Current Grade:</strong> <span class="font-bold text-blue-600">${course.current_grade || 'N/A'}</span></p>
                                <p><strong>Predicted Grade:</strong> <span class="font-bold ${getGradeColor(course.predicted_grade)}">${course.predicted_grade || 'N/A'}</span></p>
                                <p><strong>Attendance Rate:</strong> <span class="font-bold">${Math.round(course.attendance_rate || 0)}%</span></p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Performance Metrics -->
                    <div>
                        <h4 class="font-semibold text-gray-900 mb-3">Performance Overview</h4>
                        <div class="grid grid-cols-3 gap-4">
                            <div class="bg-blue-50 p-4 rounded-lg text-center">
                                <div class="text-2xl font-bold text-blue-600">${Math.round(course.attendance_rate || 0)}%</div>
                                <div class="text-sm text-gray-600">Attendance</div>
                            </div>
                            <div class="bg-green-50 p-4 rounded-lg text-center">
                                <div class="text-2xl font-bold text-green-600">${course.current_grade || 'N/A'}</div>
                                <div class="text-sm text-gray-600">Current Grade</div>
                            </div>
                            <div class="bg-purple-50 p-4 rounded-lg text-center">
                                <div class="text-2xl font-bold text-purple-600">${course.predicted_grade || 'N/A'}</div>
                                <div class="text-sm text-gray-600">Predicted Grade</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Quick Links -->
                    <div class="grid grid-cols-2 gap-3 pt-4 border-t">
                        <a href="attendance.html?course=${course.course_id}" 
                           class="bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 text-center">
                            <i class="fas fa-calendar-check mr-2"></i>View Attendance
                        </a>
                        <a href="assessments.html?course=${course.course_id}" 
                           class="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 text-center">
                            <i class="fas fa-clipboard-check mr-2"></i>View Assessments
                        </a>
                        <a href="grades.html?course=${course.course_id}" 
                           class="bg-purple-600 text-white py-2 px-4 rounded hover:bg-purple-700 text-center">
                            <i class="fas fa-chart-line mr-2"></i>View Grades
                        </a>
                        <a href="predictions.html?course=${course.course_id}" 
                           class="bg-orange-600 text-white py-2 px-4 rounded hover:bg-orange-700 text-center">
                            <i class="fas fa-crystal-ball mr-2"></i>View Predictions
                        </a>
                    </div>
                </div>
            `;
        }
        
        // Show modal
        elements.courseModal?.classList.remove('hidden');
    }
    
    function showQuickActions(courseId) {
        const course = state.allCourses.find(c => c.course_id == courseId);
        if (!course) return;
        
        // Update quick actions content
        if (elements.quickActionsContent) {
            elements.quickActionsContent.innerHTML = `
                <a href="attendance.html?course=${course.course_id}" 
                   class="block w-full text-left p-3 hover:bg-gray-50 rounded border">
                    <i class="fas fa-calendar-check text-green-600 mr-3"></i>
                    <span class="font-medium">View Attendance</span>
                    <p class="text-sm text-gray-600 mt-1">Check your attendance record for this course</p>
                </a>
                <a href="assessments.html?course=${course.course_id}" 
                   class="block w-full text-left p-3 hover:bg-gray-50 rounded border">
                    <i class="fas fa-clipboard-check text-blue-600 mr-3"></i>
                    <span class="font-medium">View Assessments</span>
                    <p class="text-sm text-gray-600 mt-1">See assignments, quizzes, and exams</p>
                </a>
                <a href="grades.html?course=${course.course_id}" 
                   class="block w-full text-left p-3 hover:bg-gray-50 rounded border">
                    <i class="fas fa-chart-line text-purple-600 mr-3"></i>
                    <span class="font-medium">View Grades</span>
                    <p class="text-sm text-gray-600 mt-1">Check your grades and progress</p>
                </a>
                <a href="predictions.html?course=${course.course_id}" 
                   class="block w-full text-left p-3 hover:bg-gray-50 rounded border">
                    <i class="fas fa-crystal-ball text-orange-600 mr-3"></i>
                    <span class="font-medium">Grade Predictions</span>
                    <p class="text-sm text-gray-600 mt-1">View AI-powered grade predictions</p>
                </a>
            `;
        }
        
        // Show quick actions modal
        elements.quickActionsModal?.classList.remove('hidden');
    }
    
    // UI Helper functions
    function showLoading() {
        if (elements.coursesContainer) {
            elements.coursesContainer.innerHTML = `
                <div class="col-span-full text-center py-8">
                    <div class="inline-flex items-center px-4 py-2 text-gray-600">
                        <i class="fas fa-spinner fa-spin mr-2"></i>
                        Loading courses...
                    </div>
                </div>
            `;
        }
    }
    
    function hideLoading() {
        const loader = document.getElementById('loader');
        if (loader) loader.style.display = 'none';
    }
    
    function showEmptyState() {
        if (elements.coursesContainer) elements.coursesContainer.innerHTML = '';
        if (elements.emptyState) elements.emptyState.classList.remove('hidden');
    }
    
    function hideEmptyState() {
        if (elements.emptyState) elements.emptyState.classList.add('hidden');
    }
    
    function showError(message) {
        showNotification(message, 'error');
    }
    
    function showSuccess(message) {
        showNotification(message, 'success');
    }
    
    function showNotification(message, type = 'info') {
        const bgColor = type === 'error' ? 'bg-red-500' : 
                       type === 'success' ? 'bg-green-500' : 'bg-blue-500';
        
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 ${bgColor} text-white px-4 py-2 rounded shadow-lg z-50`;
        toast.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'} mr-2"></i>
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
});