// Main Dashboard JavaScript

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const progressSection = document.getElementById('progressSection');
const progressContainer = document.getElementById('progressContainer');
const resultsSection = document.getElementById('resultsSection');
const resultsGrid = document.getElementById('resultsGrid');
const downloadAllBtn = document.getElementById('downloadAllBtn');
const selectAllBtn = document.getElementById('selectAllBtn');
const deselectAllBtn = document.getElementById('deselectAllBtn');
const selectionCount = document.getElementById('selectionCount');

let enhancedImages = [];
let paginationState = {
    currentPage: 1,
    perPage: 10,
    totalPages: 0,
    totalPhotos: 0,
    hasNext: false,
    hasPrev: false
};

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadUserStats();
    
    // Note: Auto-download after payment is handled on payment_success.html page
    // Dashboard doesn't need to trigger downloads to avoid duplicates
    
    if (uploadArea && fileInput) {
        setupUploadHandlers();
    }
    
    // Setup feature type toggle
    setupFeatureTypeToggle();
    
    // Setup pagination button handlers
    const prevPageBtn = document.getElementById('prevPageBtn');
    const nextPageBtn = document.getElementById('nextPageBtn');
    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', goToPrevPage);
    }
    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', goToNextPage);
    }
    
    // Load enhanced images from localStorage (if user was redirected from home page)
    // Use a small delay to ensure all DOM elements are ready
    setTimeout(function() {
        const hasLocalStorageImages = loadEnhancedImagesFromStorage();
        // If no localStorage images, load from database
        if (!hasLocalStorageImages) {
            loadUserPhotosFromDatabase(1);
        }
    }, 100);
});

// Check if payment was just completed and trigger auto-download
function checkAndAutoDownload() {
    // Check if payment_data is available from server
    const paymentDataScript = document.getElementById('payment-data');
    if (!paymentDataScript) {
        return;
    }
    
    try {
        const paymentData = JSON.parse(paymentDataScript.textContent);
        if (paymentData && paymentData.photos && paymentData.photos.length > 0) {
            console.log('Payment detected, starting auto-download for', paymentData.photos.length, 'photos');
            
            // Wait a bit for page to load, then start downloads
            setTimeout(function() {
                downloadPaidPhotos(paymentData.photos);
            }, 2000);
        }
    } catch (error) {
        console.error('Error parsing payment data:', error);
    }
}

// Download photos that were just paid for
function downloadPaidPhotos(photos) {
    if (!photos || photos.length === 0) {
        return;
    }
    
    let downloadIndex = 0;
    const downloadPromises = [];
    
    function downloadNext() {
        if (downloadIndex < photos.length) {
            const photo = photos[downloadIndex];
            const filename = photo.enhanced_filename.replace('enhanced_', '').replace('.jpg', '') + '.jpg';
            const url = '/api/photos/' + photo.id + '/enhanced';
            
            const downloadPromise = new Promise(function(resolve, reject) {
                fetch(url)
                    .then(function(response) {
                        return response.blob();
                    })
                    .then(function(blob) {
                        const blobUrl = window.URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.href = blobUrl;
                        link.download = filename;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        window.URL.revokeObjectURL(blobUrl);
                        console.log('Auto-downloaded:', filename);
                        resolve();
                    })
                    .catch(function(error) {
                        console.error('Error downloading image:', error);
                        window.open(url, '_blank');
                        resolve(); // Continue even if one fails
                    });
            });
            
            downloadPromises.push(downloadPromise);
            downloadIndex++;
            
            // Wait before next download
            setTimeout(downloadNext, 500);
        } else {
            // All downloads initiated
            Promise.all(downloadPromises).then(function() {
                console.log('All auto-downloads complete!');
            }).catch(function(error) {
                console.error('Some auto-downloads failed:', error);
            });
        }
    }
    
    downloadNext();
}

