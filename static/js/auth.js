// Authentication JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const errorMessage = document.getElementById('errorMessage');
    
    // Handle login form
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await handleAuth(loginForm, '/login');
        });
    }
    
    // Handle signup form
    if (signupForm) {
        signupForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            if (password !== confirmPassword) {
                showError('Passwords do not match');
                return;
            }
            
            await handleAuth(signupForm, '/signup');
        });
    }
});

async function handleAuth(form, endpoint) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    const submitButton = form.querySelector('button[type="submit"]');
    const btnText = submitButton.querySelector('.btn-text');
    const btnLoader = submitButton.querySelector('.btn-loader');
    
    // Show loading state
    submitButton.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';
    hideError();
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            // Redirect to dashboard
            window.location.href = result.redirect || '/dashboard';
        } else {
            showError(result.error || 'An error occurred. Please try again.');
        }
    } catch (error) {
        console.error('Auth error:', error);
        showError('Network error. Please check your connection and try again.');
    } finally {
        // Reset button state
        submitButton.disabled = false;
        btnText.style.display = 'inline-block';
        btnLoader.style.display = 'none';
    }
}

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            hideError();
        }, 5000);
    }
}

function hideError() {
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.style.display = 'none';
    }
}


