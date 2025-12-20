# PostgreSQL Setup Guide for Render

This guide will help you set up PostgreSQL database on Render for your Airbnb Photo Enhancer application.

## Why PostgreSQL?

- ✅ **Data Persistence**: Data survives service restarts
- ✅ **Production Ready**: Designed for production applications
- ✅ **Scalable**: Can handle multiple concurrent connections
- ✅ **Reliable**: Better error handling and transaction support
- ✅ **Free Tier Available**: 750 hours/month free on Render

## Step-by-Step Setup

### Step 1: Create PostgreSQL Database on Render

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Log in to your account

2. **Create New PostgreSQL Database**
   - Click **"New +"** button (top right)
   - Select **"PostgreSQL"** from the dropdown

3. **Configure Database**
   - **Name**: `airbnb-enhancer-db` (or your preferred name)
   - **Database**: `    ` (or leave default)
   - **User**: (auto-generated, you can customize)
   - **Region**: Choose the same region as your web service
   - **PostgreSQL Version**: Latest (15 or 16 recommended)
   - **Plan**: 
     - **Free**: 750 hours/month, 1 GB storage (good for testing)
     - **Starter ($7/month)**: Better for production

4. **Create Database**
   - Click **"Create Database"**
   - Wait for database to be provisioned (1-2 minutes)

### Step 2: Get Database Connection URL

1. **Go to Database Dashboard**
   - Click on your newly created database
   - You'll see the database details

2. **Copy Internal Database URL**
   - Find **"Internal Database URL"** section
   - Click **"Copy"** button
   - This URL is for services within Render (recommended)
   - Format: `postgresql://user:password@host:5432/dbname`

   **OR**

   - Use **"External Database URL"** if connecting from outside Render
   - Format: `postgresql://user:password@host:5432/dbname`

   **Note**: Internal URL is faster and more secure for Render services.

### Step 3: Add DATABASE_URL to Web Service

1. **Go to Your Web Service**
   - Navigate to your web service in Render Dashboard
   - Click on the service name

2. **Open Environment Tab**
   - Click **"Environment"** tab in the left sidebar

3. **Add DATABASE_URL Variable**
   - Click **"Add Environment Variable"**
   - **Name**: `DATABASE_URL`
   - **Value**: Paste the Internal Database URL you copied
   - Click **"Save Changes"**

4. **Verify**
   - You should see `DATABASE_URL` in the environment variables list
   - The value should start with `postgresql://`

### Step 4: Redeploy Service

1. **Automatic Redeploy**
   - Render will automatically redeploy when you save environment variables
   - Wait for deployment to complete (2-5 minutes)

2. **Manual Redeploy (if needed)**
   - Go to **"Manual Deploy"** tab
   - Click **"Deploy latest commit"**
   - Or click **"Clear build cache & deploy"** if having issues

### Step 5: Verify Database Connection

1. **Check Health Endpoint**
   - Visit: `https://your-app.onrender.com/api/health`
   - Should show:
     ```json
     {
       "status": "healthy",
       "database": {
         "type": "PostgreSQL",
         "connected": true,
         "users": 0,
         "images": 0
       }
     }
     ```

2. **Check Application Logs**
   - Go to your web service → **"Logs"** tab
   - Look for:
     ```
     INFO: Using PostgreSQL database
     INFO: Database tables created successfully
     INFO: Database initialized: 0 users, 0 images
     ```

3. **Test Application**
   - Create a new user account
   - Upload and enhance a photo
   - Check dashboard - photo should appear
   - Restart service - photo should still be there (data persistence!)

## Environment Variables Summary

Your web service should have these environment variables:

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
GOOGLE_CLIENT_ID=your-google-client-id (optional)
GOOGLE_CLIENT_SECRET=your-google-client-secret (optional)
GTM_CONTAINER_ID=GTM-xxxxx (optional)
FLASK_DEBUG=False
PORT=5000
```

## Troubleshooting

### Issue: "Database connection failed"

**Solution:**
1. Verify `DATABASE_URL` is correct
2. Check if database is running (Render Dashboard → Database → Status)
3. Ensure you're using **Internal Database URL** (not external)
4. Verify database and web service are in the same region

### Issue: "No module named 'psycopg2'"

**Solution:**
1. Ensure `psycopg2-binary>=2.9.9` is in `requirements.txt`
2. Redeploy service to install dependencies
3. Check build logs for installation errors

### Issue: "relation does not exist" or "table does not exist"

**Solution:**
1. Tables should be created automatically on first run
2. Check logs for: `"Database tables created successfully"`
3. If not, manually trigger:
   - Go to Render Shell (or SSH)
   - Run: `python -c "from app import app, db; app.app_context().push(); db.create_all()"`

### Issue: "postgres:// vs postgresql://"

**Solution:**
- The code automatically converts `postgres://` to `postgresql://`
- This is handled in `app.py` automatically
- No action needed

