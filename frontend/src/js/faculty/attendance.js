document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const usernameElement = document.getElementById('username');
    const logoutBtn = document.getElementById('logoutBtn');
    const courseSelect = document.getElementById('courseSelect');
    const attendanceDate = document.getElementById('attendanceDate');
    const loadRosterBtn = document.getElementById('loadRosterBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const attendanceRoster = document.getElementById('attendanceRoster');
    const rosterTitle = document.getElementById('rosterTitle');
    const rosterSubtitle = document.getElementById('rosterSubtitle');
    const studentList = document.getElementById('studentList');
    const markAllPresentBtn = document.getElementById('markAllPresentBtn');
    const saveAttendanceBtn = document.getElementById('saveAttendanceBtn');
    const successModal = document.getElementById('successModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const closeModalBtn = document.getElementById('closeModalBtn');
    
    // Counters
    const presentCount = document.getElementById('presentCount');
    const absentCount = document.getElementById('absentCount');
    const lateCount = document.getElementById('lateCount');
    const excusedCount = document.getElementById('excusedCount');
    
    // State
    let currentRoster = [];
    let currentOffering = null;
    let currentDate = null;
    
    // Initialize
    init();
    
    function init() {
        // Check authentication using the correct method name
        if (!authApi.isLoggedIn()) {
            window.location.href = '../login.html';
            return;
        }
        
        // Display username
        const user = authApi.getCurrentUser();
        if (user) {
            usernameElement.textContent = user.username;
        }
        
        // Set default date to today
        attendanceDate.valueAsDate = new Date();
        
        // Load faculty courses
        loadFacultyCourses();
        
        // Event listeners
        setupEventListeners();
    }
    
    function setupEventListeners() {
        // Logout
        logoutBtn.addEventListener('click', function() {
            authApi.logout();
        });
        
        // Course selection change
        courseSelect.addEventListener('change', function() {
            updateLoadRosterButton();
        });
        
        // Date change
        attendanceDate.addEventListener('change', function() {
            updateLoadRosterButton();
        });
        
        // Load roster
        loadRosterBtn.addEventListener('click', function() {
            loadClassRoster();
        });
        
        // Mark all present
        markAllPresentBtn.addEventListener('click', function() {
            markAllStudents('present');
        });
        
        // Save attendance
        saveAttendanceBtn.addEventListener('click', function() {
            saveAttendance();
        });
        
        // Close modal
        closeModalBtn.addEventListener('click', function() {
            successModal.classList.add('hidden');
        });
    }
    
    async function loadFacultyCourses() {
        try {
            console.log('Loading faculty courses...');
            const response = await apiClient.get('faculty/courses');
            console.log('Courses response:', response);
            
            if (response.status === 'success' && response.data.courses) {
                populateCourseSelect(response.data.courses);
            } else {
                console.error('Failed to load courses:', response);
                showError('Failed to load courses');
            }
        } catch (error) {
            console.error('Error loading courses:', error);
            showError('Failed to load courses. Please refresh the page.');
        }
    }
    
    function populateCourseSelect(courses) {
        // Clear existing options except the first one
        courseSelect.innerHTML = '<option value="">Select a course...</option>';
        
        if (!courses || courses.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No courses available';
            option.disabled = true;
            courseSelect.appendChild(option);
            return;
        }
        
        courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course.offering_id;
            option.textContent = `${course.course_code} - ${course.course_name} (Section ${course.section})`;
            option.dataset.courseName = course.course_name;
            option.dataset.courseCode = course.course_code;
            option.dataset.section = course.section;
            courseSelect.appendChild(option);
        });
        
        console.log(`Loaded ${courses.length} courses into dropdown`);
    }
    
    function updateLoadRosterButton() {
        const hasSelection = courseSelect.value && attendanceDate.value;
        loadRosterBtn.disabled = !hasSelection;
        
        if (hasSelection) {
            loadRosterBtn.classList.remove('bg-gray-400', 'cursor-not-allowed');
            loadRosterBtn.classList.add('bg-blue-600', 'hover:bg-blue-700');
        } else {
            loadRosterBtn.classList.add('bg-gray-400', 'cursor-not-allowed');
            loadRosterBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
        }
    }
    
    async function loadClassRoster() {
        const offeringId = courseSelect.value;
        const date = attendanceDate.value;
        
        if (!offeringId || !date) {
            showError('Please select both course and date');
            return;
        }
        
        console.log(`Loading roster for offering ${offeringId} on ${date}`);
        
        // Show loading
        loadingIndicator.classList.remove('hidden');
        attendanceRoster.classList.add('hidden');
        
        try {
            const response = await apiClient.get(`faculty/attendance/roster/${offeringId}?date=${date}`);
            console.log('Roster response:', response);
            
            if (response.status === 'success' && response.data.roster) {
                currentRoster = response.data.roster;
                currentOffering = offeringId;
                currentDate = date;
                
                displayRoster(response.data.roster, date);
                updateRosterHeader();
                console.log(`Loaded roster with ${response.data.roster.length} students`);
            } else {
                console.error('Failed to load roster:', response);
                showError('Failed to load class roster');
            }
        } catch (error) {
            console.error('Error loading roster:', error);
            if (error.response && error.response.status === 401) {
                showError('Session expired. Please log in again.');
                setTimeout(() => {
                    window.location.href = '../login.html';
                }, 2000);
            } else {
                showError('Failed to load class roster. Please try again.');
            }
        } finally {
            loadingIndicator.classList.add('hidden');
        }
    }
    
    function displayRoster(roster, date) {
        studentList.innerHTML = '';
        
        if (roster.length === 0) {
            studentList.innerHTML = '<p class="text-gray-500 text-center py-8">No students enrolled in this course.</p>';
            attendanceRoster.classList.remove('hidden');
            return;
        }
        
        roster.forEach((student, index) => {
            const studentRow = createStudentRow(student, index);
            studentList.appendChild(studentRow);
        });
        
        attendanceRoster.classList.remove('hidden');
        updateCounters();
    }
    
    function createStudentRow(student, index) {
        const row = document.createElement('div');
        row.className = 'flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50';
        row.dataset.enrollmentId = student.enrollment_id;
        
        row.innerHTML = `
            <div class="flex items-center space-x-4">
                <div class="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center text-gray-600 font-medium">
                    ${student.first_name[0]}${student.last_name[0]}
                </div>
                <div>
                    <div class="font-medium text-gray-900">${student.name}</div>
                    <div class="text-sm text-gray-500">ID: ${student.student_id}</div>
                    ${student.check_in_time ? `<div class="text-xs text-blue-600">Check-in: ${student.check_in_time}</div>` : ''}
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <div class="flex space-x-1">
                    <button class="attendance-btn ${student.status === 'present' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'} px-3 py-2 rounded-md text-sm hover:bg-green-700 focus:outline-none" 
                            data-status="present" data-enrollment="${student.enrollment_id}">
                        Present
                    </button>
                    <button class="attendance-btn ${student.status === 'absent' ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-700'} px-3 py-2 rounded-md text-sm hover:bg-red-700 focus:outline-none" 
                            data-status="absent" data-enrollment="${student.enrollment_id}">
                        Absent
                    </button>
                    <button class="attendance-btn ${student.status === 'late' ? 'bg-yellow-600 text-white' : 'bg-gray-200 text-gray-700'} px-3 py-2 rounded-md text-sm hover:bg-yellow-700 focus:outline-none" 
                            data-status="late" data-enrollment="${student.enrollment_id}">
                        Late
                    </button>
                    <button class="attendance-btn ${student.status === 'excused' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'} px-3 py-2 rounded-md text-sm hover:bg-blue-700 focus:outline-none" 
                            data-status="excused" data-enrollment="${student.enrollment_id}">
                        Excused
                    </button>
                </div>
            </div>
        `;
        
        // Add event listeners to attendance buttons
        const attendanceButtons = row.querySelectorAll('.attendance-btn');
        attendanceButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const status = this.dataset.status;
                const enrollmentId = this.dataset.enrollment;
                markStudentAttendance(enrollmentId, status, this);
            });
        });
        
        return row;
    }
    
    function markStudentAttendance(enrollmentId, status, buttonElement) {
        // Update UI immediately
        const row = buttonElement.closest('[data-enrollment-id]');
        const buttons = row.querySelectorAll('.attendance-btn');
        
        // Reset all buttons in this row
        buttons.forEach(btn => {
            btn.classList.remove('bg-green-600', 'bg-red-600', 'bg-yellow-600', 'bg-blue-600', 'text-white');
            btn.classList.add('bg-gray-200', 'text-gray-700');
        });
        
        // Highlight selected button
        const statusColors = {
            'present': 'bg-green-600',
            'absent': 'bg-red-600',
            'late': 'bg-yellow-600',
            'excused': 'bg-blue-600'
        };
        
        buttonElement.classList.remove('bg-gray-200', 'text-gray-700');
        buttonElement.classList.add(statusColors[status], 'text-white');
        
        // Update the roster data
        const studentIndex = currentRoster.findIndex(s => s.enrollment_id == enrollmentId);
        if (studentIndex !== -1) {
            currentRoster[studentIndex].status = status;
        }
        
        // Update counters
        updateCounters();
    }
    
    function markAllStudents(status) {
        if (!currentRoster.length) return;
        
        currentRoster.forEach(student => {
            student.status = status;
        });
        
        // Update UI
        const allButtons = document.querySelectorAll('.attendance-btn');
        allButtons.forEach(btn => {
            btn.classList.remove('bg-green-600', 'bg-red-600', 'bg-yellow-600', 'bg-blue-600', 'text-white');
            btn.classList.add('bg-gray-200', 'text-gray-700');
            
            if (btn.dataset.status === status) {
                const statusColors = {
                    'present': 'bg-green-600',
                    'absent': 'bg-red-600',
                    'late': 'bg-yellow-600',
                    'excused': 'bg-blue-600'
                };
                btn.classList.remove('bg-gray-200', 'text-gray-700');
                btn.classList.add(statusColors[status], 'text-white');
            }
        });
        
        updateCounters();
    }
    
    function updateCounters() {
        const counts = currentRoster.reduce((acc, student) => {
            acc[student.status] = (acc[student.status] || 0) + 1;
            return acc;
        }, {});
        
        presentCount.textContent = counts.present || 0;
        absentCount.textContent = counts.absent || 0;
        lateCount.textContent = counts.late || 0;
        excusedCount.textContent = counts.excused || 0;
    }
    
    function updateRosterHeader() {
        const selectedOption = courseSelect.options[courseSelect.selectedIndex];
        if (selectedOption) {
            const courseName = selectedOption.dataset.courseName;
            const courseCode = selectedOption.dataset.courseCode;
            const section = selectedOption.dataset.section;
            
            rosterTitle.textContent = `${courseCode} - ${courseName}`;
            rosterSubtitle.textContent = `Section ${section} • ${currentDate} • ${currentRoster.length} students`;
        }
    }
    
    async function saveAttendance() {
        if (!currentRoster.length) {
            showError('No roster loaded');
            return;
        }
        
        // Prepare attendance data - only include students with marked attendance
        const attendanceRecords = currentRoster
            .filter(student => student.status && student.status !== 'not_marked')
            .map(student => ({
                enrollment_id: student.enrollment_id,
                attendance_date: currentDate,
                status: student.status,
                notes: student.notes || null
            }));
        
        if (attendanceRecords.length === 0) {
            showError('Please mark attendance for at least one student');
            return;
        }
        
        // Disable save button
        saveAttendanceBtn.disabled = true;
        saveAttendanceBtn.textContent = 'Saving...';
        
        try {
            console.log('Saving attendance records:', attendanceRecords);
            const response = await apiClient.post('faculty/attendance/bulk-mark', {
                attendance_records: attendanceRecords
            });
            
            console.log('Save response:', response);
            
            if (response.status === 'success') {
                showSuccess(`Attendance saved successfully! ${response.data.summary.successful} records saved.`);
                // Optionally reload the roster to show updated data
                // loadClassRoster();
            } else {
                showError('Failed to save attendance');
            }
        } catch (error) {
            console.error('Error saving attendance:', error);
            if (error.response && error.response.status === 401) {
                showError('Session expired. Please log in again.');
                setTimeout(() => {
                    window.location.href = '../login.html';
                }, 2000);
            } else {
                showError('Failed to save attendance. Please try again.');
            }
        } finally {
            // Re-enable save button
            saveAttendanceBtn.disabled = false;
            saveAttendanceBtn.textContent = 'Save Attendance';
        }
    }
    
    function showSuccess(message) {
        modalTitle.textContent = 'Success!';
        modalMessage.textContent = message;
        
        // Update modal styling for success
        const icon = successModal.querySelector('svg');
        const iconContainer = successModal.querySelector('.bg-green-100');
        const button = closeModalBtn;
        
        iconContainer.className = 'mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4';
        icon.className = 'h-6 w-6 text-green-600';
        icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>';
        button.className = 'px-4 py-2 bg-green-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-300';
        
        successModal.classList.remove('hidden');
    }
    
    function showError(message) {
        modalTitle.textContent = 'Error';
        modalMessage.textContent = message;
        
        // Update modal styling for error
        const icon = successModal.querySelector('svg');
        const iconContainer = successModal.querySelector('.bg-green-100');
        const button = closeModalBtn;
        
        iconContainer.className = 'mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4';
        icon.className = 'h-6 w-6 text-red-600';
        button.className = 'px-4 py-2 bg-red-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-300';
        
        // Change icon to X for error
        icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>';
        
        successModal.classList.remove('hidden');
    }
});