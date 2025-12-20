// Home Page JavaScript - Free Photo Enhancement

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const progressSection = document.getElementById('progressSection');
const progressContainer = document.getElementById('progressContainer');
const resultsSection = document.getElementById('resultsSection');
const resultsGrid = document.getElementById('resultsGrid');
const signupPrompt = document.getElementById('signupPrompt');

let enhancedImages = [];
let requiresLogin = false;

// Save enhanced images to localStorage (persists across redirects)
function saveEnhancedImages() {
    if (enhancedImages.length > 0) {
        localStorage.setItem('pendingEnhancedImages', JSON.stringify(enhancedImages));
        localStorage.setItem('pendingRequiresLogin', JSON.stringify(requiresLogin));
    }
}

// Helper function to show download/signup section based on auth status
function updateDownloadSection(isAuthenticated) {
    const resultsNote = document.getElementById('resultsNote');
    const signupPromptEl = document.getElementById('signupPrompt');
    
    if (!resultsNote) {
        console.error('resultsNote element not found!');
        return;
    }
    
    console.log('Updating download section. Authenticated:', isAuthenticated, 'Images:', enhancedImages.length);
    
    if (isAuthenticated) {
        // User is logged in - show download button
        resultsNote.innerHTML = '';
        resultsNote.style.textAlign = 'center';
        
        // Add message
        const message = document.createElement('p');
        message.style.marginBottom = '1rem';
        message.textContent = `You've enhanced ${enhancedImages.length} photo${enhancedImages.length > 1 ? 's' : ''}. Ready to download!`;
        resultsNote.appendChild(message);
        
        // Create download button container
        const buttonContainer = document.createElement('div');
        buttonContainer.style.textAlign = 'center';
        
        // Create download button
        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'btn btn-primary btn-large';
        downloadBtn.textContent = `Download All ${enhancedImages.length} Photo${enhancedImages.length > 1 ? 's' : ''}`;
        downloadBtn.onclick = downloadAllImages;
        downloadBtn.style.display = 'inline-block';
        downloadBtn.style.margin = '0 auto';
        
        buttonContainer.appendChild(downloadBtn);
        resultsNote.appendChild(buttonContainer);
        
        // Hide signup prompt
        if (signupPromptEl) {
            signupPromptEl.style.display = 'none';
        }
        
        console.log('Download button created and added');
    } else {
        // User is not logged in - show signup prompt
        resultsNote.innerHTML = `<p style="margin-bottom: 1rem; text-align: center;">You've enhanced ${enhancedImages.length} photo${enhancedImages.length > 1 ? 's' : ''}. Sign up to download all!</p>`;
        if (signupPromptEl) {
            signupPromptEl.style.display = 'block';
        }
    }
}

// Load enhanced images from localStorage
function loadEnhancedImages() {
    if (!resultsGrid || !resultsSection || !progressSection) {
        return; // Elements not available yet
    }
    
    const savedImages = localStorage.getItem('pendingEnhancedImages');
    const savedRequiresLogin = localStorage.getItem('pendingRequiresLogin');
    
    if (savedImages) {
        try {
            enhancedImages = JSON.parse(savedImages);
            requiresLogin = JSON.parse(savedRequiresLogin || 'false');
            
            if (enhancedImages.length > 0) {
                displayResults();
                progressSection.style.display = 'none';
                resultsSection.style.display = 'block';
                
                // Check authentication and update UI accordingly
                checkAuthStatus();
            }
        } catch (e) {
            console.error('Error loading saved images:', e);
            localStorage.removeItem('pendingEnhancedImages');
            localStorage.removeItem('pendingRequiresLogin');
        }
    }
}

