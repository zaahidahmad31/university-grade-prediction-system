document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const gradesContainer = document.getElementById('gradesContainer');
    const noGrades = document.getElementById('noGrades');
    
    // Stats elements
    const overallAverage = document.getElementById('overallAverage');
    const gradedCount = document.getElementById('gradedCount');
    const pendingCount = document.getElementById('pendingCount');
    const totalCount = document.getElementById('totalCount');
    
    // Charts
    let gradeDistributionChart = null;
    let gradeTrendChart = null;
    
    // State
    let gradesData = null;
    
    // Initialize
    init();
    
    function init() {
        // Check authentication
        if (!authApi.isLoggedIn()) {
            window.location.href = '../login.html';
            return;
        }
        
        // Check user role
        if (!authApi.hasRole('student')) {
            window.location.href = '../login.html';
            return;
        }
        
        // Display username
        const user = authApi.getCurrentUser();
        if (user) {
            usernameElement.textContent = user.username;
        }
        
        // Load grades
        loadGrades();
        
        // Set up event listeners
        setupEventListeners();
    }
    
    function setupEventListeners() {
        // Logout
        logoutBtn.addEventListener('click', function() {
            authApi.logout();
        });
    }
    
    async function loadGrades() {
        try {
            showLoading(true);
            
            console.log('Loading grade summary...');
            const response = await apiClient.get('student/grades/summary');
            console.log('Grade summary response:', response);
            
            if (response.status === 'success' && response.data) {
                gradesData = response.data;
                
                // Load detailed assessments for charts
                await loadDetailedAssessments();
                
                updateStats();
                createCharts();
                displayGradesByCategory();
            } else {
                showNoGrades();
            }
        } catch (error) {
            console.error('Error loading grades:', error);
            if (error.response && error.response.status === 401) {
                authApi.logout();
            } else {
                showError('Failed to load grades. Please refresh the page.');
            }
        } finally {
            showLoading(false);
        }
    }
    
    async function loadDetailedAssessments() {
        try {
            const response = await apiClient.get('student/assessments/all');
            if (response.status === 'success' && response.data) {
                gradesData.detailedAssessments = response.data.courses;
            }
        } catch (error) {
            console.error('Error loading detailed assessments:', error);
        }
    }
    
    function updateStats() {
        overallAverage.textContent = gradesData.overall_percentage + '%';
        gradedCount.textContent = gradesData.graded_assessments;
        pendingCount.textContent = gradesData.pending_assessments;
        totalCount.textContent = gradesData.total_assessments;
    }
    
    function createCharts() {
        createGradeDistributionChart();
        createGradeTrendChart();
    }
    
    function createGradeDistributionChart() {
        const ctx = document.getElementById('gradeDistributionChart').getContext('2d');
        
        const gradeData = gradesData.grade_distribution;
        const labels = Object.keys(gradeData);
        const data = Object.values(gradeData);
        
        if (gradeDistributionChart) {
            gradeDistributionChart.destroy();
        }
        
        gradeDistributionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#10B981', // Green for A
                        '#3B82F6', // Blue for B
                        '#F59E0B', // Yellow for C
                        '#F97316', // Orange for D
                        '#EF4444'  // Red for F
                    ],
                    borderWidth: 2,
                    borderColor: '#FFFFFF'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    function createGradeTrendChart() {
        const ctx = document.getElementById('gradeTrendChart').getContext('2d');
        
        // Prepare trend data from detailed assessments
        let trendData = [];
        if (gradesData.detailedAssessments) {
            gradesData.detailedAssessments.forEach(course => {
                course.assessments.forEach(assessment => {
                    if (assessment.percentage !== null) {
                        trendData.push({
                            date: new Date(assessment.submission_date || assessment.due_date),
                            percentage: assessment.percentage,
                            title: assessment.title
                        });
                    }
                });
            });
        }
        
        // Sort by date
        trendData.sort((a, b) => a.date - b.date);
        
        const labels = trendData.map(item => item.date.toLocaleDateString());
        const percentages = trendData.map(item => item.percentage);
        
        if (gradeTrendChart) {
            gradeTrendChart.destroy();
        }
        
        gradeTrendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Grade Percentage',
                    data: percentages,
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                const index = context[0].dataIndex;
                                return trendData[index].title;
                            },
                            label: function(context) {
                                return 'Score: ' + context.parsed.y + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    function displayGradesByCategory() {
        if (!gradesData.detailedAssessments || gradesData.detailedAssessments.length === 0) {
            showNoGrades();
            return;
        }
        
        gradesContainer.innerHTML = '';
        
        gradesData.detailedAssessments.forEach(course => {
            const gradedAssessments = course.assessments.filter(a => a.percentage !== null);
            if (gradedAssessments.length > 0) {
                const courseSection = createCourseGradeSection(course, gradedAssessments);
                gradesContainer.appendChild(courseSection);
            }
        });
        
        gradesContainer.classList.remove('hidden');
        noGrades.classList.add('hidden');
    }
    
    function createCourseGradeSection(course, assessments) {
        const section = document.createElement('div');
        section.className = 'bg-white rounded-lg shadow-md overflow-hidden';
        
        // Calculate course average
        const courseAverage = assessments.reduce((sum, a) => sum + a.percentage, 0) / assessments.length;
        
        section.innerHTML = `
            <div class="bg-gray-50 px-6 py-4 border-b">
                <div class="flex justify-between items-center">
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900">${course.course_code} - ${course.course_name}</h3>
                        <p class="text-sm text-gray-600">${assessments.length} graded assessment(s)</p>
                    </div>
                    <div class="text-right">
                        <div class="text-2xl font-bold text-blue-600">${courseAverage.toFixed(1)}%</div>
                        <div class="text-sm text-gray-500">Course Average</div>
                    </div>
                </div>
            </div>
            <div class="p-6">
                <div class="overflow-x-auto">
                    <table class="min-w-full">
                        <thead>
                            <tr class="border-b">
                                <th class="text-left py-2 font-medium text-gray-700">Assessment</th>
                                <th class="text-left py-2 font-medium text-gray-700">Type</th>
                                <th class="text-left py-2 font-medium text-gray-700">Score</th>
                                <th class="text-left py-2 font-medium text-gray-700">Grade</th>
                                <th class="text-left py-2 font-medium text-gray-700">Date</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100">
                            ${assessments.map(assessment => createGradeRow(assessment)).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        return section;
    }
    
    function createGradeRow(assessment) {
        const submissionDate = assessment.submission_date ? new Date(assessment.submission_date) : null;
        const gradeBadge = getGradeBadge(assessment.percentage);
        
        return `
            <tr class="hover:bg-gray-50">
                <td class="py-3">
                    <div>
                        <div class="font-medium text-gray-900">${assessment.title}</div>
                        ${assessment.feedback ? `<div class="text-xs text-gray-500 mt-1">${assessment.feedback}</div>` : ''}
                    </div>
                </td>
                <td class="py-3 text-sm text-gray-600">${assessment.type_name}</td>
                <td class="py-3">
                    <div class="text-sm">
                        <span class="font-medium">${assessment.score}/${assessment.max_score}</span>
                        <span class="text-gray-500">(${assessment.percentage.toFixed(1)}%)</span>
                    </div>
                </td>
                <td class="py-3">${gradeBadge}</td>
                <td class="py-3 text-sm text-gray-600">
                    ${submissionDate ? submissionDate.toLocaleDateString() : 'Not specified'}
                </td>
            </tr>
        `;
    }
    
    function getGradeBadge(percentage) {
        let grade, colorClass;
        if (percentage >= 90) {
            grade = 'A';
            colorClass = 'bg-green-100 text-green-800';
        } else if (percentage >= 80) {
            grade = 'B';
            colorClass = 'bg-blue-100 text-blue-800';
        } else if (percentage >= 70) {
            grade = 'C';
            colorClass = 'bg-yellow-100 text-yellow-800';
        } else if (percentage >= 60) {
            grade = 'D';
            colorClass = 'bg-orange-100 text-orange-800';
        } else {
            grade = 'F';
            colorClass = 'bg-red-100 text-red-800';
        }
        
        return `<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${colorClass}">${grade}</span>`;
    }
    
    function showLoading(show) {
        if (show) {
            loadingIndicator.classList.remove('hidden');
            gradesContainer.classList.add('hidden');
            noGrades.classList.add('hidden');
        } else {
            loadingIndicator.classList.add('hidden');
        }
    }
    
    function showNoGrades() {
        gradesContainer.classList.add('hidden');
        noGrades.classList.remove('hidden');
    }
    
    function showError(message) {
        console.error(message);
        alert(message);
    }
});