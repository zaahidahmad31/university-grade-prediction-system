// Alert Manager for Student Dashboard
class AlertManager {
    constructor() {
        this.alertContainer = null;
        this.alertBadge = null;
        this.unreadCount = 0;
        this.apiClient = apiClient; // Use the global apiClient
    }

    init() {
        console.log('Initializing alert manager...');
        
        // Create alert UI components
        this.createAlertUI();
        
        // Load initial alerts
        this.loadAlerts();
        
        // Set up refresh interval (check every 5 minutes)
        setInterval(() => this.checkNewAlerts(), 5 * 60 * 1000);
    }

    createAlertUI() {
        // Add alert container to the page
        const alertContainerHTML = `
            <div id="alert-container" class="fixed top-20 right-4 w-96 max-h-96 overflow-y-auto z-50 hidden">
                <div class="bg-white rounded-lg shadow-xl border border-gray-200">
                    <div class="p-4 border-b border-gray-200 flex justify-between items-center">
                        <h3 class="text-lg font-semibold">Alerts</h3>
                        <button onclick="alertManager.toggleAlerts()" class="text-gray-500 hover:text-gray-700">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div id="alert-list" class="max-h-80 overflow-y-auto">
                        <div class="p-4 text-center text-gray-500">
                            <i class="fas fa-spinner fa-spin"></i> Loading alerts...
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add alert bell to navbar
        const navbar = document.querySelector('.flex.items-center.space-x-4');
        if (navbar) {
            const alertBellHTML = `
                <div class="relative ml-4">
                    <button onclick="alertManager.toggleAlerts()" class="relative p-2 text-gray-600 hover:text-gray-800 transition-colors">
                        <i class="fas fa-bell text-xl"></i>
                        <span id="alert-badge" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center hidden">
                            0
                        </span>
                    </button>
                </div>
            `;
            navbar.insertAdjacentHTML('beforeend', alertBellHTML);
        }

        // Add container to body
        document.body.insertAdjacentHTML('beforeend', alertContainerHTML);
        
        this.alertContainer = document.getElementById('alert-container');
        this.alertBadge = document.getElementById('alert-badge');
    }

    async loadAlerts(unreadOnly = false) {
        try {
            console.log('Loading alerts...');
            const response = await this.apiClient.get(`alerts/student?unread_only=${unreadOnly}`);
            
            if (response.status === 'success') {
                console.log('Alerts loaded:', response.data);
                this.displayAlerts(response.data.alerts);
                this.updateBadge(response.data.unread_count);
            }
        } catch (error) {
            console.error('Error loading alerts:', error);
            this.displayError();
        }
    }

    displayAlerts(alerts) {
        const alertList = document.getElementById('alert-list');
        
        if (!alerts || alerts.length === 0) {
            alertList.innerHTML = `
                <div class="p-4 text-center text-gray-500">
                    <i class="fas fa-check-circle text-4xl mb-2 text-green-500"></i>
                    <p>No alerts at this time</p>
                </div>
            `;
            return;
        }

        let html = '';
        alerts.forEach(alert => {
            const icon = this.getAlertIcon(alert.severity);
            const bgColor = this.getAlertColor(alert.severity);
            const readClass = alert.is_read ? 'opacity-60' : '';
            
            html += `
                <div class="p-4 border-b border-gray-200 hover:bg-gray-50 cursor-pointer ${readClass}" 
                     onclick="alertManager.handleAlertClick(${alert.alert_id})">
                    <div class="flex items-start">
                        <div class="${bgColor} rounded-full p-2 mr-3">
                            <i class="${icon} text-white text-sm"></i>
                        </div>
                        <div class="flex-1">
                            <h4 class="font-semibold text-sm">${alert.type}</h4>
                            <p class="text-sm text-gray-600 mt-1">${alert.message}</p>
                            <div class="flex justify-between items-center mt-2">
                                <span class="text-xs text-gray-500">${alert.course_name}</span>
                                <span class="text-xs text-gray-500">${this.formatDate(alert.triggered_date)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        alertList.innerHTML = html;
    }

    displayError() {
        const alertList = document.getElementById('alert-list');
        alertList.innerHTML = `
            <div class="p-4 text-center text-red-500">
                <i class="fas fa-exclamation-circle text-4xl mb-2"></i>
                <p>Error loading alerts</p>
                <button onclick="alertManager.loadAlerts()" class="mt-2 text-sm underline">
                    Try again
                </button>
            </div>
        `;
    }

    updateBadge(count) {
        this.unreadCount = count;
        
        if (count > 0) {
            this.alertBadge.textContent = count > 9 ? '9+' : count;
            this.alertBadge.classList.remove('hidden');
        } else {
            this.alertBadge.classList.add('hidden');
        }
    }

    toggleAlerts() {
        if (this.alertContainer.classList.contains('hidden')) {
            this.alertContainer.classList.remove('hidden');
            // Reload alerts when opening
            this.loadAlerts();
        } else {
            this.alertContainer.classList.add('hidden');
        }
    }

    async handleAlertClick(alertId) {
        try {
            // Mark as read
            await this.apiClient.put(`alerts/${alertId}/read`);
            
            // Reload alerts
            this.loadAlerts();
            
        } catch (error) {
            console.error('Error marking alert as read:', error);
        }
    }

    async checkNewAlerts() {
        try {
            const response = await this.apiClient.get('alerts/student?unread_only=true');
            
            if (response.status === 'success') {
                const newCount = response.data.unread_count;
                
                // Show browser notification if new alerts
                if (newCount > this.unreadCount) {
                    this.showNotification('New Alert', 'You have new academic alerts');
                }
                
                this.updateBadge(newCount);
            }
        } catch (error) {
            console.error('Error checking new alerts:', error);
        }
    }

    getAlertIcon(severity) {
        const icons = {
            'critical': 'fas fa-exclamation-triangle',
            'warning': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle'
        };
        return icons[severity] || 'fas fa-bell';
    }

    getAlertColor(severity) {
        const colors = {
            'critical': 'bg-red-500',
            'warning': 'bg-yellow-500',
            'info': 'bg-blue-500'
        };
        return colors[severity] || 'bg-gray-500';
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 60) {
            return `${diffMins} minutes ago`;
        } else if (diffMins < 1440) {
            const hours = Math.floor(diffMins / 60);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else {
            const days = Math.floor(diffMins / 1440);
            return `${days} day${days > 1 ? 's' : ''} ago`;
        }
    }

    showNotification(title, message) {
        // Check if browser supports notifications
        if (!("Notification" in window)) {
            return;
        }

        // Check permission
        if (Notification.permission === "granted") {
            new Notification(title, {
                body: message,
                icon: '/assets/images/logo.png'
            });
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then(permission => {
                if (permission === "granted") {
                    new Notification(title, {
                        body: message,
                        icon: '/assets/images/logo.png'
                    });
                }
            });
        }
    }
}

// Create global instance
window.alertManager = new AlertManager();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (localStorage.getItem('access_token')) {
            window.alertManager.init();
        }
    });
} else {
    // DOM is already loaded
    if (localStorage.getItem('access_token')) {
        window.alertManager.init();
    }
}