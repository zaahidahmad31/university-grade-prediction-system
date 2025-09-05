// Activity tracker utility
const activityTracker = {
    
    // Track page views automatically
    trackPageView: async function() {
        try {
            const pageData = {
                page_url: window.location.pathname,
                page_title: document.title,
                course_id: this.getCourseIdFromPage()
            };
            
            await apiClient.post('student/lms/track/page', pageData);
        } catch (error) {
            console.error('Failed to track page view:', error);
        }
    },
    
    // Track when viewing an assessment
    trackAssessmentView: async function(assessmentId, assessmentName) {
        try {
            await apiClient.post('student/lms/track/assessment', {
                assessment_id: assessmentId,
                assessment_name: assessmentName
            });
        } catch (error) {
            console.error('Failed to track assessment view:', error);
        }
    },
    
    // Track resource/material views
    trackResourceView: async function(resourceId, resourceName, resourceType = 'document') {
        try {
            await apiClient.post('student/lms/track/resource', {
                resource_id: resourceId,
                resource_name: resourceName,
                resource_type: resourceType
            });
        } catch (error) {
            console.error('Failed to track resource view:', error);
        }
    },
    
    // Helper to extract course ID from page
    getCourseIdFromPage: function() {
        // Try to get from URL params
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('course_id') || null;
    },
    
    // Initialize tracking on page load
    init: function() {
        // Track page view on load
        if (authApi.isLoggedIn() && authApi.hasRole('student')) {
            this.trackPageView();
            
            // Track page view every 5 minutes if still on page
            setInterval(() => {
                if (document.visibilityState === 'visible') {
                    this.trackPageView();
                }
            }, 300000); // 5 minutes
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    activityTracker.init();
});