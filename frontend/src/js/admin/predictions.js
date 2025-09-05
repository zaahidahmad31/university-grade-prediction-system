document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    
    // Summary elements
    const totalPredictions = document.getElementById('totalPredictions');
    const highRiskCount = document.getElementById('highRiskCount');
    const mediumRiskCount = document.getElementById('mediumRiskCount');
    const modelAccuracy = document.getElementById('modelAccuracy');
    
    // Model performance elements
    const modelVersion = document.getElementById('modelVersion');
    const modelPrecision = document.getElementById('modelPrecision');
    const modelRecall = document.getElementById('modelRecall');
    const modelF1 = document.getElementById('modelF1');
    
    // Filter elements
    const riskFilter = document.getElementById('riskFilter');
    const gradeFilter = document.getElementById('gradeFilter');
    const courseFilter = document.getElementById('courseFilter');
    const searchInput = document.getElementById('searchInput');
    const applyFilters = document.getElementById('applyFilters');
    const exportBtn = document.getElementById('exportBtn');
    const trendDays = document.getElementById('trendDays');
    
    // Table elements
    const predictionsTableBody = document.getElementById('predictionsTableBody');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const paginationContainer = document.getElementById('paginationContainer');
    const paginationButtons = document.getElementById('paginationButtons');
    const startRecord = document.getElementById('startRecord');
    const endRecord = document.getElementById('endRecord');
    const totalRecords = document.getElementById('totalRecords');
    
    // Modal elements
    const detailsModal = document.getElementById('detailsModal');
    const closeModal = document.getElementById('closeModal');
    const modalContent = document.getElementById('modalContent');
    
    // State
    let currentPage = 1;
    const perPage = 10;
    let totalPages = 0;
    let charts = {};
    
    // Initialize
    init();
    
    function init() {
        // Check authentication
        if (!authApi.isLoggedIn()) {
            window.location.href = '../login.html';
            return;
        }
        
        // Check admin role
        if (!authApi.hasRole('admin')) {
            window.location.href = '../login.html';
            return;
        }
        
        // Display username
        const user = authApi.getCurrentUser();
        if (user) {
            usernameElement.textContent = user.username;
        }
        
        // Load data
        loadSummary();
        loadModelPerformance();
        loadCharts();
        loadPredictions();
        loadCourses();
        
        // Set up event listeners
        setupEventListeners();
    }
    
    function setupEventListeners() {
        // Logout
        logoutBtn.addEventListener('click', function() {
            authApi.logout();
        });
        
        // Filters
        applyFilters.addEventListener('click', function() {
            currentPage = 1;
            loadPredictions();
        });
        
        // Export
        exportBtn.addEventListener('click', exportPredictions);
        
        // Trend days change
        trendDays.addEventListener('change', function() {
            loadTrendChart();
        });
        
        // Modal
        closeModal.addEventListener('click', function() {
            detailsModal.classList.add('hidden');
        });
        
        // Close modal on outside click
        detailsModal.addEventListener('click', function(e) {
            if (e.target === detailsModal) {
                detailsModal.classList.add('hidden');
            }
        });
        
        // Enter key on search
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                currentPage = 1;
                loadPredictions();
            }
        });
    }
    
    async function loadSummary() {
        try {
            const response = await adminPredictionsApi.getPredictionsSummary();
            
            if (response.status === 'success' && response.data) {
                const data = response.data;
                
                // Update summary cards
                totalPredictions.textContent = data.total_predictions || 0;
                highRiskCount.textContent = data.high_risk_count || 0;
                mediumRiskCount.textContent = data.medium_risk_count || 0;
                modelAccuracy.textContent = `${(data.accuracy_rate || 0).toFixed(1)}%`;
            }
        } catch (error) {
            console.error('Error loading summary:', error);
        }
    }
    
    async function loadModelPerformance() {
        try {
            const response = await adminPredictionsApi.getModelPerformance();
            
            if (response.status === 'success' && response.data) {
                const data = response.data;
                
                modelVersion.textContent = data.model_version || '-';
                modelPrecision.textContent = data.precision ? `${data.precision.toFixed(1)}%` : '-';
                modelRecall.textContent = data.recall ? `${data.recall.toFixed(1)}%` : '-';
                modelF1.textContent = data.f1_score ? `${data.f1_score.toFixed(1)}%` : '-';
            }
        } catch (error) {
            console.error('Error loading model performance:', error);
        }
    }
    
    async function loadCharts() {
        // Load all charts
        loadRiskDistributionChart();
        loadGradeDistributionChart();
        loadTrendChart();
    }
    
    async function loadRiskDistributionChart() {
        try {
            const response = await adminPredictionsApi.getPredictionsSummary();
            
            if (response.status === 'success' && response.data) {
                const data = response.data;
                
                const ctx = document.getElementById('riskDistributionChart').getContext('2d');
                
                if (charts.riskDistribution) {
                    charts.riskDistribution.destroy();
                }
                
                charts.riskDistribution = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['High Risk', 'Medium Risk', 'Low Risk'],
                        datasets: [{
                            data: [
                                data.risk_distribution?.high || 0,
                                data.risk_distribution?.medium || 0,
                                data.risk_distribution?.low || 0
                            ],
                            backgroundColor: [
                                'rgba(239, 68, 68, 0.8)',
                                'rgba(245, 158, 11, 0.8)',
                                'rgba(34, 197, 94, 0.8)'
                            ],
                            borderWidth: 0
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
        } catch (error) {
            console.error('Error loading risk distribution chart:', error);
        }
    }
    
    async function loadGradeDistributionChart() {
        try {
            const response = await adminPredictionsApi.getPredictionsSummary();
            
            if (response.status === 'success' && response.data) {
                const data = response.data;
                
                const ctx = document.getElementById('gradeDistributionChart').getContext('2d');
                
                if (charts.gradeDistribution) {
                    charts.gradeDistribution.destroy();
                }
                
                const grades = ['A', 'B', 'C', 'D', 'F'];
                const gradeData = grades.map(grade => data.grade_distribution?.[grade] || 0);
                
                charts.gradeDistribution = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: grades,
                        datasets: [{
                            label: 'Predicted Grades',
                            data: gradeData,
                            backgroundColor: 'rgba(59, 130, 246, 0.8)',
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            }
        } catch (error) {
            console.error('Error loading grade distribution chart:', error);
        }
    }
    
    async function loadTrendChart() {
        try {
            const days = parseInt(trendDays.value);
            const response = await adminPredictionsApi.getPredictionTrends(days);
            
            if (response.status === 'success' && response.data) {
                const trends = response.data.trends;
                
                const ctx = document.getElementById('trendChart').getContext('2d');
                
                if (charts.trend) {
                    charts.trend.destroy();
                }
                
                charts.trend = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: trends.map(t => new Date(t.date).toLocaleDateString()),
                        datasets: [
                            {
                                label: 'High Risk',
                                data: trends.map(t => t.high),
                                borderColor: 'rgb(239, 68, 68)',
                                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                tension: 0.1
                            },
                            {
                                label: 'Medium Risk',
                                data: trends.map(t => t.medium),
                                borderColor: 'rgb(245, 158, 11)',
                                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                                tension: 0.1
                            },
                            {
                                label: 'Low Risk',
                                data: trends.map(t => t.low),
                                borderColor: 'rgb(34, 197, 94)',
                                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                                tension: 0.1
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }
        } catch (error) {
            console.error('Error loading trend chart:', error);
        }
    }
    
    async function loadPredictions() {
        try {
            showLoading(true);
            
            // Get filter values
            const params = {
                page: currentPage,
                per_page: perPage,
                risk_level: riskFilter.value,
                grade: gradeFilter.value,
                course_id: courseFilter.value,
                search: searchInput.value
            };
            
            // Remove empty values
            Object.keys(params).forEach(key => {
                if (!params[key]) delete params[key];
            });
            
            const response = await adminPredictionsApi.getPredictions(params);
            
            if (response.status === 'success' && response.data) {
                const predictions = response.data.predictions;
                const pagination = response.data.pagination;
                
                // Update pagination info
                totalPages = pagination.pages;
                totalRecords.textContent = pagination.total;
                startRecord.textContent = pagination.total > 0 ? ((currentPage - 1) * perPage) + 1 : 0;
                endRecord.textContent = Math.min(currentPage * perPage, pagination.total);
                
                // Render predictions
                renderPredictions(predictions);
                renderPagination();
            }
        } catch (error) {
            console.error('Error loading predictions:', error);
            showError('Failed to load predictions');
        } finally {
            showLoading(false);
        }
    }
    
    function renderPredictions(predictions) {
        if (predictions.length === 0) {
            predictionsTableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="px-6 py-4 text-center text-gray-500">
                        No predictions found
                    </td>
                </tr>
            `;
            return;
        }
        
        predictionsTableBody.innerHTML = predictions.map(pred => `
            <tr>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div>
                        <div class="text-sm font-medium text-gray-900">${pred.student.name}</div>
                        <div class="text-sm text-gray-500">${pred.student.student_id}</div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${pred.course.course_code}</div>
                    <div class="text-sm text-gray-500">${pred.course.course_name}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="text-sm font-medium">${pred.current_grade || '-'}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs font-semibold rounded-full ${getGradeClass(pred.predicted_grade)}">
                        ${pred.predicted_grade}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs font-semibold rounded-full ${getRiskClass(pred.risk_level)}">
                        ${pred.risk_level}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="text-sm font-medium">${(pred.confidence_score * 100).toFixed(0)}%</div>
                        <div class="ml-2 w-16 bg-gray-200 rounded-full h-2">
                            <div class="bg-blue-600 h-2 rounded-full" style="width: ${pred.confidence_score * 100}%"></div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${formatDate(pred.prediction_date)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <button onclick="viewPredictionDetails(${pred.prediction_id})" 
                            class="text-blue-600 hover:text-blue-900">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            </tr>
        `).join('');
    }
    
    function renderPagination() {
        let html = '';
        
        // Previous button
        html += `
            <button onclick="changePage(${currentPage - 1})" 
                    class="px-3 py-1 text-sm border rounded ${currentPage === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white hover:bg-gray-50'}"
                    ${currentPage === 1 ? 'disabled' : ''}>
                Previous
            </button>
        `;
        
        // Page numbers
        const maxButtons = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
        let endPage = Math.min(totalPages, startPage + maxButtons - 1);
        
        if (endPage - startPage < maxButtons - 1) {
            startPage = Math.max(1, endPage - maxButtons + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            html += `
                <button onclick="changePage(${i})" 
                        class="px-3 py-1 text-sm border rounded ${i === currentPage ? 'bg-blue-600 text-white' : 'bg-white hover:bg-gray-50'}">
                    ${i}
                </button>
            `;
        }
        
        // Next button
        html += `
            <button onclick="changePage(${currentPage + 1})" 
                    class="px-3 py-1 text-sm border rounded ${currentPage === totalPages ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white hover:bg-gray-50'}"
                    ${currentPage === totalPages ? 'disabled' : ''}>
                Next
            </button>
        `;
        
        paginationButtons.innerHTML = html;
    }
    
    window.changePage = function(page) {
        if (page < 1 || page > totalPages) return;
        currentPage = page;
        loadPredictions();
    };
    
    window.viewPredictionDetails = async function(predictionId) {
        try {
            const response = await adminPredictionsApi.getPredictionDetails(predictionId);
            
            if (response.status === 'success' && response.data) {
                showPredictionModal(response.data);
            }
        } catch (error) {
            console.error('Error loading prediction details:', error);
            alert('Failed to load prediction details');
        }
    };
    
    function showPredictionModal(data) {
        const pred = data.prediction;
        const student = data.student;
        const course = data.course;
        const performance = data.performance;
        
        modalContent.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Student Information -->
                <div>
                    <h4 class="font-semibold text-gray-700 mb-2">Student Information</h4>
                    <div class="bg-gray-50 p-4 rounded">
                        <p class="text-sm"><span class="font-medium">Name:</span> ${student.name}</p>
                        <p class="text-sm"><span class="font-medium">ID:</span> ${student.student_id}</p>
                        <p class="text-sm"><span class="font-medium">Email:</span> ${student.email}</p>
                        <p class="text-sm"><span class="font-medium">Program:</span> ${student.program}</p>
                        <p class="text-sm"><span class="font-medium">Year:</span> ${student.year}</p>
                    </div>
                </div>
                
                <!-- Course Information -->
                <div>
                    <h4 class="font-semibold text-gray-700 mb-2">Course Information</h4>
                    <div class="bg-gray-50 p-4 rounded">
                        <p class="text-sm"><span class="font-medium">Course:</span> ${course.course_code} - ${course.course_name}</p>
                        <p class="text-sm"><span class="font-medium">Term:</span> ${course.term}</p>
                        <p class="text-sm"><span class="font-medium">Faculty:</span> ${course.faculty}</p>
                    </div>
                </div>
            </div>
            
            <!-- Prediction Details -->
            <div class="mt-4">
                <h4 class="font-semibold text-gray-700 mb-2">Prediction Details</h4>
                <div class="bg-gray-50 p-4 rounded">
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <p class="text-sm text-gray-500">Current Grade</p>
                            <p class="text-lg font-semibold">${pred.current_grade || '-'}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">Predicted Grade</p>
                            <p class="text-lg font-semibold ${getGradeTextClass(pred.predicted_grade)}">${pred.predicted_grade}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">Risk Level</p>
                            <p class="text-lg font-semibold ${getRiskTextClass(pred.risk_level)}">${pred.risk_level}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">Confidence</p>
                            <p class="text-lg font-semibold">${(pred.confidence_score * 100).toFixed(0)}%</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Performance Metrics -->
            <div class="mt-4">
                <h4 class="font-semibold text-gray-700 mb-2">Current Performance</h4>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="bg-blue-50 p-3 rounded text-center">
                        <p class="text-sm text-gray-600">Attendance</p>
                        <p class="text-xl font-semibold text-blue-600">${performance.attendance_rate.toFixed(0)}%</p>
                    </div>
                    <div class="bg-green-50 p-3 rounded text-center">
                        <p class="text-sm text-gray-600">Assessment Avg</p>
                        <p class="text-xl font-semibold text-green-600">${performance.assessment_average.toFixed(0)}%</p>
                    </div>
                    <div class="bg-purple-50 p-3 rounded text-center">
                        <p class="text-sm text-gray-600">LMS Engagement</p>
                        <p class="text-xl font-semibold text-purple-600">${performance.lms_engagement.toFixed(0)}%</p>
                    </div>
                    <div class="bg-yellow-50 p-3 rounded text-center">
                        <p class="text-sm text-gray-600">Submission Rate</p>
                        <p class="text-xl font-semibold text-yellow-600">${performance.submission_rate.toFixed(0)}%</p>
                    </div>
                </div>
            </div>
            
            <!-- Contributing Factors -->
            ${pred.factors && Object.keys(pred.factors).length > 0 ? `
                <div class="mt-4">
                    <h4 class="font-semibold text-gray-700 mb-2">Contributing Factors</h4>
                    <div class="bg-gray-50 p-4 rounded">
                        ${Object.entries(pred.factors).map(([key, value]) => `
                            <div class="flex justify-between py-1">
                                <span class="text-sm text-gray-600">${formatFactorName(key)}</span>
                                <span class="text-sm font-medium">${formatFactorValue(value)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            <!-- Recommendations -->
            ${pred.recommendations && pred.recommendations.length > 0 ? `
                <div class="mt-4">
                    <h4 class="font-semibold text-gray-700 mb-2">Recommendations</h4>
                    <ul class="list-disc list-inside space-y-1">
                        ${pred.recommendations.map(rec => `
                            <li class="text-sm text-gray-600">${rec}</li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
        
        detailsModal.classList.remove('hidden');
    }
    
    async function loadCourses() {
        try {
            const response = await adminApi.getCourses({ limit: 100 });
            
            if (response.status === 'success' && response.data) {
                const courses = response.data.courses;
                
                courseFilter.innerHTML = '<option value="">All Courses</option>';
                courses.forEach(course => {
                    courseFilter.innerHTML += `
                        <option value="${course.course_id}">
                            ${course.course_code} - ${course.course_name}
                        </option>
                    `;
                });
            }
        } catch (error) {
            console.error('Error loading courses:', error);
        }
    }
    
    function exportPredictions() {
        const params = {
            risk_level: riskFilter.value,
            grade: gradeFilter.value,
            course_id: courseFilter.value
        };
        
        adminPredictionsApi.exportPredictions(params);
    }
    
    // Helper functions
    function showLoading(show) {
        if (show) {
            loadingIndicator.classList.remove('hidden');
            predictionsTableBody.innerHTML = '';
        } else {
            loadingIndicator.classList.add('hidden');
        }
    }
    
    function showError(message) {
        predictionsTableBody.innerHTML = `
            <tr>
                <td colspan="8" class="px-6 py-4 text-center text-red-600">
                    <i class="fas fa-exclamation-circle mr-2"></i>${message}
                </td>
            </tr>
        `;
    }
    
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }
    
    function getGradeClass(grade) {
        const classes = {
            'A': 'bg-green-100 text-green-800',
            'B': 'bg-blue-100 text-blue-800',
            'C': 'bg-yellow-100 text-yellow-800',
            'D': 'bg-orange-100 text-orange-800',
            'F': 'bg-red-100 text-red-800'
        };
        return classes[grade] || 'bg-gray-100 text-gray-800';
    }
    
    function getGradeTextClass(grade) {
        const classes = {
            'A': 'text-green-600',
            'B': 'text-blue-600',
            'C': 'text-yellow-600',
            'D': 'text-orange-600',
            'F': 'text-red-600'
        };
        return classes[grade] || 'text-gray-600';
    }
    
    function getRiskClass(risk) {
        const classes = {
            'high': 'bg-red-100 text-red-800',
            'medium': 'bg-yellow-100 text-yellow-800',
            'low': 'bg-green-100 text-green-800'
        };
        return classes[risk] || 'bg-gray-100 text-gray-800';
    }
    
    function getRiskTextClass(risk) {
        const classes = {
            'high': 'text-red-600',
            'medium': 'text-yellow-600',
            'low': 'text-green-600'
        };
        return classes[risk] || 'text-gray-600';
    }
    
    function formatFactorName(name) {
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    function formatFactorValue(value) {
        if (typeof value === 'number') {
            return value.toFixed(2);
        }
        return value;
    }
});