document.addEventListener('DOMContentLoaded', function() {
    console.log('Predictions page loading...');
    
    // Get elements - with null checks
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    
    let allPredictions = [];
    let filteredPredictions = [];
    let coursesList = [];
    
    // Initialize page
    init();
    
    async function init() {
        console.log('Initializing predictions page...');
        
        // Check authentication using the correct method
        if (!authApi.isLoggedIn()) {
            console.log('User not logged in, redirecting...');
            window.location.href = '../login.html';
            return;
        }
        
        // Check role
        const userRole = authApi.getUserRole();
        console.log('User role:', userRole);
        
        if (userRole !== 'student') {
            console.log('User is not a student, redirecting...');
            window.location.href = '../login.html';
            return;
        }
        
        // Display username
        const user = authApi.getCurrentUser();
        if (user && usernameElement) {
            usernameElement.textContent = user.username;
        }
        
        // Set up logout button
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function() {
                authApi.logout();
            });
        }
        
        // Load data
        await loadCourses();
        await loadPredictions();
    }
    
    async function loadCourses() {
        try {
            console.log('Loading courses...');
            const response = await apiClient.get('student/courses');
            console.log('Courses response:', response);
            
            if (response.status === 'success' && response.data && response.data.courses) {
                coursesList = response.data.courses;
                populateCourseFilter();
            }
        } catch (error) {
            console.error('Error loading courses:', error);
        }
    }
    
    function populateCourseFilter() {
        console.log('Populating course filter with', coursesList.length, 'courses');
        
        // Try different possible IDs for the course filter
        const courseFilter = document.getElementById('courseFilter') || 
                           document.querySelector('select[name="course"]') ||
                           document.querySelector('.course-filter');
                           
        if (!courseFilter) {
            console.log('Course filter element not found');
            return;
        }
        
        courseFilter.innerHTML = '<option value="">All Courses</option>';
        
        coursesList.forEach(course => {
            const option = document.createElement('option');
            option.value = course.course_code;
            option.textContent = `${course.course_code} - ${course.course_name}`;
            courseFilter.appendChild(option);
        });
        
        console.log('Course filter populated');
    }
    
    async function loadPredictions() {
        try {
            console.log('Loading predictions...');
            const response = await apiClient.get('student/predictions');
            console.log('Predictions response:', response);
            
            if (response.status === 'success' && response.data && response.data.predictions) {
                allPredictions = response.data.predictions;
                filteredPredictions = [...allPredictions];
                console.log('Loaded', allPredictions.length, 'predictions');
                displayPredictions();
            } else {
                console.log('No predictions data in response');
                showNoPredictions();
            }
        } catch (error) {
            console.error('Error loading predictions:', error);
            showError('Failed to load predictions. Please refresh the page.');
        }
    }
    
    function displayPredictions() {
        console.log('Displaying', filteredPredictions.length, 'predictions');
        
        const tableBody = document.getElementById('predictionsTableBody');
        const tableContainer = document.querySelector('.overflow-x-auto');
        const noPredictionsMessage = document.getElementById('noPredictionsMessage');
        
        if (filteredPredictions.length === 0) {
            // Hide table, show no predictions message
            if (tableContainer) tableContainer.style.display = 'none';
            if (noPredictionsMessage) noPredictionsMessage.classList.remove('hidden');
            updatePredictionCount();
            return;
        }
        
        // Show table, hide no predictions message
        if (tableContainer) tableContainer.style.display = 'block';
        if (noPredictionsMessage) noPredictionsMessage.classList.add('hidden');
        
        if (!tableBody) {
            console.error('Table body element not found');
            return;
        }
        
        // Clear existing rows
        tableBody.innerHTML = '';
        
        // Add prediction rows
        filteredPredictions.forEach(prediction => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50 transition-colors';
            row.innerHTML = createPredictionTableRow(prediction);
            tableBody.appendChild(row);
        });
        
        // Update count and stats
        updatePredictionCount();
    }
    
    function findPredictionsContainer() {
        // Try multiple possible container IDs/classes
        return document.getElementById('predictionsTableBody') ||
               document.getElementById('predictionsList') ||
               document.getElementById('predictionsContainer') ||
               document.querySelector('.predictions-list') ||
               document.querySelector('[data-predictions-container]') ||
               document.querySelector('tbody'); // Last resort - find any tbody
    }
    
    function createPredictionTableRow(prediction) {
        const riskLevel = getRiskLevel(prediction.predicted_grade);
        const confidencePercent = Math.round(prediction.confidence_score * 100);
        
        return `
            <td class="px-6 py-4 whitespace-nowrap">
                <div>
                    <div class="text-sm font-medium text-gray-900">${prediction.course_code}</div>
                    <div class="text-sm text-gray-500">${prediction.course_name}</div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${getGradeBadge(prediction.predicted_grade)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${getRiskBadge(riskLevel)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <span class="text-sm text-gray-600 mr-2">${confidencePercent}%</span>
                    <div class="w-24 bg-gray-200 rounded-full h-2">
                        <div class="bg-blue-600 h-2 rounded-full" style="width: ${confidencePercent}%"></div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatDate(prediction.prediction_date)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button onclick="viewPredictionDetails('${prediction.prediction_id}')" 
                        class="text-blue-600 hover:text-blue-900 transition-colors">
                    <i class="fas fa-eye mr-1"></i> View Details
                </button>
            </td>
        `;
    }
    
    function createPredictionCard(prediction) {
        const riskLevel = getRiskLevel(prediction.predicted_grade);
        const confidencePercent = Math.round(prediction.confidence_score * 100);
        
        return `
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-lg font-semibold">${prediction.course_name}</h3>
                        <p class="text-sm text-gray-600">${prediction.course_code}</p>
                    </div>
                    <div class="text-right">
                        ${getGradeBadge(prediction.predicted_grade)}
                    </div>
                </div>
                <div class="space-y-2">
                    <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-600">Risk Level:</span>
                        ${getRiskBadge(riskLevel)}
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-600">Confidence:</span>
                        <div class="flex items-center">
                            <span class="text-sm font-medium mr-2">${confidencePercent}%</span>
                            <div class="w-24 bg-gray-200 rounded-full h-2">
                                <div class="bg-blue-600 h-2 rounded-full" style="width: ${confidencePercent}%"></div>
                            </div>
                        </div>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-sm text-gray-600">Prediction Date:</span>
                        <span class="text-sm">${formatDate(prediction.prediction_date)}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    function getRiskLevel(grade) {
        if (grade === 'A' || grade === 'B') return 'low';
        if (grade === 'C') return 'medium';
        return 'high';
    }
    
    function getGradeBadge(grade) {
        const colors = {
            'A': 'bg-green-100 text-green-800',
            'B': 'bg-blue-100 text-blue-800',
            'C': 'bg-yellow-100 text-yellow-800',
            'D': 'bg-orange-100 text-orange-800',
            'F': 'bg-red-100 text-red-800'
        };
        
        const colorClass = colors[grade] || 'bg-gray-100 text-gray-800';
        return `<span class="inline-flex px-3 py-1 text-sm font-semibold rounded-full ${colorClass}">${grade}</span>`;
    }
    
    function getRiskBadge(riskLevel) {
        const badges = {
            'low': '<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Low Risk</span>',
            'medium': '<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">Medium Risk</span>',
            'high': '<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">High Risk</span>'
        };
        return badges[riskLevel] || '';
    }
    
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });
    }
    
    function showNoPredictions() {
        console.log('Showing no predictions message');
        
        const tableContainer = document.querySelector('.overflow-x-auto');
        const noPredictionsMessage = document.getElementById('noPredictionsMessage');
        
        // Hide table
        if (tableContainer) tableContainer.style.display = 'none';
        
        // Show no predictions message
        if (noPredictionsMessage) noPredictionsMessage.classList.remove('hidden');
        
        // Update count
        updatePredictionCount();
    }
    
    function updatePredictionCount() {
        // Try to find count element
        const countElement = document.getElementById('predictionCount') ||
                           document.querySelector('.prediction-count') ||
                           document.querySelector('[data-prediction-count]');
                           
        if (countElement) {
            countElement.textContent = `${filteredPredictions.length} prediction${filteredPredictions.length !== 1 ? 's' : ''} found`;
        }
        
        // Update stats if they exist
        updateStats();
    }
    
    function updateStats() {
        const stats = {
            total: filteredPredictions.length,
            low: 0,
            medium: 0,
            high: 0
        };
        
        filteredPredictions.forEach(prediction => {
            const riskLevel = getRiskLevel(prediction.predicted_grade);
            stats[riskLevel]++;
        });
        
        // Try to update stat elements if they exist
        const totalElement = document.getElementById('totalCourses') || document.querySelector('[data-total-courses]');
        const lowElement = document.getElementById('lowRiskCount') || document.querySelector('[data-low-risk]');
        const mediumElement = document.getElementById('mediumRiskCount') || document.querySelector('[data-medium-risk]');
        const highElement = document.getElementById('highRiskCount') || document.querySelector('[data-high-risk]');
        
        if (totalElement) totalElement.textContent = stats.total;
        if (lowElement) lowElement.textContent = stats.low;
        if (mediumElement) mediumElement.textContent = stats.medium;
        if (highElement) highElement.textContent = stats.high;
    }
    
    function showError(message) {
        console.error(message);
        const container = findPredictionsContainer();
        
        if (container) {
            container.innerHTML = `
                <div class="text-center py-8">
                    <p class="text-red-500">${message}</p>
                </div>
            `;
        }
    }
    
    function exportToCSV() {
        console.log('Exporting to CSV...');
        
        if (filteredPredictions.length === 0) {
            alert('No predictions to export');
            return;
        }
        
        // Create CSV content
        let csv = 'Course Code,Course Name,Predicted Grade,Risk Level,Confidence,Prediction Date\n';
        
        filteredPredictions.forEach(prediction => {
            const riskLevel = getRiskLevel(prediction.predicted_grade);
            const confidencePercent = Math.round(prediction.confidence_score * 100);
            const date = formatDate(prediction.prediction_date);
            
            // Escape quotes in course name
            const courseName = prediction.course_name.replace(/"/g, '""');
            
            csv += `"${prediction.course_code}","${courseName}","${prediction.predicted_grade}","${riskLevel}","${confidencePercent}%","${date}"\n`;
        });
        
        // Create blob and download
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `grade_predictions_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('CSV export completed');
    }
    
    // Add the viewPredictionDetails function to window
    window.viewPredictionDetails = function(predictionId) {
        console.log('View details for prediction:', predictionId);
        
        // Find the prediction
        const prediction = allPredictions.find(p => p.prediction_id == predictionId);
        
        if (!prediction) {
            alert('Prediction not found');
            return;
        }
        
        // Show modal if it exists, otherwise use alert
        const modal = document.getElementById('predictionModal');
        if (modal) {
            showPredictionModal(prediction);
        } else {
            // Fallback to alert if modal doesn't exist
            showPredictionAlert(prediction);
        }
    };
    
    function showPredictionModal(prediction) {
        const riskLevel = getRiskLevel(prediction.predicted_grade);
        const confidencePercent = Math.round(prediction.confidence_score * 100);
        
        // Update modal content
        document.getElementById('modalCourseCode').textContent = prediction.course_code;
        document.getElementById('modalCourseName').textContent = prediction.course_name;
        document.getElementById('modalGrade').textContent = prediction.predicted_grade;
        document.getElementById('modalGrade').className = `text-3xl font-bold ${getGradeColor(prediction.predicted_grade)}`;
        document.getElementById('modalRisk').textContent = riskLevel.toUpperCase();
        document.getElementById('modalRisk').className = `text-xl font-semibold ${getRiskColor(riskLevel)}`;
        document.getElementById('modalConfidence').textContent = confidencePercent + '%';
        
        // Update recommendations
        const recommendations = getRecommendationsList(prediction.predicted_grade, riskLevel);
        const recommendationsList = document.getElementById('modalRecommendations');
        recommendationsList.innerHTML = recommendations.map(rec => `<li>${rec}</li>`).join('');
        
        // Store current prediction for download
        window.currentPrediction = prediction;
        
        // Show modal
        document.getElementById('predictionModal').classList.remove('hidden');
    }
    
    function showPredictionAlert(prediction) {
        const riskLevel = getRiskLevel(prediction.predicted_grade);
        const confidencePercent = Math.round(prediction.confidence_score * 100);
        
        const details = `
PREDICTION DETAILS
==================
Course: ${prediction.course_code} - ${prediction.course_name}
Predicted Grade: ${prediction.predicted_grade}
Risk Level: ${riskLevel.toUpperCase()}
Confidence: ${confidencePercent}%
Prediction Date: ${formatDate(prediction.prediction_date)}

RECOMMENDATIONS:
${getRecommendations(prediction.predicted_grade, riskLevel)}
        `;
        
        alert(details);
    }
    
    window.closePredictionModal = function() {
        const modal = document.getElementById('predictionModal');
        if (modal) {
            modal.classList.add('hidden');
        }
    };
    
    window.downloadPredictionReport = function() {
        if (!window.currentPrediction) return;
        
        const prediction = window.currentPrediction;
        const riskLevel = getRiskLevel(prediction.predicted_grade);
        const confidencePercent = Math.round(prediction.confidence_score * 100);
        
        const report = `GRADE PREDICTION REPORT
========================
Generated: ${new Date().toLocaleString()}

COURSE INFORMATION
------------------
Course Code: ${prediction.course_code}
Course Name: ${prediction.course_name}

PREDICTION RESULTS
------------------
Predicted Grade: ${prediction.predicted_grade}
Risk Level: ${riskLevel.toUpperCase()}
Confidence: ${confidencePercent}%
Prediction Date: ${formatDate(prediction.prediction_date)}

RECOMMENDATIONS
---------------
${getRecommendations(prediction.predicted_grade, riskLevel)}

NEXT STEPS
----------
1. Review the recommendations above
2. Meet with your instructor if needed
3. Utilize available campus resources
4. Monitor your progress regularly

This report was generated by the University Grade Prediction System.
For questions, please contact your academic advisor.`;
        
        const blob = new Blob([report], { type: 'text/plain;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `prediction_report_${prediction.course_code}_${new Date().toISOString().split('T')[0]}.txt`;
        link.click();
    };
    
    function getGradeColor(grade) {
        const colors = {
            'A': 'text-green-600',
            'B': 'text-blue-600',
            'C': 'text-yellow-600',
            'D': 'text-orange-600',
            'F': 'text-red-600'
        };
        return colors[grade] || 'text-gray-600';
    }
    
    function getRiskColor(riskLevel) {
        const colors = {
            'low': 'text-green-600',
            'medium': 'text-yellow-600',
            'high': 'text-red-600'
        };
        return colors[riskLevel] || 'text-gray-600';
    }
    
    function getRecommendationsList(grade, riskLevel) {
        if (riskLevel === 'high') {
            return [
                'Schedule an immediate meeting with your instructor',
                'Visit the academic support center for tutoring',
                'Review and complete all missing assignments',
                'Create a detailed study schedule',
                'Consider forming or joining a study group',
                'Speak with your academic advisor about options'
            ];
        } else if (riskLevel === 'medium') {
            return [
                'Increase your study time by 1-2 hours per week',
                'Attend all remaining classes without exception',
                'Visit instructor during office hours for clarification',
                'Review class notes daily',
                'Complete all practice problems and exercises',
                'Seek help early if you struggle with any topics'
            ];
        } else {
            return [
                'Maintain your current study habits',
                'Continue regular class attendance',
                'Stay engaged with course material',
                'Help classmates who may be struggling',
                'Consider advanced topics or extra credit',
                'Prepare thoroughly for final exams'
            ];
        }
    }
    
    function getRecommendations(grade, riskLevel) {
        if (riskLevel === 'high') {
            return `• Immediate intervention recommended
• Schedule meeting with instructor
• Consider tutoring services
• Review study habits and time management
• Check for missing assignments`;
        } else if (riskLevel === 'medium') {
            return `• Monitor progress closely
• Increase study time
• Attend all classes
• Seek help during office hours
• Form study groups with classmates`;
        } else {
            return `• Continue current study habits
• Maintain attendance
• Stay engaged in class
• Help other students if possible
• Prepare for advanced topics`;
        }
    }
    
    function handleFilterSubmit() {
        console.log('Applying filters...');
        
        const courseFilter = document.getElementById('courseFilter');
        const riskFilter = document.getElementById('riskFilter');
        const searchInput = document.getElementById('searchInput');
        
        const courseValue = courseFilter ? courseFilter.value : '';
        const riskValue = riskFilter ? riskFilter.value : '';
        const searchValue = searchInput ? searchInput.value.toLowerCase().trim() : '';
        
        console.log('Filter values:', { courseValue, riskValue, searchValue });
        
        filteredPredictions = allPredictions.filter(prediction => {
            // Course filter
            if (courseValue && prediction.course_code !== courseValue) {
                return false;
            }
            
            // Risk level filter
            const riskLevel = getRiskLevel(prediction.predicted_grade);
            if (riskValue && riskLevel !== riskValue) {
                return false;
            }
            
            // Search filter
            if (searchValue) {
                const searchText = `${prediction.course_code} ${prediction.course_name}`.toLowerCase();
                if (!searchText.includes(searchValue)) {
                    return false;
                }
            }
            
            return true;
        });
        
        console.log('Filtered predictions:', filteredPredictions.length);
        displayPredictions();
    }
    
    function clearFilters() {
        console.log('Clearing filters...');
        
        const courseFilter = document.getElementById('courseFilter');
        const riskFilter = document.getElementById('riskFilter');
        const searchInput = document.getElementById('searchInput');
        
        if (courseFilter) courseFilter.value = '';
        if (riskFilter) riskFilter.value = '';
        if (searchInput) searchInput.value = '';
        
        filteredPredictions = [...allPredictions];
        displayPredictions();
    }
    
    async function generateNewPredictions() {
        console.log('Generating new predictions...');
        
        if (!confirm('Generate new predictions for all your courses? This may take a moment.')) {
            return;
        }
        
        try {
            // Show loading state
            const generateBtn = document.getElementById('generateNewBtn');
            if (generateBtn) {
                generateBtn.disabled = true;
                generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Generating...';
            }
            
            // Make API call to generate predictions
            const response = await apiClient.post('student/predictions/generate', {});
            console.log('Generate predictions response:', response);
            
            if (response.status === 'success') {
                // Show success message
                const successCount = response.data.success_count || 0;
                const errorCount = response.data.error_count || 0;
                
                let message = `Generated ${successCount} predictions successfully`;
                if (errorCount > 0) {
                    message += ` (${errorCount} failed)`;
                }
                
                alert(message);
                
                // Reload predictions to show the new ones
                await loadPredictions();
            } else {
                throw new Error(response.message || 'Failed to generate predictions');
            }
            
        } catch (error) {
            console.error('Error generating predictions:', error);
            alert('Failed to generate predictions. Please try again.\n\nError: ' + (error.message || 'Unknown error'));
        } finally {
            // Reset button state
            const generateBtn = document.getElementById('generateNewBtn');
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<i class="fas fa-sync-alt mr-2"></i> Generate New Predictions';
            }
        }
    }
    
    // Set up event listeners for buttons and filters
    function setupEventListeners() {
        console.log('Setting up event listeners...');
        
        // Generate New Predictions button
        const generateNewBtn = document.getElementById('generateNewBtn');
        if (generateNewBtn) {
            generateNewBtn.addEventListener('click', generateNewPredictions);
            console.log('Generate button listener attached');
        }
        
        // Export button
        const exportBtn = document.getElementById('exportBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', exportToCSV);
            console.log('Export button listener attached');
        }
        
        // Filter buttons
        const applyBtn = document.getElementById('applyBtn');
        if (applyBtn) {
            applyBtn.addEventListener('click', handleFilterSubmit);
            console.log('Apply button listener attached');
        }
        
        const clearBtn = document.getElementById('clearBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', clearFilters);
            console.log('Clear button listener attached');
        }
        
        // Filter dropdowns (auto-apply on change)
        const courseFilter = document.getElementById('courseFilter');
        if (courseFilter) {
            courseFilter.addEventListener('change', handleFilterSubmit);
        }
        
        const riskFilter = document.getElementById('riskFilter');
        if (riskFilter) {
            riskFilter.addEventListener('change', handleFilterSubmit);
        }
        
        // Search input (apply on Enter)
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    handleFilterSubmit();
                }
            });
        }
        
        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', function() {
                window.location.reload();
            });
        }
    }
    
    // Call setupEventListeners after the page loads
    setupEventListeners();
});