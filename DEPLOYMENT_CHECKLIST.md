# Deployment Checklist

## ✅ Code Cleanup Complete

- [x] Removed all ngrok-related files
- [x] Removed temporary/test files
- [x] Removed old documentation files
- [x] Fixed debug mode for production
- [x] Updated logging for production
- [x] Added gunicorn to requirements
- [x] Created Procfile for deployment
- [x] Updated .gitignore

## 📋 Pre-Deployment Steps

### 1. Environment Variables

Set these in your hosting platform:

```bash
# Required
SECRET_KEY=<generate-strong-random-key>
FLASK_DEBUG=False
GEMINI_API_KEY=<your-gemini-key>
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Optional
GTM_CONTAINER_ID=GTM-xxxxx
GOOGLE_CLIENT_ID=<if-using-oauth>
GOOGLE_CLIENT_SECRET=<if-using-oauth>
DATABASE_URL=<postgresql-url-for-production>
PORT=5000
```

### 2. Generate SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Update Stripe Webhook

1. Go to Stripe Dashboard → Webhooks
2. Update endpoint URL to: `https://yourdomain.com/api/payment/webhook`
3. Copy the new webhook secret
4. Update `STRIPE_WEBHOOK_SECRET` environment variable

### 4. Update Google OAuth (if using)

1. Google Cloud Console → Credentials
2. Update Authorized redirect URIs:
   - `https://yourdomain.com/auth/google/callback`
3. Update Authorized JavaScript origins:
   - `https://yourdomain.com`

### 5. Database Setup

For production, use PostgreSQL (not SQLite):

```bash
# Example DATABASE_URL
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

The app will create tables automatically on first run.

## 🚀 Deployment Platforms

### Heroku
```bash
heroku create your-app-name
heroku config:set SECRET_KEY=...
# ... set all env vars
git push heroku main
```

### Railway
1. Connect GitHub repo
2. Set environment variables
3. Auto-deploys on push

### Render
1. Connect GitHub repo
2. Select "Web Service"
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn app:app`
5. Set environment variables

## ✅ Post-Deployment Testing

- [ ] Home page loads
- [ ] User can sign up
- [ ] User can log in
- [ ] Photo upload works
- [ ] Photo enhancement works
- [ ] Payment flow works
- [ ] Download after payment works
- [ ] Webhook receives events
- [ ] Analytics tracking works
- [ ] OAuth login works (if enabled)

## 🔒 Security Reminders

- ✅ Never commit `.env` file
- ✅ Use strong SECRET_KEY
- ✅ Set FLASK_DEBUG=False
- ✅ Use HTTPS only
- ✅ Keep dependencies updated
- ✅ Monitor logs for errors

## 📝 Files Ready for Deployment

### Core Application
- ✅ `app.py` - Main Flask app
- ✅ `models.py` - Database models
- ✅ `image_enhancer.py` - Image processing
- ✅ `requirements.txt` - Dependencies
- ✅ `Procfile` - Deployment config

### Frontend
- ✅ All HTML templates
- ✅ All JavaScript files
- ✅ All CSS files
- ✅ Static assets

### Documentation
- ✅ `README.md`
- ✅ `DEPLOYMENT.md`
- ✅ `STRIPE_SETUP.md`
- ✅ `GTM_SETUP.md`
- ✅ `ANALYTICS_SETUP.md`

## 🎯 Ready to Deploy!

Your codebase is clean, secure, and ready for production deployment.

