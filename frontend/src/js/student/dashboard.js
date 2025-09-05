document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    const coursesList = document.getElementById('coursesList');
    const predictionsList = document.getElementById('predictionsList');
    
    // Dashboard summary elements
    const gpaElement = document.getElementById('currentGPA');
    const attendanceElement = document.getElementById('attendanceRate');
    const assessmentsElement = document.getElementById('upcomingAssessments');
    
    // ✅ FIX: Declare dashboardSummary variable in proper scope
    let dashboardSummary = {};
    
    // Display username
    const user = authApi.getCurrentUser();
    if (user) {
        usernameElement.textContent = user.username;
    }
    
    // Set up logout button
    logoutBtn.addEventListener('click', function() {
        authApi.logout();
    });
    
    // Load all student data
    loadDashboardData();
    
    async function loadDashboardData() {
        try {
            // Load dashboard summary
            await loadDashboardSummary();
            
            // Load courses
            await loadCourses();
            
            // Load predictions
            await loadPredictions();
            
            // Load recent assessments
            await loadRecentAssessments();
            
            // Load grade summary
            await loadGradeSummary();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            showError('Failed to load dashboard data. Please refresh the page.');
        }
    }
    
    async function loadDashboardSummary() {
        try {
            const response = await apiClient.get('student/dashboard');
            console.log('Dashboard summary response:', response);
            
            if (response.status === 'success' && response.data) {
                // ✅ FIX: Store the summary in the properly declared variable
                dashboardSummary = response.data.summary || {};
                
                // Update summary cards
                if (gpaElement) gpaElement.textContent = dashboardSummary.gpa || '-';
                if (attendanceElement) attendanceElement.textContent = (dashboardSummary.attendance_rate || 0) + '%';
                if (assessmentsElement) assessmentsElement.textContent = dashboardSummary.upcoming_assessments || 0;
            }
        } catch (error) {
            console.error('Error loading dashboard summary:', error);
        }
    }
    
    async function loadCourses() {
        try {
            const response = await apiClient.get('student/courses');
            console.log('Courses response:', response);
            
            if (response.status === 'success' && response.data) {
                displayCourses(response.data.courses);
            } else {
                coursesList.innerHTML = '<p class="text-gray-500">No courses found</p>';
            }
        } catch (error) {
            console.error('Error loading courses:', error);
            coursesList.innerHTML = '<p class="text-red-500">Error loading courses</p>';
        }
    }
    
    async function loadPredictions() {
        try {
            const response = await apiClient.get('student/predictions');
            console.log('Predictions response:', response);
            
            if (response.status === 'success' && response.data) {
                displayPredictions(response.data.predictions);
            } else {
                predictionsList.innerHTML = '<p class="text-gray-500">No predictions available</p>';
            }
        } catch (error) {
            console.error('Error loading predictions:', error);
            predictionsList.innerHTML = '<p class="text-red-500">Error loading predictions</p>';
        }
    }
    
    function displayCourses(courses) {
        if (!courses || courses.length === 0) {
            coursesList.innerHTML = `
                <div class="text-center py-6">
                    <i class="fas fa-graduation-cap text-gray-400 text-3xl mb-2"></i>
                    <p class="text-gray-500">No courses enrolled</p>
                    <a href="courses.html" class="text-blue-600 hover:text-blue-800 text-sm">Browse Courses</a>
                </div>
            `;
            return;
        }
        
        // Show only first 3 courses on dashboard
        const displayCourses = courses.slice(0, 3);
        
        let html = '';
        displayCourses.forEach(course => {
            const attendanceRate = course.attendance_rate || 0;
            const attendanceColor = attendanceRate >= 80 ? 'text-green-600' :
                                   attendanceRate >= 60 ? 'text-yellow-600' : 'text-red-600';
            
            const gradeColor = ['A', 'B'].includes(course.predicted_grade) ? 'text-green-600' :
                              course.predicted_grade === 'C' ? 'text-yellow-600' : 
                              ['D', 'F'].includes(course.predicted_grade) ? 'text-red-600' : 'text-gray-600';
            
            html += `
                <div class="border-b pb-3 mb-3 last:border-b-0">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <h4 class="font-semibold text-gray-900">${course.course_name || 'Course Name'}</h4>
                            <p class="text-sm text-gray-600">${course.course_code || 'N/A'} • Section ${course.section || 'N/A'}</p>
                            <div class="flex items-center mt-1 space-x-3 text-xs">
                                <span class="${attendanceColor}">
                                    <i class="fas fa-calendar-check mr-1"></i>
                                    ${Math.round(attendanceRate)}% attendance
                                </span>
                                <span class="${gradeColor}">
                                    <i class="fas fa-chart-line mr-1"></i>
                                    Grade: ${course.predicted_grade || 'N/A'}
                                </span>
                            </div>
                            ${course.next_assessment ? `
                            <p class="text-xs text-orange-600 mt-1">
                                <i class="fas fa-clock mr-1"></i>
                                ${course.next_assessment}
                            </p>
                            ` : ''}
                        </div>
                        <div class="text-right space-y-1">
                            <a href="courses.html?course=${course.course_id}" 
                               class="block text-blue-600 hover:text-blue-800 text-sm">
                                View Details →
                            </a>
                            <a href="assessments.html?course=${course.course_id}" 
                               class="block text-green-600 hover:text-green-800 text-sm">
                                Assessments →
                            </a>
                        </div>
                    </div>
                </div>
            `;
        });
        
        // Add "View All" link if there are more courses
        if (courses.length > 3) {
            html += `
                <div class="text-center pt-3 border-t">
                    <a href="courses.html" class="text-blue-600 hover:text-blue-800 text-sm font-medium">
                        View all ${courses.length} courses →
                    </a>
                </div>
            `;
        } else if (courses.length > 0) {
            html += `
                <div class="text-center pt-3 border-t">
                    <a href="courses.html" class="text-blue-600 hover:text-blue-800 text-sm font-medium">
                        View course details →
                    </a>
                </div>
            `;
        }
        
        coursesList.innerHTML = html;
    }
    
    function displayPredictions(predictions) {
        if (!predictions || predictions.length === 0) {
            predictionsList.innerHTML = '<p class="text-gray-500">No predictions available</p>';
            return;
        }
        
        let html = '';
        predictions.forEach(prediction => {
            // Determine color based on predicted grade
            let gradeColor = 'text-green-600';
            if (prediction.predicted_grade === 'C' || prediction.predicted_grade === 'D') {
                gradeColor = 'text-yellow-600';
            } else if (prediction.predicted_grade === 'F') {
                gradeColor = 'text-red-600';
            }
            
            const confidencePercent = Math.round((prediction.confidence_score || 0) * 100);
            
            html += `
                <div class="border-b pb-3 mb-3 last:border-b-0">
                    <h4 class="font-semibold">${prediction.course_name || 'Course'}</h4>
                    <p class="text-sm text-gray-600">${prediction.course_code || 'N/A'}</p>
                    <div class="mt-2 flex justify-between items-center">
                        <span>Predicted Grade: <span class="font-bold ${gradeColor}">${prediction.predicted_grade || 'N/A'}</span></span>
                        <span class="text-sm text-gray-600">Confidence: ${confidencePercent}%</span>
                    </div>
                    <div class="mt-1 w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-blue-600 h-2 rounded-full" style="width: ${confidencePercent}%"></div>
                    </div>
                </div>
            `;
        });
        
        predictionsList.innerHTML = html;
    }

    async function loadRecentAssessments() {
        try {
            const response = await apiClient.get('student/assessments');
            console.log('Recent assessments response:', response);
            
            if (response.status === 'success' && response.data) {
                displayRecentAssessments(response.data.assessments || []);
            }
        } catch (error) {
            console.error('Error loading recent assessments:', error);
            const recentAssessments = document.getElementById('recentAssessments');
            if (recentAssessments) {
                recentAssessments.innerHTML = '<p class="text-gray-500 text-sm">Unable to load assessments</p>';
            }
        }
    }

    function displayRecentAssessments(assessments) {
        const recentAssessments = document.getElementById('recentAssessments');
        if (!recentAssessments) return;
        
        if (!assessments || assessments.length === 0) {
            recentAssessments.innerHTML = '<p class="text-gray-500 text-sm">No recent assessments</p>';
            return;
        }
        
        // Show only recent/upcoming assessments
        const recentAssessmentsList = assessments.slice(0, 3);
        
        const html = recentAssessmentsList.map(assessment => {
            const dueDate = assessment.due_date ? new Date(assessment.due_date) : null;
            const isOverdue = dueDate && new Date() > dueDate;
            const isUpcoming = dueDate && new Date() < dueDate;
            
            return `
                <div class="flex justify-between items-center p-3 border border-gray-200 rounded-lg">
                    <div>
                        <div class="font-medium text-sm">${assessment.title || 'Assessment'}</div>
                        <div class="text-xs text-gray-500">${assessment.course_code || 'N/A'} • ${assessment.type_name || 'Assessment'}</div>
                    </div>
                    <div class="text-right text-sm">
                        ${assessment.score !== null ? `
                            <div class="font-medium text-green-600">${assessment.score}/${assessment.max_score}</div>
                        ` : dueDate ? `
                            <div class="font-medium ${isOverdue ? 'text-red-600' : isUpcoming ? 'text-orange-600' : 'text-gray-600'}">
                                ${dueDate.toLocaleDateString()}
                            </div>
                        ` : ''}
                        <div class="text-xs text-gray-500">
                            ${assessment.score !== null ? 'Graded' : isOverdue ? 'Overdue' : isUpcoming ? 'Due' : 'Pending'}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        recentAssessments.innerHTML = html;
    }

    async function loadGradeSummary() {
        try {
            // ✅ FIX: Now dashboardSummary is properly declared and accessible
            const dashboardAverage = document.getElementById('dashboardAverage');
            if (dashboardAverage && dashboardSummary && typeof dashboardSummary.gpa !== 'undefined') {
                dashboardAverage.textContent = Number(dashboardSummary.gpa).toFixed(2);
            } else if (dashboardAverage) {
                dashboardAverage.textContent = '-';
            }
        } catch (error) {
            console.error('Error loading grade summary:', error);
        }
    }

    function showError(message) {
        // Create a toast notification
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded shadow-lg z-50';
        toast.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-circle mr-2"></i>
                ${message}
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }


});