### Issue: Database shows 0 users/images after restart

**Solution:**
- This shouldn't happen with PostgreSQL (data persists)
- If it does, check:
  1. Database is actually PostgreSQL (not SQLite)
  2. `DATABASE_URL` is set correctly
  3. Database is running and accessible
  4. Check database directly to verify data exists

## Migration from SQLite to PostgreSQL

If you were using SQLite and want to migrate existing data:

### Option 1: Fresh Start (Recommended for new deployments)
- Just set `DATABASE_URL` to PostgreSQL
- Tables will be created automatically
- Users will need to sign up again
- Old photos won't be migrated

### Option 2: Data Migration (Advanced)
1. Export data from SQLite:
   ```bash
   sqlite3 instance/airbnb_enhancer.db .dump > backup.sql
   ```

2. Convert SQLite dump to PostgreSQL format (requires manual editing)

3. Import to PostgreSQL:
   ```bash
   psql $DATABASE_URL < converted_backup.sql
   ```

**Note**: For most cases, starting fresh is easier and cleaner.

## Database Management

### View Database in Render Dashboard
- Go to your database → **"Info"** tab
- See connection details, status, and metrics

### Connect via psql (Command Line)
1. Get connection string from Render Dashboard
2. Install PostgreSQL client locally
3. Connect:
   ```bash
   psql $DATABASE_URL
   ```

### View Tables
```sql
\dt  -- List all tables
SELECT * FROM "user" LIMIT 10;  -- View users
SELECT * FROM enhanced_image LIMIT 10;  -- View images
```

### Backup Database
- Render provides automatic backups on paid plans
- For free tier, export manually:
  ```bash
  pg_dump $DATABASE_URL > backup.sql
  ```

## Cost Information

### Free Tier
- ✅ 750 hours/month (enough for 24/7 operation)
- ✅ 1 GB storage
- ✅ Automatic backups (limited)
- ⚠️ Spins down after 15 minutes of inactivity (free tier only)

### Starter Plan ($7/month)
- ✅ Always on (no spin down)
- ✅ 10 GB storage
- ✅ Automatic daily backups
- ✅ Better performance

### Recommendation
- **Start with Free Tier** for testing
- **Upgrade to Starter** when you have real users
- **Upgrade to Standard ($20/month)** for production with high traffic

## Security Best Practices

1. **Use Internal Database URL**
   - More secure (not exposed to internet)
   - Faster (internal network)

2. **Rotate Passwords**
   - Change database password periodically
   - Update `DATABASE_URL` when changed

3. **Backup Regularly**
   - Set up automatic backups
   - Test restore procedures

4. **Monitor Access**
   - Check database logs for unusual activity
   - Use strong passwords

## Next Steps

After setting up PostgreSQL:

1. ✅ Verify health endpoint shows PostgreSQL
2. ✅ Test user registration
3. ✅ Test photo enhancement
4. ✅ Verify photos persist after service restart
5. ✅ Set up monitoring/alerts
6. ✅ Configure backups

## Support

If you encounter issues:

1. Check application logs in Render Dashboard
2. Check database status in Render Dashboard
3. Verify all environment variables are set
4. Test health endpoint: `/api/health`
5. Review `DATABASE_TROUBLESHOOTING.md` for common issues

## Summary

✅ **PostgreSQL is now configured!**

Your application will:
- Persist data across service restarts
- Handle concurrent users better
- Scale as you grow
- Provide better error handling

The code automatically:
- Detects PostgreSQL from `DATABASE_URL`
- Creates tables on first run
- Handles connection pooling
- Converts `postgres://` to `postgresql://`

Just set `DATABASE_URL` and deploy! 🚀