// Update navbar based on authentication status
function updateNavbar(isAuthenticated) {
    const navMenu = document.querySelector('.nav-menu');
    if (!navMenu) return;
    
    // Find the Sign In/Sign Out link - check both login and logout hrefs
    const signInLink = document.querySelector('a[href="/login"]') || 
                       document.querySelector('a[href="/logout"]') ||
                       document.querySelector('.nav-menu a.nav-link:not([href="/pricing"]):not([href="/"])');
    const getStartedLink = document.querySelector('a[href="/signup"]') || 
                          document.querySelector('a.btn[href="/signup"]');
    const homeLink = document.querySelector('.nav-menu a[href="/"]');
    
    if (isAuthenticated) {
        // Check if Dashboard link exists
        let dashboardLink = document.querySelector('a[href="/dashboard"]');
        
        // Add Dashboard link if it doesn't exist
        if (!dashboardLink) {
            dashboardLink = document.createElement('a');
            dashboardLink.href = '/dashboard';
            dashboardLink.className = 'nav-link';
            dashboardLink.textContent = 'Dashboard';
            // Insert before Sign Out link
            if (signInLink) {
                navMenu.insertBefore(dashboardLink, signInLink);
            } else {
                navMenu.appendChild(dashboardLink);
            }
        } else {
            dashboardLink.style.display = 'inline-block';
        }
        
        // Add Home link if it doesn't exist
        if (!homeLink) {
            const newHomeLink = document.createElement('a');
            newHomeLink.href = '/';
            newHomeLink.className = 'nav-link';
            newHomeLink.textContent = 'Home';
            // Insert before Dashboard link
            if (dashboardLink) {
                navMenu.insertBefore(newHomeLink, dashboardLink);
            } else if (signInLink) {
                navMenu.insertBefore(newHomeLink, signInLink);
            } else {
                navMenu.appendChild(newHomeLink);
            }
        } else {
            homeLink.style.display = 'inline-block';
        }
        
        // Change "Sign In" to "Sign Out"
        if (signInLink) {
            signInLink.textContent = 'Sign Out';
            signInLink.href = '/logout';
        }
        
        // Hide "Get Started" button
        if (getStartedLink) {
            getStartedLink.style.display = 'none';
        }
    } else {
        // Remove Home link if it exists (but keep the brand logo)
        if (homeLink && homeLink.classList.contains('nav-link')) {
            homeLink.remove();
        }
        
        // Remove Dashboard link if it exists
        const dashboardLink = document.querySelector('a[href="/dashboard"]');
        if (dashboardLink && dashboardLink.classList.contains('nav-link')) {
            dashboardLink.remove();
        }
        
        // Change "Sign Out" back to "Sign In"
        if (signInLink) {
            signInLink.textContent = 'Sign In';
            signInLink.href = '/login';
        }
        
        // Show "Get Started" button
        if (getStartedLink) {
            getStartedLink.style.display = 'inline-block';
        }
    }
}

// Check authentication status and update UI
async function checkAuthStatus() {
    // Default: assume user is not logged in
    let isAuthenticated = false;
    
    try {
        const response = await fetch('/api/check-auth');
        if (response.ok) {
            const data = await response.json();
            isAuthenticated = data.authenticated || false;
            console.log('Authentication check result:', isAuthenticated);
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
        // If check fails, default to showing signup prompt
        isAuthenticated = false;
    }
    
    // Update navbar
    updateNavbar(isAuthenticated);
    
    // Update results section UI if there are enhanced images
    if (enhancedImages.length > 0) {
        requiresLogin = !isAuthenticated;
        if (!isAuthenticated) {
            localStorage.setItem('pendingRequiresLogin', JSON.stringify(true));
        } else {
            localStorage.removeItem('pendingRequiresLogin');
        }
        
        // Make sure results section is visible
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }
        
        // Always update download section based on auth status when we have images
        // Use a small delay to ensure DOM is ready
        setTimeout(() => {
            updateDownloadSection(isAuthenticated);
        }, 50);
        
        console.log('Auth status updated. Authenticated:', isAuthenticated, 'Images:', enhancedImages.length);
    }
    
    // Return authentication status for promise chain
    return isAuthenticated;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadEnhancedImages();
    
    // Check auth status on page load to update navbar
    checkAuthStatus();
    
    // Check again after a short delay (to catch redirects after login)
    setTimeout(() => {
        if (enhancedImages.length > 0) {
            checkAuthStatus();
        }
    }, 500);
    
    // Check auth status when page becomes visible (user returns after login)
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && enhancedImages.length > 0) {
            setTimeout(() => checkAuthStatus(), 100);
        }
    });
    
    // Also check on window focus (when user returns to tab)
    window.addEventListener('focus', () => {
        if (enhancedImages.length > 0) {
            setTimeout(() => checkAuthStatus(), 100);
        }
    });
});

