# Database Troubleshooting Guide

## Issue: Enhanced Photos Not Saved to User Profile

If enhanced photos are not appearing in user profiles on the deployed version, it's likely a database initialization issue.

## Quick Diagnosis

### 1. Check Database Health
Visit: `https://your-domain.com/api/health`

This will show:
- Database connection status
- Database type (SQLite or PostgreSQL)
- Number of users and images in database
- Any connection errors

### 2. Check Server Logs
Look for these log messages on startup:
- ✅ `"Database tables created successfully"` - Good!
- ✅ `"Database initialized: X users, Y images"` - Good!
- ❌ `"CRITICAL: Failed to initialize database"` - Problem!

### 3. Check Environment Variables
Ensure `DATABASE_URL` is set correctly in your deployment platform:

**For SQLite (development/testing):**
```
DATABASE_URL=sqlite:///airbnb_enhancer.db
```

**For PostgreSQL (production - recommended):**
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## Common Issues and Solutions

### Issue 1: Database Tables Not Created

**Symptoms:**
- Photos enhance successfully but don't appear in dashboard
- Health check shows database connected but 0 images
- No errors in logs

**Solution:**
1. The app should create tables automatically on startup
2. If not, manually trigger table creation:
   ```python
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```
3. Or restart your deployment service

### Issue 2: Database Connection Fails

**Symptoms:**
- Health check returns `"status": "unhealthy"`
- Logs show `"CRITICAL: Failed to initialize database"`
- Error messages about connection refused or authentication failed

**Solutions:**

**For SQLite:**
- Ensure the `instance/` directory exists and is writable
- Check file permissions
- Verify the database path is correct

**For PostgreSQL:**
- Verify `DATABASE_URL` is correct
- Check database credentials
- Ensure database exists
- Verify network connectivity (for external databases)
- Check firewall rules

### Issue 3: User ID Not Saved

**Symptoms:**
- Photos save but `user_id` is NULL in database
- Photos don't appear in user's dashboard

**Check:**
1. Verify user is logged in when enhancing photos
2. Check logs for: `"User authenticated: True, User ID: X"`
3. If `User authenticated: False`, the photo will save but won't be linked to user

**Solution:**
- Ensure users are logged in before enhancing photos
- Check authentication is working correctly
- Verify session management

### Issue 4: SQLite on Render (Ephemeral Storage)

**Symptoms:**
- Photos work initially but disappear after service restart
- Database resets periodically

**Solution:**
- **Upgrade to PostgreSQL** (recommended for production)
- SQLite on Render's free tier uses ephemeral storage
- Data is lost on service restarts

## Step-by-Step Fix for Render Deployment

### Option A: Fix SQLite (Quick Fix)

1. **Check Environment Variables:**
   - Go to Render Dashboard → Your Web Service → Environment
   - Ensure `DATABASE_URL` is set (or leave unset for default SQLite)

2. **Restart Service:**
   - Render Dashboard → Your Web Service → Manual Deploy → Clear build cache & deploy

3. **Check Logs:**
   - Look for: `"Database tables created successfully"`
   - If you see errors, note them

4. **Test:**
   - Visit `/api/health` to verify database connection
   - Try enhancing a photo while logged in
   - Check dashboard to see if photo appears

### Option B: Upgrade to PostgreSQL (Recommended)

1. **Create PostgreSQL Database:**
   - Render Dashboard → New + → PostgreSQL
   - Name: `airbnb-enhancer-db`
   - Region: Same as your web service
   - Plan: Free (or paid for production)

2. **Get Database URL:**
   - Go to database dashboard
   - Copy "Internal Database URL"
   - Format: `postgresql://user:password@host:5432/dbname`

3. **Update Environment Variable:**
   - Go to Web Service → Environment
   - Add/Update: `DATABASE_URL` = [paste Internal Database URL]
   - Save changes

4. **Redeploy:**
   - Render will automatically redeploy
   - Tables will be created automatically

5. **Verify:**
   - Check `/api/health` endpoint
   - Should show PostgreSQL and connection status
   - Test photo enhancement

## Verification Checklist

After fixing, verify:

- [ ] `/api/health` returns `"status": "healthy"`
- [ ] Database type is correct (SQLite or PostgreSQL)
- [ ] Can create new user account
- [ ] Can log in
- [ ] Can enhance photo while logged in
- [ ] Enhanced photo appears in dashboard
- [ ] Photo has correct `user_id` in database
- [ ] Can view photo details
- [ ] Can delete photo

## Testing Database Connection

### Test 1: Health Check
```bash
curl https://your-domain.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": {
    "type": "PostgreSQL",
    "connected": true,
    "users": 1,
    "images": 5
  }
}
```

### Test 2: Check Logs
Look for these messages in deployment logs:
```
INFO: Using PostgreSQL database
INFO: Database tables created successfully
INFO: Database initialized: 1 users, 5 images
```

### Test 3: Manual Database Query
If you have database access:
```sql
-- Check if tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check if photos are being saved
SELECT id, user_id, original_filename, created_at 
FROM enhanced_image 
ORDER BY created_at DESC 
LIMIT 10;

-- Check if user_id is set correctly
SELECT COUNT(*) FROM enhanced_image WHERE user_id IS NOT NULL;
```

## Still Having Issues?

1. **Check Application Logs:**
   - Look for any `ERROR` or `CRITICAL` messages
   - Check for database-related errors

2. **Verify Environment Variables:**
   - All required variables are set
   - `DATABASE_URL` is correct format
   - No typos in variable names

3. **Test Locally:**
   - Run app locally with same `DATABASE_URL`
   - See if issue reproduces locally

4. **Check Database Permissions:**
   - User has CREATE TABLE permissions
   - User has INSERT/UPDATE/SELECT permissions

5. **Contact Support:**
   - Include health check response
   - Include relevant log messages
   - Include database type and configuration

## Prevention

To prevent this issue in the future:

1. **Use PostgreSQL for Production:**
   - More reliable than SQLite
   - Better for concurrent access
   - Data persistence

2. **Monitor Health Endpoint:**
   - Set up monitoring for `/api/health`
   - Alert if status becomes unhealthy

3. **Regular Backups:**
   - Backup database regularly
   - Test restore procedures

4. **Logging:**
   - Monitor application logs
   - Set up log aggregation
   - Alert on database errors

