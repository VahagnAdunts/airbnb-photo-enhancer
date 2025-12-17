# Deployment Guide

## Pre-Deployment Checklist

### ✅ Code Cleanup
- [x] Removed ngrok-related files
- [x] Removed temporary/test files
- [x] Removed old documentation files
- [x] Fixed debug mode for production
- [x] Updated .gitignore

### Environment Variables Required

Create a `.env` file with the following variables:

```bash
# Flask Configuration
SECRET_KEY=your-strong-secret-key-here-change-this
FLASK_DEBUG=False
PORT=5000

# Database
DATABASE_URL=sqlite:///airbnb_enhancer.db
# For production, use PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/dbname

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Stripe Payment (Required for downloads)
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Google Tag Manager (Optional)
GTM_CONTAINER_ID=GTM-xxxxx
```

## Security Checklist

### Before Deploying:

1. **Change SECRET_KEY**
   - Generate a strong random secret key
   - Never use the default "your-secret-key-change-in-production"

2. **Set FLASK_DEBUG=False**
   - Debug mode should NEVER be enabled in production
   - Set via environment variable: `FLASK_DEBUG=False`

3. **Use Environment Variables**
   - Never hardcode API keys or secrets
   - Use `.env` file (not committed to git)
   - Or use your hosting platform's environment variable settings

4. **Database Security**
   - Use PostgreSQL for production (not SQLite)
   - Use strong database passwords
   - Enable SSL connections

5. **HTTPS Required**
   - Always use HTTPS in production
   - Update Stripe webhook URL to use HTTPS
   - Update Google OAuth redirect URIs to use HTTPS

6. **File Upload Security**
   - Current implementation validates file types
   - Consider adding file size limits
   - Consider scanning uploads for malware

## Deployment Platforms

### Option 1: Heroku

1. **Install Heroku CLI**
2. **Create Procfile**:
   ```
   web: gunicorn app:app
   ```
3. **Add to requirements.txt**:
   ```
   gunicorn==21.2.0
   ```
4. **Deploy**:
   ```bash
   heroku create your-app-name
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set GEMINI_API_KEY=your-key
   heroku config:set STRIPE_SECRET_KEY=your-key
   # ... set all other env vars
   git push heroku main
   ```

### Option 2: Railway

1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Railway auto-detects Flask apps
4. Deploy automatically on push

### Option 3: Render

1. Connect GitHub repository
2. Select "Web Service"
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Set environment variables
6. Deploy

### Option 4: DigitalOcean App Platform

1. Connect GitHub repository
2. Select Python environment
3. Set environment variables
4. Deploy

## Post-Deployment Steps

### 1. Update Stripe Webhook

1. Go to Stripe Dashboard → Webhooks
2. Update webhook URL to your production domain:
   ```
   https://yourdomain.com/api/payment/webhook
   ```
3. Copy the new webhook secret
4. Update `STRIPE_WEBHOOK_SECRET` in your environment

### 2. Update Google OAuth

1. Go to Google Cloud Console
2. Update authorized redirect URIs:
   ```
   https://yourdomain.com/auth/google/callback
   ```
3. Update authorized JavaScript origins:
   ```
   https://yourdomain.com
   ```

### 3. Update Google Tag Manager

1. Update GTM container if needed
2. Verify analytics is tracking correctly

### 4. Database Migration

If using a new database:
```bash
# The app will create tables automatically on first run
# Or manually:
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 5. Test Everything

- [ ] User registration/login
- [ ] Photo upload and enhancement
- [ ] Payment flow
- [ ] Download after payment
- [ ] Webhook receiving payments
- [ ] Analytics tracking
- [ ] OAuth login (if enabled)

## Production Considerations

### Performance

- Use a production WSGI server (gunicorn, uwsgi)
- Enable caching (Redis recommended)
- Use CDN for static files
- Optimize database queries
- Consider image optimization

### Monitoring

- Set up error tracking (Sentry, Rollbar)
- Monitor server logs
- Set up uptime monitoring
- Track payment success rates

### Backup

- Regular database backups
- Backup uploaded images
- Store backups off-site

## Troubleshooting

### Common Issues

1. **Webhook not working**
   - Check webhook URL is correct
   - Verify webhook secret matches
   - Check server logs for errors

2. **Payments not processing**
   - Verify Stripe keys are correct
   - Check Stripe Dashboard for errors
   - Verify webhook is receiving events

3. **Database errors**
   - Check database connection string
   - Verify database exists
   - Check permissions

4. **Image enhancement failing**
   - Verify GEMINI_API_KEY is set
   - Check API quota/limits
   - Review server logs

## Support

For issues, check:
- Server logs
- Stripe Dashboard → Logs
- Google Cloud Console → Logs
- Application error tracking

