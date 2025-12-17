# Render Deployment Guide - Step by Step

This guide will walk you through deploying your application to Render.com.

## Prerequisites

Before starting, make sure you have:
- ✅ A GitHub account
- ✅ Your code pushed to a GitHub repository
- ✅ All your API keys ready (Gemini, Stripe, etc.)

---

## Step 1: Prepare Your GitHub Repository

### 1.1 Initialize Git (if not already done)

```bash
cd /Users/vahagn/Desktop/Ai\ Agents/airbnb_photoh_enhancment

# Check if git is initialized
git status

# If not initialized, run:
git init
git add .
git commit -m "Initial commit - Ready for deployment"
```

### 1.2 Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click the **"+"** icon → **"New repository"**
3. Repository name: `airbnb-photo-enhancer` (or your preferred name)
4. Description: "AI-powered photo enhancement for Airbnb listings"
5. Choose **Public** or **Private**
6. **DO NOT** initialize with README, .gitignore, or license (you already have these)
7. Click **"Create repository"**

### 1.3 Push Your Code to GitHub

GitHub will show you commands. Run these in your terminal:

```bash
# Add your GitHub repository as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/airbnb-photo-enhancer.git

# Rename branch to main (if needed)
git branch -M main

# Push your code
git push -u origin main
```

**Note**: If you get authentication errors, you may need to:
- Use a Personal Access Token instead of password
- Or set up SSH keys

---

## Step 2: Create Render Account

### 2.1 Sign Up for Render

