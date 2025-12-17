# Google Tag Manager Setup Guide

## Quick Setup (You're Almost Done!)

Since you already have Google Tag Manager set up with ID `GTM-5RMF5T2D`, you just need to:

### Step 1: Add GTM Container ID to .env file

Add this line to your `.env` file:

```bash
GTM_CONTAINER_ID=GTM-5RMF5T2D
```

### Step 2: Restart Your Flask Application

```bash
# Stop the current server (Ctrl+C)
# Then restart it
python app.py
```

### Step 3: Configure Google Analytics in GTM

1. Go to [Google Tag Manager](https://tagmanager.google.com/)
2. Select your container (`GTM-5RMF5T2D`)
3. Click **"Add a new tag"**
4. Choose **"Google Analytics: GA4 Configuration"**
5. Enter your **Measurement ID** (format: `G-XXXXXXXXXX`)
   - If you don't have one yet, create it in [Google Analytics](https://analytics.google.com/)
6. Configure the tag trigger (usually "All Pages")
7. Click **"Save"** and **"Submit"** to publish

## ✅ That's It!

The code is already integrated into all your HTML pages. You don't need to copy-paste anything manually.

## What's Already Done

✅ GTM code added to all HTML pages (head and body)
✅ Backend configured to read `GTM_CONTAINER_ID` from environment
✅ Analytics helper functions ready to use

## How It Works

1. **GTM Container Code**: Loads on every page (already in your HTML files)
2. **Tag Configuration**: You configure tags (like GA4) in the GTM dashboard
3. **No Code Changes**: Add/remove analytics tools without touching your code
4. **Data Collection**: GTM sends data to Google Analytics automatically

## Benefits of Using GTM

- ✅ **No Code Changes**: Add new tracking tools without editing HTML
- ✅ **Easy Management**: Manage all tags from one dashboard
- ✅ **Version Control**: Track changes and rollback if needed
- ✅ **Preview Mode**: Test tags before publishing
- ✅ **Multiple Tags**: Add Facebook Pixel, LinkedIn, etc. easily

## Next Steps

1. Add `GTM_CONTAINER_ID=GTM-5RMF5T2D` to `.env`
2. Restart Flask app
3. Configure GA4 tag in GTM dashboard
4. Test using GTM Preview mode
5. Publish your container

## Testing

1. Use **GTM Preview Mode** to test tags before publishing
2. Check **Google Analytics Realtime** report to see visitors
3. Verify tags are firing correctly in browser DevTools

## Need Help?

- [GTM Documentation](https://support.google.com/tagmanager)
- [GA4 Setup Guide](https://support.google.com/analytics/answer/9304153)

