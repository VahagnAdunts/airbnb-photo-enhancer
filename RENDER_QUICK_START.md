# Render Deployment - Quick Start Checklist

Follow this checklist step by step. Check off each item as you complete it.

## 📋 Pre-Deployment Checklist

### Step 1: Prepare GitHub Repository

- [ ] **Initialize Git** (if not done):
  ```bash
  git init
  git add .
  git commit -m "Initial commit - Ready for Render deployment"
  ```

- [ ] **Create GitHub Repository**:
  - Go to github.com → New repository
  - Name: `airbnb-photo-enhancer`
  - Don't initialize with README
  - Create repository

- [ ] **Push to GitHub**:
  ```bash
  git remote add origin https://github.com/YOUR_USERNAME/airbnb-photo-enhancer.git
  git branch -M main
  git push -u origin main
  ```

### Step 2: Create Render Account

- [ ] Go to [render.com](https://render.com)
- [ ] Sign up with GitHub account
- [ ] Connect GitHub account
- [ ] Authorize Render to access repositories

### Step 3: Create Web Service

- [ ] Click **"New +"** → **"Web Service"**
- [ ] Connect your repository: `airbnb-photo-enhancer`
- [ ] Configure service:
  - **Name**: `airbnb-photo-enhancer`
  - **Region**: `Oregon (US West)` (or closest to you)
  - **Branch**: `main`
  - **Root Directory**: `.` (leave as is)
  - **Runtime**: `Python 3`
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `gunicorn app:app`
  - **Instance Type**: `Free`
- [ ] Click **"Create Web Service"**

### Step 4: Set Environment Variables

Go to **Environment** tab and add:

- [ ] **SECRET_KEY**
  - Generate: `python -c "import secrets; print(secrets.token_hex(32))"`
  - Copy and paste the output

- [ ] **FLASK_DEBUG** = `False`

- [ ] **GEMINI_API_KEY** = `[Your Gemini API key]`

- [ ] **STRIPE_SECRET_KEY** = `sk_live_xxxxx`

- [ ] **STRIPE_PUBLISHABLE_KEY** = `pk_live_xxxxx`

- [ ] **STRIPE_WEBHOOK_SECRET** = `[We'll update this after getting URL]`

- [ ] **GTM_CONTAINER_ID** = `GTM-xxxxx` (if using)

- [ ] **GOOGLE_CLIENT_ID** = `[If using OAuth]`

- [ ] **GOOGLE_CLIENT_SECRET** = `[If using OAuth]`

### Step 5: Wait for Deployment

- [ ] Watch build logs
- [ ] Wait for "Your service is live" message
- [ ] Copy your app URL: `https://your-app-name.onrender.com`

### Step 6: Update Stripe Webhook

- [ ] Go to Stripe Dashboard → Webhooks
- [ ] Update webhook URL to: `https://your-app-name.onrender.com/api/payment/webhook`
- [ ] Copy new webhook secret
- [ ] Update `STRIPE_WEBHOOK_SECRET` in Render
- [ ] Render will auto-redeploy

### Step 7: Update Google OAuth (if using)

- [ ] Google Cloud Console → Credentials
- [ ] Add redirect URI: `https://your-app-name.onrender.com/auth/google/callback`
- [ ] Add JavaScript origin: `https://your-app-name.onrender.com`

### Step 8: Test Everything

- [ ] Visit your app URL
- [ ] Test homepage loads
- [ ] Test user signup
- [ ] Test user login
- [ ] Test photo upload
- [ ] Test photo enhancement
- [ ] Test payment flow (use test card: 4242 4242 4242 4242)
- [ ] Test download after payment
- [ ] Check Stripe Dashboard for payment
- [ ] Check Render logs for errors

## ✅ Deployment Complete!

Your app is now live on Render!

## 🔄 Making Updates

After making changes:

```bash
git add .
git commit -m "Description of changes"
git push origin main
```

Render will automatically redeploy!

## 📞 Need Help?

- See `RENDER_DEPLOYMENT_GUIDE.md` for detailed instructions
- Render Docs: https://render.com/docs
- Check Render logs for errors