1. Go to [render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Sign up with your GitHub account (recommended) or email
4. Verify your email if required

### 2.2 Connect GitHub Account

1. After signing up, Render will ask to connect GitHub
2. Click **"Connect GitHub"** or **"Authorize Render"**
3. Select the repositories you want to give access to
4. Click **"Install"** or **"Authorize"**

---

## Step 3: Create New Web Service

### 3.1 Start New Service

1. In Render Dashboard, click **"New +"** button (top right)
2. Select **"Web Service"**

### 3.2 Connect Repository

1. You'll see a list of your GitHub repositories
2. Find and click on **"airbnb-photo-enhancer"** (or your repo name)
3. Click **"Connect"**

### 3.3 Configure Service

Fill in the following details:

**Name:**
```
airbnb-photo-enhancer
```
(or any name you prefer)

**Region:**
```
Oregon (US West)
```
(Choose closest to your users)

**Branch:**
```
main
```
(or `master` if that's your branch)

**Root Directory:**
```
.
```
(Leave as is - root of repository)

**Runtime:**
```
Python 3
```

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn app:app
```

**Instance Type:**
```
Free
```
(Start with free, upgrade later if needed)

### 3.4 Click "Create Web Service"

Render will start building your application.

---

## Step 4: Configure Environment Variables

### 4.1 Access Environment Variables

1. In your Render service dashboard
2. Go to **"Environment"** tab (left sidebar)
3. Click **"Add Environment Variable"**

### 4.2 Add Required Variables

Add each variable one by one:

#### Required Variables:

**1. SECRET_KEY**
```
Name: SECRET_KEY
Value: [Generate a strong random key - see below]
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and paste as the value.

**2. FLASK_DEBUG**
```
Name: FLASK_DEBUG
Value: False
```

**3. GEMINI_API_KEY**
```
Name: GEMINI_API_KEY
Value: [Your Google Gemini API key]
```

**4. STRIPE_SECRET_KEY**
```
Name: STRIPE_SECRET_KEY
Value: sk_live_xxxxx
```
(Use your live Stripe secret key)

**5. STRIPE_PUBLISHABLE_KEY**
```
Name: STRIPE_PUBLISHABLE_KEY
Value: pk_live_xxxxx
```
(Use your live Stripe publishable key)

**6. STRIPE_WEBHOOK_SECRET**
```
Name: STRIPE_WEBHOOK_SECRET
Value: whsec_xxxxx
```
(We'll update this after getting the webhook URL)

#### Optional Variables:

**7. GTM_CONTAINER_ID** (if using analytics)
```
Name: GTM_CONTAINER_ID
Value: GTM-xxxxx
```

**8. GOOGLE_CLIENT_ID** (if using OAuth)
```
Name: GOOGLE_CLIENT_ID
Value: [Your Google OAuth Client ID]
```

**9. GOOGLE_CLIENT_SECRET** (if using OAuth)
```
Name: GOOGLE_CLIENT_SECRET
Value: [Your Google OAuth Client Secret]
```

**10. DATABASE_URL** (for production database)
```
Name: DATABASE_URL
Value: [Leave empty for now - SQLite will be used]
```
Or set up PostgreSQL later:
```
postgresql://user:password@host:5432/dbname
```

**11. PORT** (usually not needed - Render sets this automatically)
```
Name: PORT
Value: [Leave empty - Render handles this]
```

### 4.3 Save Environment Variables

After adding each variable, click **"Save Changes"**

---

## Step 5: Wait for Deployment

### 5.1 Monitor Build Process

1. Render will automatically start building
2. Watch the **"Logs"** tab to see progress
3. Build typically takes 2-5 minutes

### 5.2 Check for Errors

If build fails:
- Check the logs for error messages
- Common issues:
  - Missing dependencies in requirements.txt
  - Syntax errors in code
  - Missing environment variables

### 5.3 Get Your App URL

Once deployed, Render will give you a URL like:
```
https://airbnb-photo-enhancer.onrender.com
```

**Save this URL** - you'll need it for the next steps!

---

## Step 6: Update External Services

### 6.1 Update Stripe Webhook

1. Go to [Stripe Dashboard](https://dashboard.stripe.com) → **Webhooks**
2. Find your webhook endpoint (or create new one)
3. Update the **Endpoint URL** to:
   ```
   https://your-app-name.onrender.com/api/payment/webhook
   ```
   Replace `your-app-name` with your actual Render app name
4. Click **"Save"**
5. Copy the **Signing secret** (starts with `whsec_`)
6. Go back to Render → Environment Variables
7. Update `STRIPE_WEBHOOK_SECRET` with the new value
8. Click **"Save Changes"**
9. Render will automatically redeploy

### 6.2 Update Google OAuth (if using)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **APIs & Services** → **Credentials**
3. Click on your OAuth 2.0 Client ID
4. Under **Authorized redirect URIs**, add:
   ```
   https://your-app-name.onrender.com/auth/google/callback
   ```
5. Under **Authorized JavaScript origins**, add:
   ```
   https://your-app-name.onrender.com
   ```
6. Click **"Save"**

### 6.3 Update Google Tag Manager (if using)

1. Your GTM container should work automatically
2. No changes needed - it uses the container ID from environment variable

---

## Step 7: Test Your Deployment

### 7.1 Basic Tests

1. Visit your Render URL: `https://your-app-name.onrender.com`
2. Check if homepage loads
3. Try signing up
4. Try logging in
5. Upload a test photo
6. Test payment flow (use Stripe test mode first!)

### 7.2 Payment Testing

1. Use Stripe test cards:
   - Success: `4242 4242 4242 4242`
   - Any future expiry date
   - Any 3-digit CVC
2. Complete a test payment
3. Verify download works after payment
4. Check Stripe Dashboard → Payments to see the transaction

### 7.3 Webhook Testing

1. Make a test payment
2. Go to Stripe Dashboard → Webhooks → Your webhook
3. Check **"Events"** tab
4. You should see `checkout.session.completed` event
5. Check Render logs to verify webhook was received

---

## Step 8: Set Up Custom Domain (Optional)

### 8.1 Add Custom Domain in Render

1. In Render dashboard → Your service
2. Go to **"Settings"** tab
3. Scroll to **"Custom Domains"**
4. Click **"Add Custom Domain"**
5. Enter your domain (e.g., `app.yourdomain.com`)
6. Follow Render's DNS instructions

### 8.2 Update DNS

1. Go to your domain registrar (GoDaddy, Namecheap, etc.)
2. Add a CNAME record:
   ```
   Type: CNAME
   Name: app (or www, or @)
   Value: your-app-name.onrender.com
   ```
3. Wait for DNS propagation (can take up to 48 hours)

### 8.3 Update External Services

After custom domain is active:
- Update Stripe webhook URL
- Update Google OAuth redirect URIs
- Update any other external services

---

## Step 9: Monitor and Maintain

### 9.1 Check Logs Regularly

1. Render Dashboard → Your service → **"Logs"** tab
2. Monitor for errors
3. Check payment processing
4. Watch for API errors

### 9.2 Set Up Monitoring (Optional)

1. Render Dashboard → **"Alerts"**
2. Set up email alerts for:
   - Service down
   - Build failures
   - High error rates

### 9.3 Database Backups

If using PostgreSQL:
1. Render Dashboard → Your database
2. Enable automatic backups
3. Set backup schedule

---

## Troubleshooting

### Build Fails

**Error: "Module not found"**
- Check `requirements.txt` has all dependencies
- Verify all imports in code

**Error: "Port already in use"**
- Render sets PORT automatically - don't hardcode it
- Your code already handles this correctly

**Error: "Database connection failed"**
- Check DATABASE_URL is correct
- Verify database is running (if using PostgreSQL)

### App Crashes After Deployment

**Check logs:**
1. Render Dashboard → Logs
2. Look for Python errors
3. Check for missing environment variables

**Common fixes:**
- Verify all environment variables are set
- Check SECRET_KEY is set
- Ensure FLASK_DEBUG=False

### Payments Not Working

1. **Check Stripe keys:**
   - Verify you're using LIVE keys (not test)
   - Keys should start with `sk_live_` and `pk_live_`

2. **Check webhook:**
   - Verify webhook URL is correct
   - Check webhook secret matches
   - Test webhook in Stripe Dashboard

3. **Check logs:**
   - Look for Stripe API errors
   - Check payment creation errors

### Slow Performance

**Free tier limitations:**
- Free tier spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- Consider upgrading to paid plan for better performance

---

## Render-Specific Tips

### Auto-Deploy

Render automatically deploys when you push to GitHub:
1. Make changes locally
2. Commit: `git commit -m "Your changes"`
3. Push: `git push origin main`
4. Render detects changes and redeploys automatically

### Manual Deploy

1. Render Dashboard → Your service
2. Click **"Manual Deploy"**
3. Select branch
4. Click **"Deploy"**

### Rollback

1. Render Dashboard → Your service
2. Go to **"Events"** tab
3. Find previous successful deployment
4. Click **"Redeploy"**

---

## Cost Considerations

### Free Tier Includes:
- ✅ 750 hours/month (enough for 24/7 on one service)
- ✅ 512 MB RAM
- ✅ Shared CPU
- ✅ Automatic SSL
- ✅ Custom domains

### Paid Plans Start At:
- $7/month for better performance
- No spin-down delays
- More resources

---

## Next Steps After Deployment

1. ✅ Test all features thoroughly
2. ✅ Set up monitoring/alerts
3. ✅ Configure custom domain (optional)
4. ✅ Set up database backups (if using PostgreSQL)
5. ✅ Monitor performance and costs
6. ✅ Set up staging environment (optional)

---

## Quick Reference

### Your Render URLs:
- **App URL**: `https://your-app-name.onrender.com`
- **Dashboard**: `https://dashboard.render.com`
- **Webhook URL**: `https://your-app-name.onrender.com/api/payment/webhook`

### Important Commands:
```bash
# View logs locally (if needed)
git log

# Push updates
git add .
git commit -m "Update description"
git push origin main
```

---

## Support

- **Render Docs**: https://render.com/docs
- **Render Support**: support@render.com
- **Community**: https://community.render.com

---

**You're all set!** Follow these steps and your app will be live on Render. 🚀

