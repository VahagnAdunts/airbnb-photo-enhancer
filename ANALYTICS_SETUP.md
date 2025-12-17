# Google Analytics Setup Guide

This guide explains how to set up Google Analytics 4 (GA4) to track visitors to your website.

## What is Google Analytics?

Google Analytics is a free web analytics service that provides insights into:
- **Visitor Count**: How many people visit your website
- **Page Views**: Which pages are most popular
- **User Behavior**: How visitors navigate your site
- **Traffic Sources**: Where visitors come from (search engines, social media, direct, etc.)
- **Conversion Events**: Important actions like signups, downloads, etc.
- **Geographic Data**: Where your visitors are located
- **Device Information**: Desktop, mobile, or tablet usage

## How Analytics Works

1. **Tracking Script**: A small JavaScript code snippet is added to every page of your website
2. **Data Collection**: When a visitor loads a page, the script sends information to Google Analytics
3. **Data Processing**: Google processes and stores the data
4. **Reporting**: You can view reports in the Google Analytics dashboard

## Setup Instructions

### Step 1: Create a Google Analytics Account

1. Go to [Google Analytics](https://analytics.google.com/)
2. Sign in with your Google account
3. Click **"Start measuring"** or **"Create Account"**
4. Enter an account name (e.g., "Elevance AI")
5. Click **"Next"**

### Step 2: Set Up a Property

1. Enter a property name (e.g., "Elevance AI Website")
2. Select your time zone and currency
3. Click **"Next"**
4. Fill in business information (optional)
5. Click **"Create"**
6. Accept the terms of service

### Step 3: Get Your Measurement ID

1. After creating the property, you'll see a **"Web"** stream option
2. Click **"Web"** to set up web tracking
3. Enter your website URL (e.g., `https://yourdomain.com`)
4. Enter a stream name (e.g., "Main Website")
5. Click **"Create stream"**
6. You'll see your **Measurement ID** (format: `G-XXXXXXXXXX`)
7. **Copy this Measurement ID** - you'll need it in the next step

### Step 4: Configure Your Application

1. Open your `.env` file (or create one if it doesn't exist)
2. Add the following line:
   ```
   GA_MEASUREMENT_ID=G-XXXXXXXXXX
   ```
   Replace `G-XXXXXXXXXX` with your actual Measurement ID from Step 3

3. **Example:**
   ```
   GA_MEASUREMENT_ID=G-ABC123XYZ789
   ```

4. Save the file

### Step 5: Restart Your Application

Restart your Flask application for the changes to take effect:

```bash
# Stop the current server (Ctrl+C)
# Then restart it
python app.py
```

## Verifying Analytics is Working

1. Visit your website in a browser
2. Open Google Analytics dashboard
3. Go to **Reports** > **Realtime**
4. You should see your visit appear within a few seconds

**Note**: It may take 24-48 hours for full reports to populate, but real-time data should appear immediately.

## What Gets Tracked Automatically

The analytics implementation automatically tracks:

- **Page Views**: Every page visit
- **User Sessions**: How long visitors stay
- **Traffic Sources**: Where visitors come from
- **Device Type**: Desktop, mobile, or tablet
- **Geographic Location**: Country and city of visitors
- **Browser Information**: Which browsers visitors use

## Custom Event Tracking

The analytics system also includes helper functions for tracking custom events. These are available in `static/js/analytics.js`:

### Available Functions

- `trackPhotoUpload(photoCount)` - Track when photos are uploaded
- `trackPhotoEnhancement(photoCount, intensity)` - Track when photos are enhanced
- `trackDownload(photoCount)` - Track when photos are downloaded
- `trackSignup(method)` - Track user signups
- `trackLogin(method)` - Track user logins
- `trackEvent(eventName, eventParams)` - Track any custom event

### Example Usage

To track a photo upload in your JavaScript code:

```javascript
// Track when a photo is uploaded
trackPhotoUpload(3); // 3 photos uploaded

// Track when photos are enhanced
trackPhotoEnhancement(3, 'moderate');

// Track when photos are downloaded
trackDownload(2); // 2 photos downloaded

// Track a custom event
trackEvent('button_click', {
    button_name: 'Get Started',
    page: 'home'
});
```

## Viewing Analytics Data

### Accessing Reports

1. Go to [Google Analytics](https://analytics.google.com/)
2. Select your property
3. Navigate to **Reports** in the left sidebar

### Key Reports

- **Realtime**: See visitors right now
- **Acquisition**: Where visitors come from
- **Engagement**: Which pages are most popular
- **Demographics**: Age, gender, interests
- **Technology**: Browsers, devices, operating systems
- **Events**: Custom events you're tracking

### Important Metrics

- **Users**: Number of unique visitors
- **Sessions**: Number of visits
- **Page Views**: Total pages viewed
- **Bounce Rate**: Percentage of single-page visits
- **Average Session Duration**: How long visitors stay
- **Conversion Rate**: Percentage completing goals (signups, downloads, etc.)

## Privacy Considerations

- Google Analytics uses cookies to track visitors
- You should mention this in your Privacy Policy and Cookie Policy
- Consider adding a cookie consent banner for GDPR compliance (if serving EU visitors)
- Users can opt out using browser extensions or Google's opt-out tool

## Troubleshooting

### Analytics Not Working?

1. **Check Measurement ID**: Verify `GA_MEASUREMENT_ID` is set correctly in `.env`
2. **Check Browser Console**: Open browser DevTools (F12) and check for errors
3. **Verify Script Loading**: Check Network tab to see if `gtag/js` is loading
4. **Check Real-time Report**: Wait a few minutes and check Google Analytics Realtime report
5. **Clear Cache**: Clear browser cache and try again

### Common Issues

- **No data appearing**: Wait 24-48 hours for full reports (real-time should work immediately)
- **Script not loading**: Check that `GA_MEASUREMENT_ID` is set in environment variables
- **Events not tracking**: Verify `analytics.js` is loaded and functions are called correctly

## Additional Resources

- [Google Analytics Help Center](https://support.google.com/analytics)
- [GA4 Documentation](https://developers.google.com/analytics/devguides/collection/ga4)
- [Event Tracking Guide](https://developers.google.com/analytics/devguides/collection/ga4/events)

## Support

If you need help setting up analytics, refer to the Google Analytics documentation or contact support.