// Scroll to upload section
function scrollToUpload() {
    const uploadSection = document.getElementById('uploadSection');
    if (uploadSection) {
        uploadSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Initialize upload handlers
if (uploadArea && fileInput) {
    // Upload area click handler
    uploadArea.addEventListener('click', () => fileInput.click());

    // File input change handler
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFiles(Array.from(e.target.files));
        }
    });

    // Drag and drop handlers
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('image/'));
        if (files.length > 0) {
            handleFiles(files);
        }
    });
}

async function handleFiles(files) {
    // Reset UI
    enhancedImages = [];
    requiresLogin = false;
    resultsSection.style.display = 'none';
    signupPrompt.style.display = 'none';
    progressSection.style.display = 'block';
    progressContainer.innerHTML = '';

    // Create progress items for each file
    const progressItems = files.map((file, index) => {
        const progressItem = createProgressItem(file.name, index);
        progressContainer.appendChild(progressItem.element);
        return { file, progressItem, index };
    });

    // Process files one by one
    for (const { file, progressItem, index } of progressItems) {
        try {
            updateProgress(progressItem, 'Uploading...', 20);
            
            // Get enhancement settings
            const changeIntensity = document.querySelector('input[name="change_intensity"]:checked')?.value || 'moderate';
            const detailLevel = document.querySelector('input[name="detail_level"]:checked')?.value || 'moderate';
            
            // Upload and process the image
            const formData = new FormData();
            formData.append('image', file);
            formData.append('change_intensity', changeIntensity);
            formData.append('detail_level', detailLevel);
            
            updateProgress(progressItem, 'Analyzing with AI...', 40);
            
            const response = await fetch('/api/enhance', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            updateProgress(progressItem, 'Enhancing image...', 70);
            
            const result = await response.json();
            
            // Check if login is required (default to true if not authenticated)
            requiresLogin = result.requires_login !== false;
            
            updateProgress(progressItem, 'Completed!', 100);
            progressItem.element.classList.add('completed');

            // Add to results
            // Include image_id if present (means it's saved to database and requires payment)
            enhancedImages.push({
                id: result.image_id || result.photo_id || undefined, // Include ID if present
                originalName: file.name,
                enhancedUrl: result.enhanced_image_url,
                originalUrl: result.original_image_url,
                enhancements: result.enhancements
            });

        } catch (error) {
            console.error(`Error processing ${file.name}:`, error);
            updateProgress(progressItem, 'Error: ' + error.message, 0);
            progressItem.element.style.borderLeftColor = '#FF385C';
        }
    }

    // Show results
    if (enhancedImages.length > 0) {
        displayResults();
        progressSection.style.display = 'none';
        resultsSection.style.display = 'block';
        
        // Save to localStorage (persists across redirects)
        saveEnhancedImages();
        
        // Check auth status and update UI accordingly
        // Use a small delay to ensure DOM is fully updated
        setTimeout(() => {
            checkAuthStatus().then((isAuthenticated) => {
                console.log('Auth status checked, UI updated. Authenticated:', isAuthenticated);
            }).catch(err => {
                console.error('Error in checkAuthStatus:', err);
                // Default to showing signup prompt if check fails
                updateDownloadSection(false);
                updateNavbar(false);
            });
        }, 100);
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
        progressSection.style.display = 'none';
    }
}

function createProgressItem(fileName, index) {
    const item = document.createElement('div');
    item.className = 'progress-item';
    item.innerHTML = `
        <div class="progress-item-header">
            <span class="progress-item-name">${escapeHtml(fileName)}</span>
            <span class="progress-item-status">Waiting...</span>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar" style="width: 0%"></div>
        </div>
    `;
    
    return {
        element: item,
        statusElement: item.querySelector('.progress-item-status'),
        barElement: item.querySelector('.progress-bar')
    };
}

function updateProgress(progressItem, status, percentage) {
    progressItem.statusElement.textContent = status;
    progressItem.barElement.style.width = percentage + '%';
}

function displayResults() {
    resultsGrid.innerHTML = '';
    
    enhancedImages.forEach((image, index) => {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        resultItem.innerHTML = `
            <div class="result-comparison">
                <div class="comparison-side">
                    <div class="comparison-label-small">Before</div>
                    <div class="result-image-container">
                        <img src="${image.originalUrl}" alt="Original" class="result-image" loading="lazy">
                    </div>
                </div>
                <div class="comparison-side">
                    <div class="comparison-label-small">After</div>
                    <div class="result-image-container">
                        <img src="${image.enhancedUrl}" alt="Enhanced" class="result-image" loading="lazy">
                    </div>
                </div>
            </div>
        `;
        resultsGrid.appendChild(resultItem);
    });
    
    // After displaying results, check auth status to show appropriate button
    if (enhancedImages.length > 0) {
        setTimeout(() => {
            checkAuthStatus();
        }, 100);
    }
}

async function downloadAllImages() {
    // Check if payment is required
    // Photos with IDs (saved to database) require payment for authenticated users
    // Photos without IDs (preview mode) are free
    const photoIds = enhancedImages.map(img => img.id).filter(id => id !== undefined && id !== null);
    
    if (photoIds.length > 0) {
        // These are saved photos - payment is required for authenticated users
        // Check if user is authenticated
        let isAuthenticated = false;
        try {
            const authResponse = await fetch('/api/check-auth');
            if (authResponse.ok) {
                const authData = await authResponse.json();
                isAuthenticated = authData.authenticated || false;
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
        }
        
        if (isAuthenticated) {
            // User is authenticated and photos are saved - payment required
            // Check if payment has already been completed
            const paymentCompleted = await checkPaymentStatus(photoIds);
            
            if (!paymentCompleted) {
                // Payment required but not completed - redirect to payment
                await initiatePayment(photoIds);
                return;
            }
            // If payment is completed, continue to download below
        } else {
            // User not authenticated but photos have IDs - shouldn't happen, but handle gracefully
            // Redirect to login
            window.location.href = '/login?return_url=/';
            return;
        }
    }
    
    // Payment completed or not required (preview photos) - proceed with download
    enhancedImages.forEach((image, index) => {
        setTimeout(() => {
            downloadImage(image.enhancedUrl, image.originalName);
        }, index * 200);
    });
    
    // Clear saved images after successful download
    localStorage.removeItem('pendingEnhancedImages');
    localStorage.removeItem('pendingRequiresLogin');
}

// Check if payment has been completed for these photos
async function checkPaymentStatus(photoIds) {
    try {
        const response = await fetch('/api/payment/check-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ photo_ids: photoIds })
        });
        
        if (response.ok) {
            const data = await response.json();
            // Return true only if payment is confirmed as completed
            return data.success === true && data.paid === true;
        }
        // If check fails, assume payment not completed (require payment)
        console.warn('Payment status check failed, requiring payment');
        return false;
    } catch (error) {
        console.error('Error checking payment status:', error);
        // On error, assume payment not completed (require payment)
        return false;
    }
}

// Initiate payment flow
async function initiatePayment(photoIds) {
    try {
        const response = await fetch('/api/payment/create-checkout-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ photo_ids: photoIds })
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.url) {
                // Redirect to Stripe Checkout
                window.location.href = data.url;
            } else {
                alert('Error: Payment session URL not received');
            }
        } else {
            const error = await response.json();
            alert(`Payment error: ${error.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error initiating payment:', error);
        alert('An error occurred while initiating payment. Please try again.');
    }
}

function downloadImage(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename.replace(/\.[^/.]+$/, '_enhanced.jpg');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function showComparison(index) {
    const image = enhancedImages[index];
    const modal = document.getElementById('comparisonModal');
    const content = document.getElementById('comparisonContent');
    
    if (!modal || !content) return;
    
    content.innerHTML = `
        <div class="comparison-image-wrapper">
            <img src="${image.originalUrl}" alt="Original" class="comparison-image">
            <div class="comparison-label">Original</div>
        </div>
        <div class="comparison-image-wrapper">
            <img src="${image.enhancedUrl}" alt="Enhanced" class="comparison-image">
            <div class="comparison-label">Enhanced</div>
        </div>
    `;
    
    modal.classList.add('active');
}

function closeComparison() {
    const modal = document.getElementById('comparisonModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Close modal on outside click
document.addEventListener('click', (e) => {
    const modal = document.getElementById('comparisonModal');
    if (modal && e.target === modal) {
        closeComparison();
    }
});

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


