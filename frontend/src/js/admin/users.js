// Admin User Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    const addUserBtn = document.getElementById('addUserBtn');
    
    // Table elements
    const usersTableBody = document.getElementById('usersTableBody');
    const searchInput = document.getElementById('searchInput');
    const userTypeFilter = document.getElementById('userTypeFilter');
    const statusFilter = document.getElementById('statusFilter');
    const filterBtn = document.getElementById('filterBtn');
    
    // Pagination elements
    const startRecord = document.getElementById('startRecord');
    const endRecord = document.getElementById('endRecord');
    const totalRecords = document.getElementById('totalRecords');
    const prevPage = document.getElementById('prevPage');
    const nextPage = document.getElementById('nextPage');
    
    // Modal elements
    const userModal = document.getElementById('userModal');
    const modalTitle = document.getElementById('modalTitle');
    const closeModal = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelBtn');
    const userForm = document.getElementById('userForm');
    
    // State
    let users = [];
    let currentPage = 1;
    let totalPages = 1;
    let filters = {};
    
    // Initialize
    init();
    
    function init() {
        // Check authentication
        if (!authApi.isLoggedIn()) {
            window.location.href = '../login.html';
            return;
        }
        
        // Check if user is admin
        const user = authApi.getCurrentUser();
        if (user.user_type !== 'admin') {
            alert('Access denied. Admin privileges required.');
            window.location.href = '../login.html';
            return;
        }
        
        // Display username
        if (user) {
            usernameElement.textContent = user.username;
        }
        
        // Set up event listeners
        setupEventListeners();
        
        // Load users
        loadUsers();
    }
    
    function setupEventListeners() {
        // Logout
        logoutBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to logout?')) {
                authApi.logout();
            }
        });
        
        // Add user
        addUserBtn.addEventListener('click', function() {
            openUserModal();
        });
        
        // Filters
        filterBtn.addEventListener('click', applyFilters);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });
        
        // Pagination
        prevPage.addEventListener('click', function() {
            if (currentPage > 1) {
                currentPage--;
                loadUsers();
            }
        });
        
        nextPage.addEventListener('click', function() {
            if (currentPage < totalPages) {
                currentPage++;
                loadUsers();
            }
        });
        
        // Modal
        closeModal.addEventListener('click', closeUserModal);
        cancelBtn.addEventListener('click', closeUserModal);
        userForm.addEventListener('submit', handleUserSubmit);
        
        // Close modal on outside click
        userModal.addEventListener('click', function(e) {
            if (e.target === userModal) {
                closeUserModal();
            }
        });
    }
    
    async function loadUsers() {
        try {
            // Build query parameters
            const params = new URLSearchParams({
                page: currentPage,
                limit: 10,
                ...filters
            });
            
            const response = await apiClient.get(`admin/users?${params}`);
            
            if (response.status === 'success' && response.data) {
                users = response.data.users;
                currentPage = response.data.current_page;
                totalPages = response.data.total_pages;
                
                displayUsers(users);
                updatePagination(response.data);
            }
        } catch (error) {
            console.error('Error loading users:', error);
            
            // Show demo data
            const demoUsers = [
                {
                    user_id: 1,
                    username: 'john.doe',
                    email: 'john.doe@university.edu',
                    user_type: 'student',
                    is_active: true,
                    created_at: '2024-01-15T10:30:00',
                    full_name: 'John Doe'
                },
                {
                    user_id: 2,
                    username: 'jane.smith',
                    email: 'jane.smith@university.edu',
                    user_type: 'faculty',
                    is_active: true,
                    created_at: '2024-01-10T14:20:00',
                    full_name: 'Jane Smith'
                },
                {
                    user_id: 3,
                    username: 'admin.user',
                    email: 'admin@university.edu',
                    user_type: 'admin',
                    is_active: true,
                    created_at: '2024-01-01T09:00:00',
                    full_name: 'System Admin'
                }
            ];
            displayUsers(demoUsers);
            updatePagination({ total: 3, current_page: 1, per_page: 10 });
        }
    }
    
    function displayUsers(users) {
        if (!users || users.length === 0) {
            usersTableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                        No users found
                    </td>
                </tr>
            `;
            return;
        }
        
        const html = users.map(user => `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10">
                            <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                                <i class="fas fa-user text-gray-600"></i>
                            </div>
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${user.full_name || user.username}</div>
                            <div class="text-sm text-gray-500">@${user.username}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${user.user_type === 'admin' ? 'bg-purple-100 text-purple-800' : 
                          user.user_type === 'faculty' ? 'bg-blue-100 text-blue-800' : 
                          'bg-green-100 text-green-800'}">
                        ${user.user_type}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${user.email}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                        ${user.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${formatDate(user.created_at)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button onclick="editUser(${user.user_id})" class="text-indigo-600 hover:text-indigo-900 mr-3">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button onclick="toggleUserStatus(${user.user_id}, ${user.is_active})" 
                            class="text-${user.is_active ? 'red' : 'green'}-600 hover:text-${user.is_active ? 'red' : 'green'}-900">
                        <i class="fas fa-${user.is_active ? 'ban' : 'check-circle'}"></i> 
                        ${user.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                </td>
            </tr>
        `).join('');
        
        usersTableBody.innerHTML = html;
    }
    
    function updatePagination(data) {
        const start = (data.current_page - 1) * data.per_page + 1;
        const end = Math.min(data.current_page * data.per_page, data.total);
        
        startRecord.textContent = start;
        endRecord.textContent = end;
        totalRecords.textContent = data.total;
        
        // Update button states
        prevPage.disabled = currentPage === 1;
        nextPage.disabled = currentPage === totalPages;
    }
    
    function applyFilters() {
        filters = {
            search: searchInput.value,
            user_type: userTypeFilter.value,
            status: statusFilter.value
        };
        
        // Remove empty filters
        Object.keys(filters).forEach(key => {
            if (!filters[key]) delete filters[key];
        });
        
        currentPage = 1;
        loadUsers();
    }
    
    function openUserModal(userId = null) {
        if (userId) {
            modalTitle.textContent = 'Edit User';
            // Load user data
            const user = users.find(u => u.user_id === userId);
            if (user) {
                document.getElementById('userId').value = user.user_id;
                document.getElementById('modalUsername').value = user.username;
                document.getElementById('modalEmail').value = user.email;
                document.getElementById('modalUserType').value = user.user_type;
                document.getElementById('modalStatus').value = user.is_active ? 'active' : 'inactive';
                document.getElementById('modalPassword').required = false;
            }
        } else {
            modalTitle.textContent = 'Add New User';
            userForm.reset();
            document.getElementById('modalPassword').required = true;
        }
        
        userModal.classList.remove('hidden');
    }
    
    function closeUserModal() {
        userModal.classList.add('hidden');
        userForm.reset();
    }
    
    async function handleUserSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(userForm);
        const userId = formData.get('userId');
        
        const userData = {
            username: formData.get('username'),
            email: formData.get('email'),
            user_type: formData.get('userType'),
            is_active: formData.get('status') === 'active'
        };
        
        if (formData.get('password')) {
            userData.password = formData.get('password');
        }
        
        try {
            let response;
            if (userId) {
                // Update existing user
                response = await apiClient.put(`admin/users/${userId}`, userData);
            } else {
                // Create new user
                response = await apiClient.post('admin/users', userData);
            }
            
            if (response.status === 'success') {
                alert(userId ? 'User updated successfully' : 'User created successfully');
                closeUserModal();
                loadUsers();
            }
        } catch (error) {
            console.error('Error saving user:', error);
            alert('Error saving user. Please try again.');
        }
    }
    
    // Global functions for inline buttons
    window.editUser = function(userId) {
        openUserModal(userId);
    };
    
    window.toggleUserStatus = async function(userId, isActive) {
        const action = isActive ? 'deactivate' : 'activate';
        if (confirm(`Are you sure you want to ${action} this user?`)) {
            try {
                const response = await apiClient.put(`admin/users/${userId}/status`, {
                    is_active: !isActive
                });
                
                if (response.status === 'success') {
                    alert(`User ${action}d successfully`);
                    loadUsers();
                }
            } catch (error) {
                console.error('Error updating user status:', error);
                alert('Error updating user status. Please try again.');
            }
        }
    };
    
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
});