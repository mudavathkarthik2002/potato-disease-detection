// ============================================
// LOGIN
// ============================================
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email')?.value;
    const password = document.getElementById('password')?.value;
    const remember = document.getElementById('remember')?.checked;
    
    if (!email || !password) {
        showToast('Please fill in all fields', 'error');
        return;
    }
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    if (submitBtn) setLoading(submitBtn.id || 'loginBtn', true, 'Signing in...');
    
    try {
        const result = await apiCall('/api/auth/login', 'POST', {
            email,
            password,
            remember
        });
        
        if (result.success) {
            showToast('Welcome back!', 'success');
            setTimeout(() => {
                window.location.href = result.redirect || '/dashboard';
            }, 500);
        }
    } catch (error) {
        // Error handled by apiCall
    } finally {
        if (submitBtn) setLoading(submitBtn.id || 'loginBtn', false);
    }
}

// ============================================
// REGISTER
// ============================================
async function handleRegister(event) {
    event.preventDefault();
    
    const form = event.target;
    const password = document.getElementById('password')?.value;
    const confirmPassword = document.getElementById('confirm_password')?.value;
    const terms = document.getElementById('terms')?.checked;
    
    if (!terms) {
        showToast('Please agree to the Terms of Service', 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }
    
    if (password.length < 8) {
        showToast('Password must be at least 8 characters', 'error');
        return;
    }
    
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    delete data.confirm_password;
    delete data.terms;
    
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) setLoading(submitBtn.id || 'registerBtn', true, 'Creating account...');
    
    try {
        const result = await apiCall('/api/auth/register', 'POST', data);
        
        if (result.success) {
            showToast('Account created successfully!', 'success');
            setTimeout(() => {
                window.location.href = result.redirect || '/login';
            }, 500);
        }
    } catch (error) {
        // Error handled by apiCall
    } finally {
        if (submitBtn) setLoading(submitBtn.id || 'registerBtn', false);
    }
}

// ============================================
// LOGOUT
// ============================================
async function handleLogout(e) {
    e.preventDefault();
    
    if (!confirm('Are you sure you want to logout?')) return;
    
    try {
        const result = await apiCall('/api/auth/logout', 'POST');
        if (result.success) {
            showToast('Logged out successfully', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 500);
        }
    } catch (error) {
        // Error handled by apiCall
    }
}

// ============================================
// INIT
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    document.querySelectorAll('[data-logout]').forEach(btn => {
        btn.addEventListener('click', handleLogout);
    });
});