// Load enhanced images from localStorage when user is redirected after signup/login
// Returns true if images were loaded, false otherwise
function loadEnhancedImagesFromStorage() {
    console.log('Checking for pending enhanced images in localStorage...');
    const savedImages = localStorage.getItem('pendingEnhancedImages');
    
    if (!savedImages) {
        console.log('No pending enhanced images found in localStorage');
        return false;
    }
    
    // Ensure DOM elements are available
    const resultsSectionEl = document.getElementById('resultsSection');
    const resultsGridEl = document.getElementById('resultsGrid');
    const downloadAllBtnEl = document.getElementById('downloadAllBtn');
    
    if (!resultsSectionEl || !resultsGridEl) {
        console.error('Required DOM elements not found. Retrying in 500ms...');
        setTimeout(() => loadEnhancedImagesFromStorage(), 500);
        return;
    }
    
    try {
        enhancedImages = JSON.parse(savedImages);
        console.log('Parsed enhanced images from localStorage:', enhancedImages.length);
        
        if (enhancedImages.length > 0) {
            // Verify image data structure
            const validImages = enhancedImages.filter(img => img.enhancedUrl && img.originalUrl);
            if (validImages.length === 0) {
                console.error('No valid images found in localStorage data');
                localStorage.removeItem('pendingEnhancedImages');
                localStorage.removeItem('pendingRequiresLogin');
                return;
            }
            
            enhancedImages = validImages;
            
            // Display the enhanced images
            displayResults();
            resultsSectionEl.style.display = 'block';
            
            console.log('Successfully loaded and displayed', enhancedImages.length, 'enhanced images');
            
            // Scroll to results section after a short delay
            setTimeout(() => {
                resultsSectionEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 300);
            
            return true;
        } else {
            console.log('Enhanced images array is empty');
            localStorage.removeItem('pendingEnhancedImages');
            localStorage.removeItem('pendingRequiresLogin');
            return false;
        }
    } catch (e) {
        console.error('Error loading saved images from localStorage:', e);
        console.error('Error details:', e.message);
        localStorage.removeItem('pendingEnhancedImages');
        localStorage.removeItem('pendingRequiresLogin');
        return false;
    }
}

// Load user's previously enhanced photos from database with pagination
async function loadUserPhotosFromDatabase(page = 1) {
    console.log(`Loading user photos from database (page ${page})...`);
    
    const resultsSectionEl = document.getElementById('resultsSection');
    const resultsGridEl = document.getElementById('resultsGrid');
    const downloadAllBtnEl = document.getElementById('downloadAllBtn');
    
    if (!resultsSectionEl || !resultsGridEl) {
        console.error('Required DOM elements not found for loading database photos');
        return;
    }
    
    try {
        const response = await fetch(`/api/photos?page=${page}&per_page=${paginationState.perPage}`);
        if (!response.ok) {
            console.error('Failed to load photos from database:', response.status);
            return;
        }
        
        const data = await response.json();
        if (!data.success) {
            console.log('Failed to load photos:', data.error || 'Unknown error');
            return;
        }
        
        // Update pagination state
        if (data.pagination) {
            paginationState.currentPage = data.pagination.page;
            paginationState.totalPages = data.pagination.pages;
            paginationState.totalPhotos = data.pagination.total;
            paginationState.hasNext = data.pagination.has_next;
            paginationState.hasPrev = data.pagination.has_prev;
        }
        
        if (!data.photos || data.photos.length === 0) {
            console.log('No photos found in database');
            if (page === 1) {
                // Only hide if this is the first page load
                resultsSectionEl.style.display = 'none';
            }
            updatePaginationControls();
            return;
        }
        
        console.log(`Found ${data.photos.length} photos on page ${page} (${paginationState.totalPhotos} total)`);
        
        // Convert database photo format to display format
        enhancedImages = data.photos.map(photo => ({
            id: photo.id,
            originalName: photo.original_filename,
            originalUrl: `/api/photos/${photo.id}/original`,
            enhancedUrl: `/api/photos/${photo.id}/enhanced`,
            enhancements: photo.enhancement_settings || {},
            createdAt: photo.created_at,
            selected: false
        }));
        
        // Display the photos
        displayResults();
        resultsSectionEl.style.display = 'block';
        updatePaginationControls();
        
        console.log('Successfully loaded and displayed', enhancedImages.length, 'photos from database');
        
        // Scroll to results section after a short delay
        setTimeout(() => {
            resultsSectionEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
    } catch (error) {
        console.error('Error loading photos from database:', error);
    }
}

// Update pagination controls
function updatePaginationControls() {
    const paginationContainer = document.getElementById('paginationContainer');
    const paginationInfo = document.getElementById('paginationInfo');
    const paginationPages = document.getElementById('paginationPages');
    const prevPageBtn = document.getElementById('prevPageBtn');
    const nextPageBtn = document.getElementById('nextPageBtn');
    
    if (!paginationContainer || !paginationInfo || !paginationPages || !prevPageBtn || !nextPageBtn) {
        return;
    }
    
    // Show pagination only if there are multiple pages
    if (paginationState.totalPages > 1) {
        paginationContainer.style.display = 'flex';
        
        // Update info text
        const start = (paginationState.currentPage - 1) * paginationState.perPage + 1;
        const end = Math.min(paginationState.currentPage * paginationState.perPage, paginationState.totalPhotos);
        paginationInfo.textContent = `Showing ${start}-${end} of ${paginationState.totalPhotos} photos`;
        
        // Update page numbers
        let pageNumbers = '';
        const maxVisiblePages = 5;
        let startPage = Math.max(1, paginationState.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(paginationState.totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage < maxVisiblePages - 1) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        if (startPage > 1) {
            pageNumbers += `<button class="pagination-page-btn" onclick="goToPage(1)">1</button>`;
            if (startPage > 2) {
                pageNumbers += `<span class="pagination-ellipsis">...</span>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            if (i === paginationState.currentPage) {
                pageNumbers += `<button class="pagination-page-btn active" onclick="goToPage(${i})">${i}</button>`;
            } else {
                pageNumbers += `<button class="pagination-page-btn" onclick="goToPage(${i})">${i}</button>`;
            }
        }
        
        if (endPage < paginationState.totalPages) {
            if (endPage < paginationState.totalPages - 1) {
                pageNumbers += `<span class="pagination-ellipsis">...</span>`;
            }
            pageNumbers += `<button class="pagination-page-btn" onclick="goToPage(${paginationState.totalPages})">${paginationState.totalPages}</button>`;
        }
        
        paginationPages.innerHTML = pageNumbers;
        
        // Update prev/next buttons
        prevPageBtn.disabled = !paginationState.hasPrev;
        nextPageBtn.disabled = !paginationState.hasNext;
    } else {
        paginationContainer.style.display = 'none';
    }
}

// Navigation functions
function goToPage(page) {
    if (page >= 1 && page <= paginationState.totalPages && page !== paginationState.currentPage) {
        loadUserPhotosFromDatabase(page);
    }
}

function goToNextPage() {
    if (paginationState.hasNext) {
        goToPage(paginationState.currentPage + 1);
    }
}

function goToPrevPage() {
    if (paginationState.hasPrev) {
        goToPage(paginationState.currentPage - 1);
    }
}

// Make functions globally available for onclick handlers
window.goToPage = goToPage;
window.goToNextPage = goToNextPage;
window.goToPrevPage = goToPrevPage;

async function loadUserStats() {
    try {
        const response = await fetch('/api/user/stats');
        if (response.ok) {
            const stats = await response.json();
            const totalProcessed = document.getElementById('totalProcessed');
            if (totalProcessed) {
                totalProcessed.textContent = stats.images_processed;
            }
        }
    } catch (error) {
        console.error('Error loading user stats:', error);
    }
}

function setupUploadHandlers() {
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

// Setup feature type toggle (Enhancement vs Night Conversion)
function setupFeatureTypeToggle() {
    const featureTypeRadios = document.querySelectorAll('input[name="feature_type"]');
    const enhancementSettings = document.getElementById('enhancementSettings');
    const detailLevelSettings = document.getElementById('detailLevelSettings');
    const featureHint = document.getElementById('featureHint');
    
    if (!featureTypeRadios.length) return;
    
    function updateFeatureUI() {
        const selectedFeature = document.querySelector('input[name="feature_type"]:checked')?.value || 'enhancement';
        
        if (selectedFeature === 'night_conversion') {
            // Hide enhancement-specific settings
            if (enhancementSettings) enhancementSettings.style.display = 'none';
            if (detailLevelSettings) detailLevelSettings.style.display = 'none';
            if (featureHint) {
                featureHint.textContent = 'Convert your day photos into beautiful night photos with lights turned on';
            }
        } else {
            // Show enhancement settings
            if (enhancementSettings) enhancementSettings.style.display = 'block';
            if (detailLevelSettings) detailLevelSettings.style.display = 'block';
            if (featureHint) {
                featureHint.textContent = 'Enhance your photos for better Airbnb and Booking.com listings';
            }
        }
    }
    
    // Add event listeners
    featureTypeRadios.forEach(radio => {
        radio.addEventListener('change', updateFeatureUI);
    });
    
    // Initialize UI
    updateFeatureUI();
}

async function handleFiles(files) {
    // Reset UI
    enhancedImages = [];
    resultsSection.style.display = 'none';
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
            
            // Get feature type
            const featureType = document.querySelector('input[name="feature_type"]:checked')?.value || 'enhancement';
            
            // Upload and process the image
            const formData = new FormData();
            formData.append('image', file);
            
            // Determine which endpoint to use
            let endpoint = '/api/enhance';
            let processingMessage = 'Analyzing with AI...';
            
            if (featureType === 'night_conversion') {
                endpoint = '/api/convert-to-night';
                processingMessage = 'Converting to night...';
            } else {
                // Get enhancement settings only for enhancement feature
                const changeIntensity = document.querySelector('input[name="change_intensity"]:checked')?.value || 'moderate';
                const detailLevel = document.querySelector('input[name="detail_level"]:checked')?.value || 'moderate';
                formData.append('change_intensity', changeIntensity);
                formData.append('detail_level', detailLevel);
            }
            
            updateProgress(progressItem, processingMessage, 40);
            
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            // Update processing message for the final step
            processingMessage = featureType === 'night_conversion' ? 'Converting to night...' : 'Enhancing image...';
            updateProgress(progressItem, processingMessage, 70);
            
            const result = await response.json();
            
            updateProgress(progressItem, 'Completed!', 100);
            progressItem.element.classList.add('completed');

            // Add to results
            // If image_id/photo_id exists, this is a saved photo that requires payment
            // If no id, it's a preview photo (free download)
            enhancedImages.push({
                id: result.image_id || result.photo_id || undefined, // Use image_id from backend
                originalName: file.name,
                enhancedUrl: result.enhanced_image_url,
                originalUrl: result.original_image_url,
                enhancements: result.enhancements,
                conversionType: result.conversion_type || 'enhancement' // Track conversion type
            });

            // Update stats
            loadUserStats();

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
        
        // After successful uploads, reload from database to show paginated view
        // This ensures new photos appear in the correct pagination context
        setTimeout(() => {
            loadUserPhotosFromDatabase(1);
        }, 1000);
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
    
    // Initialize selected state for all images if not already set
    enhancedImages.forEach((image, index) => {
        if (image.selected === undefined) {
            image.selected = false;
        }
    });
    
    enhancedImages.forEach((image, index) => {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        resultItem.dataset.index = index;
        resultItem.innerHTML = `
            <div class="result-item-checkbox">
                <input type="checkbox" id="photo-${index}" class="photo-checkbox" ${image.selected ? 'checked' : ''} onchange="togglePhotoSelection(${index}); event.stopPropagation();">
                <label for="photo-${index}" class="checkbox-label"></label>
            </div>
            <div class="result-comparison">
                <div class="comparison-side">
                    <div class="comparison-label-small">${image.conversionType === 'night_conversion' ? 'Day' : 'Before'}</div>
                    <div class="result-image-container">
                        <img src="${image.originalUrl}" alt="${image.conversionType === 'night_conversion' ? 'Original day property photo' : 'Original'}" class="result-image" loading="lazy">
                    </div>
                </div>
                <div class="comparison-side">
                    <div class="comparison-label-small">${image.conversionType === 'night_conversion' ? 'Night' : 'After'}</div>
                    <div class="result-image-container">
                        <img src="${image.enhancedUrl}" alt="${image.conversionType === 'night_conversion' ? 'Night-converted property photo with lights on' : 'Enhanced'}" class="result-image" loading="lazy">
                    </div>
                </div>
            </div>
        `;
        
        // Add click handler to the entire photo item
        resultItem.addEventListener('click', (e) => {
            // Don't toggle if clicking on the checkbox (it handles its own event)
            if (e.target.closest('.result-item-checkbox')) {
                return;
            }
            togglePhotoSelection(index);
        });
        
        resultsGrid.appendChild(resultItem);
    });
    
    updateSelectionUI();
}

function downloadImage(url, filename) {
    // Handle both base64 data URLs and regular URLs
    if (url.startsWith('data:')) {
        // Base64 data URL - direct download
    const link = document.createElement('a');
    link.href = url;
    link.download = filename.replace(/\.[^/.]+$/, '_enhanced.jpg');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    } else {
        // Regular URL - fetch and download
        fetch(url)
            .then(response => response.blob())
            .then(blob => {
                const blobUrl = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = blobUrl;
                link.download = filename.replace(/\.[^/.]+$/, '_enhanced.jpg');
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(blobUrl);
            })
            .catch(error => {
                console.error('Error downloading image:', error);
                // Fallback: open in new tab
                window.open(url, '_blank');
            });
    }
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

// Selection functions
function togglePhotoSelection(index) {
    if (enhancedImages[index]) {
        enhancedImages[index].selected = !enhancedImages[index].selected;
        
        // Update the checkbox visual state to match
        const checkbox = document.getElementById(`photo-${index}`);
        if (checkbox) {
            checkbox.checked = enhancedImages[index].selected;
        }
        
        updateSelectionUI();
    }
}

function selectAllPhotos() {
    enhancedImages.forEach(image => {
        image.selected = true;
    });
    updateSelectionUI();
    // Update checkboxes
    document.querySelectorAll('.photo-checkbox').forEach(checkbox => {
        checkbox.checked = true;
    });
}

function deselectAllPhotos() {
    enhancedImages.forEach(image => {
        image.selected = false;
    });
    updateSelectionUI();
    // Update checkboxes
    document.querySelectorAll('.photo-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
}

function updateSelectionUI() {
    const selectedCount = enhancedImages.filter(img => img.selected).length;
    const totalCount = enhancedImages.length;
    
    // Update selection count
    if (selectionCount) {
        selectionCount.textContent = `${selectedCount} selected`;
    }
    
    // Update download button
    updateDownloadButton();
}

function updateDownloadButton() {
    if (downloadAllBtn) {
        const selectedCount = enhancedImages.filter(img => img.selected).length;
        const totalPrice = (selectedCount * 0.55).toFixed(2);
        
        if (selectedCount === 0) {
            downloadAllBtn.textContent = 'Download Selected (0)';
            downloadAllBtn.disabled = true;
            downloadAllBtn.style.opacity = '0.5';
            downloadAllBtn.style.cursor = 'not-allowed';
        } else {
            downloadAllBtn.textContent = `Download ${selectedCount} Photo${selectedCount > 1 ? 's' : ''} - $${totalPrice}`;
            downloadAllBtn.disabled = false;
            downloadAllBtn.style.opacity = '1';
            downloadAllBtn.style.cursor = 'pointer';
        }
    }
}

// Make functions globally accessible
window.togglePhotoSelection = togglePhotoSelection;
window.selectAllPhotos = selectAllPhotos;
window.deselectAllPhotos = deselectAllPhotos;

// Select All button
if (selectAllBtn) {
    selectAllBtn.addEventListener('click', selectAllPhotos);
}

// Deselect All button
if (deselectAllBtn) {
    deselectAllBtn.addEventListener('click', deselectAllPhotos);
}

// Download selected button with payment check
if (downloadAllBtn) {
    downloadAllBtn.addEventListener('click', async () => {
        const selectedImages = enhancedImages.filter(img => img.selected);
        
        if (selectedImages.length === 0) {
            alert('Please select at least one photo to download.');
            return;
        }
        
        // Check if payment is required and completed
        // Only photos with IDs (from database) require payment
        // Photos without IDs (preview/localStorage) are free
        const photoIds = selectedImages.map(img => img.id).filter(id => id !== undefined && id !== null);
        
        if (photoIds.length > 0) {
            // These are saved photos - payment is ALWAYS required
            // Check if payment has already been completed
            const paymentCompleted = await checkPaymentStatus(photoIds);
            
            if (!paymentCompleted) {
                // Payment required but not completed - redirect to payment
                await initiatePayment(photoIds);
                return;
            }
            // If payment is completed, continue to download below
        }
        
        // Payment completed or not required (preview photos) - proceed with download
        selectedImages.forEach((image, index) => {
            setTimeout(() => {
                downloadImage(image.enhancedUrl, image.originalName);
            }, index * 200);
        });
        
        // Clear localStorage after download (only if all were from localStorage)
        const allFromLocalStorage = enhancedImages.every(img => img.enhancedUrl && img.enhancedUrl.startsWith('data:'));
        if (allFromLocalStorage) {
            localStorage.removeItem('pendingEnhancedImages');
            localStorage.removeItem('pendingRequiresLogin');
        }
    });
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
        // Show loading state
        if (downloadAllBtn) {
            downloadAllBtn.disabled = true;
            downloadAllBtn.textContent = 'Processing...';
        }
        
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
                if (downloadAllBtn) {
                    downloadAllBtn.disabled = false;
                    updateDownloadButton();
                }
            }
        } else {
            const error = await response.json();
            alert(`Payment error: ${error.error || 'Unknown error'}`);
            if (downloadAllBtn) {
                downloadAllBtn.disabled = false;
                updateDownloadButton();
            }
        }
    } catch (error) {
        console.error('Error initiating payment:', error);
        alert('An error occurred while initiating payment. Please try again.');
        if (downloadAllBtn) {
            downloadAllBtn.disabled = false;
            updateDownloadButton();
        }
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
