// Profile page functionality
document.addEventListener('DOMContentLoaded', async function() {
    // Check authentication
    if (!authApi.isLoggedIn() || authApi.getUserRole() !== 'student') {
        window.location.href = '/login.html';
        return;
    }

    // Load profile data
    await loadProfile();

    // Set up form submission
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileUpdate);
    }
});

document.getElementById('photoUpload')?.addEventListener('change', handlePhotoUpload);

async function loadProfile() {
    try {
        showLoading();
        const response = await studentApi.getProfile();
        
        if (response.status === 'success' && response.data) {
            populateProfileForm(response.data);
        }
    } catch (error) {
        showError('Failed to load profile');
    } finally {
        hideLoading();
    }
}

function populateProfileForm(data) {
    // User info
    document.getElementById('username').value = data.user.username || '';
    document.getElementById('email').value = data.user.email || '';
    
    // Student info
    document.getElementById('studentId').value = data.student.student_id || '';
    document.getElementById('firstName').value = data.student.first_name || '';
    document.getElementById('lastName').value = data.student.last_name || '';
    document.getElementById('dateOfBirth').value = data.student.date_of_birth || '';
    document.getElementById('gender').value = data.student.gender || '';
    document.getElementById('program').value = data.student.program_code || '';
    document.getElementById('yearOfStudy').value = data.student.year_of_study || '';
    
    // Display-only fields
    document.getElementById('gpa').textContent = data.student.gpa || 'N/A';
    document.getElementById('status').textContent = data.student.status || 'N/A';
    document.getElementById('enrollmentDate').textContent = 
        data.student.enrollment_date ? new Date(data.student.enrollment_date).toLocaleDateString() : 'N/A';
}

async function handleProfileUpdate(e) {
    e.preventDefault();
    
    const formData = {
        email: document.getElementById('email').value,
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        date_of_birth: document.getElementById('dateOfBirth').value,
        gender: document.getElementById('gender').value
    };
    
    try {
        showLoading();
        const response = await studentApi.updateProfile(formData);
        
        if (response.status === 'success') {
            showSuccess('Profile updated successfully');
            // Reload profile to show updated data
            await loadProfile();
        }
    } catch (error) {
        showError('Failed to update profile');
    } finally {
        hideLoading();
    }
}



async function handlePhotoUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
        showError('File size must be less than 5MB');
        return;
    }
    
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
        showError('Please upload a valid image file (JPEG, PNG, or GIF)');
        return;
    }
    
    const formData = new FormData();
    formData.append('photo', file);
    
    try {
        showLoading();
        
        const response = await fetch('/api/student/upload-photo', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.status === 'success') {
            showSuccess('Photo uploaded successfully');
            // Update photo preview
            document.getElementById('profilePhoto').src = data.data.photo_url;
        } else {
            showError(data.message || 'Failed to upload photo');
        }
    } catch (error) {
        showError('Failed to upload photo');
    } finally {
        hideLoading();
    }
}
