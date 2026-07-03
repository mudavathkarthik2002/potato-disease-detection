// ============================================
// TOGGLE PASSWORD
// ============================================
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    const icon = event.currentTarget.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================
function showToast(message, type = 'info', duration = 4000) {
    const existingToasts = document.querySelectorAll('.toast-custom');
    existingToasts.forEach(toast => toast.remove());
    
    const colors = {
        success: '#48bb78',
        error: '#fc8181',
        warning: '#ed8936',
        info: '#667eea'
    };
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    const toast = document.createElement('div');
    toast.className = 'toast-custom';
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        border-left: 4px solid ${colors[type] || colors.info};
        z-index: 99999;
        max-width: 450px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 12px;
        font-family: 'Inter', sans-serif;
    `;
    
    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info}" style="color: ${colors[type] || colors.info}; font-size: 1.2rem;"></i>
        <span style="flex: 1;">${message}</span>
        <button onclick="this.parentElement.remove()" style="background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #999; padding: 0 5px;">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

// ============================================
// API CALL
// ============================================
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || result.detail || 'Something went wrong');
        }
        
        return result;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

// ============================================
// SET LOADING
// ============================================
function setLoading(elementId, loading = true, text = 'Loading...') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (loading) {
        element.disabled = true;
        element.dataset.original = element.innerHTML;
        element.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${text}`;
    } else {
        element.disabled = false;
        if (element.dataset.original) {
            element.innerHTML = element.dataset.original;
        }
    }
}

// ============================================
// DRAG AND DROP
// ============================================
function setupDragDrop(dropZoneId, fileInputId, previewId) {
    const dropZone = document.getElementById(dropZoneId);
    const fileInput = document.getElementById(fileInputId);
    
    if (!dropZone || !fileInput) return;
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, e => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, e => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        });
    });
    
    dropZone.addEventListener('drop', e => {
        const files = e.dataTransfer.files;
        if (files.length) {
            fileInput.files = files;
            handleFileUpload(fileInput, previewId);
        }
    });
    
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => handleFileUpload(fileInput, previewId));
}

function handleFileUpload(fileInput, previewId) {
    const file = fileInput.files[0];
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        showToast('Please upload an image file', 'error');
        fileInput.value = '';
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        showToast('File size must be less than 10MB', 'error');
        fileInput.value = '';
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById(previewId);
        if (preview) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        }
    };
    reader.readAsDataURL(file);
}