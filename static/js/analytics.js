// Google Analytics 4 Helper Functions
// This file provides helper functions for tracking custom events

/**
 * Track a custom event in Google Analytics
 * @param {string} eventName - Name of the event
 * @param {object} eventParams - Additional parameters for the event
 */
function trackEvent(eventName, eventParams = {}) {
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, eventParams);
    } else {
        console.log('Analytics event:', eventName, eventParams);
    }
}

/**
 * Track page view
 * @param {string} pagePath - Path of the page
 * @param {string} pageTitle - Title of the page
 */
function trackPageView(pagePath, pageTitle) {
    if (typeof gtag !== 'undefined') {
        gtag('config', window.GA_MEASUREMENT_ID || 'G-XXXXXXXXXX', {
            page_path: pagePath,
            page_title: pageTitle
        });
    }
}

/**
 * Track photo upload event
 * @param {number} photoCount - Number of photos uploaded
 */
function trackPhotoUpload(photoCount) {
    trackEvent('photo_upload', {
        photo_count: photoCount,
        event_category: 'engagement',
        event_label: 'Photo Upload'
    });
}

/**
 * Track photo enhancement completion
 * @param {number} photoCount - Number of photos enhanced
 * @param {string} intensity - Enhancement intensity level
 */
function trackPhotoEnhancement(photoCount, intensity = 'moderate') {
    trackEvent('photo_enhanced', {
        photo_count: photoCount,
        intensity: intensity,
        event_category: 'conversion',
        event_label: 'Photo Enhancement'
    });
}

/**
 * Track download event
 * @param {number} photoCount - Number of photos downloaded
 */
function trackDownload(photoCount) {
    trackEvent('photo_download', {
        photo_count: photoCount,
        event_category: 'conversion',
        event_label: 'Photo Download'
    });
}

/**
 * Track signup event
 * @param {string} method - Signup method (email, google)
 */
function trackSignup(method = 'email') {
    trackEvent('signup', {
        method: method,
        event_category: 'conversion',
        event_label: 'User Signup'
    });
}

/**
 * Track login event
 * @param {string} method - Login method (email, google)
 */
function trackLogin(method = 'email') {
    trackEvent('login', {
        method: method,
        event_category: 'engagement',
        event_label: 'User Login'
    });
}

// Auto-track page views on page load
document.addEventListener('DOMContentLoaded', function() {
    if (typeof gtag !== 'undefined') {
        const pagePath = window.location.pathname + window.location.search;
        const pageTitle = document.title;
        trackPageView(pagePath, pageTitle);
    }
});

